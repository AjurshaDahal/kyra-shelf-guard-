"""Video stitching utility."""

from pathlib import Path

import cv2
import numpy as np


def create_demo_video(frames: list[np.ndarray], output_path: str | Path, fps: float = 5.0) -> None:
    """Stitch a list of BGR frames into an MP4 video."""
    if not frames:
        return

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    h, w = frames[0].shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))

    for frame in frames:
        writer.write(frame)

    writer.release()
