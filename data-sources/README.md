# Data Sources

This folder records where public data comes from and how it is converted.
The authoritative rules live in [docs/DATASETS.md](../docs/DATASETS.md);
`provenance.json` is the machine-validated record of sources, checksums,
licences, selections, exclusions, and conversion commands.

## Adding or updating a source

1. Add one entry to `provenance.json` with every required field.
2. Never store a private absolute home path; use `<KYRA_DATA_ROOT>/...`.
3. Keep the full archive and converted bulk data out of Git
   (`D:\KyraData\` per the dataset rules).
4. Update `tests/test_dataset_provenance.py` only if the schema meaning
   changes; otherwise the committed record is validated by the existing tests.
5. Status values are honest: `pending_download`, `retrieved`,
   `converted`, or `excluded`. A blank required field is a schema failure.

Current state: the OCID source is recorded as `pending_download`; the licence
review is approved (D-014, 2026-09-07) but nothing has been downloaded yet.
Conversion will start only after a team-confirmed subset and the source
checksum are recorded here at retrieval time.