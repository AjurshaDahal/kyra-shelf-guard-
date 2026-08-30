from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kyra.adapters import (
    BaselineProvider,
    GeometryProvider,
    MockBaselineProvider,
    RuleEvaluator,
    TrackingProvider,
)
from kyra.contracts import (
    AlertEvent,
    FramePacket,
    ShelfConfig,
    VolumeChangeEvent,
)


@dataclass(slots=True)
class BoundedFrameQueue:
    """Bounded frame queue that drops the oldest unprocessed frame when full."""

    maxsize: int = 2
    _frames: deque[FramePacket] = field(default_factory=deque)
    dropped_frames: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.maxsize <= 0:
            raise ValueError("queue size must be positive")

    def __len__(self) -> int:
        return len(self._frames)

    @property
    def history(self) -> tuple[FramePacket, ...]:
        return tuple(self._frames)

    def push(self, frame: FramePacket) -> None:
        if len(self._frames) >= self.maxsize:
            dropped = self._frames.popleft()
            self.dropped_frames.append(
                {
                    "frame_id": dropped.frame_id,
                    "timestamp_ns": dropped.timestamp_ns,
                    "reason": "oldest_unprocessed_frame_dropped",
                }
            )
        self._frames.append(frame)

    def peek(self) -> FramePacket:
        if not self._frames:
            raise IndexError("queue is empty")
        return self._frames[0]

    def pop(self) -> FramePacket:
        if not self._frames:
            raise IndexError("queue is empty")
        return self._frames.popleft()


@dataclass(slots=True)
class EvidenceWriter:
    """Write minimal evidence records using the existing contract fields."""

    output_dir: Path = Path("evidence")

    def write(self, alert: AlertEvent, path: str | Path | None = None) -> str:
        record = {
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
        destination = (
            Path(path)
            if path is not None
            else self.output_dir / f"{alert.alert_id}.json"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return str(destination)


@dataclass(slots=True)
class MockPipeline:
    shelf_config: ShelfConfig
    tracking_provider: TrackingProvider
    geometry_provider: GeometryProvider
    rule_evaluator: RuleEvaluator
    evidence_writer: EvidenceWriter = field(default_factory=EvidenceWriter)
    queue: BoundedFrameQueue = field(default_factory=lambda: BoundedFrameQueue(maxsize=2))
    baseline_provider: BaselineProvider = field(default_factory=MockBaselineProvider)

    def accept(self, frame: FramePacket) -> None:
        self.queue.push(frame)

    def confirm_temporal(
        self,
        volume_event: VolumeChangeEvent,
        *,
        processing_delay_ns: int = 0,
    ) -> bool:
        del processing_delay_ns
        duration_ns = (
            volume_event.confirmation_timestamp_ns - volume_event.first_seen_timestamp_ns
        )
        return duration_ns >= 2_000_000_000

    def process_pending(self) -> list[AlertEvent]:
        if not self.queue:
            return []

        frames = tuple(self.queue.pop() for _ in range(len(self.queue)))
        tracking = self.tracking_provider.track(frames, self.shelf_config)
        if not tracking:
            return []

        baseline = self.baseline_provider.build(frames, self.shelf_config)
        events = self.geometry_provider.detect_changes(baseline, frames, self.shelf_config)
        if not events:
            return []

        alerts: list[AlertEvent] = []
        for event in events:
            if not self.confirm_temporal(event):
                continue
            chosen = tracking[0] if len(tracking) > 0 else None
            alert = self.rule_evaluator.evaluate(event, chosen)
            if alert is None:
                continue
            alerts.append(alert)
            self.evidence_writer.write(alert)
        return alerts


__all__ = [
    "BoundedFrameQueue",
    "MockPipeline",
    "EvidenceWriter",
]
