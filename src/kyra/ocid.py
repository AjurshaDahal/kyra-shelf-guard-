"""OCID-to-scenario conversion mapping and canonical layout writer.

Filesystem discovery (which frames exist, source ordering, checksum gate)
lives in ``scripts/convert_ocid.py``; this module owns the mapping semantics:
metadata parsing, depth/mask conversion, event derivation, addition-to-removal
reversal, and the on-disk layout.  Depth units follow the OCID archive scale
(0.1 mm per raw unit by default) and are stored as uint16 millimetres; zero
depth stays unknown and is never invented as free space.
"""

from __future__ import annotations

import hashlib
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from kyra.contracts import ChangeType, SourceType
from kyra.manifest import (
    MANIFEST_SCHEMA_VERSION,
    FrameRecord,
    GroundTruthEvent,
    ScenarioManifest,
    ShapeFamily,
    ShelfConfigRecord,
    write_manifest,
)

MAX_DEPTH_MM = 65_535
_PNG_WRITE_OPTIONS = (cv2.IMWRITE_PNG_COMPRESSION, 9)

CATEGORY_SHAPE_FAMILIES = {
    "box": ShapeFamily.THIN_BOX_OR_TRAY,
    "book": ShapeFamily.THIN_BOX_OR_TRAY,
    "plate": ShapeFamily.THIN_BOX_OR_TRAY,
    "bowl": ShapeFamily.CYLINDER,
    "bottle": ShapeFamily.CYLINDER,
    "cup": ShapeFamily.CYLINDER,
    "jar": ShapeFamily.CYLINDER,
    "shoe": ShapeFamily.IRREGULAR,
    "bag": ShapeFamily.HANDLED_OR_HANGING,
}
DEFAULT_SHAPE_FAMILY = ShapeFamily.IRREGULAR


@dataclass(frozen=True, slots=True)
class OcidCamera:
    width: int
    height: int
    fx: float
    fy: float
    cx: float
    cy: float
    depth_scale: float

    @property
    def intrinsics(self) -> tuple[tuple[float, float, float], ...]:
        return (
            (self.fx, 0.0, self.cx),
            (0.0, self.fy, self.cy),
            (0.0, 0.0, 1.0),
        )


@dataclass(frozen=True, slots=True)
class OcidObjectRef:
    object_id: int
    category: str


@dataclass(frozen=True, slots=True)
class OcidFrame:
    frame_id: str
    objects: tuple[OcidObjectRef, ...] = ()


@dataclass(frozen=True, slots=True)
class OcidSequenceMetadata:
    database_name: str
    database_version: str | None
    camera: OcidCamera
    frames: tuple[OcidFrame, ...]


def parse_sequence_metadata(text: str) -> OcidSequenceMetadata:
    """Parse and strictly validate OCID-style TOML metadata."""
    try:
        payload = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"invalid OCID metadata TOML: {error}") from None
    database = payload.get("database")
    camera_values = payload.get("camera")
    frame_values = payload.get("frames")
    if not isinstance(database, dict) or not isinstance(camera_values, dict):
        raise ValueError("OCID metadata must define database and camera tables")
    if not isinstance(frame_values, list) or not frame_values:
        raise ValueError("OCID metadata must define at least one frame")

    required_camera = ("width", "height", "fx", "fy", "cx", "cy", "depth_scale")
    missing = [name for name in required_camera if name not in camera_values]
    if missing:
        raise ValueError(f"OCID camera table is missing fields: {sorted(missing)}")
    try:
        camera = OcidCamera(
            width=int(camera_values["width"]),
            height=int(camera_values["height"]),
            fx=float(camera_values["fx"]),
            fy=float(camera_values["fy"]),
            cx=float(camera_values["cx"]),
            cy=float(camera_values["cy"]),
            depth_scale=float(camera_values["depth_scale"]),
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"OCID camera values must be numeric: {error}") from None
    if camera.width < 1 or camera.height < 1 or camera.depth_scale <= 0:
        raise ValueError("OCID camera width/height must be positive and depth_scale > 0")

    frames: list[OcidFrame] = []
    seen: set[str] = set()
    for raw_frame in frame_values:
        if not isinstance(raw_frame, dict) or "id" not in raw_frame:
            raise ValueError("every OCID frame must define an id string")
        frame_id = str(raw_frame["id"])
        if frame_id in seen:
            raise ValueError(f"duplicate OCID frame id: {frame_id!r}")
        seen.add(frame_id)
        objects: list[OcidObjectRef] = []
        for raw_object in raw_frame.get("objects", []):
            if not isinstance(raw_object, dict) or "id" not in raw_object:
                raise ValueError(f"frame {frame_id!r} has an invalid object entry")
            objects.append(
                OcidObjectRef(
                    object_id=int(raw_object["id"]),
                    category=str(raw_object.get("category", "unknown")),
                )
            )
        frames.append(OcidFrame(frame_id=frame_id, objects=tuple(objects)))
    return OcidSequenceMetadata(
        database_name=str(database.get("name", "ocid")),
        database_version=database.get("version"),
        camera=camera,
        frames=tuple(frames),
    )


