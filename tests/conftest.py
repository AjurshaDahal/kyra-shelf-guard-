from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import cv2
import numpy as np
import pytest

from kyra.contracts import FramePacket, ShelfConfig, SourceType
from kyra.manifest import (
    FrameRecord,
    ScenarioManifest,
    ShelfConfigRecord,
    TrackAnnotation,
    write_manifest,
)


@pytest.fixture
def intrinsics() -> np.ndarray:
    return np.array(
        [[100.0, 0.0, 15.5], [0.0, 100.0, 15.5], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )


@pytest.fixture
def camera_to_shelf() -> np.ndarray:
    return np.eye(4, dtype=np.float64)


@pytest.fixture
def shelf_config() -> ShelfConfig:
    return ShelfConfig(
        shelf_id="shelf-01",
        roi_xyxy=(0, 0, 32, 32),
        bounds_min_m=(-0.2, -0.2, 0.5),
        bounds_max_m=(0.2, 0.2, 1.2),
    )


@pytest.fixture
def make_frame_packet(
    intrinsics: np.ndarray,
    camera_to_shelf: np.ndarray,
) -> Callable[..., FramePacket]:
    def factory(
        *,
        frame_id: str = "frame-0001",
        timestamp_ns: int = 1_000_000_000,
        depth_m: np.ndarray | None = None,
        valid_depth_mask: np.ndarray | None = None,
        source_type: SourceType = SourceType.SYNTHETIC_RGBD,
    ) -> FramePacket:
        depth = (
            np.ones((32, 32), dtype=np.float32)
            if depth_m is None
            else np.asarray(depth_m)
        )
        valid = (
            np.ones(depth.shape, dtype=bool)
            if valid_depth_mask is None
            else np.asarray(valid_depth_mask)
        )
        return FramePacket(
            frame_id=frame_id,
            timestamp_ns=timestamp_ns,
            rgb=np.zeros((*depth.shape, 3), dtype=np.uint8),
            depth_m=depth,
            valid_depth_mask=valid,
            intrinsics=intrinsics.copy(),
            camera_to_shelf=camera_to_shelf.copy(),
            source_type=source_type,
        )

    return factory


@pytest.fixture
def make_manifest() -> Callable[..., ScenarioManifest]:
    def factory(
        *,
        frames: list[FrameRecord] | None = None,
        baseline_frame_ids: list[str] | None = None,
        intrinsics: tuple[tuple[float, float, float], ...] | None = None,
    ) -> ScenarioManifest:
        records = frames or [
            FrameRecord(
                frame_id="frame-0001",
                timestamp_ns=1_000_000_000,
                rgb_path="rgb/frame-0001.png",
                depth_path="depth/frame-0001.png",
            )
        ]
        return ScenarioManifest(
            scenario_id="scenario-001",
            random_seed=42,
            source_type=SourceType.SYNTHETIC_RGBD,
            evidence_source="synthetic",
            category="thin-tray",
            intrinsics=intrinsics
            or ((100.0, 0.0, 2.0), (0.0, 100.0, 1.5), (0.0, 0.0, 1.0)),
            camera_to_shelf=(
                (1.0, 0.0, 0.0, 0.0),
                (0.0, 1.0, 0.0, 0.0),
                (0.0, 0.0, 1.0, 0.0),
                (0.0, 0.0, 0.0, 1.0),
            ),
            shelf=ShelfConfigRecord(
                shelf_id="shelf-01",
                roi_xyxy=(0, 0, 5, 4),
                bounds_min_m=(-0.2, -0.2, 0.5),
                bounds_max_m=(0.2, 0.2, 1.2),
            ),
            baseline_frame_ids=baseline_frame_ids or [records[0].frame_id],
            frames=records,
        )

    return factory


def _write_png(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f"OpenCV could not write test image {path}")


@pytest.fixture
def scenario_path(tmp_path: Path, make_manifest: Callable[..., ScenarioManifest]) -> Path:
    root = tmp_path / "scenario"
    frames: list[FrameRecord] = []
    for index in (1, 2):
        frame_id = f"frame-{index:04d}"
        rgb_bgr = np.zeros((4, 5, 3), dtype=np.uint8)
        rgb_bgr[:, :] = (5 * index, 10 * index, 20 * index)
        depth_mm = np.full((4, 5), 1000 + 100 * (index - 1), dtype=np.uint16)
        valid_mask = np.full((4, 5), 255, dtype=np.uint8)
        occlusion_mask = np.zeros((4, 5), dtype=np.uint8)
        if index == 1:
            depth_mm[0, 1] = 0
            valid_mask[0, 2] = 0
            occlusion_mask[1, 1] = 255

        rgb_path = f"rgb/{frame_id}.png"
        depth_path = f"depth/{frame_id}.png"
        valid_path = f"masks/{frame_id}-valid.png"
        occlusion_path = f"masks/{frame_id}-occlusion.png"
        _write_png(root / rgb_path, rgb_bgr)
        _write_png(root / depth_path, depth_mm)
        _write_png(root / valid_path, valid_mask)
        _write_png(root / occlusion_path, occlusion_mask)
        frames.append(
            FrameRecord(
                frame_id=frame_id,
                timestamp_ns=index * 1_000_000_000,
                rgb_path=rgb_path,
                depth_path=depth_path,
                valid_mask_path=valid_path,
                occlusion_mask_path=occlusion_path,
                tracks=(
                    [
                        TrackAnnotation(
                            track_id=7,
                            box_xyxy=(1.0, 0.0, 4.0, 3.0),
                            position_m=(0.1, 0.0, 0.8),
                            near_shelf=True,
                            authorized=False,
                        )
                    ]
                    if index == 2
                    else []
                ),
            )
        )

    manifest = make_manifest(frames=frames, baseline_frame_ids=["frame-0001"])
    manifest_path = root / "scenario.json"
    write_manifest(manifest, manifest_path)
    return manifest_path
