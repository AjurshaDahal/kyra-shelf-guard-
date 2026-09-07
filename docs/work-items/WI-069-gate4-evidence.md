# WI-069 — Gate 4 deterministic evidence generator and record

- **Owner:** P3
- **Status:** Complete
- **Started:** 2026-09-09
- **Completed:** 2026-09-09
- **Requirements:** Gate 4 exit criteria (deterministic replay, masks, proximity, authorization, window, matrix, serialized evidence)
- **Integration gate:** Gate 4 (evidence component; gate decision remains with Person 4)

## Objective

Land the deterministic Gate 4 evidence generator and status/record updates on
`main` via a clean integration, replacing the superseded `person3` branch
push (commits `de1c8d1`, `d3c709b` by @AjurshaDahal).

## In scope

- `scripts/generate_person3_gate4_evidence.py` (cherry-picked from
  `origin/person3`, authored 2026-09-09).
- `docs/status/PERSON3.md` (owner-status update to Complete with the
  integration-level blocked list; stale historical test counts replaced with
  merged-tree verification).
- `docs/gates/GATE-4.md` (evidence record: matrix, serialized hashes,
  environment, limitations; recorded per the docs/gates README convention).
- `docs/work-items/WI-069-gate4-evidence.md`, `CHANGELOG.md` entry.

## Out of scope

- Gate 4 closure in `docs/PROJECT_STATUS.md` (Person 4 decision after review).
- Live/pretrained tracker adapter, live detector integration, upstream
  depth/volume integration, and Gate 5 chain validation (tracked as blocked).

## Inputs, outputs, and contracts

No shared-contract changes. Evidence uses frozen C-003 `VolumeChangeEvent`,
C-004 `PersonTrack`, C-005 `AlertEvent`, manifest 1.1 reader, and rule version
`P3-001`. Generated evidence lives under git-ignored `evidence/`; the
committed generator reproduces it deterministically.

## Implementation summary

Cherry-picked the two new commits from `origin/person3` onto current `main`,
resolved the `docs/status/PERSON3.md` conflict by preserving the author's
new structure and correcting stale counts, and compiled the formal evidence
record from an actual frozen-environment run (matrix assertions passed;
twelve-file SHA-256 manifest identical across two runs).

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows, Python 3.12.7 (frozen lock) | `python scripts/generate_person3_gate4_evidence.py` | exit 0; matrix asserted; hashes stable |
| Windows, Python 3.12.7 | `python -m pytest -q` | 195 passed |
| Windows, Python 3.12.7 | `python -m ruff check .` | passed |
| Windows, Python 3.12.7 | `python -m compileall -q src tests scripts` | passed |
| Windows, repository | `python scripts/check_repo_consistency.py` | passed |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | passed with companions |

## Risks and limitations

- Synthetic `VolumeChangeEvent` inputs; real P2 -> P3 chain validation is a
  Gate 5 item.
- The optional pretrained adapter is unimplemented; its review decision
  belongs to Person 4.
- Evidence files are git-ignored; the generator + hashes in the record are
  the durable evidence.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/69
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/70
- Commit: `0452c2e` (squash merge on `main`)