# WI-004 — PersonTrack Compatibility Freeze

- **Owner:** P4
- **Status:** Complete
- **Started:** 2026-08-26
- **Completed:** 2026-08-26
- **Requirements:** C-004 contract compatibility
- **Integration gate:** Gate 1

## Objective

Freeze the existing `PersonTrack` runtime boundary with a deterministic Person 4
compatibility fixture and focused tests, without changing its public contract.

## In scope

- A local compatibility fixture for `PersonTrack`.
- Tests for track identity, nanosecond timestamps, image-space boxes, metric
  position, proximity/authorization flags, pose-keypoint normalization, and
  near-shelf timestamp behavior.
- Rejection of pose-keypoint arrays without x, y, and confidence columns.

## Out of scope

- C-005 or later contracts.
- Manifest changes, runtime configuration, geometry, tracking implementation,
  orchestration, CLI, evaluation, or package changes.

## Inputs, outputs, and contracts

- `PersonTrack` remains the existing runtime dataclass in
  `src/kyra/contracts.py`.
- Track timestamps are integer nanoseconds.
- Bounding boxes are image-space `(x1, y1, x2, y2)` values.
- Positions are optional three-dimensional metre coordinates.
- Pose keypoints are two-dimensional `float32` arrays with x, y, confidence
  columns.
- `near_shelf`, `wrist_in_shelf`, and `authorized` preserve their boolean state.
- A near-shelf track defaults `last_near_timestamp_ns` to its current timestamp;
  a non-near-shelf track leaves it unset unless explicitly provided.

## Implementation summary

Added a deterministic compatibility fixture and focused tests for field
preservation, pose-keypoint normalization, explicit and default near-shelf
 timestamps, and invalid keypoint shape rejection. No production contract
changed.

## Documentation impact

- Updated Person 4 status with the completed C-004 evidence.
- Added this work-item record.
- Added a changelog entry for the compatibility test floor.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.10 | `.venv\\Scripts\\python.exe -m pytest tests\\test_person_track_compatibility.py -v` | 4 passed | Focused C-004 test run |
| Windows, Python 3.12.10 | `.venv\\Scripts\\python.exe -m pytest tests\\test_contracts.py -v` | 9 passed | Contract regression test run |
| Windows, repository | `.venv\\Scripts\\python.exe scripts\\check_repo_consistency.py` | Passed | Repository consistency validation |
| Windows, repository | `.venv\\Scripts\\python.exe scripts\\check_change_impact.py --base HEAD` | Passed | Change-impact validation |
| Windows, repository | `git diff --check` | Passed | No whitespace errors |

## Risks, limitations, and failures

C-004 tests cover the current runtime dataclass behavior. No contract version or
production implementation change was required. Serialization and producer
conformance remain future integration evidence because no Person 3 producer
exists yet.

## Handoff

C-004 is ready for integration review. The next Person 4 task must be approved
and separately scoped; do not begin C-005 in this work item.

## Final links

- Issue: N/A
- Pull request: N/A
- Commit: N/A
