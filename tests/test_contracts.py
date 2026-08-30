from __future__ import annotations

import re
from collections.abc import Callable

import numpy as np
import pytest

from kyra.contracts import (
    SHELF_CONFIG_C007_FIELDS,
    BaselineArtifact,
    FramePacket,
    ShelfConfig,
    SourceType,
)
from kyra.manifest import ShelfConfigRecord


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


def test_c007_v1_boundary_is_exactly_five_fields() -> None:
    assert SHELF_CONFIG_C007_FIELDS == (
        "shelf_id",
        "roi_xyxy",
        "bounds_min_m",
        "bounds_max_m",
        "voxel_size_m",
    )
    for excluded in (
        "random_seed",
        "system_mode",
        "intrinsics",
        "camera_to_shelf",
        "portable_max_volume_m3",
        "removal_floor_m",
        "registration_reject_m",
        "minimum_visible_fraction",
        "minimum_alert_volume_m3",
        "proximity_distance_m",
    ):
        assert excluded not in SHELF_CONFIG_C007_FIELDS


def test_runtime_and_persisted_shelf_boundary_match() -> None:
    shelf = ShelfConfig(
        shelf_id="shelf-01",
        roi_xyxy=(0, 0, 64, 48),
        bounds_min_m=(-0.2, -0.2, 0.5),
        bounds_max_m=(0.2, 0.2, 1.2),
        voxel_size_m=0.02,
    )
    record = ShelfConfigRecord(
        **{field: getattr(shelf, field) for field in SHELF_CONFIG_C007_FIELDS}
    )

    assert shelf.c007_fields == record.c007_fields == SHELF_CONFIG_C007_FIELDS
    assert set(record.model_dump(mode="json").keys()) == set(SHELF_CONFIG_C007_FIELDS)
    assert shelf.c007_values == record.c007_values == {
        "shelf_id": "shelf-01",
        "roi_xyxy": (0, 0, 64, 48),
        "bounds_min_m": (-0.2, -0.2, 0.5),
        "bounds_max_m": (0.2, 0.2, 1.2),
        "voxel_size_m": 0.02,
    }


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
