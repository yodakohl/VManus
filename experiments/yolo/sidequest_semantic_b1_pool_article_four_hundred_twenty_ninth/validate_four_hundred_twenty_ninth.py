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
    events = read("FOUR_HUNDRED_TWENTY_NINTH_B1_66_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_TWENTY_NINTH_B1_21_STATEMENTS.tsv")
    transfer = read("FOUR_HUNDRED_TWENTY_NINTH_TEN_TRANSFERRED_EXACT_CARDS.tsv")
    local = read("FOUR_HUNDRED_TWENTY_NINTH_B1_LOCAL_DECK.tsv")
    models = read("FOUR_HUNDRED_TWENTY_NINTH_THREE_B1_MODELS.tsv")
    checks = {
        "sixty_six_events": len(events) == 66,
        "exact_event_range": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(101, 167)],
        "every_event_value": all(row["small_value_de"] for row in events),
        "twenty_one_statements": len(statements) == 21,
        "statement_event_sum": sum(int(row["events"]) for row in statements) == 66,
        "ten_transferred_cards": len(transfer) == 10,
        "twenty_three_transferred_events": sum(int(row["B1_events"]) for row in transfer) == 23,
        "source_count_matches": sum(row["lexicon_source"] == "HERBAL_EXACT_CARD_TRANSFER" for row in events) == 23,
        "local_card_count_matches": len(local) == len({row["joint_tuple_id"] for row in events if row["lexicon_source"] == "B1_LEARNED_LOCAL_CARD"}),
        "three_models": len(models) == 3,
        "pool_model_selected": [row["model"] for row in models if row["decision"] == "SELECT"] == ["SHARED_POOL_WORKSTATION"],
        "sealed_pages_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
