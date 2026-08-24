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
    events = read("FOUR_HUNDRED_FORTY_SECOND_REVISED_B3_86_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_FORTY_SECOND_REVISED_B3_34_STATEMENTS.tsv")
    tournament = read("FOUR_HUNDRED_FORTY_SECOND_NINE_CARD_TOURNAMENT.tsv")
    dictionary = read("FOUR_HUNDRED_FORTY_SECOND_FINAL_B3_52_CARD_DICTIONARY.tsv")
    local = read("FOUR_HUNDRED_FORTY_SECOND_EIGHT_B3_LOCAL_WHOLE_CARDS.tsv")
    checks = {
        "events_86": len(events) == 86,
        "statements_34": len(statements) == 34,
        "tournament_36": len(tournament) == 36,
        "nine_selected": sum(row["decision"] == "SELECT" for row in tournament) == 9,
        "dictionary_52": len(dictionary) == 52,
        "B3_productive_18": sum(row["drawer"] == "B3_PRODUCTIVE_COMPOSITION" for row in dictionary) == 18,
        "local_8": len(local) == 8,
        "full_rinse_promoted": [row["small_value_de"] for row in events if row["surface"] == "cheeety"] == ["voll spülen"],
        "station_chain_present": all(any(row["small_value_de"] == value for row in events) for value in ("Quellstation", "Absetzmaß", "Auffangpunkt")),
        "every_value": all(row["small_value_de"] for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
