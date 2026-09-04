# WI-014 — Deterministic scenario generator

- **Owner:** P1
- **Status:** In review
- **Started:** 2026-09-04
- **Completed:** N/A
- **Requirements:** P1-03; P1-SIM-001, P1-SIM-002, P1-SIM-004, P1-SIM-005
- **Integration gate:** Gate 2

## Objective

Provide one offline, lightweight generator that writes a replayable manifest 1.1
RGB-D scenario deterministically from explicit settings and a single seed.

## In scope

- `src/kyra/simulation.py` settings and generation API.
- Low-resolution lossless RGB, uint16-millimetre depth, valid-depth, object, and
  occlusion PNG assets.
- Thirty opening baseline frames followed by event frames with monotonically
  increasing integer-nanosecond timestamps.
- Seeded object placement for all four approved C-006 shape families.
- Removal and addition ground truth, synthetic evidence labels, calibration,
  shelf bounds, portable relative paths, and safe output-folder handling.
- Focused determinism, replay, metadata, shape, change-direction, and overwrite
  protection tests.

## Out of scope

- P1-04 ten-scenario composition or frozen golden checksums.
- BlenderProc, downloaded assets, OCID/public data, or provenance changes.
- Baseline algorithms and known-volume acceptance.
- Person 2 geometry, Person 3 tracking/rules, Person 4 pipeline/CLI/evaluation,
  complete Gate 2, target-T4, public-data, or end-to-end claims.
- Shared contract, schema, or runtime `FramePacket` changes.

## Inputs, outputs, and contracts

- Consumes approved C-006 manifest version 1.1 and its four `ShapeFamily` values.
- Uses the frozen C-007 shelf fields without extending their meaning.
- Writes RGB and masks as PNG; depth is single-channel uint16 millimetres on
  disk and replays as two-dimensional float32 metres through
  `ScenarioFrameSource`.
- Uses integer nanosecond timestamps in increasing order and forward-slash
  relative manifest paths.
- Produces synthetic development evidence only. Runtime `SCHEMA_VERSION` and
  `FramePacket` are unchanged.

## Implementation summary

The generator derives object position, dimensions, thickness, texture, and
colour from one NumPy random generator. It writes inspectable scenario assets,
builds the approved manifest model, and rejects a non-empty destination so stale
or user-owned files are never silently mixed with new output. Removal scenarios
show an object during the baseline and expose the cleared shelf after the event;
addition scenarios do the inverse. The event object mask remains available as
ground truth in either direction.

## Documentation impact

- Updated `docs/status/PERSON1.md` with the in-review implementation and honest
  evidence boundary.
- Updated `docs/PERSON1_IMPLEMENTATION_PLAN.md` to close P1-02 and record P1-03.
- Updated `CHANGELOG.md` with the new Person 1 capability.
- Added this durable issue-scoped record.
- `docs/DATASETS.md` is unchanged because no external data, asset, model,
  licence, or provenance behavior changed.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest tests/test_simulation.py -q` | Passed | 8 passed in 4.27s on 2026-09-05; synthetic/offline only |
| Windows, Python 3.12.7 | `python -m pytest -q` | Passed | 113 passed in 4.64s on 2026-09-05 |
| Windows, Python 3.12.7 | `.venv\Scripts\python.exe -m ruff check .` | Passed | All checks passed |
| Windows, Python 3.12.7 | `.venv\Scripts\python.exe -m compileall -q src tests scripts` | Passed | Exit code 0 |
| Windows, repository | `.venv\Scripts\python.exe scripts/check_repo_consistency.py` | Passed | Repository consistency check passed |
| Windows, repository | `.venv\Scripts\python.exe scripts/check_change_impact.py --base origin/main` | Passed | Six changed files satisfied required companions |
| Windows, Git | `git diff --check` and `git diff --cached --check` | Passed | No whitespace errors |

## Risks, limitations, and failures

- The generated output is intentionally simple synthetic evidence; it is not a
  physics renderer, public-data result, target-T4 result, or end-to-end alert.
- P1-04 still needs the team to confirm the provisional scenario-ten choice
  before golden checksums can be frozen.
- Cross-platform byte equality is not claimed by this work item; the current
  determinism proof compares independent runs in the same locked Windows
  environment. Windows/T4 pack equality remains P1-12 evidence.

## Handoff

Person 1 should address review on issue #14, then claim P1-04. That work composes
the approved behavior matrix from this generator and must record the team
decision for scenario ten before calling the pack frozen. Person 4 validates
consumption at Gate 2 after the remaining Person 1 exit evidence exists.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/14
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/16
- Implementation commit: `696e92e`
