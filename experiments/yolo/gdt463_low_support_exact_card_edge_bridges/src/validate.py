#!/usr/bin/env python3
"""Validate GDT463 low-support exact-card bridges."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt463_low_support_exact_card_edge_bridges"
OUT = BASE / "artifacts"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
GDT459_PATH = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt462_near_threshold_ar_edge_exception_audit/artifacts/gdt462_107_revised_hybrid_dictionary.tsv"
RUN_SCRIPT = BASE / "src/run.py"

DECISION_PATH = OUT / "gdt463_4_bridge_decisions.tsv"
CARRIER_PATH = OUT / "gdt463_recipe_sequence_carriers.tsv"
PARADIGM_PATH = OUT / "gdt463_ain_aiin_oin_suffix_paradigm.tsv"
TARGET_PATH = OUT / "gdt463_4_target_reconstructions.tsv"
LABEL_PATH = OUT / "gdt463_107_revised_hybrid_dictionary.tsv"
PAGE_PATH = OUT / "gdt463_6_page_summary.tsv"
RESULT_PATH = OUT / "gdt463_result.json"
VALIDATION_PATH = OUT / "gdt463_validation.json"

EXPECTED_METRICS = {
    "oin": ("O+IIN", 2, 3, 3, 16, 28, 13),
    "kor": ("K+OR", 3, 2, 2, 10, 14, 9),
    "yky": ("Y+K+Y", 1, 1, 1, 3, 5, 4),
    "cfhy": ("CH+LOCAL_CHAR_F+Y", 2, 1, 1, 3, 4, 4),
}
EXPECTED_STATUS = {
    "FULL_FUNCTION_FORMULA": 14,
    "FUNCTION_SHELL_PLUS_LEARNED_CORE": 85,
    "OWNER_FAMILY_STEM_ONLY": 1,
    "WHOLE_LEARNED_LABEL": 7,
}
EXPECTED_TARGETS = {
    "opoiiinoin": ("FUNCTION_SHELL_PLUS_LEARNED_CORE", "O+IIN", 3, "[STERNSTELLENNAME:opoiiin] · AUSFÜHRUNG · STUFE"),
    "korainy": ("FULL_FUNCTION_FORMULA", "K+OR+AIN+Y", 7, "GEBEN · EINHEIT · ANTEIL · POSTEN"),
    "ykyd": ("FULL_FUNCTION_FORMULA", "Y+K+Y+D_ADDR", 4, "POSTEN · GEBEN · POSTEN · HIER"),
    "ykocfhy": ("FUNCTION_SHELL_PLUS_LEARNED_CORE", "CH+LOCAL_CHAR_F+Y", 4, "[DROGENNAME:yko] · NEHMEN · HIER · POSTEN"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def contains_sequence(needle: list[str], haystack: list[str]) -> bool:
    return any(haystack[index:index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    running = read_tsv(RUNNING_PATH)
    old_addresses = {row["surface"]: row for row in read_tsv(GDT459_PATH)}
    source = read_tsv(SOURCE_PATH)
    decisions = read_tsv(DECISION_PATH)
    carriers = read_tsv(CARRIER_PATH)
    paradigms = read_tsv(PARADIGM_PATH)
    targets = read_tsv(TARGET_PATH)
    labels = read_tsv(LABEL_PATH)
    pages = read_tsv(PAGE_PATH)
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    check("source_label_count", len(source) == 107, "107 source labels")
    check("source_whole_count", sum(row["gdt462_hybrid_status"] == "WHOLE_LEARNED_LABEL" for row in source) == 11, "eleven GDT462 whole labels")
    check("decision_count", len(decisions) == 4, "four low-support bridges")
    check("decision_stem_set", {row["surface_stem"] for row in decisions} == set(EXPECTED_METRICS), "exact oin/kor/yky/cfhy set")

    running_recipe: dict[str, str] = {}
    running_events: dict[str, list[dict[str, str]]] = {}
    invariant = True
    for row in running:
        previous = running_recipe.setdefault(row["surface"], row["component_recipe"])
        invariant &= previous == row["component_recipe"]
        running_events.setdefault(row["surface"], []).append(row)
    check("running_surface_invariance", invariant, "one recipe per running surface")

    recomputed = True
    for row in decisions:
        stem = row["surface_stem"]
        edge = row["edge"]
        recipe = row["component_recipe"]
        atoms = recipe.split("+")
        if edge == "PREFIX":
            extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.startswith(stem)]
            matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[:len(atoms)] == atoms]
        else:
            extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.endswith(stem)]
            matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[-len(atoms):] == atoms]
        sequence = [(surface, candidate) for surface, candidate in running_recipe.items() if contains_sequence(atoms, candidate.split("+"))]
        pages_seen = {event["physical_page"] for surface, _ in sequence for event in running_events[surface]}
        expected = EXPECTED_METRICS[stem]
        recomputed &= (
            recipe == expected[0]
            and len(running_events[stem]) == int(row["base_running_event_count"]) == expected[1]
            and len(extensions) == int(row["edge_extension_type_count"]) == expected[2]
            and len(matches) == int(row["edge_matching_type_count"]) == expected[3]
            and len(matches) == len(extensions)
            and len(sequence) == int(row["recipe_sequence_carrier_type_count"]) == expected[4]
            and sum(len(running_events[surface]) for surface, _ in sequence) == int(row["recipe_sequence_carrier_event_count"]) == expected[5]
            and len(pages_seen) == int(row["recipe_sequence_page_count"]) == expected[6]
            and row["decision"] == "PROMOTE_EXACT_CARD_EDGE"
        )
    check("four_metrics_recomputed", recomputed, "all edge and sequence metrics reproduce")
    check("all_extension_precision_one", all(row["edge_type_precision"] == "1.000000" for row in decisions), "all observed extensions align")
    check("all_sequence_four_pages", all(int(row["recipe_sequence_page_count"]) >= 4 for row in decisions), "every recipe sequence spans at least four pages")

    check("carrier_count", len(carriers) == 32, f"observed={len(carriers)} expected=32")
    carrier_valid = True
    for row in carriers:
        stem = row["edge_stem"]
        atoms = EXPECTED_METRICS[stem][0].split("+")
        carrier_valid &= row["carrier_surface"] in running_recipe and contains_sequence(atoms, running_recipe[row["carrier_surface"]].split("+"))
    check("carrier_rows_valid", carrier_valid, "all carrier rows contain their bridge recipe sequence")

    paradigm_index = {row["surface_suffix"]: row for row in paradigms}
    check("suffix_paradigm_count", len(paradigms) == 3 and set(paradigm_index) == {"ain", "aiin", "oin"}, "three suffix axes")
    check("ain_axis_exact", paradigm_index["ain"]["matching_type_count"] == "53" and paradigm_index["ain"]["extension_type_count"] == "53" and paradigm_index["ain"]["type_precision"] == "1.000000", "AIN suffix 53/53")
    check("aiin_axis_exact", paradigm_index["aiin"]["matching_type_count"] == "89" and paradigm_index["aiin"]["extension_type_count"] == "89" and paradigm_index["aiin"]["type_precision"] == "1.000000", "AIIN suffix 89/89")
    check("oin_axis_exact", paradigm_index["oin"]["matching_type_count"] == "3" and paradigm_index["oin"]["extension_type_count"] == "3" and paradigm_index["oin"]["type_precision"] == "1.000000", "OIN suffix 3/3")

    check("target_count", len(targets) == 4 and {row["surface"] for row in targets} == set(EXPECTED_TARGETS), "four exact targets")
    target_valid = True
    for row in targets:
        status, recipe, added, default = EXPECTED_TARGETS[row["surface"]]
        target_valid &= row["new_status"] == status and row["selected_function_recipe"] == recipe and int(row["added_known_character_count"]) == added and row["selected_literal_de"] == default
    check("target_reconstructions_exact", target_valid, "four selected reconstructions fixed")
    check("full_targets_old_recipe_exact", old_addresses["korainy"]["minimal_segmentation_recipe"] == "K+OR+AIN+Y" and old_addresses["ykyd"]["minimal_segmentation_recipe"] == "Y+K+Y+D_ADDR", "old minimal recipes support both full targets")
    check("full_targets_old_gate_green", all(old_addresses[surface]["factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" for surface in ("korainy", "ykyd")), "both full target recipes passed old factor gate")
    check("full_target_chunks_exist", running_recipe.get("korain") == "K+OR+AIN" and running_recipe.get("y") == "Y" and running_recipe.get("yky") == "Y+K+Y" and running_recipe.get("d") == "D_ADDR", "two-chunk full reconstructions use exact running cards")
    check("yky_recipe_replication", running_recipe.get("ykchy") == "Y+K+Y" and len(running_events["ykchy"]) == 3, "thin yky edge has replicated recipe surface")

    check("revised_label_count", len(labels) == 107, "107 revised labels")
    check("source_order_exact", [row["source_event_id"] for row in labels] == [row["source_event_id"] for row in source] and [row["surface"] for row in labels] == [row["surface"] for row in source], "source order and surfaces unchanged")
    check("source_bindings_exact", all(tuple(new[key] for key in ("physical_page", "register", "locus", "owner_de", "content_class", "image_object_id", "review_image_sha256")) == tuple(old[key] for key in ("physical_page", "register", "locus", "owner_de", "content_class", "image_object_id", "review_image_sha256")) for new, old in zip(labels, source)), "bindings retained")
    changed = [row for row in labels if row["gdt463_change"] != "UNCHANGED"]
    check("changed_exact_four", len(changed) == 4 and {row["surface"] for row in changed} == set(EXPECTED_TARGETS), "only four rows change")
    unchanged_valid = all(
        new["gdt463_hybrid_status"] == old["gdt462_hybrid_status"]
        and new["prefix_stem"] == old["prefix_stem"]
        and new["suffix_stem"] == old["suffix_stem"]
        and new["known_function_character_count"] == old["known_function_character_count"]
        and new["ordered_function_recipe_trace"] == old["ordered_function_recipe_trace"]
        and new["revised_short_default_de"] == old["revised_short_default_de"]
        for new, old in zip(labels, source)
        if new["gdt463_change"] == "UNCHANGED"
    )
    check("unchanged_exact", unchanged_valid, "103 rows retain all semantic fields")
    changed_valid = all(
        row["gdt463_hybrid_status"] == EXPECTED_TARGETS[row["surface"]][0]
        and row["ordered_function_recipe_trace"] == EXPECTED_TARGETS[row["surface"]][1]
        and int(row["known_function_character_count"]) == EXPECTED_TARGETS[row["surface"]][2]
        and row["revised_short_default_de"] == EXPECTED_TARGETS[row["surface"]][3]
        for row in changed
    )
    check("changed_exact", changed_valid, "four changed dictionary rows match target edition")
    statuses = Counter(row["gdt463_hybrid_status"] for row in labels)
    check("status_counts", dict(statuses) == EXPECTED_STATUS, f"observed={dict(statuses)}")
    check("remaining_whole_set", {row["surface"] for row in labels if row["gdt463_hybrid_status"] == "WHOLE_LEARNED_LABEL"} == {"oiil", "ofaom", "chdaiirdainy", "ofchdamy", "opoeey", "of", "yddy"}, "exact seven whole labels remain")
    check("known_character_count", sum(int(row["known_function_character_count"]) for row in labels) == 413, "413/713 known function characters")
    check("surface_character_count", sum(int(row["surface_character_count"]) for row in labels) == 713, "713 source characters")
    check("function_label_count", sum(int(row["known_function_character_count"]) > 0 for row in labels) == 99, "99 labels with function")
    check("structure_label_count", sum(int(row["known_function_character_count"]) > 0 or row["owner_family_stem_trace"] != "NONE" for row in labels) == 100, "100 labels with structure")
    check("page_count", len(pages) == 6 and {row["physical_page"] for row in pages} == {"f17r", "f71v", "f72r", "f77r", "f88v", "f89r"}, "six admitted pages only")
    check("page_totals", sum(int(row["label_count"]) for row in pages) == 107 and sum(int(row["full_function_formula_count"]) for row in pages) == 14 and sum(int(row["function_shell_plus_core_count"]) for row in pages) == 85 and sum(int(row["whole_learned_label_count"]) for row in pages) == 7 and sum(int(row["gdt463_change_count"]) for row in pages) == 4 and sum(int(row["known_function_character_count"]) for row in pages) == 413, "page summary reconciles")

    check("result_status", result["status"] == "FOUR_LOW_SUPPORT_EXACT_CARD_BRIDGES_REDUCE_WHOLE_LABEL_TAIL_TO_SEVEN", result["status"])
    check("result_counts", result["source_label_count"] == 107 and result["bridge_decision_count"] == 4 and result["promoted_bridge_count"] == 4 and result["recipe_sequence_carrier_row_count"] == 32 and result["full_formula_promotions"] == ["korainy", "ykyd"] and result["hybrid_shell_promotions"] == ["opoiiinoin", "ykocfhy"] and result["revised_hybrid_status_counts"] == EXPECTED_STATUS and result["remaining_whole_label_count"] == 7 and result["labels_with_any_function_count"] == 99 and result["labels_with_any_structure_count"] == 100 and result["known_function_character_count"] == 413 and result["surface_character_count"] == 713 and result["known_function_character_fraction"] == "0.579243", "result JSON reconciles")
    check("claim_ceiling_zeroes", all(result[key] == 0 for key in ("new_core_meanings", "new_pages", "surface_predictions", "confirmed_lexemes")), "no new meanings/pages/surfaces/lexemes")
    generated = (DECISION_PATH, CARRIER_PATH, PARADIGM_PATH, TARGET_PATH, LABEL_PATH, PAGE_PATH, RESULT_PATH)
    serialized = "\n".join(path.read_text(encoding="utf-8") for path in generated)
    check("sealed_pages_absent", "f84" not in serialized.lower(), "no sealed folio token")
    check("artifact_size_gate", all(path.stat().st_size < 5_000_000 for path in generated), "all artifacts below 5 MB")
    before = {path: path.read_bytes() for path in generated}
    completed = subprocess.run([sys.executable, str(RUN_SCRIPT)], cwd=ROOT, check=False, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in generated}
    check("deterministic_rebuild_exit", completed.returncode == 0, f"returncode={completed.returncode}")
    check("deterministic_rebuild_bytes", before == after, "all generated artifacts byte-identical")

    passed = sum(bool(row["passed"]) for row in checks)
    validation = {"status": "PASS" if passed == len(checks) else "FAIL", "checks_passed": passed, "checks_total": len(checks), "checks": checks}
    VALIDATION_PATH.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
