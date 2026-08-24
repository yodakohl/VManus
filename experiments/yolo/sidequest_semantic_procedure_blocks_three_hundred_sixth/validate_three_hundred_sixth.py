#!/usr/bin/env python3
"""Validate statement phases and procedure blocks."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    statements = read("THREE_HUNDRED_SIXTH_116_STATEMENT_PHASES.tsv")
    boundaries = read("THREE_HUNDRED_SIXTH_105_STATEMENT_BOUNDARIES.tsv")
    blocks = read("THREE_HUNDRED_SIXTH_EIGHT_PROCEDURE_BLOCKS.tsv")
    pairs = Counter(r["dominant_pair"] for r in boundaries)
    checks = {
        "statements_116": len(statements) == 116,
        "boundaries_105": len(boundaries) == 105,
        "blocks_8": len(blocks) == 8,
        "block_statements_18": sum(int(r["statement_count"]) for r in blocks) == 18,
        "transfer_transfer_7": pairs["TRANSFER>TRANSFER"] == 7,
        "measure_apply_2": pairs["MEASURE_STAGE>APPLY_CONTACT"] == 2,
        "transfer_apply_2": pairs["TRANSFER>APPLY_CONTACT"] == 2,
        "b3_four_transfer": any(r["record_unit_id"] == "B3" and r["first_statement"] == "B3-S022" and r["last_statement"] == "B3-S025" and r["statement_count"] == "4" for r in blocks),
        "all_blocks_pure": all(r["dominant_phase"] != "MIXED" for r in blocks),
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*") if p.suffix in {".tsv", ".md"}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
