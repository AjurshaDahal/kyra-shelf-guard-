"""Versioned JSON scenario format used by simulation, replay, and evaluation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from kyra.contracts import SCHEMA_VERSION, ChangeType, SourceType


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ShelfConfigRecord(StrictModel):
    shelf_id: str
    roi_xyxy: tuple[int, int, int, int]
    bounds_min_m: tuple[float, float, float]
    bounds_max_m: tuple[float, float, float]
    voxel_size_m: float = 0.01


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
    tracks: list[TrackAnnotation] = Field(default_factory=list)


class GroundTruthEvent(StrictModel):
    change_type: ChangeType
    first_seen_timestamp_ns: int
    volume_m3: float = 0.0
    bounds_min_m: tuple[float, float, float] | None = None
    bounds_max_m: tuple[float, float, float] | None = None
    associated_track_id: int | None = None
    should_alert: bool = False


class ScenarioManifest(StrictModel):
    schema_version: str = SCHEMA_VERSION
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

    @model_validator(mode="after")
    def validate_frame_references(self) -> ScenarioManifest:
        frame_ids = {frame.frame_id for frame in self.frames}
        if len(frame_ids) != len(self.frames):
            raise ValueError("frame IDs must be unique")
        missing = set(self.baseline_frame_ids) - frame_ids
        if missing:
            raise ValueError(f"baseline frames missing from manifest: {sorted(missing)}")
        timestamps = [frame.timestamp_ns for frame in self.frames]
        if timestamps != sorted(timestamps):
            raise ValueError("frames must be ordered by timestamp")
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
