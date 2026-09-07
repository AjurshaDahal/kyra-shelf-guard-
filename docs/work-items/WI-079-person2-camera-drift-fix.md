# WI-079: Person 2 Camera Drift Fix (Issue #79)

**Owner:** Person 2
**Status:** Complete
**Date:** 2026-09-07

## Scope
Fix the critical bug where horizontal camera drift produces a false REMOVAL event (Issue #79) that blocks Gates 3 and 5.

## Accomplished
- Diagnosed root cause: Kabsch SVD registration is blind to horizontal pixel shifts on a flat planar shelf wall because unprojection from identical pixel coordinates produces identical 3D points. The shift creates a paired pattern of false removal and addition.
- Implemented paired removal+addition drift detection in `src/kyra/geometry/provider.py`. When both `removal_pixel_count` and `addition_pixel_count` are positive and comparable in magnitude (ratio >= 0.3), the change is suppressed as a drift artifact (`UNKNOWN`).
- Updated `tests/test_vertical_pipeline.py` to assert the camera drift scenario correctly produces no false events.
- All 216 tests passed.

## Evidence
- 216/216 tests pass, including `test_camera_drift_does_not_produce_false_removal`.

