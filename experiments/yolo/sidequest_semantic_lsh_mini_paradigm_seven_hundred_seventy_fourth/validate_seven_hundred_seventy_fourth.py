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
    lsh = read("SEVEN_HUNDRED_SEVENTY_FOURTH_LSH_MINI_PARADIGM.tsv")
    cards = read("SEVEN_HUNDRED_SEVENTY_FOURTH_173_UPDATED_CARD_ACCESS.tsv")
    statements = read("SEVEN_HUNDRED_SEVENTY_FOURTH_116_UPDATED_STATEMENT_ACCESS.tsv")
    remaining = read("SEVEN_HUNDRED_SEVENTY_FOURTH_5_REMAINING_MODEL_CARDS.tsv")
    roles = read("SEVEN_HUNDRED_SEVENTY_FOURTH_4_ROLE_COMPONENT_LOADS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTY_FOURTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    role = {row["role"]: row for row in roles}
    checks = {
        "counts_2_173_116_5_4": (len(lsh), len(cards), len(statements), len(remaining), len(roles)) == (2, 173, 116, 5, 4),
        "lsh_three_events_exact": sum(int(row["events"]) for row in lsh) == 3 and all(row["prediction_exact"] == "YES" for row in lsh),
        "lsh_cards_exact": {(row["component_recipe"], row["registered_reading_de"]) for row in lsh} == {("LSH+O", "WASCHEN · ARBEITSGANG"), ("LSH+E+DY", "WASCHEN · KURZ · SCHLUSS")},
        "remaining_split_3_2": (sum(row["register"] == "HERBAL" for row in remaining), sum(row["register"] == "BIO" for row in remaining)) == (3, 2),
        "remaining_five_events": sum(int(row["events"]) for row in remaining) == 5,
        "productive_168_376_111": (summary["productive_cards"], summary["productive_events"], summary["productive_statements"]) == (168, 376, 111),
        "specialists_36_components": int(role["HERBAL_SCRIBE"]["total_prose_components"]) == int(role["BIO_STATION_SCRIBE"]["total_prose_components"]) == 36,
        "master39_astro0": (role["MASTER_CORRECTOR"]["total_prose_components"], role["ASTRO_TABLE_SCRIBE"]["total_prose_components"]) == ("39", "0"),
        "readings_unchanged": all(row["reading_changed"] == "NO" for row in cards),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (lsh, cards, statements, remaining, roles) for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
