#!/usr/bin/env python3
"""Build the GDT600 surface-grammar edition."""

from __future__ import annotations

import json

from model import build, load_inputs, write_built


def main() -> int:
    built = build(load_inputs())
    write_built(built)
    result = built["result"]
    print(json.dumps({
        "status": result["status"],
        "hosts": result["host_count"],
        "actions": result["action_count"],
        "statements": result["statement_count"],
        "changed_hosts": result["changed_host_count"],
        "changed_actions": result["changed_action_count"],
        "modifier_reorders": result["modifier_reorder_count"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
