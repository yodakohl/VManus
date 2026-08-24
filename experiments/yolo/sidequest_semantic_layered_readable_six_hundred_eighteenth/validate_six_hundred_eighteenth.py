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
    cases = read("SIX_HUNDRED_EIGHTEENTH_6_CASE_NOUN_LEDGER.tsv")
    events = read("SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    statements = read("SIX_HUNDRED_EIGHTEENTH_116_LAYERED_STATEMENTS.tsv")
    records = read("SIX_HUNDRED_EIGHTEENTH_11_RECORD_LAYERED_SUMMARY.tsv")
    checks = {
        "cases6": len(cases) == 6 and {row["case_id"] for row in cases} == {f"C{i}" for i in range(1, 7)},
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "cards173": len({row["card_no"] for row in events}) == 173,
        "commands163": len({(row["semantic_component_parse"], row["standard_command_de"]) for row in events}) == 163,
        "no_hidden_substance": all(row["card_word_contains_concrete_substance"] == "NO" for row in events),
        "statements116": len(statements) == 116 and sum(int(row["event_count"]) for row in statements) == 381,
        "four_layers_full": all(all(row[key].strip() for key in ["layer_1_card_command_de", "layer_2_image_owner_or_station_de", "layer_3_case_material_de", "layer_4_application_context_de"]) for row in statements),
        "records11": len(records) == 11 and sum(int(row["events"]) for row in records) == 381,
        "b6_no_herbal": next(row for row in cases if row["case_id"] == "C6")["preparation_record"] == "NONE",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_EIGHTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
