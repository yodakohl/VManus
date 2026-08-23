#!/usr/bin/env python3
"""Validate reverse decompression coverage and layer separation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    groups = read_tsv("SIXTY_FOURTH_381_REVERSE_DECOMPRESSION.tsv")
    chains = read_tsv("SIXTY_FOURTH_16_REVERSE_CHAINS.tsv")
    checks = {
        "381_groups": len(groups) == 381,
        "group_ids_unique": len({row["source_group_id"] for row in groups}) == 381,
        "all_structural_readbacks_complete": all(row["structural_readback_complete"] == "YES" for row in groups),
        "component_status_exhaustive": {row["component_status"] for row in groups} <= {"PRODUCTIVE_COMPONENTS", "LEARNED_BODY_PRESENT"},
        "component_partition_complete": sum(row["component_status"] == "PRODUCTIVE_COMPONENTS" for row in groups) + sum(row["component_status"] == "LEARNED_BODY_PRESENT" for row in groups) == 381,
        "sixteen_chains": len(chains) == 16,
        "chain_ids_unique": len({row["unit_id"] for row in chains}) == 16,
        "all_reverse_layers_present": all(all(row[key].strip() for key in ("visible_surface_input", "recovered_atom_sequence", "recovered_clause_shapes", "recovered_slot_program", "dictionary_only_readback_de", "owner_augmented_readback_de", "full_master_source_de")) for row in chains),
        "layer_requirements_explicit": all(row["construction_recovery"].startswith("DIRECT") and row["short_card_recovery"].startswith("REQUIRES") and row["concrete_owner_recovery"].startswith("REQUIRES") and row["full_source_recovery"].startswith("REQUIRES") for row in chains),
        "allowed_pages_only": {row["page"] for row in groups + chains} <= ALLOWED,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in groups + chains),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
