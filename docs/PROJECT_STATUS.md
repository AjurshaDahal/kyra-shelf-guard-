# Project Status

- **Snapshot date:** 2026-09-08
- **Verified baseline commit:** `2b4dbba`
- **Verified collaboration foundation commit:** `dd9885f`
- **Latest shared commit reviewed for this correction:** `e755c04`
- **Latest verified local environment:** Windows, Python 3.12.7
- **Latest verified checks:** See owner status and work-item records for dated,
  per-change evidence; do not infer a current total from an older test count.
- **End-to-end status:** Deterministic generated/replay vertical slice
  demonstrated. Full pretrained-model execution on representative RGB-D shelf
  activity is not yet demonstrated.
- **Target T4 status:** Core suite, Person 1 verifier, and golden-pack audit ran
  on a Kaggle free-T4 notebook on 2026-09-07. YOLO and MiDaS were not run
  together through the complete pipeline, and target latency remains open.

This is the integration snapshot. Detailed owner progress and next actions live
in the linked status files; per-change history lives in `docs/work-items/`.

## Workstreams

| ID | Owner | Status | Implemented truth | Next gate-bound outcome | Detail |
|---|---|---|---|---|---|
| P1 | Person 1 | Complete for current component scope | Contracts, strict manifests, replay, baseline persistence, MiDaS anchor alignment, deterministic generation, golden pack, OCID conversion, and 8-manifest/168-frame OCID replay | Representative shelf-activity recordings remain an integration/evaluation need | [P1 status](status/PERSON1.md) |
| P2 | Person 2 | Complete for current component scope | Registration, signed depth difference, occlusion safety, clustering, volume, temporal state, and camera-drift suppression | Validate geometry on representative shelf-removal recordings | [P2 status](status/PERSON2.md) |
| P3 | Person 3 | In progress | Replay tracking, proximity/rules, masks, and a real recorded-image YOLO+ByteTrack CPU smoke | Convert RGB-D detections to metric shelf positions and use them in the integrated pipeline | [P3 status](status/PERSON3.md) |
| P4 | Person 4 | In progress | Shared contracts/tools, deterministic vertical slice, CLI/demo, generated evaluation runner, and partial release preparation | Run and evaluate the model-backed prerecorded path; close Gates 6–7 only with representative evidence | [P4 status](status/PERSON4.md) |

## Integration gates

| Gate | Status | Current evidence or blocker |
|---|---|---|
| G1 — Contract compatibility | Complete | C-001–C-007 are approved/frozen; compatibility and deterministic mock evidence are recorded in `docs/gates/GATE-1.md`. |
| G2 — Data and baseline | Complete | Deterministic generation, golden pack, baseline builder, provenance, bounded OCID replay, and core T4 checks are recorded in `docs/gates/GATE-2.md`. |
| G3 — Geometry | Complete | Registration, differencing, occlusion safety, clustering, volume, temporal state, and drift suppression are recorded in `docs/gates/GATE-3.md`. |
| G4 — Tracking and rules | In progress | Deterministic replay evidence and a real YOLO+ByteTrack CPU smoke exist. Metric RGB-D localization, shelf proximity, and integrated pretrained execution remain absent. |
| G5 — Complete vertical pipeline | Complete for deterministic replay scope | The generated P1→P2→P3→P4 replay path and CLI are verified in `docs/gates/GATE-5.md`; this is not a model-backed or real-use-case closure. |
| G6 — Frozen evaluation | In progress | The 420 results are generated-fixture regression evidence, not an independently frozen representative dataset or an executed class-based comparison (`docs/gates/GATE-6.md`). |
| G7 — Performance and release | In progress | Core T4 and local release-preparation checks exist; full YOLO+MiDaS T4 execution, target latency, representative evaluation, and independent sign-off remain open (`docs/gates/GATE-7.md`). |

Gate exit criteria are authoritative in [Integration Gates](INTEGRATION_GATES.md).
Only Person 4 changes a gate to `Complete`, and only with linked evidence from
every named owner.

## Active cross-team decisions and blockers

- D-014 approves OCID CC-BY 4.0 research use, and D-015 selects the Kaggle
  free-T4 notebook as the target runner. These decisions do not themselves
  prove representative evaluation or model-backed T4 execution.
- OCID replay provides real RGB-D sensor input but no people/removal activity,
  so it cannot establish alert recall or person-proximity behavior.
- A representative RGB-D recording set with people, shelf removals, restocking,
  occlusion, and negatives is not currently available locally.
- The independent Person 1 handoff sign-off remains open and requires a human
  teammate or instructor.
- Person 1–4 GitHub handles/reviewer assignments remain unknown, and the current
  private-repository plan does not enforce branch protection server-side.

See [Decisions](DECISIONS.md) for full text. Do not implement around a pending
decision by creating a second informal interface.
