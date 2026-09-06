"""Generate the offline Person 1 candidate golden scenario pack."""

from __future__ import annotations

import argparse
from pathlib import Path

from kyra.golden_pack import generate_golden_pack


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination",
        type=Path,
        help="new or empty output directory; existing files are never overwritten",
    )
    args = parser.parse_args()
    root = generate_golden_pack(args.destination)
    print(f"Generated candidate golden pack: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
