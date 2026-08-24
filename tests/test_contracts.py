from __future__ import annotations

import re
from collections.abc import Callable

import numpy as np
import pytest

from kyra.contracts import BaselineArtifact, FramePacket, ShelfConfig, SourceType


def _packet(**overrides: object) -> FramePacket:
    values: dict[str, object] = {
        "frame_id": "frame-0001",
        "timestamp_ns": 1,
        "rgb": np.zeros((2, 3, 3), dtype=np.uint8),
        "depth_m": np.ones((2, 3), dtype=np.float64),
        "valid_depth_mask": np.ones((2, 3), dtype=np.uint8),
        "intrinsics": np.eye(3),
        "camera_to_shelf": np.eye(4),
        "source_type": SourceType.SYNTHETIC_RGBD,
    }
    values.update(overrides)
    return FramePacket(**values)  # type: ignore[arg-type]


def test_frame_packet_normalizes_types_and_keeps_unknown_depth_invalid() -> None:
    depth = np.array([[1.0, 0.0, np.nan], [2.0, -1.0, np.inf]])

    packet = _packet(depth_m=depth)

    assert packet.rgb.dtype == np.uint8
    assert packet.depth_m.dtype == np.float32
    assert packet.valid_depth_mask.dtype == bool
    np.testing.assert_array_equal(
        packet.valid_depth_mask,
        np.array([[True, False, False], [True, False, False]]),
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("rgb", np.zeros((3, 3, 3)), "RGB and depth dimensions differ"),
        ("valid_depth_mask", np.ones((3, 3)), "valid-depth mask"),
        ("intrinsics", np.eye(4), "expected shape (3, 3)"),
        ("camera_to_shelf", np.eye(3), "expected shape (4, 4)"),
    ],
)
def test_frame_packet_rejects_invalid_shapes(
    field: str,
    value: np.ndarray,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=re.escape(message)):
        _packet(**{field: value})


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"roi_xyxy": (1, 1, 1, 2)}, "positive width and height"),
        ({"bounds_max_m": (0.0, 1.0, 1.0)}, "positive extent"),
        ({"voxel_size_m": 0.0}, "voxel size must be positive"),
    ],
)
def test_shelf_config_rejects_invalid_geometry(
    changes: dict[str, object],
    message: str,
) -> None:
    values: dict[str, object] = {
        "shelf_id": "shelf-01",
        "roi_xyxy": (0, 0, 2, 2),
        "bounds_min_m": (0.0, 0.0, 0.0),
        "bounds_max_m": (1.0, 1.0, 1.0),
    }
    values.update(changes)
    with pytest.raises(ValueError, match=message):
        ShelfConfig(**values)  # type: ignore[arg-type]


def test_baseline_artifact_rejects_mismatched_image_arrays(
    make_frame_packet: Callable[..., FramePacket],
) -> None:
    packet = make_frame_packet(depth_m=np.ones((2, 2), dtype=np.float32))

    with pytest.raises(ValueError, match="identical dimensions"):
        BaselineArtifact(
            shelf_id="shelf-01",
            roi_xyxy=(0, 0, 2, 2),
            bounds_min_m=(0.0, 0.0, 0.0),
            bounds_max_m=(1.0, 1.0, 1.0),
            baseline_depth_m=packet.depth_m,
            valid_mask=packet.valid_depth_mask,
            fixed_geometry_mask=np.ones((1, 2), dtype=bool),
            portable_components=(),
            occupancy_grid=np.zeros((1, 1, 1), dtype=np.uint8),
            noise_sigma_m=np.zeros((2, 2), dtype=np.float32),
            intrinsics=packet.intrinsics,
            camera_to_shelf=packet.camera_to_shelf,
            calibration_checksum="checksum",
        )
