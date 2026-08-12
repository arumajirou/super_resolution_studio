from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def _configured_roots(name: str) -> tuple[Path, ...]:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return ()
    return tuple(
        Path(item).expanduser().resolve()
        for item in raw.split(os.pathsep)
        if item.strip()
    )


def allowed_input_roots() -> tuple[Path, ...]:
    return _configured_roots("SR_STUDIO_ALLOWED_INPUT_ROOTS")


def allowed_output_roots() -> tuple[Path, ...]:
    return _configured_roots("SR_STUDIO_ALLOWED_OUTPUT_ROOTS")


def _is_within(path: Path, roots: Iterable[Path]) -> bool:
    for root in roots:
        try:
            path.relative_to(root)
        except ValueError:
            continue
        return True
    return False


def validate_path(path: Path, roots: tuple[Path, ...], *, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if roots and not _is_within(resolved, roots):
        rendered = ", ".join(str(root) for root in roots)
        raise ValueError(
            f"{label} path is outside configured roots: {resolved}; allowed={rendered}"
        )
    return resolved


def validate_input_path(path: Path) -> Path:
    return validate_path(path, allowed_input_roots(), label="input")


def validate_output_path(path: Path) -> Path:
    return validate_path(path, allowed_output_roots(), label="output")
