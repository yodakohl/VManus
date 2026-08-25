#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_functional_allograph_microlexicon_nine_hundred_third"
SELECTOR = ROOT / "sidequest_semantic_contextual_allograph_selector_nine_hundred_second"
PREFIX = "NINE_HUNDRED_FOURTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    old_lexicon = read(SOURCE / "NINE_HUNDRED_THIRD_15_FUNCTIONAL_ALLOGRAPHS.tsv")
    source_families = read(SOURCE / "NINE_HUNDRED_THIRD_16_REVISED_ALLOGRAPH_FAMILIES.tsv")
    source_marks = read(SOURCE / "NINE_HUNDRED_THIRD_437_FUNCTION_SELECTED_MARKS.tsv")
    source_units = read(SOURCE / "NINE_HUNDRED_THIRD_118_FUNCTION_SELECTED_UNITS.tsv")
    all_occurrences = read(SELECTOR / "NINE_HUNDRED_SECOND_MULTI_ALLOGRAPH_OCCURRENCES.tsv")
    added = read(HERE / f"{PREFIX}_23_ADDITIONAL_FUNCTIONAL_ALLOGRAPHS.tsv")
    combined = read(HERE / f"{PREFIX}_38_COMPLETE_ALLOGRAPH_MICROLEXICON.tsv")
    occurrences = read(HERE / f"{PREFIX}_70_ADDITIONAL_MICROFUNCTION_OCCURRENCES.tsv")
    families = read(HERE / f"{PREFIX}_16_COMPLETE_FUNCTIONAL_FAMILIES.tsv")
    marks = read(HERE / f"{PREFIX}_437_FUNCTIONALLY_RENDERED_MARKS.tsv")
    units = read(HERE / f"{PREFIX}_118_FUNCTIONALLY_RENDERED_UNITS.tsv")
    cards = read(HERE / f"{PREFIX}_6_FUNCTIONALLY_RENDERED_JOB_CARDS.tsv")

    target_recipes = {"AIIN", "AR", "CHD+Y", "CHK+EE+Y", "OK+CHD+DY", "OK+OL", "OK+Y", "OL+Y", "OT+CHD+DY", "OT+Y"}
    check("added_allograph_count", len(added) == 23, len(added))
    check("added_allograph_unique", len({(row["component_recipe"], row["surface"]) for row in added}) == 23, len({(row["component_recipe"], row["surface"]) for row in added}))
    check("added_recipe_set", {row["component_recipe"] for row in added} == target_recipes, sorted(row["component_recipe"] for row in added))
    check("added_all_functional", all(row["entry_class"] == "FUNCTIONAL_ALLOGRAPH" for row in added), "23/23")
    check("added_occurrence_total", sum(int(row["occurrence_marks"]) for row in added) == 70, sum(int(row["occurrence_marks"]) for row in added))
    check("added_microfunctions_unique", len({row["renderer_microfunction"] for row in added}) == 23, len({row["renderer_microfunction"] for row in added}))

    check("combined_lexicon_count", len(combined) == 38, len(combined))
    check("combined_form_unique", len({(row["component_recipe"], row["surface"]) for row in combined}) == 38, len({(row["component_recipe"], row["surface"]) for row in combined}))
    check("combined_microfunction_unique", len({row["renderer_microfunction"] for row in combined}) == 38, len({row["renderer_microfunction"] for row in combined}))
    check("combined_class_split", Counter(row["entry_class"] for row in combined) == Counter({"FUNCTIONAL_ALLOGRAPH": 36, "LOCAL_WHOLE_WORD": 2}), Counter(row["entry_class"] for row in combined))
    old_forms = {(row["component_recipe"], row["surface"], row["renderer_microfunction"]) for row in old_lexicon}
    check("old_microlexicon_preserved", old_forms <= {(row["component_recipe"], row["surface"], row["renderer_microfunction"]) for row in combined}, len(old_forms))
    local_words = {(row["surface"], row["renderer_microfunction"]) for row in combined if row["entry_class"] == "LOCAL_WHOLE_WORD"}
    check("local_whole_words_exact", local_words == {("iokeeor", "WEATHER_CLASS_WHOLE_WORD"), ("daiial", "MOISTURE_STAGE_WHOLE_WORD")}, sorted(local_words))

    check("additional_occurrence_count", len(occurrences) == 70, len(occurrences))
    check("additional_occurrence_unique", len({row["order_mark_id"] for row in occurrences}) == 70, len({row["order_mark_id"] for row in occurrences}))
    check("additional_occurrence_recipe_set", {row["component_recipe"] for row in occurrences} == target_recipes, sorted(row["component_recipe"] for row in occurrences))
    check("additional_occurrence_exact", all(row["revised_match"] == "YES" and row["revised_predicted_surface"] == row["surface"] for row in occurrences), "70/70")
    combined_lookup = {(row["component_recipe"], row["surface"]): row for row in combined}
    check("additional_occurrence_lexicon_alignment", all(
        row["renderer_microfunction"] == combined_lookup[(row["component_recipe"], row["surface"])]["renderer_microfunction"]
        and row["intended_trigger_de"] == combined_lookup[(row["component_recipe"], row["surface"])]["intended_trigger_de"]
        for row in occurrences
    ), "70/70")
    expected_ids = {row["order_mark_id"] for row in all_occurrences if row["component_recipe"] in target_recipes}
    check("additional_occurrence_id_set", {row["order_mark_id"] for row in occurrences} == expected_ids, len(expected_ids))

    check("family_count", len(families) == 16, len(families))
    check("family_recipe_unique", len({row["component_recipe"] for row in families}) == 16, len({row["component_recipe"] for row in families}))
    source_family_by_recipe = {row["component_recipe"]: row for row in source_families}
    check("family_inventory_preserved", all(
        row["surface_family"] == source_family_by_recipe[row["component_recipe"]]["surface_family"]
        and row["occurrence_marks"] == source_family_by_recipe[row["component_recipe"]]["occurrence_marks"]
        for row in families
    ), "16/16")
    check("all_families_intent_selected", all(row["selector_feature_set"] == "INTENDED_MICROFUNCTION" for row in families), "16/16")
    check("all_raw_context_removed", all(row["raw_context_selector_removed"] == "YES" for row in families), "16/16")
    check("family_microfunction_inventory", all(
        int(row["selector_rules"]) == sum(item["component_recipe"] == row["component_recipe"] for item in combined)
        and row["microfunction_choices"].count("->") == int(row["selector_rules"])
        for row in families
    ), "16/16")
    check("family_occurrence_total", sum(int(row["occurrence_marks"]) for row in families) == 143, sum(int(row["occurrence_marks"]) for row in families))

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
    status_expected = Counter({"MICROFUNCTION_SELECTED": 143, "NO_CHOICE_NEEDED": 294})
    check("mark_selector_status_split", Counter(row["allograph_selector_status"] for row in marks) == status_expected, Counter(row["allograph_selector_status"] for row in marks))
    check("no_raw_context_selector", not any(row["allograph_selector_status"] == "CONTEXT_SELECTED" for row in marks), "0")
    micro_marks = [row for row in marks if row["allograph_selector_status"] == "MICROFUNCTION_SELECTED"]
    check("micro_mark_lexicon_alignment", all(
        row["renderer_microfunction"] == combined_lookup[(row["component_recipe"], row["surface"])]["renderer_microfunction"]
        for row in micro_marks
    ), "143/143")

    check("unit_count", len(units) == 118, len(units))
    check("unit_unique", len({row["master_unit_id"] for row in units}) == 118, len({row["master_unit_id"] for row in units}))
    source_unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in source_units}
    marks_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        marks_by_unit[source_unit_lookup[(row["order_id"], row["stage"], row["unit"])]["master_unit_id"]].append(row)
    check("unit_mark_total", sum(len(rows) for rows in marks_by_unit.values()) == 437, sum(len(rows) for rows in marks_by_unit.values()))
    check("unit_micro_counts", all(int(row["microfunction_marks"]) == sum(mark["allograph_selector_status"] == "MICROFUNCTION_SELECTED" for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("unit_micro_total", sum(int(row["microfunction_marks"]) for row in units) == 143, sum(int(row["microfunction_marks"]) for row in units))
    check("unit_raw_context_zero", all(int(row["raw_context_selector_marks"]) == 0 for row in units), "118/118")
    check("units_complete", all(row["complete_functional_renderer"] == "YES" for row in units), "118/118")

    check("job_card_count", len(cards) == 6, len(cards))
    check("job_card_micro_total", sum(int(row["microfunction_marks"]) for row in cards) == 143, sum(int(row["microfunction_marks"]) for row in cards))
    check("job_card_raw_context_zero", all(int(row["raw_context_selector_marks"]) == 0 for row in cards), "6/6")
    check("job_cards_complete", all(row["complete_functional_renderer"] == "YES" for row in cards), "6/6")

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
