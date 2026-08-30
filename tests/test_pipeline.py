from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from kyra.adapters import (
    MockGeometryProvider,
    MockRuleEvaluator,
    MockTrackingProvider,
)
from kyra.contracts import (
    AlertEvent,
    ChangeType,
    FramePacket,
    ShelfConfig,
    SourceType,
    VolumeChangeEvent,
)
from kyra.pipeline import BoundedFrameQueue, EvidenceWriter, MockPipeline


def _frame(index: int, *, timestamp_ns: int | None = None) -> FramePacket:
    ts = index * 1_000_000_000 if timestamp_ns is None else timestamp_ns
    depth = np.full((8, 8), 0.75, dtype=np.float32)
    if index > 0:
        depth[2:6, 2:6] = 0.25
    valid = np.ones_like(depth, dtype=bool)
    if index == 2:
        valid[3:5, 3:5] = False
    return FramePacket(
        frame_id=f"frame-{index:04d}",
        timestamp_ns=ts,
        rgb=np.zeros((8, 8, 3), dtype=np.uint8),
        depth_m=depth,
        valid_depth_mask=valid,
        intrinsics=np.eye(3, dtype=np.float64),
        camera_to_shelf=np.eye(4, dtype=np.float64),
        source_type=SourceType.SYNTHETIC_RGBD,
    )


def _shelf() -> ShelfConfig:
    return ShelfConfig(
        shelf_id="shelf-01",
        roi_xyxy=(0, 0, 8, 8),
        bounds_min_m=(-0.2, -0.2, 0.5),
        bounds_max_m=(0.2, 0.2, 1.2),
    )


class RecordingTrackingProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []

    def track(self, frames, shelf_config):
        self.calls.append(tuple(frame.frame_id for frame in frames))
        return MockTrackingProvider().track(frames, shelf_config)


class RecordingGeometryProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []

    def detect_changes(self, baseline, frames, shelf_config):
        self.calls.append(tuple(frame.frame_id for frame in frames))
        return MockGeometryProvider().detect_changes(baseline, frames, shelf_config)


def test_pipeline_accepts_framepacket() -> None:
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=MockTrackingProvider(),
        geometry_provider=MockGeometryProvider(),
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )

    frame = _frame(0)
    pipeline.accept(frame)

    assert len(pipeline.queue) == 1
    assert pipeline.queue.peek() is frame


def test_tracking_adapter_is_invoked() -> None:
    tracking = RecordingTrackingProvider()
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=tracking,
        geometry_provider=MockGeometryProvider(),
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )

    frame = _frame(0)
    pipeline.accept(frame)
    pipeline.process_pending()

    assert tracking.calls == [(frame.frame_id,)]


def test_geometry_adapter_is_invoked() -> None:
    geometry = RecordingGeometryProvider()
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=MockTrackingProvider(),
        geometry_provider=geometry,
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )

    frame = _frame(0)
    pipeline.accept(frame)
    pipeline.process_pending()

    assert geometry.calls == [(frame.frame_id,)]


def test_temporal_confirmation_rejects_duration_below_two_seconds() -> None:
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=MockTrackingProvider(),
        geometry_provider=MockGeometryProvider(),
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )
    event = VolumeChangeEvent(
        event_id="event-01",
        shelf_id="shelf-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=1_000_000_000,
        confirmation_timestamp_ns=2_500_000_000,
        missing_volume_m3=0.01,
        bounds_min_m=(-0.1, -0.1, 0.5),
        bounds_max_m=(0.1, 0.1, 0.9),
        centroid_m=(0.0, 0.0, 0.75),
        visible_shelf_fraction=0.9,
        confidence=0.8,
        evidence_frame_ids=("frame-0001", "frame-0002"),
    )

    assert pipeline.confirm_temporal(event) is False


