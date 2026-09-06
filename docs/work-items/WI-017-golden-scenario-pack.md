# WI-017 — Candidate golden scenario pack

- **Owner:** P1
- **Status:** Complete (candidate merged via PR #27 as `327a905`; pack remains unfrozen pending D-009)
- **Started:** 2026-09-04
- **Completed:** 2026-09-06
- **Requirements:** P1-04; P1-SIM-003, P1-SIM-005, P1-QA-001
- **Integration gate:** Gate 2

## Objective

Compose and audit one tiny, deterministic ten-scenario candidate pack from the
P1-03 generator without prematurely freezing the provisional D-009 choice.

## In scope

- `src/kyra/golden_pack.py` candidate matrix and composition API.
- `scripts/generate_golden_pack.py` safe offline generation entry point.
- `scenario-fixtures/golden/` manifests, PNG assets, index, and SHA-256 inventory.
- P1-owned extensions to the lightweight generator for no-change, occlusion,
  lighting, invalid-depth, camera-drift, and authorized-restocking source data.
- Focused checks for manifest replay, behavior encoding, shape coverage,
  checksum integrity, and byte-identical regeneration.

## Out of scope

- Calling the pack frozen or resolving the team's D-009 choice.
- Downstream Person 2 geometry, Person 3 tracking/alert decisions, or Person 4
  pipeline, CLI, evaluation, CI, release, and Gate 2 acceptance.
- Target-T4 or cross-platform byte-equality claims.
- BlenderProc, downloaded assets, OCID/public data, provenance, or licences.
- Shared contracts, manifest schema, runtime `FramePacket`, or C-007 changes.

## Inputs, outputs, and contracts

- Issue #14 and pull request #16 supplied the merged P1-03 generator; this work
  is now integrated with that result on current `origin/main`.
- Consumes approved C-006 manifest 1.1 and the frozen C-007 shelf fields without
  changing their names, types, units, coordinate frames, or compatibility.
- Writes 16-bit PNG millimetres and replays two-dimensional float32 metres;
  zero depth and false valid masks remain unknown rather than empty shelf space.
- Uses increasing integer-nanosecond timestamps, fixed scenario seeds, sorted
  JSON/checksum output, and forward-slash relative paths.
- The index records `pack_status: candidate` and
  `decision_status: D-009-provisional-team-confirmation-required`.

## Implementation summary

The pack composes G01 through G10 from explicit settings and covers no change,
two removal shapes, addition, person-only occlusion, removal then occlusion,
authorized restocking, lighting variation, invalid depth, and camera drift. It
includes every approved `ShapeFamily`. The audit checks source evidence and
metadata only; it does not claim that downstream components produced the
indexed expected results. Generation refuses a non-empty destination.

## Documentation impact

- Updated `CHANGELOG.md` with the candidate capability and remaining freeze gap.
- Updated `docs/PERSON1_IMPLEMENTATION_PLAN.md` with P1-04 status and evidence.
- Updated `docs/status/PERSON1.md` with current scope, limitations, and handoff.
- Updated `docs/TESTING.md` with the safe generation and focused-audit commands.
- `docs/DECISIONS.md`, `docs/CONTRACTS.md`, and `docs/DATASETS.md` are unchanged:
  D-009 remains provisional, no public contract changed, and no external data
  or licence was introduced.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest tests/test_simulation.py tests/test_golden_pack.py -q` | Passed | 11 passed in 6.46s on 2026-09-05; synthetic/offline only |
| Windows, Python 3.12.7 | `python -m pytest -q` | Passed | 116 passed in 5.58s on 2026-09-05 |
| Windows, Python 3.12.7 | `.venv\Scripts\python.exe -m ruff check .` | Passed | All checks passed |
| Windows, Python 3.12.7 | `.venv\Scripts\python.exe -m compileall -q src tests scripts` | Passed | Exit code 0 |
| Windows, repository | `.venv\Scripts\python.exe scripts/check_repo_consistency.py` | Passed | Repository consistency check passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | Failed | Reconfirmed on 2026-09-05: classifier incorrectly requires P4 status and AGENTS/CONTRIBUTING for the P1-owned script/test; tracked in #18 |
| Windows, artifacts | File count and byte total under `scenario-fixtures/golden/` | Passed | 117 files; 62,614 bytes |

## Risks, limitations, and failures

- The D-009 second-removal choice is provisional. Reviewers must confirm it
  before changing `pack_status` or using this checksum inventory as frozen
  cross-owner evidence.
- OpenCV PNG output is byte-identical in the current locked Windows environment;
  cross-platform equality remains unproven until P1-12.
- These fixtures prove deterministic inputs and labels, not downstream volume,
  tracking, alerting, performance, or real-camera behavior.
- `docs/TEAM_OWNERSHIP.md` and this approved plan assign golden fixtures,
  corresponding tests, and the named generation script to Person 1, while
  `scripts/check_change_impact.py` currently classifies those paths as Person 4
  governance. Issue #18 records both sources and keeps this branch fail-closed.
- Test-first execution initially failed because `kyra.golden_pack` and the
  committed fixtures did not exist; implementation and generation resolved the
  expected red state.

## Handoff

Person 4 should land the narrow classifier correction in issue #18. Person 1
then integrates that correction, reruns every required check, pushes this
branch, and requests review of the behavior matrix—especially the provisional
irregular-removal choice. Pull request #16 is merged. The team must record D-009
confirmation before Person 1 changes the pack from candidate to frozen.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/17
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/27
- Commit: `327a905` (squash merge on `main`)