def ocid_depth_to_mm(raw_depth: np.ndarray, depth_scale: float) -> np.ndarray:
    """Map raw OCID depth units to uint16 millimetres, keeping zero as unknown."""
    values = np.asarray(raw_depth).astype(np.float64) * depth_scale * 1000.0
    if not np.all(np.isfinite(values)) or np.any(values > max(MAX_DEPTH_MM, 0)):
        raise ValueError("OCID depth contains values that cannot be stored in uint16 mm")
    return np.round(values).astype(np.uint16)


def valid_mask(raw_depth: np.ndarray) -> np.ndarray:
    return (np.asarray(raw_depth) > 0).astype(np.uint8) * 255


def object_mask(segmentation: np.ndarray, object_id: int) -> np.ndarray:
    return (np.asarray(segmentation) == object_id).astype(np.uint8) * 255


def shape_family_for(category: str) -> ShapeFamily:
    return CATEGORY_SHAPE_FAMILIES.get(category, DEFAULT_SHAPE_FAMILY)


def derive_events(
    frames: Sequence[OcidFrame],
) -> list[tuple[int, ChangeType, OcidObjectRef]]:
    """Report ADDITION/REMOVAL transitions inside the recorded window.

    The first frame establishes the initial state; only transitions between
    consecutive recorded frames produce events, so a sequence that starts with
    an object does not invent an addition for it.
    """
    present: dict[int, OcidObjectRef] = {}
    events: list[tuple[int, ChangeType, OcidObjectRef]] = []
    for index, frame in enumerate(frames):
        current = {entry.object_id: entry for entry in frame.objects}
        if index == 0:
            present = current
            continue
        for object_id in sorted(current):
            if object_id not in present:
                events.append((index, ChangeType.ADDITION, current[object_id]))
        for object_id in sorted(present):
            if object_id not in current:
                events.append((index, ChangeType.REMOVAL, present[object_id]))
        present = current
    return events


