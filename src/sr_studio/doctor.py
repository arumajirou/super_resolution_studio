from __future__ import annotations

import json
import platform
import shutil
import sys
from typing import Any

from .catalog import MODEL_SPECS
from .registry import ProviderRegistry


def collect_doctor() -> dict[str, Any]:
    registry = ProviderRegistry()
    models = []
    for spec in MODEL_SPECS:
        health = registry.get(spec.id).doctor()
        models.append(
            {
                "id": spec.id,
                "catalog_status": spec.status.value,
                "ready": health.ready,
                "runtime_status": health.status,
                "details": health.details,
            }
        )
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "nvidia_smi": shutil.which("nvidia-smi"),
        "models": models,
    }


def collect_doctor_json() -> str:
    return json.dumps(collect_doctor(), indent=2, ensure_ascii=False)
