# Getting Started as a Team Member

Use this guide when you are ready to contribute. You do not need to understand
every technical document before choosing where to begin.

## 1. Understand the project

Read the [Project Guide for Team Members](README.md), especially what is working,
what is missing, and what the project is not allowed to claim.

## 2. Confirm your role

Ask the team which role you own: Person 1, 2, 3, or 4. Do not choose another
person's files just because they look related. If your name or GitHub account has
not been assigned, ask the project lead to update the roster first.

## 3. Find one task

Choose one GitHub Issue assigned to your role. It should say the result, scope,
files, checks, and dependencies. If no task exists, create one from the work-item
template before changing files.

## 4. Read only the detail you need

- [Team Ownership](../TEAM_OWNERSHIP.md) says which part belongs to whom.
- [Project Status](../PROJECT_STATUS.md) shows detailed current state.
- [Decisions](../DECISIONS.md) records choices already made.
- [Contracts](../CONTRACTS.md) describes information shared between parts.
- [Testing](../TESTING.md) explains what proof a task needs.
- Coding agents use the separate [agent documentation route](../agents/README.md).

## 5. Set up on Windows

~~~powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.lock
.\\.venv\\Scripts\\python.exe -m pip install -e .
.\\.venv\\Scripts\\python.exe -m pytest
~~~

The tests should pass before you start. If they do not, save the exact error and
ask the team whether the shared branch is already broken. Do not hide the failure.

## 6. Make one small change

Create a branch for your issue, keep the change inside your role, add the needed
tests, and update the task record and status page. Shared information formats need
a reviewed proposal before anyone changes them.

Use the exact [branch
routine](../COLLABORATION_WORKFLOW.md#3-branch-without-shared-state-ambiguity)
and [verified commit and push
routine](../COLLABORATION_WORKFLOW.md#7-commit-and-push-a-verified-checkpoint)
instead of guessing from a generic Git workflow. The full contribution rules are
in [Contributing](../../CONTRIBUTING.md).

## 7. Hand over clear evidence

Record what changed, the commands actually run, whether they passed or failed,
what remains missing, and the exact next step. A plan or successful build is not
proof that the complete project works.
