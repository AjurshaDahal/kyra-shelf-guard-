# WI-025 — Single Person 1 verification entry point

- **Owner:** P1
- **Status:** Complete (merged via PR #28 as `7f2fd84`)
- **Started:** 2026-09-06
- **Completed:** 2026-09-06
- **Requirements:** P1-11; P1-QA-002
- **Integration gate:** Gate 2

## Objective

One command that runs the Person 1 acceptance checks — manifest schema, golden
checksum, reader replay, baseline build, MiDaS policy, and provenance — with
clear per-check failure messages, collecting all failures, and exiting 0 only
when every check passes, without downloading anything.

## In scope

- `scripts/verify_person1.py` (the deliverable).
- Companion documentation for this work item.

## Out of scope

- P1-12 target/Windows validation reports and P1-13 handoff (later work items).
- Pipeline/CLI ownership (Person 4), downloads, contract changes, and golden
  pack composition itself (issue #17).

## Inputs, outputs, and contracts

Consumes `ScenarioManifest`/`load_manifest` (C-006), `ScenarioFrameSource`
(io), `BaselineBuilder`/`MidasAnchorAligner` (baseline), `ShelfConfig` (C-007
field set), `data-sources/provenance.json` (when present), and the golden pack
`checksums.sha256` inventory (when present). No manifest, schema, unit,
timestamp, or contract change.

## Implementation summary

The script runs seven named checks: golden pack presence, manifest schema,
golden checksums, reader replay, baseline build, MiDaS policy, and provenance
record. Check functions return collected error lists; `main` prints
`[OK]`/`[FAIL]` lines and exits 1 on any failure. When the golden pack is
absent, pack-dependent checks report "skipped: golden pack is absent" so the
run never passes vacuously (verified on the current `origin/main` tree: exit 1
with exactly the expected missing-pack/provenance failures). The MiDaS policy
check exercises the aligner on a tiny anchor matrix and asserts finite,
valid-only output; the provenance check mirrors the `test_dataset_provenance`
schema rules (required fields, known statuses, no private home path).

Two pack-layout facts were discovered and handled:

- The candidate golden pack declares one baseline marker frame per scenario
  (compact-fixture design; 2 frames total per scenario). The baseline check
  therefore builds with `minimum_frames=len(baseline_frames)` instead of the
  builder's 30-frame rule, which remains enforced by the baseline tests. The
  boot record documents this.
- The checksum inventory records the generator's LF output. Under
  `core.autocrlf=true` with no `.gitattributes` (current repository state), a
  Windows checkout delivers CRLF bytes for text assets, so raw-byte
  comparison would make the same pack fail on Windows and pass on T4. The
  verifier hashes text assets (.json/.toml/.sha256/.md/.txt) canonically by
  normalizing CRLF to LF; binary assets are hashed verbatim. A CRLF-mangled
  copy of the pack verifies identically to the LF tree.

## Documentation impact

- `CHANGELOG.md`: added the P1-11 entry and expanded the known-gaps line with
  the `scripts/verify_person1.py` push dependency and the pack inventory
  portability note.
- `docs/status/PERSON1.md`: recorded P1-11 implementation status, the
  verification evidence, and the push blocker.
- `docs/PERSON1_IMPLEMENTATION_PLAN.md`: marked P1-11 locally implemented with
  the proof command chain; Wave 5 checkpoint refreshed.
- `docs/work-items/WI-025-verify-person1.md`: this record.
- No decision, contract, dataset, testing-policy, or gate-completion change
  was made; `docs/DATASETS.md` truth is unchanged.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.7 | `python -m pytest -q` | 113 passed in 10.47s | 2026-09-06 local run |
| Windows, Python 3.12.7 | `python -m ruff check .` | All checks passed | 2026-09-06 local run |
| Windows, Python 3.12.7 | `python -m compileall -q src tests scripts` | exit 0 | 2026-09-06 local run |
| Windows, repository | `python scripts/check_repo_consistency.py` | passed | 2026-09-06 local run |
| Windows, Python 3.12.7 | `python scripts/verify_person1.py --golden <LF pack> --provenance <record>` | exit 0, all 7 checks OK | 2026-09-06, pack = regeneration of `p1/17` at `C:\Users\praka\AppData\Local\Temp\opencode\p117-wt\regenerated` (LF) |
| Windows, Python 3.12.7 | same command against a CRLF-mangled copy of the pack | exit 0, all 7 checks OK | 2026-09-06, simulates a Windows checkout under core.autocrlf=true |
| Windows, Python 3.12.7 | same command against origin/main tree | exit 1 with only the missing-pack and missing-provenance failures | 2026-09-06, proves no vacuous pass |
| Windows, Python 3.12.7 | negative control: tampered PNG + tampered JSON | exit 1; both files reported by checksums, reader, and baseline checks | 2026-09-06 local run |
| Windows, repository | `python scripts/check_change_impact.py --base origin/main` | intentional failure: `scripts/verify_person1.py` classifies as PERSON4/governance (issue #18) | 2026-09-06; push deferred |

## Risks, limitations, and failures

- Push blocker (known): issue #18 still classifies every `scripts/*.py`
  change as Person 4/governance; per the #17/#23 precedent this branch is
  committed locally and pushed when Person 4 lands the narrow classifier fix.
  No false Person 4 status or governance companions were added.
- The golden checks need the pack fixtures; they are only on branch
  `p1/17-golden-scenario-pack` until issue #17 merges. Green evidence above
  uses the byte-faithful regeneration of that pack in a temporary directory.
- Real finding for issue #17: `tests/test_golden_pack.py` compares raw bytes
  against the LF inventory, so after the pack merges, a Windows checkout
  under `core.autocrlf=true` (no `.gitattributes`) will fail that audit test.
  Recommended fix candidates: canonical-LF comparison in the pack audit test
  (P1-04 scope) or an approved `.gitattributes` eol policy (Person 4
  governance). The verifier already implements canonical-LF hashing so
  P1-QA-001's same-checksum claim is environment-neutral.
- The pack's one-frame baseline markers do not exercise the 30-frame fusion
  path; that path remains covered by `tests/test_baseline.py` and
  `tests/acceptance/test_baseline_volume.py`.
- Evidence is synthetic and local; it does not close Gate 2, prove T4
  portability, or replace the P1-12 reports.

## Handoff

- Next exact action: when issue #18 lands, push branch `p1/25-verify-person1`
  (contains the script and companions) and open the pull request against
  `origin/main`; its checks then run against the merged golden pack.
- For issue #17: apply the canonical-LF inventory comparison (or agree a
  `.gitattributes` policy with Person 4) before the pack is called frozen.
- Dependencies: Person 4 issue #18 (push), P1-04 merge (golden fixtures).

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/25
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/28
- Commit: `7f2fd84` (squash merge on `main`)