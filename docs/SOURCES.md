# AUTHORITATIVE SOURCES

Verified during design on 2026-08-12:

- FiDeSR: https://github.com/Ar0Kim/FiDeSR — official README documents Python 3.10, pretrained assets and `test_fidesr.py` x4 invocation; Apache-2.0.
- TinySR: https://github.com/Microtreei/TinySR — official README documents inference code/models, x4 command and tile-related flags; Apache-2.0.
- VOSR: https://github.com/cswry/VOSR — official README documents HF `CSWRY/VOSR`, 0.5B/1.4B, one-step/multi-step entrypoints and tile size.
- SeedVR2-3B: https://huggingface.co/ByteDance-Seed/SeedVR2-3B — official model card/license; upstream model repository is 14.6 GB at the verified snapshot.
- PGSR paper: https://arxiv.org/abs/2608.09133 — published 2026-08-10; catalog status remains blocked until a dedicated checkpoint is available.
- CVPR 2026 VOSR paper: https://openaccess.thecvf.com/content/CVPR2026/html/Wu_VOSR_A_Vision-Only_Generative_Model_for_Image_Super-Resolution_CVPR_2026_paper.html
- CVPR 2026 FiDeSR paper: https://openaccess.thecvf.com/content/CVPR2026/html/Kim_FiDeSR_High-Fidelity_and_Detail-Preserving_One-Step_Diffusion_Super-Resolution_CVPR_2026_paper.html

## Core dependency snapshot (2026-08-12)

The project declaration targets the then-current stable releases: Gradio 6.20.0, Pillow 12.3.0, Pydantic 2.13.4, Typer 0.27.0, pytest 9.1.1, pytest-cov 7.1.0, Ruff 0.15.22, mypy 2.3.0 and Hatchling 1.31.0. The final lock could not be generated in this execution environment because PyPI DNS resolution was unavailable; rerun `uv lock`/`uv sync --all-groups` when network access is restored.
