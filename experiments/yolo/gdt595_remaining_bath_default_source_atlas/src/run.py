#!/usr/bin/env python3
"""Compile GDT595's fully specific bath-object working edition."""

from __future__ import annotations

import json

from model import STATUS, build, load_inputs, write_built


def main() -> int:
    built = build(load_inputs())
    write_built(built)
    print(json.dumps({
        "status": STATUS,
        "source_cards": built["result"]["cold_source_card_count"],
        "propagations": built["result"]["dependent_carry_propagation_count"],
        "final_profile": built["result"]["final_object_profile"],
        "cold_remaining": built["result"]["remaining_cold_bath_object_default_count"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
