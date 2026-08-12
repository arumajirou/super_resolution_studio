# HANDOFF

Next execution environment should:

1. Re-run `uv sync --all-groups` and all local quality gates.
2. Configure one research model runtime at a time.
3. Start with FiDeSR or TinySR, then VOSR 0.5B one-step, then SeedVR2.
4. Record load/inference/output/VRAM evidence; do not mark a model verified from catalog presence alone.
5. Create `arumajirou/super_resolution_studio`, attach project tracking, push design-first history and open a Draft PR for implementation if repository creation becomes available.
