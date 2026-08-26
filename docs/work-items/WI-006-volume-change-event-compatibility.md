# WI-006 — VolumeChangeEvent Compatibility Freeze

- **Owner:** P4
- **Status:** Complete
- **Started:** 2026-08-26
- **Completed:** 2026-08-26
- **Requirements:** C-003 contract compatibility
- **Integration gate:** Gate 1

## Objective

Freeze the existing `VolumeChangeEvent` runtime boundary with a deterministic
Person 4 compatibility fixture and focused tests, without changing its public
contract.

## In scope

- A local compatibility fixture for `VolumeChangeEvent`.
- Tests for event identity, shelf association, signed change type, nanosecond
  timestamps, cubic-metre volume, shelf-frame bounds and centroid, visibility,
  confidence, rejection reason, and evidence-frame metadata.

## Out of scope

- C-004, C-005, or later contracts.
- Manifest changes, including P-005, runtime configuration, geometry
  implementation, tracking, orchestration, CLI, evaluation, or package changes.

## Inputs, outputs, and contracts

- `VolumeChangeEvent` remains the existing runtime dataclass in
  `src/kyra/contracts.py`.
- `change_type` uses the existing `ChangeType` enum.
- Timestamps are integer nanoseconds.
- Missing volume and geometry coordinates use metres, with volume in cubic metres.
- Bounds and centroid are shelf-frame coordinates.
- Visibility and confidence preserve the producer's quality values.
- Rejection reason is optional and evidence frame IDs default to an empty tuple.

## Implementation summary

Added a deterministic compatibility fixture and focused tests for all existing
`VolumeChangeEvent` fields and default metadata behavior. No production contract
changed.

## Documentation impact

- Updated Person 4 status with the completed C-003 evidence.
- Added this work-item record.
- Added a changelog entry for the compatibility test floor.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.10 | `.venv\\Scripts\\python.exe -m pytest tests\\test_volume_change_event_compatibility.py -v` | 2 passed | Focused C-003 test run |
| Windows, Python 3.12.10 | `.venv\\Scripts\\python.exe -m pytest tests\\test_contracts.py -v` | 9 passed | Contract regression test run |
| Windows, repository | `.venv\\Scripts\\python.exe scripts\\check_repo_consistency.py` | Passed | Repository consistency validation |
| Windows, repository | `.venv\\Scripts\\python.exe scripts\\check_change_impact.py --base HEAD` | Passed | Change-impact validation |
| Windows, repository | `git diff --check` | Passed | No whitespace errors |

## Risks, limitations, and failures

C-003 tests cover the current runtime dataclass behavior. Serialization and
producer conformance remain future integration evidence because no Person 2
producer exists yet. No contract version or production implementation change
was required.

## Handoff

C-003 is ready for integration review. The next Person 4 task must be approved
and separately scoped; do not begin C-004 in this work item.

## Final links

- Issue: N/A
- Pull request: N/A
- Commit: N/A
