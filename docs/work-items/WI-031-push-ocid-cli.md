# WI-031 — Push OCID conversion CLI entry point

- **Owner:** P1
- **Status:** In review
- **Started:** 2026-09-06
- **Completed:** N/A
- **Requirements:** P1-10; P1-DATA-002
- **Integration gate:** Gate 2 (partial input only; gate remains open)

## Objective

Publish `scripts/convert_ocid.py`, the thin OCID conversion CLI that was
deliberately excluded from WI-023/PR #24 because issue #18 classified scripts
as Person 4 governance. The classifier fix (PR #29, `0b034c0`) makes the
script a Person 1 change, so it lands here with Person 1 companions only.

## In scope

- `scripts/convert_ocid.py` (fill existing reviewed content; no logic change).
- Companions: CHANGELOG, `docs/status/PERSON1.md`,
  `docs/PERSON1_IMPLEMENTATION_PLAN.md`, this record.

## Out of scope

- Real OCID download / the approved-external-sample smoke test (P-003 licence
  gate pending).
- Converter logic changes (`src/kyra/ocid.py` already merged in #24),
  shared contracts, D-009, P1-12/P1-13, dependabot bumps.

## Inputs, outputs, and contracts

Consumes the merged `kyra.ocid` module and frozen C-006/C-007 surfaces. Depth
units (uint16 mm on disk), nanosecond timestamps, masks, and unknown-depth
rules are unchanged.

## Implementation summary

The script performs filesystem discovery of `frame-*.color.png` assets, gates
the source `metadata.toml` by SHA-256 (case-insensitive comparison, exit 2 on
mismatch), parses the shelf configuration JSON into `ShelfConfigRecord`, and
calls `kyra.ocid` mapping functions to write the converted scenario plus
manifest. It exposes `--reverse` for addition-to-removal conversion and prints
the manifest SHA-256.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 | `python scripts/convert_ocid.py <mini> <out> --shelf <json> --expected-sha256 <ok> --reverse` | exit 0; 3 frames; removal-frame object mask replayed via ScenarioFrameSource |
| Windows, Python 3.12.7 | same with a wrong `--expected-sha256` | exit 2; mismatch message |
| Windows, Python 3.12.7 | `python -m pytest -q` | full suite result recorded below |
| Windows, Python 3.12.7 | `python -m ruff check .` / compileall / `check_repo_consistency.py` | recorded below |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | PASS (script classifies as Person 1 after PR #29) |

## Risks and limitations

- The script is only as good as its merged module; the real-OCID smoke test
  still needs P-003 approval and the archive download.
- `convert_ocid.py` remains the documented conversion command in the
  provenance record; pushing it does not change that record's pending status.

## Handoff

- After merge: only P1-12 (T4 leg), P1-13 (handoff), and the D-009 freeze
  decision remain for Person 1 completion.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/31
- Pull request: pending
- Commit: pending