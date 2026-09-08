# Dataset and Provenance Rules

## Rule in one sentence

Keep large data outside Git, verify what was downloaded, convert only approved records, and leave enough information for another person to reproduce the choice.

## Planned sources

| Source | Use | Core requirement? | Authority to check before use |
|---|---|---|---|
| Procedural Kyra fixtures | Fast deterministic golden pack | Yes | This repository and assignment |
| [OCID](https://www.acin.tuwien.ac.at/en/vision-for-robotics/software-tools/object-clutter-indoor-dataset/) | Public RGB-D clutter examples and reversed removal cases | Selected conversion required | Official TU Wien dataset page and its terms |
| [BlenderProc](https://github.com/DLR-RM/BlenderProc) | Optional realistic rendering | No | Official DLR repository |
| [Google Scanned Objects](https://research.google/resources/datasets/scanned-objects-google-research/) | Optional object geometry | No | Official Google Research dataset page and terms |
| [MiDaS](https://github.com/isl-org/MiDaS) | Optional relative-depth fallback | No | Official project repository and model-specific terms |
| [Open3D](https://www.open3d.org/) | Optional geometry checks | No | Official project documentation |

A source appearing in this table is not automatic permission to download, redistribute, or combine it with the project. Review the exact terms and selected files first.

## Storage

The official OCID page describes an archive of roughly 6.4 GiB. Allow 15–20 GB for the archive, extraction, selected conversion, and temporary output.

```text
D:\KyraData\
├── downloads\
├── ocid\
├── converted\
├── blenderproc-cache\
└── reports\
```

Do not commit those folders. Only tiny deterministic fixtures intended for automated tests belong in `scenario-fixtures/` or `tests/fixtures/`.

Optional model caches and generated model outputs follow the same rule. The
MiDaS smoke uses `<KYRA_DATA_ROOT>/model-smoke/` for its revision-pinned code,
checkpoint, relative-depth arrays, approximate two-anchor outputs, and hashed
JSON report. The checkpoint is not redistributed by this repository. A
successful model run is recorded separately from metric-depth accuracy,
latency, live-camera, volume, or alert evidence.

## Provenance record

The planned `data-sources/provenance.json` must record, for every source or selected subset:

- Stable source ID and name.
- Official source URL and terms/licence URL.
- Retrieval date and source version, release, or snapshot when available.
- Downloaded filename and byte size.
- Published checksum when available and locally computed SHA-256.
- Exact selected scenes, objects, frames, and split.
- Excluded records and the reason: licence, corruption, missing depth, calibration, duplication, or out of scope.
- Conversion command and converter version.
- Output schema version and output checksum list.
- Required attribution text.

Do not store a private absolute home path. Use an environment-neutral path hint such as `<KYRA_DATA_ROOT>/ocid`.

## Checksum workflow on Windows

Before extraction or conversion:

```powershell
Get-FileHash -Algorithm SHA256 D:\KyraData\downloads\<archive-name>
```

Compare the result with the publisher’s checksum when one exists. If no publisher checksum is available, record that fact and treat the locally computed hash as an identity record, not proof that the download is authentic.

## OCID conversion rules

- Validate the source checksum before reading it.
- Preserve source frame order, calibration, depth units, and masks.
- Convert depth into the scenario contract without inventing missing values.
- Record the exact source sequence and frame range.
- Reverse an addition sequence only when the physical order remains valid as a removal example.
- When reversing, create new monotonically increasing timestamps and update expected change direction and time.
- Keep original provenance even when the converted sequence direction changes.
- Reject unclear calibration, corrupted files, unsupported encoding, or licence uncertainty and record the reason.

### Current selected OCID evidence (2026-09-08)

- Verified OCID 1.0.0 archive: 6,822,716,319 bytes; publisher MD5
  `aa0eff01f75104c40e4243e6f892a757`; local SHA-256
  `01878149adf7eb330f99439ee9d15d6e2280a1aa3539b90e0b6dc3c7ba1fa29f`.
- Selected `ARID20/table/{top,bottom}/seq0{1,2}`. Each 21-frame source sequence
  was converted in forward and reverse order, yielding 8 external scenarios
  and 168 replayed frames.
- Every manifest was read through `ScenarioFrameSource`; timestamps were
  monotonic, RGB/depth/mask dimensions agreed, in-memory depth was `float32`
  metres, and invalid source depth remained zero/unknown.
- The exact source-metadata and output-manifest SHA-256 values are retained in
  `<KYRA_DATA_ROOT>/ocid/verification_summary.json` outside Git.

This is recorded-data conversion and replay evidence. It is not a real shop,
live-camera, theft-intent, model-accuracy, or production-readiness result, and
the selected ARID-derived frames are not redistributed from this repository.

## Licence review gate

The repository code is AGPL-3.0-only, but datasets, object assets, model weights, and generated output may have different conditions. Before public distribution, record whether each source permits the planned research use, derivative conversion, redistribution of tiny fixtures, and publication of examples. If the answer is unclear, exclude the source until the team receives clarification.
# YOLO recorded-image smoke assets

Issue #85 uses the official Ultralytics YOLO11n detection weights and official
`bus.jpg` example only as external smoke inputs. Their URLs, byte counts, and
SHA-256 values are recorded in `data-sources/provenance.json`; neither asset is
redistributed in Git. The OCID frames are negative execution observations, not
person-detection accuracy evidence, because OCID has no person annotations.
