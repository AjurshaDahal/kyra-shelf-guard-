# WI-072 — Lazy optional tracking adapter (YOLO + ByteTrack)

- **Owner:** P3 (shared-surface coordination with P4)
- **Status:** Complete
- **Started:** 2026-09-09
- **Completed:** 2026-09-09
- **Requirements:** Gate 4 exit criterion "lazy optional pretrained adapter"; D-001/D-002 optional-path rules
- **Integration gate:** Gate 4 (final exit-criterion component)

## Objective

Land the optional lazily-loaded pretrained tracking adapter on `main` as an
additive provider, with tests proving it never imports Torch/ultralytics at
construction and raises a clear error without the tracking extras.

## In scope

- `src/kyra/adapters.py`: `LazyUltralyticsTrackingProvider` (authored by
  @AjurshaDahal on `origin/person3`, commit `b0a6c7e`) — additive class +
  `__all__` entry; no protocol or mock changes.
- `tests/test_lazy_tracking_adapter.py` (same commit, 3 tests): no-import-at-
  construction, missing-extras error, and fake-model `PersonTrack` conversion.
- Companions: `CHANGELOG.md`, `docs/status/PERSON3.md`, `docs/gates/GATE-4.md`
  addendum, `docs/status/PERSON4.md` note, this record.

## Out of scope

- Running the model on the target environment (Gate 5/7 with
  `requirements-gpu.lock`).
- Any deterministic-core dependency on ultralytics.

## Inputs, outputs, and contracts

Consumes `FramePacket` (C-001); produces frozen `PersonTrack` (C-004) objects
with empty `(0, 3)` pose keypoints, `position_m=None`, and deterministic
sorting. No shared-contract change; `src/kyra/adapters.py` is extended
additively under Person 4 coordination.

## Implementation summary

Cherry-picked the two code files from the superseded `person3` branch commit
`b0a6c7e`; wrote fresh doc companions (the branch's own doc edits were based
on the obsolete branch base and were not applicable verbatim). Full suite:
199 tests pass (196 + 3 new); ruff, compileall, consistency, and
change-impact all green.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 (frozen lock, no GPU extras installed) | `python -m pytest tests/test_lazy_tracking_adapter.py -q` | 3 passed in 0.06s |
| Windows, Python 3.12.7 | `python -m pytest -q` | 199 passed in 4.39s |
| Windows, Python 3.12.7 | `python -m ruff check .` | passed |
| Windows, Python 3.12.7 | `python -m compileall -q src tests scripts` | passed |
| Windows, repository | `python scripts/check_repo_consistency.py` | passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | passed with companions |

## Risks and limitations

- The adapter is untested against a real ultralytics installation in CI by
  design (extras are not in the core lock); live smoke on the Kaggle T4
  notebook is a Gate 7 item.
- No GPU/extras path was executed in this validation run.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/72
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/73
- Commit: `d22dbf6` (squash merge on `main`)