# Person 2 Specification — Geometry and Change

**Status:** Ready for team review
**Owner:** Person 2
**Source of truth:** `Four-Person_Physics-Based_Shelf_Removal_Detection_Plan.docx`

## Goal in simple words

Person 2 compares incoming RGB-D shelf frames against the opening baseline and detects stable, metric 3D changes (removals or additions) without knowing item categories or SKUs. Person 2 prioritizes occlusion and invalid-depth safety over forcing a decision on every frame: missing or occluded depth is never treated as empty shelf space.

## What Person 2 owns

- Registering current frames against fixed baseline shelf structure and detecting camera drift.
- Rejecting frames with registration residual exceeding the configured threshold (2 cm).
- Calculating signed depth differences between current observations and baseline depth.
- Adaptive per-pixel noise thresholding based on baseline noise estimates ($3\sigma$).
- Occlusion safety: calculating visible shelf fraction and suppressing removal confirmation when visibility is below 70% or when occluded by persons.
- Cleaning candidate change masks and extracting 3D connected components.
- Unprojecting component pixels into 3D shelf coordinates.
- Calculating 3D bounding boxes, centroids, and metric volume (integrating ray depth $\\times$ pixel area, cross-checked against the 1 cm baseline occupancy grid).
- Temporal persistence tracking: requiring change in $\\ge 5$ of the latest 7 frames and persistence for $\\ge 0.5$ seconds before confirmation.
- Emitting deterministic `VolumeChangeEvent` objects.
- Providing baseline update hooks for verified additions or authorized restocking (after 2 seconds of stable observation).
- Supplying independent unit and acceptance tests and test reports.

## What Person 2 does not own

- Reading raw scenario files from disk (owned by Person 1).
- Building the initial 30-frame baseline artifact (owned by Person 1).
- Person tracking, bounding boxes, or pose keypoints (owned by Person 3).
- Evaluating authorization policies or issuing final theft alerts (owned by Person 3).
- Bounded orchestration pipelines, CLI commands, or final benchmark evaluation (owned by Person 4).
- Modifying shared contracts (`contracts.py`, `manifest.py`) without Person 4 approval.

## Scientific literature grounding

The implementation directly operationalizes research from the project bibliography:

1. **Automated On-Shelf Availability (Milella et al., 2020)**:
   - Defines the workflow for shelf ROI extraction, reference background subtraction, 2D/3D component clustering, and volumetric calculation on retail shelves using consumer depth sensors.
2. **M3C2 and M3C2-EP (Lague et al., 2013; Winiwarter et al., 2021)**:
   - Establishes error propagation and statistical Level of Detection (LoD). Rather than an arbitrary global cutoff, the per-pixel threshold scales with baseline noise $\sigma$: $\\text{threshold} = \\max(\\text{removal\\_floor\\_m}, 3 \\times \\sigma_{\\text{baseline}})$, preventing sensor noise from triggering false removals.
3. **TSDF Differencing & POCD (Fehr et al.; Qian et al., 2022)**:
   - Formulates 3D space into *occupied*, *free*, and *unobserved/unknown*. Missing depth or occluded voxels are treated as unobserved, never as free space.
4. **Shopper Interaction & Occlusion (Amazon Go Patent US 9,530,060; Liciotti et al., 2015)**:
   - Recognizes that shopper interactions temporarily occlude items. Confirmation of removed items must be held pending until the shopper/hand clears and shelf visibility is restored.
5. **Dynamic Point Filtering (Habibiroudkenar et al., 2024 DynaHull)**:
   - Distinguishes stationary objects from transient dynamic occluders through spatial density and temporal consistency over consecutive observations.

## Required inputs and outputs

| Item | Source | Responsibility |
|---|---|---|
| `FramePacket` | Person 1 / Replay | Consumes metric depth in metres, valid-depth mask, intrinsics, and camera-to-shelf transform. |
| `BaselineArtifact` | Person 1 / Baseline | Consumes baseline depth, fixed geometry mask, noise sigma grid ($\\sigma$), and 1 cm occupancy grid. |
| `ShelfConfig` | Shared C-007 boundary | Consumes ROI, 3D bounds, `voxel_size_m`, and rejection/confirmation thresholds. |
| Occlusion masks | Person 3 / Replay | Consumes aligned boolean person masks for occlusion suppression. |
| `VolumeChangeEvent` | Person 2 | Emits confirmed volume change events with metric volume, 3D centroid, bounds, and confidence. |

## Functional requirements

### Shelf-only registration and drift

