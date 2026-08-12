from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import TypeAdapter

from .schemas import RuntimeConfig


def default_runtime_config_path() -> Path:
    override = os.environ.get("SR_STUDIO_RUNTIME_CONFIG")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".config" / "sr-studio" / "runtimes.json"


def load_runtime_configs(path: Path | None = None) -> dict[str, RuntimeConfig]:
    target = path or default_runtime_config_path()
    if not target.exists():
        return {}
    raw = json.loads(target.read_text(encoding="utf-8"))
    configs = TypeAdapter(list[RuntimeConfig]).validate_python(raw)
    return {cfg.model_id: cfg for cfg in configs}
