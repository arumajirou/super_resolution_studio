from pathlib import Path

from sr_studio.catalog import get_model_spec
from sr_studio.providers.external import ExternalCommandProvider
from sr_studio.schemas import RuntimeConfig


def test_configured_external_doctor_requires_executable(tmp_path: Path) -> None:
    runtime = RuntimeConfig(
        model_id="seedvr2-3b",
        workdir=tmp_path,
        python_executable=Path("/unused/python"),
        paths={"executable": str(tmp_path / "missing")},
    )
    provider = ExternalCommandProvider(get_model_spec("seedvr2-3b"), runtime)
    health = provider.doctor()
    assert not health.ready
    assert health.status == "BLOCKED"
    assert any("executable missing" in item for item in health.details)
