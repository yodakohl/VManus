#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTY_THIRD"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_forty_third.py")], check=True)
    cards = read("10_MIXED_TIER_CARDS.tsv")
    events = read("20_MIXED_TIER_EVENTS.tsv")
    statements = read("18_MIXED_TIER_STATEMENTS.tsv")
    contexts = read("2_DAVON_CONTEXTS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "tier_inventory": len(cards) == 10 and len(events) == 20 and len(statements) == 18,
        "frequency_ranks": [int(row["frequency_rank"]) for row in cards] == list(range(31, 41)),
        "mixed_modes": sum(row["learning_mode"] == "COMPOSE_COMPONENTS" for row in cards) == 9 and sum(row["learning_mode"] == "MEMORIZE_WHOLE_CARD" for row in cards) == 1,
        "whole_card_identity": next(row for row in cards if row["learning_mode"] == "MEMORIZE_WHOLE_CARD")["surfaces"] == "dchol|schol" and next(row for row in cards if row["learning_mode"] == "MEMORIZE_WHOLE_CARD")["portable_workshop_paraphrase_de"] == "davon",
        "davon_contexts": len(contexts) == 2 and {row["page"] for row in contexts} == {"f11r", "f56r"} and {row["record"] for row in contexts} == {"H3", "H5"},
        "davon_same_role": all(row["antecedent"] == "CURRENT_PREPARED_MATERIAL_IN_SAME_HERBAL_RECORD" and row["decision"] == "KEEP_DAVON_WHOLE_ANAPHOR" for row in contexts),
        "register_correction": summary["davon_registers"] == ["HERBAL"] and summary["register_correction"] == "BOTH_DAVON_EVENTS_ARE_HERBAL_NOT_HERBAL_PLUS_BIOLOGICAL",
        "full_scope": len({row["page"] for row in events}) == 7 and len({row["record"] for row in events}) == 10,
        "cumulative_coverage": summary["cumulative_top40_events"] == 237,
        "no_component_change": summary["component_changes"] == 0,
        "allowed_pages": {row["page"] for row in events + statements + contexts} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
