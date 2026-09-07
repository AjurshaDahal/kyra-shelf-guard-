from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import cv2
import numpy as np

from kyra.contracts import (
    SCHEMA_VERSION,
    ChangeType,
    ShelfConfig,
    SystemMode,
    VolumeChangeEvent,
)
from kyra.io import ScenarioFrameSource
from kyra.manifest import (
    FrameRecord,
    ScenarioManifest,
    ShelfConfigRecord,
    TrackAnnotation,
    write_manifest,
)
from kyra.proximity.person_proximity import update_proximity
from kyra.rules.alert_engine import (
    ASSOCIATION_WINDOW_NS,
    RULE_VERSION,
    evaluate_removal_alert,
)
from kyra.tracking.replay_tracker import ReplayTracker

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "person3-gate4"
SCENARIO_DIR = EVIDENCE / "scenario"
MANIFEST_PATH = SCENARIO_DIR / "scenario.json"

FRAME_SHAPE = (4, 5)

FRAME_1_TIMESTAMP_NS = 1_000_000_000
FRAME_2_TIMESTAMP_NS = 2_000_000_000

SHELF_ID = "shelf-01"
TRACK_ID = 7

SHELF_BOUNDS_MIN = (-0.2, -0.2, 0.5)
SHELF_BOUNDS_MAX = (0.2, 0.2, 1.2)

PROXIMITY_DISTANCE_M = 1.0
MINIMUM_ALERT_VOLUME_M3 = 5e-5


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def build_shelf_config() -> ShelfConfig:
    return ShelfConfig(
        shelf_id=SHELF_ID,
        roi_xyxy=(0, 0, 5, 4),
        bounds_min_m=SHELF_BOUNDS_MIN,
        bounds_max_m=SHELF_BOUNDS_MAX,
        minimum_alert_volume_m3=MINIMUM_ALERT_VOLUME_M3,
        proximity_distance_m=PROXIMITY_DISTANCE_M,
    )


def write_png(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f"OpenCV could not write {path}")


def build_scenario() -> None:
    if EVIDENCE.exists():
        shutil.rmtree(EVIDENCE)

    for directory in (
        SCENARIO_DIR / "rgb",
        SCENARIO_DIR / "depth",
        SCENARIO_DIR / "masks",
    ):
        directory.mkdir(parents=True, exist_ok=True)

    frames: list[FrameRecord] = []

    for index in (1, 2):
        frame_id = f"frame-{index:04d}"

        # RGB image.
        rgb_bgr = np.zeros(
            (*FRAME_SHAPE, 3),
            dtype=np.uint8,
        )
        rgb_bgr[:, :] = (
            5 * index,
            10 * index,
            20 * index,
        )

        # 16-bit depth in millimetres.
        depth_mm = np.full(
            FRAME_SHAPE,
            1000 + 100 * (index - 1),
            dtype=np.uint16,
        )

        # Valid-depth mask.
        valid_mask = np.full(
            FRAME_SHAPE,
            255,
            dtype=np.uint8,
        )

        # Person occlusion mask.
        occlusion_mask = np.zeros(
            FRAME_SHAPE,
            dtype=np.uint8,
        )

        if index == 1:
            # Explicit invalid depth.
            depth_mm[0, 1] = 0

            # Explicit invalid-mask pixel.
            valid_mask[0, 2] = 0

            # Explicit occlusion pixel.
            occlusion_mask[1, 1] = 255

        rgb_path = f"rgb/{frame_id}.png"
        depth_path = f"depth/{frame_id}.png"
        valid_path = f"masks/{frame_id}-valid.png"
        occlusion_path = f"masks/{frame_id}-occlusion.png"

        write_png(SCENARIO_DIR / rgb_path, rgb_bgr)
        write_png(SCENARIO_DIR / depth_path, depth_mm)
        write_png(SCENARIO_DIR / valid_path, valid_mask)
        write_png(SCENARIO_DIR / occlusion_path, occlusion_mask)

        tracks: list[TrackAnnotation] = []

        if index == 2:
            tracks.append(
                TrackAnnotation(
                    track_id=TRACK_ID,
                    box_xyxy=(1.0, 0.0, 4.0, 3.0),
                    position_m=(0.1, 0.0, 0.8),
                    near_shelf=True,
                    authorized=False,
                )
            )

        frames.append(
            FrameRecord(
                frame_id=frame_id,
                timestamp_ns=(
                    FRAME_1_TIMESTAMP_NS
                    if index == 1
                    else FRAME_2_TIMESTAMP_NS
                ),
                rgb_path=rgb_path,
                depth_path=depth_path,
                valid_mask_path=valid_path,
                occlusion_mask_path=occlusion_path,
                tracks=tracks,
            )
        )

    manifest = ScenarioManifest(
        schema_version="1.1",
        scenario_id="person3-gate4-001",
        random_seed=42,
        source_type="synthetic_rgbd",
        evidence_source="synthetic",
        category="thin-tray",
        intrinsics=(
            (100.0, 0.0, 2.0),
            (0.0, 100.0, 1.5),
            (0.0, 0.0, 1.0),
        ),
        camera_to_shelf=(
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ),
        shelf=ShelfConfigRecord(
            shelf_id=SHELF_ID,
            roi_xyxy=(0, 0, 5, 4),
            bounds_min_m=SHELF_BOUNDS_MIN,
            bounds_max_m=SHELF_BOUNDS_MAX,
        ),
        baseline_frame_ids=["frame-0001"],
        frames=frames,
    )

    write_manifest(manifest, MANIFEST_PATH)


