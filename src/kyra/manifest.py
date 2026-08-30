"""Versioned JSON scenario format used by simulation, replay, and evaluation."""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from kyra.contracts import SHELF_CONFIG_C007_FIELDS, ChangeType, SourceType

MANIFEST_SCHEMA_VERSION = "1.1"
SUPPORTED_MANIFEST_VERSIONS = {"1.0", "1.1"}


class ShapeFamily(StrEnum):
    THIN_BOX_OR_TRAY = "thin_box_or_tray"
    CYLINDER = "cylinder"
    IRREGULAR = "irregular"
    HANDLED_OR_HANGING = "handled_or_hanging"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ShelfConfigRecord(StrictModel):
    shelf_id: str
    roi_xyxy: tuple[int, int, int, int]
    bounds_min_m: tuple[float, float, float]
    bounds_max_m: tuple[float, float, float]
    voxel_size_m: float = 0.01

    @property
    def c007_fields(self) -> tuple[str, ...]:
        """Return the exact field names in the approved C-007 v1 shelf boundary."""
        return SHELF_CONFIG_C007_FIELDS

    @property
    def c007_values(self) -> dict[str, object]:
        """Return the approved C-007 v1 shelf boundary values without expanding scope."""
        return {name: getattr(self, name) for name in SHELF_CONFIG_C007_FIELDS}


class TrackAnnotation(StrictModel):
    track_id: int
    box_xyxy: tuple[float, float, float, float]
    pose_keypoints_xyc: list[tuple[float, float, float]] = Field(default_factory=list)
    position_m: tuple[float, float, float] | None = None
    near_shelf: bool = False
    authorized: bool = False


class FrameRecord(StrictModel):
    frame_id: str
    timestamp_ns: int
    rgb_path: str
    depth_path: str
    valid_mask_path: str | None = None
    occlusion_mask_path: str | None = None
    object_mask_path: str | None = None
    tracks: list[TrackAnnotation] = Field(default_factory=list)


class GroundTruthEvent(StrictModel):
    change_type: ChangeType
    first_seen_timestamp_ns: int
    volume_m3: float = 0.0
    bounds_min_m: tuple[float, float, float] | None = None
    bounds_max_m: tuple[float, float, float] | None = None
    associated_track_id: int | None = None
    shape_family: ShapeFamily | None = None
    should_alert: bool = False


class ScenarioManifest(StrictModel):
    schema_version: str = MANIFEST_SCHEMA_VERSION
    scenario_id: str
    random_seed: int
    source_type: SourceType
    evidence_source: Literal["synthetic", "public_rgbd", "tracker_only", "real_end_to_end"]
    category: str
    held_out_category: bool = False
    split: Literal["development", "frozen_test", "golden"] = "golden"
    intrinsics: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]
    camera_to_shelf: tuple[
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
        tuple[float, float, float, float],
    ]
    shelf: ShelfConfigRecord
    baseline_frame_ids: list[str]
    frames: list[FrameRecord]
    ground_truth_events: list[GroundTruthEvent] = Field(default_factory=list)
    system_mode: Literal["NORMAL", "RESTOCK_MODE"] = "NORMAL"
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def validate_schema_version(cls, values: object) -> object:
        if not isinstance(values, dict):
            return values
        version = values.get("schema_version", MANIFEST_SCHEMA_VERSION)
        if version not in SUPPORTED_MANIFEST_VERSIONS:
            raise ValueError(f"unsupported manifest version: {version!r}")
        return values

    @model_validator(mode="after")
    def validate_frame_references(self) -> ScenarioManifest:
        if self.schema_version not in SUPPORTED_MANIFEST_VERSIONS:
            raise ValueError(f"unsupported manifest version: {self.schema_version!r}")

        frame_ids = {frame.frame_id for frame in self.frames}
        if len(frame_ids) != len(self.frames):
            raise ValueError("frame IDs must be unique")
        missing = set(self.baseline_frame_ids) - frame_ids
        if missing:
            raise ValueError(f"baseline frames missing from manifest: {sorted(missing)}")
        timestamps = [frame.timestamp_ns for frame in self.frames]
        if timestamps != sorted(timestamps):
            raise ValueError("frames must be ordered by timestamp")

        if self.schema_version == "1.1":
            for event in self.ground_truth_events:
                if event.shape_family is None:
                    raise ValueError("version 1.1 object events must define shape_family")
            event_frames = {
                frame.frame_id: frame
                for frame in self.frames
                if frame.timestamp_ns
                in {event.first_seen_timestamp_ns for event in self.ground_truth_events}
            }
            for event in self.ground_truth_events:
                frame = event_frames.get(next(
                    (
                        frame.frame_id
                        for frame in self.frames
                        if frame.timestamp_ns == event.first_seen_timestamp_ns
                    ),
                    None,
                ))
                if frame is not None and frame.object_mask_path is None:
                    raise ValueError(
                        "version 1.1 object frames must define object_mask_path"
                    )

        return self


def load_manifest(path: str | Path) -> ScenarioManifest:
    return ScenarioManifest.model_validate_json(Path(path).read_text(encoding="utf-8"))


def write_manifest(manifest: ScenarioManifest, path: str | Path) -> str:
    """Write canonical JSON and return its SHA-256 checksum."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = manifest.model_dump_json(indent=2) + "\n"
    destination.write_text(payload, encoding="utf-8", newline="\n")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def manifest_checksum(manifest: ScenarioManifest) -> str:
    payload = json.dumps(manifest.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
