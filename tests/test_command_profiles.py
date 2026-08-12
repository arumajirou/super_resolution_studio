from pathlib import Path

from sr_studio.catalog import get_model_spec
from sr_studio.command_profiles import build_command_plan
from sr_studio.schemas import RuntimeConfig, UpscaleRequest


def _request(model_id: str) -> UpscaleRequest:
    return UpscaleRequest(
        model_id=model_id,
        inputs=[Path("/tmp/input.png")],
        output_dir=Path("/tmp/out"),
        scale=4,
        tile_size=512,
    )


def test_fidesr_command_matches_official_contract(tmp_path: Path) -> None:
    runtime = RuntimeConfig(
        model_id="fidesr",
        workdir=tmp_path,
        python_executable=Path("/venv/bin/python"),
        paths={"base_model": "/models/sd21", "checkpoint": "/models/fidesr.pkl"},
    )
    plan = build_command_plan(
        get_model_spec("fidesr"),
        runtime,
        _request("fidesr"),
        Path("/tmp/input.png"),
        Path("/tmp/stage-in"),
        Path("/tmp/stage-out"),
    )
    assert plan.argv[:2] == ["/venv/bin/python", str(tmp_path / "test_fidesr.py")]
    assert "--pretrained_model_path" in plan.argv
    assert "--pretrained_path" in plan.argv
    assert "--input_image" in plan.argv
    assert "--output_dir" in plan.argv
    assert all(token not in {";", "&&", "|"} for token in plan.argv)


def test_tinysr_command_has_tile_and_fp16_contract(tmp_path: Path) -> None:
    runtime = RuntimeConfig(
        model_id="tinysr",
        workdir=tmp_path,
        python_executable=Path("/venv/bin/python"),
        paths={
            "backbone": "/m/backbone",
            "vae": "/m/vae",
            "lora": "/m/lora",
            "embedding": "/m/embedding",
        },
    )
    plan = build_command_plan(
        get_model_spec("tinysr"),
        runtime,
        _request("tinysr"),
        Path("/tmp/input.png"),
        Path("/tmp/stage-in"),
        Path("/tmp/stage-out"),
    )
    assert "--is_use_tile=True" in plan.argv
    assert "--mixed_precision=fp16" in plan.argv
    assert "--upscale=4" in plan.argv


def test_vosr_command_selects_onestep_script(tmp_path: Path) -> None:
    runtime = RuntimeConfig(
        model_id="vosr-0.5b-one-step",
        workdir=tmp_path,
        python_executable=Path("/venv/bin/python"),
        paths={"checkpoint_0.5B_os": "/m/vosr05-os"},
    )
    plan = build_command_plan(
        get_model_spec("vosr-0.5b-one-step"),
        runtime,
        _request("vosr-0.5b-one-step"),
        Path("/tmp/input.png"),
        Path("/tmp/stage-in"),
        Path("/tmp/stage-out"),
    )
    assert plan.argv[1].endswith("inference_vosr_onestep.py")
    assert plan.argv[plan.argv.index("-u") + 1] == "4"
    assert "--tile_size" in plan.argv
