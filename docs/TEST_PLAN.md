# TEST PLAN

Core CI must not download multi-GB checkpoints.

- Catalog/schema contract tests.
- Official command-argument generation tests for FiDeSR/TinySR/VOSR.
- Baseline single-image x4 E2E.
- Directory batch with one corrupt image to verify failure isolation.
- Doctor probe without model loading.
- UI construction smoke test.
- Ruff format/check, strict mypy and pytest.

GPU certification is separate and must record model/revision/runtime/CUDA/GPU/VRAM/input/output/hash/timing evidence.
- Configured input/output root sandbox acceptance and escape rejection.
- PGSR blocked-checkpoint refusal before execution.
- Configured-external runtime doctor rejects missing executable.
- Provider timeout is recorded as a per-file `TIMEOUT` without corrupting batch state.
- Directory symlink escape is rejected when input roots are configured.
