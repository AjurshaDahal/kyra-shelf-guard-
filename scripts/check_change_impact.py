"""Require documentation and status companions for changed repository surfaces."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _is_under(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path == prefix or path.startswith(f"{prefix}/") for prefix in prefixes)


PERSON1_SCRIPTS = frozenset(
    {
        "generate_golden_pack.py",
        "convert_ocid.py",
        "verify_person1.py",
    }
)


def _owner_for(path: str) -> str | None:
    p1_exact = {"src/kyra/io.py", "src/kyra/baseline.py"}
    p4_exact = {"src/kyra/contracts.py", "src/kyra/manifest.py", "src/kyra/cli.py"}
    if path in p1_exact or _is_under(
        path, ("src/kyra/data", "src/kyra/simulation", "src/kyra/calibration")
    ):
        return "PERSON1"
    if _is_under(path, ("src/kyra/geometry", "src/kyra/differencing", "src/kyra/occlusion")):
        return "PERSON2"
    if _is_under(path, ("src/kyra/tracking", "src/kyra/proximity", "src/kyra/rules")):
        return "PERSON3"
    if path in p4_exact or _is_under(path, ("src/kyra/pipeline", "src/kyra/evaluation")):
        return "PERSON4"
    if path.startswith("tests/"):
        name = Path(path).name.lower()
        if any(
            token in name
            for token in (
                "baseline",
                "io",
                "simulation",
                "dataset",
                "ocid",
                "golden",
                "midas",
                "provenance",
            )
        ):
            return "PERSON1"
        if any(token in name for token in ("geometry", "differencing", "occlusion", "volume")):
            return "PERSON2"
        if any(token in name for token in ("tracking", "proximity", "rules", "alert")):
            return "PERSON3"
        return "PERSON4"
    if path.startswith("scripts/"):
        return "PERSON1" if Path(path).name in PERSON1_SCRIPTS else "PERSON4"
    if path.startswith(".github/"):
        return "PERSON4"
    return None


def assess_changes(changed: set[str]) -> list[str]:
    """Return missing companion errors for normalized repository-relative paths."""

    errors: list[str] = []
    implementation = {
        path
        for path in changed
        if path.startswith(("src/", "tests/", "scripts/")) and path.endswith(".py")
    }
    governance = {
        path
        for path in changed
        if path.startswith(".github/")
        or (path.startswith("scripts/") and Path(path).name not in PERSON1_SCRIPTS)
    }
    owners = {owner for path in implementation | governance if (owner := _owner_for(path))}

    if implementation or governance:
        if "CHANGELOG.md" not in changed:
            errors.append("implementation/governance changes require CHANGELOG.md")
        has_work_item = any(
            path.startswith("docs/work-items/") and path.endswith(".md") for path in changed
        )
        if not has_work_item:
            errors.append("implementation/governance changes require a docs/work-items/*.md record")
        for owner in sorted(owners):
            required = f"docs/status/{owner}.md"
            if required not in changed:
                errors.append(f"{owner} changes require {required}")

    shared_contract = bool(
        {"src/kyra/contracts.py", "src/kyra/manifest.py"} & changed
        or any(path.startswith("src/kyra/config") for path in changed)
    )
    if shared_contract:
        for required in ("docs/CONTRACTS.md", "docs/DECISIONS.md"):
            if required not in changed:
                errors.append(f"shared-contract changes require {required}")
        if not any(path.startswith("docs/contract-changes/") for path in changed):
            errors.append(
                "shared-contract changes require an approved docs/contract-changes record"
            )

    dependency_change = bool(
        "pyproject.toml" in changed or any(path.startswith("requirements") for path in changed)
    )
    if dependency_change:
        for required in ("docs/DEVELOPMENT.md", "docs/TESTING.md"):
            if required not in changed:
                errors.append(f"dependency changes require {required}")

    if governance and not ({"AGENTS.md", "CONTRIBUTING.md"} & changed):
        errors.append("governance changes require AGENTS.md or CONTRIBUTING.md")

    return sorted(set(errors))


def changed_files(base: str) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRT", base, "--"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or f"git diff failed for base {base!r}"
        raise RuntimeError(message)
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base", default="HEAD~1", help="Git revision to compare with the worktree"
    )
    args = parser.parse_args()
    try:
        changed = changed_files(args.base)
    except RuntimeError as exc:
        print(f"Change-impact check could not compare revisions: {exc}", file=sys.stderr)
        return 2

    if not changed:
        print(f"Change-impact check passed: no changes relative to {args.base}.")
        return 0

    errors = assess_changes(changed)
    if errors:
        print("Change-impact check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Change-impact check passed for {len(changed)} changed files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
