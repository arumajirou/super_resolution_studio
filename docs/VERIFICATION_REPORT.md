# VERIFICATION REPORT

Verification date: 2026-08-12.

## EXECUTED / VERIFIED

- Design-first local Git history exists before implementation (`d1700bc` design gate, then implementation commits).
- `python -m compileall` over `src` and `tests`: PASS.
- `pytest`: **16 passed** after the final security/provenance hardening.
- Baseline CLI end-to-end: PASS. A generated 12×10 PNG was upscaled x4 to 48×40.
- Baseline run manifest: PASS. Input/output SHA-256 and environment snapshot are recorded; output is readable.
- Gradio UI construction test: PASS without loading GPU models.
- Gradio local server smoke: PASS; HTTP 200 from `127.0.0.1:7866`.
- Batch failure isolation: PASS; a corrupt image fails without preventing valid-image completion.
- Timeout isolation: PASS; provider timeout maps to per-file `TIMEOUT`.
- Configurable input/output root sandbox: PASS for accepted paths and rejected escapes.
- External configured runtime doctor: PASS for missing-executable detection.
- PGSR blocked-checkpoint gate: PASS; execution is refused before inference.
- FiDeSR/TinySR/VOSR command-generation contract tests: PASS.
- High-confidence tracked-file secret scan: PASS / no matches.

## PARTIALLY VERIFIED

- Core functionality is verified using packages already present in the execution environment.
- Real GPU inference for FiDeSR, TinySR, VOSR, SeedVR2, DreamSR, TEASR and ODTSR was **not executed** here. Catalog presence, command generation or weight availability is not treated as inference evidence.

## BLOCKED

- `uv sync --all-groups`: BLOCKED by the execution container's DNS/network failure when resolving PyPI (`pypi.org`), not by a dependency-resolution conflict proven in this run.
- `uv.lock`: BLOCKED because dependency metadata required to resolve the lock is not present in the local uv cache while the network is unavailable.
- Ruff and mypy: BLOCKED because they are not preinstalled and PyPI is unreachable. Therefore the full declared local quality gate is **PARTIALLY_VERIFIED**, not fully VERIFIED.
- GitHub repository and GitHub Project creation: BLOCKED because the connected GitHub action set exposes operations inside existing repositories but no repository/project creation operation, and this runtime has no local `gh` binary.
- Hugging Face plugin: upstream 502 during this turn; public official model pages/repositories were used for source verification, but no user-account mutation was performed.

## Final evidence paths

- `evidence/bootstrap/uv-sync.log`
- `evidence/uv-lock-offline.log`
- `evidence/final/secret-scan.txt`
- `evidence/final/compileall.log`
- `evidence/final/pytest.log`
- `evidence/final/uv-lock-offline.log`
- `evidence/final/uv-build-offline.log`
- `evidence/final/models.txt`
- `evidence/final/doctor.json`
- `evidence/final/ui-smoke.txt`
- `evidence/final/smoke/cli-output.json`
- `evidence/final/smoke/output/<run_id>/manifest.json`

## Dependency declaration note

`pyproject.toml` was updated against current PyPI stable releases on 2026-08-12. The smoke environment itself contains Gradio 6.5.1 and Typer 0.26.3, so exact execution against the newly declared Gradio 6.20.0 / Typer 0.27.0 stack remains **EXECUTION_PENDING** until dependency download is possible. This is why the dependency-level gate remains PARTIALLY_VERIFIED.
