#!/usr/bin/env python3
"""Compile GDT592's complete bath-object working edition."""

from __future__ import annotations

import json

from object_model import STATUS, build, load_inputs, write_built


def main() -> int:
    built = build(load_inputs())
    write_built(built)
    result = built["result"]
    print(
        json.dumps(
            {
                "status": STATUS,
                "bath_actions": result["bath_action_count"],
                "bath_episodes": result["bath_episode_count"],
                "object_profile": result["object_profile"],
                "clause_patches": result["clause_patch_count"],
                "patched_statements": result["patched_statement_count"],
                "episode_carries": result["episode_carry_count"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
