# WI-053 — Integrate Dependabot dependency bumps and synchronize dependency locks

- **Owner:** P4
- **Status:** Complete
- **Started:** 2026-09-07
- **Completed:** 2026-09-07
- **Requirements:** dependency-security governance (WI-036 pattern)
- **Integration gate:** None

## Objective

Bring the locked, CI-installed dependency set and the optional GPU locks into
agreement with the open Dependabot bumps pydantic 2.13.5, torch 2.14.0, and
ultralytics 8.4.138, and prove the suite passes with the true pins installed.

## In scope

- `pyproject.toml`: pydantic 2.13.4 -> 2.13.5 (runtime); torch 2.13.0 -> 2.14.0
  (tracking and midas extras); ultralytics 8.4.123 -> 8.4.138 (tracking extra).
- `requirements.lock`: pydantic 2.13.4 -> 2.13.5 (core lock).
- `requirements-gpu.lock`: torch 2.13.0 -> 2.14.0; ultralytics 8.4.123 ->
  8.4.138 (optional GPU extras).
- `docs/DEVELOPMENT.md` and `docs/TESTING.md` dependency refresh logs.
- `CHANGELOG.md`, `docs/status/PERSON4.md`, this record.

## Out of scope

- numpy 2.4.6 / opencv-python-headless 5.0.0.93 (already current), other
  dependency upgrades, code/schema/contract changes, and any target-T4 or
  installed-GPU acceptance claim for the optional torch/ultralytics bumps.

## Inputs, outputs, and contracts

Dependabot PRs #47/#48/#49 supply the pins; this work item folds them into the
synchronized lock files and documentation the repository dependency policy
requires (per `docs/DEVELOPMENT.md`). No shared-contract or schema changes.
The three Dependabot PRs are closed as superseded by this integration.

## Implementation summary

Applied the three pin changes to `pyproject.toml`, updated `requirements.lock`
(core pydantic pin) and `requirements-gpu.lock` (optional torch/ultralytics
pins), installed the synced core lock into the local environment
(`pip install -r requirements.lock && pip install -e .`), and ran the full
required checks including the byte-identical golden-pack regeneration audit.

## Documentation impact

- `docs/DEVELOPMENT.md`: dependency refresh log entry for 2026-09-07.
- `docs/TESTING.md`: dependency refresh log entry for 2026-09-07, keeping the
  optional-pin caveat (not an installed GPU or T4 acceptance result).
- `CHANGELOG.md`: `Changed` entry for the synchronized pins.
- `docs/status/PERSON4.md`: Issue #53 section.
- This durable work-item record.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 (pins: pydantic 2.13.5, numpy 2.4.6, cv2 5.0.0.93) | `python -m pytest -q` | 189 passed (2026-09-07) |
| Windows, Python 3.12.7 | `python -m ruff check .` | Passed |
| Windows, Python 3.12.7 | `python -m compileall -q src tests scripts` | Passed |
| Windows, repository | `python scripts/check_repo_consistency.py` | Passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | Passed with companions |
| Windows, repository | golden-pack regeneration vs `scenario-fixtures/golden/checksums.sha256` | Byte-identical (2026-09-07) |
| CI | Core checks (Python 3.11/3.12), Documentation change impact | Passed on the pull request |

## Risks and limitations

- Optional GPU pins (torch 2.14.0, ultralytics 8.4.138) are verified as
  published/advisory-fixed pins only; target-T4 smoke validation remains a
  Gate 7 item and is not claimed here.
- The core lock reinstalled cleanly; CI revalidates from the lock on the PR.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/53
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/54
- Commit: `4146e3b` (squash merge on `main`)
- Superseded and closed: Dependabot PRs #47, #48, #49