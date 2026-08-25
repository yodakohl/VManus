#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTY_SIXTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixty_sixth.py")], check=True)
    archetypes = read(f"{PREFIX}_4_HERBAL_PREPARATION_ARCHETYPES.tsv")
    matrix = read(f"{PREFIX}_24_PAIR_COMPATIBILITY_MATRIX.tsv")
    selected = read(f"{PREFIX}_6_SELECTED_PROCESS_PAIRINGS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "four_preparations": len(archetypes) == 4 and {row["page"] for row in archetypes} == {"f10r", "f11r", "f55v", "f56r"},
        "complete_matrix": len(matrix) == 24 and all(Counter(row["biological_record"] for row in matrix)[record] == 4 for record in ["B1", "B2", "B3", "B4", "B5", "B6"]),
        "six_selections": len(selected) == 6 and {row["biological_record"] for row in selected} == {"B1", "B2", "B3", "B4", "B5", "B6"},
        "all_preparations_used": {row["primary_preparation_page"] for row in selected} == {"f10r", "f11r", "f55v", "f56r"},
        "score_order": all(int(row["primary_score"]) > int(row["secondary_score"]) for row in selected),
        "no_direct_reference": all(row["direct_product_reference"] == "NO" for row in matrix) and summary["direct_product_references"] == 0,
        "type_not_product": all(row["identity_ceiling"] == "ZUBEREITUNGSART_NICHT_EXAKTES_PRODUKT" for row in selected),
        "no_new_meaning": summary["new_card_meanings"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in matrix + selected + archetypes),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
