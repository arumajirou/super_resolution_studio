from sr_studio.catalog import MODEL_SPECS, get_model_spec
from sr_studio.schemas import ModelStatus


def test_catalog_contains_expected_models() -> None:
    ids = {spec.id for spec in MODEL_SPECS}
    assert len(ids) >= 12
    assert {"fidesr", "tinysr", "vosr-0.5b-one-step", "seedvr2-3b", "pgsr"} <= ids


def test_pgsr_is_blocked_until_checkpoint() -> None:
    assert get_model_spec("pgsr").status is ModelStatus.BLOCKED_CHECKPOINT


def test_baseline_supports_multiple_scales() -> None:
    assert get_model_spec("pillow-lanczos").supported_scales == (2, 4, 8)
