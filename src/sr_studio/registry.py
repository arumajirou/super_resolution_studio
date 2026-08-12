from __future__ import annotations

from .catalog import get_model_spec
from .providers import ExternalCommandProvider, PillowLanczosProvider, Provider
from .runtime import load_runtime_configs
from .schemas import RuntimeKind


class ProviderRegistry:
    def __init__(self) -> None:
        self._runtime_configs = load_runtime_configs()

    def get(self, model_id: str) -> Provider:
        spec = get_model_spec(model_id)
        if spec.runtime_kind is RuntimeKind.NATIVE:
            if spec.id == "pillow-lanczos":
                return PillowLanczosProvider()
            raise KeyError(f"no native provider for {spec.id}")
        return ExternalCommandProvider(spec, self._runtime_configs.get(spec.id))
