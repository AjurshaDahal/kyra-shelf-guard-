# Project Status

- **Snapshot date:** 2026-09-09
- **Verified baseline commit:** `2b4dbba`
- **Verified collaboration foundation commit:** `dd9885f`
- **Latest shared commit:** `d22dbf6`
- **Latest verified local environment:** Windows, Python 3.12.7
- **Latest verified local checks:** 199 tests passed on Python 3.12.7 on 2026-09-09 (dated total; see the owner status files and work-item records for per-change evidence)
- **Latest verified hosted checks:** Core CI passed on Python 3.11 and 3.12 (latest main run for PR #73: 34118684569); dependency graph reports zero open alerts
- **End-to-end status:** Not demonstrated
- **Target T4 status:** Suite, verifier, and golden-pack audit executed on a Kaggle free-T4 GPU notebook 2026-09-07 (D-015; report `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md`); independent handoff sign-off pending (issue #59)

This is the integration snapshot. Detailed owner progress and next actions live in the linked status files; per-change history lives in `docs/work-items/`.

## Workstreams

| ID | Owner | Status | Implemented truth | Next gate-bound outcome | Detail |
|---|---|---|---|---|---|
| P1 | Person 1 | In progress | Contracts foundation, strict manifest, replay reader, baseline build/persistence, MiDaS anchor alignment, deterministic generator, candidate golden pack, OCID conversion path, verification entry point | Full P1 acceptance, D-009 freeze, Windows/T4 handoff | [P1 status](status/PERSON1.md) |
| P2 | Person 2 | In progress | Registration, signed diff (3σ), occlusion safety, 3D clustering, ray volume, temporal engine, and ShelfGeometryProvider implemented and merged (#51) | Gate 3 golden-pack evidence and real pipeline wiring | [P2 status](status/PERSON2.md) |
| P3 | Person 3 | Complete | Deterministic replay tracking, proximity, occlusion masking, removal-alert rules, and the Gate 4 evidence generator/record merged (#19, #70); evidence record `docs/gates/GATE-4.md` | Real P2→P3 chain validation and integration-level items (live adapter optional) at Gates 4–5 | [P3 status](status/PERSON3.md) |
| P4 | Person 4 | In progress | Gate 1 compatibility plus a candidate real-owner scenario pipeline and five-command CLI (#77) | Resolve the P2 camera-drift blocker (#79), collect owner approvals, and close Gate 5 | [P4 status](status/PERSON4.md) |

## Integration gates

| Gate | Status | Current evidence or blocker |
|---|---|---|
| G1 — Contract compatibility | Complete | C-001–C-007 are approved/frozen; contract compatibility tests and deterministic Person 4 mocks already satisfy the Gate 1 exit criteria for the shared compatibility layer. Real P1/P2/P3 algorithm outputs remain required for Gates 2–5. |
| G2 — Data and baseline | In progress | 189 dated local tests; deterministic generator, frozen golden pack (D-009 confirmed 2026-09-06), OCID conversion path, and verification entry point are merged; Windows/T4 handoff and the real-data OCID smoke test remain open |
| G3 — Geometry | In progress | Person 2 engine and fixture evidence exist, but P4 review found that the OCID-mini input is synthetic rather than real-sensor evidence and that persistent camera drift produces a false `REMOVAL` in full replay (#79) |
| G4 — Tracking and rules | Complete | Deterministic matrix + serialized `PersonTrack`/`AlertEvent` evidence (`docs/gates/GATE-4.md`, #70) and the lazy optional pretrained adapter (#73) merged; live T4 smoke of the adapter and the real P2→P3 chain remain Gate 5/7 exercises |
| G5 — Complete vertical pipeline | In progress | Candidate P1→P2→P3→P4 deterministic scenario pipeline and all five CLI commands implemented in #77; 13 focused tests cover the required alert/no-alert cases. Formal closure waits on G2/G3 prerequisites, camera-drift fix #79, and owner approvals. |
| G6 — Frozen evaluation | Blocked | Requires Gate 5 and frozen split/configuration |
| G7 — Performance and release | Blocked | Requires Gate 6, target-T4 evidence, report, and release review |

Gate exit criteria are authoritative in [Integration Gates](INTEGRATION_GATES.md). Only Person 4 changes a gate to `Complete`, and only with linked evidence from every named owner.

## Active cross-team decisions/blockers

- D-014 (OCID licence, approved 2026-09-07) and D-015 (target-T4 runner =
  Kaggle free-T4 GPU notebook `notebooks/kyra_t4_validation.ipynb`, approved
  2026-09-07) resolved P-003 and P-004; OCID download/conversion and the T4
  run itself remain open actions.
- The independent Person 1 handoff sign-off remains the only open Phase 0
  item; it needs a human teammate or instructor, not a decision.
- Person 1–4 GitHub handles and reviewer assignments are not yet known.
- The current GitHub plan does not support protected branches on this private
  repository; required checks and reviews are documented and automated but
  cannot yet be made server-enforced.
- WI-001 closed all six alerts from the first GitHub dependency scan. Optional Torch target-T4 validation remains separate and open for Gate 7.

See [Decisions](DECISIONS.md) for full text. Do not implement around a pending decision by creating a second informal interface.
