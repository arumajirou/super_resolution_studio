from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..schemas import ProviderHealth, ProviderResult, UpscaleRequest


class Provider(ABC):
    @abstractmethod
    def doctor(self) -> ProviderHealth: ...

    @abstractmethod
    def upscale_one(
        self, input_path: Path, output_path: Path, request: UpscaleRequest
    ) -> ProviderResult: ...
