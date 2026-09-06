"""Known-volume baseline acceptance: synthetic objects at least 0.5 litres within 10%.

Every accepted case is a floor-sitting object with a flat top: the baseline
estimator integrates the pixel frustum from the object surface down to the
shelf plane, so its model error for such objects is a known function of the
thickness-to-distance ratio.  Cases are chosen so the exact-model error stays
below 10%.  A hanging-plate guard case proves the suite is not vacuous: the
estimator intentionally includes the void column under a hanging object, so
that case is expected to exceed the bound and is documented as Person 2
occlusion-safe geometry scope.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pytest

from kyra.baseline import BaselineBuilder
from kyra.contracts import FramePacket, ShelfConfig

PLANE_DEPTH_M = 1.0
MAX_RELATIVE_ERROR = 0.10


def _raster(
    footprint: np.ndarray, top_depth_m: float, height: int = 32, width: int = 32
) -> np.ndarray:
    depth = np.full((height, width), PLANE_DEPTH_M, dtype=np.float32)
    depth[footprint] = top_depth_m
    return depth


def _box(
    x1: int, y1: int, x2: int, y2: int, height: int = 32, width: int = 32
) -> np.ndarray:
    mask = np.zeros((height, width), dtype=bool)
    mask[y1:y2, x1:x2] = True
    return mask


def _disc(cx: float, cy: float, radius: float, height: int = 32, width: int = 32) -> np.ndarray:
    ys, xs = np.mgrid[0:height, 0:width]
    return (xs - cx) ** 2 + (ys - cy) ** 2 <= radius**2


def _l_shape(height: int = 32, width: int = 32) -> np.ndarray:
    mask = np.zeros((height, width), dtype=bool)
    mask[6:14, 6:26] = True
    mask[6:26, 6:14] = True
    return mask


@dataclass(frozen=True, slots=True)
class VolumeCase:
    name: str
    footprint: np.ndarray
    top_depth_m: float
    expected_volume_m3: float
    seed: int


def _volume_for(pixel_count: int, top_depth_m: float, fx: float, fy: float) -> float:
    footprint_area_m2 = pixel_count * (top_depth_m / fx) * (top_depth_m / fy)
    thickness_m = PLANE_DEPTH_M - top_depth_m
    return footprint_area_m2 * thickness_m


def _cases(fx: float, fy: float) -> list[VolumeCase]:
    return [
        VolumeCase(
            "box-12x12-center-5cm",
            _box(10, 10, 22, 22),
            0.95,
            _volume_for(144, 0.95, fx, fy),
            seed=101,
        ),
        VolumeCase(
            "box-14x14-offset-3cm",
            _box(12, 6, 26, 20),
            0.97,
            _volume_for(196, 0.97, fx, fy),
            seed=102,
        ),
        VolumeCase(
            "box-16x10-offset-6cm",
            _box(4, 12, 20, 22),
            0.94,
            _volume_for(160, 0.94, fx, fy),
            seed=103,
        ),
        VolumeCase(
            "cylinder-r7-center-5cm",
            _disc(15.5, 15.5, 7.0),
            0.95,
            _volume_for(156, 0.95, fx, fy),
            seed=104,
        ),
        VolumeCase(
            "cylinder-r9-offset-3cm",
            _disc(22.0, 9.0, 9.0),
            0.97,
            _volume_for(256, 0.97, fx, fy),
            seed=105,
        ),
        VolumeCase(
            "irregular-L-arms-8px-5cm",
            _l_shape(),
            0.95,
            _volume_for(256, 0.95, fx, fy),
            seed=106,
        ),
        VolumeCase(
            "box-18x18-center-6cm",
            _box(7, 7, 25, 25),
            0.94,
            _volume_for(324, 0.94, fx, fy),
            seed=107,
        ),
    ]


def _baseline_for(
    case: VolumeCase,
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> object:
    depth = _raster(case.footprint, case.top_depth_m)
    frames = [
        make_frame_packet(
            frame_id=f"calibration-{index:04d}",
            timestamp_ns=index * 1_000_000_000,
            depth_m=depth.copy(),
        )
        for index in range(30)
    ]
    return BaselineBuilder().fit(frames, shelf_config)


@pytest.mark.parametrize(
    "case",
    _cases(fx=100.0, fy=100.0),
    ids=lambda case: case.name,
)
def test_known_volume_within_10_percent(
    case: VolumeCase,
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    artifact = _baseline_for(case, make_frame_packet, shelf_config)

    assert len(artifact.portable_components) == 1, (
        f"seed={case.seed}: expected exactly one portable component, "
        f"got {len(artifact.portable_components)}"
    )
    measured = artifact.portable_components[0].volume_m3
    relative_error = abs(measured - case.expected_volume_m3) / case.expected_volume_m3
    assert relative_error <= MAX_RELATIVE_ERROR, (
        f"seed={case.seed}: expected {case.expected_volume_m3:.6f} m3, "
        f"measured {measured:.6f} m3, relative error {relative_error:.3%} "
        f"exceeds {MAX_RELATIVE_ERROR:.0%}"
    )


def test_hanging_plate_bias_is_detected_and_reported(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    """Guard: hanging objects inflate volume via the void column under them.

    A 5 mm plate suspended at 0.95 m has a true volume of about 0.12 litres,
    but the baseline estimator integrates the frustum down to the 1.0 m plane,
    so the reported volume is an order of magnitude larger.  Person 2's
    occlusion-safe volume path owns this case; the baseline must never
    silently accept it as a within-limit volume.
    """
    top_depth_m = 0.95
    footprint = _box(8, 8, 24, 24)
    plate_thickness_m = 0.005
    footprint_area_m2 = 256 * (top_depth_m / 100.0) ** 2
    true_volume = footprint_area_m2 * plate_thickness_m
    artifact = _baseline_for(
        VolumeCase("hanging-plate", footprint, top_depth_m, true_volume, seed=201),
        make_frame_packet,
        shelf_config,
    )

    assert len(artifact.portable_components) == 1
    measured = artifact.portable_components[0].volume_m3
    relative_error = abs(measured - true_volume) / true_volume
    assert relative_error > MAX_RELATIVE_ERROR, (
        "hanging-plate bias guard: expected the void-column overestimate to "
        f"exceed {MAX_RELATIVE_ERROR:.0%}, got {relative_error:.3%}"
    )