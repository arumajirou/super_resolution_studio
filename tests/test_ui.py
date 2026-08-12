import gradio as gr

from sr_studio.ui import create_app


def test_ui_builds_without_loading_gpu_models() -> None:
    app = create_app()
    assert isinstance(app, gr.Blocks)
