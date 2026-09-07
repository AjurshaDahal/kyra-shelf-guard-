# Person 2 Implementation Plan

**Status:** Complete; all 4 milestones (P2-01 through P2-04) implemented and verified
**Owner:** Person 2
**Estimated effort:** 8–12 focused working days
**Requirements:** [PERSON2_SPEC.md](PERSON2_SPEC.md)

## Outcome

Person 2 delivers an offline, CPU-first 3D change detection package that processes `FramePacket`, `BaselineArtifact`, `ShelfConfig`, and Person 3 occlusion masks to produce confirmed `VolumeChangeEvent` objects. The system operates safely under person occlusion, suppresses invalid depth, calculates metric volume, and passes all Gate 3 integration criteria without requiring GPU, Blender, or network access.

## Starting point

Present before P2-01:
- Shared contracts (`FramePacket`, `BaselineArtifact`, `ShelfConfig`, `VolumeChangeEvent`) in `src/kyra/contracts.py`.
- Mock provider `MockGeometryProvider` in `src/kyra/adapters.py`.
- Replayable scenario reader in `src/kyra/io.py` and deterministic scenario generator in `src/kyra/simulation.py`.
- Person 3 person occlusion mask generator in `src/kyra/proximity/occlusion.py`.

Missing before P2-01:
- Registration and camera drift compensation.
- Signed depth differencer with per-pixel noise thresholding.
- Occlusion safety and shelf visibility monitoring.
- 3D connected-component clustering and ray/occupancy volume estimation.
- Temporal persistence state engine and real `GeometryProvider` adapter.

## Phased Milestones

```text
┌─────────────────────────────────────────────────────────────┐
│ Milestone 1 (P2-01): Shelf Registration & Drift Check       │
│ - Estimate rigid drift on fixed shelf surfaces             │
│ - Reject residual > 2 cm; correct drift <= 15 mm / 1°       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Milestone 2 (P2-02): Signed Differencing & Occlusion Safety │
│ - Signed difference Δz with per-pixel 3σ noise threshold   │
│ - Person occlusion mask integration & visibility ratio      │
│ - Suspend confirmation when visibility < 70%               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Milestone 3 (P2-03): 3D Clustering & Metric Volume          │
│ - Morphological 2D cleaning & connected components         │
│ - 3D shelf-coordinate unprojection                         │
│ - Ray depth integration & 1 cm occupancy grid cross-check   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Milestone 4 (P2-04): Temporal Engine & GeometryProvider     │
│ - 5 of 7 frame window, >= 0.5 s persistence check          │
│ - Event deduplication & VolumeChangeEvent emission          │
│ - Baseline update hooks for stable restocking              │
│ - Integration with Person 4 pipeline via GeometryProvider   │
└─────────────────────────────────────────────────────────────┘
```

## Milestone breakdown

### Milestone 1 — P2-01: Shelf-only registration and drift check

- **Requirements:** P2-REG-001, P2-REG-002, P2-REG-003.
- **Paths:** `src/kyra/geometry/registration.py`, `tests/test_geometry_drift.py`.
- **Do:**
  1. Extract 3D points from current frame depth where `BaselineArtifact.fixed_geometry_mask` is True and `valid_depth_mask` is True.
  2. Compute alignment transformation against baseline fixed structure (centroid shift + rigid alignment).
  3. Compute registration residual (root-mean-square or mean absolute error).
  4. If residual > `ShelfConfig.registration_reject_m` (0.02 m), return a registration failure record (`residual_m`, `rejected=True`, `rejection_reason="registration_residual_exceeded"`).
  5. If within the correction envelope (<= 15 mm, <= 1°), apply rigid correction to depth or unprojected points.
- **Proof:** Synthetic drift scenarios within 15 mm/1° are corrected to < 3 mm residual; drifts > 20 mm are cleanly rejected with an explicit rejection reason.
- **Estimate:** 2 days.

