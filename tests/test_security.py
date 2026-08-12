from pathlib import Path

import pytest

from sr_studio.security import validate_input_path, validate_output_path


def test_input_root_policy_accepts_inside_and_rejects_outside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    inside = allowed / "image.png"
    inside.write_bytes(b"x")
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"x")
    monkeypatch.setenv("SR_STUDIO_ALLOWED_INPUT_ROOTS", str(allowed))
    assert validate_input_path(inside) == inside.resolve()
    with pytest.raises(ValueError, match="outside configured roots"):
        validate_input_path(outside)


def test_output_root_policy_rejects_escape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    allowed = tmp_path / "outputs"
    allowed.mkdir()
    monkeypatch.setenv("SR_STUDIO_ALLOWED_OUTPUT_ROOTS", str(allowed))
    assert validate_output_path(allowed / "nested") == (allowed / "nested").resolve()
    with pytest.raises(ValueError, match="outside configured roots"):
        validate_output_path(tmp_path / "escape")


def test_directory_symlink_cannot_escape_input_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sr_studio.engine import expand_inputs

    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"x")
    link = allowed / "linked.png"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")
    monkeypatch.setenv("SR_STUDIO_ALLOWED_INPUT_ROOTS", str(allowed))
    with pytest.raises(ValueError, match="outside configured roots"):
        expand_inputs([allowed])
