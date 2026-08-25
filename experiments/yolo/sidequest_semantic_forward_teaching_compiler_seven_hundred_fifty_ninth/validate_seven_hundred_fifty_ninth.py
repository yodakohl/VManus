#!/usr/bin/env python3
"""Validate Pass 759 forward output against the fixed Pass758 edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P758 = ROOT / "experiments/yolo/sidequest_semantic_complete_mixed_codebook_packer_seven_hundred_fifty_eighth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    inputs = read(HERE / "SEVEN_HUNDRED_FIFTY_NINTH_116_FORWARD_INPUT.tsv")
    rules = read(HERE / "SEVEN_HUNDRED_FIFTY_NINTH_25_CONTEXT_RULES.tsv")
    traces = read(HERE / "SEVEN_HUNDRED_FIFTY_NINTH_116_LAYER_TRACE.tsv")
    outputs = read(HERE / "SEVEN_HUNDRED_FIFTY_NINTH_116_FORWARD_OUTPUT.tsv")
    cards = read(HERE / "SEVEN_HUNDRED_FIFTY_NINTH_381_FORWARD_CARDS.tsv")
    targets = {row["statement_id"]: row for row in read(P758 / "SEVEN_HUNDRED_FIFTY_EIGHTH_116_FINAL_PACKING_AUDIT.tsv")}
    target_cards = read(P758 / "SEVEN_HUNDRED_FIFTY_EIGHTH_381_FINAL_CARD_OUTPUT.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FIFTY_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    builder_text = (HERE / "build_seven_hundred_fifty_ninth.py").read_text(encoding="utf-8")
    checks = {
        "counts_116_25_116_116_381": (len(inputs), len(rules), len(traces), len(outputs), len(cards)) == (116, 25, 116, 116, 381),
        "all_statement_sequences_exact": all(row["forward_recipe_sequence"] == targets[row["statement_id"]]["final_recipe_sequence"] for row in outputs),
        "all_forward_cards_exact": [(row["statement_id"], row["card_ordinal_in_statement"], row["surface"], row["forward_component_recipe"]) for row in cards] == [(row["statement_id"], row["card_ordinal_in_statement"], row["surface"], row["component_recipe"]) for row in target_cards],
        "seven_exemplars_used": sum(row["applied_exemplar"] != "NONE" for row in outputs) == 7,
        "twenty_five_rules_each_used_once": all(row["forward_uses"] == "1" for row in rules),
        "builder_declares_no_target_use": summary["builder_uses_final_target_sequence"] is False,
        "builder_lacks_target_column_name": "observed_recipe_sequence_after_reveal" not in builder_text and "final_recipe_sequence" not in builder_text,
        "fixed_pages_only": {row["page"] for row in cards} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (inputs, rules, traces, outputs, cards) for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FIFTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
