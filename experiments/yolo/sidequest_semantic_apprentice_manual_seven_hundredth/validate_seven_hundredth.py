#!/usr/bin/env python3
"""Validate the consolidated apprentice manual."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python3", str(HERE / "build_seven_hundredth.py")], check=True)
    tablet = read("SEVEN_HUNDREDTH_39_TABLET_ENTRIES.tsv")
    cards = read("SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    trace = read("SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    statements = read("SEVEN_HUNDREDTH_116_STATEMENT_EDITION.tsv")
    rules = read("SEVEN_HUNDREDTH_7_RENDERER_RULES.tsv")
    trays = read("SEVEN_HUNDREDTH_18_OWNER_TRAYS.tsv")
    slips = read("SEVEN_HUNDREDTH_5_OVERRIDE_SLIPS.tsv")
    checks = {
        "tablet_36_plus_3": len(tablet) == 39 and Counter(row["entry_kind"] for row in tablet) == Counter({"COMPOSABLE_WORK_COMPONENT": 36, "MEMORIZED_WHOLE_COMMAND": 3}),
        "one_seventy_three_cards": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "card_classes": Counter(row["card_class"] for row in cards) == Counter({"COMPOSED_WITH_BOUND_RENDERER": 114, "COMPOSED_DIRECT_ALL_FORMS": 56, "MEMORIZED_WHOLE_COMMAND": 3}),
        "three_eighty_one_events": len(trace) == 381 and [row["event_id"] for row in trace] == [f"E{i:03d}" for i in range(1, 382)],
        "one_sixteen_statements": len(statements) == 116 and sum(int(row["events"]) for row in statements) == 381,
        "selection_layers": Counter(row["surface_selection_layer"] for row in trace) == Counter({"GLOBAL_CARD_FORM": 314, "CONTEXT_WRAPPER_RULE": 8, "OWNER_CARD_DEFAULT": 54, "LOCAL_OVERRIDE_SLIP": 5}),
        "all_exact_surfaces": all(row["produced_surface"] == row["observed_surface"] and row["exact_surface_match"] == "YES" for row in trace),
        "seven_rules": len(rules) == 7,
        "eighteen_trays": len(trays) == 18,
        "five_slips": len(slips) == 5,
        "fixed_pages": {row["page"] for row in trace} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "no_empty_layers": all(row["semantic_layer_de"] and row["visible_character_layers_de"] for row in trace),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (HERE / "SEVEN_HUNDREDTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
