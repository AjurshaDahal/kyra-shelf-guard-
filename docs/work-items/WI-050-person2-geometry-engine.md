# WI-050 — Person 2 geometry, differencing, occlusion, and volume engine

- **Owner:** P2
- **Status:** In review
- **Started:** 2026-09-06
- **Completed:** N/A
- **Requirements:** P2-REG-001 to P2-REG-003, P2-DIFF-001 to P2-DIFF-003, P2-OCC-001 to P2-OCC-003, P2-VOL-001 to P2-VOL-004, P2-STATE-001 to P2-STATE-004, P2-QA-001 to P2-QA-003
- **Integration gate:** Gate 3

## Objective

Deliver the complete Person 2 production geometry package on `main`: shelf-only registration with camera drift compensation, signed depth differencing with M3C2-EP per-pixel noise thresholding, occlusion safety and shelf visibility monitoring, 3D spatial clustering, ray-frustum metric volume estimation, sliding-window temporal persistence confirmation with restock baseline update hooks, and the `ShelfGeometryProvider` implementing the shared `GeometryProvider` protocol. This work was authored on `origin/p2/15-geometry-foundation` (commits `062da30`, `5667f93`, `8b12ce7`) and integrated onto current `main` by this pull request (issue #50); no shared contract changes.

## In scope

- `docs/PERSON2_SPEC.md` and `docs/PERSON2_IMPLEMENTATION_PLAN.md` grounded in scientific literature (Milella et al. 2020; Lague et al. 2013 and Winiwarter et al. 2021 M3C2-EP; Fehr et al. TSDF; Amazon Go patent US 9,530,060; Liciotti et al. 2015; Habibiroudkenar et al. 2024 DynaHull).
- `src/kyra/geometry/points.py`: 3D unprojection, projection, and transformation utilities.
- `src/kyra/geometry/registration.py`: Kabsch-SVD rigid alignment of valid fixed shelf pixels against baseline geometry; drift envelope (15 mm / 1.0°); explicit rejection reasons `drift_envelope_exceeded`, `registration_residual_exceeded` (default 2 cm), `insufficient_fixed_geometry_points`; corrected depth generation.
- `src/kyra/differencing/signed_diff.py`: signed depth difference with threshold `max(removal_floor_m, 3 * sigma_baseline)`; classes `REMOVAL`, `ADDITION`, `NO_CHANGE`, `UNKNOWN`.
- `src/kyra/occlusion/safety.py`: shelf visibility ratio, person-mask integration, occlusion flag below 70% visible shelf fraction.
- `src/kyra/geometry/clustering.py`: morphological 2D cleaning, connected components, 3D back-projection to camera and shelf coordinates.
- `src/kyra/geometry/volume.py`: ray frustum volume integration, 1 cm occupancy-grid bounding-prism cross-check, confidence, volume threshold `>= 5e-5 m^3`.
- `src/kyra/geometry/temporal_state.py`: change in `>= 5` of latest 7 observations, duration `>= 0.5 s`, deduplication, baseline update hook after 2.0 s of stable restocking.
- `src/kyra/geometry/provider.py`: production `ShelfGeometryProvider` conforming to the shared `GeometryProvider` protocol.
- Five test suites: `tests/test_geometry_drift.py`, `tests/test_geometry_diff.py`, `tests/test_geometry_visibility.py`, `tests/test_geometry_cluster.py`, `tests/test_geometry_adapter.py` (28 tests).
- `docs/PERSON2_TECHNICAL_REPORT.md` and the owner documentation companions listed below.

## Out of scope

- Person tracking, occlusion person masks, and alert rules (Person 3).
- Input replay reader and opening baseline calibration builder (Person 1).
- Real (non-mock) end-to-end pipeline execution and final CLI/evaluation (Person 4).
- Modifying shared contracts (`contracts.py`, `manifest.py`, `adapters.py`).
- Gate 3 completion evidence on the frozen golden pack; this merge alone does not close Gate 3.

## Inputs, outputs, and contracts

- Consumes `FramePacket` (C-001; `depth_m` float32 metres, `valid_depth_mask`, 3x3 `intrinsics`), `BaselineArtifact` (C-002; baseline depth, fixed-geometry mask, occupancy grid, noise sigma grid), `ShelfConfig` (C-007 v1 five-field boundary), and Person 3 occlusion masks.
- Produces deterministic `VolumeChangeEvent` (C-003) objects with metric volume, 3D centroid, 3D bounds, confidence, and evidence frame IDs via `ShelfGeometryProvider`.
- Unknown, zero, NaN, masked, or occluded depth is classified `UNKNOWN`, never removal evidence.

## Implementation summary

The package connects the five core stages of metric 3D change detection: (1) registration verifies rigid alignment against baseline fixed structure within the 15 mm / 1.0° envelope; (2) occlusion safety flags frames with less than 70% visible shelf area; (3) differencing computes per-pixel signed depth delta against baseline with M3C2-EP 3-sigma noise suppression; (4) clustering groups candidate pixels and computes metric volume in shelf coordinates via frustum ray integration with occupancy-grid cross-check; (5) temporal state confirms changes persisting across 5 of 7 frames for at least 0.5 s and emits deduplicated `VolumeChangeEvent` objects.

## Documentation impact

- Created `docs/PERSON2_SPEC.md`, `docs/PERSON2_IMPLEMENTATION_PLAN.md`, and `docs/PERSON2_TECHNICAL_REPORT.md`.
- Updated `docs/status/PERSON2.md` from "Not started" to "In review" with verified evidence.
- Updated `docs/agents/README.md` routing table with Person 2 specification/plan links.
- Updated `CHANGELOG.md` with the new modules and capabilities.
- Updated `docs/PROJECT_STATUS.md` Person 2 workstream row.
- Created this durable work-item record (replaces the pre-issue local records WI-015/WI-016 authored on `origin/p2/15-geometry-foundation`, which were never merged).

## Verification

Author evidence (Linux, Python 3.13, original branch base; recorded 2026-09-06):

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Linux, Python 3.13 / .venv | `python -m pytest tests/test_geometry_drift.py -v` | Passed | 9 passed in 0.11s; CPU-only deterministic |
| Linux, Python 3.13 / .venv | `python -m pytest tests/test_geometry*.py -v` | Passed | 28 passed in 0.28s |
| Linux, Python 3.13 / .venv | `python -m pytest` | Passed | 141 passed in 0.86s on the original branch base |
| Linux, Python 3.13 / .venv | `ruff check .` | Passed | All checks passed |
| Linux, Python 3.13 / .venv | `python -m compileall -q src tests scripts` | Passed | Exit code 0 |
| Linux, benchmark | `test_shelf_geometry_provider_latency_budget` | Passed | p95 latency = 1.25 ms (< 40 ms budget) |

Integration-tree evidence (Windows, Python 3.12.7, branch `p2/50-integrate-geometry-engine` based on current `origin/main`; recorded 2026-09-07): see `docs/status/PERSON2.md`.

## Risks, limitations, and failures

- Core is pure CPU-first NumPy/OpenCV; Open3D point-to-plane ICP remains an optional integration path for complex non-planar shelf geometry.
- Registration and change tests use synthetic fixed-shelf planes and controlled displacements; real-sensor OCID sequences and the frozen golden pack are evaluated at Gate 3, which remains open.
- The hanging-overhang void-column bias (known from Person 1 acceptance, WI-021) belongs to this occlusion-safe geometry scope and is not claimed as resolved by these tests.
- Integration-tree full-suite and governance results are recorded in `docs/status/PERSON2.md` only after the checks actually run on this branch.

## Handoff

- Reviewer/owner: Person 4 delegate for governance and shared-surface scrutiny; original author credited (co-author on the squash merge).
- Next exact actions after merge: (1) run the Person 2 acceptance evidence against the frozen golden pack (G01-G10) and record it for Gate 3; (2) wire `ShelfGeometryProvider` into the real vertical pipeline at Gate 5.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/50
- Pull request: pending
- Commit: pending