def serialize_track(track) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "track_id": track.track_id,
        "timestamp_ns": track.timestamp_ns,
        "box_xyxy": list(track.box_xyxy),
        "pose_keypoints_xyc": track.pose_keypoints_xyc.tolist(),
        "position_m": (
            list(track.position_m)
            if track.position_m is not None
            else None
        ),
        "near_shelf": track.near_shelf,
        "wrist_in_shelf": track.wrist_in_shelf,
        "authorized": track.authorized,
        "last_near_timestamp_ns": track.last_near_timestamp_ns,
    }


def build_volume_event(
    *,
    event_id: str,
    change_type: ChangeType,
    timestamp_ns: int,
    missing_volume_m3: float,
) -> VolumeChangeEvent:
    return VolumeChangeEvent(
        event_id=event_id,
        shelf_id=SHELF_ID,
        change_type=change_type,
        first_seen_timestamp_ns=timestamp_ns,
        confirmation_timestamp_ns=timestamp_ns,
        missing_volume_m3=missing_volume_m3,
        bounds_min_m=(-0.1, -0.1, 0.5),
        bounds_max_m=(0.1, 0.1, 0.8),
        centroid_m=(0.0, 0.0, 0.65),
        visible_shelf_fraction=1.0,
        confidence=0.95,
        evidence_frame_ids=("frame-0002",),
    )


def get_runtime_track(source: ScenarioFrameSource):
    tracker = ReplayTracker(source)

    tracks = tracker.tracks_for_frame("frame-0002")

    assert len(tracks) == 1
    assert tracks[0].track_id == TRACK_ID

    track = tracks[0]

    # ReplayTracker deliberately reconstructs the runtime track without
    # injecting upstream metric position. Supply the representative
    # depth/3D position here before running the proximity rule.
    annotation = source.track_annotations("frame-0002")[0]

    track.position_m = annotation.position_m
    track.authorized = annotation.authorized

    return track


def evaluate_case(
    source: ScenarioFrameSource,
    *,
    authorized: bool = False,
    system_mode: SystemMode = SystemMode.NORMAL,
    change_type: ChangeType = ChangeType.REMOVAL,
    timestamp_ns: int = FRAME_2_TIMESTAMP_NS,
    missing_volume_m3: float = 1e-3,
):
    track = get_runtime_track(source)

    track.authorized = authorized

    shelf = build_shelf_config()

    track = update_proximity(track, shelf)

    event = build_volume_event(
        event_id="matrix-case",
        change_type=change_type,
        timestamp_ns=timestamp_ns,
        missing_volume_m3=missing_volume_m3,
    )

    return evaluate_removal_alert(
        event,
        (track,),
        shelf,
        system_mode=system_mode,
    )


