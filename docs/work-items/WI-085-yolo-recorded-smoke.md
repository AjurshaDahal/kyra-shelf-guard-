# WI-085 — Real YOLO11n and ByteTrack recorded-image smoke

- **Owner:** P3
- **Status:** In review
- **Started:** 2026-09-08
- **Issue:** https://github.com/DontHash/kyra-shelf-guard/issues/85
- **Pull request:** https://github.com/DontHash/kyra-shelf-guard/pull/91

## Checkpoint outcome

The existing adapter executed pinned YOLO11n detection and ByteTrack on CPU.
Two copies of official `bus.jpg` produced eight track records total, with IDs
1 through 4 present in both frames. Two frames from each of four OCID sequences
produced zero tracks. OCID has no person labels, so that is not accuracy or
false-positive evidence.

Real execution exposed two integration defects: Kyra RGB frames now cross the
Ultralytics NumPy boundary as contiguous BGR, and `lap==0.5.13` is pinned rather
than installed automatically during inference.

## External evidence

- Report: `C:\KyraData\model-smoke\yolo\yolo_bytetrack_smoke_report.json`
- Report SHA-256: `9209e2f06a3afd54b3c1ec17c75928a33a3567361737b33fa9dec7b113b0aaac`
- YOLO11n SHA-256: `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`
- Positive image SHA-256: `c02019c4979c191eb739ddd944445ef408dad5679acab6fd520ef9d434bfbc63`
- Environment: Windows 11, Python 3.12.7, Torch 2.14.0 CPU,
  Ultralytics 8.4.138, `cuda_available=false`

## Verification

- focused adapter and provenance tests: 11 passed
- real smoke runner: passed and wrote the checksum-identified report
- dependency integrity: `pip check` passed
- full repository tests: 246 passed in 79.21 seconds
- full Ruff check: passed
- byte compilation: passed
- repository consistency: passed
- change-impact validation against `origin/main`: passed

## Remaining outside this work item

- Pull-request review and merge.
- Clean-environment optional dependency installation proof.
- Target-T4, latency, pose, metric-position, proximity, and end-to-end alert
  validation under their respective integration work items.

## Claim boundary

This is real pretrained detector/tracker execution, not pose estimation,
metric positioning, shelf proximity, alert integration, live-camera evidence,
target-T4 evidence, latency measurement, recall/FPR evidence, or deployment
validation. It does not establish theft or intent.
