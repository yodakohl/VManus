#!/usr/bin/env python3

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


chart = rows("THREE_HUNDRED_THIRTY_EIGHTH_COMPLETE_173_CARD_TEACHING_CHART.tsv")
layers = rows("THREE_HUNDRED_THIRTY_EIGHTH_THREE_TEACHING_LAYERS.tsv")
counts = Counter(row["teaching_category"] for row in chart)
checks = {
    "all_173_cards": len(chart) == 173 and len({row["joint_tuple_id"] for row in chart}) == 173,
    "all_381_events": sum(int(row["occurrences"]) for row in chart) == 381,
    "three_layers": len(layers) == 3 and len(counts) == 3,
    "one_hundred_twenty_five_invariant": counts["INVARIANT_TEACHING_CORE"] == 125,
    "thirty_four_variable": counts["HAND_VARIABLE_ALLOGRAPH_CARD"] == 34,
    "fourteen_stable_memorized": counts["STABLE_MEMORIZED_TECHNICAL_CARD"] == 14,
    "two_variable_memorized": sum(row["teaching_category"] == "HAND_VARIABLE_ALLOGRAPH_CARD" and row["deck_class"] == "MEMORIZED_WHOLE_CARD" for row in chart) == 2,
    "variable_cards_have_palette": all(int(row["surface_count"]) > 1 for row in chart if row["teaching_category"] == "HAND_VARIABLE_ALLOGRAPH_CARD"),
    "stable_cards_have_one_form": all(int(row["surface_count"]) == 1 for row in chart if row["teaching_category"] != "HAND_VARIABLE_ALLOGRAPH_CARD"),
    "hand_forms_registered": all(all(row[key] in row["registered_surface_palette"].split("|") for key in ("hand_a_bare", "hand_b_q_operational", "hand_c_s_entry", "hand_d_expanded")) for row in chart),
    "sealed_absent": all("f84" not in row["pages"] for row in chart),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_THIRTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
