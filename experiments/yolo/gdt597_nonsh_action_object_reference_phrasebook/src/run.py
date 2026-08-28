#!/usr/bin/env python3
"""Build the provisional GDT597 non-SH object/reference phrasebook."""

from __future__ import annotations

import json

from model import build, load_inputs, write_built


def main() -> int:
    built = build(load_inputs())
    write_built(built)
    result = built["result"]
    print(json.dumps({
        "status": result["status"],
        "actions": result["action_count"],
        "written": result["written_action_count"],
        "left": result["left_reference_count"],
        "right": result["right_reference_count"],
        "defaults": result["action_default_count"],
        "review": result["long_reference_review_count"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
