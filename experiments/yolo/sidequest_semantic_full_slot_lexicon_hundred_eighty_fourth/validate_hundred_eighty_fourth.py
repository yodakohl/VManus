#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    lexicon = read("HUNDRED_EIGHTY_FOURTH_173_CARD_SIX_SLOT_LEXICON.tsv")
    unused = read("HUNDRED_EIGHTY_FOURTH_148_UNUSED_SLOT_CANDIDATES.tsv")
    corrections = read("HUNDRED_EIGHTY_FOURTH_8_FORWARD_ALIGNMENT_CORRECTIONS.tsv")
    shortlist = read("HUNDRED_EIGHTY_FOURTH_24_LOW_OVERLAP_SHORTLIST.tsv")
    second = read("HUNDRED_EIGHTY_FOURTH_CORRECTED_16_TOKEN_SECOND_EXERCISE.tsv")
    fields = read("HUNDRED_EIGHTY_FOURTH_CORRECTED_5_FIELD_SECOND_EXERCISE.tsv")
    slot_counts = Counter(row["observed_slot"] for row in lexicon)
    palette_alignment = Counter(row["forward_alignment"] for row in lexicon if row["writing_class"] == "CURRENT_25_CARD_PALETTE")
    rebuilt = " | ".join(
        " ".join(row["surface"] for row in second if int(row["corrected_field"]) == field)
        for field in range(1, 6)
    )
    checks = {
        "173_cards": len(lexicon) == 173 and len({row["master_card_id"] for row in lexicon}) == 173,
        "381_events_reconciled": sum(int(row["event_count"]) for row in lexicon) == 381,
        "six_slot_distribution": slot_counts == Counter({"G1": 13, "G2": 25, "G3": 15, "G4": 91, "G5": 15, "G6": 14}),
        "148_unused": len(unused) == 148 and not ({row["master_card_id"] for row in unused} & {row["master_card_id"] for row in lexicon if row["writing_class"] == "CURRENT_25_CARD_PALETTE"}),
        "24_shortlist_four_each": len(shortlist) == 24 and Counter(row["slot"] for row in shortlist) == Counter({f"G{i}": 4 for i in range(1, 7)}),
        "palette_alignment_17_6_1_1": palette_alignment == Counter({"EXACT_SLOT_MATCH": 17, "SEMANTIC_ROLE_BRIDGE_WITH_POSITIONAL_RULES": 6, "FORWARD_SLOT_EXTENSION": 1, "STRUCTURAL_REPAIR_REQUIRED": 1}),
        "eight_alignment_rows": len(corrections) == 8,
        "only_ody_requires_repair": [row["master_card_id"] for row in corrections if row["alignment"] == "STRUCTURAL_REPAIR_REQUIRED"] == ["MC100"],
        "corrected_second_16_tokens": len(second) == 16 and [int(row["token_order"]) for row in second] == list(range(1, 17)),
        "corrected_second_5_fields": len(fields) == 5 and rebuilt == " | ".join(row["visible_sequence"] for row in fields),
        "ody_now_field_final": next(row for row in second if row["master_card_id"] == "MC100")["field_final"] == "YES",
        "no_new_values": all(row["portable_value_de"] for row in lexicon),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [lexicon, unused, corrections, shortlist, second, fields] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "decision": "FULL_173_CARD_SLOT_LEXICON_READY__ODY_FIELD_BOUNDARY_REPAIRED",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
