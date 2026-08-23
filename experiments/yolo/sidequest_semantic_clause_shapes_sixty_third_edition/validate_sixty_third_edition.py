#!/usr/bin/env python3
"""Validate the twelve-shape clause reduction."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    shapes = read_tsv("SIXTY_THIRD_12_CLAUSE_SHAPES.tsv")
    mapped = read_tsv("SIXTY_THIRD_381_GROUP_SHAPE_MAP.tsv")
    chains = read_tsv("SIXTY_THIRD_16_COMPRESSION_CHAINS.tsv")
    checks = {
        "twelve_shapes": len(shapes) == 12,
        "shape_ids_unique": len({row["shape_id"] for row in shapes}) == 12,
        "every_shape_observed": all(int(row["observed_group_count"]) > 0 for row in shapes),
        "381_groups": len(mapped) == 381,
        "source_group_ids_unique": len({row["source_group_id"] for row in mapped}) == 381,
        "all_groups_assigned": all(row["clause_shape_id"] and row["clause_shape_family"] for row in mapped),
        "mapped_counts_equal_shape_counts": Counter(row["clause_shape_id"] for row in mapped) == Counter({row["shape_id"]: int(row["observed_group_count"]) for row in shapes}),
        "sixteen_chains": len(chains) == 16,
        "chain_units_unique": len({row["unit_id"] for row in chains}) == 16,
        "all_chain_layers_present": all(all(row[key].strip() for key in ("natural_source_prose_de", "terse_source_formular_de", "slot_program", "clause_shape_program", "atom_sequence", "visible_surface")) for row in chains),
        "allowed_pages_only": {row["page"] for row in mapped + chains} <= ALLOWED,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in mapped + chains + shapes),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
