from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from ..command_profiles import build_command_plan
from ..schemas import ModelSpec, ProviderHealth, ProviderResult, RuntimeConfig, UpscaleRequest
from .base import Provider

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}


class ExternalCommandProvider(Provider):
    def __init__(self, spec: ModelSpec, runtime: RuntimeConfig | None) -> None:
        self.spec = spec
        self.runtime = runtime

    def doctor(self) -> ProviderHealth:
        if self.spec.status.value == "BLOCKED_CHECKPOINT":
            return ProviderHealth(
                model_id=self.spec.id,
                ready=False,
                status="BLOCKED_CHECKPOINT",
                details=[self.spec.hardware_notes],
            )
        if self.runtime is None:
            return ProviderHealth(
                model_id=self.spec.id,
                ready=False,
                status="RUNTIME_NOT_CONFIGURED",
                details=["Add this model to the runtime configuration file."],
            )
        missing: list[str] = []
        if not self.runtime.workdir.is_dir():
            missing.append(f"workdir missing: {self.runtime.workdir}")
        if self.spec.command_profile != "configured_external":
            if not self.runtime.python_executable.is_file():
                missing.append(f"python executable missing: {self.runtime.python_executable}")
        else:
            executable = self.runtime.paths.get("executable")
            if not executable:
                missing.append("configured external runtime missing executable")
            elif not Path(executable).expanduser().is_file():
                missing.append(f"executable missing: {executable}")
        return ProviderHealth(
            model_id=self.spec.id,
            ready=not missing,
            status="READY" if not missing else "BLOCKED",
            details=missing,
        )

    def upscale_one(
        self, input_path: Path, output_path: Path, request: UpscaleRequest
    ) -> ProviderResult:
        if self.runtime is None:
            raise RuntimeError(f"runtime not configured for {self.spec.id}")
        health = self.doctor()
        if not health.ready:
            raise RuntimeError("; ".join(health.details) or health.status)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=f"sr-{self.spec.id}-") as temp_dir:
            temp_root = Path(temp_dir)
            stage_input = temp_root / "input"
            stage_output = temp_root / "output"
            stage_input.mkdir()
            stage_output.mkdir()
            staged = stage_input / input_path.name
            shutil.copy2(input_path, staged)

            plan = build_command_plan(
                self.spec,
                self.runtime,
                request,
                staged,
                stage_input,
                stage_output,
            )
            completed = subprocess.run(
                plan.argv,
                cwd=plan.cwd,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.runtime.timeout_seconds,
                shell=False,
            )
            if completed.returncode != 0:
                return ProviderResult(
                    exit_code=completed.returncode,
                    stdout=completed.stdout,
                    stderr=completed.stderr,
                    argv=plan.argv,
                )
            candidates = sorted(
                path
                for path in plan.output_dir.rglob("*")
                if path.is_file() and path.suffix.lower() in _IMAGE_EXTS
            )
            if not candidates:
                raise RuntimeError("provider succeeded but no image output was found")
            preferred = next((p for p in candidates if input_path.stem in p.stem), candidates[0])
            with Image.open(preferred) as image:
                image.verify()
            shutil.copy2(preferred, output_path)
            return ProviderResult(
                output_path=output_path,
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                argv=plan.argv,
            )
