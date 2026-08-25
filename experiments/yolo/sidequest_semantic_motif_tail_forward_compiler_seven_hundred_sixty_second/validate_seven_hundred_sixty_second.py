#!/usr/bin/env python3
"""Validate Pass 762 motif/tail forward compiler."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P760 = ROOT / "experiments/yolo/sidequest_semantic_parameterized_apprentice_rules_seven_hundred_sixtieth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    dictionary = read(HERE / "SEVEN_HUNDRED_SIXTY_SECOND_27_MOTIF_TAIL_DICTIONARY.tsv")
    layouts = read(HERE / "SEVEN_HUNDRED_SIXTY_SECOND_7_LAYOUT_LINES.tsv")
    expansions = read(HERE / "SEVEN_HUNDRED_SIXTY_SECOND_50_LAYOUT_EXPANSIONS.tsv")
    outputs = read(HERE / "SEVEN_HUNDRED_SIXTY_SECOND_116_FORWARD_OUTPUT.tsv")
    targets = {row["statement_id"]: row for row in read(P760 / "SEVEN_HUNDRED_SIXTIETH_116_FORWARD_OUTPUT.tsv")}
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTY_SECOND_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    builder_text = (HERE / "build_seven_hundred_sixty_second.py").read_text(encoding="utf-8")
    checks = {
        "counts_27_7_50_116": (len(dictionary), len(layouts), len(expansions), len(outputs)) == (27, 7, 50, 116),
        "dictionary_8_motifs_19_tails": (sum(row["token_kind"] == "SHARED_MOTIF" for row in dictionary), sum(row["token_kind"] == "LOCAL_TAIL_STRIP" for row in dictionary)) == (8, 19),
        "all_outputs_identical": all(row["forward_recipe_sequence"] == targets[row["statement_id"]]["forward_recipe_sequence"] for row in outputs),
        "cards_381": sum(int(row["forward_cards"]) for row in outputs) == 381,
        "seven_layout_uses": sum(row["generation_layer"] == "MOTIF_TAIL_LAYOUT" for row in outputs) == 7,
        "layout_expands_74_cards": sum(int(row["end_card_ordinal"]) - int(row["start_card_ordinal"]) + 1 for row in expansions) == 74,
        "no_full_output_field_in_builder": "memorized_card_sequence" not in builder_text and "observed_recipe_sequence" not in builder_text,
        "stored_full_sentence_outputs_zero": summary["stored_full_sentence_outputs"] == 0,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (dictionary, layouts, expansions, outputs) for row in rows),
        "no_semantic_or_output_change": summary["semantic_changes"] == 0 and summary["output_changes"] == 0,
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
