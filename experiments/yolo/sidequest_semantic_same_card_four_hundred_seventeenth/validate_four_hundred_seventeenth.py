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
    occ = read("FOUR_HUNDRED_SEVENTEENTH_FIVE_SAME_OCCURRENCES.tsv")
    models = read("FOUR_HUNDRED_SEVENTEENTH_FOUR_SAME_MODELS.tsv")
    statements = read("FOUR_HUNDRED_SEVENTEENTH_FIVE_REVISED_STATEMENTS.tsv")
    renderer = read("FOUR_HUNDRED_SEVENTEENTH_THREE_RENDERER_FORMS.tsv")
    checks = {
        "five_occurrences": len(occ) == 5,
        "five_records": len({row["record"] for row in occ}) == 5,
        "one_exact_card": len({row["joint_tuple_id"] for row in occ}) == 1,
        "portable_value_same": {row["portable_value_de"] for row in occ} == {"dasselbe"},
        "four_models": len(models) == 4,
        "same_selected": [row["candidate"] for row in models if row["decision"] == "SELECT_SHORTEST"] == ["DASSELBE"],
        "five_statements": len(statements) == 5,
        "three_renderer_forms": len(renderer) == 3,
        "renderer_counts_sum": sum(int(row["events"]) for row in renderer) == 5,
        "renderer_meaning_invariant": {row["meaning_de"] for row in renderer} == {"dasselbe"},
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (occ, models, statements, renderer) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
