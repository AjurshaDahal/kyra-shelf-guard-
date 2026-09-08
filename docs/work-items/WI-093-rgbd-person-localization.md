# WI-093 — Metric RGB-D localization for pretrained person tracks

- **Owner:** P3
- **Status:** Complete
- **Started:** 2026-09-08
- **Issue:** https://github.com/DontHash/kyra-shelf-guard/issues/93
- **Pull request:** https://github.com/DontHash/kyra-shelf-guard/pull/96

## Scope

Convert pretrained person detection boxes into metric shelf-frame positions
using aligned `FramePacket` depth and intrinsics, then apply the existing Person
3 proximity state. Extend the recorded YOLO smoke runner without changing
shared contracts C-001 through C-007.

## Implemented

- robust median depth from the inner portion of each person box
- metric camera back-projection and `camera_to_shelf` transformation
- fail-closed handling for invalid boxes, depth, intrinsics, or transforms
- continuing-track `last_near_timestamp_ns` preservation
- recorded-image YOLO smoke reporting for localized position and proximity

## Verification

- focused tests: 6 passed
- Ruff on changed Python surfaces: passed
- external report:
  `C:\KyraData\model-smoke\yolo\yolo_bytetrack_rgbd_localization_report.json`
- report SHA-256:
  `af43048f3e0ad16f9a73f969df7a570ec7a31e5ca1e297fd9b12a13825354de6`

- full repository suite: 257 passed in 91.56 seconds
- full Ruff check: passed
- byte compilation: passed
- repository consistency: passed
- change-impact validation against `origin/main`: passed

## Claim boundary

The positive-control RGB is recorded, but its metric depth is constructed. The
OCID samples contain real metric RGB-D but no people and produced zero tracks.
The method uses a bounding-box depth statistic rather than person segmentation.
This work does not prove real person-plus-shelf RGB-D localization accuracy,
model-backed alert integration, target-T4 latency, recall, false-positive rate,
theft, or intent.

## Next exact action

Complete Person 4 issue #94 by making the prerecorded scenario runner
optionally consume pretrained tracks, this localization result, aligned person
masks, Person 2 geometry, and Person 3 rules without saved track annotations.
