# Person 1 Test Report — Target T4 (Kaggle free-T4 GPU notebook)

**Report status:** Pass with limitations
**Tester:** Runner of `notebooks/kyra_t4_validation.ipynb` on Kaggle (free T4 GPU)
**Date:** 2026-09-07 (dated evidence)
**Environment:** Target T4 — Kaggle GPU T4 accelerator (decision D-015)
**Independent tester:** No — self-run; the independent teammate sign-off stays open (issue #59)

## Build identity

| Field | Recorded value |
|---|---|
| Git commit or source archive checksum | GitHub ZIP snapshot of `main`; content fingerprint matches commit `65d3707` byte-exact for `pyproject.toml`, `notebooks/kyra_t4_validation.ipynb`, `src/kyra/contracts.py`, `scenario-fixtures/golden/golden-pack.json` (re-verified 2026-09-07) |
| Golden-pack checksum | `golden-pack.json` SHA-256 `A6B9A29674B84E92E9C4D236F662095778A6E5229E7651B2AC7195E959CAE8F9`; inventory `checksums.sha256` SHA-256 `F889E0FD9A6E5119B2BE686A6BEB153A7C8DDF25EE29E9C4EAFB9A6B6BB5F33F` |
| Python version | 3.12.13 (Kaggle provisioned) |
| Dependency lock checksum | `requirements.lock` SHA-256 `1331D0B0EB691152EF44C5723087B22AE27F4C0A854C4969957661E065C0CD1A` |
| Operating system | Linux 6.12.90+ (x86_64, glibc 2.35) on Kaggle |
| CPU | Kaggle host CPU; model not recorded in the exported artifact |
| GPU and driver, if used | NVIDIA T4 free-tier accelerator per Kaggle notebook settings (runner-confirmed); `nvidia-smi` and `torch.cuda.get_device_name` text were not included in the exported ZIP, so the accelerator identity is not independently re-verifiable from the artifact |

## Commands and results

| Exact command | Exit code | Duration | Result or report path |
|---|---:|---:|---|
| `pip install -r requirements.lock` | 0 | — | installed the frozen core pins (pydantic 2.13.5, numpy 2.4.6, opencv 5.0.0.93) |
| `pip install -e .` | 0 | — | editable package installed |
| `python -m pytest -q` | 0 | 1.95 s | **189 passed** (`.pytest_cache` nodeids = 189 entries) |
| `python scripts/verify_person1.py` | 0 | — | seven-check Person 1 verifier passed |
| `python scripts/generate_golden_pack.py <audit>` | 0 | — | regeneration audit **byte-identical: True**; `golden-audit/checksums.sha256` equals the committed inventory (116/116, independently re-verified locally) |
| GPU smoke: `pip install -r requirements-gpu.lock` + torch probe | 0 | — | optional published-pin smoke (torch 2.14.0 / ultralytics 8.4.138); probe exit 0 |

## Acceptance results

| Requirement | Pass / Fail / Not run | Evidence or limitation |
|---|---|---|
| Same-seed byte-identical manifests | Pass | golden-pack regeneration audit byte-identical (116/116) |
| Ten scenarios load | Pass | verifier exit 0 includes golden-pack schema/checksum/reader replay |
| Baseline reloads without recomputation | Pass | verifier baseline check and baseline tests within the 189 |
| Fixed shelf never portable | Pass | baseline policy tests within the 189 |
| Under-0.5 m³ object classification | Pass | suite covers; acceptance evidence is unit/synthetic |
| At least 0.5 L object volume error ≤10% | Pass | `tests/acceptance/test_baseline_volume.py` within the 189 |
| MiDaS good and rejection cases | Pass | verifier MiDaS-policy check and tests within the 189 |
| Provenance completeness | Pass | verifier provenance check; record `data-sources/provenance.json` |
| Full Person 1 unit and contract suite | Pass | 189 tests passed on the target environment |

## Golden scenarios

| ID | Loaded | Expected result matched | Notes |
|---|---|---|---|
| G01 | Yes | Not run | change-detection outcomes are Gate 3–5 evidence, not produced by this suite run |
| G02 | Yes | Not run | same |
| G03 | Yes | Not run | same |
| G04 | Yes | Not run | same |
| G05 | Yes | Not run | same |
| G06 | Yes | Not run | same |
| G07 | Yes | Not run | same |
| G08 | Yes | Not run | same |
| G09 | Yes | Not run | same |
| G10 | Yes | Not run | same |

Loads are exercised through the verifier replay and the golden-pack tests within the 189; per-scenario detection outcomes remain open Gate 2–5 work.

## Problems and exclusions

- The exported ZIP contained the draft report, `.pytest_cache` (189 nodeids), the `golden-audit` directory, and the repository snapshot, but **no notebook output cells**. The accelerator setting (GPU T4) and `nvidia-smi` text are runner-confirmed only and are recorded as such, not claimed as artifact-verified.
- GPU smoke is published-pin evidence (torch probe exit 0), not model accuracy or an end-to-end detection result.
- The repository snapshot was an export of `main` `65d3707`; the runner's notebook applied the one-line `copytree` fix from `13ea8e4` in the UI, so the executed cell set is the merged discovery cell plus that documented patch.
- Independent tester sign-off: not done (issue #59). This report is self-run evidence.
- Real OCID conversion and Gate 2–7 detection evidence remain open; this run proves the committed suite, verifier, and golden-pack reproducibility on the target T4 environment only.

## Handoff decision

- [ ] Ready for Persons 2, 3, and 4.
- [x] Ready with the limitations listed above.
- [ ] Not ready; blocking items remain.

**Tester sign-off:** Kaggle notebook runner (`PERSON1_TEST_REPORT_T4_2026-09-07_draft.txt` produced by `notebooks/kyra_t4_validation.ipynb`, 2026-09-07)
**Receiving teammate sign-off:** pending — independent handoff sign-off is issue #59