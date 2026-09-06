# Person 1 Test Report — Windows laptop, candidate pack

**Report status:** Pass with limitations
**Tester:** Person 1 implementation agent (automated runs, recorded verbatim)
**Date:** 2026-09-06
**Environment:** Windows laptop
**Independent tester:** No — the P1-13 independent teammate handoff is a
separate, not-yet-performed leg.

## Build identity

| Field | Recorded value |
|---|---|
| Git commit or source archive checksum | `422a841` on `p1/17-golden-scenario-pack` (contains `origin/main` `2082507` plus the merge and canonical-LF pack audit) |
| Golden-pack checksum | `checksums.sha256` SHA-256: `87D65FFD3ECD72D5C8499A794F300AD9E240DE87C87003733251100F8DA4F74B`; inventory covers 116 assets, 62,614 canonical-LF bytes (64,067 as checked out under `core.autocrlf=true`) |
| Python version | 3.12.7 |
| Dependency lock checksum | `requirements.lock` SHA-256: `9EB4D4F9A8C7DB2070F4C89C384BDB41440C3E5A1F176CBA04D2FFF531128640` |
| Operating system | Microsoft Windows 11 Home Single Language 10.0.26200 |
| CPU | 12th Gen Intel(R) Core(TM) i5-12450H |
| GPU and driver, if used | NVIDIA GeForce RTX 2050 — not used; the core suite is CPU-first by design |

## Commands and results

| Exact command | Exit code | Duration | Result or report path |
|---|---:|---:|---|
| `.venv\Scripts\python.exe -m pytest -q` | 0 | 4.73 s | 158 passed (includes 3 golden-pack tests) |
| `.venv\Scripts\python.exe -m ruff check .` | 0 | 0.13 s | All checks passed |
| `.venv\Scripts\python.exe -m compileall -q src tests scripts` | 0 | <1 s | No output |
| `.venv\Scripts\python.exe scripts\check_repo_consistency.py` | 0 | <1 s | Repository consistency check passed |
| `.venv\Scripts\python.exe scripts\verify_person1.py --golden scenario-fixtures\golden --provenance data-sources\provenance.json` | 0 | 0.08 s | All seven checks OK (pack present, schema, checksums, reader, baseline, MiDaS, provenance) |
| `.venv\Scripts\python.exe scripts\check_change_impact.py --base origin/main` | 1 | <1 s | Expected failure, issue #18: `scripts/generate_golden_pack.py` and `tests/test_golden_pack.py` classify as Person 4/governance; no false companions added |

## Acceptance results

| Requirement | Pass / Fail / Not run | Evidence or limitation |
|---|---|---|
| Same-seed byte-identical manifests | Pass | `tests/test_simulation.py` same-seed byte/hash comparisons; pack regeneration byte-identical to the recorded inventory |
| Ten scenarios load | Pass | `tests/test_golden_pack.py` replay + `verify_person1.py` reader check over all 117 pack assets |
| Baseline reloads without recomputation | Pass | `tests/test_baseline.py` round-trip with `BaselineBuilder.fit` monkeypatched to fail |
| Fixed shelf never portable | Pass | `tests/test_baseline.py` empty-shelf and fixed/portable separation tests |
| Under-0.5 m³ object classification | Pass | `tests/test_baseline.py` and volume acceptance suite |
| At least 0.5 L object volume error ≤10% | Pass | `tests/acceptance/test_baseline_volume.py` (7 cases; hanging-plate guard documents Person 2 scope) |
| MiDaS good and rejection cases | Pass | `tests/test_baseline.py` anchor matrix + aligner policy smoke in `verify_person1.py` |
| Provenance completeness | Pass | `tests/test_dataset_provenance.py` + `verify_person1.py` provenance check |
| Full Person 1 unit and contract suite | Pass | 158 tests, exit 0 |

## Golden scenarios

| ID | Loaded | Expected result matched | Notes |
|---|---|---|---|
| G01 | Yes | Yes | no-change |
| G02 | Yes | Yes | thin-item removal |
| G03 | Yes | Yes | irregular-item removal (D-009 provisional) |
| G04 | Yes | Yes | addition |
| G05 | Yes | Yes | person-only occlusion |
| G06 | Yes | Yes | removal then occlusion |
| G07 | Yes | Yes | authorized restocking |
| G08 | Yes | Yes | lighting variation |
| G09 | Yes | Yes | invalid-depth region |
| G10 | Yes | Yes | camera drift |

Expected-result matching is asserted by the pack behavior-matrix tests; the
pack remains a candidate and its checksums are not frozen evidence.

## Problems and exclusions

- The pack is a candidate, not frozen: D-009 team confirmation and the issue
  #18 classifier fix are still pending; this report must not be read as
  frozen-pack or Gate 2 evidence.
- Target T4 leg not run (G0.4 runner assignment is Person 4's; T4 access
  pending).
- Real OCID data leg not run (P-003 licence review pending; archive not
  downloaded).
- `scripts/verify_person1.py` and `scripts/convert_ocid.py` ran from the
  branch worktree and local file respectively; neither is pushed to `main`
  until issue #18 lands.
- The local RTX 2050 result is not a substitute for T4 evidence.

## Handoff decision

- [ ] Ready for Persons 2, 3, and 4.
- [x] Ready with the limitations listed above (candidate-input evidence only).
- [ ] Not ready; blocking items remain.

**Tester sign-off:** Person 1 implementation agent, 2026-09-06
**Receiving teammate sign-off:** pending (P1-13 independent handoff)