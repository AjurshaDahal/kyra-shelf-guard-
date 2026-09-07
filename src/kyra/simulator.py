"""Local visual review environment for deterministic synthetic scenarios."""

from __future__ import annotations

import argparse
import base64
import json
import tempfile
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from kyra.cli import SIMULATION_CASES, generate_example_scenario
from kyra.io import ScenarioFrameSource
from kyra.pipeline import run_scenario

CASES: tuple[dict[str, str], ...] = (
    {
        "id": "suspicious-removal",
        "name": "Suspicious removal",
        "description": "A nearby unauthorized person and a visible removal produce one alert.",
        "expected_status": "pass",
    },
    {
        "id": "removal-without-person",
        "name": "Removal without a person",
        "description": "Geometry reports a removal, but the rule engine does not alert.",
        "expected_status": "pass",
    },
    {
        "id": "no-change",
        "name": "No change",
        "description": "A stable shelf produces no change event and no alert.",
        "expected_status": "pass",
    },
    {
        "id": "person-without-removal",
        "name": "Person without removal",
        "description": "A nearby person alone is insufficient to create an alert.",
        "expected_status": "pass",
    },
    {
        "id": "addition",
        "name": "Item addition",
        "description": "An added object is classified as an addition, not a suspicious removal.",
        "expected_status": "pass",
    },
    {
        "id": "authorized-restock",
        "name": "Authorized restock",
        "description": "Restock mode and an authorized track suppress suspicious-removal alerts.",
        "expected_status": "pass",
    },
    {
        "id": "occlusion-then-removal",
        "name": "Occlusion, then removal",
        "description": "Temporary occlusion is ignored; later visible removal produces one alert.",
        "expected_status": "pass",
    },
    {
        "id": "outside-association-window",
        "name": "Outside association window",
        "description": "A removal more than two seconds after the person was near does not alert.",
        "expected_status": "pass",
    },
    {
        "id": "invalid-depth",
        "name": "Invalid depth",
        "description": "Unknown depth is not interpreted as empty shelf space.",
        "expected_status": "pass",
    },
    {
        "id": "camera-drift",
        "name": "Camera drift (known failure)",
        "description": (
            "The current geometry path wrongly reports a removal; this exposes blocker #79."
        ),
        "expected_status": "known-failure",
        "blocker": "#79",
    },
)

if tuple(item["id"] for item in CASES) != SIMULATION_CASES:
    raise RuntimeError("simulator case catalog must match the deterministic CLI profiles")


