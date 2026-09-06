# WI-018 — Align change-impact ownership with approved Person 1 paths

- **Owner:** P4 (approval recorded by the repository steward on 2026-09-06; task prepared and reviewed by P1)
- **Status:** Complete
- **Started:** 2026-09-04
- **Completed:** 2026-09-06
- **Requirements:** repository governance; Gate 2 enabler
- **Integration gate:** None (governance/CI alignment)

## Objective

Remove the classifier conflict that treated Person 1's named scripts and the
golden-pack audit test as Person 4 governance, without weakening Person 4
guardrails for actual governance, CI, pipeline, CLI, and evaluation paths.

## In scope

- `scripts/check_change_impact.py`: `PERSON1_SCRIPTS` allowlist, `_owner_for`
  script/test classification, and governance-set exclusion of allowlisted
  scripts.
- `tests/test_repo_governance.py`: four focused classifier tests.
- `CONTRIBUTING.md`: documented the change-impact ownership rule.
- `docs/status/PERSON4.md`, `CHANGELOG.md`, this record.

## Out of scope

- Shared contract/schema changes, P1-04 behavior, the D-009 freeze decision,
  and any blanket reassignment of scripts to Person 1.

## Implementation summary

`PERSON1_SCRIPTS = {"generate_golden_pack.py", "convert_ocid.py", "verify_person1.py"}`.
`_owner_for` returns Person 1 for allowlisted script names and for test names
containing `golden`, `midas`, or `provenance` (the plan-named test files whose
deviations are now reconcilable). The governance set in `assess_changes`
excludes allowlisted scripts, so no AGENTS.md/CONTRIBUTING.md companion is
demanded for them; every other `scripts/` and `.github/` change still requires
Person 4 status and governance companions. The new tests assert both sides of
the rule.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest tests/test_repo_governance.py -q` | 7 passed |
| Windows, Python 3.12.7 | `python -m pytest -q` | full suite result recorded below |
| Windows, repository | `git diff --name-only origin/main` + patched validator | PR #27 (128 files) and PR #28 (5 files) both PASS with their Person 1 companions (pre-landing validation) |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | PASS with this issue's companions |

## Risks and limitations

- The allowlist is intentionally narrow; a future Person 1 script must be
  added to `PERSON1_SCRIPTS` through the documented Person 4-reviewed change,
  per `CONTRIBUTING.md`.
- The fix changes a required CI check but no runtime contract; no
  DECISIONS/CONTRACTS impact.

## Handoff

- After landing: merge PR #27 (golden pack) and PR #28 (verify script) once
  their checks rebuild green; then continue D-009 and P1-12/P1-13.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/18
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/29
- Commit: `0b034c0` (squash merge on `main`)