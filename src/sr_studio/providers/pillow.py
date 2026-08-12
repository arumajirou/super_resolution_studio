from __future__ import annotations

from pathlib import Path

from PIL import Image

from ..schemas import ProviderHealth, ProviderResult, UpscaleRequest
from .base import Provider


class PillowLanczosProvider(Provider):
    model_id = "pillow-lanczos"

    def doctor(self) -> ProviderHealth:
        return ProviderHealth(model_id=self.model_id, ready=True, status="READY")

    def upscale_one(
        self, input_path: Path, output_path: Path, request: UpscaleRequest
    ) -> ProviderResult:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(input_path) as image:
            image.load()
            width, height = image.size
            resized = image.resize(
                (width * request.scale, height * request.scale), Image.Resampling.LANCZOS
            )
            resized.save(output_path)
        return ProviderResult(output_path=output_path, exit_code=0)
