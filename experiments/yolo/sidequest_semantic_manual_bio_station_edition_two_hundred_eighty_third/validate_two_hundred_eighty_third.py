#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    statements = read("TWO_HUNDRED_EIGHTY_THIRD_97_STATION_TRANSLATIONS.tsv")
    records = read("TWO_HUNDRED_EIGHTY_THIRD_SIX_BIO_NARRATIVES.tsv")
    resets = read("TWO_HUNDRED_EIGHTY_THIRD_FOUR_OWNER_RESETS.tsv")
    checks = {
        "statement_count_97": len(statements) == 97,
        "record_count_6": len(records) == 6,
        "event_count_281": sum(len(r["surface_sequence"].split(" · ")) for r in statements) == 281,
        "statement_ids_unique": len({r["statement_id"] for r in statements}) == 97,
        "records_exact": Counter(r["record_unit_id"] for r in statements) == Counter({"B1": 21, "B2": 22, "B3": 34, "B4": 16, "B5": 3, "B6": 1}),
        "pages_exact": {r["page"] for r in statements} == {"f81v", "f82r", "f83r"},
        "owner_resets_4": len(resets) == 4,
        "owner_reset_ids_exact": {r["statement_id"] for r in resets} == {"B2-S012", "B3-S016", "B3-S026", "B4-S015"},
        "all_translations_concrete": all(r["station_translation_de"].strip() for r in statements),
        "all_local_only": all(r["global_flow_policy"] == "LOCAL_STATION_ONLY__NO_GLOBAL_CIRCUIT" for r in statements),
        "closed_open_85_12": Counter(r["terminal_status"] for r in statements) == Counter({"CLOSED": 85, "OPEN": 12}),
        "no_sealed_page": all("f84" not in "\t".join(r.values()).lower() for r in statements + records + resets),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
