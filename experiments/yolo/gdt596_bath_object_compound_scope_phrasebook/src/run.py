#!/usr/bin/env python3
"""Build the GDT596 compound/scope phrasebook."""

from __future__ import annotations

import json

from model import STATUS, build, load_inputs, write_built


def main() -> int:
    built = build(load_inputs())
    write_built(built)
    result = built["result"]
    print(json.dumps({
        "status": STATUS,
        "actions": result["action_count"],
        "exact_replays": result["exact_replay_count"],
        "typing_cards": result["typing_card_count"],
        "reference_scope_cards": result["reference_scope_card_count"],
        "primitives": result["phrasebook_primitive_count"],
        "exceptions": result["exception_count"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
