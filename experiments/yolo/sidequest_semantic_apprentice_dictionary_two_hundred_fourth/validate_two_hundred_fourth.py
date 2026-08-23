#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def artifact_hashes() -> dict[str, str]:
    names = [
        "TWO_HUNDRED_FOURTH_COMPONENT_LEXICON.tsv",
        "TWO_HUNDRED_FOURTH_FIVE_FIELD_MODES.tsv",
        "TWO_HUNDRED_FOURTH_22_WHOLE_CARD_DECK.tsv",
        "TWO_HUNDRED_FOURTH_173_CARD_APPRENTICE_INDEX.tsv",
        "BUILD_SUMMARY.json",
    ]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    components = read("TWO_HUNDRED_FOURTH_COMPONENT_LEXICON.tsv")
    modes = read("TWO_HUNDRED_FOURTH_FIVE_FIELD_MODES.tsv")
    whole = read("TWO_HUNDRED_FOURTH_22_WHOLE_CARD_DECK.tsv")
    index = read("TWO_HUNDRED_FOURTH_173_CARD_APPRENTICE_INDEX.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "29_components": len(components) == 29 and len({row["component"] for row in components}) == 29,
        "five_field_modes": len(modes) == 5 and {row["field_mode"] for row in modes} == {"CH", "D", "O", "Q", "S"},
        "22_whole_cards": len(whole) == 22 and len({row["master_card_id"] for row in whole}) == 22,
        "173_card_index": len(index) == 173 and len({row["master_card_id"] for row in index}) == 173,
        "every_row_has_example": all(row["example_event"].startswith("E") and row["example_statement"] for row in index),
        "whole_deck_matches_index": {row["master_card_id"] for row in whole} == {row["master_card_id"] for row in index if row["learning_mode"] == "GANZKARTE_LERNEN"},
        "short_values": all(0 < len(row["value_de"].split()) <= 3 for row in index),
        "component_examples_real": all(int(row["card_types"]) > 0 and int(row["visible_events"]) > 0 for row in components),
        "all_drawers_named": all(row["drawer"] and row["visible_components"] for row in index),
        "381_source_events": summary["events"] == 381,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (components, modes, whole, index) for row in rows for value in row.values()),
    }
    first = artifact_hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_fourth.py")], check=True)
    second = artifact_hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
