# Gate 7 Evidence — Performance and Release Preparation

- **Gate:** Gate 7 (Performance and Release)
- **Accountable owner:** Person 4 (Integration and Release)
- **Date recorded:** 2026-09-08
- **Corrected:** 2026-09-08 under issue #92
- **Status:** In progress; partial release evidence only

## Verified evidence

- The committed core test suite, Person 1 verifier, and golden-pack audit ran in
  a Kaggle free-T4 notebook. The detailed boundary and artifact limitation are
  recorded in `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md`.
- Six deterministic CLI commands (`simulate`, `calibrate`, `run`, `evaluate`,
  `benchmark`, and `demo`) completed in the recorded local smoke environment.
- The golden pack was byte-identical across the recorded Windows and Linux/T4
  checks.
- The repository licence, external-data provenance policy, indexed-file secret
  scan, and alert terminology were reviewed.
- The deterministic CPU fixture runner recorded p50 191.85 ms and p95 286.52 ms.

## What the evidence does not establish

- YOLO and MiDaS were not executed together through the complete pipeline on
  the T4.
- The assignment's less-than-150-ms model-backed end-to-end latency target was
  not measured or met by the recorded CPU fixture timing.
- The T4 report does not contain representative people-plus-shelf-removal or
  restocking recordings.
- The optional tracking dependency pins do not prove GPU execution.
- Independent owner/reviewer release sign-off is not recorded.
- Gate 6 remains open, so the release cannot claim assignment-level accuracy,
  generalization, or full production readiness.

## Remaining exit evidence

1. Run the actual pretrained tracking/depth path with geometry and alert logic
   on a T4 and retain stage plus end-to-end timings.
2. Evaluate representative frozen RGB-D recordings and publish reproducible
   failure analysis.
3. Re-run clean-environment checks from the intended release revision.
4. Obtain the required independent sign-offs and record the release revision.

## Gate 7 conclusion

The project has useful core portability and release-preparation evidence, but
Gate 7 remains **in progress**. The current record does not support saying that
all deliverables, target latency, or production readiness are complete.
