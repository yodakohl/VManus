#!/usr/bin/env python3
"""Show the three-channel GDT589 replay for one known carrier governor."""

from __future__ import annotations

import argparse
import json

from replay_lib import build_replay, load_inputs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay one known complete host: gate, ordered carrier slots, and portable reading."
    )
    parser.add_argument("primary_governor_key")
    args = parser.parse_args()
    hosts, slots = build_replay(load_inputs())
    host = next(
        (row for row in hosts if row["primary_governor_key"] == args.primary_governor_key),
        None,
    )
    if host is None:
        raise SystemExit(f"Unknown carrier governor: {args.primary_governor_key}")
    payload = {
        "host": host,
        "ordered_slots": [
            row for row in slots if row["primary_governor_key"] == args.primary_governor_key
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
