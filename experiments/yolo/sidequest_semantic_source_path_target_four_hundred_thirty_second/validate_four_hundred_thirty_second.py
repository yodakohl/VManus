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
    events = read("FOUR_HUNDRED_THIRTY_SECOND_REVISED_B1_66_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_SECOND_REVISED_B1_21_STATEMENTS.tsv")
    lexicon = read("FOUR_HUNDRED_THIRTY_SECOND_SOURCE_PATH_TARGET_LEXICON.tsv")
    audit = read("FOUR_HUNDRED_THIRTY_SECOND_SIX_CARD_OCCURRENCE_AUDIT.tsv")
    checks = {
        "B1_events_66": len(events) == 66,
        "B1_statements_21": len(statements) == 21,
        "lexicon_9": len(lexicon) == 9,
        "audit_6_cards": len(audit) == 6,
        "audit_16_occurrences": sum(int(row["events"]) for row in audit) == 16,
        "otar_source_not_second_outlet": [row["small_value_de"] for row in events if row["surface"] == "otar"] == ["danach von dort"],
        "schedy_concrete_transfer": [row["small_value_de"] for row in events if row["surface"] == "schedy"] == ["überführen; Schluss"],
        "three_strain_occurrences": [row for row in audit if row["joint_tuple_id"] == "d68bc8de3bcee09db23c"][0]["events"] == "3",
        "all_values": all(row["small_value_de"] for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTY_SECOND_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
