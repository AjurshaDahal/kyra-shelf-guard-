# WI-084 — Pinned MiDaS v3.1 on recorded OCID

- **Owner:** Person 1
- **Status:** In review
- **Started:** 2026-09-08
- **Requirement:** Objective 1 optional monocular-depth path
- **Integration gate:** Additional recorded-data evidence; no gate is closed

## Objective

Run a real pretrained MiDaS v3.1 model on checksum-identified OCID RGB through
an optional lazy adapter while preserving the boundary between relative model
output and calibrated metric depth.

## In scope

- `LazyMidasV31DepthEstimator` in `src/kyra/baseline.py`.
- Unit tests with injected model dependencies.
- Official model code pinned to commit `1645b7e1675301fdfac03640738fe5a6531e17d6`.
- `DPT_SwinV2_T_256` checkpoint execution on recorded OCID frames.
- External evidence containing source/checkpoint hashes and output statistics.

## Out of scope

- Live camera or RealSense input.
- T4 or latency acceptance.
- Metric-depth or volume accuracy from unaligned relative predictions.
- End-to-end suspicious shelf-removal alerts or claims about intent.
- Model weights, OCID data, and generated arrays in Git.

## Contracts

Consumes an RGB array from `FramePacket`. Produces only a two-dimensional
float32 relative inverse-depth array. Existing `MidasAnchorAligner` remains the
required boundary before metric geometry. No shared contract changes.

## Current evidence

- Focused injected-dependency tests: 27 baseline/MiDaS tests passed.
- First real load with `timm==1.0.19` failed because the published SwinV2
  checkpoint state dictionary does not match that newer parameter layout.
- The official MiDaS v3.1 environment pins `timm==0.6.12`, which fails its
  module import on Python 3.11+. Upstream 0.6.13 contains that dataclass fix
  and retains the required 0.6.x checkpoint layout.
- With `timm==0.6.13`, real pretrained inference completed on OCID
  `arid20-table-top-seq01-fwd/frame-000000`: finite 480x640 float32 relative
  inverse depth on CPU. This is model execution, not metric accuracy evidence.
- The bounded run completed on the first frame of four independent source
  sequences (`top/seq01`, `top/seq02`, `bottom/seq01`, `bottom/seq02`). All
  outputs were finite, contiguous 480x640 float32 arrays. Two sensor-depth
  anchors per frame also exercised the existing alignment boundary and marked
  every result approximate; with exactly two fitted points, the residual is
  not an independent accuracy statistic.
- External report:
  `C:\KyraData\model-smoke\midas\midas_ocid_smoke_report.json`, SHA-256
  `06259314dc4c585d2188b23d856b8e81af69604b97ab5e1b6f718246c0c7d27a`.
- Checkpoint SHA-256:
  `0a859caa18be4bf9375e87dc6b684f6e83dc45b2dc13d8c8b89f6acb2a17a2c5`.

## Acceptance checks

- At least one checksum-identified OCID frame completes real pretrained
  inference.
- Output is source-resolution, finite, contiguous, two-dimensional float32.
- Report repository revision, checkpoint/input hashes, dependencies, device,
  and output statistics outside Git.
- Focused and full tests, lint, byte-compilation, consistency, and
  change-impact checks pass.

## Verification

| Environment | Command | Result |
|---|---|---|
| Windows 11, Python 3.12.7, CPU Torch 2.14.0, timm 0.6.13 | real `DPT_SwinV2_T_256` smoke on four OCID source frames | 4/4 finite contiguous 480x640 float32 outputs; external report SHA-256 `06259314...d27a` |
| Windows 11, Python 3.12.7 | `python -m pytest tests/test_midas_inference.py tests/test_baseline.py tests/test_dataset_provenance.py -q` | 35 passed |
| Windows 11, Python 3.12.7 | `python -m pytest -q` | 250 passed in 175.30s |
| Windows 11, Python 3.12.7 | `python -m ruff check .` | passed |
| Windows 11, Python 3.12.7 | `python -m compileall -q src tests scripts` | passed |
| Windows repository | `python scripts/check_repo_consistency.py` | passed |
| Windows repository | `python scripts/check_change_impact.py --base origin/main` | passed for 13 changed files |

## Links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/84
