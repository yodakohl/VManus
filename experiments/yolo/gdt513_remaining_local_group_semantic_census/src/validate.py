#!/usr/bin/env python3
"""Independent source, reading, hypothesis and lock validator for GDT513."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt513_remaining_local_group_semantic_census"
ART = BASE / "artifacts"
G405 = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G408 = ROOT / "experiments/yolo/gdt408_twenty_six_page_leave_one_page_transfer/artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G473 = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition/artifacts"

LOCAL_IN = G407 / "gdt407_693_local_group_edition.tsv"
GROUP_IN = G407 / "gdt407_5269_unified_group_ledger.tsv"
LEAVEOUT_IN = G408 / "gdt408_693_local_leaveout.tsv"
DICT_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
ADDRESS_IN = G473 / "gdt473_183_unified_address_working_edition.tsv"
LOCK_IN = G405 / "gdt405_426_locked_surface_dictionary.tsv"

EDITION_OUT = ART / "gdt513_510_remaining_local_working_edition.tsv"
RECIPE_OUT = ART / "gdt513_342_remaining_local_recipe_dictionary.tsv"
PAGE_OUT = ART / "gdt513_10_page_summary.tsv"
HYPOTHESIS_OUT = ART / "gdt513_5_hypothesis_scorecard.tsv"
EXPECTATION_OUT = ART / "gdt513_5_new_page_expectations.tsv"
COLLISION_OUT = ART / "gdt513_18_surface_parse_collision_audit.tsv"
READING_OUT = ART / "GDT513_REMAINING_LOCAL_READING_BOOK.md"
RESULT_OUT = ART / "gdt513_result.json"
VALIDATION_OUT = ART / "gdt513_validation.json"

STATUS = "ALL_510_REMAINING_LOCAL_GROUPS_RECEIVE_DEFAULTS__MIXED_RECORD_MODEL_SELECTED"
GUARD = "WORKING_COMPONENT_AND_STRUCTURAL_DEFAULTS_ONLY__NO_CONFIRMED_LEXEME"

ACTION_HEADS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ORDER_CONTROLS = {"OL", "OT"}
RELATIONS = {"AL", "AR", "L", "AIR"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}
LEGACY_STRUCTURAL = {"CHEO", "CTH", "CHK", "CPH", "CKH", "CFH"}

EXPECTED_PAGE_COUNTS = {
    "f67r2": 64,
    "f68r1": 34,
    "f69v": 140,
    "f70v": 218,
    "f75r": 10,
    "f76r": 9,
    "f81v": 2,
    "f82r": 13,
    "f83r": 4,
    "f88r": 16,
}
EXPECTED_EVIDENCE = {
    "A_EXACT_RUNNING_SURFACE_RECIPE": 252,
    "B_RUNNING_RECIPE_NEW_SURFACE": 22,
    "C_RUNNING_SURFACE_DIFFERENT_LOCAL_PARSE": 18,
    "D_EXACT_LOCAL_SURFACE_OTHER_PAGE": 6,
    "E_LOCAL_RECIPE_OTHER_PAGE": 5,
    "F_PAGE_PRIVATE_VISIBLE_COMPOSITION": 198,
    "G_SECTION_MARKER": 9,
}
EXPECTED_ROLES = {
    "COORDINATE_OR_CATALOGUE_CARD": 120,
    "ITINERARY_OR_ADDRESS_CARD": 104,
    "LOCAL_CLASS_OR_NAME_CARD": 23,
    "ORDERED_INSTRUCTION_CARD": 254,
    "SECTION_MARKER": 9,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def expected_role(atoms: list[str]) -> str:
    aset = set(atoms)
    if atoms == ["SECTION_MARKER"]:
        return "SECTION_MARKER"
    if aset & ACTION_HEADS:
        return "ORDERED_INSTRUCTION_CARD"
    if aset & ORDER_CONTROLS:
        return "ITINERARY_OR_ADDRESS_CARD"
    if aset & (RELATIONS | ARGUMENTS):
        return "COORDINATE_OR_CATALOGUE_CARD"
    return "LOCAL_CLASS_OR_NAME_CARD"


def main() -> int:
    local_rows = read_tsv(LOCAL_IN)
    group_rows = read_tsv(GROUP_IN)
    leaveout_rows = read_tsv(LEAVEOUT_IN)
    dictionary_rows = read_tsv(DICT_IN)
    address_rows = read_tsv(ADDRESS_IN)
    lock_rows = read_tsv(LOCK_IN)
    edition = read_tsv(EDITION_OUT)
    recipes = read_tsv(RECIPE_OUT)
    pages = read_tsv(PAGE_OUT)
    hypotheses = read_tsv(HYPOTHESIS_OUT)
    expectations = read_tsv(EXPECTATION_OUT)
    collisions = read_tsv(COLLISION_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    reading = READING_OUT.read_text(encoding="utf-8")

    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("source_counts", (len(local_rows), len(group_rows), len(leaveout_rows), len(dictionary_rows), len(address_rows), len(lock_rows)) == (693, 5269, 693, 46, 183, 426))
    check("output_counts", (len(edition), len(recipes), len(pages), len(hypotheses), len(expectations), len(collisions)) == (510, 342, 10, 5, 5, 18))
    check("edition_ids", [row["gdt513_local_id"] for row in edition] == [f"G513-L{i:03d}" for i in range(1, 511)])
    check("recipe_ids", [row["gdt513_recipe_id"] for row in recipes] == [f"G513-R{i:03d}" for i in range(1, 343)])
    check("collision_ids", [row["gdt513_collision_id"] for row in collisions] == [f"G513-C{i:02d}" for i in range(1, 19)])
    check("unique_source_ids", len({row["source_event_id"] for row in edition}) == 510)

    address_ids = {row["source_event_id"] for row in address_rows}
    expected_source = [row for row in local_rows if row["source_event_id"] not in address_ids]
    expected_ids = {row["source_event_id"] for row in expected_source}
    check("exact_183_510_partition", expected_ids == {row["source_event_id"] for row in edition} and not expected_ids & address_ids)
    check("source_order_preserved", [row["source_event_id"] for row in edition] == [row["source_event_id"] for row in expected_source])
    source_by_id = {row["source_event_id"]: row for row in expected_source}
    for row in edition:
        source = source_by_id[row["source_event_id"]]
        label = row["gdt513_local_id"]
        check(label + "_identity", all(row[field] == source[field] for field in ["physical_page", "source_panel", "register", "locus", "source_order", "owner_de", "surface", "component_recipe"]))

    dictionary = {row["atom"]: row for row in dictionary_rows}
    leaveout = {row["source_event_id"]: row for row in leaveout_rows}
    locked = {row["surface"]: row["locked_recipe"] for row in lock_rows}
    running_surface_recipes: dict[str, set[str]] = defaultdict(set)
    running_surface_events: Counter[str] = Counter()
    running_recipe_surfaces: dict[str, set[str]] = defaultdict(set)
    running_recipe_events: Counter[str] = Counter()
    running_recipe_pages: dict[str, set[str]] = defaultdict(set)
    for source in group_rows:
        if source["group_kind"] != "RUNNING_EVENT":
            continue
        surface = source["surface"]
        recipe = source["component_recipe"]
        running_surface_recipes[surface].add(recipe)
        running_surface_events[surface] += 1
        running_recipe_surfaces[recipe].add(surface)
        running_recipe_events[recipe] += 1
        running_recipe_pages[recipe].add(source["physical_page"])

    recomputed_evidence: Counter[str] = Counter()
    recomputed_roles: Counter[str] = Counter()
    lock_alignment: Counter[str] = Counter()
    for row in edition:
        recipe = row["component_recipe"]
        atoms = ["SECTION_MARKER"] if recipe == "SECTION_MARKER" else recipe.split("+")
        label = row["gdt513_local_id"]
        unresolved = [atom for atom in atoms if atom not in dictionary and atom not in LEGACY_STRUCTURAL and atom != "SECTION_MARKER"]
        check(label + "_known_atoms", not unresolved and row["unresolved_atoms"] == "NONE")
        role = expected_role(atoms)
        check(label + "_role", row["record_role"] == row["mixed_model_assignment"] == role)
        check(label + "_meaning_status", row["meaning_status"] == ("SECTION_MARKER_DEFAULT" if role == "SECTION_MARKER" else "COMPLETE_WORKING_COMPONENT_READING"))
        check(label + "_guard", row["guard"] == GUARD and row["portable_meaning_changed"] == row["structural_tag_promoted_to_word"] == "NO")
        check(label + "_trace_present", bool(row["component_trace_de"]) and row["component_trace_de"] in row["default_working_reading_de"] if role != "SECTION_MARKER" else row["default_working_reading_de"] == f"ABSCHNITTSMARKE {row['surface']}")
        check(label + "_structural_brackets", all((atom not in LEGACY_STRUCTURAL and not (atom in dictionary and dictionary[atom]["semantic_layer"] != "PORTABLE_BROAD_WORKING_CORE")) or f"[{atom}:" in row["component_trace_de"] for atom in atoms))

        surface = row["surface"]
        if role == "SECTION_MARKER":
            evidence = "G_SECTION_MARKER"
        elif recipe in running_surface_recipes.get(surface, set()):
            evidence = "A_EXACT_RUNNING_SURFACE_RECIPE"
        elif recipe in running_recipe_events:
            evidence = "B_RUNNING_RECIPE_NEW_SURFACE"
        elif surface in running_surface_recipes:
            evidence = "C_RUNNING_SURFACE_DIFFERENT_LOCAL_PARSE"
        elif leaveout[row["source_event_id"]]["leave_one_page_replay_class"] == "EXACT_LOCAL_SURFACE_OTHER_PAGE":
            evidence = "D_EXACT_LOCAL_SURFACE_OTHER_PAGE"
        elif leaveout[row["source_event_id"]]["leave_one_page_replay_class"] == "LOCAL_RECIPE_SHAPE_OTHER_PAGE":
            evidence = "E_LOCAL_RECIPE_OTHER_PAGE"
        else:
            evidence = "F_PAGE_PRIVATE_VISIBLE_COMPOSITION"
        check(label + "_evidence", row["running_support_tier"] == evidence)
        check(label + "_running_counts", int(row["running_surface_event_count"]) == running_surface_events[surface] and int(row["running_surface_recipe_count"]) == len(running_surface_recipes.get(surface, set())) and int(row["running_recipe_event_count"]) == running_recipe_events[recipe] and int(row["running_recipe_surface_count"]) == len(running_recipe_surfaces.get(recipe, set())))
        check(label + "_leaveout", row["local_leaveout_class"] == leaveout[row["source_event_id"]]["leave_one_page_replay_class"] and row["other_local_surface_pages"] == leaveout[row["source_event_id"]]["other_surface_pages"] and row["other_local_recipe_pages"] == leaveout[row["source_event_id"]]["other_recipe_pages"])
        recomputed_evidence[evidence] += 1
        recomputed_roles[role] += 1

        if surface not in locked:
            alignment = "NOT_IN_GDT405_LOCK"
            future = "NEW_SURFACE_USE_VISIBLE_LOCKED_ATOMS"
        elif locked[surface] == recipe:
            alignment = "MATCHES_GDT405_LOCK"
            future = "REPLAY_GDT405_LOCKED_RECIPE"
        elif role == "SECTION_MARKER":
            alignment = "ROLE_BOUND_SECTION_MARKER_DIFFERS_FROM_RUNNING_LOCK"
            future = "CURRENT_MARKER_STAYS_STRUCTURAL__FUTURE_RUNNING_FORM_REPLAYS_GDT405_LOCK"
        else:
            alignment = "LOCAL_ONLY_PARSE_DIFFERS_FROM_GDT405_LOCK"
            future = "CURRENT_LOCAL_PARSE_STAYS_LOCAL__FUTURE_BATCH_REPLAYS_GDT405_LOCK"
        check(label + "_lock", row["gdt405_lock_alignment"] == alignment and row["future_batch_recipe_policy"] == future and row["gdt405_locked_recipe"] == (locked[surface] if surface in locked else "NONE"))
        lock_alignment[alignment] += 1

    check("page_distribution", dict(Counter(row["physical_page"] for row in edition)) == EXPECTED_PAGE_COUNTS)
    check("distinct_counts", len({row["surface"] for row in edition}) == 370 and len({row["component_recipe"] for row in edition}) == 342)
    check("evidence_distribution", dict(recomputed_evidence) == EXPECTED_EVIDENCE)
    check("role_distribution", dict(recomputed_roles) == EXPECTED_ROLES)
    check("lock_distribution", lock_alignment == Counter({"NOT_IN_GDT405_LOCK": 343, "MATCHES_GDT405_LOCK": 157, "ROLE_BOUND_SECTION_MARKER_DIFFERS_FROM_RUNNING_LOCK": 8, "LOCAL_ONLY_PARSE_DIFFERS_FROM_GDT405_LOCK": 2}))

    recipe_by_name = {row["component_recipe"]: row for row in recipes}
    check("recipe_coverage", set(recipe_by_name) == {row["component_recipe"] for row in edition})
    for recipe, summary in recipe_by_name.items():
        rows = [row for row in edition if row["component_recipe"] == recipe]
        check("recipe_" + summary["gdt513_recipe_id"], int(summary["event_count"]) == len(rows) and int(summary["surface_count"]) == len({row["surface"] for row in rows}) and int(summary["physical_page_count"]) == len({row["physical_page"] for row in rows}) and summary["meaning_complete_for_every_event"] == "YES" and summary["guard"] == GUARD)

    page_by_name = {row["physical_page"]: row for row in pages}
    check("page_coverage", set(page_by_name) == set(EXPECTED_PAGE_COUNTS))
    for page, expected_count in EXPECTED_PAGE_COUNTS.items():
        row = page_by_name[page]
        check("page_" + page, int(row["local_group_count"]) == int(row["complete_default_count"]) == expected_count and sum(int(row[field]) for field in ["section_marker_count", "instruction_card_count", "itinerary_or_address_count", "coordinate_or_catalogue_count", "local_class_or_name_count"]) == expected_count and row["guard"] == GUARD)

    check("hypothesis_ranks", [int(row["working_rank"]) for row in hypotheses] == [1, 2, 3, 4, 5])
    check("hypothesis_ids", [row["hypothesis_id"] for row in hypotheses] == ["H5_MIXED_FORMULA_RECORD_NOMENCLATOR", "H3_DATASET_OR_RECORD_CARDS", "H1_PRODUCTIVE_FORMULA_LAYER", "H4_OWNER_CONDITIONED_RENDERER", "H2_PURE_NOMENCLATOR"])
    check("hypothesis_choice", hypotheses[0]["working_decision"] == "SELECT_AS_BEST_CURRENT_ARCHITECTURE" and hypotheses[-1]["working_decision"] == "REJECT_AS_SINGLE_GLOBAL_MODEL__KEEP_LOCAL_NAME_TAIL")
    check("hypothesis_exploratory", all(row["statistical_score"] == "NOT_APPLICABLE_EXPLORATORY_COMPARISON" for row in hypotheses))
    check("expectation_ids", [row["expectation_id"] for row in expectations] == [f"G513-P{i}" for i in range(1, 6)])

    collision_ids = {row["source_event_id"] for row in collisions}
    expected_collision_ids = {row["source_event_id"] for row in edition if row["running_support_tier"] == "C_RUNNING_SURFACE_DIFFERENT_LOCAL_PARSE"}
    check("collision_coverage", collision_ids == expected_collision_ids)
    check("collision_structural", all(row["collision_explanation"] != "UNRESOLVED_OWNER_CONDITIONED_PARSE_WARNING" and row["portable_polysemy_inferred"] == row["structural_tag_promoted_to_word"] == "NO" and row["guard"] == GUARD for row in collisions))
    check("collision_lock_mismatch_count", sum(row["gdt405_lock_alignment"] == "LOCAL_ONLY_PARSE_DIFFERS_FROM_GDT405_LOCK" for row in collisions) == 2)

    check("result_status", result["status"] == STATUS)
    check("result_primary_counts", result["remaining_local_groups"] == 510 and result["physical_pages"] == 10 and result["distinct_surfaces"] == 370 and result["distinct_recipes"] == 342 and result["complete_component_readings"] == 501 and result["section_marker_defaults"] == 9 and result["unresolved_atoms"] == 0)
    check("result_evidence", result["evidence_tier_counts"] == EXPECTED_EVIDENCE and result["direct_running_recipe_support"] == 274 and result["page_private_visible_compositions"] == 198 and result["leaveout_page_private_events"] == 297)
    check("result_roles", result["record_role_counts"] == EXPECTED_ROLES)
    check("result_collisions", result["surface_parse_collisions"] == result["surface_parse_collisions_with_named_structural_explanation"] == 18)
    check("result_lock", result["gdt405_lock_contacts"] == 167 and result["gdt405_lock_recipe_matches"] == 157 and result["gdt405_local_only_recipe_mismatches"] == 2 and result["gdt405_section_marker_role_mismatches"] == 8)
    check("result_model", result["hypotheses_compared"] == 5 and result["selected_architecture"] == "H5_MIXED_FORMULA_RECORD_NOMENCLATOR" and result["new_page_expectations"] == 5)
    check("result_invariants", result["portable_meanings_changed"] == result["new_portable_atoms"] == result["structural_tags_promoted_to_words"] == 0 and result["guard"] == GUARD)
    check("sealed_absence", all("f84" not in str(value) for row in edition for value in row.values()))
    check("reading_status", STATUS in reading and "501 besitzen bereits" in reading and "Keine Zeile bestätigt" in reading)
    check("reading_pages", all(f"## {page}" in reading for page in EXPECTED_PAGE_COUNTS))
    check("reading_complete", all(row["default_working_reading_de"] in reading for row in edition))

    failed = [name for name, passed in checks if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "failed_checks": failed,
    }
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
