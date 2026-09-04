# Person 3 Status — Tracking, Proximity, and Alert Logic

- **Status:** In progress
- **Last updated:** 2026-09-05

## Implemented

- Deterministic replay reconstruction of `PersonTrack`.
- Shelf proximity calculation from metric person position.
- Near-shelf timestamp tracking.
- Person bounding-box occlusion masking.
- Deterministic removal-alert association.
- Authorized-person filtering.
- Restock-mode alert suppression.
- Minimum removal-volume threshold handling.
- Replay annotations without pose keypoints are normalized to the shared
  `PersonTrack` empty-array shape.
- Person 3 integration and edge-case tests.

## Verification

- Original macOS full suite: `74 passed` before synchronization with current
  `main`.
- Windows/Python 3.12.7 clean-integration focused suite: `22 passed`.
- Windows/Python 3.12.7 clean-integration full suite: `105 passed`.
- Ruff, byte-compilation, repository-consistency, and change-impact checks
  passed; the impact validator accepted all 17 changed files.
- Clean integration pull request #19 passed Core CI on Python 3.11 and 3.12
  plus Pull Request Governance before merge.

## Active

- Live detector/tracker adapter and shared-runtime integration planning.

## Blocked or pending

- Live integration with the detector/tracker and upstream depth/volume stages.
- Full Gate 4 matrix and serialized evidence.

## Risks / assumptions

- Metric person position is supplied by the depth/3D stage.
- Proximity uses the configured metric distance threshold.
- Removal association uses a two-second temporal window.
- Occlusion currently uses person bounding boxes rather than segmentation.

## Next

Integrate with the live detector/tracker and coordinate with Persons 1, 2,
and 4 on the shared runtime pipeline.

## Evidence

- Person 3 implementation commit: `bd44222`.
- Ruff fix commit: `5e384b8`.
- Contributor pull request: `#12`, superseded by the clean integration.
- Merged clean integration pull request: `#19`; squash commit `5876649`.
- Issue: `#13` records branch synchronization and the empty-pose regression fix.
- Clean integration is based on `origin/main` at `eacb4cc` and contains no
  shared-contract diff.
- Windows/Python 3.12.7 focused suite: 22 passed; full suite: 105 passed.
