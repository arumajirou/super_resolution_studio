# DETAILED DESIGN

Core Pydantic schemas: `ModelSpec`, `RuntimeConfig`, `UpscaleRequest`, `ProviderHealth`, `ProviderResult`, `FileResult`, `RunManifest`.

Providers implement `doctor()` and `upscale_one()`. The external provider stages one input, builds an official/provider-specific argv, invokes it with `shell=False`, validates an image output and copies it to the run output path.

Run layout: `<output>/<run_id>/<model_id>/...` plus `<output>/<run_id>/manifest.json`.

FiDeSR command profile is based on `test_fidesr.py`; TinySR on `test/test_tinysr.py`; VOSR selects `inference_vosr.py` or `inference_vosr_onestep.py` and 0.5B/1.4B checkpoint keys.
