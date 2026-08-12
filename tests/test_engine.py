import json
from pathlib import Path

from PIL import Image
import pytest

from sr_studio.engine import run_upscale
from sr_studio.schemas import ResultStatus, UpscaleRequest


def _make_image(path: Path, size: tuple[int, int] = (8, 6)) -> None:
    Image.new("RGB", size, (20, 40, 60)).save(path)


def test_pillow_single_end_to_end(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    _make_image(source)
    request = UpscaleRequest(
        model_id="pillow-lanczos",
        inputs=[source],
        output_dir=tmp_path / "outputs",
        scale=4,
    )
    manifest = run_upscale(request)
    assert manifest.status == "SUCCEEDED"
    result = manifest.results[0]
    assert result.status is ResultStatus.SUCCEEDED
    assert result.input_sha256 and result.output_sha256
    assert result.output_path is not None
    with Image.open(result.output_path) as image:
        assert image.size == (32, 24)
    manifest_path = request.output_dir / manifest.run_id / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == manifest.run_id


def test_directory_batch_and_failure_isolation(tmp_path: Path) -> None:
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    _make_image(inputs / "good.png")
    (inputs / "bad.jpg").write_text("not-an-image", encoding="utf-8")
    request = UpscaleRequest(
        model_id="pillow-lanczos",
        inputs=[inputs],
        output_dir=tmp_path / "outputs",
        scale=2,
    )
    manifest = run_upscale(request)
    statuses = {result.input_path.name: result.status for result in manifest.results}
    assert statuses["good.png"] is ResultStatus.SUCCEEDED
    assert statuses["bad.jpg"] is ResultStatus.FAILED
    assert manifest.status == "PARTIAL_OR_FAILED"


def test_blocked_checkpoint_is_refused_before_execution(tmp_path: Path) -> None:
    request = UpscaleRequest(
        model_id="pgsr",
        inputs=[tmp_path / "never-read.png"],
        output_dir=tmp_path / "outputs",
        scale=4,
    )
    with pytest.raises(RuntimeError, match="blocked"):
        run_upscale(request)


def test_timeout_is_recorded_per_file(tmp_path: Path) -> None:
    import subprocess

    from sr_studio.schemas import ProviderResult

    class TimeoutProvider:
        def upscale_one(
            self, input_path: Path, output_path: Path, request: UpscaleRequest
        ) -> ProviderResult:
            raise subprocess.TimeoutExpired(cmd=["fake-provider"], timeout=1)

    class Registry:
        def get(self, model_id: str) -> TimeoutProvider:
            return TimeoutProvider()

    source = tmp_path / "source.png"
    _make_image(source)
    request = UpscaleRequest(
        model_id="pillow-lanczos",
        inputs=[source],
        output_dir=tmp_path / "outputs",
        scale=4,
    )
    manifest = run_upscale(request, registry=Registry())  # type: ignore[arg-type]
    assert manifest.results[0].status is ResultStatus.TIMEOUT
    assert manifest.status == "PARTIAL_OR_FAILED"
