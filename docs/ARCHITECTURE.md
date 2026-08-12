# ARCHITECTURE

```text
Gradio UI / Typer CLI
        |
        v
 request validation + model catalog
        |
        v
  orchestration engine -------> provenance / SHA-256 / manifest
        |
        +--> Pillow native baseline
        |
        +--> argv-only external adapter
                    |
                    +--> isolated FiDeSR runtime
                    +--> isolated TinySR runtime
                    +--> isolated VOSR runtime
                    +--> isolated SeedVR2/runtime-specific commands
```

External providers are intentionally process-isolated. Upstream Python versions may differ from the core Python version.
