# WI-021 — Harden baseline calibration, known-volume acceptance, and MiDaS policy

- **Owner:** P1
- **Status:** In review (local implementation complete; pending push/review)
- **Started:** 2026-09-06
- **Completed:** N/A
- **Requirements:** P1-06, P1-07, P1-08; P1-CAL-001..005, P1-MIDAS-001..002
- **Integration gate:** Gate 2

## Objective

Harden the baseline calibration/persistence code with focused gap tests, add a
known-volume acceptance suite where every accepted synthetic case (at least
0.5 litres, varied position and supported floor-sitting shape families) is
within 10% of ground truth, and complete the MiDaS alignment policy matrix
without changing any shared contract.

## In scope

- `tests/test_baseline.py` growth (P1-06 gap tests, P1-08 MiDaS policy tests).
- New `tests/acceptance/test_baseline_volume.py` (P1-07 known-volume acceptance).
- `src/kyra/baseline.py` corrections only where tests expose a real gap; none
  were needed, so the module is unchanged.

## Out of scope

- Shared contract/schema changes (frozen C-001..C-007 surfaces only consumed).
- Person 2 geometry/volume, Person 3 alerts, Person 4 pipeline/evaluation.
- OCID converter, provenance record, BlenderProc, verification script, T4
  evidence, and frozen-pack claims (issues #17, #18, and later P1 work items).
- Hanging/handled objects as accepted volume cases: the baseline estimator
  integrates the void column under a hanging object, so those cases exceed the
  10% bound by design and are recorded as Person 2 occlusion-safe geometry
  scope.

## Inputs, outputs, and contracts

Consumes `ShelfConfig`, `FramePacket`, `BaselineArtifact`, `PortableComponent`,
and `SourceType` exactly as frozen. Depth stays `float32` metres in memory;
unknown depth stays zero/NaN-flagged. No manifest, schema, coordinate-frame,
unit, or compatibility behavior changed.

## Implementation summary

P1-06 added eight focused calibration/persistence tests: mixed-resolution and
changed-intrinsics frame batches reject; unsafe occupancy-grid dimensions
reject; an empty shelf is entirely fixed geometry with zero portable
components; injected per-pixel jitter raises the noise sigma above the 1 mm
floor; the calibration checksum changes with shelf configuration and with
median-affecting depth content, stays identical across repetitions, and — as a
documented robustness property — absorbs a single-frame outlier pixel.
P1-07 added the `tests/acceptance/` known-volume matrix (7 parametrized cases:
12x12, 14x14, 16x10, and 18x18 boxes; radius-7 and radius-9 cylinders; an
8-px-arm irregular L union; top depths 0.94-0.97 m on a 1.0 m plane;
0.55-1.72 litres; seeds 101-107), where the exact estimator model error is
1.9-6.5% and every case passes the 10% bound, plus a hanging-plate guard case
(seed 201) that proves the suite is not vacuous by recording the expected
>10% void-column overestimate. P1-08 added the remaining MiDaS policy tests:
`SourceType.MIDAS_ALIGNED` frames label the artifact `approximate_metric=True`
and synthetic frames label it False; the flag survives a save/load round trip
in both NPZ metadata JSON and the artifact; `align` maps negative and NaN
relative inverses to zero (unknown) while preserving finite positive depth;
and the `maximum_residual_m` limit is explicit — the same mildly inconsistent
anchor set rejects at 0.001 m and accepts at 0.5 m. No `baseline.py` gap was
observed; the module landed unchanged.

Plan deviation, recorded per the issue: P1-08's plan name
`tests/test_midas_alignment.py` was not used. The current change-impact
classifier (issue #18) would classify that filename as Person 4, so the MiDaS
policy tests remain in `tests/test_baseline.py`, which already owns the MiDaS
rejection matrix and classifies as Person 1. The plan file records this
deviation for later reconciliation when the classifier fix lands.

## Documentation impact

- `CHANGELOG.md`: added P1-06/P1-07/P1-08 entries; corrected the stale known
  gap that claimed the deterministic generator was unimplemented.
- `docs/status/PERSON1.md`: moved P1-06/P1-07/P1-08 into Implemented with
  dated evidence; documented the handled/hanging limitation.
- `docs/PERSON1_IMPLEMENTATION_PLAN.md`: marked P1-06/P1-07/P1-08 complete,
  recorded the midas-test-filename deviation, and refreshed the checkpoint.
- `docs/work-items/WI-021-calibration-baseline-acceptance.md`: this record.
- No decision, contract, dataset, architecture, testing-policy, or
  gate-completion truth changed; `docs/TESTING.md` and `docs/DECISIONS.md` are
  intentionally untouched.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.7, repo root | `python -m pytest tests/test_baseline.py tests/acceptance/test_baseline_volume.py -q` | 31 passed in 0.23 s | 2026-09-06 local run |
| Windows, Python 3.12.7, repo root | `python -m pytest -q` | 134 passed in 3.25 s | 2026-09-06 local run |
| Windows, Python 3.12.7, repo root | `python -m ruff check .` | All checks passed | 2026-09-06 local run |
| Windows, Python 3.12.7, repo root | `python -m compileall -q src tests scripts` | exit 0 | 2026-09-06 local run |
| Windows, Python 3.12.7, repo root | `python scripts/check_repo_consistency.py` | passed | 2026-09-06 local run |
| Windows, Python 3.12.7, repo root | `python scripts/check_change_impact.py --base origin/main` | passed | 2026-09-06 local run, with companions |

## Risks, limitations, and failures

- Two initially written tests failed because the expectations were wrong, not
  the code: an empty shelf is legitimately all-fixed geometry, and a
  single-frame outlier pixel is legitimately absorbed by the median fusion.
  Both tests now assert the intended behavior and document it.
- Handled/hanging objects cannot meet the 10% bound with the current baseline
  estimator (void-column overestimate). This is an explicit recorded
  limitation handed to Person 2's occlusion-safe volume scope; the guard test
  keeps the failure visible if the estimator ever starts accepting it.
- Acceptance cases are floor-sitting and flat-topped by design; the suite does
  not cover slanted or curved-surface objects.
- Evidence is synthetic and local; it does not close Gate 2, freeze anything,
  or replace target-T4 evidence.

## Handoff

- Next: review and merge of branch `p1/21-calibration-baseline-acceptance`
  into `main` (owner: Person 1 lead, reviewers per team roster).
- After merge: Person 1 proceeds to P1-09 provenance and P1-10 OCID converter;
  Person 4 issue #18 remains the gate for pushing issue #17's golden pack.
- Dependencies: none beyond frozen contracts on `origin/main`.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/21
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/22
- Commit: `67ef2d7` (branch `p1/21-calibration-baseline-acceptance`)