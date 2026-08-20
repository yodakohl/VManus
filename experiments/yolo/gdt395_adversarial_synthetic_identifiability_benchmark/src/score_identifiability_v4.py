#!/usr/bin/env python3
"""Canonical opaque-set partition correction for GDT395 scoring."""

from __future__ import annotations

import score_identifiability_v3 as v3

v1 = v3.v1


def parse_oracle_partition_v4(value: object, label: str) -> str | None:
    atoms = v1.parse_oracle_pipe(value, label)
    if not atoms:
        return None
    return "|".join(atoms)


def main() -> int:
    v1.open_tsv = v3.open_tsv_v3
    v1.parse_bool = v3.parse_world_boolean_v3
    v1.architecture_scores = v3.architecture_scores_v3
    v1.parse_oracle_scalar = parse_oracle_partition_v4
    return v1.main()


if __name__ == "__main__":
    raise SystemExit(main())

