# System Requirements for Person 1

## Short answer

Yes, this laptop can complete Person 1.

The local machine checked on 21 August 2026 has:

- ASUS Vivobook K3405ZF.
- Intel Core i5-12450H, 8 cores and 12 logical processors.
- About 16 GB RAM.
- NVIDIA RTX 2050 with 4 GB graphics memory.
- Python 3.12 installed.
- About 39.5 GB free on `D:` and 36.7 GB free on `C:` at the time of the check.

This is enough for the complete CPU-first path: manifests, image reading, lightweight procedural scenes, baseline calibration, save/load, MiDaS alignment tests using supplied arrays, OCID conversion, and unit tests.

## Recommended local setup

| Resource | Minimum for core work | Recommended for this assignment | This laptop |
|---|---:|---:|---:|
| CPU | 4 modern cores | 6 or more cores | 8 cores |
| RAM | 8 GB | 16 GB | About 16 GB |
| Free space | 10 GB without datasets | 30–60 GB with selected data and renders | About 76 GB across `C:` and `D:` |
| GPU | Not required | NVIDIA GPU for small BlenderProc/MiDaS experiments | RTX 2050, 4 GB |
| Python | 3.11+ | 3.12 on this machine | 3.12 available |

## What should run locally

- Scenario schema validation and checksums.
- RGB-D reading and unit conversion.
- Tiny procedural golden scenarios.
- Baseline fusion from 30 frames.
- Fixed-versus-portable classification.
- Baseline save/load.
- MiDaS anchor alignment using test arrays.
- Selected OCID conversion.
- All core unit and contract tests.
- Small BlenderProc batches with conservative resolution and batch size.

## What may be slow or constrained

- Large BlenderProc batches.
- High-resolution rendering with many assets.
- Running full MiDaS or other Torch models alongside Blender on a 4 GB GPU.
- Keeping full source datasets, converted copies, and render caches on the same drive.

These are speed and capacity limits, not blockers. Run small local batches, close other GPU-heavy applications, and store bulk data outside the repository.

## Storage plan

The official OCID record is about 6.4 GiB before conversion. Keep extra room for the downloaded archive, extracted data, selected converted scenarios, and checksums. A practical allowance is 15–20 GB for OCID work alone.

BlenderProc and scanned-object assets vary greatly in size. Start with procedural objects, then download only the approved subset needed for extended tests. Do not download a full asset library merely because storage is available.

Suggested layout:

```text
D:\KyraData\
├── downloads\
├── ocid\
├── converted\
├── blenderproc-cache\
└── reports\

D:\Code\Kyra\
├── source and documentation only
└── tiny golden fixtures only
```

## Target T4 requirement

The assignment separately requires the ten-scenario golden pack to load in the target T4 environment. The RTX 2050 cannot prove T4 compatibility. Complete and test locally first, then run the same frozen pack and lock-file installation in the assigned T4 environment. Record that as a separate acceptance report.

## Go/no-go rules

Proceed locally when:

- The core virtual environment installs from `requirements.lock`.
- At least 20 GB remains free before downloading OCID or rendering batches.
- Golden fixtures stay small enough to review and copy to the T4 environment.

Pause heavy data work when:

- Free space would fall below 10 GB on the target drive.
- A BlenderProc scene exceeds GPU memory repeatedly.
- A dependency requires changing shared versions without a compatibility test.

In those cases, reduce the dataset or render batch rather than changing the core design.
