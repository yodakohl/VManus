#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    occ = read("FOUR_HUNDRED_FOURTEENTH_OTYTCHOL_OCCURRENCE.tsv")
    models = read("FOUR_HUNDRED_FOURTEENTH_FOUR_PRODUCT_MODELS.tsv")
    module = read("FOUR_HUNDRED_FOURTEENTH_SIX_CARD_EXTRACTION_MODULE.tsv")
    contrasts = read("FOUR_HUNDRED_FOURTEENTH_FOUR_COLLECTION_CONTRASTS.tsv")
    checks = {
        "one_target": len(occ) == 1 and occ[0]["event_id"] == "E007",
        "whole_card": occ[0]["composition"].startswith("MEMORIZED_WHOLE_CARD"),
        "extract_selected": occ[0]["selected_whole_word_de"] == "Auszug",
        "four_models": len(models) == 4,
        "one_selected": [row["candidate"] for row in models if row["decision"] == "SELECT"] == ["AUSZUG"],
        "six_module_cards": len(module) == 6,
        "module_order": [row["event_id"] for row in module] == ["E004", "E005", "E006", "E007", "E008", "E009"],
        "four_contrasts": len(contrasts) == 4,
        "otytchol_distinct_from_qotchol": contrasts[0]["selected_value_de"] != contrasts[1]["selected_value_de"],
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (occ, models, module, contrasts) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FOURTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
