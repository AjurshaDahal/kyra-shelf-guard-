# WI-082 — Gate 6 Evaluation Machinery

## Owner

Person 4 — integration and evaluation.

## Scope

Prepare P4-owned deterministic Gate 6 evaluation machinery and a separate
multi-frame synthetic scoring split. Preserve G01-G10, C-001 through C-007,
and all P1/P2/P3 algorithms.

## Delivered preparation

- Added deterministic split loading and SHA-256 inventory validation.
- Added scenario-level event and alert scoring with aggregate TP/FP/FN,
  precision, recall, F1, and confusion matrices.
- Event TP now requires matching change type; event-presence metrics remain
  separately reported.
- Added applicable timing, volume, and bounds summaries.
- Added exact split metadata, frame-spacing, and index/manifest validation.
- Added explicit no/partial/all-threshold state reporting and portable output.
- Added explicit excluded-metric reporting.
- Added opt-in threshold configuration without approving numeric thresholds.
- Added the ten-category, multi-frame synthetic split generator and prepared
  checksumed fixture output.
- Extended `kyra evaluate` with `--split` while preserving single-manifest
  evaluation behavior.

## Explicit exclusions

- No P1/P2/P3 implementation changes.
- No frozen contract changes and no C-008.
- No public OCID evaluation, live tracker evaluation, or release validation.
- Gate 6 is not closed.

## Acceptance evidence

Focused and full validation commands/results are recorded after implementation.
Fixture contents and Gate 6 numeric acceptance thresholds require separate
owner approval before closure. The current report is
`evidence/gate6-evaluation.json`; its SHA-256 is
`9acf402768d274cc871b7aaf5fd712256879096e094e1429cf62c8e7b846a343`.
This report is synthetic vertical validation only and does not claim Section 10
final acceptance.
