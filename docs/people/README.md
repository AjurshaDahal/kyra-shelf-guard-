# Project Guide for Team Members

This page explains Kyra without assuming that you know computer-vision or software
engineering terms.

## What are we trying to make?

We want a system that watches a shelf using a camera that records both colour and
distance. It should notice a lasting shelf change, check whether a person was
nearby, and create an alert for a human to review.

The system must say suspicious shelf-removal alert. It must not claim that a person
stole something or that it knows their intention.

## Is it finished?

No. Kyra is a set of tested building blocks, not a finished app.

This summary was checked against the detailed project record on 2026-08-30:

- **Working now:** shared information formats, reading saved camera frames,
  checking input files, building and saving a normal-shelf reference, and tests
  that keep shared information compatible.
- **Started but incomplete:** preparing the remaining sample data and shared rules
  needed to connect the four people's work.
- **Not built yet:** measuring shelf changes, connecting those changes to nearby
  people, making the final alert decision, joining all parts into one flow, the
  five planned commands, and the final evaluation tools.
- **Not proven yet:** a complete run from camera input to alert, real-world
  performance, and testing on the target T4 computer.

The current shared version passes 161 automated tests on Windows with Python
3.12.7 (dated total, 2026-09-06). This is evidence for the existing building
blocks only, not proof that the complete system works.

For exact evidence and blockers, use the technical [Project Status](../PROJECT_STATUS.md).

## Who does what?

### Person 1 — Prepare the input

Person 1 prepares saved camera recordings, checks that they are valid, and builds
a reliable picture of what the shelf normally looks like.

### Person 2 — Measure shelf changes

Person 2 works out whether something was added or removed and estimates how much
the shelf changed. Missing camera information must never be treated as empty space.

### Person 3 — Connect people and alerts

Person 3 follows nearby people in saved recordings, handles authorised restocking,
and applies the fixed rules that decide whether an alert should be created.

### Person 4 — Join and check everything

Person 4 maintains the shared rules, joins the work together, builds commands and
reports, checks final evidence, and keeps project documentation consistent.

The detailed file boundaries are in [Team Ownership](../TEAM_OWNERSHIP.md).

## What should I do next?

If you are joining the work, follow [Getting Started](GETTING_STARTED.md). If you
only need progress, stay on this page; the technical pages are for implementation
and review.

## Words you may see

| Word | Simple meaning |
|---|---|
| RGB-D camera | A camera that records colour and distance |
| Baseline | A saved picture of the shelf in its normal state |
| Contract | An agreed format used to pass information between two parts |
| Fixture | A small saved example used in a test |
| Pipeline | The complete path that joins all parts in order |
| Integration gate | A checkpoint that needs named evidence before the team moves on |

This is a plain-English summary. If it conflicts with an approved decision,
contract, test, or the original assignment, the more detailed source wins.
