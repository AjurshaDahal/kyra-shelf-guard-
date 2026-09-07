# WI-064 — Kaggle free-T4 GPU target-T4 leg report

- **Owner:** P1
- **Status:** In review
- **Started:** 2026-09-07
- **Completed:** N/A
- **Requirements:** G0.4 / decision D-015; Gate 2 evidence; PERSON1 handoff T4 leg
- **Integration gate:** Gate 2 (evidence component; gate remains open)

## Objective

Record the executed target-T4 leg on the designated Kaggle free-T4 GPU
notebook: `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md` with the environment
identity, exact commands and exits, dated test totals, golden-pack
byte-identity audit, and honest limitations.

## In scope

- `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md` (new dated report, template-based).
- `docs/status/PERSON1.md`: P1-14 evidence, updated blocked/pending and next.
- `docs/PROJECT_STATUS.md`: target-T4 status line (run recorded; sign-off open).
- `README.md` / `docs/people/README.md`: honest T4 wording.
- `CHANGELOG.md` entry and this record.

## Out of scope

- The independent handoff sign-off (issue #59), real OCID conversion, any
  detection/end-to-end claim, and any claim that the accelerator identity is
  artifact-verified rather than runner-confirmed.

## Inputs, outputs, and contracts

No shared contracts touched. Evidence artifacts: Kaggle export ZIP
(`PERSON1_TEST_REPORT_T4_2026-09-07_draft.txt`, `.pytest_cache` nodeids = 189,
`golden-audit/checksums.sha256`, repository snapshot fingerprint = `main`
`65d3707`). The golden-audit inventory was independently re-verified
byte-identical against the committed `scenario-fixtures/golden/checksums.sha256`
(116/116) during this record's preparation.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest -q` | 189 passed |
| Windows, Python 3.12.7 | `python -m ruff check .` | Passed |
| Windows, Python 3.12.7 | `python -m compileall -q src tests scripts` | Passed |
| Windows, repository | `python scripts/check_repo_consistency.py` | Passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | Passed with companions |
| Local re-verification | golden-audit vs committed checksums.sha256 | identical (116 entries) |
| Local re-verification | zip snapshot vs `65d3707` (pyproject, notebook, contracts.py, golden-pack.json) | byte-exact |

## Risks and limitations

- The exported artifact contains no notebook output cells; accelerator (T4)
  identity is runner-confirmed per Kaggle settings, recorded as such.
- GPU smoke is a published-pin probe (exit 0), not model accuracy.
- The runner applied the one-line `copytree` fix from `13ea8e4` in the UI;
  the executed cell set is the merged discovery cell plus that documented patch.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/64
- Pull request: pending
- Commit: pending