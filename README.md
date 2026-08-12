# Super Resolution Studio

A design-first, multi-model image super-resolution control plane with a Gradio UI and CLI.

## What works in the core release

- Single-image and directory/batch processing.
- Built-in Pillow Lanczos baseline (CPU, no model downloads).
- Model catalog with FiDeSR, TinySR, VOSR, SeedVR2, DreamSR, TEASR, ODTSR and PGSR status metadata.
- Safe isolated external-runtime adapters for FiDeSR, TinySR and VOSR command contracts.
- Generic configured adapter for SeedVR2 and experimental providers.
- Per-run JSON manifest, input/output SHA-256 and per-file failure isolation.
- `models`, `doctor`, `upscale`, `batch`, and `ui` CLI commands.

## Why runtimes are isolated

Current SR research implementations pin different Python/PyTorch/CUDA/dependency combinations. The core app never imports those heavy stacks. Each research model gets its own runtime and checkpoint directory, which avoids dependency conflicts and makes certification evidence model-specific.

## Setup

```bash
uv sync --all-groups
uv run sr-studio models
uv run sr-studio doctor
uv run sr-studio ui
```

## Baseline CLI

```bash
uv run sr-studio upscale input.png -o outputs --model pillow-lanczos --scale 4
uv run sr-studio batch ./photos -o outputs --model pillow-lanczos --scale 4
```

## External runtimes

Copy `runtime_specs/runtimes.example.json` to `~/.config/sr-studio/runtimes.json` and replace all paths with your installed upstream repositories, Python executables, and checkpoints.

A catalog entry is not evidence that a model has been executed. Use `doctor` and the GPU certification workflow before promoting a research model to verified.

See `docs/` for requirements, architecture, detailed design, test plan, model matrix, runbook and verification status.
