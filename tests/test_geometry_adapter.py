from __future__ import annotations

import numpy as np

from kyra.adapters import GeometryProvider
from kyra.contracts import (
    BaselineArtifact,
    ChangeType,
    FramePacket,
    ShelfConfig,
    SourceType,
)
from kyra.geometry.provider import ShelfGeometryProvider
from kyra.geometry.temporal_state import update_baseline_after_restock


def _make_intrinsics(width: int = 32, height: int = 24) -> np.ndarray:
    return np.array(
        [
            [100.0, 0.0, width / 2.0],
            [0.0, 100.0, height / 2.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )


def _make_shelf_config() -> ShelfConfig:
    return ShelfConfig(
        shelf_id="shelf-test-01",
        roi_xyxy=(4, 4, 28, 20),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        minimum_alert_volume_m3=5e-5,
        minimum_visible_fraction=0.70,
    )


def _make_baseline(width: int = 32, height: int = 24) -> BaselineArtifact:
    intrinsics = _make_intrinsics(width, height)
    cam_to_shelf = np.eye(4, dtype=np.float64)

    depth = np.full((height, width), 1.0, dtype=np.float32)
    valid = np.ones((height, width), dtype=bool)

    # Fixed shelf structure around border of ROI
    fixed = np.zeros((height, width), dtype=bool)
    fixed[4:8, 4:28] = True
    fixed[16:20, 4:28] = True
    fixed[8:16, 4:8] = True
    fixed[8:16, 24:28] = True

    occupancy = np.zeros((height, width, 1), dtype=np.uint8)
    occupancy[..., 0] = valid.astype(np.uint8)

    return BaselineArtifact(
        shelf_id="shelf-test-01",
        roi_xyxy=(4, 4, 28, 20),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        baseline_depth_m=depth,
        valid_mask=valid,
        fixed_geometry_mask=fixed,
        portable_components=(),
        occupancy_grid=occupancy,
        noise_sigma_m=np.full((height, width), 0.002, dtype=np.float32),
        intrinsics=intrinsics,
        camera_to_shelf=cam_to_shelf,
        calibration_checksum="f" * 64,
    )


def _make_frame(
    index: int,
    timestamp_ns: int,
    *,
    removal: bool = False,
    occluded: bool = False,
    width: int = 32,
    height: int = 24,
) -> FramePacket:
    intrinsics = _make_intrinsics(width, height)
    cam_to_shelf = np.eye(4, dtype=np.float64)

    depth = np.full((height, width), 1.0, dtype=np.float32)
    valid = np.ones((height, width), dtype=bool)

    if removal:
        # Removal in portable region: surface is farther by 50 mm
        depth[10:14, 10:18] += 0.050

    if occluded:
        # Occlusion covers half the ROI
        valid[4:14, 4:28] = False
        depth[4:14, 4:28] = 0.0

    return FramePacket(
        frame_id=f"frame-{index:04d}",
        timestamp_ns=timestamp_ns,
        rgb=np.zeros((height, width, 3), dtype=np.uint8),
        depth_m=depth,
        valid_depth_mask=valid,
        intrinsics=intrinsics,
        camera_to_shelf=cam_to_shelf,
        source_type=SourceType.SYNTHETIC_RGBD,
    )


def test_shelf_geometry_provider_implements_protocol() -> None:
    provider = ShelfGeometryProvider()
    assert isinstance(provider, GeometryProvider)


def test_shelf_geometry_provider_no_change_produces_zero_events() -> None:
    baseline = _make_baseline()
    config = _make_shelf_config()
    provider = ShelfGeometryProvider()

    frames = [
        _make_frame(i, 1_000_000_000 + i * 100_000_000, removal=False)
        for i in range(10)
    ]

    events = provider.detect_changes(baseline, frames, config)
    assert events == ()


def test_shelf_geometry_provider_removal_confirmed() -> None:
    baseline = _make_baseline()
    config = _make_shelf_config()
    provider = ShelfGeometryProvider()

    # 10 frames spaced by 100 ms (1.0 second total) with persistent removal
    frames = [
        _make_frame(i, 1_000_000_000 + i * 100_000_000, removal=True)
        for i in range(10)
    ]

    events = provider.detect_changes(baseline, frames, config)
    # Exactly one confirmed event emitted (deduplicated)
    assert len(events) == 1
    event = events[0]

    assert event.shelf_id == "shelf-test-01"
    assert event.change_type is ChangeType.REMOVAL
    assert event.missing_volume_m3 > config.minimum_alert_volume_m3
    assert event.confidence > 0.70
    assert len(event.evidence_frame_ids) >= 5
    # First seen at or before 1.4s, confirmed around frame 5 or 6 (>= 0.5s duration)
    assert event.confirmation_timestamp_ns - event.first_seen_timestamp_ns >= 500_000_000


def test_shelf_geometry_provider_occlusion_produces_zero_removal() -> None:
    baseline = _make_baseline()
    config = _make_shelf_config()
    provider = ShelfGeometryProvider()

    # Frames have both removal and heavy occlusion (> 30% occluded)
    frames = [
        _make_frame(i, 1_000_000_000 + i * 100_000_000, removal=True, occluded=True)
        for i in range(10)
    ]

    events = provider.detect_changes(baseline, frames, config)
    # Occlusion must suppress removal confirmation!
    assert events == ()


def test_update_baseline_after_restock() -> None:
    baseline = _make_baseline()
    config = _make_shelf_config()

    # 3 frames spanning 2.5 seconds (> 2.0s required)
    stable_frames = [
        _make_frame(0, 1_000_000_000),
        _make_frame(1, 2_500_000_000),
        _make_frame(2, 3_500_000_000),
    ]

    updated = update_baseline_after_restock(baseline, stable_frames, config)
    assert updated.metadata.get("restocked_at_ns") == 3_500_000_000


def test_shelf_geometry_provider_latency_budget() -> None:
    import time

    baseline = _make_baseline()
    config = _make_shelf_config()
    provider = ShelfGeometryProvider()

    frames = [
        _make_frame(i, 1_000_000_000 + i * 100_000_000, removal=(i >= 5))
        for i in range(25)
    ]

    # Warmup
    provider.detect_changes(baseline, frames[:2], config)

    latencies_ms = []
    for f in frames:
        t0 = time.perf_counter()
        provider.detect_changes(baseline, [f], config)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)

    p95 = float(np.percentile(latencies_ms, 95))
    # Requirement P2-QA-002: target below 40 ms p95
    assert p95 < 40.0
