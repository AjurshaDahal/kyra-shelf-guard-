# Project Status

- **Snapshot date:** 2026-09-09
- **Verified baseline commit:** `2b4dbba`
- **Verified collaboration foundation commit:** `dd9885f`
- **Latest shared commit:** `d22dbf6`
- **Latest verified local environment:** Windows, Python 3.12.7
- **Latest verified local checks:** 222 tests passed on Python 3.12.7 on 2026-09-08 (dated total; see the owner status files and work-item records for per-change evidence)
- **Latest verified hosted checks:** Core CI passed on Python 3.11 and 3.12 (latest main run for PR #73: 34118684569); dependency graph reports zero open alerts
- **End-to-end status:** Demonstrated (Gate 5 vertical pipeline, Gate 6 frozen evaluation, and Gate 7 release sign-off complete)
- **Target T4 status:** Suite, verifier, and golden-pack audit executed on a Kaggle free-T4 GPU notebook 2026-09-07 (D-015; report `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md`); independent handoff sign-off pending (issue #59)

This is the integration snapshot. Detailed owner progress and next actions live in the linked status files; per-change history lives in `docs/work-items/`.

## Workstreams

| ID | Owner | Status | Implemented truth | Next gate-bound outcome | Detail |
|---|---|---|---|---|---|
| P1 | Person 1 | Complete | Contracts foundation, strict manifest, replay reader, baseline build/persistence, MiDaS anchor alignment, deterministic generator, frozen golden pack (D-009), OCID converter, and a verified 8-scenario/168-frame real OCID replay (`docs/gates/GATE-2.md`) | Gate 2 complete; recorded OCID input available for bounded model checks | [P1 status](status/PERSON1.md) |
| P2 | Person 2 | Complete | Registration, signed diff (3σ), occlusion safety, 3D clustering, ray volume, temporal engine, ShelfGeometryProvider, and Issue #79 camera drift fix merged (`docs/gates/GATE-3.md`) | Gate 3 complete; geometry ready for Gate 6 | [P2 status](status/PERSON2.md) |
| P3 | Person 3 | Complete | Deterministic replay tracking, proximity, occlusion masking, removal-alert rules, Gate 4 evidence record, and lazy tracking adapter merged (`docs/gates/GATE-4.md`) | Gate 4 complete; tracking ready for Gate 6 | [P3 status](status/PERSON3.md) |
| P4 | Person 4 | Complete | Gate 1 through 7 complete; vertical scenario pipeline, CLI commands, visual demo, 420-trial evaluation, and Gate 7 release verified (`docs/gates/GATE-7.md`) | All 4 workstreams complete; production ready | [P4 status](status/PERSON4.md) |

## Integration gates

| Gate | Status | Current evidence or blocker |
|---|---|---|
| G1 — Contract compatibility | Complete | C-001–C-007 are approved/frozen; contract compatibility tests and deterministic Person 4 mocks satisfy the Gate 1 exit criteria (`docs/gates/GATE-1.md`). |
| G2 — Data and baseline | Complete | Deterministic generator, frozen golden pack (D-009), 30-frame baseline builder, volume benchmark, MiDaS policy, provenance record, and Kaggle T4 report verified; evidence record `docs/gates/GATE-2.md`. |
| G3 — Geometry | Complete | Person 2 registration, 3σ differencing, occlusion safety, 3D clustering, volume, temporal engine, and Issue #79 camera drift fix verified; evidence record `docs/gates/GATE-3.md`. |
| G4 — Tracking and rules | Complete | Deterministic matrix + serialized `PersonTrack`/`AlertEvent` evidence (`docs/gates/GATE-4.md`, #70) and lazy optional pretrained adapter (#73) merged. |
| G5 — Complete vertical pipeline | Complete | P1→P2→P3→P4 deterministic scenario pipeline, 5 CLI commands, `kyra demo` video generator, and full test suite (217 tests) passing; evidence record `docs/gates/GATE-5.md`. |
| G6 — Frozen evaluation | Complete | 420-trial evaluation executed without test-set tuning (100% recall, 0% FPR, 100% geometry accuracy, 0% volume MAPE, 4.95 FPS); evidence record `docs/gates/GATE-6.md`. |
| G7 — Performance and release | Complete | Target-T4 validation, clean-clone 6-command smoke verification, licence/provenance audit, security check, and claims verification complete; evidence record `docs/gates/GATE-7.md`. |

Gate exit criteria are authoritative in [Integration Gates](INTEGRATION_GATES.md). Only Person 4 changes a gate to `Complete`, and only with linked evidence from every named owner.

## Active cross-team decisions/blockers

- D-014 (OCID licence, approved 2026-09-07) and D-015 (target-T4 runner =
  Kaggle free-T4 GPU notebook `notebooks/kyra_t4_validation.ipynb`, approved
  2026-09-07) resolved P-003 and P-004. The target-T4 run and the selected
  real OCID download/conversion/replay are complete; wider public-data
  evaluation remains separate from those smoke checks.
- The independent Person 1 handoff sign-off remains the only open Phase 0
  item; it needs a human teammate or instructor, not a decision.
- Person 1–4 GitHub handles and reviewer assignments are not yet known.
- The current GitHub plan does not support protected branches on this private
  repository; required checks and reviews are documented and automated but
  cannot yet be made server-enforced.
- WI-001 closed all six alerts from the first GitHub dependency scan. Optional Torch target-T4 validation remains separate and open for Gate 7.

See [Decisions](DECISIONS.md) for full text. Do not implement around a pending decision by creating a second informal interface.
