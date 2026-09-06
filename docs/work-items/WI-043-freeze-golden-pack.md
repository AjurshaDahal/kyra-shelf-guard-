# WI-043 — Freeze the golden scenario pack (D-009 confirmed)

- **Owner:** P1
- **Status:** Complete (merged via PR #43 as `9f637f7`)
- **Started:** 2026-09-06
- **Completed:** 2026-09-06
- **Requirements:** P1-04; P1-SIM-003, D-009, P1-QA-001 (freeze prerequisite)
- **Integration gate:** Gate 2 enabler

## Objective

Freeze the ten-scenario golden pack after the D-009 confirmation, so its
checksums become frozen evidence usable by the P1-12 target-T4 leg and
downstream owners.

## In scope

- `src/kyra/golden_pack.py`: constants to `frozen` /
  `D-009-confirmed-2026-09-06`.
- Regenerated `scenario-fixtures/golden/golden-pack.json` and
  `checksums.sha256` (only `golden-pack.json` changed canonically among the
  pack files; verified byte-identical for every other asset).
- `tests/test_golden_pack.py` assertions.
- `docs/DECISIONS.md` (D-009 confirmed), plan (G0.2, P1-04, Wave 2 exit,
  status line, starting point), `docs/status/PERSON1.md`,
  `docs/PROJECT_STATUS.md` (G2 row), `docs/PERSON1_HANDOFF.md`, `CHANGELOG.md`,
  this record.

## Out of scope

- The T4 leg and P-003/OCID download; Person 2/3/4 implementation; gate
  completion claims.

## Implementation summary

The D-009 decision was confirmed on 2026-09-06 (recorded under issue #40). The
pack generator's status constants were updated to frozen / confirmed, the pack
was regenerated to a temporary directory, a canonical-LF comparison confirmed
that only `golden-pack.json` genuinely changed, and that file plus the
regenerated checksum inventory were synchronized into the repo. The frozen
pack regeneration remains byte-identical, so the audit test passes on both
Windows (CRLF) and T4 (LF) checkouts.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest tests/test_golden_pack.py tests/test_simulation.py -q` | 11 passed |
| Windows, Python 3.12.7 | `python -m pytest -q` | 161 passed |
| Windows, Python 3.12.7 | `python -m ruff check .` | Passed |
| Windows, repository | `python scripts/check_repo_consistency.py` | Passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | Passed with companions |

## Risks and limitations

- Freezing records the D-009 interpretation; it does not by itself provide
  T4 agreement (P1-12) or end-to-end evidence (Gates 3-7).

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/40 (decision)
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/43
- Commit: `9f637f7` (squash merge on `main`)