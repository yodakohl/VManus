#!/usr/bin/env python3
"""Run GDT598's combined six-page statement integration."""

from __future__ import annotations

import json

from model import build, load_inputs, write_built


def main() -> int:
    built = build(load_inputs())
    write_built(built)
    result = built["result"]
    print(json.dumps({
        "status": result["status"],
        "statements": result["statement_count"],
        "hosts": result["host_count"],
        "actions": result["action_count"],
        "completed": result["completed_object_action_count"],
        "remaining": result["remaining_action_gap_count"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
