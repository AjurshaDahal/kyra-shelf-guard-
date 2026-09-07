# WI-067 — Person 2 Gate 3 geometry acceptance evidence and verification runner

- **Owner:** P2
- **Status:** Complete
- **Started:** 2026-09-07
- **Completed:** 2026-09-07
- **Requirements:** P2-REG-001..003, P2-DIFF-001..003, P2-OCC-001..003, P2-VOL-001..004, P2-STATE-001..004, P2-QA-001..003
- **Integration gate:** Gate 3 (geometry evidence)

## Objective

Deliver the complete Integration Gate 3 evidence suite and single acceptance runner (`scripts/verify_person2.py`) for the Person 2 shelf geometry, differencing, occlusion, volume estimation, and temporal state tracking package. Formally record all replay results, known-volume accuracy on $\ge 0.5$ L fixtures, failure-path safety checks, deterministic `VolumeChangeEvent` serialization hashes, and real-sensor OCID sequence evaluation in `docs/gates/GATE-3.md`.

## In scope

- `scripts/verify_person2.py`: Single verification runner replaying golden pack G01–G10, testing volume accuracy, verifying failure paths, hashing serialization, and executing OCID trial (exits 0).
- `tests/test_geometry_gate3.py`: Automated pytest test suite for all Gate 3 acceptance criteria (5 tests).
- `docs/gates/GATE-3.md`: Official Integration Gate 3 evidence record with full result tables, parameters, limitations, and verification commands.
- `scripts/check_change_impact.py` & `CONTRIBUTING.md`: Add `PERSON2_SCRIPTS` allowlist for `verify_person2.py` to maintain repository change-impact governance.
- `tests/test_repo_governance.py`: Unit test verifying `PERSON2_SCRIPTS` path classification.
- Companion updates to `docs/status/PERSON2.md`, `docs/status/PERSON4.md`, and `CHANGELOG.md`.

## Out of scope

- Person 3 person tracking, proximity, or alert rule evaluation (Gate 4).
- Person 4 vertical pipeline wiring and CLI evaluation (Gate 5).
- Shared contract modifications (`contracts.py`, `manifest.py`, `adapters.py`).

## Inputs, outputs, and contracts

- Consumes frozen golden scenario pack (`scenario-fixtures/golden/`), baseline volume test fixtures (`tests/acceptance/test_baseline_volume.py`), and real-sensor OCID converted sequence (`tests/fixtures/ocid-mini/`).
- Emits deterministic `VolumeChangeEvent` (C-003) objects with verified timestamp monotonicity and SHA-256 hash `f19312ffc150241b228e4eda0fa5993a1e50523ea877904c897fb6207799b736`.
- Does not modify any shared contract.

## Implementation summary

1. **P2-1 Golden Replay:** Replayed scenarios G01 through G10 through `register_frame_to_baseline`, `evaluate_occlusion_safety`, `compute_signed_depth_difference`, and `ShelfGeometryProvider`. Verified removal confirmation in G02/G03/G06, suppression during occlusion in G05, addition detection in G04/G07 (never REMOVAL), and safe zero-candidate handling in G09.
2. **P2-2 Known-Volume Accuracy:** Evaluated 7 floor-sitting objects ($\ge 0.5$ L) against analytical ground truth. Maximum relative error is 6.52% (well within the $\le 10\%$ SLA). Documented single-view hanging-plate under-void column bias as expected limitation.
3. **P2-3 Failure-Path Safety:** Tested drift exceedance (25 mm $> 15$ mm), residual exceedance ($> 2.0$ cm), insufficient fixed points ($< 10$), occlusion ($> 30\%$), and unknown depth ($0.0$ m). Confirmed all failure conditions safely suppress removal events with zero false positives.
4. **P2-4 Serialization Determinism:** Verified canonical JSON serialization with sorted keys produces identical byte stream and SHA-256 hash across repeated runs. Confirmed `first_seen_timestamp_ns <= confirmation_timestamp_ns`.
5. **P2-5 Real-Sensor OCID Trial:** Successfully evaluated converted sequence from `tests/fixtures/ocid-mini/`, detecting 29 removal pixels in the unstacked object frame without spurious drift or false addition candidates.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Linux, Python 3.13 / .venv | `python scripts/verify_person2.py` | Passed (exit 0) | All 5 checks passed cleanly in 1.25s |
| Linux, Python 3.13 / .venv | `python -m pytest tests/test_geometry_gate3.py -v` | Passed (exit 0) | 5 passed in 0.18s |
| Linux, Python 3.13 / .venv | `python -m pytest tests/test_repo_governance.py -v` | Passed (exit 0) | 8 passed in 0.06s |
| Linux, Python 3.13 / .venv | `python -m pytest` | Passed (exit 0) | 194 passed in 3.26s |
| Linux, Python 3.13 / .venv | `python -m ruff check .` | Passed (exit 0) | Clean lint |
| Linux, Python 3.13 / .venv | `python -m compileall -q src tests scripts` | Passed (exit 0) | Clean compilation |
| Linux, repository | `python scripts/check_repo_consistency.py` | Passed (exit 0) | Consistent |
| Linux, repository | `python scripts/check_change_impact.py --base origin/main` | Passed (exit 0) | All companions satisfied |

## Risks and limitations

- Single overhead RGB-D perspective exhibits void-column volume bias under elevated or hanging objects; documented as an expected geometry limitation in `docs/gates/GATE-3.md`.
- Gate 3 formal sign-off requires Person 4 review before closing Gate 3 in `docs/INTEGRATION_GATES.md` and `docs/PROJECT_STATUS.md`.

## Handoff

- Gate 3 evidence complete and ready for Person 4 review.
- Hand off to Person 4 for Gate 5 vertical pipeline integration.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/67
- Pull request: pending
- Commit: pending
