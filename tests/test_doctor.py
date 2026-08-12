from sr_studio.doctor import collect_doctor


def test_doctor_does_not_load_heavy_models() -> None:
    report = collect_doctor()
    by_id = {item["id"]: item for item in report["models"]}
    assert by_id["pillow-lanczos"]["ready"] is True
    assert by_id["fidesr"]["runtime_status"] in {"RUNTIME_NOT_CONFIGURED", "BLOCKED", "READY"}
    assert by_id["pgsr"]["runtime_status"] == "BLOCKED_CHECKPOINT"
