# WI-005 — AlertEvent Compatibility Freeze

- **Owner:** P4
- **Status:** Complete
- **Started:** 2026-08-26
- **Completed:** 2026-08-26
- **Requirements:** C-005 contract compatibility
- **Integration gate:** Gate 1

## Objective

Freeze the existing `AlertEvent` runtime boundary with a deterministic Person 4
compatibility fixture and focused tests, without changing its public contract.

## In scope

- A local compatibility fixture for `AlertEvent`.
- Tests for alert identity, shelf and source-event references, track identity,
  rule version, timestamps, metric volume, confidence, reason, evidence frames,
  and frozen-instance behavior.

## Out of scope

- C-006 or later contracts.
- Manifest changes, runtime configuration, geometry, tracking implementation,
  orchestration, CLI, evaluation, or package changes.

## Inputs, outputs, and contracts

- `AlertEvent` remains the existing frozen dataclass in `src/kyra/contracts.py`.
- Alert timestamps are integer nanoseconds.
- Missing volume is measured in cubic metres.
- `volume_event_id` links the alert to a geometry event and `person_track_id`
  links it to the associated person track.
- `rule_version`, `reason`, and evidence frame IDs preserve deterministic rule
  provenance.
- Evidence frame IDs default to an empty tuple.

## Implementation summary

Added a deterministic compatibility fixture and focused tests for field
preservation, default evidence-frame behavior, and frozen-instance enforcement.
No production contract changed.

## Documentation impact

- Updated Person 4 status with the completed C-005 evidence.
- Added this work-item record.
- Added a changelog entry for the compatibility test floor.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.10 | `.venv\\Scripts\\python.exe -m pytest tests\\test_alert_event_compatibility.py -v` | 2 passed | Focused C-005 test run |
| Windows, Python 3.12.10 | `.venv\\Scripts\\python.exe -m pytest tests\\test_contracts.py -v` | 9 passed | Contract regression test run |
| Windows, repository | `.venv\\Scripts\\python.exe scripts\\check_repo_consistency.py` | Passed | Repository consistency validation |
| Windows, repository | `.venv\\Scripts\\python.exe scripts\\check_change_impact.py --base HEAD` | Passed | Change-impact validation |
| Windows, repository | `git diff --check` | Passed | No whitespace errors |

## Risks, limitations, and failures

C-005 tests cover the current runtime dataclass behavior. Serialization and
producer conformance remain future integration evidence because no Person 3
producer exists yet. No contract version or production implementation change
was required.

## Handoff

C-005 is ready for integration review. The next Person 4 task must be approved
and separately scoped; do not begin C-006 in this work item.

## Final links

- Issue: N/A
- Pull request: N/A
- Commit: N/A
