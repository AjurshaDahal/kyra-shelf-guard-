# WI-003 — BaselineArtifact Compatibility Freeze

- **Owner:** P4
- **Status:** Complete
- **Started:** 2026-08-26
- **Completed:** 2026-08-26
- **Requirements:** C-002 contract compatibility
- **Integration gate:** Gate 1

## Objective

Freeze the existing `BaselineArtifact` runtime and persistence boundary with a
deterministic Person 4 compatibility fixture and focused tests, without changing
its public contract.

## In scope

- A local compatibility fixture for `BaselineArtifact` and `PortableComponent`.
- Runtime array normalization and shape tests.
- Complete NPZ/JSON save/load compatibility coverage.

## Out of scope

- C-001, C-003, or later contracts.
- Runtime configuration, manifest changes, including P-005, geometry, tracking,
  orchestration, CLI, evaluation, or package changes.

## Inputs, outputs, and contracts

- `BaselineArtifact` remains schema version `1.0` as defined in
  `src/kyra/contracts.py`.
- Image-space depth and noise arrays are two-dimensional `float32` metres.
- Image-space masks are two-dimensional boolean arrays.
- Occupancy is a three-dimensional `uint8` grid.
- Intrinsics are `float64` `3 x 3`; camera-to-shelf transform is `float64` `4 x 4`.
- Portable components preserve cubic-metre volume, shelf-frame bounds, and pixel
  count.
- Persistence remains compressed NPZ arrays plus sorted JSON metadata.

## Implementation summary

Added a deterministic compatibility fixture and focused tests for runtime
normalization, dimensions, portable-component values, metadata, calibration
checksum, approximate-metric state, and complete save/load round trips. No
production contract changed.

## Documentation impact

- Updated Person 4 status with the completed C-002 evidence.
- Added this work-item record.
- Added a changelog entry for the compatibility test floor.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.10 | `.venv\\Scripts\\python.exe -m pytest tests\\test_baseline_artifact_compatibility.py -v` | 2 passed | Focused C-002 test run |
| Windows, Python 3.12.10 | `.venv\\Scripts\\python.exe -m pytest tests\\test_baseline.py -v` | 10 passed | Baseline regression test run |
| Windows, repository | `.venv\\Scripts\\python.exe scripts\\check_repo_consistency.py` | Passed | Repository consistency validation |
| Windows, repository | `.venv\\Scripts\\python.exe scripts\\check_change_impact.py --base HEAD` | Passed | Change-impact validation |
| Windows, repository | `git diff --check` | Passed | No whitespace errors |

## Risks, limitations, and failures

C-002 tests cover the current runtime and persistence behavior. No contract
version or production implementation change was required.

## Handoff

C-002 is ready for integration review. The next Person 4 task must be approved
and separately scoped; do not begin C-003 in this work item.

## Final links

- Issue: N/A
- Pull request: N/A
- Commit: N/A
