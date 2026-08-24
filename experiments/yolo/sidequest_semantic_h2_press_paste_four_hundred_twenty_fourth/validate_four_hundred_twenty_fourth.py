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
    events = read("FOUR_HUNDRED_TWENTY_FOURTH_H2_24_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_TWENTY_FOURTH_H2_THREE_STATEMENTS.tsv")
    graph = read("FOUR_HUNDRED_TWENTY_FOURTH_H2_SPLIT_REJOIN_GRAPH.tsv")
    models = read("FOUR_HUNDRED_TWENTY_FOURTH_FOUR_FINAL_PRODUCT_MODELS.tsv")
    comparison = read("FOUR_HUNDRED_TWENTY_FOURTH_H2_H3_MULTIPRODUCT_COMPARISON.tsv")
    checks = {
        "twenty_four_events": len(events) == 24,
        "exact_event_range": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(15, 39)],
        "every_value_nonempty": all(row["selected_small_value_de"] for row in events),
        "three_statements": len(statements) == 3,
        "seven_graph_steps": len(graph) == 7,
        "two_split_products": len([row for row in events if row["product_register"].startswith("PRODUCT_")]) == 2,
        "two_rejoin_preparations": len([row for row in events if row["product_register"].endswith("_REJOIN")]) == 2,
        "four_product_models": len(models) == 4,
        "paste_selected": [row["candidate"] for row in models if row["decision"] == "SELECT"] == ["PASTE"],
        "two_record_comparison": len(comparison) == 2,
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (events, statements, graph, models, comparison) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
