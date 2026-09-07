# WI-077 — Deterministic Gate 5 scenario pipeline and CLI

- **Owner:** P4
- **Status:** In review
- **Started:** 2026-09-07
- **Completed:** N/A
- **Requirements:** assignment five-command interface; Gate 5 vertical pipeline
- **Integration gate:** Gate 5 candidate evidence; gate remains open

## Objective

Deliver the fastest defensible working product slice: join the real owner
components behind `simulate`, `calibrate`, `run`, `evaluate`, and `benchmark`,
and prove behavior with deterministic software test scenarios without claiming
real-world validation.

## Scope and ownership

- `src/kyra/pipeline.py`: P4 orchestration through P1 frame/baseline, P2
  geometry, and P3 replay/proximity/occlusion/rule implementations.
- `src/kyra/cli.py`: five commands and deterministic integration profiles.
- `src/kyra/simulator.py` and `src/kyra/simulator.html`: loopback-only visual
  reviewer over those profiles and the real integrated scenario path.
- `tests/test_vertical_pipeline.py`: end-to-end synthetic scenario matrix.
- `tests/test_simulator.py`: visual-review data and local HTTP API checks.
- P4 documentation/status/evidence corrections. No frozen contract changes and
  no owner algorithm is copied or modified.

## Acceptance results

The focused suite passes 13 tests covering suspicious removal, removal without
a person, person without removal, no change, addition, authorized restocking,
temporary occlusion followed by removal, removal outside the two-second
association window, duplicate suppression, invalid depth, ground-truth
isolation, the five commands, and benchmarking.

The `camera-drift` profile is a deliberately recorded failing evaluation:
expected no change, actual `REMOVAL`, no alert, exit 1. This is a Person 2
geometry blocker (#79), not something P4 suppresses after the fact.

The visual reviewer starts with `python -m kyra.simulator`, automatically runs
the suspicious-removal case, and exposes RGB/depth playback plus expected and
actual events/alerts for all ten profiles. Focused simulator and pipeline tests
pass 16 checks; interactive browser verification confirmed the default case
shows 37 frames, one removal, and one linked alert.

Full branch regression on Windows/Python 3.12.7: 215 tests passed; Ruff,
byte-compilation, repository consistency, and change-impact validation passed.

## Candidate smoke environment and commands

- Windows; Python 3.12.7; NumPy 2.4.6; OpenCV 5.0.0; Pydantic 2.13.5.
- CPU-only core environment; no network, CUDA, model download, or real dataset.

```powershell
python -m kyra.cli simulate evidence/gate5-77-final/suspicious-removal --case suspicious-removal --output evidence/gate5-77-final/simulate.json
python -m kyra.cli calibrate evidence/gate5-77-final/suspicious-removal/scenario.json --output evidence/gate5-77-final/baseline.npz --report evidence/gate5-77-final/calibrate.json
python -m kyra.cli run evidence/gate5-77-final/suspicious-removal/scenario.json --baseline evidence/gate5-77-final/baseline.npz --output evidence/gate5-77-final/run.json
python -m kyra.cli evaluate evidence/gate5-77-final/suspicious-removal/scenario.json --baseline evidence/gate5-77-final/baseline.npz --output evidence/gate5-77-final/evaluate.json
python -m kyra.cli benchmark evidence/gate5-77-final/suspicious-removal/scenario.json --baseline evidence/gate5-77-final/baseline.npz --runs 5 --output evidence/gate5-77-final/benchmark.json
```

Observed: one `REMOVAL`, one alert linked to the source volume event and track
1, evaluation passed, p50 28.1047 ms and p95 37.3485 ms over five runs.

## Checksums

| Artifact | SHA-256 |
|---|---|
| suspicious-removal `scenario.json` | `51372dc699ee0f9f53a6ca33b4243aaa0fd31bd333f6043ed0f1e254925f6380` |
| `baseline.npz` | `58b89cc331688df2608f44ec7b7184167e46b73be6cf3e9607fec71cd7a27cd8` |
| `baseline.json` | `9c5c442491120fc42a5ed55b52f14ad61db3c9d1e26fcedc0a1028df53a26eef` |
| `run.json` | `8cd0c2be86b2a92594f89a8de51ae2081a5bc5981beed1d9256d49079cd22056` |
| `evaluate.json` | `006cbd6691968e529431f180c6cf81e3778d4fc44ba86cee06809fec373b5a96` |
| `benchmark.json` | `f7e994435a60768700e7fbdc4d811ff0a4ad3a3ac25bea813304454932098dbb` |
| drift `scenario.json` | `2df54ed46c618e8b76899247082e654ed08d4847265931090a4fe6961e69d44b` |
| drift evaluation | `e63994faa46f5e466020090f14603f49469f4b8ddfaec299e3217e0974991569` |

Generated artifacts are git-ignored; this record, commands, tests, and hashes
are durable. Timing JSON is environment-specific rather than byte-stable proof.

## Gate decision and limits

This establishes a working synthetic candidate product slice. Gate 5 is not
Complete because Gate 2/3 entry conditions are open, drift fails, and all-owner
approval has not been collected. A formal `docs/gates/GATE-5.md` must not be
created until every exit criterion passes.

## Links

- Work item: https://github.com/DontHash/kyra-shelf-guard/issues/77
- Person 2 blocker: https://github.com/DontHash/kyra-shelf-guard/issues/79
