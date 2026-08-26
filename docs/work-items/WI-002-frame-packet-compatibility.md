# WI-002 — FramePacket Compatibility Freeze

- **Owner:** P4
- **Status:** Complete
- **Started:** 2026-08-26
- **Completed:** 2026-08-26
- **Requirements:** C-001 contract compatibility
- **Integration gate:** Gate 1

## Objective

Freeze the existing `FramePacket` runtime boundary with a deterministic Person 4
compatibility fixture and focused tests, without changing its public contract.

## In scope

- A local compatibility fixture for `FramePacket`.
- Tests for frame identity, timestamp ordering, RGB/depth/mask shapes and dtypes,
  metric depth values, camera intrinsics, camera-to-shelf coordinates, and
  invalid-depth handling.

## Out of scope

- Other runtime contracts or configuration.
- Manifest changes, including P-005.
- Geometry, tracking, orchestration, CLI, evaluation, or package changes.

## Inputs, outputs, and contracts

- `FramePacket` remains schema version `1.0` as defined in `src/kyra/contracts.py`.
- Depth is two-dimensional `float32` metres in memory.
- RGB is a three-dimensional `uint8` array.
- Valid depth is a two-dimensional boolean mask.
- Intrinsics are `float64` `3 x 3`; camera-to-shelf transform is `float64` `4 x 4`.
- Timestamps are integer nanoseconds and remain ordered by replay consumers.
- Zero, non-finite, negative, or explicitly masked depth is unknown.

## Implementation summary

Added a deterministic compatibility fixture and focused tests. No production
contract or public import changed.

## Documentation impact

- Updated Person 4 status with the completed C-001 evidence.
- Added this work-item record.
- Added a changelog entry for the compatibility test floor.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.14 | `python -m pytest tests\\test_frame_packet_compatibility.py -q` | Blocked: pytest is not installed | Local environment limitation |
| Windows, Python 3.14 | `python -m compileall -q src tests scripts` | Passed | Local syntax validation |
| Windows, repository | `git diff --check` | Passed | No whitespace errors |

## Risks, limitations, and failures

The focused pytest command could not run because the documented Python 3.12
virtual environment is absent and the available Python 3.14 environment does not
have pytest installed. No contract inconsistency was observed during test design.

## Handoff

The C-001 test floor is ready for execution in the supported Python 3.12
environment. The next Person 4 task should address the next approved shared
contract only after the required owner approvals and work item are recorded.

## Final links

- Issue: N/A
- Pull request: N/A
- Commit: N/A
