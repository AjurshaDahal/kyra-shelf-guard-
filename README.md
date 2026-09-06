# Kyra Shelf Guard

Kyra is a university team project that studies whether a camera can notice when
something may have been removed from a shelf. It can raise a suspicious
shelf-removal alert for a person to review. It does not prove theft or decide
what someone intended to do.

## Where the project stands

Kyra is still in the foundation stage. Some building blocks work and the
automated checks pass on the current shared version (161 tests on Windows with
Python 3.12 on 2026-09-06), but the parts have not yet been joined into a
complete system. There is no finished app or usable command-line tool yet,
and the full project has not been tested on the target T4 computer.

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
| Person 2 | Measure whether the shelf has physically changed | Not started |
| Person 3 | Connect a shelf change to nearby people and apply the alert rules | Not started |
| Person 4 | Join the parts, provide shared rules and tools, test the whole system, and maintain the project documents | In progress |

The exact ownership rules live in [Team Ownership](docs/TEAM_OWNERSHIP.md).

## Quick setup for developers

~~~powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install --upgrade pip
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.lock
.\\.venv\\Scripts\\python.exe -m pip install -e .
.\\.venv\\Scripts\\python.exe -m pytest
~~~

Do not run the kyra command yet. The future command is listed in the project
settings, but the command itself has not been built.

## Important limits

- This repository does not contain a finished end-to-end result.
- Passing automated checks proves only the tested building blocks.
- Large datasets, generated recordings, model files, and run output stay outside Git.
- The original assignment remains the controlling source when a summary conflicts with it.

Code is licensed under AGPL-3.0-only; see [LICENSE](LICENSE). Dataset, asset,
and model licences are reviewed separately.
