#!/usr/bin/env python3
"""Validate GDT464 and verify a byte-identical deterministic rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt464_residual_exact_package_bridge"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
ADDRESS_PATH = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt463_low_support_exact_card_edge_bridges/artifacts/gdt463_107_revised_hybrid_dictionary.tsv"

DECISION_PATH = OUT / "gdt464_4_bridge_decisions.tsv"
SUPPORT_PATH = OUT / "gdt464_191_supporting_surfaces.tsv"
FAMILY_PATH = OUT / "gdt464_owner_family_audit.tsv"
TARGET_PATH = OUT / "gdt464_10_target_revisions.tsv"
LABEL_PATH = OUT / "gdt464_107_revised_hybrid_dictionary.tsv"
RESIDUAL_PATH = OUT / "gdt464_7_residual_decisions.tsv"
PAGE_PATH = OUT / "gdt464_6_page_summary.tsv"
RESULT_PATH = OUT / "gdt464_result.json"
VALIDATION_PATH = OUT / "gdt464_validation.json"

GENERATED = (DECISION_PATH, SUPPORT_PATH, FAMILY_PATH, TARGET_PATH, LABEL_PATH, RESIDUAL_PATH, PAGE_PATH, RESULT_PATH)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains_atoms(needle: list[str], haystack: list[str]) -> bool:
    return any(haystack[index:index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    running = read_tsv(RUNNING_PATH)
    addresses = read_tsv(ADDRESS_PATH)
    source = read_tsv(SOURCE_PATH)
    decisions = read_tsv(DECISION_PATH)
    support = read_tsv(SUPPORT_PATH)
    family = read_tsv(FAMILY_PATH)
    targets = read_tsv(TARGET_PATH)
    labels = read_tsv(LABEL_PATH)
    residuals = read_tsv(RESIDUAL_PATH)
    pages = read_tsv(PAGE_PATH)
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    running_recipe: dict[str, str] = {}
    running_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    invariant = True
    for row in running:
        previous = running_recipe.setdefault(row["surface"], row["component_recipe"])
        invariant &= previous == row["component_recipe"]
        running_events[row["surface"]].append(row)

    check("running_source_count", len(running) == 4576, f"observed={len(running)}")
    check("running_surface_invariance", invariant, "one recipe per running surface")
    check("address_source_count", len(addresses) == 183, f"observed={len(addresses)}")
    check("source_label_count", len(source) == 107, f"observed={len(source)}")
    check("source_residual_count", sum(row["gdt463_hybrid_status"] == "WHOLE_LEARNED_LABEL" for row in source) == 7, "seven old whole labels")
    check("decision_count", len(decisions) == 4, f"observed={len(decisions)}")
    check("decision_ids", {row["bridge_id"] for row in decisions} == {f"G464-B{i:02d}" for i in range(1, 5)}, "B01-B04")
    check("all_factor_green", all(row["factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" for row in decisions), "four green gates")

    decision = {row["bridge_id"]: row for row in decisions}
    expected_decisions = {
        "G464-B01": ("O+LOCAL_CHAR_F", 6, 6, "1.000000", 6, 5, 0, 0, "NONE"),
        "G464-B02": ("AIN+Y", 53, 53, "1.000000", 214, 20, 0, 0, "NONE"),
        "G464-B03": ("EE+Y", 46, 45, "0.978261", 192, 18, 0, 0, "sorcheey"),
        "G464-B04": ("Y+D_ADDR+Y", 79, 79, "1.000000", 135, 21, 13, 66, "NONE"),
    }
    for bridge_id, expected in expected_decisions.items():
        row = decision[bridge_id]
        observed = (
            row["selected_recipe"], int(row["calibration_candidate_type_count"]),
            int(row["calibration_matching_type_count"]), row["calibration_precision"],
            int(row["matching_event_count"]), int(row["matching_page_count"]),
            int(row["left_arm_type_count"]), int(row["right_arm_type_count"]), row["exception"],
        )
        check(f"decision_metrics_{bridge_id}", observed == expected, f"observed={observed}")

    check("of_base", running_recipe.get("qof") == "O+LOCAL_CHAR_F", str(running_recipe.get("qof")))
    of_extensions = sorted(surface for surface in running_recipe if surface.startswith("of"))
    check("of_extension_count", len(of_extensions) == 6, f"observed={len(of_extensions)}")
    check("of_extension_precision", all(running_recipe[s].split("+")[:2] == ["O", "LOCAL_CHAR_F"] for s in of_extensions), "6/6")

    ain_extensions = sorted(surface for surface in running_recipe if surface != "ain" and surface.endswith("ain"))
    check("ain_exact_cards", running_recipe.get("ain") == "AIN" and running_recipe.get("y") == "Y", "ain and y")
    check("ain_extension_count", len(ain_extensions) == 53, f"observed={len(ain_extensions)}")
    check("ain_extension_precision", all(running_recipe[s].split("+")[-1:] == ["AIN"] for s in ain_extensions), "53/53")

    eey_candidates = sorted(surface for surface in running_recipe if surface.endswith("eey") and not surface.endswith("eeey"))
    eey_matches = [surface for surface in eey_candidates if running_recipe[surface].split("+")[-2:] == ["EE", "Y"]]
    check("eey_candidate_count", len(eey_candidates) == 46, f"observed={len(eey_candidates)}")
    check("eey_match_count", len(eey_matches) == 45, f"observed={len(eey_matches)}")
    check("eey_exact_exception", sorted(set(eey_candidates) - set(eey_matches)) == ["sorcheey"], str(sorted(set(eey_candidates) - set(eey_matches))))

    def sequence_surfaces(recipe: str) -> list[str]:
        atoms = recipe.split("+")
        return [surface for surface, candidate in running_recipe.items() if contains_atoms(atoms, candidate.split("+"))]

    left, right = sequence_surfaces("Y+D_ADDR"), sequence_surfaces("D_ADDR+Y")
    check("yddy_exact_cards", {s: running_recipe.get(s) for s in ("y", "d", "dy")} == {"y": "Y", "d": "D_ADDR", "dy": "Y"}, "three exact cards")
    check("yddy_left_arm", len(left) == 13 and sum(len(running_events[s]) for s in left) == 18, "13 types / 18 events")
    check("yddy_right_arm", len(right) == 66 and sum(len(running_events[s]) for s in right) == 117, "66 / 117")

    check("support_row_count", len(support) == 191, f"observed={len(support)}")
    support_by_bridge = Counter(row["bridge_id"] for row in support)
    check("support_bridge_counts", support_by_bridge == Counter({"G464-B01": 7, "G464-B02": 56, "G464-B03": 46, "G464-B04": 82}), str(support_by_bridge))
    support_status = Counter(row["support_status"] for row in support)
    check("support_status_counts", support_status == Counter({"MATCH": 190, "EXACT_WHOLE_CARD_EXCEPTION": 1}), str(support_status))
    check("support_unique_keys", len({(row["bridge_id"], row["support_role"], row["surface"]) for row in support}) == len(support), "no duplicate support keys")
    check("support_running_rows_valid", all(row["surface"] in running_recipe and row["component_recipe"] == running_recipe[row["surface"]] for row in support if row["source_layer"] == "GDT407_RUNNING"), "all running support rows exact")
    check("support_anchor_valid", [row for row in support if row["source_layer"] == "GDT463_ADDRESS"] == [{
        "bridge_id": "G464-B02", "support_role": "HELD_ADDRESS_ANCHOR", "source_layer": "GDT463_ADDRESS",
        "surface": "korainy", "component_recipe": "K+OR+AIN+Y", "event_count": "1", "pages": "f89r",
        "registers": "PHARMA", "support_status": "MATCH",
    }], "one held address anchor")

    check("family_summary_count", len(family) == 1, "one summary row")
    check("family_search_counts", family[0]["raw_replicated_owner_family_count"] == "22" and family[0]["maximal_replicated_owner_family_count"] == "19", str(family[0]))
    check("family_no_residual_touch", family[0]["residual_touching_strict_family_count"] == "0", str(family[0]))

    check("target_count", len(targets) == 10, f"observed={len(targets)}")
    expected_changed = {"ofaom", "chdaiirdainy", "ofaralar", "otainy", "ofchdamy", "ofsholdy", "opoeey", "of", "yddy", "ofakal"}
    check("target_surfaces", {row["surface"] for row in targets} == expected_changed, "ten exact changed surfaces")
    check("target_positive_additions", all(int(row["added_known_character_count"]) > 0 for row in targets), "all add characters")
    check("target_added_total", sum(int(row["added_known_character_count"]) for row in targets) == 27, "27 characters")

    check("label_count", len(labels) == 107, f"observed={len(labels)}")
    check("label_source_alignment", [row["source_event_id"] for row in labels] == [row["source_event_id"] for row in source], "source order exact")
    check("label_surface_alignment", [row["surface"] for row in labels] == [row["surface"] for row in source], "surfaces exact")
    changed = [row for row in labels if row["gdt464_change"] != "UNCHANGED"]
    check("changed_label_count", len(changed) == 10 and {row["surface"] for row in changed} == expected_changed, "ten changes only")
    status = Counter(row["gdt464_hybrid_status"] for row in labels)
    check("label_status_counts", status == Counter({"FULL_FUNCTION_FORMULA": 18, "FUNCTION_SHELL_PLUS_LEARNED_CORE": 87, "OWNER_FAMILY_STEM_ONLY": 1, "WHOLE_LEARNED_LABEL": 1}), str(status))
    check("known_character_total", sum(int(row["known_function_character_count"]) for row in labels) == 440, "440")
    check("surface_character_total", sum(int(row["surface_character_count"]) for row in labels) == 713, "713")
    check("label_character_reconciliation", all(int(row["known_function_character_count"]) + int(row["remaining_learned_character_count"]) == len(row["surface"]) == int(row["surface_character_count"]) for row in labels), "all rows reconcile")
    check("full_formula_complete", all(int(row["remaining_learned_character_count"]) == 0 for row in labels if row["gdt464_hybrid_status"] == "FULL_FUNCTION_FORMULA"), "all full formulae complete")
    check("unchanged_rows_byte_values", all(
        row["gdt464_hybrid_status"] == old["gdt463_hybrid_status"]
        and row["known_function_character_count"] == old["known_function_character_count"]
        and row["ordered_function_recipe_trace"] == old["ordered_function_recipe_trace"]
        and row["revised_short_default_de"] == old["revised_short_default_de"]
        for row, old in zip(labels, source) if row["gdt464_change"] == "UNCHANGED"
    ), "all untouched semantic fields retained")

    check("residual_count", len(residuals) == 7, f"observed={len(residuals)}")
    check("residual_surface_set", {row["surface"] for row in residuals} == {"oiil", "ofaom", "chdaiirdainy", "ofchdamy", "opoeey", "of", "yddy"}, "seven old residuals")
    check("residual_promotions", sum(row["decision"] == "PROMOTE_BOUNDED_BRIDGE" for row in residuals) == 6, "six promoted")
    check("single_whole_residual", [row["surface"] for row in residuals if row["new_status"] == "WHOLE_LEARNED_LABEL"] == ["oiil"], "oiil only")
    check("no_owner_family_promotion", all(row["strict_owner_family_bridge"] == "NONE" for row in residuals), "zero strict family bridges")

    check("page_count", len(pages) == 6, f"observed={len(pages)}")
    check("page_label_total", sum(int(row["label_count"]) for row in pages) == 107, "107")
    check("page_change_total", sum(int(row["gdt464_change_count"]) for row in pages) == 10, "10")
    check("page_known_total", sum(int(row["known_function_character_count"]) for row in pages) == 440, "440")

    check("result_status", result["status"] == "FOUR_BOUNDED_BRIDGES_REDUCE_WHOLE_LABEL_TAIL_TO_ONE", result["status"])
    check("result_counts", result["source_label_count"] == 107 and result["bridge_count"] == 4 and result["changed_label_count"] == 10 and result["promoted_residual_count"] == 6, str(result))
    check("result_tail", result["remaining_whole_label_count"] == 1 and result["remaining_whole_labels"] == ["oiil"], str(result["remaining_whole_labels"]))
    check("result_status_counts", result["revised_hybrid_status_counts"] == dict(sorted(status.items())), str(result["revised_hybrid_status_counts"]))
    check("result_structure_counts", result["labels_with_any_function_count"] == 105 and result["labels_with_any_structure_count"] == 106, "105/106")
    check("result_character_counts", result["known_function_character_count"] == 440 and result["surface_character_count"] == 713 and result["known_function_character_fraction"] == "0.617111", "440/713")
    check("claim_ceiling", result["new_core_meanings"] == result["new_pages"] == result["surface_predictions"] == result["confirmed_lexemes"] == 0, "no expanded claim")
    check("sealed_pages_absent", all(not row.get("physical_page", "").startswith("f84") for table in (running, addresses, source, targets, labels, residuals, pages) for row in table), "no sealed page rows")

    before = {path.name: sha256(path) for path in GENERATED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    check("deterministic_rebuild_exit", completed.returncode == 0, completed.stderr[-500:] or "exit 0")
    after = {path.name: sha256(path) for path in GENERATED}
    check("deterministic_rebuild_bytes", before == after, "all generated artifact hashes unchanged")

    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "check_count": len(checks), "passed": passed, "failed": failed, "checks": checks,
    }
    VALIDATION_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "passed": passed, "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