def main() -> None:
    build_scenario()

    source = ScenarioFrameSource(MANIFEST_PATH)
    shelf = build_shelf_config()

    # ------------------------------------------------------------------
    # 1. Replay tracking + shelf proximity
    # ------------------------------------------------------------------

    track = get_runtime_track(source)

    track = update_proximity(track, shelf)

    assert track.near_shelf is True
    assert track.last_near_timestamp_ns == FRAME_2_TIMESTAMP_NS

    track_payload = serialize_track(track)

    write_json(
        EVIDENCE / "person3-track-001.json",
        track_payload,
    )

    # ------------------------------------------------------------------
    # 2. Deterministic removal alert
    # ------------------------------------------------------------------

    volume_event = build_volume_event(
        event_id="p3-g4-removal-001",
        change_type=ChangeType.REMOVAL,
        timestamp_ns=FRAME_2_TIMESTAMP_NS,
        missing_volume_m3=1e-3,
    )

    alert = evaluate_removal_alert(
        volume_event,
        (track,),
        shelf,
        system_mode=SystemMode.NORMAL,
    )

    assert alert is not None, "expected a deterministic Person 3 alert"
    assert alert.person_track_id == TRACK_ID
    assert alert.volume_event_id == "p3-g4-removal-001"
    assert alert.shelf_id == SHELF_ID
    assert alert.rule_version == RULE_VERSION

    alert_payload = {
        "schema_version": SCHEMA_VERSION,
        "alert_id": alert.alert_id,
        "shelf_id": alert.shelf_id,
        "volume_event_id": alert.volume_event_id,
        "person_track_id": alert.person_track_id,
        "rule_version": alert.rule_version,
        "first_seen_timestamp_ns": alert.first_seen_timestamp_ns,
        "alert_timestamp_ns": alert.alert_timestamp_ns,
        "missing_volume_m3": alert.missing_volume_m3,
        "confidence": alert.confidence,
        "reason": alert.reason,
        "evidence_frame_ids": list(alert.evidence_frame_ids),
    }

    write_json(
        EVIDENCE / "person3-alert-001.json",
        alert_payload,
    )

    # ------------------------------------------------------------------
    # 3. Deterministic no-alert matrix
    # ------------------------------------------------------------------

    cases = [
        (
            "eligible-removal",
            evaluate_case(source),
            True,
        ),
        (
            "authorized-person",
            evaluate_case(
                source,
                authorized=True,
            ),
            False,
        ),
        (
            "restock-mode",
            evaluate_case(
                source,
                system_mode=SystemMode.RESTOCK_MODE,
            ),
            False,
        ),
        (
            "below-minimum-volume",
            evaluate_case(
                source,
                missing_volume_m3=1e-6,
            ),
            False,
        ),
        (
            "outside-two-second-window",
            evaluate_case(
                source,
                timestamp_ns=(
                    FRAME_2_TIMESTAMP_NS
                    + ASSOCIATION_WINDOW_NS
                    + 1
                ),
            ),
            False,
        ),
        (
            "addition-direction",
            evaluate_case(
                source,
                change_type=ChangeType.ADDITION,
            ),
            False,
        ),
    ]

    matrix = []

    for case_id, result, expected_alert in cases:
        actual_alert = result is not None

        assert actual_alert == expected_alert, (
            f"{case_id}: expected alert={expected_alert}, "
            f"got alert={actual_alert}"
        )

        matrix.append(
            {
                "case_id": case_id,
                "expected_alert": expected_alert,
                "actual_alert": actual_alert,
                "alert_id": (
                    result.alert_id
                    if result is not None
                    else None
                ),
            }
        )

    matrix_payload = {
        "schema_version": SCHEMA_VERSION,
        "rule_version": RULE_VERSION,
        "association_window_ns": ASSOCIATION_WINDOW_NS,
        "proximity_distance_m": shelf.proximity_distance_m,
        "minimum_alert_volume_m3": shelf.minimum_alert_volume_m3,
        "cases": matrix,
    }

    write_json(
        EVIDENCE / "person3-gate4-matrix.json",
        matrix_payload,
    )

    # ------------------------------------------------------------------
    # 4. SHA-256 checksums
    # ------------------------------------------------------------------

    files = sorted(
        path
        for path in EVIDENCE.rglob("*")
        if path.is_file()
        and path.name != "SHA256SUMS.txt"
    )

    lines = []

    for path in files:
        digest = sha256_file(path)
        lines.append(
            f"{digest}  {path.relative_to(EVIDENCE)}"
        )

    (EVIDENCE / "SHA256SUMS.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    print("Generated Person 3 Gate 4 evidence:")
    for line in lines:
        print(line)

    print()
    print(f"Track ID: {track.track_id}")
    print(f"Near shelf: {track.near_shelf}")
    print(
        f"Last near timestamp: "
        f"{track.last_near_timestamp_ns}"
    )
    print(f"Alert ID: {alert.alert_id}")
    print(f"Rule version: {RULE_VERSION}")
    print(f"Evidence directory: {EVIDENCE}")


if __name__ == "__main__":
    main()