| ID | Requirement | Completion proof |
|---|---|---|
| P2-REG-001 | Estimate global depth shift and rigid alignment on fixed shelf geometry (`fixed_geometry_mask`). | Corrects translation up to 15 mm and rotation up to 1° without corrupting portable-object regions. |
| P2-REG-002 | Calculate registration residual against baseline fixed geometry; reject frames where residual exceeds `registration_reject_m` (default 0.02 m). | Frames with drift > 2 cm return rejected state with `rejection_reason="registration_residual_exceeded"`. |
| P2-REG-003 | Core registration runs CPU-first via NumPy/OpenCV; Open3D point-to-plane ICP acts as an optional acceleration adapter. | Core registration tests pass with Open3D uninstalled. |

### Signed depth classification

| ID | Requirement | Completion proof |
|---|---|---|
| P2-DIFF-001 | Classify depth differences: $\\Delta z = z_{\\text{curr}} - z_{\\text{base}}$. Farther valid surface ($\\Delta z > T$) $\\to$ candidate `REMOVAL`; nearer valid surface ($\\Delta z < -T$) $\\to$ `ADDITION` / occluder. | Unit tests verify sign conventions on synthetic steps. |
| P2-DIFF-002 | Compute per-pixel threshold $T(u, v) = \\max(\\text{removal\\_floor\\_m}, 3 \\times \\sigma_{\\text{noise}}(u, v))$. | High-noise pixels suppress false removals below $3\\sigma$. |
| P2-DIFF-003 | Any zero, NaN, masked, or person-occluded pixel is classified as `UNKNOWN` and excluded from removal evidence. | Tests assert zero removal pixels in unknown regions. |

### Occlusion safety

| ID | Requirement | Completion proof |
|---|---|---|
| P2-OCC-001 | Compute `visible_shelf_fraction = valid_unoccluded_shelf_pixels / total_roi_pixels`. | Unit test verifies exact ratio across masked geometries. |
| P2-OCC-002 | Suspend change confirmation when `visible_shelf_fraction < minimum_visible_fraction` (default 0.70). | Occlusion-only scenarios emit zero confirmed removals. |
| P2-OCC-003 | Wait for occlusion to clear before confirming negative space; do not accumulate removal evidence across occluded frames. | Multi-frame person occlusion test confirms removal only after person departs. |

### 3D clustering and metric volume

| ID | Requirement | Completion proof |
|---|---|---|
| P2-VOL-001 | Clean candidate mask with morphological filtering and extract connected components. | Rejects isolated single-pixel noise spikes. |
| P2-VOL-002 | Unproject component pixels into 3D shelf coordinates using camera intrinsics and `camera_to_shelf` transform. | Verifies correct 3D centroid and oriented bounding box. |
| P2-VOL-003 | Estimate metric volume by integrating ray depth $\\times$ pixel area, cross-checked against baseline 1 cm occupancy grid. | Clean objects $\\ge 0.5$ L have median volume error $\\le 15\\%$. |
| P2-VOL-004 | Reject or mark low confidence for components smaller than `minimum_alert_volume_m3` ($5 \\times 10^{-5}\\text{ m}^3$). | Sub-threshold clusters do not trigger volume change events. |

### Temporal confirmation and state

| ID | Requirement | Completion proof |
|---|---|---|
| P2-STATE-001 | Require candidate detection in at least 5 of the latest 7 frames. | Transient single-frame glitches produce zero confirmed events. |
| P2-STATE-002 | Require temporal persistence of at least 0.5 seconds (500 ms) before confirmation. | Events faster than 0.5 s remain unconfirmed. |
| P2-STATE-003 | Deduplicate events; emit single `VolumeChangeEvent` for a confirmed removal until state clears or changes. | Repeated frames during same removal produce one event ID. |
| P2-STATE-004 | Support addition and authorized-restocking baseline update hooks after 2.0 seconds of stable observation. | Baseline updates to new geometry after stable restocking. |

### Performance and acceptance

| ID | Requirement | Completion proof |
|---|---|---|
| P2-QA-001 | All Person 2 unit and integration tests pass independently on Python 3.12 without network or GPU. | `pytest tests/test_geometry*.py` exit code 0. |
| P2-QA-002 | Frame processing latency target is below 40 ms p95 on standard CPU at target resolution. | Benchmark test logs execution time. |
| P2-QA-003 | Implements `GeometryProvider` protocol in `src/kyra/adapters.py`. | Adapter passes protocol check and replaces `MockGeometryProvider`. |
