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
    occ = read("FOUR_HUNDRED_THIRTEENTH_OS_OCCURRENCE.tsv")
    vessels = read("FOUR_HUNDRED_THIRTEENTH_SIX_VESSEL_CARDS.tsv")
    models = read("FOUR_HUNDRED_THIRTEENTH_FOUR_OS_MODELS.tsv")
    h1 = read("FOUR_HUNDRED_THIRTEENTH_H1_TEN_EVENT_CHAIN.tsv")
    checks = {
        "one_os_occurrence": len(occ) == 1,
        "os_is_whole_card": occ[0]["composition"] == "MEMORIZED_WHOLE_CARD__NOT_O_PLUS_S",
        "topf_selected": occ[0]["selected_whole_word_de"] == "Topf",
        "six_vessel_cards": len(vessels) == 6,
        "vessel_ids_distinct": len({row["joint_tuple_id"] for row in vessels}) == 6,
        "no_shared_stem_claim": {row["shared_visible_stem_claim"] for row in vessels} == {"NONE__LEARNED_VESSEL_DECK"},
        "four_models": len(models) == 4,
        "one_selected_word": [row["candidate"] for row in models if row["decision"] == "SELECT_WORD"] == ["TOPF"],
        "ten_h1_events": len(h1) == 10,
        "h1_event_order": [row["event_id"] for row in h1] == [f"E{i:03d}" for i in range(1, 11)],
        "one_container_role": sum(row["role_in_chain"] == "CONTAINER" for row in h1) == 1,
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (occ, vessels, models, h1) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
