"""Frame annotation for the video demo."""

import cv2
import numpy as np

from kyra.contracts import AlertEvent, FramePacket, ShelfConfig, VolumeChangeEvent
from kyra.differencing.signed_diff import SignedDifferenceResult


def colorize_depth(
    depth_m: np.ndarray, valid_mask: np.ndarray, min_d: float = 0.5, max_d: float = 2.0
) -> np.ndarray:
    """Convert float depth to 8-bit BGR colormap."""
    norm = np.clip((depth_m - min_d) / (max_d - min_d), 0.0, 1.0)
    gray = (norm * 255).astype(np.uint8)
    colorized = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    colorized[~valid_mask] = (0, 0, 0)
    return colorized


def annotate_frame(
    frame: FramePacket,
    shelf_config: ShelfConfig,
    diff_result: SignedDifferenceResult | None,
    events: list[VolumeChangeEvent],
    alerts: list[AlertEvent],
    person_mask: np.ndarray | None = None,
    track_boxes: list[tuple[int, tuple[float, float, float, float], bool]] | None = None,
) -> np.ndarray:
    """Create a composite 2-pane view with annotations."""
    rgb = frame.rgb.copy()

    depth_vis = colorize_depth(frame.depth_m, frame.valid_depth_mask)

    x1, y1, x2, y2 = shelf_config.roi_xyxy
    cv2.rectangle(rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.rectangle(depth_vis, (x1, y1), (x2, y2), (0, 255, 0), 2)

    if diff_result is not None:
        depth_vis[diff_result.removal_candidate_mask] = (0, 0, 255)
        depth_vis[diff_result.addition_candidate_mask] = (255, 0, 0)

    if person_mask is not None:
        depth_vis[person_mask.astype(bool)] = (255, 0, 255)

    if track_boxes:
        for track_id, box, authorized in track_boxes:
            bx1, by1, bx2, by2 = map(int, box)
            color = (255, 255, 0) if authorized else (0, 165, 255)
            cv2.rectangle(rgb, (bx1, by1), (bx2, by2), color, 2)
            cv2.putText(
                rgb, f"ID:{track_id}", (bx1, by1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
            )

    h, w = rgb.shape[:2]
    composite = np.zeros((h + 80, w * 2, 3), dtype=np.uint8)

    cv2.rectangle(composite, (0, 0), (w * 2, 40), (40, 40, 40), -1)
    cv2.putText(
        composite, "KYRA SHELF GUARD", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
    )
    cv2.putText(
        composite,
        f"Frame: {frame.frame_id}",
        (w * 2 - 200, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (200, 200, 200),
        1,
    )

    composite[40 : 40 + h, 0:w] = rgb
    composite[40 : 40 + h, w : w * 2] = depth_vis

    cv2.putText(
        composite, "RGB + Tracking", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
    )
    cv2.putText(
        composite,
        "Depth + Change Detection",
        (w + 10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    cv2.rectangle(composite, (0, h + 40), (w * 2, h + 80), (30, 30, 30), -1)

    status_text = "STATUS: NOMINAL"
    status_color = (0, 255, 0)

    if alerts:
        status_text = f"ALERT: SUSPICIOUS REMOVAL (Vol: {alerts[-1].missing_volume_m3 * 1000:.1f}L)"
        status_color = (0, 0, 255)
    elif events:
        ev = events[-1]
        vol = ev.missing_volume_m3 * 1000 if ev.missing_volume_m3 else 0.0
        status_text = f"EVENT: {ev.change_type.name} (Vol: {vol:.1f}L)"
        status_color = (0, 165, 255)

    cv2.putText(
        composite, status_text, (10, h + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2
    )

    return composite
