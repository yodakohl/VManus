#!/usr/bin/env python3
"""Validate GDT606 artifacts, carrier audit, and deterministic bindings."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "src"
OUT = HERE / "artifacts"
CONFIGS = {
    "primary_42L_4D_34S_7N_11W": {"L": 42, "D": 4, "S": 34, "N": 7, "W": 11},
    "sensitivity_36L_4D_40S_7N_11W": {"L": 36, "D": 4, "S": 40, "N": 7, "W": 11},
    "sensitivity_46L_4D_30S_7N_11W": {"L": 46, "D": 4, "S": 30, "N": 7, "W": 11},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def main() -> int:
    checks: list[str] = []
    binding = json.loads((OUT / "binding_inventory.json").read_text())
    require(binding["schema"] == "gdt606-binding-inventory-v1", "binding schema", checks)
    for name, expected in binding["sources"].items():
        require(sha256(SRC / name) == expected, f"source hash {name}", checks)
    for name, expected in binding["artifacts"].items():
        require(sha256(OUT / name) == expected, f"artifact hash {name}", checks)

    guarded = rows(OUT / "guarded_rows.tsv")
    require(len(guarded) == 4165, "4165 guarded rows", checks)
    require(all(not row["page"].lower().startswith("f84") for row in guarded), "no f84 selector", checks)
    require(len({row["physical_folio"] for row in guarded if row["split"] == "train"}) == 68, "68 train folios", checks)
    require(len({row["physical_folio"] for row in guarded if row["split"] == "held"}) == 23, "23 held folios", checks)

    units = json.loads((OUT / "unit_sequences.json").read_text())
    require(units["schema"].startswith("gdt606-"), "GDT606 unit schema", checks)
    require(len(units["inventory"]) == 98, "98 units", checks)
    require(len(units["sequences"]["train"]) == 20336, "20336 train chunks", checks)
    require(len(units["sequences"]["held"]) == 9838, "9838 held chunks", checks)
    require(sum(units["frequency"]["train"].values()) == 43335, "43335 train occurrences", checks)
    require(sum(units["frequency"]["held"].values()) == 21679, "21679 held occurrences", checks)
    require(set(units["frequency"]["held"]) <= set(units["inventory"]), "zero held-only units", checks)

    mappings = rows(OUT / "complete_mappings.tsv")
    grouped: dict[tuple[str, str, str, int], list[dict[str, str]]] = defaultdict(list)
    for row in mappings:
        grouped[(row["language"], row["model_kind"], row["config"], int(row["seed"]))].append(row)
    require(len(grouped) == 48, "48 complete keys", checks)
    require(len(mappings) == 48 * 98, "4704 mapping rows", checks)
    for identity, values in grouped.items():
        require(len(values) == 98 and len({row["unit"] for row in values}) == 98, f"complete key {identity}", checks)
        require(Counter(row["category"] for row in values) == CONFIGS[identity[2]], f"capacity {identity}", checks)
        require(all((row["category"] == "N") == (row["output"] == "") for row in values), f"null contract {identity}", checks)
        letters = Counter(row["output"] for row in values if row["category"] == "L")
        require(max(letters.values()) <= 6, f"homophone cap {identity}", checks)

    result = json.loads((OUT / "mixed_attack_result.json").read_text())
    require(result["schema"].startswith("gdt606-"), "GDT606 attack schema", checks)
    require(result["decision"] == "MIXED_CODEBOOK_UNSTABLE_PSEUDOTEXT", "unstable pseudotext decision", checks)
    require(result["passing_languages"] == [], "zero passing languages", checks)
    for language, decision in result["decisions"].items():
        require(not decision["all_gates_pass"], f"failed reading gates {language}", checks)
        require(not decision["gates"]["min_exact_weighted_agreement_ge_0_50"], f"exact stability failure {language}", checks)

    carrier = json.loads((OUT / "carrier_stability_result.json").read_text())
    require(carrier["schema"].startswith("gdt606-"), "GDT606 carrier schema", checks)
    require(carrier["carrier_stable_words_at_75pct"] == 0, "zero exact carrier-stable words", checks)
    fragments = rows(OUT / "carrier_stable_fragments.tsv")
    require(len(fragments) == 597, "597 prefix-family carrier fragments", checks)
    require({row["language"] for row in fragments} == {"middle_high_german"}, "fragments MHG-only", checks)
    require({row["fragment"] for row in fragments} == {"gesch"}, "single gesch prefix", checks)
    require({row["carrier_units"] for row in fragments} == {"o"}, "single o carrier", checks)

    unanimous: dict[str, set[str]] = {}
    category_tables: dict[str, dict[str, dict[str, str]]] = {}
    for language in ("latin", "old_italian", "middle_high_german"):
        table = {row["unit"]: row for row in rows(OUT / f"category_stability_all_configs_{language}.tsv")}
        category_tables[language] = table
        unanimous[language] = {
            unit for unit, row in table.items()
            if row["all_configs_modal_category"] == "W"
            and float(row["all_configs_category_fraction"]) == 1.0
        }
    require({"o", "y", "ol"} <= set.intersection(*unanimous.values()), "o y ol unanimous whole-word category", checks)
    require(
        all(
            all(float(category_tables[language][unit]["all_configs_category_fraction"]) >= 11 / 12 for language in category_tables)
            for unit in ("C", "d")
        ),
        "C d near-unanimous whole-word category",
        checks,
    )

    source_text = "\n".join(
        path.read_text() for path in SRC.glob("*.py") if path.name != "validate.py"
    ).lower()
    require("sidequest_theory" not in source_text, "no workshop theory import", checks)
    validation = {
        "schema": "gdt606-validation-v1",
        "status": "PASS",
        "checks": len(checks),
        "decision": "MIXED_CODEBOOK_UNSTABLE_PSEUDOTEXT__STRUCTURAL_WHOLE_WORD_CATEGORY_LEAD",
    }
    (OUT / "gdt606_validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
