"""Occlusion safety and shelf visibility monitoring for Person 2."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from kyra.contracts import BaselineArtifact, FramePacket, ShelfConfig


@dataclass(slots=True, frozen=True)
class OcclusionSafetyResult:
    """Result of shelf visibility and occlusion assessment."""

    visible_shelf_fraction: float
    is_occluded: bool
    person_present: bool
    unoccluded_mask: np.ndarray
    occluded_mask: np.ndarray
    total_roi_pixels: int
    unoccluded_pixel_count: int
    person_pixel_count: int


def evaluate_occlusion_safety(
    current_frame: FramePacket,
    baseline: BaselineArtifact,
    shelf_config: ShelfConfig,
    *,
    person_occlusion_mask: np.ndarray | None = None,
) -> OcclusionSafetyResult:
    """Evaluate visibility and occlusion status over the configured shelf ROI.

    A shelf frame is flagged as occluded if:
        visible_shelf_fraction < shelf_config.minimum_visible_fraction (default 0.70)
    or if an unverified person occludes critical shelf space.

    Args:
        current_frame: Incoming observation frame.
        baseline: BaselineArtifact.
        shelf_config: ShelfConfig containing ROI bounds and visibility threshold.
        person_occlusion_mask: Optional boolean mask of person bodies/hands.

    Returns:
        OcclusionSafetyResult indicating visible fraction and occlusion flags.
    """
    h, w = current_frame.depth_m.shape
    x1, y1, x2, y2 = shelf_config.roi_xyxy

    roi_mask = np.zeros((h, w), dtype=bool)
    roi_mask[max(0, y1) : min(h, y2), max(0, x1) : min(w, x2)] = True
    total_roi_pixels = int(np.count_nonzero(roi_mask))

    if total_roi_pixels == 0:
        return OcclusionSafetyResult(
            visible_shelf_fraction=0.0,
            is_occluded=True,
            person_present=False,
            unoccluded_mask=np.zeros((h, w), dtype=bool),
            occluded_mask=np.zeros((h, w), dtype=bool),
            total_roi_pixels=0,
            unoccluded_pixel_count=0,
            person_pixel_count=0,
        )

    # Valid depth in current frame
    valid_depth = (
        current_frame.valid_depth_mask
        & np.isfinite(current_frame.depth_m)
        & (current_frame.depth_m > 0)
    )

    person_mask = (
        np.zeros((h, w), dtype=bool)
        if person_occlusion_mask is None
        else person_occlusion_mask.astype(bool)
    )

    person_pixel_count = int(np.count_nonzero(roi_mask & person_mask))
    person_present = person_pixel_count > 0

    # Unoccluded valid shelf pixels
    unoccluded_mask = roi_mask & valid_depth & ~person_mask
    unoccluded_pixel_count = int(np.count_nonzero(unoccluded_mask))

    occluded_mask = roi_mask & ~unoccluded_mask

    visible_shelf_fraction = float(unoccluded_pixel_count / total_roi_pixels)
    is_occluded = visible_shelf_fraction < shelf_config.minimum_visible_fraction

    return OcclusionSafetyResult(
        visible_shelf_fraction=visible_shelf_fraction,
        is_occluded=is_occluded,
        person_present=person_present,
        unoccluded_mask=unoccluded_mask,
        occluded_mask=occluded_mask,
        total_roi_pixels=total_roi_pixels,
        unoccluded_pixel_count=unoccluded_pixel_count,
        person_pixel_count=person_pixel_count,
    )
