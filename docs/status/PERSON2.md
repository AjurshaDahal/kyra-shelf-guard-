# Person 2 Status — Geometry and Change

- **Status:** In progress
- **Last updated:** 2026-09-07

## Implemented

- Established formal Person 2 Specification (`docs/PERSON2_SPEC.md`) and Phased Implementation Plan (`docs/PERSON2_IMPLEMENTATION_PLAN.md`) grounded in scientific literature: Milella et al. (2020) retail on-shelf availability, Lague et al. (2013) and Winiwarter et al. (2021) M3C2-EP noise propagation, and Fehr et al. TSDF occlusion distinction.
- Implemented Milestone 1 (P2-01): Shelf-only registration and camera drift check (`src/kyra/geometry/registration.py` and `src/kyra/geometry/points.py`):
  - 3D rigid transform estimation via Kabsch SVD algorithm.
  - Camera drift envelope check (corrects drift up to 15 mm and 1.0°).
  - Explicit rejection for drift envelope exceedance (`rejection_reason="drift_envelope_exceeded"`).
  - Explicit rejection for residual > `registration_reject_m` (default 2 cm; `rejection_reason="registration_residual_exceeded"`).
  - Explicit rejection when valid fixed shelf points are insufficient (`rejection_reason="insufficient_fixed_geometry_points"`).
  - Corrected depth generation for downstream stages.
- Implemented Milestone 2 (P2-02): Signed depth differencing and occlusion safety:
  - `src/kyra/differencing/signed_diff.py`: Per-pixel M3C2-EP $3\sigma$ noise thresholding $\max(\text{removal\_floor\_m}, 3 \times \sigma_{\text{baseline}})$, surface classification (`REMOVAL`, `ADDITION`, `NO_CHANGE`, `UNKNOWN`).
  - `src/kyra/occlusion/safety.py`: Shelf visibility ratio calculation, person mask integration, and occlusion flag when visible shelf fraction $< 0.70$.
- Implemented Milestone 3 (P2-03): 3D clustering and metric volume estimation:
  - `src/kyra/geometry/clustering.py`: Morphological 2D cleaning, connected component labeling, and 3D back-projection into camera and shelf coordinates.
  - `src/kyra/geometry/volume.py`: Frustum ray volume integration, 1 cm occupancy grid bounding prism cross-check, confidence calculation, and volume thresholding ($\ge 5 \times 10^{-5}\,\text{m}^3$).
- Implemented Milestone 4 (P2-04): Temporal state engine and production provider:
  - `src/kyra/geometry/temporal_state.py`: Sliding-window temporal tracker requiring change in $\ge 5$ of latest 7 observations, duration $\ge 0.5$ s, and event deduplication; baseline update hook after 2.0 s of stable restocking.
  - `src/kyra/geometry/provider.py`: Production `ShelfGeometryProvider` implementing the `GeometryProvider` protocol in `src/kyra/adapters.py`.
- Added comprehensive unit and acceptance tests across 5 test suites (`tests/test_geometry_*.py`, 28 tests).

## Active

- All four milestones (P2-01..P2-04) implemented and merged to `main` via pull request #51.
- **Issue #79 (Camera Drift)** fixed in `src/kyra/geometry/provider.py` by adding paired removal+addition drift detection. Work-item record: `docs/work-items/WI-079-person2-camera-drift-fix.md`.
- Gate 3 acceptance evidence completed and blocking regression (#79) resolved.

## Blocked or pending

- None. Issue #79 camera drift blocker is resolved.

## Next

- Hand off Gate 3 evidence to Person 4 for review and closure of Gate 3.
- Coordinate with Person 4 to wire `ShelfGeometryProvider` into the main vertical pipeline at Gate 5.

## Evidence

- `tests/test_vertical_pipeline.py`: `test_camera_drift_does_not_produce_false_removal` passes, confirming Issue #79 is fixed.
- Full repository test suite: 216 passed in ~13s (2026-09-07).
- Lint and type checks: `python -m ruff check .` passed; `python -m compileall -q src tests scripts` passed.
- Consistency checks: `python scripts/check_repo_consistency.py` passed; `python scripts/check_change_impact.py --base origin/main` passed.
- Real-sensor OCID sequence trial: evaluated 2 frames on converted OCID sequence, 29 removal pixels detected in unstacked frame with zero registration errors.
