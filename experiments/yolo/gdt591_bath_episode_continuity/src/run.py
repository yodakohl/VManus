#!/usr/bin/env python3
"""Compile GDT591 from the fixed GDT590 bath-host population."""

from __future__ import annotations

import json

from continuity_model import STATUS, build, load_inputs, write_built


def main() -> int:
    built = build(load_inputs())
    write_built(built)
    result = built["result"]
    print(
        json.dumps(
            {
                "status": STATUS,
                "bath_hosts": result["bath_host_count"],
                "statements": result["bath_statement_count"],
                "paragraphs": result["bath_paragraph_count"],
                "statement_transitions": result["statement_transition_count"],
                "remote_carriers": result["remote_carrier_count"],
                "e2652_exact_signature_population_count": result[
                    "e2652_exact_signature_population_count"
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
