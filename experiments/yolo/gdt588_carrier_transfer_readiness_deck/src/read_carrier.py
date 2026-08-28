#!/usr/bin/env python3
"""Read one already-parsed future carrier through the fixed GDT587 model."""

from __future__ import annotations

import argparse
import json

from transfer_lib import intake_reading


def comma_set(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply GDT587 nouns without parsing a new surface or changing the model."
    )
    parser.add_argument("--register", required=True)
    parser.add_argument("--rule", required=True, help="fixed GDT584 action rule")
    parser.add_argument("--root", required=True, help="one of Y, AIIN, AIN, OR")
    parser.add_argument("--roots", required=True, help="comma-separated carrier roots at the host")
    parser.add_argument(
        "--host-values",
        required=True,
        help="comma-separated complete fixed host values, including carrier roots and blockers",
    )
    parser.add_argument("--source-page", default="UNRELEASED")
    args = parser.parse_args()
    result = intake_reading(
        register=args.register,
        rule=args.rule,
        root=args.root,
        roots=comma_set(args.roots),
        host_values=comma_set(args.host_values),
        source_page=args.source_page,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
