from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from .catalog import MODEL_SPECS
from .doctor import collect_doctor_json
from .engine import run_upscale
from .schemas import UpscaleRequest

app = typer.Typer(no_args_is_help=True, help="Multi-model image super-resolution studio")


@app.command("models")
def models() -> None:
    for spec in MODEL_SPECS:
        typer.echo(
            f"{spec.id:24} {spec.status.value:22} scale={spec.supported_scales} "
            f"hf={spec.hf_repo or '-'}"
        )


@app.command("doctor")
def doctor() -> None:
    typer.echo(collect_doctor_json())


@app.command("upscale")
def upscale(
    input_path: Annotated[Path, typer.Argument(exists=True, readable=True)],
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o")] = Path("outputs"),
    model: Annotated[str, typer.Option("--model", "-m")] = "pillow-lanczos",
    scale: Annotated[int, typer.Option("--scale", "-s")] = 4,
    tile_size: Annotated[int, typer.Option("--tile-size")] = 0,
) -> None:
    request = UpscaleRequest(
        model_id=model,
        inputs=[input_path],
        output_dir=output_dir,
        scale=scale,
        tile_size=tile_size or None,
    )
    manifest = run_upscale(request)
    typer.echo(json.dumps(manifest.model_dump(mode="json"), indent=2, ensure_ascii=False))


@app.command("batch")
def batch(
    input_dir: Annotated[Path, typer.Argument(exists=True, file_okay=False, readable=True)],
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o")] = Path("outputs"),
    model: Annotated[str, typer.Option("--model", "-m")] = "pillow-lanczos",
    scale: Annotated[int, typer.Option("--scale", "-s")] = 4,
    tile_size: Annotated[int, typer.Option("--tile-size")] = 0,
) -> None:
    request = UpscaleRequest(
        model_id=model,
        inputs=[input_dir],
        output_dir=output_dir,
        scale=scale,
        tile_size=tile_size or None,
    )
    manifest = run_upscale(request)
    typer.echo(json.dumps(manifest.model_dump(mode="json"), indent=2, ensure_ascii=False))


@app.command("ui")
def ui() -> None:
    from .ui import launch

    launch()
