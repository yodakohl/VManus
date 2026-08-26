#!/usr/bin/env python3
"""Validate GDT432's exhaustive one-root phrase contrast audit."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt432_reversible_neighbor_phrase_contrast_audit"
OUT = BASE / "artifacts"
SOURCE_NEIGHBORS = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_145_neighbor_exemplars.tsv"
SOURCE_CARDS = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_47_strong_prediction_phrasebook.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt432_145_generic_neighbor_contrasts.tsv",
        OUT / "gdt432_725_register_neighbor_contrasts.tsv",
        OUT / "gdt432_directed_root_pair_summary.tsv",
        OUT / "gdt432_47_card_reversibility.tsv",
        OUT / "gdt432_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}
    generic = read_tsv(tracked[0])
    registers = read_tsv(tracked[1])
    pairs = read_tsv(tracked[2])
    cards = read_tsv(tracked[3])
    source_neighbors = read_tsv(SOURCE_NEIGHBORS)
    source_cards = read_tsv(SOURCE_CARDS)
    result = json.loads((OUT / "gdt432_result.json").read_text(encoding="utf-8"))
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)
    route_ids = {row["route_id"] for row in generic}
    register_counts = Counter(row["route_id"] for row in registers)
    card_route_counts = Counter(row["candidate_recipe"] for row in generic)
    source_card_counts = {row["candidate_recipe"]: int(row["source_neighbor_count"]) for row in source_cards}

    checks = {
        "generic_rows_145": len(generic) == 145,
        "generic_routes_unique": len(route_ids) == 145,
        "source_routes_exact": {(row["candidate_recipe"], row["source_neighbor_recipe"]) for row in generic} == {(row["candidate_recipe"], row["source_neighbor_recipe"]) for row in source_neighbors},
        "one_changed_atom_each": all(sum(a != b for a, b in zip(row["source_neighbor_recipe"].split("+"), row["candidate_recipe"].split("+"))) == 1 for row in generic),
        "changed_position_exact": all(row["source_neighbor_recipe"].split("+")[int(row["changed_atom_position"]) - 1] == row["source_atom"] and row["candidate_recipe"].split("+")[int(row["changed_atom_position"]) - 1] == row["target_atom"] for row in generic),
        "family_preserved": all(row["factor_family"].strip() for row in generic),
        "direct_support_positive": all(int(row["direct_shared_frame_count"]) > 0 for row in generic),
        "trace_delta_one": all(row["semantic_trace_delta_count"] == "1" for row in generic),
        "unchanged_slots_preserved": all(row["unchanged_slots_preserved"] == "YES" for row in generic),
        "generic_phrases_changed": all(row["natural_phrase_changed"] == "YES" for row in generic),
        "generic_decisions_pass": all(row["decision"] == "REVERSIBLE_ONE_ROOT_CONTRAST" for row in generic),
        "register_rows_725": len(registers) == 725,
        "five_registers_per_route": all(register_counts[route_id] == 5 for route_id in route_ids),
        "all_register_names_exact": {row["register"] for row in registers} == {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"},
        "local_trace_delta_one": all(row["local_trace_delta_count"] == "1" for row in registers),
        "local_phrases_changed": all(row["local_phrase_changed"] == "YES" for row in registers),
        "target_matches_gdt431": all(row["target_matches_gdt431"] == "YES" for row in registers),
        "local_decisions_pass": all(row["decision"] == "LOCAL_CONTRAST_VISIBLE" for row in registers),
        "cards_47": len(cards) == 47 and len({row["candidate_recipe"] for row in cards}) == 47,
        "card_ids_exact": {row["candidate_recipe"] for row in cards} == set(source_card_counts),
        "card_neighbor_counts_exact": all(card_route_counts[recipe] == count for recipe, count in source_card_counts.items()),
        "card_generic_counts_pass": all(int(row["generic_pass_count"]) == int(row["neighbor_route_count"]) for row in cards),
        "card_register_counts_pass": all(int(row["register_pass_count"]) == int(row["register_contrast_total"]) == int(row["neighbor_route_count"]) * 5 for row in cards),
        "card_decisions_pass": all(row["decision"] == "CARD_CONTRASTS_ALL_REVERSIBLE" for row in cards),
        "pair_rows_nonempty": bool(pairs) and len({row["directed_root_change"] for row in pairs}) == len(pairs),
        "pair_counts_cover_145": sum(int(row["route_count"]) for row in pairs) == 145,
        "pair_decisions_pass": all(row["decision"] == "PAIR_REMAINS_AUDIBLE" for row in pairs),
        "result_status": result["status"] == "ALL_145_NEIGHBOR_ROUTES_AND_725_REGISTER_CONTRASTS_REVERSIBLE",
        "result_counts": result["card_count"] == 47 and result["generic_neighbor_route_count"] == 145 and result["register_neighbor_contrast_count"] == 725,
        "result_pass_counts": result["generic_contrast_pass_count"] == 145 and result["register_contrast_pass_count"] == 725,
        "result_trace_histogram": result["trace_delta_histogram"] == {"1": 145},
        "no_new_semantics_or_pages": result["new_component_values"] == result["new_pages"] == result["surface_predictions"] == 0,
        "no_placeholder_language": all(term not in output_text.upper() for term in ("UNKNOWN", "EXEMPLAR_VALUE", "UNTRANSLATED")),
        "no_forbidden_page": "f84" not in output_text.lower(),
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt432_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