def _png_data_url(image: np.ndarray) -> str:
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise RuntimeError("could not encode simulator preview")
    payload = base64.b64encode(encoded.tobytes()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def _render_frames(source: ScenarioFrameSource) -> list[dict[str, Any]]:
    frames = list(source)
    valid_depth = np.concatenate(
        [frame.depth_m[frame.valid_depth_mask] for frame in frames]
    )
    depth_min = float(valid_depth.min()) if valid_depth.size else 0.0
    depth_max = float(valid_depth.max()) if valid_depth.size else 1.0
    depth_span = max(depth_max - depth_min, 1e-6)
    baseline_ids = set(source.manifest.baseline_frame_ids)
    records = {record.frame_id: record for record in source.manifest.frames}
    x1, y1, x2, y2 = source.manifest.shelf.roi_xyxy
    rendered: list[dict[str, Any]] = []

    for frame in frames:
        record = records[frame.frame_id]
        rgb_bgr = cv2.cvtColor(frame.rgb, cv2.COLOR_RGB2BGR)
        cv2.rectangle(rgb_bgr, (x1, y1), (x2 - 1, y2 - 1), (44, 210, 255), 1)
        for track in record.tracks:
            tx1, ty1, tx2, ty2 = (int(value) for value in track.box_xyxy)
            color = (82, 210, 90) if track.authorized else (70, 70, 240)
            cv2.rectangle(rgb_bgr, (tx1, ty1), (tx2, ty2), color, 1)
            cv2.putText(
                rgb_bgr,
                f"P{track.track_id}",
                (max(0, tx1), max(9, ty1 - 2)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.28,
                color,
                1,
                cv2.LINE_AA,
            )

        normalized = np.zeros(frame.depth_m.shape, dtype=np.uint8)
        normalized[frame.valid_depth_mask] = np.clip(
            (frame.depth_m[frame.valid_depth_mask] - depth_min) / depth_span * 255,
            0,
            255,
        ).astype(np.uint8)
        depth_color = cv2.applyColorMap(255 - normalized, cv2.COLORMAP_TURBO)
        depth_color[~frame.valid_depth_mask] = (18, 18, 22)
        occlusion = source.occlusion_mask(frame.frame_id)
        if occlusion.any():
            depth_color[occlusion] = (180, 60, 180)

        rendered.append(
            {
                "frame_id": frame.frame_id,
                "timestamp_ns": frame.timestamp_ns,
                "phase": "baseline" if frame.frame_id in baseline_ids else "event",
                "track_count": len(record.tracks),
                "occluded_pixels": int(occlusion.sum()),
                "valid_depth_percent": round(float(frame.valid_depth_mask.mean() * 100), 2),
                "rgb_png": _png_data_url(rgb_bgr),
                "depth_png": _png_data_url(depth_color),
            }
        )
    return rendered


def run_example_case(
    work_root: str | Path,
    case: str = "suspicious-removal",
    *,
    seed: int = 42,
) -> dict[str, Any]:
    """Generate, execute, evaluate, and render one synthetic review case."""

    if case not in SIMULATION_CASES:
        raise ValueError(f"unknown simulation case: {case!r}")
    root = Path(work_root)
    root.mkdir(parents=True, exist_ok=True)
    scenario_dir = Path(tempfile.mkdtemp(prefix=f"{case}-", dir=root))
    manifest_path = generate_example_scenario(scenario_dir, case, seed=seed)
    source = ScenarioFrameSource(manifest_path)
    pipeline = run_scenario(manifest_path)
    expected_types = sorted(
        event.change_type.value for event in source.manifest.ground_truth_events
    )
    actual_types = sorted(event["change_type"] for event in pipeline["events"])
    expected_alert_count = sum(
        event.should_alert for event in source.manifest.ground_truth_events
    )
    actual_alert_count = int(pipeline["alert_count"])
    passed = expected_types == actual_types and expected_alert_count == actual_alert_count
    catalog_entry = next(item for item in CASES if item["id"] == case)
    return {
        "case": case,
        "case_name": catalog_entry["name"],
        "description": catalog_entry["description"],
        "expected_status": catalog_entry["expected_status"],
        "blocker": catalog_entry.get("blocker"),
        "seed": seed,
        "scenario_id": source.manifest.scenario_id,
        "evidence_source": source.manifest.evidence_source,
        "passed": passed,
        "expected_change_types": expected_types,
        "actual_change_types": actual_types,
        "expected_alert_count": expected_alert_count,
        "actual_alert_count": actual_alert_count,
        "frames": _render_frames(source),
        "pipeline": pipeline,
    }


class SimulatorServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], work_root: Path) -> None:
        self.work_root = work_root
        super().__init__(address, SimulatorRequestHandler)


class SimulatorRequestHandler(BaseHTTPRequestHandler):
    server: SimulatorServer

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def _json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            body = files("kyra").joinpath("simulator.html").read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/api/cases":
            self._json({"default_case": "suspicious-removal", "cases": CASES})
            return
        self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/run":
            self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 8192:
                raise ValueError("request is too large")
            request = json.loads(self.rfile.read(content_length) or b"{}")
            case = str(request.get("case", "suspicious-removal"))
            seed = int(request.get("seed", 42))
            self._json(run_example_case(self.server.work_root, case, seed=seed))
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
        except Exception as error:  # pragma: no cover - surfaced to the local reviewer
            self._json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)


def create_server(host: str, port: int, work_root: str | Path) -> SimulatorServer:
    """Create the loopback HTTP server; tests can request an ephemeral port."""

    return SimulatorServer((host, port), Path(work_root))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch Kyra's local visual simulator")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.port < 0 or args.port > 65535:
        raise ValueError("--port must be between 0 and 65535")
    with tempfile.TemporaryDirectory(prefix="kyra-simulator-") as temp_root:
        host = "127.0.0.1"
        server = create_server(host, args.port, temp_root)
        url = f"http://{host}:{server.server_port}"
        print(f"Kyra simulator: {url}")
        print("Synthetic test evidence only. Press Ctrl+C to stop.")
        if not args.no_open:
            threading.Timer(0.25, webbrowser.open, args=(url,)).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nKyra simulator stopped.")
        finally:
            server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["CASES", "create_server", "run_example_case"]
