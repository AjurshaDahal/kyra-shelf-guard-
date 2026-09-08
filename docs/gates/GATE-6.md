# Gate 6 Evidence — Generated-Fixture Evaluation

- **Gate:** Gate 6 (Frozen Evaluation)
- **Accountable owner:** Person 4 (Integration and Evaluation)
- **Reviewers:** Person 1 (data split), Person 2 (geometry), Person 3 (rules)
- **Date recorded:** 2026-09-08
- **Corrected:** 2026-09-08 under issue #92
- **Status:** In progress; generated-fixture evidence only

## Scope

This record covers a deterministic generated-fixture exercise of the current
replay pipeline. It does not satisfy the assignment's staged real-use-case
dataset requirement and does not measure a class-based baseline, pretrained
inference, a live camera, or target-T4 model latency.

## Generated dataset

`scripts/evaluate_frozen_suite.py` creates every evaluated scenario on demand:

- 60 positive procedural scenarios carrying 20 category labels, with three
  variants per label. The labels alter generated metadata/shape families; they
  are not independently collected examples of 20 real product categories.
- 60 positive generated reverse-transition profiles whose names reference
  OCID. The runner does not load the OCID archive or converted OCID frames.
- 300 generated negative controls covering occlusion, nearby people without a
  removal, additions/authorized restocking, invalid depth, and drift/static
  cases.

All randomness is seeded. This supports repeatable software regression checks,
but it is not independent test-set evidence.

## Recorded generated-fixture results

| Metric | Assignment target | Generated-fixture result | Interpretation |
|---|---|---|---|
| Alert recall | >92% | 120/120 (100%) | Fixture regression only |
| False-alert rate | <1.1% | 0/300 (0%) | Fixture regression only |
| Geometry balanced accuracy | >90% | 100% | Fixture regression only |
| Volume MAPE for generated objects >=0.5 L | <=10% | 0% | Fixture regression only |
| Runner latency | <150 ms on T4 | p50 191.85 ms; p95 286.52 ms on recorded CPU run | Not model-backed or T4 evidence |

The exact values are retained because they are useful for catching code
regressions. They must not be presented as real-world accuracy or production
performance.

## Comparison boundary

The repository documents architectural differences between an item classifier
and the geometry path. It did not run a class-based YOLO accuracy baseline, so
there is no empirical comparison result. The 20 generated labels do not prove
generalization to 20 unseen real item categories.

## Evidence still required to close Gate 6

- An independently frozen, representative RGB-D set containing people,
  removals, restocking, occlusion, and no-change controls.
- Actual pretrained-model pipeline outputs on that set.
- An executed and documented class-based baseline if comparative accuracy is
  claimed.
- Failure analysis and reproducible recall/false-alert calculations on the
  representative set.

## Gate 6 conclusion

The generated matrix is strong deterministic regression evidence. Gate 6
remains **in progress** until representative independent data supports the
assignment-level accuracy and generalization claims.
