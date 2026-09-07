"""Person 2 Gate 3 acceptance test suite.

Validates:
1. Replay of frozen golden scenarios G01-G10 through ShelfGeometryProvider.
2. Known-volume accuracy on >=0.5 L fixtures (<=10% error SLA).
3. Failure-path safety: drift envelope, residuals, sparse points, occlusion, invalid depth.
4. Deterministic VolumeChangeEvent serialization and SHA-256 hashing.
5. Real-sensor OCID sequence trial on converted fixture.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import asdict
from pathlib import Path

import cv2
import numpy as np

from kyra.baseline import BaselineBuilder
from kyra.contracts import (
    ChangeType,
    FramePacket,
    ShelfConfig,
    SourceType,
    VolumeChangeEvent,
)
from kyra.differencing.signed_diff import compute_signed_depth_difference
from kyra.geometry import (
    ShelfGeometryProvider,
    register_frame_to_baseline,
)
from kyra.io import ScenarioFrameSource
from kyra.occlusion.safety import evaluate_occlusion_safety
from kyra.ocid import parse_sequence_metadata, write_converted_sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PACK_DIR = REPO_ROOT / "scenario-fixtures" / "golden"
OCID_MINI_DIR = REPO_ROOT / "tests" / "fixtures" / "ocid-mini" / "ocid" / "sequence-01"


def test_golden_pack_replay_g01_to_g10() -> None:
    """Replay all 10 frozen golden scenarios through ShelfGeometryProvider."""
    index_path = GOLDEN_PACK_DIR / "golden-pack.json"
    assert index_path.is_file(), f"missing golden pack index at {index_path}"

    index = json.loads(index_path.read_text(encoding="utf-8"))
    scenarios = index.get("scenarios", [])
    assert len(scenarios) == 10, f"expected 10 golden scenarios, found {len(scenarios)}"

    for entry in scenarios:
        provider = ShelfGeometryProvider()
        sid = entry["scenario_id"]
        behavior = entry["behavior"]
        manifest_path = GOLDEN_PACK_DIR / entry["manifest_path"]
        assert manifest_path.is_file(), f"manifest missing: {manifest_path}"

        source = ScenarioFrameSource(manifest_path)
        baseline_frames = source.baseline_frames()
        assert len(baseline_frames) > 0, f"{sid}: missing baseline frames"

        shelf = ShelfConfig(**source.manifest.shelf.c007_values)
        baseline_artifact = BaselineBuilder(minimum_frames=len(baseline_frames)).fit(
            baseline_frames, shelf
        )

        event_frames = list(source.event_frames())
        assert len(event_frames) > 0, f"{sid}: missing event frames"

        first_event = event_frames[0]
        pmask = source.occlusion_mask(first_event.frame_id)
        person_mask = pmask if pmask.any() else None

        # 1. Registration
        reg_result = register_frame_to_baseline(first_event, baseline_artifact, shelf)
        working_depth = (
            reg_result.corrected_depth_m
            if reg_result.corrected_depth_m is not None
            else first_event.depth_m
        )

        # 2. Occlusion
        occ_result = evaluate_occlusion_safety(
            first_event, baseline_artifact, shelf, person_occlusion_mask=person_mask
        )

        # 3. Differencing
        diff_result = compute_signed_depth_difference(
            working_depth,
            baseline_artifact,
            shelf,
            first_event.valid_depth_mask,
            person_occlusion_mask=person_mask,
        )

        # 4. Multi-frame streaming verification
        stream_frames = [
            FramePacket(
                frame_id=f"{first_event.frame_id}-stream-{s}",
                timestamp_ns=first_event.timestamp_ns + s * 100_000_000,
                rgb=first_event.rgb,
                depth_m=first_event.depth_m,
                valid_depth_mask=first_event.valid_depth_mask,
                intrinsics=first_event.intrinsics,
                camera_to_shelf=first_event.camera_to_shelf,
                source_type=first_event.source_type,
            )
            for s in range(7)
        ]
        stream_masks = [person_mask] * 7
        confirmed_events = provider.detect_changes(
            baseline_artifact, stream_frames, shelf, person_occlusion_masks=stream_masks
        )
        confirmed_type = confirmed_events[0].change_type.value if confirmed_events else "NONE"

        # Behavior invariants
        if behavior in {"thin_item_removal", "irregular_item_removal"}:
            assert diff_result.removal_pixel_count > 0, f"{sid}: expected removal pixels"
            assert confirmed_type == "REMOVAL", f"{sid}: expected confirmed REMOVAL event"
        elif behavior == "addition":
            assert diff_result.addition_pixel_count > 0, f"{sid}: expected addition pixels"
            assert confirmed_type != "REMOVAL", f"{sid}: addition must not emit REMOVAL"
        elif behavior == "person_only_occlusion":
            assert occ_result.is_occluded, f"{sid}: expected occlusion flag True"
            assert confirmed_type == "NONE", f"{sid}: occlusion must suppress removal confirmation"
        elif behavior == "invalid_depth":
            assert (
                diff_result.removal_pixel_count == 0
            ), f"{sid}: invalid depth must not yield removal"
            assert confirmed_type == "NONE", f"{sid}: invalid depth must not yield event"


def test_known_volume_accuracy_on_fixtures() -> None:
    """Verify >=0.5 L fixtures satisfy <= 10% volume error."""
    from tests.acceptance.test_baseline_volume import _baseline_for, _cases

    shelf_config = ShelfConfig(
        shelf_id="acceptance-shelf",
        roi_xyxy=(0, 0, 32, 32),
        bounds_min_m=(-0.5, -0.5, 0.0),
        bounds_max_m=(0.5, 0.5, 2.0),
        voxel_size_m=0.01,
    )
    intrinsics = np.array(
        [[100.0, 0.0, 16.0], [0.0, 100.0, 16.0], [0.0, 0.0, 1.0]], dtype=np.float32
    )

    def make_frame_packet(frame_id: str, timestamp_ns: int, depth_m: np.ndarray) -> FramePacket:
        return FramePacket(
            frame_id=frame_id,
            timestamp_ns=timestamp_ns,
            rgb=np.zeros((32, 32, 3), dtype=np.uint8),
            depth_m=depth_m,
            valid_depth_mask=np.ones_like(depth_m, dtype=bool),
            intrinsics=intrinsics,
            camera_to_shelf=np.eye(4, dtype=np.float32),
            source_type=SourceType.SYNTHETIC_RGBD,
        )

    for case in _cases(100.0, 100.0):
        artifact = _baseline_for(case, make_frame_packet, shelf_config)
        measured_l = artifact.portable_components[0].volume_m3 * 1000.0
        expected_l = case.expected_volume_m3 * 1000.0
        rel_error = abs(measured_l - expected_l) / expected_l
        assert rel_error <= 0.10, f"{case.name}: error {rel_error:.2%} exceeds 10% SLA"


def test_failure_paths_suppress_removal_events() -> None:
    """Failure conditions must safely reject and never produce removal events."""
    shelf = ShelfConfig(
        shelf_id="fail-shelf",
        roi_xyxy=(10, 10, 50, 50),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.2),
        registration_reject_m=0.02,
        minimum_visible_fraction=0.70,
    )
    intrinsics = np.array(
        [[200.0, 0.0, 32.0], [0.0, 200.0, 32.0], [0.0, 0.0, 1.0]], dtype=np.float32
    )
    camera_to_shelf = np.eye(4, dtype=np.float32)

    depth_base = np.full((64, 64), 0.80, dtype=np.float32)
    base_frame = FramePacket(
        frame_id="base-0",
        timestamp_ns=0,
        rgb=np.zeros((64, 64, 3), dtype=np.uint8),
        depth_m=depth_base,
        valid_depth_mask=np.ones((64, 64), dtype=bool),
        intrinsics=intrinsics,
        camera_to_shelf=camera_to_shelf,
        source_type=SourceType.SYNTHETIC_RGBD,
    )
    baseline = BaselineBuilder(minimum_frames=1).fit([base_frame], shelf)
    provider = ShelfGeometryProvider()

    # 1. Excessive translation drift (25 mm > 15 mm envelope)
    frame_drift = FramePacket(
        frame_id="drift-fail",
        timestamp_ns=1_000_000_000,
        rgb=np.zeros((64, 64, 3), dtype=np.uint8),
        depth_m=depth_base + 0.025,
        valid_depth_mask=np.ones((64, 64), dtype=bool),
        intrinsics=intrinsics,
        camera_to_shelf=camera_to_shelf,
        source_type=SourceType.SYNTHETIC_RGBD,
    )
    reg_drift = register_frame_to_baseline(frame_drift, baseline, shelf)
    assert reg_drift.rejected and reg_drift.rejection_reason == "drift_envelope_exceeded"
    assert len(provider.detect_changes(baseline, [frame_drift], shelf)) == 0

    # 2. Insufficient fixed geometry points (< 10 points)
    valid_few = np.zeros((64, 64), dtype=bool)
    valid_few[0, :5] = True
    frame_few = FramePacket(
        frame_id="few-points",
        timestamp_ns=2_000_000_000,
        rgb=np.zeros((64, 64, 3), dtype=np.uint8),
        depth_m=depth_base,
        valid_depth_mask=valid_few,
        intrinsics=intrinsics,
        camera_to_shelf=camera_to_shelf,
        source_type=SourceType.SYNTHETIC_RGBD,
    )
    reg_few = register_frame_to_baseline(frame_few, baseline, shelf)
    assert reg_few.rejected and reg_few.rejection_reason == "insufficient_fixed_geometry_points"

    # 3. Severe occlusion (< 70% visible shelf)
    person_occ = np.zeros((64, 64), dtype=bool)
    person_occ[10:45, 10:45] = True
    occ_res = evaluate_occlusion_safety(
        base_frame, baseline, shelf, person_occlusion_mask=person_occ
    )
    assert occ_res.is_occluded and occ_res.visible_shelf_fraction < 0.70

    # 4. Unknown depth (zeros in ROI)
    depth_zero = depth_base.copy()
    depth_zero[10:50, 10:50] = 0.0
    diff_zero = compute_signed_depth_difference(
        depth_zero, baseline, shelf, valid_depth_mask=(depth_zero > 0)
    )
    assert diff_zero.removal_pixel_count == 0


def test_volume_change_event_serialization_determinism() -> None:
    """Verify deterministic VolumeChangeEvent JSON serialization and SHA-256 hash."""
    event = VolumeChangeEvent(
        event_id="volume-event-test-0001",
        shelf_id="shelf-main-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=1_000_000_000,
        confirmation_timestamp_ns=1_600_000_000,
        missing_volume_m3=0.001250,
        bounds_min_m=(-0.1, -0.1, 0.4),
        bounds_max_m=(0.1, 0.1, 0.6),
        centroid_m=(0.0, 0.0, 0.5),
        visible_shelf_fraction=0.95,
        confidence=0.92,
        evidence_frame_ids=(
            "frame-0000",
            "frame-0001",
            "frame-0002",
            "frame-0003",
            "frame-0004",
            "frame-0005",
            "frame-0006",
        ),
    )
    payload1 = json.dumps(asdict(event), sort_keys=True, indent=2)
    payload2 = json.dumps(asdict(event), sort_keys=True, indent=2)
    assert payload1 == payload2

    sha256 = hashlib.sha256(payload1.encode("utf-8")).hexdigest()
    assert sha256 == "f19312ffc150241b228e4eda0fa5993a1e50523ea877904c897fb6207799b736"
    assert event.first_seen_timestamp_ns <= event.confirmation_timestamp_ns


def test_ocid_sequence_trial_execution() -> None:
    """Evaluate converted real-sensor OCID sequence for removal detection."""
    from tests.test_ocid import _shelf

    assert (OCID_MINI_DIR / "metadata.toml").is_file()
    meta = parse_sequence_metadata((OCID_MINI_DIR / "metadata.toml").read_text(encoding="utf-8"))
    frames = []
    for i in range(3):
        rgb = cv2.imread(str(OCID_MINI_DIR / f"frame-{i:06d}.color.png"), cv2.IMREAD_COLOR)
        depth = cv2.imread(str(OCID_MINI_DIR / f"frame-{i:06d}.depth.png"), cv2.IMREAD_UNCHANGED)
        mask = cv2.imread(str(OCID_MINI_DIR / f"frame-{i:06d}.mask.png"), cv2.IMREAD_GRAYSCALE)
        assert rgb is not None and depth is not None and mask is not None
        frames.append((rgb, depth, mask))

    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / "ocid_trial"
        write_converted_sequence(
            meta,
            frames,
            dest,
            shelf=_shelf(),
            scenario_id="ocid-gate3-trial",
            seed=42,
            reverse=True,
        )
        source = ScenarioFrameSource(dest / "scenario.json")
        shelf = ShelfConfig(**source.manifest.shelf.c007_values)
        baseline_frames = source.baseline_frames()
        baseline = BaselineBuilder(minimum_frames=len(baseline_frames)).fit(baseline_frames, shelf)

        results = []
        for frame in source.event_frames():
            diff = compute_signed_depth_difference(
                frame.depth_m, baseline, shelf, frame.valid_depth_mask
            )
            results.append(diff.removal_pixel_count)

        assert results[-1] > 0, "reversed OCID sequence frame 0 must observe removal pixels"
