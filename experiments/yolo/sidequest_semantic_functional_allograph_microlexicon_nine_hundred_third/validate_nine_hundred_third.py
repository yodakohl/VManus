#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_contextual_allograph_selector_nine_hundred_second"
PREFIX = "NINE_HUNDRED_THIRD"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    source_families = read(SOURCE / "NINE_HUNDRED_SECOND_16_MULTI_ALLOGRAPH_FAMILIES.tsv")
    source_occurrences = read(SOURCE / "NINE_HUNDRED_SECOND_MULTI_ALLOGRAPH_OCCURRENCES.tsv")
    source_marks = read(SOURCE / "NINE_HUNDRED_SECOND_437_CONTEXT_SELECTED_MARKS.tsv")
    source_units = read(SOURCE / "NINE_HUNDRED_SECOND_118_CONTEXT_SELECTED_UNITS.tsv")
    lexicon = read(HERE / f"{PREFIX}_15_FUNCTIONAL_ALLOGRAPHS.tsv")
    occurrences = read(HERE / f"{PREFIX}_73_MICROFUNCTION_OCCURRENCES.tsv")
    families = read(HERE / f"{PREFIX}_16_REVISED_ALLOGRAPH_FAMILIES.tsv")
    marks = read(HERE / f"{PREFIX}_437_FUNCTION_SELECTED_MARKS.tsv")
    units = read(HERE / f"{PREFIX}_118_FUNCTION_SELECTED_UNITS.tsv")
    cards = read(HERE / f"{PREFIX}_6_FUNCTION_SELECTED_JOB_CARDS.tsv")

    target_recipes = {"AL", "OL", "Y", "NONE", "CHD+DY", "SH+EE+Y"}
    expected_forms = {
        ("AL", "dal"), ("AL", "cheal"),
        ("OL", "ol"), ("OL", "chol"), ("OL", "ls"),
        ("Y", "y"), ("Y", "dy"), ("Y", "chey"), ("Y", "chy"),
        ("NONE", "iokeeor"), ("NONE", "daiial"),
        ("CHD+DY", "schedy"), ("CHD+DY", "dchdy"),
        ("SH+EE+Y", "cheey"), ("SH+EE+Y", "sheey"),
    }
    check("microlexicon_count", len(lexicon) == 15, len(lexicon))
    check("microlexicon_unique", len({(row["component_recipe"], row["surface"]) for row in lexicon}) == 15, len({(row["component_recipe"], row["surface"]) for row in lexicon}))
    check("microlexicon_form_set", {(row["component_recipe"], row["surface"]) for row in lexicon} == expected_forms, sorted((row["component_recipe"], row["surface"]) for row in lexicon))
    check("target_recipe_set", {row["component_recipe"] for row in lexicon} == target_recipes, sorted(row["component_recipe"] for row in lexicon))
    check("entry_class_split", Counter(row["entry_class"] for row in lexicon) == Counter({"FUNCTIONAL_ALLOGRAPH": 13, "LOCAL_WHOLE_WORD": 2}), Counter(row["entry_class"] for row in lexicon))
    check("microfunction_unique", len({row["renderer_microfunction"] for row in lexicon}) == 15, len({row["renderer_microfunction"] for row in lexicon}))
    check("microfunction_occurrence_total", sum(int(row["occurrence_marks"]) for row in lexicon) == 73, sum(int(row["occurrence_marks"]) for row in lexicon))
    dy_row = next(row for row in lexicon if row["component_recipe"] == "Y" and row["surface"] == "dy")
    check("dy_is_echo_not_close", dy_row["renderer_microfunction"] == "ECHOED_CURRENT_REFERENT" and "kein Schluss" in dy_row["intended_trigger_de"], (dy_row["renderer_microfunction"], dy_row["intended_trigger_de"]))

    check("micro_occurrence_count", len(occurrences) == 73, len(occurrences))
    check("micro_occurrence_unique", len({row["order_mark_id"] for row in occurrences}) == 73, len({row["order_mark_id"] for row in occurrences}))
    check("micro_occurrence_recipe_set", {row["component_recipe"] for row in occurrences} == target_recipes, sorted(row["component_recipe"] for row in occurrences))
    check("micro_occurrence_match", all(row["revised_match"] == "YES" and row["revised_predicted_surface"] == row["surface"] for row in occurrences), "73/73")
    lexicon_lookup = {(row["component_recipe"], row["surface"]): row for row in lexicon}
    check("micro_occurrence_lexicon_alignment", all(
        row["renderer_microfunction"] == lexicon_lookup[(row["component_recipe"], row["surface"])]["renderer_microfunction"]
        and row["intended_trigger_de"] == lexicon_lookup[(row["component_recipe"], row["surface"])]["intended_trigger_de"]
        for row in occurrences
    ), "73/73")
    source_target_ids = {row["order_mark_id"] for row in source_occurrences if row["component_recipe"] in target_recipes}
    check("micro_occurrence_id_set_exact", {row["order_mark_id"] for row in occurrences} == source_target_ids, len(source_target_ids))

    check("family_count", len(families) == 16, len(families))
    check("family_recipe_unique", len({row["component_recipe"] for row in families}) == 16, len({row["component_recipe"] for row in families}))
    source_family_by_recipe = {row["component_recipe"]: row for row in source_families}
    check("family_form_inventory_preserved", all(
        row["surface_family"] == source_family_by_recipe[row["component_recipe"]]["surface_family"]
        and row["occurrence_marks"] == source_family_by_recipe[row["component_recipe"]]["occurrence_marks"]
        for row in families
    ), "16/16")
    targeted_families = [row for row in families if row["component_recipe"] in target_recipes]
    remaining_families = [row for row in families if row["component_recipe"] not in target_recipes]
    check("target_family_count", len(targeted_families) == 6, len(targeted_families))
    check("target_family_selector", all(row["selector_feature_set"] == "INTENDED_MICROFUNCTION" for row in targeted_families), "6/6")
    check("remaining_family_count", len(remaining_families) == 10, len(remaining_families))
    check("remaining_occurrence_total", sum(int(row["occurrence_marks"]) for row in remaining_families) == 70, sum(int(row["occurrence_marks"]) for row in remaining_families))
    check("remaining_no_identity_selector", not any(row["selector_feature_set"] == "MEMORIZED_IDENTITY" for row in remaining_families), "0")
    check("remaining_no_unit_selector", not any(row["selector_feature_set"] == "UNIT" for row in remaining_families), "0")
    check("local_whole_family_retained", next(row for row in targeted_families if row["component_recipe"] == "NONE")["selector_portability"] == "LOCAL_WHOLE_WORD_SELECTOR", "NONE")

    check("mark_count", len(marks) == 437, len(marks))
    check("mark_unique", len({row["order_mark_id"] for row in marks}) == 437, len({row["order_mark_id"] for row in marks}))
    source_mark_by_id = {row["order_mark_id"]: row for row in source_marks}
    check("mark_order_preserved", [row["order_mark_id"] for row in marks] == [row["order_mark_id"] for row in source_marks], "437/437")
    check("mark_form_semantics_preserved", all(
        row["surface"] == source_mark_by_id[row["order_mark_id"]]["surface"]
        and row["identity"] == source_mark_by_id[row["order_mark_id"]]["identity"]
        and row["component_recipe"] == source_mark_by_id[row["order_mark_id"]]["component_recipe"]
        and row["concrete_default_de"] == source_mark_by_id[row["order_mark_id"]]["concrete_default_de"]
        for row in marks
    ), "437/437")
    check("all_surface_predictions_exact", all(row["predicted_surface"] == row["surface"] for row in marks), "437/437")
    micro_marks = [row for row in marks if row["allograph_selector_status"] == "MICROFUNCTION_SELECTED"]
    check("micro_mark_count", len(micro_marks) == 73, len(micro_marks))
    check("micro_mark_id_set", {row["order_mark_id"] for row in micro_marks} == source_target_ids, len(micro_marks))
    check("micro_mark_fields", all(row["allograph_selector_feature"] == "INTENDED_MICROFUNCTION" and row["renderer_microfunction"] != "NOT_APPLICABLE" for row in micro_marks), "73/73")
    check("nonmicro_marks_unchanged_selector", all(
        row["allograph_selector_feature"] == source_mark_by_id[row["order_mark_id"]]["allograph_selector_feature"]
        and row["allograph_selector_key"] == source_mark_by_id[row["order_mark_id"]]["allograph_selector_key"]
        for row in marks if row["order_mark_id"] not in source_target_ids
    ), "364/364")

    check("unit_count", len(units) == 118, len(units))
    check("unit_unique", len({row["master_unit_id"] for row in units}) == 118, len({row["master_unit_id"] for row in units}))
    source_unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in source_units}
    marks_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        marks_by_unit[source_unit_lookup[(row["order_id"], row["stage"], row["unit"])]["master_unit_id"]].append(row)
    check("unit_mark_total", sum(len(rows) for rows in marks_by_unit.values()) == 437, sum(len(rows) for rows in marks_by_unit.values()))
    check("unit_micro_counts", all(int(row["microfunction_marks"]) == sum(mark["allograph_selector_status"] == "MICROFUNCTION_SELECTED" for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("unit_micro_total", sum(int(row["microfunction_marks"]) for row in units) == 73, sum(int(row["microfunction_marks"]) for row in units))
    check("units_complete", all(row["functional_selector_complete"] == "YES" for row in units), "118/118")

    check("job_card_count", len(cards) == 6, len(cards))
    check("job_card_micro_total", sum(int(row["microfunction_marks"]) for row in cards) == 73, sum(int(row["microfunction_marks"]) for row in cards))
    check("job_cards_complete", all(row["functional_selector_complete"] == "YES" for row in cards), "6/6")

    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    observed_pages = {row["page"] for row in marks}
    check("fixed_page_allowlist", observed_pages <= allowed_pages, sorted(observed_pages))
    check("sealed_pages_absent_from_data", not any(page.lower().startswith("f84") for page in observed_pages), "0")

    passed = all(item["passed"] for item in checks)
    result = {"status": "PASS" if passed else "FAIL", "checks": len(checks), "passed": sum(bool(item["passed"]) for item in checks), "failed": [item for item in checks if not item["passed"]], "details": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(json.dumps(result["failed"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
