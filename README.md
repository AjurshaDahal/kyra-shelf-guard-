# Kyra Shelf Guard

Kyra is a university team project that studies whether a camera can notice when
something may have been removed from a shelf. It can raise a suspicious
shelf-removal alert for a person to review. It does not prove theft or decide
what someone intended to do.

## Where the project stands

Kyra now has a candidate command-line vertical slice for deterministic test
scenarios. It joins the real baseline, replay tracking, shelf geometry, and
alert-rule components; it is not yet a finished or real-world-validated app.
The committed suite, verifier, and golden-pack audit have been run on a Kaggle
free-T4 GPU notebook (report: `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md`), but
the full project has not been run end-to-end anywhere, and the independent
handoff sign-off is still open.

For a simple progress summary, read [Project Guide for Team Members](docs/people/README.md).

## Choose your starting point

- **Need the documentation map:** start with the
  [documentation hub](docs/README.md), which separates plain-English, agent,
  and authoritative technical paths.
- **Team member, student, or reviewer:** start with the
  [plain-English project guide](docs/people/README.md).
- **Ready to work on the project:** follow the
  [team getting-started guide](docs/people/GETTING_STARTED.md).
- **Coding agent:** start with the
  [agent documentation route](docs/agents/README.md), then follow
  [AGENTS.md](AGENTS.md).
- **Need the detailed technical record:** use
  [Project Status](docs/PROJECT_STATUS.md), [Team Ownership](docs/TEAM_OWNERSHIP.md),
  and [Contracts](docs/CONTRACTS.md).

## What the four people are building

| Person | Plain-English responsibility | Current state |
|---|---|---|
| Person 1 | Prepare camera recordings and a reliable picture of a normal shelf | In progress |
| Person 2 | Measure whether the shelf has physically changed | In progress |
| Person 3 | Connect a shelf change to nearby people and apply the alert rules | In progress |
| Person 4 | Join the parts, provide shared rules and tools, test the whole system, and maintain the project documents | Complete for the shared layer; end-to-end validation remains open |

The exact ownership rules live in [Team Ownership](docs/TEAM_OWNERSHIP.md).

## Quick setup for developers

~~~powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install --upgrade pip
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.lock
.\\.venv\\Scripts\\python.exe -m pip install -e .
.\\.venv\\Scripts\\python.exe -m pytest
~~~

Use the visual test-scenario reviewer after setup:

~~~powershell
.\.venv\Scripts\python.exe -m kyra.simulator
~~~

That command opens the local **Kyra Scenario Lab** at
`http://127.0.0.1:8765`. It preloads the suspicious-removal example and lets a
reviewer play, pause, or step through RGB and depth frames, then run all ten
cases one at a time. The screen compares saved expectations with actual
pipeline events and alerts. The camera-drift case is a passing regression case
that must produce no event and no alert.

The same path can be exercised one command at a time without the visual interface:

~~~powershell
kyra simulate evidence/quick-smoke --case suspicious-removal
kyra calibrate evidence/quick-smoke/scenario.json --output evidence/baseline.npz
kyra run evidence/quick-smoke/scenario.json --baseline evidence/baseline.npz
kyra evaluate evidence/quick-smoke/scenario.json --baseline evidence/baseline.npz
kyra benchmark evidence/quick-smoke/scenario.json --baseline evidence/baseline.npz
~~~

Generated evidence stays outside Git. The `camera-drift` profile verifies that
camera motion is suppressed rather than reported as a shelf removal.

## Important limits

- This repository contains a synthetic test-scenario vertical slice, not a
  finished real-world end-to-end result.
- Passing automated checks proves only the tested building blocks.
- Large datasets, generated recordings, model files, and run output stay outside Git.
- The original assignment remains the controlling source when a summary conflicts with it.

Code is licensed under AGPL-3.0-only; see [LICENSE](LICENSE). Dataset, asset,
and model licences are reviewed separately.
