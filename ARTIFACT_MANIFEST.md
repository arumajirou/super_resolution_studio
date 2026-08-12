# ARTIFACT MANIFEST

## Tracked deliverables

- `README.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`, `SHA256SUMS`
- `src/sr_studio/` — CLI/UI, model catalog, registry, engine, runtime adapters, provenance and path sandbox
- `tests/` — catalog, command-contract, engine, doctor, UI, external-runtime and security tests
- `runtime_specs/runtimes.example.json` — isolated runtime configuration template
- `docs/REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/DETAILED_DESIGN.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/TEST_PLAN.md`
- `docs/MODEL_MATRIX.md`
- `docs/RUNBOOK.md`
- `docs/VERIFICATION_REPORT.md`
- `docs/HANDOFF.md`
- `docs/SOURCES.md`
- `docs/PROJECT_TRACKING.md`

## Generated evidence in the downloadable bundle

The final ZIP also includes `evidence/` with dependency-blocker logs, final pytest/compile/secret-scan logs, CLI baseline output, run manifest, UI HTTP smoke and checksum verification. Evidence is intentionally ignored by Git because it is run-specific.

## Deliberate exclusions

- Research model weights/checkpoints and cloned upstream repositories are not bundled.
- `.venv`, caches, `.git`, generated build directories and UI output caches are not bundled.
- `uv.lock` is absent because the execution container could not resolve PyPI and the required dependency metadata was not present in the local uv cache; this is recorded as BLOCKED rather than fabricated.

## Verification state

Core implementation: **VERIFIED for the built-in baseline / PARTIALLY_VERIFIED overall**. Real GPU inference certification for research providers and publication to a newly created GitHub repository remain separate gates.
