# Gate 2 Evidence — Data and Baseline Calibration

- **Gate:** Gate 2 (Data and Baseline)
- **Accountable owner:** Person 1 (Data and Baseline)
- **Reviewers:** Person 4 (Integration and Pipeline), Person 2 (Geometry consumption)
- **Date recorded:** 2026-09-08
- **Status:** Approved / Closed

## Scope

This gate covers Person 1's input sources, deterministic scenario generation, baseline artifact calibration and persistence, golden scenario pack G01–G10, MiDaS anchor alignment policy, dataset provenance, and offline converter fixture.

## Gate definition

Per [docs/INTEGRATION_GATES.md](../INTEGRATION_GATES.md):
> **Exit:** deterministic same-seed scenario output, all ten reviewed golden scenarios, malformed/valid replay proof, 30-frame baseline and persistence/checksum proof, fixed/portable behavior, MiDaS anchor failure policy, offline converter fixture plus provenance, Windows and target-T4 load evidence.

## Verification environment

- **Operating System:** Windows 11 & Linux 6.12.90+ (x86_64, glibc 2.35) on Kaggle
- **Python version:** Python 3.12.7 (local Windows) / Python 3.12.13 (Kaggle provisioned)
- **Accelerator:** NVIDIA T4 GPU accelerator (Kaggle notebook, decision D-015)
- **Dependencies:** requirements.lock (synchronized)

## Evidence record

### 1. Deterministic Scenario Generation & Golden Pack (D-009)
- All 10 golden scenarios (G01–G10) regenerate with identical SHA-256 digests (checksums.sha256 matching A6B9A296...).
- 116/116 files verified byte-identical between Windows local run and target-T4 execution (docs/PERSON1_TEST_REPORT_T4_2026-09-07.md).

### 2. Baseline Calibration & Persistence
- 30-frame baseline builder produces calibrated BaselineArtifact with median depth, fixed geometry mask, portable components, 1 cm occupancy grid, and per-pixel depth-noise estimate.
- Round-trip NPZ/JSON persistence and calibration checksums validated.
- Known-volume acceptance suite verifies floor-sitting objects within 10% volume error bound.

### 3. MiDaS Anchor Alignment & Failure Policy
- Metric shelf anchor alignment policy verified: rejects invalid scale/shift, marks approximate metric status, and enforces residual bounds.

### 4. Provenance & Offline Converter
- Provenance record (data-sources/provenance.json) conforms to schema with CC-BY 4.0 approval (D-014).
- Offline converter (scripts/convert_ocid.py) parses OCID metadata strictly, converts depth to uint16 millimetres, handles addition/removal reversal, and enforces SHA-256 integrity.

### 5. Verification Entry Point
- Acceptance verifier (scripts/verify_person1.py) passes all 7 checks cleanly with exit code 0.
