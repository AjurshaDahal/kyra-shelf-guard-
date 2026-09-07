from __future__ import annotations

import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen

from kyra.simulator import CASES, create_server, run_example_case


def test_suspicious_removal_visual_case_runs_real_pipeline(tmp_path: Path) -> None:
    result = run_example_case(tmp_path, "suspicious-removal", seed=42)

    assert result["case"] == "suspicious-removal"
    assert result["evidence_source"] == "synthetic"
    assert result["passed"] is True
    assert result["expected_change_types"] == ["REMOVAL"]
    assert result["actual_change_types"] == ["REMOVAL"]
    assert result["actual_alert_count"] == 1
    assert len(result["frames"]) == 37
    assert result["frames"][0]["phase"] == "baseline"
    assert result["frames"][-1]["phase"] == "event"
    assert result["frames"][0]["rgb_png"].startswith("data:image/png;base64,")
    assert result["frames"][0]["depth_png"].startswith("data:image/png;base64,")


def test_case_catalog_marks_known_camera_drift_limitation() -> None:
    catalog = {item["id"]: item for item in CASES}

    assert catalog["suspicious-removal"]["expected_status"] == "pass"
    assert catalog["camera-drift"]["expected_status"] == "known-failure"
    assert catalog["camera-drift"]["blocker"] == "#79"


def test_local_http_api_serves_catalog_and_runs_one_case(tmp_path: Path) -> None:
    server = create_server("127.0.0.1", 0, tmp_path)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(f"{base_url}/api/cases", timeout=10) as response:
            catalog = json.load(response)
        assert catalog["default_case"] == "suspicious-removal"
        assert len(catalog["cases"]) == 10

        request = Request(
            f"{base_url}/api/run",
            data=json.dumps({"case": "no-change", "seed": 42}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
        assert result["case"] == "no-change"
        assert result["passed"] is True
        assert result["actual_change_types"] == []
        assert result["actual_alert_count"] == 0
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
