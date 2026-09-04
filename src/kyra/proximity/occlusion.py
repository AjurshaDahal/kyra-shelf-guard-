"""Person occlusion masking for Person 3."""

from __future__ import annotations

import numpy as np

from kyra.contracts import PersonTrack


def build_person_occlusion_mask(
    tracks: tuple[PersonTrack, ...],
    frame_shape: tuple[int, int],
) -> np.ndarray:
    """Build a boolean mask covering all tracked-person bounding boxes."""

    height, width = frame_shape

    mask = np.zeros((height, width), dtype=bool)

    for track in tracks:
        x1, y1, x2, y2 = track.box_xyxy

        # Convert floating-point coordinates to pixel boundaries.
        left = max(0, int(np.floor(x1)))
        top = max(0, int(np.floor(y1)))
        right = min(width, int(np.ceil(x2)))
        bottom = min(height, int(np.ceil(y2)))

        if left >= right or top >= bottom:
            continue

        mask[top:bottom, left:right] = True

    return mask
