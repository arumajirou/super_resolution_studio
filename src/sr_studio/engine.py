from __future__ import annotations

import platform
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image

from .catalog import get_model_spec
from .provenance import sha256_file, write_manifest
from .registry import ProviderRegistry
from .schemas import FileResult, ModelStatus, ResultStatus, RunManifest, UpscaleRequest
from .security import validate_input_path, validate_output_path

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}


def expand_inputs(inputs: list[Path]) -> list[Path]:
    expanded: list[Path] = []
    for raw in inputs:
        path = validate_input_path(raw)
        if path.is_dir():
            for item in sorted(path.rglob("*")):
                if item.is_file() and item.suffix.lower() in _IMAGE_EXTS:
                    expanded.append(validate_input_path(item))
        elif path.is_file():
            expanded.append(path)
        else:
            expanded.append(path)
    return expanded


def _safe_stem(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", path.stem).strip("_") or "image"


def _output_suffix(path: Path) -> str:
    suffix = path.suffix.lower()
    return suffix if suffix in _IMAGE_EXTS else ".png"


def _environment_snapshot() -> dict[str, str | None]:
    return {
        "python": sys.version.splitlines()[0],
        "platform": platform.platform(),
        "nvidia_smi": shutil.which("nvidia-smi"),
    }


def _write_process_logs(
    run_root: Path, index: int, stdout: str, stderr: str
) -> tuple[Path | None, Path | None]:
    stdout_path: Path | None = None
    stderr_path: Path | None = None
    if stdout:
        stdout_path = run_root.parent / "stdout" / f"{index:04d}.log"
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
    if stderr:
        stderr_path = run_root.parent / "stderr" / f"{index:04d}.log"
        stderr_path.parent.mkdir(parents=True, exist_ok=True)
        stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
    return stdout_path, stderr_path


def run_upscale(request: UpscaleRequest, registry: ProviderRegistry | None = None) -> RunManifest:
    spec = get_model_spec(request.model_id)
    if spec.status is ModelStatus.BLOCKED_CHECKPOINT:
        raise RuntimeError(f"{spec.id} is blocked: {spec.hardware_notes}")
    if request.scale not in spec.supported_scales:
        raise ValueError(
            f"scale {request.scale} is not supported by {request.model_id}; "
            f"supported={spec.supported_scales}"
        )
    provider_registry = registry or ProviderRegistry()
    provider = provider_registry.get(request.model_id)

    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    output_root = validate_output_path(request.output_dir)
    run_root = output_root / run_id / request.model_id
    manifest = RunManifest(
        run_id=run_id,
        started_at=datetime.now(UTC),
        request=request,
        model=spec,
        environment=_environment_snapshot(),
    )
    inputs = expand_inputs(request.inputs)
    if not inputs:
        raise ValueError("no input images found")

    for index, input_path in enumerate(inputs, start=1):
        start = time.perf_counter()
        result = FileResult(input_path=input_path, status=ResultStatus.FAILED)
        try:
            if not input_path.is_file():
                raise FileNotFoundError(input_path)
            result.input_sha256 = sha256_file(input_path)
            with Image.open(input_path) as image:
                image.verify()
            output_path = run_root / (
                f"{index:04d}_{_safe_stem(input_path)}__x{request.scale}"
                f"{_output_suffix(input_path)}"
            )
            provider_result = provider.upscale_one(input_path, output_path, request)
            result.exit_code = provider_result.exit_code
            if provider_result.argv is not None:
                manifest.provider_argv = provider_result.argv
            result.stdout_log, result.stderr_log = _write_process_logs(
                run_root, index, provider_result.stdout, provider_result.stderr
            )
            if provider_result.exit_code not in (None, 0):
                result.status = ResultStatus.FAILED
                result.error = (provider_result.stderr or "external provider failed")[-4000:]
            elif provider_result.output_path and provider_result.output_path.is_file():
                with Image.open(provider_result.output_path) as image:
                    image.verify()
                result.output_path = provider_result.output_path
                result.output_sha256 = sha256_file(provider_result.output_path)
                result.status = ResultStatus.SUCCEEDED
            else:
                result.error = "provider did not produce an output file"
        except subprocess.TimeoutExpired as exc:
            result.status = ResultStatus.TIMEOUT
            result.error = str(exc)
        except Exception as exc:  # noqa: BLE001 - isolated per-file batch error by design
            result.status = ResultStatus.FAILED
            result.error = f"{type(exc).__name__}: {exc}"
        finally:
            result.elapsed_seconds = time.perf_counter() - start
            manifest.results.append(result)

    manifest.finished_at = datetime.now(UTC)
    manifest.status = (
        "SUCCEEDED"
        if all(item.status is ResultStatus.SUCCEEDED for item in manifest.results)
        else "PARTIAL_OR_FAILED"
    )
    write_manifest(run_root.parent / "manifest.json", manifest)
    return manifest