### Milestone 2 — P2-02: Signed depth differencing and occlusion safety

- **Requirements:** P2-DIFF-001, P2-DIFF-002, P2-DIFF-003, P2-OCC-001, P2-OCC-002, P2-OCC-003.
- **Paths:** `src/kyra/differencing/signed_diff.py`, `src/kyra/occlusion/safety.py`, `tests/test_differencing.py`, `tests/test_occlusion_safety.py`.
- **Do:**
  1. Calculate signed depth change $\Delta z = z_{	ext{curr}} - z_{	ext{base}}$ across shelf ROI.
  2. Compute per-pixel threshold $T(u, v) = \max(	ext{removal\_floor\_m}, 3 	imes \sigma_{	ext{noise}}(u, v))$.
  3. Classify into candidate masks: `REMOVAL` ($\Delta z > T$), `ADDITION` ($\Delta z < -T$), and `UNKNOWN` (invalid depth or person occlusion mask).
  4. Compute `visible_shelf_fraction = valid_unoccluded_pixels / total_roi_pixels`.
  5. If `visible_shelf_fraction < minimum_visible_fraction` (0.70), mark frame as occluded and suspend change confirmation.
- **Proof:** Synthetic removal, addition, noise, and person-occlusion frames correctly classified; zero false removals generated in occluded regions.
- **Estimate:** 2.5 days.

### Milestone 3 — P2-03: 3D point-cloud clustering and metric volume estimation

- **Requirements:** P2-VOL-001, P2-VOL-002, P2-VOL-003, P2-VOL-004.
- **Paths:** `src/kyra/geometry/clustering.py`, `src/kyra/geometry/volume.py`, `tests/test_geometry_clustering.py`, `tests/test_geometry_volume.py`.
- **Do:**
  1. Morphologically filter candidate 2D removal mask (remove isolated pixels, close small gaps).
  2. Label connected components and extract bounding boxes.
  3. Unproject pixels of each component to 3D shelf coordinates using camera intrinsics and `camera_to_shelf`.
  4. Estimate metric volume using ray-integration: $\sum \Delta z_i \cdot
rac{z_i^2}{f_x f_y}$, cross-checked against occupied voxels in baseline 1 cm `occupancy_grid`.
  5. Compute 3D bounding box `(bounds_min_m, bounds_max_m)` and `centroid_m`.
  6. Filter out clusters with volume $< 	ext{minimum\_alert\_volume\_m3}$ ($5 	imes 10^{-5}\,	ext{m}^3$).
- **Proof:** Synthetic objects of volume $\ge 0.5$ L yield volume error $\le 15\%$ and 3D IoU $\ge 0.50$.
- **Estimate:** 3 days.

### Milestone 4 — P2-04: Temporal confirmation, baseline hooks, and GeometryProvider adapter

- **Requirements:** P2-STATE-001, P2-STATE-002, P2-STATE-003, P2-STATE-004, P2-QA-001, P2-QA-002, P2-QA-003.
- **Paths:** `src/kyra/geometry/temporal_state.py`, `src/kyra/geometry/provider.py`, `tests/test_geometry_provider.py`.
- **Do:**
  1. Maintain sliding history window across frames.
  2. Confirm removal only if observed in $\ge 5$ of latest 7 frames and persistence $\ge 0.5$ seconds with visibility $\ge 70\%$.
  3. Construct and emit frozen `VolumeChangeEvent`. Deduplicate ongoing removals.
  4. Provide baseline update hook: if stable addition/restock observed for $\ge 2.0$ seconds, update baseline depth and occupancy.
  5. Expose `ShelfGeometryProvider` implementing `GeometryProvider` protocol in `src/kyra/adapters.py`.
- **Proof:** End-to-end replay on synthetic golden scenarios cleanly detects removals without false positives on occlusions or additions; benchmark latency $< 40$ ms p95.
- **Estimate:** 2.5 days.
