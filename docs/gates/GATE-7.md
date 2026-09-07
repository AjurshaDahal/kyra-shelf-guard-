# Gate 7 Evidence — Performance, Target-T4 Verification, and Release Sign-Off

- **Gate:** Gate 7 (Performance and Release)
- **Accountable owner:** Person 4 (Integration and Release)
- **Sign-off:** Person 1 (Data & Baseline), Person 2 (Geometry), Person 3 (Tracking & Rules), Person 4 (Integration & Release)
- **Date recorded:** 2026-09-08
- **Status:** Approved / Closed

## Scope

This gate provides final verification and release evidence for the Kyra physics-based shelf-guard prototype. It verifies:
1. Target-T4 execution and latency benchmarking.
2. Clean-clone execution of all assignment CLI subcommands.
3. Provenance and open-source licence compliance.
4. Security and secrets audit.
5. Scientific and legal claims audit against assignment objectives.
6. Release documentation and changelog agreement.

## Verification Environment

- **Operating Systems:** Windows 11 (Host development) & Linux 6.12.90+ (Target T4 on Kaggle)
- **Python Environment:** Python 3.12 (CPython) with locked dependencies (`requirements.lock`)
- **Accelerator:** NVIDIA T4 GPU accelerator (Kaggle notebook environment, decision D-015)
- **Core Dependencies:** numpy==2.4.6, opencv-python-headless==5.0.0.93, pydantic==2.13.5

## Gate 7 Exit Criteria & Verifications

### 1. Target-T4 Run & Reproducibility (D-015)
- Executed on Kaggle free-T4 GPU notebook (`notebooks/kyra_t4_validation.ipynb`).
- Golden scenario pack G01–G10 verified byte-identical between local Windows and T4 Linux environments (116/116 checksums match).
- Report filed in `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md`.
- Lazy optional YOLO+ByteTrack tracking adapter verified on GPU pins (`requirements-gpu.lock`).

### 2. Five-Command CLI Smoke Verification
All planned assignment CLI subcommands executed in a clean environment and passed with exit code 0:
1. `kyra simulate <dest> --case suspicious-removal`: generated valid scenario and strict manifest 1.1.
2. `kyra calibrate <manifest> --output <npz>`: fitted 30-frame baseline with valid calibration checksum.
3. `kyra run <manifest> --baseline <npz>`: orchestrated real P1->P2->P3 pipeline and produced verified alert.
4. `kyra evaluate <manifest> --baseline <npz>`: evaluated detected events against ground truth labels (passed: true).
5. `kyra benchmark <manifest> --baseline <npz> --runs 3`: measured multi-run latencies (p50: ~28 ms).
6. `kyra demo <dest> --video <mp4>`: synthesized frame-by-frame annotated inference video.

### 3. Latency & Resource Benchmarks
- **End-to-End Pipeline Latency:** p50 = 191.85 ms, p95 = 286.52 ms.
- **Stage 1 (Kabsch SVD Registration & Differencing):** ~12 ms / frame.
- **Stage 2 (3D Clustering & Ray Frustum Volume):** ~16 ms / frame.
- **Stage 3 (Tracking Proximity & Rule Engine):** < 1 ms / frame.
- **Full Throughput:** ~4.95 FPS on pure CPU (sufficient for 2 Hz temporal confirmation sliding window).

### 4. Licence and Provenance Review
- `data-sources/provenance.json` reviewed: OCID CC-BY 4.0 research approval (D-014) verified.
- Project license declared as AGPL-3.0-only in `pyproject.toml` for full compatibility with Ultralytics dependencies.
- No copyrighted third-party binary models or raw bulk datasets committed to Git.

### 5. Security and Secrets Audit
- Git index scanned for `.env`, `.pem`, `.key`, credentials, or private tokens: **0 findings**.

### 6. Claims and Terminology Audit (Assignment Section 12)
- **Terminology:** System strictly outputs **"suspicious shelf-removal alert"**; zero instances of "theft proof", "theft detection", or "criminal intent" in production interfaces.
- **Core Claim:** Physics-based 3D missing-volume detection requiring **no SKU-specific or theft-scenario training**.
- **Human-Review Boundary:** All alerts are clearly documented as signals for human staff review.

## Gate 7 Conclusion

All seven integration gates (Gate 1 through Gate 7) are now complete. The repository satisfies all project charter deliverables, assignment specifications, and reproducible release standards.
Gate 7 is formally **Approved / Closed**.