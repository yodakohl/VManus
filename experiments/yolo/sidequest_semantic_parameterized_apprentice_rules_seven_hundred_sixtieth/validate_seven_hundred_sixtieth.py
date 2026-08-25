#!/usr/bin/env python3
"""Validate Pass 760 parameterized apprentice rules."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P759 = ROOT / "experiments/yolo/sidequest_semantic_forward_teaching_compiler_seven_hundred_fifty_ninth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    meta = read(HERE / "SEVEN_HUNDRED_SIXTIETH_9_PARAMETERIZED_RULES.tsv")
    variants = read(HERE / "SEVEN_HUNDRED_SIXTIETH_25_REGISTERED_VARIANTS.tsv")
    traces = read(HERE / "SEVEN_HUNDRED_SIXTIETH_116_META_RULE_TRACE.tsv")
    outputs = read(HERE / "SEVEN_HUNDRED_SIXTIETH_116_FORWARD_OUTPUT.tsv")
    targets = {row["statement_id"]: row for row in read(P759 / "SEVEN_HUNDRED_FIFTY_NINTH_116_FORWARD_OUTPUT.tsv")}
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTIETH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    distribution = sorted(int(row["registered_variants"]) for row in meta)
    checks = {
        "counts_9_25_116_116": (len(meta), len(variants), len(traces), len(outputs)) == (9, 25, 116, 116),
        "variant_distribution": distribution == [1, 1, 2, 2, 2, 3, 4, 5, 5],
        "all_variants_used_once": all(row["source_forward_uses"] == "1" for row in variants) and sum(int(row["forward_uses"]) for row in meta) == 25,
        "outputs_identical_to_pass759": all(row["forward_recipe_sequence"] == targets[row["statement_id"]]["forward_recipe_sequence"] for row in outputs),
        "cards_381": sum(int(row["forward_cards"]) for row in outputs) == 381,
        "seven_exemplars": sum(row["bound_exemplar"] != "NONE" for row in outputs) == 7,
        "fixed_pages_only": {row["page"] for row in outputs} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (meta, variants, traces, outputs) for row in rows),
        "no_semantic_or_output_change": summary["semantic_changes"] == 0 and summary["output_changes"] == 0,
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
