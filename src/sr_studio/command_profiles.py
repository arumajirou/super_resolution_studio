from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .schemas import ModelSpec, RuntimeConfig, UpscaleRequest


@dataclass(frozen=True)
class CommandPlan:
    argv: list[str]
    cwd: Path
    output_dir: Path


def _required(runtime: RuntimeConfig, key: str) -> str:
    try:
        return runtime.paths[key]
    except KeyError as exc:
        raise ValueError(f"runtime {runtime.model_id} missing required path: {key}") from exc


def _python_prefix(runtime: RuntimeConfig, script: str) -> list[str]:
    return [str(runtime.python_executable), str(runtime.workdir / script)]


def build_command_plan(
    spec: ModelSpec,
    runtime: RuntimeConfig,
    request: UpscaleRequest,
    input_path: Path,
    stage_input_dir: Path,
    stage_output_dir: Path,
) -> CommandPlan:
    profile = spec.command_profile
    if profile == "fidesr":
        argv = _python_prefix(runtime, "test_fidesr.py") + [
            "--pretrained_model_path",
            _required(runtime, "base_model"),
            "--pretrained_path",
            _required(runtime, "checkpoint"),
            "--process_size",
            str(request.extra_options.get("process_size", 512)),
            "--upscale",
            str(request.scale),
            "--input_image",
            str(stage_input_dir),
            "--output_dir",
            str(stage_output_dir),
            "--hf_scale",
            str(request.extra_options.get("hf_scale", 0.2)),
            "--lf_scale",
            str(request.extra_options.get("lf_scale", 0.2)),
        ]
        return CommandPlan(argv=argv, cwd=runtime.workdir, output_dir=stage_output_dir)

    if profile == "tinysr":
        argv = _python_prefix(runtime, "test/test_tinysr.py") + [
            "--pretrained_model_name_or_path",
            _required(runtime, "backbone"),
            "--vae_path",
            _required(runtime, "vae"),
            "--lora_dir",
            _required(runtime, "lora"),
            "--embedding_dir",
            _required(runtime, "embedding"),
            "--output_dir",
            str(stage_output_dir),
            "--input_dir",
            str(stage_input_dir),
            "--rank=64",
            "--rank_vae=64",
            f"--is_use_tile={'True' if request.tile_size else 'False'}",
            f"--vae_decoder_tiled_size={request.tile_size or 224}",
            "--vae_encoder_tiled_size=1024",
            "--latent_tiled_size=64",
            "--latent_tiled_overlap=8",
            f"--device={request.device}",
            f"--seed={request.seed}",
            f"--upscale={request.scale}",
            f"--process_size={request.extra_options.get('process_size', 512)}",
            f"--mixed_precision={request.precision}",
            "--align_method=adain",
        ]
        return CommandPlan(argv=argv, cwd=runtime.workdir, output_dir=stage_output_dir)

    if profile and profile.startswith("vosr_"):
        one_step = "onestep" in profile
        model_size = "0.5B" if "0_5b" in profile else "1.4B"
        script = "inference_vosr_onestep.py" if one_step else "inference_vosr.py"
        checkpoint_key = f"checkpoint_{model_size}_{'os' if one_step else 'ms'}"
        argv = _python_prefix(runtime, script) + [
            "-c",
            _required(runtime, checkpoint_key),
            "-i",
            str(input_path),
            "-o",
            str(stage_output_dir),
            "-u",
            str(request.scale),
        ]
        if request.tile_size:
            argv += ["--tile_size", str(request.tile_size)]
        if not one_step:
            argv += [
                "--infer_steps",
                str(request.extra_options.get("infer_steps", 25)),
                "--cfg_scale",
                str(request.extra_options.get("cfg_scale", 0.5)),
                "--weak_cond_strength_aelq",
                str(request.extra_options.get("weak_cond_strength_aelq", 0.1)),
            ]
        return CommandPlan(argv=argv, cwd=runtime.workdir, output_dir=stage_output_dir)

    if profile == "configured_external":
        executable = _required(runtime, "executable")
        args = runtime.paths.get("args", "")
        tokens = [token for token in args.split("\u001f") if token]
        replacements = {
            "{input}": str(input_path),
            "{input_dir}": str(stage_input_dir),
            "{output_dir}": str(stage_output_dir),
            "{scale}": str(request.scale),
            "{device}": request.device,
            "{precision}": request.precision,
            "{seed}": str(request.seed),
        }
        rendered: list[str] = []
        for token in tokens:
            for key, value in replacements.items():
                token = token.replace(key, value)
            rendered.append(token)
        return CommandPlan(
            argv=[executable, *rendered], cwd=runtime.workdir, output_dir=stage_output_dir
        )

    raise ValueError(f"unsupported command profile: {profile}")
