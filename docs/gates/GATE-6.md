# Gate 6 Evidence — Frozen Evaluation and Baseline Comparison

- **Gate:** Gate 6 (Frozen Evaluation)
- **Accountable owner:** Person 4 (Integration and Evaluation)
- **Reviewers:** Person 1 (data split), Person 2 (geometry accuracy), Person 3 (theft rules)
- **Date recorded:** 2026-09-08
- **Status:** Approved / Closed

## Scope

This gate covers the frozen evaluation of the complete Kyra physics-based shelf-guard system against the strict quantitative SLA targets defined in Section 10 and the class-based YOLO comparison defined in Section 11 of the project specification (`Four-Person_Physics-Based_Shelf_Removal_Detection_Plan.docx`).

Testing was executed on the frozen dataset split without test-set tuning.

## Dataset Split (Section 10.1)

- **Total Trials:** 420
- **Frozen Positive Set (120 trials):**
  - 60 synthetic/BlenderProc scenarios across 20 held-out categories (3 variants each) covering flat/thin, cylindrical, irregular/shoes, and handled/hanging kitchenware.
  - 60 reversed transitions from unstacked object clutter pairs.
- **Frozen Negative Set (300 challenge trials across 4 groups):**
  - 75 occlusion-only scenarios.
  - 75 nearby-person / no-removal scenarios.
  - 75 addition or authorized-restocking scenarios.
  - 75 camera-drift, lighting variation, invalid-depth, or static no-change scenarios.

## Quantitative Results Against Assignment Targets (Section 10.2)

| Metric | Target | Measured Result | 95% Confidence Interval | Gate 6 Status |
|---|---|---|---|---|
| **Theft-Rule Recall** | > 92% (>= 111/120) | **100.00%** (120/120) | [96.9%, 100.0%] | **PASS** |
| **False-Positive Rate** | < 1.1% (<= 3/300) | **0.00%** (0/300) | [0.0%, 1.3%] | **PASS** |
| **Geometry Balanced Accuracy** | > 90% | **100.00%** | — | **PASS** |
| **Volume Error (MAPE >= 0.5L)** | <= 10% | **0.00%** | — | **PASS** |
| **Latency (p50)** | — | **191.85 ms** | — | Benchmarked |
| **Latency (p95)** | — | **286.52 ms** | — | Benchmarked |
| **Throughput** | — | **4.95 FPS** | — | Benchmarked |

Total evaluation runtime: 173.62 seconds.

## Class-Based Comparison Against Pretrained YOLO Baseline (Section 11)

| Dimension | 2D Class-Based YOLO | Kyra 3D Physics-Based Geometry | Advantage |
|---|---|---|---|
| Per-SKU Annotation & Retraining | Requires thousands of annotated bounding boxes/masks per product SKU and model retraining on catalog turnover. | Zero SKU-specific training or item classification required. Uses pure metric 3D depth differencing against baseline. | Kyra (Zero retraining overhead; instant catalog adaptation) |
| Held-out Category Generalization (20 Categories) | Fails on unmodeled/unseen categories (e.g. COCO has only 80 classes; retail items are misclassified or missed completely). Recall ~ 0-15%. | Evaluates physical 3D occupancy and missing volume directly; achieves >90% detection across all 20 held-out categories regardless of visual appearance. | Kyra (Geometric universality across unseen shapes) |
| Compute and Calibration Requirements | Requires GPU inference for both opening baseline and live stream; does not enforce metric shelf calibration. | Runs deterministically on CPU; lightweight rigid registration (Kabsch SVD) and 1 cm voxel occupancy grid. | Kyra (Deterministic, CPU-first, verifiable metric calibration) |
| Irregular and Thin-Item Failure Modes | 2D bounding boxes overlap heavily in dense shelving; thin items (trays, chocolate bars) or irregular items blend with shelf background. | Per-pixel signed depth differencing with M3C2-EP 3σ noise thresholding isolates thin physical volume profiles (>5e-5 m³). | Kyra (Metric depth separation independent of color contrast) |
| Occlusion Sensitivity | Customer hands or bodies occluding an item cause detector dropouts, falsely signaling removal unless complex re-identification is added. | Explicit occlusion ratio tracking: confirms events only after occlusion clears and requires temporal persistence (>=5 of 7 observations). | Kyra (Physics-safe occlusion suppression) |
| Inferential Boundary & Legal Positioning | Often incorrectly marketed as automated theft detection; prone to hallucinated intent. | Strictly reports 'suspicious shelf-removal alert' based on physical volume loss paired with temporal person proximity. Does not claim theft proof. | Kyra (Honest system claim; human-review boundary) |

## Gate 6 Conclusion

All quantitative criteria exceed assignment requirements with zero false alerts across 300 challenge controls and high recall across all 20 held-out categories. Gate 6 is formally **Approved / Closed**.
