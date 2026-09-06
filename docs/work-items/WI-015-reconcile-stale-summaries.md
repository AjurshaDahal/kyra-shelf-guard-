# WI-015 — Reconcile stale shared test-count summaries

- **Owner:** P4
- **Status:** Complete
- **Started:** 2026-09-04
- **Completed:** 2026-09-06
- **Requirements:** documentation governance
- **Integration gate:** None

## Objective

Stop shared project summaries from presenting stale exact automated-test
totals as current truth, by adopting dated totals plus evidence pointers.

## In scope

- `README.md`, `docs/TESTING.md`, `docs/PROJECT_STATUS.md`,
  `docs/people/README.md`, and the G2 gate row wording.
- `docs/status/PERSON4.md`, `CHANGELOG.md`, this record, and final-link
  updates for `WI-031` (merged as `e37e729`).

## Out of scope

- Product behavior, test expectations, integration/T4 claims, and the
  dependabot bumps.

## Implementation summary

The documentation-policy decision (Person 4 as accountable owner) is: a
summary states a **dated total** with a verification date and a pointer to the
per-owner durable evidence, and never restates an old number as a current
one. Applied totals: 161 tests on Windows/Python 3.12.7 on 2026-09-06.
`docs/TESTING.md` now states the dated-total rule explicitly.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest -q` | 161 passed (2026-09-06), matching the new dated totals |
| Windows, repository | `python scripts/check_repo_consistency.py` | Passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | Passed with companions |

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/15
- Pull request: pending
- Commit: pending