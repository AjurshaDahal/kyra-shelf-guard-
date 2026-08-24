# Project Status

- **Snapshot date:** 2026-08-24
- **Verified baseline commit:** `2b4dbba`
- **Verified collaboration foundation commit:** `87888db`
- **Latest verified local environment:** Windows, Python 3.12.7
- **Latest verified foundation checks:** 39 tests passed; Ruff, compileall, repository consistency, and change-impact checks passed
- **Latest verified hosted checks:** Core CI passed on Python 3.11 and 3.12 ([run 32758461898](https://github.com/DontHash/kyra-shelf-guard/actions/runs/32758461898))
- **End-to-end status:** Not demonstrated
- **Target T4 status:** Not run

This is the integration snapshot. Detailed owner progress and next actions live in the linked status files; per-change history lives in `docs/work-items/`.

## Workstreams

| ID | Owner | Status | Implemented truth | Next gate-bound outcome | Detail |
|---|---|---|---|---|---|
| P1 | Person 1 | In progress | Contracts foundation, strict manifest, replay reader, baseline build/persistence, MiDaS anchor alignment | Deterministic generator, golden pack, provenance converter, full P1 acceptance | [P1 status](status/PERSON1.md) |
| P2 | Person 2 | Not started | Shared `VolumeChangeEvent` type exists; no owned geometry implementation | Registration, signed change, occlusion-safe volume path | [P2 status](status/PERSON2.md) |
| P3 | Person 3 | Not started | Shared track/alert types exist; no owned tracking/rules implementation | Deterministic replay tracking and rule path | [P3 status](status/PERSON3.md) |
| P4 | Person 4 | In progress | Shared contract foundation, private GitHub remote, and machine-checked collaboration controls | Frozen contracts/mocks, pipeline, CLI, evaluation | [P4 status](status/PERSON4.md) |

## Integration gates

| Gate | Status | Current evidence or blocker |
|---|---|---|
| G1 — Contract compatibility | In progress | Foundation objects exist; package layout and manifest 1.1 proposal remain unresolved |
| G2 — Data and baseline | In progress | 35 local foundation tests; generator, golden pack, conversion, Windows/T4 handoff remain open |
| G3 — Geometry | Not started | Person 2 implementation and known-volume evidence absent |
| G4 — Tracking and rules | Not started | Person 3 implementation and deterministic rule evidence absent |
| G5 — Complete vertical pipeline | Blocked | Requires Gates 1–4 and Person 4 pipeline/CLI |
| G6 — Frozen evaluation | Blocked | Requires Gate 5 and frozen split/configuration |
| G7 — Performance and release | Blocked | Requires Gate 6, target-T4 evidence, report, and release review |

Gate exit criteria are authoritative in [Integration Gates](INTEGRATION_GATES.md). Only Person 4 changes a gate to `Complete`, and only with linked evidence from every named owner.

## Active cross-team decisions/blockers

- P-001: final package layout.
- P-003: dataset/asset/model licence compatibility for eventual distribution.
- P-004: target-T4 execution owner and evidence location.
- P-005: unapproved manifest object-mask/shape-family proposal.
- Person 1–4 GitHub handles and reviewer assignments are not yet known.
- The current GitHub plan does not support protected branches on this private repository; required checks and reviews are documented and automated but cannot yet be made server-enforced.

See [Decisions](DECISIONS.md) for full text. Do not implement around a pending decision by creating a second informal interface.
