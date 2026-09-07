# WI-056 — Complete Phase 0 decisions (P-003 approval and G0.4 Kaggle free-T4 runner)

- **Owner:** P4 (recorded with project-owner approval)
- **Status:** Complete
- **Started:** 2026-09-07
- **Completed:** 2026-09-07
- **Requirements:** P-003 (licence), G0.4 (T4 runner), issue #40 closure
- **Integration gate:** None directly; unblocks Gate 2/Gate 7 T4 evidence and the OCID smoke test

## Objective

Close issue #40 by formally approving the OCID licence terms (D-014) and
assigning the target-T4 runner to a Kaggle free-T4 GPU notebook with a
reproducible runner notebook committed to the repository (D-015), leaving
only the independent Person 1 handoff sign-off as a human action.

## In scope

- `docs/DECISIONS.md`: new locked decisions D-014 (OCID CC-BY 4.0 research
  use and tiny-example publication with attribution; archive outside Git;
  YCB/ARID-derived objects guarded) and D-015 (target-T4 runner = Kaggle
  free-T4 GPU notebook `notebooks/kyra_t4_validation.ipynb`; report at
  `docs/PERSON1_TEST_REPORT_T4_<date>.md` via reviewed PR); resolved P-003
  and P-004; pending section keeps P-005/P-006.
- `docs/PROJECT_STATUS.md`: active decisions/blockers updated; the
  independent sign-off remains named as the only open Phase 0 item.
- `data-sources/provenance.json` + `data-sources/README.md`:
  `licence_review_status` now `approved-2026-09-07 (D-014)`; `status` stays
  `pending_download`; exclusions updated to the redistribution guard.
- `docs/status/PERSON1.md` and `docs/status/PERSON4.md`: unblocked T4/OCID
  state recorded.
- `CHANGELOG.md`: Phase 0 decisions entry.
- `notebooks/kyra_t4_validation.ipynb`: new Kaggle free-T4 runner notebook
  (environment identity, core lock install, full dated test suite, seven-check
  verifier, golden-pack byte-identity audit, optional GPU smoke, dated report
  output), mirroring `docs/PERSON1_HANDOFF.md` steps 1-2.
- This durable work-item record.

## Out of scope

- The actual OCID download/conversion and the actual Kaggle T4 run/report.
- The independent Person 1 handoff sign-off (tracked in a new open issue).
- Person 1-4 GitHub handles (recorded by the project owner when known).
- No code, contract, or test behavior changes.

## Inputs, outputs, and contracts

No shared contracts changed. Provenance schema 1.0 fields preserved;
`tests/test_dataset_provenance.py` must continue to pass against the updated
record.

## Implementation summary

Phase 0 items that are decisions were executed: P-003 is recorded as approved
(project owner + Person 4, D-014) with concrete conditions and the research
facts; P-004/G0.4 is recorded as decided (D-015) with the Kaggle free-T4 GPU
notebook as runner environment and the evidence contract for the T4 report.
Provenance state was updated honestly: licence approved, download still
pending. The remaining Phase 0 item (independent sign-off) is not a decision
and remains open for a human.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest -q` | 189 passed (2026-09-07) |
| Windows, Python 3.12.7 | `python -m ruff check .` | Passed |
| Windows, Python 3.12.7 | `python -m compileall -q src tests scripts` | Passed |
| Windows, repository | `python scripts/check_repo_consistency.py` | Passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | Passed with companions |
| Notebook | `notebooks/kyra_t4_validation.ipynb` loads as valid nbformat-4 JSON (9 markdown + 8 code cells) | Valid |

## Risks and limitations

- Kaggle T4 is the designated runner environment (D-015); a non-T4 GPU or
  Windows-leg result is not T4 evidence.
- The notebook itself is not executed in CI; its execution evidence is
  produced by the runner and reported via `docs/PERSON1_TEST_REPORT_T4_<date>.md`.
- Approval records are dated 2026-09-07 and reflect the project owner's
  decision; the downloader must still accept the TU Wien terms of use.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/56
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/57
- Commit: `765aa5f` (squash merge on `main`)
- Issue #40 closed as resolved (D-009, D-014, D-015); the independent
  handoff sign-off is tracked separately (issue #59)