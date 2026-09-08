# WI-081 — Real OCID conversion and replay smoke

- **Owner:** P1
- **Status:** In review
- **Started:** 2026-09-08
- **Completed:** 2026-09-08
- **Requirements:** P1-09, P1-10
- **Integration gate:** Gate 2 (supplementary evidence)

## Objective

Verify the approved OCID archive, convert a bounded real recorded-data subset,
and prove every resulting scenario can be consumed through the input contract.

## In scope

- `data-sources/provenance.json` and the dataset/status evidence documents.
- Four ARID20 tabletop sequences, each converted forward and reverse.
- Archive identity, output identity, and contract-reader replay checks.

## Out of scope

- Committing or redistributing OCID/ARID images, depth maps, or bulk outputs.
- Model inference, accuracy, latency, live cameras, store deployment, or proof
  of theft intent.

## Inputs, outputs, and contracts

- Input: OCID 1.0.0 `OCID-dataset.tar.gz`, 6,822,716,319 bytes.
- Selected input: `ARID20/table/{top,bottom}/seq0{1,2}`.
- Output: 8 external manifest 1.1 scenarios, 21 frames each, under
  `<KYRA_DATA_ROOT>/ocid/converted/`.
- Contract: uint16 millimetres on disk, two-dimensional `float32` metres in
  memory, zero unknown, monotonically increasing integer-nanosecond timestamps.
- Detailed source and manifest hashes remain in the external
  `<KYRA_DATA_ROOT>/ocid/verification_summary.json` report.

## Implementation summary

The archive matched the publisher MD5
`aa0eff01f75104c40e4243e6f892a757`; its local SHA-256 is
`01878149adf7eb330f99439ee9d15d6e2280a1aa3539b90e0b6dc3c7ba1fa29f`.
All 8 converted manifests and 168 frames loaded through
`ScenarioFrameSource` with the required timestamps, dimensions, depth type,
and unknown-depth behavior.

## Documentation impact

Provenance, dataset rules, Person 1 status, Gate 2 supplementary evidence,
project status, and changelog now describe the completed bounded smoke instead
of the stale `pending_download` state.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows 11, Python 3.12.7 | external archive MD5 and SHA-256 calculation | Passed | Values recorded above and in external verification summary |
| Windows 11, Python 3.12.7 | replay all selected manifests with `ScenarioFrameSource` | Passed: 8 scenarios, 168 frames | External `verification_summary.json` |
| Windows 11, Python 3.12.7 | `python -m pytest tests/test_ocid.py tests/test_dataset_provenance.py -q` | Passed: 21 tests | This work item |
| Windows 11, Python 3.12.7 with optional GPU dependencies | `python -m pytest -q` | Failed: 244 passed, 2 import failures | Ultralytics installed a conflicting top-level `tests` package; follow-up prerequisite issue |
| Windows 11, Python 3.12.7 | `python -m ruff check .`; byte-compile; repository consistency | Passed | This work item |

## Risks, limitations, and failures

The selected source contains ARID-derived objects and is not redistributed.
The replay check does not test missing-volume detection, people, alert logic,
accuracy, live capture, lighting drift, occlusion, or performance.

The optional model environment exposed a pre-existing test-package ambiguity:
two tests import helpers as `tests.*`, which resolves to Ultralytics'
site-packages package when it is installed. This documentation-only OCID change
did not cause the failure; the packaging prerequisite is tracked separately
before model-inference claims are recorded.

## Handoff

Person 4 reviews the contract-reader evidence. Person 1 may then use the same
external recorded frames for issue #84's pinned MiDaS v3.1 execution check.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/81
- Pull request: Pending
- Commit: Pending
