# Person 3 Status — Tracking, Proximity, and Alert Rules

- **Status:** In progress
- **Last updated:** 2026-09-08

## Implemented

Person 3 owns the tracking, shelf-proximity, and removal-alert rule layer.

Implemented and verified:

- deterministic replay tracking through `ReplayTracker`
- reconstruction of `PersonTrack` objects from scenario annotations
- shelf proximity calculation using metric 3D position and shelf AABB geometry
- `last_near_timestamp_ns` tracking
- bounding-box-based person occlusion masks
- deterministic removal-alert association
- two-second person/removal association window
- newest eligible person-track selection
- authorized-person suppression
- `RESTOCK_MODE` suppression
- minimum missing-volume threshold
- deterministic alert IDs
- frozen rule version `P3-001`
- empty-pose normalization for replay tracks
- serialized `PersonTrack` and `AlertEvent` evidence
- deterministic synthetic Gate 4 evidence generation (`scripts/generate_person3_gate4_evidence.py`)
- SHA-256 evidence manifest
- lazy optional pretrained tracking adapter
  (`LazyUltralyticsTrackingProvider` in `src/kyra/adapters.py`, issue #72):
  YOLO + ByteTrack under `requirements-gpu.lock`; heavy dependencies are
  loaded only at first `track()` call, and a clear error is raised when the
  tracking extras are absent (deterministic core unaffected, D-001/D-002)
- fail-closed metric RGB-D localization of pretrained person boxes, including
  camera-to-shelf transformation and the existing proximity-history update
  (issue #93)

## Active

Issue #85 merged through pull request #91. Real YOLO11n and ByteTrack CPU
execution passed on an official positive-control image and four two-frame OCID
samples. Issue #93 adds metric RGB-D localization, shelf-frame positioning,
and proximity state to those detected boxes. Its focused tests pass and its
external smoke report is checksum-identified below.

Person 3 remains in progress because the positive localization smoke combines
recorded RGB with constructed flat depth. OCID contributes real RGB-D but no
people. A representative person-plus-shelf RGB-D sequence and the model-backed
full pipeline integration in issue #94 remain pending.

## Blocked or pending

Gate 4 exit criteria are compiled in `docs/gates/GATE-4.md` (record under Person 4 review). The following integration-level items remain outside the owner's deterministic evidence but are tracked:

- model-backed detector/tracker use in the P4 prerecorded scenario runner
- representative real person-plus-shelf RGB-D validation
- upstream volume-change integration (real `VolumeChangeEvent` chain from Person 2's `ShelfGeometryProvider`, replacing the synthetic events used in evidence)
- required cross-owner Gate 4 validation and approvals

## Next

- Merge issue #93, then complete Person 4 issue #94 so prerecorded scenarios
  may use pretrained tracking without saved track annotations.
- Acquire or record representative synchronized RGB-D shelf interactions before
  making recall or false-positive claims.

## Evidence

- Evidence generator: `scripts/generate_person3_gate4_evidence.py` (integrated via pull request #70, commit `0452c2e`).
- Generated evidence directory: `evidence/person3-gate4/` (git-ignored by design; the reproducible generator is committed instead).
- Evidence includes `person3-track-001.json`, `person3-alert-001.json`, `person3-gate4-matrix.json`, the deterministic scenario, and `SHA256SUMS.txt`.

Representative deterministic outcome (frozen environment, 2026-09-09):

- Track ID: `7`; near shelf: `True`; last near timestamp: `2000000000 ns`
- Alert ID: `alert-p3-g4-removal-001-track-7`; rule version: `P3-001`
- Matrix cases: eligible-removal -> alert; authorized-person, restock-mode, below-minimum-volume, outside-two-second-window, addition-direction -> no alert (all asserted)

Merged-tree verification (Windows, Python 3.12.7, requirements.lock pins):

- Person 1/2/3/4 full repository suite: 195 passed
- Ruff, byte-compilation, repository-consistency, and change-impact checks passed
- Evidence generator rerun produced an identical SHA-256 manifest (deterministic regeneration)

Issue #93 evidence (Windows, Python 3.12.7, CPU):

- focused metric localization tests: 6 passed
- report: `C:\KyraData\model-smoke\yolo\yolo_bytetrack_rgbd_localization_report.json`
- report SHA-256: `af43048f3e0ad16f9a73f969df7a570ec7a31e5ca1e297fd9b12a13825354de6`
- recorded positive RGB: 8 localized tracks, IDs 1 through 4 persisted across
  both repeated frames; constructed flat depth was used
- four OCID RGB-D pairs: zero person tracks because OCID contains no people

Configuration and contract versions:

- runtime schema version: `1.0`
- scenario manifest version: `1.1`
- Person 3 rule version: `P3-001`
- association window: `2 seconds`
- minimum alert volume: `5e-5 m³`
- shelf proximity threshold: `1.0 m`

Limitations:

- the integrated pipeline still defaults to deterministic scenario annotations;
  optional pretrained runner integration is tracked by issue #94
- box localization uses inner-box median depth rather than instance
  segmentation, so its metric position can include background or carried items
- person occlusion is currently represented using track bounding boxes rather than instance segmentation
- the removal alert is a human-review signal and does not establish theft, intent, or identity
- the two-second association window is fixed by the current rule configuration
- synthetic evidence is representative component evidence and is not production deployment validation
- the Gate 4 matrix uses synthetic `VolumeChangeEvent` inputs; the real Person 2 -> Person 3 chain is validated at Gate 5
- the YOLO11n adapter emits empty pose keypoints; issue #93 adds metric position
  and shelf proximity only when aligned depth has enough valid samples
- the positive-control localization depth is constructed, while OCID has real
  depth but no people; neither is representative end-to-end validation
