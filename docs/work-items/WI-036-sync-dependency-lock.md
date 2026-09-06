# WI-036 — Synchronize dependency lock with merged pins

- **Owner:** P4
- **Status:** Complete (merged via PR #37 as `68e3b65`)
- **Started:** 2026-09-06
- **Completed:** 2026-09-06
- **Requirements:** documentation/dependency governance
- **Integration gate:** None

## Objective

Make the locked, CI-installed dependency set match the merged `pyproject.toml`
pins (numpy 2.4.6, opencv-python-headless 5.0.0.93, pydantic 2.13.4) and prove
the suite passes with those pins actually installed.

## In scope

- `requirements.lock` pin synchronization.
- Corrected dependency-refresh claims in `docs/DEVELOPMENT.md` and
  `docs/TESTING.md` (the prior entries claimed CI validated the new pins; CI
  installs the lock, so that claim was wrong until this synchronization).
- `CHANGELOG.md`, `docs/status/PERSON4.md`, this record.

## Out of scope

- Further dependency bumps, gate claims, and the auxiliary GPU/simulation
  locks (they do not pin numpy/opencv/pydantic).

## Implementation summary

The 2026-09-06 documentation and consistency pass found that the three
Dependabot merges changed `pyproject.toml` only, while CI installs
`requirements.lock`, which still pinned the old versions. The three pins were
synchronized, the synced lock was installed into the local environment
(`pip install -r requirements.lock && pip install -e .`), and the full suite
passed with the true new pins including the byte-identical golden-pack
regeneration audit under OpenCV 5.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 (pins: numpy 2.4.6, cv2 5.0.0, pydantic 2.13.4) | `python -m pytest -q` | 161 passed (2026-09-06) |
| Windows, Python 3.12.7 | `python -m ruff check .` | Passed |
| Windows, Python 3.12.7 | `python -m compileall -q src tests scripts` | Passed |
| Windows, repository | `python scripts/check_repo_consistency.py` | Passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | Passed with companions |

## Risks and limitations

- CI will validate the true pins (from the synchronized lock) once this lands.
- OpenCV 5 compatibility with the committed pack inventory is now proven by
  the local regeneration audit; the pack itself remains a candidate pending
  D-009.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/36
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/37
- Commit: `68e3b65` (squash merge on `main`)