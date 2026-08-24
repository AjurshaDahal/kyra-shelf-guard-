"""Validate the durable collaboration controls and local Markdown links."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "llms.txt",
    "docs/PROJECT_CHARTER.md",
    "docs/TEAM_OWNERSHIP.md",
    "docs/COLLABORATION_WORKFLOW.md",
    "docs/PROJECT_STATUS.md",
    "docs/INTEGRATION_GATES.md",
    "docs/CONTRACTS.md",
    "docs/CONTRACT_CHANGE_PROCESS.md",
    "docs/DOCUMENTATION_POLICY.md",
    "docs/DECISIONS.md",
    "docs/TESTING.md",
    "docs/status/PERSON1.md",
    "docs/status/PERSON2.md",
    "docs/status/PERSON3.md",
    "docs/status/PERSON4.md",
    "docs/work-items/README.md",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/workflows/ci.yml",
    ".github/workflows/pr-governance.yml",
)

STATUS_HEADINGS = (
    "## Implemented",
    "## Active",
    "## Blocked or pending",
    "## Next",
    "## Evidence",
)
ALLOWED_STATUSES = {
    "Not started",
    "Ready",
    "In progress",
    "Blocked",
    "In review",
    "Complete",
}
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _markdown_files(root: Path) -> list[Path]:
    files = list(root.glob("*.md"))
    for directory in (root / "docs", root / ".github"):
        if directory.exists():
            files.extend(directory.rglob("*.md"))
    return sorted(set(files))


def _link_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for document in _markdown_files(root):
        text = _read(document)
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            resolved = (document.parent / target).resolve()
            if not resolved.exists():
                relative_document = document.relative_to(root).as_posix()
                errors.append(f"{relative_document}: broken relative link {raw_target!r}")
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    """Return consistency errors without mutating the repository."""

    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    ownership_path = root / "docs/TEAM_OWNERSHIP.md"
    if ownership_path.is_file():
        ownership = _read(ownership_path)
        for person in range(1, 5):
            if f"Person {person}" not in ownership:
                errors.append(f"docs/TEAM_OWNERSHIP.md: Person {person} is missing")

    status_path = root / "docs/PROJECT_STATUS.md"
    if status_path.is_file():
        status = _read(status_path)
        for identifier in ("P1", "P2", "P3", "P4", "G1", "G2", "G3", "G4", "G5", "G6", "G7"):
            if not re.search(rf"\|\s*{identifier}(?:\s|—)", status):
                errors.append(f"docs/PROJECT_STATUS.md: status row {identifier} is missing")

    for person in range(1, 5):
        relative = f"docs/status/PERSON{person}.md"
        path = root / relative
        if not path.is_file():
            continue
        text = _read(path)
        match = re.search(r"\*\*Status:\*\*\s*([^\r\n]+)", text)
        current_status = match.group(1).strip() if match else ""
        if current_status not in ALLOWED_STATUSES:
            errors.append(f"{relative}: invalid or missing status {current_status!r}")
        if not re.search(r"\*\*Last updated:\*\*\s*\d{4}-\d{2}-\d{2}", text):
            errors.append(f"{relative}: missing YYYY-MM-DD last-updated date")
        for heading in STATUS_HEADINGS:
            if heading not in text:
                errors.append(f"{relative}: missing heading {heading!r}")

    agents_path = root / "AGENTS.md"
    if agents_path.is_file():
        agents = _read(agents_path)
        for token in (
            "Mandatory preflight",
            "TEAM_OWNERSHIP.md",
            "PROJECT_STATUS.md",
            "check_repo_consistency.py",
            "check_change_impact.py",
        ):
            if token not in agents:
                errors.append(f"AGENTS.md: required control reference {token!r} is missing")

    index_path = root / "llms.txt"
    if index_path.is_file():
        index = _read(index_path)
        for token in (
            "PROJECT_CHARTER.md",
            "TEAM_OWNERSHIP.md",
            "PROJECT_STATUS.md",
            "CONTRACTS.md",
            "INTEGRATION_GATES.md",
        ):
            if token not in index:
                errors.append(f"llms.txt: authoritative document {token!r} is not indexed")

    errors.extend(_link_errors(root))
    return sorted(set(errors))


def main() -> int:
    errors = validate_repository()
    if errors:
        print("Repository consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Repository consistency check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
