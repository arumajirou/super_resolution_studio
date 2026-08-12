from __future__ import annotations

from .schemas import ModelSpec, ModelStatus, RuntimeKind


def _external(
    model_id: str,
    name: str,
    family: str,
    status: ModelStatus,
    source: str,
    hf: str | None,
    profile: str,
    hardware: str,
    *,
    tile: bool = False,
    notes: str = "",
) -> ModelSpec:
    return ModelSpec(
        id=model_id,
        display_name=name,
        family=family,
        status=status,
        source_repo=source,
        hf_repo=hf,
        license="Apache-2.0",
        runtime_kind=RuntimeKind.EXTERNAL,
        supported_scales=(4,),
        default_scale=4,
        supports_tile=tile,
        hardware_notes=hardware,
        command_profile=profile,
        notes=notes,
    )


MODEL_SPECS: tuple[ModelSpec, ...] = (
    ModelSpec(
        id="pillow-lanczos",
        display_name="Pillow Lanczos (baseline)",
        family="classical",
        status=ModelStatus.VERIFIED_BASELINE,
        license="HPND",
        runtime_kind=RuntimeKind.NATIVE,
        supported_scales=(2, 4, 8),
        default_scale=4,
        hardware_notes="CPU; no model download",
        notes="Deterministic baseline and smoke-test provider.",
    ),
    _external(
        "fidesr",
        "FiDeSR",
        "one-step-diffusion",
        ModelStatus.READY_TO_INSTALL,
        "https://github.com/Ar0Kim/FiDeSR",
        "jmjin2/FiDeSR",
        "fidesr",
        "GPU recommended; upstream uses Python 3.10 and Stable Diffusion 2.1 assets.",
        notes="CVPR 2026; fidelity/detail-oriented x4 real-world SR.",
    ),
    _external(
        "tinysr",
        "TinySR",
        "compact-dit",
        ModelStatus.READY_TO_INSTALL,
        "https://github.com/Microtreei/TinySR",
        None,
        "tinysr",
        "CUDA GPU; upstream command uses fp16 and supports tiled inference.",
        tile=True,
        notes="CVPR 2026 Findings; compact DiT; x4.",
    ),
    _external(
        "vosr-0.5b-one-step",
        "VOSR 0.5B one-step",
        "vision-only-diffusion",
        ModelStatus.READY_TO_INSTALL,
        "https://github.com/cswry/VOSR",
        "CSWRY/VOSR",
        "vosr_onestep_0_5b",
        "Single CUDA GPU; use tile_size for large images.",
        tile=True,
    ),
    _external(
        "vosr-0.5b-multi-step",
        "VOSR 0.5B multi-step",
        "vision-only-diffusion",
        ModelStatus.READY_TO_INSTALL,
        "https://github.com/cswry/VOSR",
        "CSWRY/VOSR",
        "vosr_multistep_0_5b",
        "Single CUDA GPU; default upstream sampling is 25 steps.",
        tile=True,
    ),
    _external(
        "vosr-1.4b-one-step",
        "VOSR 1.4B one-step",
        "vision-only-diffusion",
        ModelStatus.READY_TO_INSTALL,
        "https://github.com/cswry/VOSR",
        "CSWRY/VOSR",
        "vosr_onestep_1_4b",
        "Heavier single-GPU path; Qwen-Image 2D VAE assets.",
        tile=True,
    ),
    _external(
        "vosr-1.4b-multi-step",
        "VOSR 1.4B multi-step",
        "vision-only-diffusion",
        ModelStatus.READY_TO_INSTALL,
        "https://github.com/cswry/VOSR",
        "CSWRY/VOSR",
        "vosr_multistep_1_4b",
        "Heavier multi-step path; Qwen-Image 2D VAE assets.",
        tile=True,
    ),
    _external(
        "seedvr2-3b",
        "SeedVR2 3B",
        "one-step-video-restoration-dit",
        ModelStatus.READY_TO_INSTALL,
        "https://github.com/ByteDance-Seed/SeedVR",
        "ByteDance-Seed/SeedVR2-3B",
        "configured_external",
        "Large model assets (~14.6 GB HF repository); isolate runtime and verify VRAM locally.",
        tile=True,
        notes=(
            "Upstream is video restoration; image upscaling is supported by "
            "demo/community runtimes."
        ),
    ),
    _external(
        "dreamsr",
        "DreamSR",
        "ultra-high-resolution-dit",
        ModelStatus.EXPERIMENTAL,
        "https://github.com/jerrydong0219/DreamSR",
        None,
        "configured_external",
        "High-resolution patch-oriented diffusion path; runtime contract pending certification.",
        tile=True,
    ),
    _external(
        "teasr",
        "TEASR",
        "any-step-dit",
        ModelStatus.EXPERIMENTAL_HEAVY,
        "https://github.com/frxg/TEASR",
        "frxg/TEASR",
        "configured_external",
        "Very heavy DiT path; upstream research targets any-step inference.",
        tile=True,
    ),
    _external(
        "odtsr",
        "ODTSR",
        "controllable-one-step-dit",
        ModelStatus.EXPERIMENTAL_HEAVY,
        "https://github.com/Double8fun/ODTSR",
        "double8fun/ODTSR",
        "configured_external",
        "Qwen-Image based; high VRAM requirement reported upstream.",
        tile=True,
    ),
    _external(
        "pgsr",
        "PGSR",
        "pixel-grounded-dit",
        ModelStatus.BLOCKED_CHECKPOINT,
        "https://github.com/yushi928/PGSR",
        None,
        "configured_external",
        "Dedicated checkpoint unavailable in the 2026-08-12 research snapshot.",
        tile=True,
        notes="Catalog-only until a dedicated pretrained checkpoint is published.",
    ),
)


CATALOG: dict[str, ModelSpec] = {spec.id: spec for spec in MODEL_SPECS}


def get_model_spec(model_id: str) -> ModelSpec:
    try:
        return CATALOG[model_id]
    except KeyError as exc:
        raise KeyError(f"unknown model_id: {model_id}") from exc
