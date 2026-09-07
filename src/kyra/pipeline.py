from __future__ import annotations

import json
from collections import deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

from kyra.adapters import (
    BaselineProvider,
    GeometryProvider,
    MockBaselineProvider,
    RuleEvaluator,
    TrackingProvider,
)
from kyra.baseline import BaselineBuilder, load_baseline
from kyra.contracts import (
    AlertEvent,
    FramePacket,
    PersonTrack,
    ShelfConfig,
    SystemMode,
    VolumeChangeEvent,
)
from kyra.geometry.provider import ShelfGeometryProvider
from kyra.io import ScenarioFrameSource
from kyra.proximity.occlusion import build_person_occlusion_mask
from kyra.proximity.person_proximity import update_proximity
from kyra.rules.alert_engine import evaluate_removal_alert
from kyra.tracking.replay_tracker import ReplayTracker


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


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def run_scenario(
    manifest_path: str | Path,
    *,
    baseline_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run one replay scenario through the real owner implementations.

    Saved track positions are input annotations, not ground-truth event labels.
    Ground-truth events are deliberately untouched here and are only consumed by
    the separate evaluation command after inference completes.
    """

    source = ScenarioFrameSource(manifest_path)
    shelf = ShelfConfig(**source.manifest.shelf.c007_values)
    baseline = (
        load_baseline(baseline_path)
        if baseline_path is not None
        else BaselineBuilder(minimum_frames=len(source.manifest.baseline_frame_ids)).fit(
            source.baseline_frames(), shelf
        )
    )
    if baseline.shelf_id != shelf.shelf_id:
        raise ValueError(
            f"baseline shelf {baseline.shelf_id!r} does not match scenario shelf "
            f"{shelf.shelf_id!r}"
        )

    tracker = ReplayTracker(source)
    event_frames = list(source.event_frames())
    person_masks: list[np.ndarray] = []
    track_state: dict[int, PersonTrack] = {}

    for frame in event_frames:
        tracks = list(tracker.tracks_for_frame(frame.frame_id))
        annotations = source.track_annotations(frame.frame_id)
        for track, annotation in zip(tracks, annotations, strict=True):
            previous = track_state.get(track.track_id)
            if previous is not None:
                track.last_near_timestamp_ns = previous.last_near_timestamp_ns
            track.position_m = annotation.position_m
            track.authorized = annotation.authorized
            update_proximity(track, shelf)
            track_state[track.track_id] = track

        replay_mask = build_person_occlusion_mask(
            tuple(tracks), frame.depth_m.shape
        )
        person_masks.append(source.occlusion_mask(frame.frame_id) | replay_mask)

    events = ShelfGeometryProvider().detect_changes(
        baseline,
        event_frames,
        shelf,
        person_occlusion_masks=person_masks,
    )
    mode = SystemMode(source.manifest.system_mode)
    alerts: list[AlertEvent] = []
    alerted_event_ids: set[str] = set()
    for event in events:
        if event.event_id in alerted_event_ids:
            continue
        alert = evaluate_removal_alert(
            event,
            tuple(track_state.values()),
            shelf,
            system_mode=mode,
        )
        if alert is not None:
            alerts.append(alert)
            alerted_event_ids.add(event.event_id)

    return {
        "scenario_id": source.manifest.scenario_id,
        "manifest_path": str(Path(manifest_path).resolve()),
        "evidence_source": source.manifest.evidence_source,
        "baseline_checksum": baseline.calibration_checksum,
        "shelf_config": _jsonable(asdict(shelf)),
        "event_frames_processed": len(event_frames),
        "event_count": len(events),
        "alert_count": len(alerts),
        "events": [_jsonable(asdict(event)) for event in events],
        "alerts": [_jsonable(asdict(alert)) for alert in alerts],
    }


__all__ = [
    "BoundedFrameQueue",
    "MockPipeline",
    "EvidenceWriter",
    "run_scenario",
]
