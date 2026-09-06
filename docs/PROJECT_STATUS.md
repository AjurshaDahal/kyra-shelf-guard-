# Project Status

- **Snapshot date:** 2026-09-06
- **Verified baseline commit:** `2b4dbba`
- **Verified collaboration foundation commit:** `dd9885f`
- **Latest shared commit:** `e37e729`
- **Latest verified local environment:** Windows, Python 3.12.7
- **Latest verified local checks:** 161 tests passed on Python 3.12.7 on 2026-09-06 (dated total; see the owner status files and work-item records for per-change evidence)
- **Latest verified hosted checks:** Core CI passed on Python 3.11 and 3.12 ([latest main run 34033069004](https://github.com/DontHash/kyra-shelf-guard/actions/runs/34033069004)); dependency graph reports zero open alerts
- **End-to-end status:** Not demonstrated
- **Target T4 status:** Not run

This is the integration snapshot. Detailed owner progress and next actions live in the linked status files; per-change history lives in `docs/work-items/`.

## Workstreams

| ID | Owner | Status | Implemented truth | Next gate-bound outcome | Detail |
|---|---|---|---|---|---|
| P1 | Person 1 | In progress | Contracts foundation, strict manifest, replay reader, baseline build/persistence, MiDaS anchor alignment, deterministic generator, candidate golden pack, OCID conversion path, verification entry point | Full P1 acceptance, D-009 freeze, Windows/T4 handoff | [P1 status](status/PERSON1.md) |
| P2 | Person 2 | Not started | Shared `VolumeChangeEvent` type exists; no owned geometry implementation | Registration, signed change, occlusion-safe volume path | [P2 status](status/PERSON2.md) |
| P3 | Person 3 | In progress | Deterministic replay tracking, proximity, occlusion masking, and removal-alert rules implemented and merged | Downstream validation against the shared golden/baseline evidence | [P3 status](status/PERSON3.md) |
| P4 | Person 4 | Complete | Gate 1 contract compatibility, mock providers, bounded pipeline, classifier fix (#18), and documentation reconciliation completed | Frozen pipeline/CLI/evaluation integration for Gates 5-7 | [P4 status](status/PERSON4.md) |

## Integration gates

| Gate | Status | Current evidence or blocker |
|---|---|---|
| G1 — Contract compatibility | Complete | C-001–C-007 are approved/frozen; contract compatibility tests and deterministic Person 4 mocks already satisfy the Gate 1 exit criteria for the shared compatibility layer. Real P1/P2/P3 algorithm outputs remain required for Gates 2–5. |
| G2 — Data and baseline | In progress | 161 dated local tests; deterministic generator, candidate golden pack, OCID conversion path, and verification entry point are merged; the D-009 freeze decision, Windows/T4 handoff, and the real-data OCID smoke test remain open |
| G3 — Geometry | Not started | Person 2 implementation and known-volume evidence absent |
| G4 — Tracking and rules | Not started | Person 3 implementation and deterministic rule evidence absent |
| G5 — Complete vertical pipeline | Blocked | Requires Gates 1–4 and Person 4 pipeline/CLI |
| G6 — Frozen evaluation | Blocked | Requires Gate 5 and frozen split/configuration |
| G7 — Performance and release | Blocked | Requires Gate 6, target-T4 evidence, report, and release review |

Gate exit criteria are authoritative in [Integration Gates](INTEGRATION_GATES.md). Only Person 4 changes a gate to `Complete`, and only with linked evidence from every named owner.

## Active cross-team decisions/blockers

- P-003: dataset/asset/model licence compatibility for eventual distribution.
- P-004: target-T4 execution owner and evidence location.
- P-005 is approved and confirmed as not affecting Person 2 or Person 3 runtime contracts; implementation remains open.
- Person 1–4 GitHub handles and reviewer assignments are not yet known.
- The current GitHub plan does not support protected branches on this private repository; required checks and reviews are documented and automated but cannot yet be made server-enforced.
- WI-001 closed all six alerts from the first GitHub dependency scan. Optional Torch target-T4 validation remains separate and open for Gate 7.

See [Decisions](DECISIONS.md) for full text. Do not implement around a pending decision by creating a second informal interface.
