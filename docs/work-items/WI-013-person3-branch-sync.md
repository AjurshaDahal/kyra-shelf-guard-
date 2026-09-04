# WI-013 — Person 3 Branch Synchronization and Empty-Pose Replay

- **Owner:** P3
- **Status:** Complete
- **Started:** 2026-09-01
- **Completed:** 2026-09-05
- **Requirements:** PR #12 governance repair and replay robustness
- **Integration gate:** Gate 4

## Objective

Bring the verified Person 3 implementation from `origin/person3` onto a clean
branch based on current `origin/main`, keep its ownership-visible diff accurate,
and ensure replay accepts a valid track annotation with no pose keypoints.

## In scope

- Create a clean integration branch from current `origin/main` and apply only
  the net Person 3 implementation diff.
- Remove the Person 3-only pose setup from shared `tests/conftest.py`.
- Keep Person 3 test filenames recognizable by the ownership validator.
- Normalize missing replay pose keypoints to an empty `(0, 3)` float array.
- Refresh Person 3 status, changelog, and verification evidence.

## Out of scope

- Shared contract or manifest changes.
- Person 1 or Person 2 algorithms.
- Person 4 pipeline/orchestration work.
- Gate 4 completion or real end-to-end evidence.

## Inputs, outputs, and contracts

The change consumes the existing `TrackAnnotation.pose_keypoints_xyc` default
and produces the existing `PersonTrack.pose_keypoints_xyc` shape. It changes no
public field, unit, coordinate frame, timestamp meaning, schema version, or
compatibility policy. No contract-change record is required.

## Implementation summary

- The integration branch starts from `origin/main` at `eacb4cc` and applies the
  17-file net Person 3 diff, so current approved mainline work is preserved.
- The source branch's earlier merge commits remain as provenance on
  `origin/person3`; they are not part of the clean integration history.
- Person 3 tests no longer change the shared `scenario_path` fixture.
- Replay explicitly maps an absent pose list to `numpy.empty((0, 3), float32)`.
- Tests are named for their Person 3 component so ownership checks do not infer
  unrelated Person 1 or Person 4 status changes.
- Contributor whitespace defects were removed without changing behavior.

## Documentation impact

- `CHANGELOG.md` records the replay robustness fix.
- `docs/status/PERSON3.md` records the merged subset, remaining work, and
  evidence boundary.
- WI-007 retains the feature handoff; this record covers the synchronization
  and regression repair requested in issue #13.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest tests/test_tracking_replay.py tests/test_tracking_mask.py tests/test_person_proximity.py tests/test_alert_engine.py tests/test_alert_edge_cases.py tests/test_alert_pipeline.py -q` | 22 passed | Person 3 focused suite on clean integration branch |
| Windows, Python 3.12.7 | `python -m pytest` | 105 passed | Full clean-integration suite |
| Windows, Python 3.12.7 | `python -m ruff check .` | Passed | Static checks |
| Windows, Python 3.12.7 | `python -m compileall -q src tests scripts` | Passed | Byte-compilation |
| Windows, Python 3.12.7 | `python scripts/check_repo_consistency.py` | Passed | Repository consistency |
| Windows, Python 3.12.7 | `python scripts/check_change_impact.py --base origin/main` | Passed for 17 changed files | Ownership/documentation impact |
| GitHub CI, PR #19 | Python 3.11 and 3.12 Core CI; Pull Request Governance | Passed | Final reviewed pull-request head |

## Risks, limitations, and failures

- The source branch was one commit behind `origin/main` at integration time;
  direct comparison included current-main reversions that were not contributor
  contract edits.
- Removing the shared fixture pose values exposed the empty-pose replay failure;
  the focused regression test now covers that valid input.
- Fresh hosted CI passed on the final pull-request head before merge.

## Handoff

Pull request #19 merged the clean integration as `5876649`; pull request #12
remains contributor provenance and is superseded for merge. Keep Gate 4 open
until its full exit evidence exists.

## Final links

- Issue: [#13](https://github.com/DontHash/kyra-shelf-guard/issues/13)
- Contributor pull request: [#12](https://github.com/DontHash/kyra-shelf-guard/pull/12)
- Merged clean integration pull request: [#19](https://github.com/DontHash/kyra-shelf-guard/pull/19),
  squash commit `5876649`
- Contributor commits: implementation `bd44222`, Ruff fix `5e384b8`,
  documentation `7471202`, and verified follow-ups through `6bdbd01`.
