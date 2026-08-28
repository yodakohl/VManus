#!/usr/bin/env python3
"""Compile GDT590 from the fixed no-new-page GDT589 base."""

from __future__ import annotations

import json

from bath_model import STATUS, build, load_inputs, write_built


def main() -> int:
    built = build(load_inputs())
    write_built(built)
    print(
        json.dumps(
            {
                "status": STATUS,
                "targets": built["result"]["target_host_count"],
                "bath_y_hosts": built["result"]["bath_y_host_count"],
                "changed_slots": built["result"]["changed_slot_count"],
                "changed_statements": built["result"]["changed_statement_count"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
