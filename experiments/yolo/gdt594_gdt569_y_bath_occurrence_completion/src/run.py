#!/usr/bin/env python3
"""Compile GDT594's occurrence-level Y bath-object edition."""

from __future__ import annotations

import json

from model import STATUS, build, load_inputs, write_built


def main() -> int:
    built = build(load_inputs())
    write_built(built)
    print(
        json.dumps(
            {
                "status": STATUS,
                "candidates": built["result"]["candidate_count"],
                "completion_profile": built["result"]["completion_object_profile"],
                "final_profile": built["result"]["final_object_profile"],
                "cold_defaults_remaining": built["result"][
                    "remaining_cold_bath_object_default_count"
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
