"""Small deterministic RGB-D scenarios for offline Person 1 testing.

The lightweight generator deliberately uses only Kyra's core NumPy and OpenCV
dependencies.  It produces inspectable PNG assets and the approved manifest
1.1 format; optional realism tools remain separate adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

import cv2
import numpy as np

from kyra.contracts import ChangeType, SourceType
from kyra.manifest import (
    FrameRecord,
    GroundTruthEvent,
    ScenarioManifest,
    ShapeFamily,
    ShelfConfigRecord,
    TrackAnnotation,
    write_manifest,
)

GENERATOR_VERSION = "1.0"
_BACKGROUND_DEPTH_MM = 1_400
_PNG_WRITE_OPTIONS = [cv2.IMWRITE_PNG_COMPRESSION, 9]


class ScenarioCondition(StrEnum):
    """Synthetic condition applied after the opening baseline."""

    OBJECT_CHANGE = "object_change"
    NO_CHANGE = "no_change"
    PERSON_ONLY_OCCLUSION = "person_only_occlusion"
    REMOVAL_THEN_OCCLUSION = "removal_then_occlusion"
    LIGHTING_VARIATION = "lighting_variation"
    INVALID_DEPTH = "invalid_depth"
    CAMERA_DRIFT = "camera_drift"
@dataclass(frozen=True, slots=True)
class ScenarioSettings:
    """Inputs that fully determine one lightweight scenario."""

    scenario_id: str
    random_seed: int
    category: str
    shape_family: ShapeFamily
    change_type: ChangeType | None
    should_alert: bool
    condition: ScenarioCondition = ScenarioCondition.OBJECT_CHANGE
    system_mode: Literal["NORMAL", "RESTOCK_MODE"] = "NORMAL"
    held_out_category: bool = False
    split: Literal["development", "frozen_test", "golden"] = "development"
    width: int = 64
    height: int = 48
    baseline_frame_count: int = 30
    event_frame_count: int = 2
    start_timestamp_ns: int = 1_000_000_000
    frame_interval_ns: int = 100_000_000

    def __post_init__(self) -> None:
        if not self.scenario_id.strip():
            raise ValueError("scenario_id must not be empty")
        if not self.category.strip():
            raise ValueError("category must not be empty")
        if self.random_seed < 0:
            raise ValueError("random_seed must be non-negative")
        object_change_conditions = {
            ScenarioCondition.OBJECT_CHANGE,
            ScenarioCondition.REMOVAL_THEN_OCCLUSION,
        }
        if self.condition in object_change_conditions:
            if self.change_type not in (ChangeType.REMOVAL, ChangeType.ADDITION):
                raise ValueError("object-change scenarios must be removal or addition")
        elif self.change_type is not None:
            raise ValueError("non-change conditions must not declare an object change")
        if (
            self.condition is ScenarioCondition.REMOVAL_THEN_OCCLUSION
            and self.change_type is not ChangeType.REMOVAL
        ):
            raise ValueError("removal-then-occlusion requires a removal change")
        if (
            self.condition is ScenarioCondition.REMOVAL_THEN_OCCLUSION
            and self.event_frame_count < 2
        ):
            raise ValueError("removal-then-occlusion requires at least two event frames")
        if self.change_type is None and self.should_alert:
            raise ValueError("a scenario without an object change cannot expect an alert")
        if self.width < 32 or self.height < 24:
            raise ValueError("scenario dimensions must be at least 32 by 24 pixels")
        if self.baseline_frame_count < 1:
            raise ValueError("baseline_frame_count must be positive")
        if self.event_frame_count < 1:
            raise ValueError("event_frame_count must be positive")
        if self.start_timestamp_ns < 0:
            raise ValueError("start_timestamp_ns must be non-negative")
        if self.frame_interval_ns <= 0:
            raise ValueError("frame_interval_ns must be positive")


def _object_mask(
    height: int,
    width: int,
    shape_family: ShapeFamily,
    rng: np.random.Generator,
) -> np.ndarray:
    mask = np.zeros((height, width), dtype=np.uint8)
    center_x = width // 2 + int(rng.integers(-(width // 8), width // 8 + 1))
    center_y = height // 2 + int(rng.integers(-(height // 10), height // 10 + 1))
    scale = int(rng.integers(0, 3))

    if shape_family is ShapeFamily.THIN_BOX_OR_TRAY:
        half_width = width // 7 + scale
        half_height = max(2, height // 16 + scale)
        cv2.rectangle(
            mask,
            (center_x - half_width, center_y - half_height),
            (center_x + half_width, center_y + half_height),
            255,
            thickness=-1,
        )
    elif shape_family is ShapeFamily.CYLINDER:
        axes = (max(3, width // 12 + scale), max(5, height // 7 + scale))
        cv2.ellipse(mask, (center_x, center_y), axes, 0, 0, 360, 255, thickness=-1)
    elif shape_family is ShapeFamily.IRREGULAR:
        radius = max(4, height // 10 + scale)
        points = np.array(
            [
                (center_x - 2 * radius, center_y + radius),
                (center_x - radius, center_y - radius),
                (center_x + radius // 2, center_y - radius // 2),
                (center_x + 2 * radius, center_y + radius),
                (center_x + radius, center_y + 2 * radius),
                (center_x - radius, center_y + 2 * radius),
            ],
            dtype=np.int32,
        )
        cv2.fillPoly(mask, [points], 255)
        cv2.circle(
            mask,
            (center_x + radius, center_y),
            radius,
            255,
            thickness=-1,
        )
    elif shape_family is ShapeFamily.HANDLED_OR_HANGING:
        half_width = width // 10 + scale
        half_height = height // 9 + scale
        body_top = center_y - half_height // 2
        cv2.rectangle(
            mask,
            (center_x - half_width, body_top),
            (center_x + half_width, center_y + half_height),
            255,
            thickness=-1,
        )
        cv2.ellipse(
            mask,
            (center_x, body_top),
            (max(3, half_width // 2), max(3, half_height)),
            0,
            180,
            360,
            255,
            thickness=2,
        )
    else:  # pragma: no cover - ShapeFamily is exhaustive; retain a clear failure.
        raise ValueError(f"unsupported shape family: {shape_family!r}")

    return mask


def _write_png(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image, _PNG_WRITE_OPTIONS):
        raise RuntimeError(f"OpenCV could not write scenario asset {path}")


def _object_bounds_and_volume(
    mask: np.ndarray,
    thickness_m: float,
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    float,
]:
    rows, columns = np.nonzero(mask)
    if rows.size == 0:
        raise ValueError("generated object mask is empty")

    shelf_width_m = 0.8
    shelf_height_m = 0.5
    height, width = mask.shape
    x_min = -0.4 + (float(columns.min()) / width) * shelf_width_m
    x_max = -0.4 + (float(columns.max() + 1) / width) * shelf_width_m
    y_min = -0.25 + (float(rows.min()) / height) * shelf_height_m
    y_max = -0.25 + (float(rows.max() + 1) / height) * shelf_height_m
    pixel_area_m2 = (shelf_width_m / width) * (shelf_height_m / height)
    volume_m3 = float(np.count_nonzero(mask)) * pixel_area_m2 * thickness_m
    z_max = _BACKGROUND_DEPTH_MM / 1000.0
    z_min = z_max - thickness_m
    bounds_min = (x_min, y_min, z_min)
    bounds_max = (x_max, y_max, z_max)
    return bounds_min, bounds_max, volume_m3


def _frame_assets(
    *,
    background_bgr: np.ndarray,
    object_mask: np.ndarray,
    object_bgr: np.ndarray,
    object_depth_mm: int,
    object_present: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rgb_bgr = background_bgr.copy()
    depth_mm = np.full(object_mask.shape, _BACKGROUND_DEPTH_MM, dtype=np.uint16)
    if object_present:
        selected = object_mask > 0
        rgb_bgr[selected] = object_bgr
        depth_mm[selected] = np.uint16(object_depth_mm)
    valid_mask = np.full(object_mask.shape, 255, dtype=np.uint8)
    occlusion_mask = np.zeros(object_mask.shape, dtype=np.uint8)
    return rgb_bgr, depth_mm, valid_mask, occlusion_mask


def _occluder_mask(object_mask: np.ndarray) -> np.ndarray:
    kernel = np.ones((7, 7), dtype=np.uint8)
    return cv2.dilate(object_mask, kernel, iterations=1)


def _track_for_mask(mask: np.ndarray, *, authorized: bool) -> TrackAnnotation:
    rows, columns = np.nonzero(mask)
    if rows.size == 0:
        raise ValueError("person mask must not be empty")
    return TrackAnnotation(
        track_id=1,
        box_xyxy=(
            float(columns.min()),
            float(rows.min()),
            float(columns.max() + 1),
            float(rows.max() + 1),
        ),
        position_m=(0.0, 0.0, 1.0),
        near_shelf=True,
        authorized=authorized,
    )


def _apply_camera_drift(
    rgb_bgr: np.ndarray,
    depth_mm: np.ndarray,
    valid_mask: np.ndarray,
    object_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    shift_x = max(2, rgb_bgr.shape[1] // 16)
    transform = np.float32(((1.0, 0.0, shift_x), (0.0, 1.0, 0.0)))
    size = (rgb_bgr.shape[1], rgb_bgr.shape[0])
    shifted_rgb = cv2.warpAffine(
        rgb_bgr,
        transform,
        size,
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )
    shifted_depth = cv2.warpAffine(
        depth_mm,
        transform,
        size,
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    shifted_valid = cv2.warpAffine(
        valid_mask,
        transform,
        size,
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    shifted_object = cv2.warpAffine(
        object_mask,
        transform,
        size,
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    return shifted_rgb, shifted_depth, shifted_valid, shifted_object


def generate_scenario(
    destination: str | Path,
    settings: ScenarioSettings,
) -> Path:
    """Generate one deterministic scenario and return its manifest path.

    A non-empty destination is rejected so regeneration cannot silently mix new
    output with stale or user-owned files.
    """

    root = Path(destination)
    if root.exists():
        if not root.is_dir() or any(root.iterdir()):
            raise FileExistsError(f"scenario output folder is not empty: {root}")
    else:
        root.mkdir(parents=True)

    rng = np.random.default_rng(settings.random_seed)
    object_mask = _object_mask(
        settings.height,
        settings.width,
        settings.shape_family,
        rng,
    )
    thickness_m = float(rng.integers(50, 91)) / 1000.0
    object_depth_mm = _BACKGROUND_DEPTH_MM - int(round(thickness_m * 1000))
    bounds_min_m, bounds_max_m, volume_m3 = _object_bounds_and_volume(
        object_mask,
        thickness_m,
    )

    background_bgr = np.zeros((settings.height, settings.width, 3), dtype=np.uint8)
    background_bgr[:, :] = np.array([48, 58, 68], dtype=np.uint8)
    texture = rng.integers(0, 8, size=background_bgr.shape[:2], dtype=np.uint8)
    background_bgr = np.clip(
        background_bgr.astype(np.uint16) + texture[:, :, None],
        0,
        255,
    ).astype(np.uint8)
    object_bgr = rng.integers(70, 231, size=3, dtype=np.uint8)

    frame_count = settings.baseline_frame_count + settings.event_frame_count
    baseline_ids = [
        f"frame-{index:04d}" for index in range(settings.baseline_frame_count)
    ]
    frames: list[FrameRecord] = []
    for index in range(frame_count):
        frame_id = f"frame-{index:04d}"
        is_baseline = index < settings.baseline_frame_count
        is_event = not is_baseline
        event_index = index - settings.baseline_frame_count
        if settings.change_type is ChangeType.REMOVAL:
            object_present = is_baseline
        elif settings.change_type is ChangeType.ADDITION:
            object_present = is_event
        else:
            object_present = True
        rgb_bgr, depth_mm, valid_mask, occlusion_mask = _frame_assets(
            background_bgr=background_bgr,
            object_mask=object_mask,
            object_bgr=object_bgr,
            object_depth_mm=object_depth_mm,
            object_present=object_present,
        )
        frame_object_mask = object_mask.copy()
        tracks: list[TrackAnnotation] = []

        if is_event and settings.condition is ScenarioCondition.PERSON_ONLY_OCCLUSION:
            occlusion_mask = _occluder_mask(object_mask)
            tracks.append(_track_for_mask(occlusion_mask, authorized=False))
        elif (
            is_event
            and settings.condition is ScenarioCondition.REMOVAL_THEN_OCCLUSION
            and event_index >= 1
        ):
            occlusion_mask = _occluder_mask(object_mask)
            tracks.append(_track_for_mask(occlusion_mask, authorized=False))
        elif is_event and settings.condition is ScenarioCondition.LIGHTING_VARIATION:
            rgb_bgr = np.clip(rgb_bgr.astype(np.uint16) + 35, 0, 255).astype(np.uint8)
        elif is_event and settings.condition is ScenarioCondition.INVALID_DEPTH:
            selected = object_mask > 0
            depth_mm[selected] = 0
            valid_mask[selected] = 0
        elif is_event and settings.condition is ScenarioCondition.CAMERA_DRIFT:
            rgb_bgr, depth_mm, valid_mask, frame_object_mask = _apply_camera_drift(
                rgb_bgr,
                depth_mm,
                valid_mask,
                frame_object_mask,
            )

        if is_event and settings.system_mode == "RESTOCK_MODE" and not tracks:
            tracks.append(_track_for_mask(frame_object_mask, authorized=True))

        rgb_path = f"rgb/{frame_id}.png"
        depth_path = f"depth/{frame_id}.png"
        valid_path = f"masks/{frame_id}-valid.png"
        occlusion_path = f"masks/{frame_id}-occlusion.png"
        object_path = f"masks/{frame_id}-object.png"
        _write_png(root / rgb_path, rgb_bgr)
        _write_png(root / depth_path, depth_mm)
        _write_png(root / valid_path, valid_mask)
        _write_png(root / occlusion_path, occlusion_mask)
        _write_png(root / object_path, frame_object_mask)

        frames.append(
            FrameRecord(
                frame_id=frame_id,
                timestamp_ns=(
                    settings.start_timestamp_ns + index * settings.frame_interval_ns
                ),
                rgb_path=rgb_path,
                depth_path=depth_path,
                valid_mask_path=valid_path,
                occlusion_mask_path=occlusion_path,
                object_mask_path=object_path,
                tracks=tracks,
            )
        )

    first_event_timestamp_ns = frames[settings.baseline_frame_count].timestamp_ns
    intrinsics = (
        (80.0, 0.0, (settings.width - 1) / 2.0),
        (0.0, 80.0, (settings.height - 1) / 2.0),
        (0.0, 0.0, 1.0),
    )
    manifest = ScenarioManifest(
        scenario_id=settings.scenario_id,
        random_seed=settings.random_seed,
        source_type=SourceType.SYNTHETIC_RGBD,
        evidence_source="synthetic",
        category=settings.category,
        held_out_category=settings.held_out_category,
        split=settings.split,
        intrinsics=intrinsics,
        camera_to_shelf=(
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ),
        shelf=ShelfConfigRecord(
            shelf_id="shelf-01",
            roi_xyxy=(0, 0, settings.width, settings.height),
            bounds_min_m=(-0.4, -0.25, 0.5),
            bounds_max_m=(0.4, 0.25, 1.5),
            voxel_size_m=0.01,
        ),
        baseline_frame_ids=baseline_ids,
        frames=frames,
        ground_truth_events=(
            [
                GroundTruthEvent(
                    change_type=settings.change_type,
                    first_seen_timestamp_ns=first_event_timestamp_ns,
                    volume_m3=volume_m3,
                    bounds_min_m=bounds_min_m,
                    bounds_max_m=bounds_max_m,
                    shape_family=settings.shape_family,
                    should_alert=settings.should_alert,
                )
            ]
            if settings.change_type is not None
            else []
        ),
        system_mode=settings.system_mode,
        notes=[
            f"generator=kyra-lightweight-{GENERATOR_VERSION}",
            f"condition={settings.condition.value}",
        ],
    )
    manifest_path = root / "scenario.json"
    write_manifest(manifest, manifest_path)
    return manifest_path
