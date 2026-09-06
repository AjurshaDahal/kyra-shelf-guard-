# WI-044 — Record OCID licence research and G0.4 T4 proposal

- **Owner:** P4 (recording) with P1 research input
- **Status:** In review
- **Started:** 2026-09-06
- **Completed:** N/A
- **Requirements:** P-003, G0.4
- **Integration gate:** Gate 2 enabler

## Objective

Turn the two remaining open decisions into one-approval artifacts with real
factual basis, without claiming approval or download.

## In scope

- `docs/DECISIONS.md`: P-003 research facts (CC-BY 4.0, published md5, depth
  format match, repository-terms open item, YCB/ARID provenance open item)
  and the G0.4/P-004 assignment proposal.
- `data-sources/provenance.json`: completed with the published checksum
  (md5), licence, terms URLs/notes; `status` stays `pending_download`.
- `docs/PERSON1_IMPLEMENTATION_PLAN.md` G0.4 row; `docs/PROJECT_STATUS.md`
  P-003/P-004 bullets; `CHANGELOG.md`; this record.

## Out of scope

- Downloading OCID, formal P-003 approval, T4 execution, gate changes, and
  Person 2/3/4 implementation.

## Implementation summary

The official TU Wien Research Data record (DOI 10.48436/pcbjd-4wa12) declares
the OCID dataset CC-BY 4.0 International; the archive is
`OCID-dataset.tar.gz` (6.4 GiB, published md5 `aa0eff01f75104c40e4243e6f892a757`)
and its depth/label formats match the converter assumptions. These facts were
recorded as research with clearly separated open items for the team, and G0.4
was recorded as a proposal (runner with T4 access, exact command set in the
handoff guide, report path `docs/PERSON1_TEST_REPORT_T4_<date>.md`).

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest tests/test_dataset_provenance.py -q` | 8 passed |
| Windows, Python 3.12.7 | `python -m pytest -q` | 161 passed |
| Windows, repository | `python scripts/check_repo_consistency.py` | Passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | Passed with companions |

## Risks and limitations

- Research is not approval. Download remains blocked until the team confirms
  the repository terms of use and the selected subset provenance (P-003), and
  G0.4 still needs a named runner with T4 hardware.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/44
- Pull request: pending
- Commit: pending