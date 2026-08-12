# REQUIREMENTS

1. Accept one image or a directory/batch from UI and CLI.
2. Select models from a registry; adding a model must not require UI changes.
3. Keep core dependencies separate from each heavy research model runtime.
4. Save per-run model/request snapshots, hashes, timestamps, exit status and per-file results.
5. Continue a batch after an individual file failure.
6. Never execute free-form shell text; external providers use argv with `shell=False`.
7. Provide a CPU baseline that works without model downloads.
8. Initial providers: FiDeSR, TinySR, VOSR 0.5B/1.4B, SeedVR2-3B; catalog DreamSR/TEASR/ODTSR; block PGSR until checkpoint availability.
9. Local quality gate: Ruff, mypy, pytest, package/smoke, secrets check before publish.
10. Real research providers become VERIFIED only after actual load + inference + output validation.
11. Support optional configured input/output filesystem roots and reject resolved paths outside them before inference.
12. Record runtime environment metadata, provider argv, process-log paths and hashes in run evidence where applicable.
