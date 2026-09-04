# WI-007 — Person 3 Proximity, Occlusion, and Alert Logic

- **Owner:** P3
- **Status:** In review
- **Started:** 2026-08-30
- **Completed:** N/A
- **Requirements:** Person 3 proximity, occlusion masking, replay tracking, and removal-alert association
- **Integration gate:** Gate 4

## Objective

Implement the Person 3 runtime logic for reconstructing person tracks from
scenario annotations, determining shelf proximity, generating person
occlusion masks, and associating confirmed volume-removal events with the
most recent eligible nearby person.

## In scope

- Replay reconstruction of `PersonTrack` objects.
- Shelf proximity calculation using metric person position.
- Near-shelf timestamp tracking.
- Person bounding-box occlusion masks.
- Removal alert association with nearby non-authorized person tracks.
- Restock-mode suppression.
- Minimum missing-volume threshold handling.
- Deterministic edge-case and integration tests.

## Out of scope

- Person detection model training.
- YOLO inference or ByteTrack runtime integration.
- Depth estimation.
- Baseline construction.
- Volume differencing.
- Changes to the shared `PersonTrack`, `VolumeChangeEvent`, or `AlertEvent`
  public contracts.

## Inputs, outputs, and contracts

- Consumes the approved scenario `TrackAnnotation`, `PersonTrack`,
  `VolumeChangeEvent`, `ShelfConfig`, and system-mode meanings without changing
  their fields, units, timestamps, or coordinate frames.
- Produces existing `PersonTrack` and `AlertEvent` contracts.
- Treats absent pose annotations as a valid empty `(0, 3)` keypoint array.

## Implementation summary

Added Person 3 proximity, occlusion, replay-tracking, and alert-engine modules
under `src/kyra/`, together with focused unit, edge-case, and integration
tests.

The implementation:

- reconstructs deterministic person tracks from replay annotations;
- calculates shelf proximity from metric positions;
- records the timestamp when a person was last near the shelf;
- creates clipped person bounding-box occlusion masks;
- ignores authorized persons for suspicious shelf-removal association;
- associates removals with an eligible person within the two-second
  association window;
- suppresses alerts during restock mode;
- rejects removal events below the configured alert-volume threshold.

## Documentation impact

- `CHANGELOG.md` records the Person 3 behavior and empty-pose fix.
- `docs/status/PERSON3.md` records the in-review implementation truth and
  evidence boundary.
- WI-013 records the clean current-main integration and empty-pose repair that
  supersede pull request #12 for merge.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| macOS, Python 3.12 | `python -m pytest -q` | 74 passed | Full local test suite |
| macOS, Python 3.12 | `python -m pytest tests/test_person3_edge_cases.py -v` | 4 passed | Original Person 3 edge-case tests |
| macOS, Python 3.12 | `python -m pytest tests/test_occlusion.py -v` | 5 passed | Original occlusion tests |
| macOS, Python 3.12 | `python -m ruff check .` | Passed | Ruff validation |
| GitHub CI | Python 3.11 | Passed | Pull-request Core CI |
| GitHub CI | Python 3.12 | Passed | Pull-request Core CI |
| Windows, Python 3.12.7 | `python -m pytest tests/test_tracking_replay.py tests/test_tracking_mask.py tests/test_person_proximity.py tests/test_alert_engine.py tests/test_alert_edge_cases.py tests/test_alert_pipeline.py -q` | 22 passed | Clean integration branch |
| Windows, Python 3.12.7 | `python -m pytest` | 105 passed | Clean integration branch |

## Risks, limitations, and assumptions

- Proximity currently depends on a valid metric `position_m` supplied by the
  depth/3D stage.
- The association window is fixed at two seconds.
- Person occlusion is represented by the tracked bounding box rather than a
  segmentation mask.
- The alert rule associates a nearby non-authorized person with a confirmed
  removal event for human review; it does not prove theft or intent.

These assumptions require review by the owners of the depth/geometry,
volume-differencing, and integration stages.

## Handoff

Person 3 implementation is ready for integration review.
Integration with the live person detector/tracker and upstream depth/volume
stages remains a team-level integration task.

## Final links

- Issue: [#13](https://github.com/DontHash/kyra-shelf-guard/issues/13) tracks the
  synchronization and empty-pose follow-up.
- Contributor pull request: [#12](https://github.com/DontHash/kyra-shelf-guard/pull/12),
  superseded for merge by the clean integration branch.
- Clean integration pull request: [#19](https://github.com/DontHash/kyra-shelf-guard/pull/19).
- Commits: `bd44222`, `5e384b8`, `7471202`; synchronization and verified
  follow-up commits remain available from the contributor branch.
