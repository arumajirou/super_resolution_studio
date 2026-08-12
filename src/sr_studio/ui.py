from __future__ import annotations

import json
from pathlib import Path

import gradio as gr

from .catalog import MODEL_SPECS, get_model_spec
from .doctor import collect_doctor_json
from .engine import run_upscale
from .schemas import UpscaleRequest


def _model_choices() -> list[tuple[str, str]]:
    return [(f"{spec.display_name} [{spec.status.value}]", spec.id) for spec in MODEL_SPECS]


def _model_table_markdown() -> str:
    rows = [
        "| Model | Status | HF | Tile | Hardware |",
        "|---|---|---|---:|---|",
    ]
    for spec in MODEL_SPECS:
        rows.append(
            f"| `{spec.id}` | {spec.status.value} | {spec.hf_repo or '-'} | "
            f"{'yes' if spec.supports_tile else 'no'} | {spec.hardware_notes} |"
        )
    return "\n".join(rows)


def _single_run(
    image_path: str | None, model_id: str, scale: int, tile_size: int, output_dir: str
) -> tuple[str | None, str, str | None]:
    if not image_path:
        return None, "No image selected", None
    request = UpscaleRequest(
        model_id=model_id,
        inputs=[Path(image_path)],
        output_dir=Path(output_dir).expanduser(),
        scale=int(scale),
        tile_size=int(tile_size) if tile_size > 0 else None,
    )
    manifest = run_upscale(request)
    succeeded = next((r for r in manifest.results if r.output_path), None)
    manifest_path = request.output_dir.resolve() / manifest.run_id / "manifest.json"
    return (
        str(succeeded.output_path) if succeeded and succeeded.output_path else None,
        json.dumps(manifest.model_dump(mode="json"), indent=2, ensure_ascii=False),
        str(manifest_path),
    )


def _batch_run(
    files: list[str] | None, model_id: str, scale: int, tile_size: int, output_dir: str
) -> tuple[str, list[str], str | None]:
    if not files:
        return "No files selected", [], None
    request = UpscaleRequest(
        model_id=model_id,
        inputs=[Path(item) for item in files],
        output_dir=Path(output_dir).expanduser(),
        scale=int(scale),
        tile_size=int(tile_size) if tile_size > 0 else None,
    )
    manifest = run_upscale(request)
    outputs = [str(item.output_path) for item in manifest.results if item.output_path]
    manifest_path = request.output_dir.resolve() / manifest.run_id / "manifest.json"
    return (
        json.dumps(manifest.model_dump(mode="json"), indent=2, ensure_ascii=False),
        outputs,
        str(manifest_path),
    )


def create_app() -> gr.Blocks:
    choices = _model_choices()
    default_model = "pillow-lanczos"
    with gr.Blocks(title="Super Resolution Studio") as demo:
        gr.Markdown("# Super Resolution Studio\nMulti-model image super-resolution control plane.")
        with gr.Tab("Single image"):
            with gr.Row():
                source = gr.Image(type="filepath", label="Input image")
                result_image = gr.Image(type="filepath", label="Upscaled output")
            model = gr.Dropdown(choices=choices, value=default_model, label="Model")
            scale = gr.Dropdown(choices=[2, 4, 8], value=4, label="Scale")
            tile = gr.Slider(0, 2048, value=0, step=64, label="Tile size (0 = disabled)")
            out_dir = gr.Textbox(value=str(Path.cwd() / "outputs"), label="Output directory")
            run = gr.Button("Upscale", variant="primary")
            log = gr.Code(label="Run manifest preview", language="json")
            manifest_file = gr.File(label="Manifest")
            run.click(
                _single_run,
                inputs=[source, model, scale, tile, out_dir],
                outputs=[result_image, log, manifest_file],
            )

        with gr.Tab("Directory / batch"):
            files = gr.File(
                file_count="directory",
                file_types=["image"],
                type="filepath",
                label="Image directory",
            )
            batch_model = gr.Dropdown(choices=choices, value=default_model, label="Model")
            batch_scale = gr.Dropdown(choices=[2, 4, 8], value=4, label="Scale")
            batch_tile = gr.Slider(0, 2048, value=0, step=64, label="Tile size")
            batch_out = gr.Textbox(value=str(Path.cwd() / "outputs"), label="Output directory")
            batch_run = gr.Button("Run batch", variant="primary")
            batch_log = gr.Code(label="Batch manifest", language="json")
            batch_outputs = gr.File(file_count="multiple", label="Upscaled outputs")
            batch_manifest = gr.File(label="Manifest")
            batch_run.click(
                _batch_run,
                inputs=[files, batch_model, batch_scale, batch_tile, batch_out],
                outputs=[batch_log, batch_outputs, batch_manifest],
            )

        with gr.Tab("Models"):
            gr.Markdown(_model_table_markdown())

        with gr.Tab("Diagnostics"):
            doctor_output = gr.Code(label="Doctor", language="json")
            gr.Button("Refresh diagnostics").click(collect_doctor_json, outputs=doctor_output)

    return demo


def launch() -> None:
    create_app().queue(default_concurrency_limit=1).launch()