def sha256_of_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_converted_sequence(
    metadata: OcidSequenceMetadata,
    frames: Sequence[tuple[np.ndarray, np.ndarray, np.ndarray]],
    output_dir: str | Path,
    *,
    shelf: ShelfConfigRecord,
    scenario_id: str,
    seed: int,
    reverse: bool = False,
    first_timestamp_ns: int = 1_000_000_000,
    frame_step_ns: int = 1_000_000_000,
    notes: Sequence[str] = (),
) -> tuple[ScenarioManifest, str]:
    """Convert OCID frames into a manifest 1.1 scenario and write its assets.

    ``frames`` holds one ``(rgb_bgr, raw_depth, segmentation)`` triple per
    source frame in source order.  With ``reverse=True`` the output plays the
    source sequence backwards, which turns a valid addition into a removal;
    timestamps are re-created monotonically and the expected event direction
    flips while provenance notes keep the original direction.
    """
    if len(frames) != len(metadata.frames):
        raise ValueError(
            f"expected {len(metadata.frames)} OCID frames, got {len(frames)}"
        )
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / "rgb").mkdir(exist_ok=True)
    (root / "depth").mkdir(exist_ok=True)
    (root / "masks").mkdir(exist_ok=True)

    source_order = list(range(len(frames)))
    output_order = list(reversed(source_order)) if reverse else source_order
    output_metadata_frames = [metadata.frames[index] for index in output_order]
    output_events = derive_events(output_metadata_frames)
    removal_output_indices = {
        index
        for index, change_type, _ in output_events
        if change_type is ChangeType.REMOVAL
    }

    records: list[FrameRecord] = []
    timestamps: list[int] = []
    for output_index, source_index in enumerate(output_order):
        rgb_bgr, raw_depth, segmentation = frames[source_index]
        frame_id = metadata.frames[source_index].frame_id
        depth_mm = ocid_depth_to_mm(raw_depth, metadata.camera.depth_scale)
        mask = valid_mask(raw_depth)
        rgb_path = f"rgb/{frame_id}.png"
        depth_path = f"depth/{frame_id}.png"
        valid_path = f"masks/{frame_id}-valid.png"
        object_path: str | None = None
        source_frame = metadata.frames[source_index]
        if source_frame.objects or output_index in removal_output_indices:
                if source_frame.objects:
                    object_segmentation = segmentation
                    object_ids = [entry.object_id for entry in source_frame.objects]
                else:
                    previous_source_index = output_order[output_index - 1]
                    object_segmentation = frames[previous_source_index][2]
                    previous_frame = metadata.frames[previous_source_index]
                    object_ids = [entry.object_id for entry in previous_frame.objects]
                object_mask_image = object_mask(
                    object_segmentation, object_ids[0]
                )
                for object_id in object_ids[1:]:
                    object_mask_image = np.maximum(
                        object_mask_image,
                        object_mask(object_segmentation, object_id),
                    )
                object_path = f"masks/{frame_id}-object.png"
                _write_png(root / object_path, object_mask_image)

        _write_png(root / rgb_path, rgb_bgr)
        _write_png(root / depth_path, depth_mm)
        _write_png(root / valid_path, mask)

        timestamp_ns = first_timestamp_ns + output_index * frame_step_ns
        timestamps.append(timestamp_ns)
        records.append(
            FrameRecord(
                frame_id=frame_id,
                timestamp_ns=timestamp_ns,
                rgb_path=rgb_path,
                depth_path=depth_path,
                valid_mask_path=valid_path,
                object_mask_path=object_path,
            )
        )

    events: list[GroundTruthEvent] = []
    for output_index, change_type, obj in output_events:
        events.append(
            GroundTruthEvent(
                change_type=change_type,
                first_seen_timestamp_ns=timestamps[output_index],
                shape_family=shape_family_for(obj.category),
                should_alert=change_type is ChangeType.REMOVAL,
            )
        )

    extra_notes = ["public source: OCID"]
    if reverse:
        extra_notes.append(
            "reversed direction: original sequence was an addition; "
            "timestamps and expected event were re-created for a removal"
        )
    if removal_output_indices:
        extra_notes.append(
            "removal-frame object masks mark the last-seen object region "
            "carried over from the immediately preceding frame"
        )
    manifest = ScenarioManifest(
        schema_version=MANIFEST_SCHEMA_VERSION,
        scenario_id=scenario_id,
        random_seed=seed,
        source_type=SourceType.PUBLIC_RGBD,
        evidence_source="public_rgbd",
        category=metadata.database_name,
        split="development",
        intrinsics=metadata.camera.intrinsics,
        camera_to_shelf=(
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ),
        shelf=shelf,
        baseline_frame_ids=[records[0].frame_id],
        frames=records,
        ground_truth_events=events,
        notes=[*extra_notes, *notes],
    )
    return manifest, write_manifest(manifest, root / "scenario.json")


def _write_png(path: Path, image: np.ndarray) -> None:
    if not cv2.imwrite(str(path), image, _PNG_WRITE_OPTIONS):
        raise RuntimeError(f"could not write converted asset {path}")