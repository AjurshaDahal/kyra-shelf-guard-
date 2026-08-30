from __future__ import annotations

import numpy as np

from kyra.adapters import (
    BaselineProvider,
    GeometryProvider,
    MockBaselineProvider,
    MockGeometryProvider,
    MockRuleEvaluator,
    MockTrackingProvider,
    RuleEvaluator,
    TrackingProvider,
)
from kyra.contracts import (
    AlertEvent,
    BaselineArtifact,
    ChangeType,
    FramePacket,
    PersonTrack,
    ShelfConfig,
    SourceType,
    VolumeChangeEvent,
)


def _frames() -> list[FramePacket]:
    frames: list[FramePacket] = []
    for index in range(3):
        depth = np.full((8, 8), 0.75, dtype=np.float32)
        if index > 0:
            depth[2:6, 2:6] = 0.25
        valid = np.ones_like(depth, dtype=bool)
        if index == 2:
            valid[3:5, 3:5] = False
        frames.append(
            FramePacket(
                frame_id=f"frame-{index:04d}",
                timestamp_ns=index * 1_000_000_000,
                rgb=np.zeros((8, 8, 3), dtype=np.uint8),
                depth_m=depth,
                valid_depth_mask=valid,
                intrinsics=np.eye(3, dtype=np.float64),
                camera_to_shelf=np.eye(4, dtype=np.float64),
                source_type=SourceType.SYNTHETIC_RGBD,
            )
        )
    return frames


def _shelf() -> ShelfConfig:
    return ShelfConfig(
        shelf_id="shelf-01",
        roi_xyxy=(0, 0, 8, 8),
        bounds_min_m=(-0.2, -0.2, 0.5),
        bounds_max_m=(0.2, 0.2, 1.2),
    )


def test_mock_tracking_produces_valid_person_track() -> None:
    frames = _frames()
    provider: TrackingProvider = MockTrackingProvider()

    tracks = provider.track(frames, _shelf())

    assert len(tracks) == len(frames)
    track = tracks[0]
    assert isinstance(track, PersonTrack)
    assert track.track_id == 1001
    assert track.timestamp_ns == frames[0].timestamp_ns
    assert track.near_shelf is True
    assert track.pose_keypoints_xyc.shape[1] == 3
    assert np.isfinite(track.pose_keypoints_xyc).all()


def test_mock_geometry_produces_valid_volume_change_event() -> None:
    frames = _frames()
    shelf = _shelf()
    baseline_provider: BaselineProvider = MockBaselineProvider()
    baseline = baseline_provider.build(frames, shelf)
    geometry_provider: GeometryProvider = MockGeometryProvider()

    events = geometry_provider.detect_changes(baseline, frames, shelf)

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, VolumeChangeEvent)
    assert event.change_type == ChangeType.REMOVAL
    assert event.shelf_id == shelf.shelf_id
    assert event.evidence_frame_ids == ("frame-0000", "frame-0002")
    assert event.first_seen_timestamp_ns == frames[0].timestamp_ns
    assert event.confirmation_timestamp_ns == frames[-1].timestamp_ns


def test_mock_baseline_provider_returns_valid_baseline_artifact() -> None:
    frames = _frames()
    shelf = _shelf()
    provider: BaselineProvider = MockBaselineProvider()

    baseline = provider.build(frames, shelf)

    assert isinstance(baseline, BaselineArtifact)
    assert baseline.shelf_id == shelf.shelf_id
    assert baseline.baseline_depth_m.shape == frames[0].depth_m.shape
    assert baseline.valid_mask.shape == frames[0].depth_m.shape
    assert baseline.calibration_checksum
    assert baseline.metadata["source_frames"] == [frame.frame_id for frame in frames]


def test_mock_outputs_are_deterministic_and_timestamps_are_preserved() -> None:
    frames = _frames()
    shelf = _shelf()

    baseline_a = MockBaselineProvider().build(frames, shelf)
    baseline_b = MockBaselineProvider().build(frames, shelf)
    tracks_a = MockTrackingProvider().track(frames, shelf)
    tracks_b = MockTrackingProvider().track(frames, shelf)
    events_a = MockGeometryProvider().detect_changes(baseline_a, frames, shelf)
    events_b = MockGeometryProvider().detect_changes(baseline_b, frames, shelf)
    rule_a = MockRuleEvaluator().evaluate(events_a[0], tracks_a[0])
    rule_b = MockRuleEvaluator().evaluate(events_b[0], tracks_b[0])

    assert baseline_a.calibration_checksum == baseline_b.calibration_checksum
    assert [track.timestamp_ns for track in tracks_a] == [track.timestamp_ns for track in tracks_b]
    assert events_a[0].evidence_frame_ids == events_b[0].evidence_frame_ids
    assert rule_a == rule_b
    assert rule_a is not None
    assert rule_a.evidence_frame_ids == events_a[0].evidence_frame_ids
    assert rule_a.shelf_id == shelf.shelf_id


def test_adapter_protocols_work_without_person_owner_implementations() -> None:
    frames = _frames()
    shelf = _shelf()
    provider = MockBaselineProvider()
    tracker = MockTrackingProvider()
    geometry = MockGeometryProvider()
    evaluator: RuleEvaluator = MockRuleEvaluator()

    baseline = provider.build(frames, shelf)
    tracks = tracker.track(frames, shelf)
    events = geometry.detect_changes(baseline, frames, shelf)
    alert = evaluator.evaluate(events[0], tracks[0])

    assert isinstance(baseline, BaselineArtifact)
    assert all(isinstance(track, PersonTrack) for track in tracks)
    assert all(isinstance(event, VolumeChangeEvent) for event in events)
    assert isinstance(alert, AlertEvent)
