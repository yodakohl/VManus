#!/usr/bin/env python3
"""Run GDT599's remaining-action object completion."""

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
        "actions": result["action_count"],
        "new_completions": result["gdt599_new_completed_action_count"],
        "remaining": result["remaining_unfilled_action_count"],
        "routes": result["selection_route_profile"],
        "objects": result["object_class_profile"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
