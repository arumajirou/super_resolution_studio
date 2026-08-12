# RUNBOOK

## Core

```bash
cd /absolute/path/to/super_resolution_studio
uv sync --all-groups
uv run sr-studio doctor
uv run sr-studio ui
```

## Runtime configuration

Copy `runtime_specs/runtimes.example.json` to `~/.config/sr-studio/runtimes.json` and edit paths. The core process does not activate provider environments; it invokes the configured Python executable directly.

## Evidence
Every run writes `manifest.json`; successful files include both input and output SHA-256. Keep GPU certification logs under `evidence/<model>/<run_id>/`.

## Optional path sandbox

To constrain local inputs/outputs, set OS-path-separator-delimited roots before launching the CLI/UI:

```bash
export SR_STUDIO_ALLOWED_INPUT_ROOTS="/data/photos:/data/scans"
export SR_STUDIO_ALLOWED_OUTPUT_ROOTS="/data/sr-output"
uv run sr-studio ui
```

When unset, the local desktop application accepts user-selected filesystem paths. When set, resolved paths outside the configured roots are rejected before inference.
