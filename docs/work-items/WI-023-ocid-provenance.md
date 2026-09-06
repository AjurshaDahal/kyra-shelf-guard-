# WI-023 — Provenance record and OCID conversion path

- **Owner:** P1
- **Status:** In review (local implementation complete; pending push/review)
- **Started:** 2026-09-06
- **Completed:** N/A
- **Requirements:** P1-09, P1-10; P1-DATA-001, P1-DATA-002, P1-DATA-003
- **Integration gate:** Gate 2

## Objective

Add a validated provenance record that fully documents the OCID source
(licence, attribution, checksum state, selection, exclusions, conversion
command), plus the pure OCID conversion mapping (depth scale, masks, frame
order, calibration, addition-to-removal reversal) with a tiny committed fixture
that converts offline and replays through `ScenarioFrameSource`.

## In scope

- `src/kyra/ocid.py` — metadata parsing, depth/mask mapping, event derivation,
  reversal, canonical layout writer, SHA-256 helper.
- `tests/fixtures/ocid-mini/` — 16x16 deterministic OCID-style sequence
  (3 frames: empty, cup appears, cup present), 10 files, about 1.4 KB.
- `tests/test_ocid.py` — 13 tests.
- `data-sources/provenance.json` + `data-sources/README.md`.
- `tests/test_dataset_provenance.py` — 8 tests.
- `scripts/convert_ocid.py` — implemented locally; NOT pushed with this issue.

## Out of scope

- Downloading or committing the real OCID archive (about 6.4 GiB) or bulk
  converted data; the recorded external smoke test stays pending retrieval.
- Frozen/golden claims, BlenderProc, verification script, target-T4 evidence,
  shared-contract changes, and Gate 2 completion.
- Other owners' algorithms; no Person 2/3/4 files touched.

## Inputs, outputs, and contracts

Consumes frozen `ShelfConfigRecord` (C-007), manifest 1.1 writer (C-006), and
`ScenarioFrameSource` (C-001-adjacent replay). Output uses `SourceType.PUBLIC_RGBD`
and `evidence_source="public_rgbd"`. Depth stays uint16 millimetres on disk and
unknown depth stays unknown; frame order and calibration are preserved; reversal
creates monotonic nanosecond timestamps and flips the expected event while
keeping provenance notes. `scripts/convert_ocid.py` is the documented
conversion command in the provenance record even though it is not yet pushed.

## Implementation summary

`kyra.ocid.parse_sequence_metadata` strictly validates OCID-style TOML (camera
fields, positive dimensions, unique frame ids). `ocid_depth_to_mm` maps raw
units through the archive depth scale to uint16 millimetres and rejects values
that cannot be represented, keeping raw-zero as unknown. `valid_mask` and
`object_mask` produce 0/255 masks. `derive_events` reports windowed
addition/removal transitions and treats the first frame as initial state (a
sequence that starts with an object does not invent an addition). Category
strings map to `ShapeFamily` with an explicit fallback. `write_converted_sequence`
writes the canonical layout (rgb/, depth/, masks/, scenario.json), assigns
monotonic timestamps in output order, derives events in output space, and for a
removal frame writes an object mask marking the last-seen object region carried
from the immediately preceding frame (required by the manifest 1.1 validator
and recorded in `notes`). `reverse=True` plays the sequence backwards, turning a
valid addition into a removal. `sha256_of_file` feeds the script's checksum
gate.

Two real defects were found and fixed during development rather than papered
over: (1) `cv2.imwrite` fails silently when the rgb/depth/masks subdirectories
do not exist, so the module now creates them; (2) events must be derived in
output order, otherwise a reversed removal's `first_seen` lands on the wrong
frame and the initial-state frame is misread as an addition.

## Documentation impact

- `CHANGELOG.md`: added P1-09/P1-10 entries and refreshed the known-gaps line.
- `docs/status/PERSON1.md`: moved P1-09/P1-10 into Implemented with evidence;
  documented the local-only script and filename deviations.
- `docs/PERSON1_IMPLEMENTATION_PLAN.md`: marked P1-09/P1-10 complete, recorded
  both deviations, and refreshed Wave 4 exit and the checkpoint.
- `docs/work-items/WI-023-ocid-provenance.md`: this record.
- `docs/DATASETS.md` already defines the provenance fields and OCID conversion
  rules, so its truth did not change. No decision, contract, testing-policy, or
  gate-completion change was made.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.7, repo root | `python -m pytest tests/test_ocid.py tests/test_dataset_provenance.py -q` | 21 passed in 0.41s | 2026-09-06 local run |
| Windows, Python 3.12.7, repo root | `python -m pytest -q` | 134 passed in 9.87s | 2026-09-06 local run |
| Windows, Python 3.12.7, repo root | `python -m ruff check .` | All checks passed | 2026-09-06 local run |
| Windows, Python 3.12.7, repo root | `python -m compileall -q src tests scripts` | exit 0 | 2026-09-06 local run |
| Windows, repository | `python scripts/check_repo_consistency.py` | passed | 2026-09-06 local run |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | passed for 18 changed files (script excluded by design) | 2026-09-06 local run |
| Windows, Python 3.12.7, local | `python scripts/convert_ocid.py ... --reverse` | exit 0; reversed removal replayed via ScenarioFrameSource; tampered checksum rejected with exit 2 | 2026-09-06 local-only run |

## Risks, limitations, and failures

- `scripts/convert_ocid.py` is not in this push: the change-impact classifier
  (issue #18) treats every `scripts/*.py` change as Person 4/governance. The
  script is reviewed and pushed with the classifier fix (same pattern as issue
  #17). The provenance record's `conversion_command` documents that path.
- The plan-named `tests/test_provenance.py` is delivered as
  `tests/test_dataset_provenance.py` for the same #18 reason; the deviation is
  recorded in the plan and this record.
- The real OCID archive has not been downloaded; `provenance.json` honestly
  records `pending_download`, and the licence review (P-003) must pass before
  download or redistribution.
- Event derivation requires the first frame to be the initial state; a removal
  that starts before the recorded window is not inventable and is not claimed.
- The `camera_to_shelf` transform is identity because OCID carries no shelf
  registration; downstream registration remains Person 2 scope.
- Evidence is synthetic and local; it does not close Gate 2, prove T4
  portability, or replace real-data smoke evidence.

## Handoff

- Next: review and merge of branch `p1/23-ocid-provenance` (owner: Person 1
  lead, reviewers per team roster), then P1-11 verification script.
- After issue #18 lands: merge the classifier fix into `p1/17` and push the
  golden-pack candidate; also push `scripts/convert_ocid.py` and the plan-named
  test renames for reconciliation.
- Dependencies: frozen C-006/C-007 on `origin/main`; Person 4 issue #18 for the
  local-only script push.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/23
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/24
- Commit: `0e4b619` (branch `p1/23-ocid-provenance`)