def test_temporal_confirmation_accepts_exactly_two_seconds() -> None:
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=MockTrackingProvider(),
        geometry_provider=MockGeometryProvider(),
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )
    event = VolumeChangeEvent(
        event_id="event-02",
        shelf_id="shelf-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=1_000_000_000,
        confirmation_timestamp_ns=3_000_000_000,
        missing_volume_m3=0.02,
        bounds_min_m=(-0.1, -0.1, 0.5),
        bounds_max_m=(0.1, 0.1, 0.9),
        centroid_m=(0.0, 0.0, 0.75),
        visible_shelf_fraction=0.8,
        confidence=0.7,
        evidence_frame_ids=("frame-0005",),
    )

    assert pipeline.confirm_temporal(event) is True


def test_temporal_confirmation_accepts_duration_above_two_seconds() -> None:
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=MockTrackingProvider(),
        geometry_provider=MockGeometryProvider(),
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )
    event = VolumeChangeEvent(
        event_id="event-03",
        shelf_id="shelf-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=5_000_000_000,
        confirmation_timestamp_ns=9_500_000_000,
        missing_volume_m3=0.02,
        bounds_min_m=(-0.1, -0.1, 0.5),
        bounds_max_m=(0.1, 0.1, 0.9),
        centroid_m=(0.0, 0.0, 0.75),
        visible_shelf_fraction=0.8,
        confidence=0.7,
        evidence_frame_ids=("frame-0005",),
    )

    assert pipeline.confirm_temporal(event) is True


def test_temporal_confirmation_ignores_processing_delay() -> None:
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=MockTrackingProvider(),
        geometry_provider=MockGeometryProvider(),
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )
    event = VolumeChangeEvent(
        event_id="event-04",
        shelf_id="shelf-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=1_000_000_000,
        confirmation_timestamp_ns=3_000_000_000,
        missing_volume_m3=0.021,
        bounds_min_m=(-0.1, -0.1, 0.5),
        bounds_max_m=(0.1, 0.1, 0.9),
        centroid_m=(0.0, 0.0, 0.75),
        visible_shelf_fraction=0.8,
        confidence=0.75,
        evidence_frame_ids=("frame-0010",),
    )

    assert pipeline.confirm_temporal(event, processing_delay_ns=86_400_000_000_000) is True
    assert pipeline.confirm_temporal(event, processing_delay_ns=0) is True


def test_irregular_arrival_or_processing_does_not_redefine_behavioral_time() -> None:
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=MockTrackingProvider(),
        geometry_provider=MockGeometryProvider(),
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )
    event = VolumeChangeEvent(
        event_id="event-05",
        shelf_id="shelf-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=2_000_000_000,
        confirmation_timestamp_ns=3_500_000_000,
        missing_volume_m3=0.018,
        bounds_min_m=(-0.1, -0.1, 0.5),
        bounds_max_m=(0.1, 0.1, 0.9),
        centroid_m=(0.0, 0.0, 0.75),
        visible_shelf_fraction=0.82,
        confidence=0.72,
        evidence_frame_ids=("frame-0011", "frame-0014"),
    )

    assert pipeline.confirm_temporal(event) is False
    assert pipeline.confirm_temporal(event, processing_delay_ns=1_000_000_000_000) is False


def test_deterministic_rule_evaluation() -> None:
    first = MockRuleEvaluator().evaluate(
        VolumeChangeEvent(
            event_id="event-03",
            shelf_id="shelf-01",
            change_type=ChangeType.REMOVAL,
            first_seen_timestamp_ns=1,
            confirmation_timestamp_ns=2,
            missing_volume_m3=0.001,
            bounds_min_m=(-0.1, -0.1, 0.5),
            bounds_max_m=(0.1, 0.1, 0.9),
            centroid_m=(0.0, 0.0, 0.75),
            visible_shelf_fraction=0.9,
            confidence=0.8,
            evidence_frame_ids=("frame-0001", "frame-0002"),
        ),
        None,
    )
    second = MockRuleEvaluator().evaluate(
        VolumeChangeEvent(
            event_id="event-03",
            shelf_id="shelf-01",
            change_type=ChangeType.REMOVAL,
            first_seen_timestamp_ns=1,
            confirmation_timestamp_ns=2,
            missing_volume_m3=0.001,
            bounds_min_m=(-0.1, -0.1, 0.5),
            bounds_max_m=(0.1, 0.1, 0.9),
            centroid_m=(0.0, 0.0, 0.75),
            visible_shelf_fraction=0.9,
            confidence=0.8,
            evidence_frame_ids=("frame-0001", "frame-0002"),
        ),
        None,
    )

    assert first == second
    assert first is not None


