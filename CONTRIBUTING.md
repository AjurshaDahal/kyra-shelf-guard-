# Contributing

Kyra is a four-person assignment with shared contracts. Keep changes small, traceable, and easy for another owner to test.

## Before changing code

1. Read `README.md`, `AGENTS.md`, and the relevant specification.
2. Find the requirement ID in `docs/PERSON1_SPEC.md`.
3. Read the implementation and nearby tests before editing.
4. Confirm that the file is inside your ownership boundary.
5. Ask before changing a shared contract, schema meaning, public API, or dataset licence decision.

## Local setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e .
```

Install a heavy optional lock file only when the task needs it.

## Change workflow

1. Add or update a failing test that expresses the requirement.
2. Make the smallest implementation change that passes it.
3. Run the focused test.
4. Run all Person 1 tests and Ruff.
5. Update the implementation-plan status and evidence.
6. Add a short entry under `CHANGELOG.md` → `Unreleased` for notable changes.
7. Record any durable design choice in `docs/DECISIONS.md`.

## Required checks

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

For a Person 1 handoff, also run the golden-pack and baseline acceptance commands defined in `docs/TESTING.md`. Record the operating system, Python version, dependency lock, command, exit code, and result.

## Data rules

- Never commit full OCID, Google Scanned Objects, generated render batches, model weights, or converted bulk data.
- Put only tiny deterministic fixtures in `scenario-fixtures/`.
- Check hashes before conversion.
- Commit provenance and conversion instructions, not the bulk source data.
- Do not use a dataset until its licence and intended use have been reviewed.

## Review checklist

- The change names one or more requirement IDs.
- Units, coordinate systems, timestamps, and invalid-depth behavior are explicit.
- Tests cover success and failure paths.
- Core tests do not need network, CUDA, Blender, or external datasets.
- Generated output is repeatable where required.
- Documentation describes only behavior that exists or clearly labels planned behavior.
- No benchmark or evaluation result is claimed without saved evidence.

## Releases

There is no confirmed release process yet. Do not create release entries from the package version alone. Add changelog comparison links only after the real Git host and release process are known.
