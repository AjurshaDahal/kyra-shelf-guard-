from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Protocol, runtime_checkable

import numpy as np

from kyra.contracts import (
    AlertEvent,
    BaselineArtifact,
    ChangeType,
    FramePacket,
    PersonTrack,
    ShelfConfig,
    VolumeChangeEvent,
)


@runtime_checkable
class BaselineProvider(Protocol):
    def build(
        self,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> BaselineArtifact:
        ...


@runtime_checkable
class TrackingProvider(Protocol):
    def track(
        self,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> tuple[PersonTrack, ...]:
        ...


@runtime_checkable
class GeometryProvider(Protocol):
    def detect_changes(
        self,
        baseline: BaselineArtifact,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> tuple[VolumeChangeEvent, ...]:
        ...


@runtime_checkable
class RuleEvaluator(Protocol):
    def evaluate(
        self,
        volume_event: VolumeChangeEvent,
        person_track: PersonTrack | None,
    ) -> AlertEvent | None:
        ...


class MockBaselineProvider:
    """Deterministic baseline stand-in for future Person 1 integration."""

    def __call__(
        self,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> BaselineArtifact:
        return self.build(frames, shelf_config)

    def build(
        self,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> BaselineArtifact:
        if not frames:
            raise ValueError("baseline mock requires at least one frame")

        depth_stack = np.stack([frame.depth_m for frame in frames], axis=0).astype(np.float32)
        valid_stack = np.stack([frame.valid_depth_mask for frame in frames], axis=0)
        baseline_depth = np.median(depth_stack, axis=0).astype(np.float32)
        valid_mask = np.all(valid_stack, axis=0)

        shape = baseline_depth.shape
        occupancy = np.zeros((*shape, 1), dtype=np.uint8)
        occupancy[..., 0] = valid_mask.astype(np.uint8)

        first = frames[0]
        digest = hashlib.sha256()
        digest.update(
            json.dumps(
                {
                    "shelf_id": shelf_config.shelf_id,
                    "roi_xyxy": shelf_config.roi_xyxy,
                    "bounds_min_m": shelf_config.bounds_min_m,
                    "bounds_max_m": shelf_config.bounds_max_m,
                    "frame_ids": [frame.frame_id for frame in frames],
                    "timestamps_ns": [frame.timestamp_ns for frame in frames],
                },
                sort_keys=True,
            ).encode("utf-8")
        )

        return BaselineArtifact(
            shelf_id=shelf_config.shelf_id,
            roi_xyxy=shelf_config.roi_xyxy,
            bounds_min_m=shelf_config.bounds_min_m,
            bounds_max_m=shelf_config.bounds_max_m,
            baseline_depth_m=baseline_depth,
            valid_mask=valid_mask,
            fixed_geometry_mask=np.ones(shape, dtype=bool),
            portable_components=(),
            occupancy_grid=occupancy,
            noise_sigma_m=np.zeros(shape, dtype=np.float32),
            intrinsics=first.intrinsics.copy(),
            camera_to_shelf=first.camera_to_shelf.copy(),
            calibration_checksum=digest.hexdigest(),
            metadata={
                "source_frames": [frame.frame_id for frame in frames],
                "deterministic_mock": True,
            },
        )


class MockTrackingProvider:
    """Deterministic tracking stand-in for future Person 3 integration."""

    def __call__(
        self,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> tuple[PersonTrack, ...]:
        return self.track(frames, shelf_config)

    def track(
        self,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> tuple[PersonTrack, ...]:
        tracks: list[PersonTrack] = []
        for index, frame in enumerate(frames):
            track_id = 1001 + index
            pose = np.array(
                [
                    [1.0, 1.0, 0.95],
                    [2.0, 2.0, 0.90],
                    [3.0, 3.0, 0.88],
                ],
                dtype=np.float32,
            )
            tracks.append(
                PersonTrack(
                    track_id=track_id,
                    timestamp_ns=frame.timestamp_ns,
                    box_xyxy=(0.0 + index * 0.1, 0.0, 1.0 + index * 0.1, 1.0),
                    pose_keypoints_xyc=pose,
                    position_m=(0.0 + index * 0.02, 0.0, 0.8),
                    near_shelf=True,
                    wrist_in_shelf=False,
                    authorized=False,
                )
            )
        return tuple(tracks)


class MockGeometryProvider:
    """Deterministic geometry stand-in for future Person 2 integration."""

    def __call__(
        self,
        baseline: BaselineArtifact,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> tuple[VolumeChangeEvent, ...]:
        return self.detect_changes(baseline, frames, shelf_config)

    def detect_changes(
        self,
        baseline: BaselineArtifact,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> tuple[VolumeChangeEvent, ...]:
        if not frames:
            return ()

        first = frames[0]
        last = frames[-1]
        evidence = (first.frame_id, last.frame_id)
        event = VolumeChangeEvent(
            event_id="volume-change-0001",
            shelf_id=shelf_config.shelf_id,
            change_type=ChangeType.REMOVAL,
            first_seen_timestamp_ns=first.timestamp_ns,
            confirmation_timestamp_ns=last.timestamp_ns,
            missing_volume_m3=0.0125,
            bounds_min_m=(-0.1, -0.1, 0.5),
            bounds_max_m=(0.1, 0.1, 0.9),
            centroid_m=(0.0, 0.0, 0.75),
            visible_shelf_fraction=0.92,
            confidence=0.88,
            evidence_frame_ids=evidence,
        )
        return (event,)


class MockRuleEvaluator:
    """Deterministic alert decision stand-in for future Person 3 rules."""

    def __call__(
        self,
        volume_event: VolumeChangeEvent,
        person_track: PersonTrack | None,
    ) -> AlertEvent | None:
        return self.evaluate(volume_event, person_track)

    def evaluate(
        self,
        volume_event: VolumeChangeEvent,
        person_track: PersonTrack | None,
    ) -> AlertEvent | None:
        if volume_event.change_type is not ChangeType.REMOVAL:
            return None
        if person_track is not None and person_track.authorized:
            return None

        person_track_id = person_track.track_id if person_track is not None else -1
        return AlertEvent(
            alert_id=f"alert-{volume_event.event_id}",
            shelf_id=volume_event.shelf_id,
            volume_event_id=volume_event.event_id,
            person_track_id=person_track_id,
            rule_version="mock-rule-v1",
            first_seen_timestamp_ns=volume_event.first_seen_timestamp_ns,
            alert_timestamp_ns=volume_event.confirmation_timestamp_ns,
            missing_volume_m3=volume_event.missing_volume_m3,
            confidence=volume_event.confidence,
            reason="suspicious shelf-removal alert",
            evidence_frame_ids=volume_event.evidence_frame_ids,
        )


class LazyUltralyticsTrackingProvider:
    """Optional YOLO + ByteTrack provider with lazy heavy-dependency loading.

    Importing :mod:`kyra.adapters` does not import Torch or Ultralytics.
    Those dependencies are loaded only when ``track()`` is first called.
    """

    def __init__(
        self,
        model: str = "yolo11n.pt",
        *,
        confidence: float = 0.25,
        tracker: str = "bytetrack.yaml",
    ) -> None:
        self.model_name = model
        self.confidence = confidence
        self.tracker = tracker
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise RuntimeError(
                    "Optional pretrained tracking requires the tracking "
                    "dependencies. Install requirements-gpu.lock before use."
                ) from exc

            self._model = YOLO(self.model_name)

        return self._model

    def track(
        self,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> tuple[PersonTrack, ...]:
        del shelf_config

        if not frames:
            return ()

        model = self._load_model()
        tracks: list[PersonTrack] = []

        for frame in frames:
            # FramePacket uses RGB in memory (C-001), while Ultralytics treats
            # NumPy image sources as OpenCV-style BGR.
            source_bgr = np.ascontiguousarray(frame.rgb[..., ::-1])
            results = model.track(
                source=source_bgr,
                persist=True,
                classes=[0],
                conf=self.confidence,
                tracker=self.tracker,
                verbose=False,
            )

            for result in results:
                boxes = result.boxes
                if boxes is None or boxes.xyxy is None:
                    continue

                xyxy = boxes.xyxy.cpu().numpy()
                ids = (
                    boxes.id.cpu().numpy()
                    if boxes.id is not None
                    else np.arange(len(xyxy), dtype=np.int64)
                )

                for box, track_id in zip(xyxy, ids, strict=True):
                    x1, y1, x2, y2 = (float(value) for value in box)

                    tracks.append(
                        PersonTrack(
                            track_id=int(track_id),
                            timestamp_ns=frame.timestamp_ns,
                            box_xyxy=(x1, y1, x2, y2),
                            pose_keypoints_xyc=np.empty((0, 3), dtype=np.float32),
                            position_m=None,
                            near_shelf=False,
                            wrist_in_shelf=False,
                            authorized=False,
                        )
                    )

        return tuple(
            sorted(
                tracks,
                key=lambda track: (
                    track.timestamp_ns,
                    track.track_id,
                    track.box_xyxy,
                ),
            )
        )


__all__ = [
    "BaselineProvider",
    "TrackingProvider",
    "GeometryProvider",
    "RuleEvaluator",
    "MockBaselineProvider",
    "MockTrackingProvider",
    "LazyUltralyticsTrackingProvider",
    "MockGeometryProvider",
    "MockRuleEvaluator",
]
