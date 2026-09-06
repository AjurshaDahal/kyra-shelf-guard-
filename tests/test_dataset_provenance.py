"""Provenance record schema: licence, checksum, selection, and exclusion rules."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

PROVENANCE_PATH = Path(__file__).parent.parent / "data-sources" / "provenance.json"

REQUIRED_STRING_FIELDS = (
    "source_id",
    "name",
    "official_url",
    "terms_url",
    "selected_subset",
    "conversion_command",
    "output_schema_version",
    "local_path_hint",
    "attribution",
    "status",
    "licence_review_status",
)
REQUIRED_NULLABLE_FIELDS = (
    "source_version",
    "downloaded_filename",
    "downloaded_bytes",
    "published_checksum",
    "computed_sha256",
)
KNOWN_STATUSES = {"pending_download", "retrieved", "converted", "excluded"}
FIELD_MESSAGES = {
    "terms_url": "missing licence/terms information",
    "selected_subset": "missing selection information",
    "conversion_command": "missing conversion command",
    "computed_sha256": "missing checksum information",
}


def _record(overrides: dict[str, object]) -> dict[str, object]:
    record = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))["sources"][0]
    record.update({key: value for key, value in overrides.items() if value is not None})
    for key, value in overrides.items():
        if value is None:
            record.pop(key, None)
    return record


def validate_provenance(record: dict[str, object]) -> list[str]:
    """Return human-readable schema violations for one source record."""
    errors: list[str] = []
    for field in REQUIRED_STRING_FIELDS:
        if field not in record or not str(record[field]).strip():
            errors.append(FIELD_MESSAGES.get(field, f"missing required string field: {field}"))
    for field in REQUIRED_NULLABLE_FIELDS:
        if field not in record:
            errors.append(FIELD_MESSAGES.get(field, f"missing field: {field}"))
    if record.get("status") not in KNOWN_STATUSES:
        errors.append(f"unknown status: {record.get('status')!r}")
    path_hint = str(record.get("local_path_hint", ""))
    if any(marker in path_hint for marker in ("\\Users\\", "/Users/", "C:\\", "C:/")):
        errors.append("local_path_hint must not expose a private home path")
    exclusions = record.get("exclusions")
    if not isinstance(exclusions, list) or not exclusions:
        errors.append("exclusions must be a non-empty list")
    else:
        for index, entry in enumerate(exclusions):
            if not isinstance(entry, dict) or not str(entry.get("reason", "")).strip():
                errors.append(f"exclusions[{index}] must have a reason")
    snapshot = record.get("computed_sha256")
    if snapshot is not None and not (
        isinstance(snapshot, str) and len(snapshot) == 64
    ):
        errors.append("computed_sha256 must be a 64-character hex string when present")
    return errors


def test_committed_provenance_record_is_valid() -> None:
    payload = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    assert payload["schema_version"]
    sources = payload["sources"]
    assert sources, "provenance.json must list at least one source"

    for record in sources:
        assert validate_provenance(record) == []


@pytest.mark.parametrize(
    ("missing", "message"),
    [
        ("terms_url", "terms"),
        ("selected_subset", "selection"),
        ("conversion_command", "conversion"),
        ("computed_sha256", "checksum"),
    ],
)
def test_provenance_rejects_missing_required_information(
    missing: str,
    message: str,
) -> None:
    errors = validate_provenance(_record({missing: None}))

    assert any(message in error for error in errors)


def test_provenance_rejects_blank_exclusion_reason() -> None:
    record = _record({"exclusions": [{"reason": " ", "detail": "x"}]})

    assert any("exclusions[0] must have a reason" in error for error in validate_provenance(record))


def test_provenance_rejects_private_home_path_hint() -> None:
    record = _record({"local_path_hint": "C:\\Users\\workshop\\data"})

    assert any("private home path" in error for error in validate_provenance(record))


def test_provenance_rejects_unknown_status() -> None:
    record = _record({"status": "downloaded_quietly"})

    assert any("unknown status" in error for error in validate_provenance(record))