def test_alert_event_generation_and_evidence_frame_ids() -> None:
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=MockTrackingProvider(),
        geometry_provider=MockGeometryProvider(),
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )
    first = _frame(0, timestamp_ns=0)
    second = _frame(1, timestamp_ns=2_000_000_000)
    pipeline.accept(first)
    pipeline.accept(second)
    alerts = pipeline.process_pending()

    assert len(alerts) == 1
    alert = alerts[0]
    assert isinstance(alert, AlertEvent)
    assert alert.shelf_id == "shelf-01"
    assert alert.evidence_frame_ids in (
        ("frame-0000", "frame-0001"),
        ("frame-0000",),
    )


def test_queue_size_two_and_oldest_unprocessed_frame_drop_behavior() -> None:
    queue = BoundedFrameQueue(maxsize=2)
    first = _frame(0)
    second = _frame(1)
    third = _frame(2)

    queue.push(first)
    queue.push(second)
    queue.push(third)

    assert len(queue) == 2
    assert queue.peek().frame_id == second.frame_id
    assert queue.history[-1].frame_id == third.frame_id
    assert queue.history[-1].timestamp_ns == third.timestamp_ns
    assert queue.dropped_frames[0]["frame_id"] == first.frame_id
    assert queue.dropped_frames[0]["timestamp_ns"] == first.timestamp_ns


def test_dropped_frame_recording_and_timestamp_preservation() -> None:
    queue = BoundedFrameQueue(maxsize=2)
    first = _frame(0, timestamp_ns=10)
    second = _frame(1, timestamp_ns=20)
    third = _frame(2, timestamp_ns=30)

    for frame in (first, second, third):
        queue.push(frame)

    assert queue.dropped_frames[0]["frame_id"] == first.frame_id
    assert queue.dropped_frames[0]["timestamp_ns"] == 10
    assert queue.peek().timestamp_ns == 20


def test_complete_mock_vertical_slice_produces_alert_event() -> None:
    pipeline = MockPipeline(
        shelf_config=_shelf(),
        tracking_provider=MockTrackingProvider(),
        geometry_provider=MockGeometryProvider(),
        rule_evaluator=MockRuleEvaluator(),
        evidence_writer=EvidenceWriter(),
    )

    pipeline.accept(_frame(0, timestamp_ns=0))
    pipeline.accept(_frame(1, timestamp_ns=2_500_000_000))

    alerts = pipeline.process_pending()

    assert len(alerts) == 1
    assert isinstance(alerts[0], AlertEvent)
    assert alerts[0].alert_id.startswith("alert-")
    assert alerts[0].reason == "suspicious shelf-removal alert"


def test_evidence_writer_writes_alert_fields() -> None:
    writer = EvidenceWriter()
    alert = AlertEvent(
        alert_id="alert-001",
        shelf_id="shelf-01",
        volume_event_id="event-001",
        person_track_id=1001,
        rule_version="mock-rule-v1",
        first_seen_timestamp_ns=1_000,
        alert_timestamp_ns=2_000,
        missing_volume_m3=0.01,
        confidence=0.8,
        reason="suspicious shelf-removal alert",
        evidence_frame_ids=("frame-0001", "frame-0002"),
    )

    path = Path("evidence") / "alert-001.json"
    result = writer.write(alert, path)
    data = json.loads(Path(result).read_text(encoding="utf-8"))

    assert data["alert_id"] == alert.alert_id
    assert data["person_track_id"] == 1001
    assert data["evidence_frame_ids"] == ["frame-0001", "frame-0002"]
