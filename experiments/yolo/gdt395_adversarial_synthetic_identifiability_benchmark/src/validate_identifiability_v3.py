#!/usr/bin/env python3
"""Case-insensitive held-oracle Boolean gate for GDT395 validation."""

from __future__ import annotations

import validate_identifiability_v2 as v2

v1 = v2.v1


def validate_oracle_partition_fields_v3(row: dict[str, str]) -> None:
    for field in v1.ORACLE_FIELDS:
        value = row[field]
        if value is None or value == "" or value == v1.UNRESOLVED:
            v1.fail("ORACLE_VALUE_GATE")
        if field not in {"corpus_seed", "productive_morphology"}:
            v1.valid_pipe_value(value, "ORACLE_PIPE_GATE")
    if row["productive_morphology"].upper() not in {"TRUE", "FALSE"}:
        v1.fail("ORACLE_BOOLEAN_GATE")
    for field in v1.TRUTH_CLUSTER_FIELDS:
        v1.valid_pipe_value(row[field], "ORACLE_CLUSTER_TRUTH_GATE")


def main() -> int:
    v1.validate_oracle_scalar_fields = validate_oracle_partition_fields_v3
    return v1.main()


if __name__ == "__main__":
    raise SystemExit(main())

