# WI-081: Video Demo Command

**Owner:** Person 4
**Status:** Complete
**Date:** 2026-09-07

## Scope
Implement `kyra demo` CLI subcommand and video visualization pipeline to generate an annotated MP4 video of the end-to-end inference running on a synthetic or real scenario.

## Accomplished
- Added `src/kyra/viz/annotate.py` to annotate RGB and depth frames with removal (red)/addition (blue) overlays, person tracking boxes, and a status bar.
- Added `src/kyra/viz/video.py` to stitch the annotated frames into an MP4 file using OpenCV `VideoWriter`.
- Added `src/kyra/demo.py` orchestration script to intercept frame-by-frame geometry output (masks) and pipe to the annotator.
- Added `demo` subcommand to `kyra.cli`.
- `test_demo.py` verifies the video file is generated successfully.
- All 216 tests pass.

## Evidence
- `tests/test_demo.py` passes.
- Full test suite 216/216 passes.

