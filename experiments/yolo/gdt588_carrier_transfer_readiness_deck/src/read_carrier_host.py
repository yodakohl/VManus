#!/usr/bin/env python3
"""Run one complete, already-segmented host through the future GDT588 bridge."""

from __future__ import annotations

import argparse
import json

from transfer_lib import future_host_reading


def comma_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Select a portable GDT583 rule and bounded GDT587 noun defaults."
    )
    parser.add_argument("--action-root", required=True, choices=("T", "SH", "CHD", "S"))
    parser.add_argument("--register", required=True)
    parser.add_argument(
        "--carrier-roots",
        required=True,
        help="comma-separated written carrier sequence; repeats must be retained",
    )
    parser.add_argument("--direct-tokens", default="")
    parser.add_argument("--host-tokens", required=True)
    parser.add_argument("--previous-action", default="NONE")
    parser.add_argument("--next-action", default="NONE")
    parser.add_argument("--source-id", default="FUTURE_UNRELEASED_HOST")
    parser.add_argument("--physical-page", default="UNRELEASED")
    args = parser.parse_args()
    result = future_host_reading(
        action_root=args.action_root,
        register=args.register,
        carrier_roots=comma_list(args.carrier_roots),
        direct_tokens=comma_list(args.direct_tokens),
        host_tokens=comma_list(args.host_tokens),
        previous_action=args.previous_action,
        next_action=args.next_action,
        source_id=args.source_id,
        physical_page=args.physical_page,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
