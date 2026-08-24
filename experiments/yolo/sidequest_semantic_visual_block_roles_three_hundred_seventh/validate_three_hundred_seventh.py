#!/usr/bin/env python3
"""Validate visual binding of the eight procedure blocks."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    blocks = read("THREE_HUNDRED_SEVENTH_EIGHT_VISUAL_BLOCK_ROLES.tsv")
    statements = read("THREE_HUNDRED_SEVENTH_18_STATEMENT_VISUAL_BINDINGS.tsv")
    checks = {
        "blocks_8": len(blocks) == 8 and len({r["block_id"] for r in blocks}) == 8,
        "statements_18": len(statements) == 18 and len({r["statement_id"] for r in statements}) == 18,
        "all_statements_once": sum(int(r["statement_count"]) for r in blocks) == 18,
        "all_roles_concrete": all(r["selected_station_role"].strip() and r["selected_block_reading_de"].strip() for r in blocks),
        "all_visual_objects": all(r["visible_object_de"].strip() and r["visible_geometry_de"].strip() for r in blocks),
        "repair_range": all(0 <= int(r["repair_cost_0_3"]) <= 3 for r in blocks),
        "gap_blocks_preserved": {r["block_id"] for r in blocks if "ungelöster Zwischenposten" in r["visible_object_de"]} == {"PB05", "PB06"},
        "no_global_flow_claim": all("GLOBAL" not in r["selected_station_role"] for r in blocks),
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*") if p.suffix in {".tsv", ".md"}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
