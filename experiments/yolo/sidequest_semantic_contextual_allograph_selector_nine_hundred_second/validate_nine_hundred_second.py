#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_allograph_renderer_nine_hundred_first"
PREFIX = "NINE_HUNDRED_SECOND"

FEATURE_SETS = [
    ("MASTER_SECTION", ("master_section",)),
    ("UNIT_POSITION", ("unit_position",)),
    ("SECTION_PLUS_POSITION", ("master_section", "unit_position")),
    ("ORDER", ("order_id",)),
    ("ORDER_PLUS_POSITION", ("order_id", "unit_position")),
    ("PAGE", ("page",)),
    ("PAGE_PLUS_POSITION", ("page", "unit_position")),
    ("STAGE", ("stage",)),
    ("STAGE_PLUS_POSITION", ("stage", "unit_position")),
    ("UNIT", ("unit",)),
    ("UNIT_PLUS_POSITION", ("unit", "unit_position")),
    ("MEMORIZED_IDENTITY", ("identity",)),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def key_for(row: dict[str, str], fields: tuple[str, ...]) -> str:
    return "|".join(row[field] for field in fields)


def deterministic(rows: list[dict[str, str]], fields: tuple[str, ...]) -> bool:
    buckets: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        buckets[key_for(row, fields)].add(row["surface"])
    return all(len(values) == 1 for values in buckets.values())


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    source_analyses = read(SOURCE / "NINE_HUNDRED_FIRST_231_IDENTITY_RENDERER_ANALYSES.tsv")
    source_marks = read(SOURCE / "NINE_HUNDRED_FIRST_437_MARK_RENDERER.tsv")
    source_units = read(SOURCE / "NINE_HUNDRED_FIRST_118_UNIT_RENDERER.tsv")
    families = read(HERE / f"{PREFIX}_16_MULTI_ALLOGRAPH_FAMILIES.tsv")
    selectors = read(HERE / f"{PREFIX}_SELECTOR_RULES.tsv")
    occurrences = read(HERE / f"{PREFIX}_MULTI_ALLOGRAPH_OCCURRENCES.tsv")
    q_context = read(HERE / f"{PREFIX}_Q_CARRIER_CONTEXT.tsv")
    marks = read(HERE / f"{PREFIX}_437_CONTEXT_SELECTED_MARKS.tsv")
    units = read(HERE / f"{PREFIX}_118_CONTEXT_SELECTED_UNITS.tsv")
    cards = read(HERE / f"{PREFIX}_6_CONTEXT_SELECTED_JOB_CARDS.tsv")

    actual_recipe_surfaces: dict[str, set[str]] = defaultdict(set)
    for row in source_marks:
        actual_recipe_surfaces[row["component_recipe"]].add(row["surface"])
    expected_multi = {recipe for recipe, values in actual_recipe_surfaces.items() if len(values) > 1}
    check("multi_family_count", len(families) == 16, len(families))
    check("multi_family_unique", len({row["component_recipe"] for row in families}) == 16, len({row["component_recipe"] for row in families}))
    check("multi_recipe_set_exact", {row["component_recipe"] for row in families} == expected_multi, sorted(expected_multi))
    check("family_surfaces_exact", all(set(row["surface_family"].split(" | ")) == actual_recipe_surfaces[row["component_recipe"]] for row in families), "16/16")
    check("family_identity_counts", all(int(row["identities"]) == len(set(row["identity_list"].split(" | "))) for row in families), "16/16")
    check("family_occurrence_total", sum(int(row["occurrence_marks"]) for row in families) == 143, sum(int(row["occurrence_marks"]) for row in families))

    check("occurrence_count", len(occurrences) == 143, len(occurrences))
    check("occurrence_unique", len({row["order_mark_id"] for row in occurrences}) == 143, len({row["order_mark_id"] for row in occurrences}))
    check("occurrence_recipe_set", {row["component_recipe"] for row in occurrences} == expected_multi, len({row["component_recipe"] for row in occurrences}))
    check("occurrence_selector_matches", all(row["selector_match"] == "YES" and row["predicted_surface"] == row["surface"] for row in occurrences), "143/143")
    check("occurrence_q_flags", all((row["q_carrier"] == "YES") == row["surface"].startswith("q") for row in occurrences), "143/143")

    occurrence_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrences:
        occurrence_by_recipe[row["component_recipe"]].append(row)
    feature_index = {name: index for index, (name, _) in enumerate(FEATURE_SETS)}
    fields_by_name = dict(FEATURE_SETS)
    minimal_ok = True
    minimal_failures = []
    for family in families:
        selected = family["selector_feature_set"]
        rows = occurrence_by_recipe[family["component_recipe"]]
        selected_index = feature_index[selected]
        if not deterministic(rows, fields_by_name[selected]):
            minimal_ok = False
            minimal_failures.append(f"{family['component_recipe']}:selected_not_deterministic")
        for earlier_name, earlier_fields in FEATURE_SETS[:selected_index]:
            if deterministic(rows, earlier_fields):
                minimal_ok = False
                minimal_failures.append(f"{family['component_recipe']}:earlier={earlier_name}")
                break
    check("selector_feature_minimality", minimal_ok, minimal_failures)
    expected_feature_counts = Counter({"MASTER_SECTION": 5, "MEMORIZED_IDENTITY": 4, "UNIT": 2, "STAGE_PLUS_POSITION": 1, "ORDER": 1, "UNIT_POSITION": 1, "SECTION_PLUS_POSITION": 1, "ORDER_PLUS_POSITION": 1})
    check("selector_feature_split", Counter(row["selector_feature_set"] for row in families) == expected_feature_counts, Counter(row["selector_feature_set"] for row in families))
    portability_expected = Counter({"SHARED_WORKFLOW_SELECTOR": 7, "MEMORIZED_IDENTITY_SELECTOR": 4, "LOCAL_MINI_DECK_SELECTOR": 2, "STAGE_SELECTOR": 1, "ORDER_OR_PAGE_SELECTOR": 2})
    check("selector_portability_split", Counter(row["selector_portability"] for row in families) == portability_expected, Counter(row["selector_portability"] for row in families))

    check("selector_rule_count", len(selectors) == 68, len(selectors))
    check("selector_rule_unique_keys", len({(row["component_recipe"], row["selector_key"]) for row in selectors}) == 68, len({(row["component_recipe"], row["selector_key"]) for row in selectors}))
    selector_lookup = {(row["component_recipe"], row["selector_key"]): row["selected_surface"] for row in selectors}
    check("selector_rule_occurrence_alignment", all(selector_lookup[(row["component_recipe"], row["selector_key"])] == row["surface"] for row in occurrences), "143/143")
    check("selector_rule_family_counts", all(int(row["selector_rules"]) == sum(selector["component_recipe"] == row["component_recipe"] for selector in selectors) for row in families), "16/16")

    q_candidate_recipes = {row["component_recipe"] for row in families if row["q_carrier_surfaces"] != "NONE" and row["non_q_surfaces"]}
    check("q_candidate_family_count", len(q_candidate_recipes) == 6, len(q_candidate_recipes))
    check("q_context_cell_count", len(q_context) == 7, len(q_context))
    check("q_context_totals", sum(int(row["total_marks"]) for row in q_context) == sum(row["component_recipe"] in q_candidate_recipes for row in occurrences), (sum(int(row["total_marks"]) for row in q_context), sum(row["component_recipe"] in q_candidate_recipes for row in occurrences)))
    check("q_context_arithmetic", all(int(row["q_marks"]) + int(row["non_q_marks"]) == int(row["total_marks"]) for row in q_context), "7/7")

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
    check("all_mark_predictions_exact", all(row["predicted_surface"] == row["surface"] for row in marks), "437/437")
    check("mark_selector_status_split", Counter(row["allograph_selector_status"] for row in marks) == Counter({"CONTEXT_SELECTED": 143, "NO_CHOICE_NEEDED": 294}), Counter(row["allograph_selector_status"] for row in marks))

    check("unit_count", len(units) == 118, len(units))
    check("unit_unique", len({row["master_unit_id"] for row in units}) == 118, len({row["master_unit_id"] for row in units}))
    source_unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in source_units}
    marks_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        marks_by_unit[source_unit_lookup[(row["order_id"], row["stage"], row["unit"])]["master_unit_id"]].append(row)
    check("unit_mark_total", sum(len(rows) for rows in marks_by_unit.values()) == 437, sum(len(rows) for rows in marks_by_unit.values()))
    check("unit_surface_predictions", all(row["predicted_surface_sequence"] == " ".join(mark["surface"] for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("unit_multi_counts", all(int(row["multi_allograph_marks"]) == sum(mark["component_recipe"] in expected_multi for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("units_complete", all(row["selector_complete"] == "YES" for row in units), "118/118")

    check("job_card_count", len(cards) == 6, len(cards))
    check("job_card_multi_total", sum(int(row["multi_allograph_marks"]) for row in cards) == 143, sum(int(row["multi_allograph_marks"]) for row in cards))
    check("job_cards_complete", all(row["selector_complete"] == "YES" for row in cards), "6/6")

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
