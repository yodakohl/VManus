#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_scribe_slot_grammar_nine_hundredth"
PREFIX = "NINE_HUNDRED_FIRST"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def recipe_tokens(recipe: str) -> list[str]:
    if recipe in {"NONE", "WHOLE[cheey|shey]", "RESUME_CARD"}:
        return [recipe]
    return recipe.split("+")


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    source_symbols = read(SOURCE / "NINE_HUNDREDTH_48_GRAMMAR_SYMBOLS.tsv")
    source_parses = read(SOURCE / "NINE_HUNDREDTH_231_IDENTITY_SLOT_PARSES.tsv")
    source_marks = read(SOURCE / "NINE_HUNDREDTH_437_MARK_SLOT_PARSES.tsv")
    source_units = read(SOURCE / "NINE_HUNDREDTH_118_UNIT_SLOT_GRAMMAR.tsv")
    symbols = read(HERE / f"{PREFIX}_48_SYMBOL_ALLOGRAPHS.tsv")
    rules = read(HERE / f"{PREFIX}_15_RENDERER_RULES.tsv")
    analyses = read(HERE / f"{PREFIX}_231_IDENTITY_RENDERER_ANALYSES.tsv")
    marks = read(HERE / f"{PREFIX}_437_MARK_RENDERER.tsv")
    units = read(HERE / f"{PREFIX}_118_UNIT_RENDERER.tsv")
    cards = read(HERE / f"{PREFIX}_6_JOB_CARD_RENDERER.tsv")
    roundtrips = read(HERE / f"{PREFIX}_10_RENDERED_ROUNDTRIPS.tsv")

    check("symbol_count", len(symbols) == 48, len(symbols))
    check("symbol_unique", len({row["symbol"] for row in symbols}) == 48, len({row["symbol"] for row in symbols}))
    check("symbol_set_preserved", {row["symbol"] for row in symbols} == {row["symbol"] for row in source_symbols}, "48/48")
    check("symbol_cues_nonempty", all(row["canonical_surface_cue"].strip() for row in symbols), "48/48")
    check("symbol_ecology_nonempty", all(int(row["weighted_mark_uses"]) > 0 and row["whole_surface_examples"].strip() for row in symbols), "48/48")
    check("symbol_position_use", all(int(row["initial_identity_uses"]) + int(row["medial_identity_uses"]) + int(row["final_identity_uses"]) > 0 for row in symbols), "48/48")

    expected_rules = {"ROOT_ORDER_COPY", "OPTIONAL_Q_CARRIER", "OK_FRAME_ALLOGRAPH", "OT_FRAME_ALLOGRAPH", "OL_FRAME_ALLOGRAPH", "CH_BODY_ALLOGRAPH", "E_GRADE_LENGTH", "ARGUMENT_OR_ADDRESS_TAIL", "L_PATH_ONSET", "R_STATE_ONSET", "Y_OPEN_ENDPOINT", "DY_CLOSED_ENDPOINT", "LOCAL_SIGN_COPY", "MEMORIZED_WHOLE_FORM", "REPEATED_ROOT_COPY"}
    check("renderer_rule_count", len(rules) == 15, len(rules))
    check("renderer_rule_set", {row["renderer_rule"] for row in rules} == expected_rules, sorted(row["renderer_rule"] for row in rules))
    check("renderer_rule_precedence", [int(row["precedence"]) for row in rules] == list(range(1, 16)), [row["precedence"] for row in rules])
    check("all_renderer_rules_used", all(int(row["identity_count"]) > 0 and int(row["mark_count"]) > 0 for row in rules), "15/15")

    check("analysis_count", len(analyses) == 231, len(analyses))
    check("analysis_unique", len({row["identity"] for row in analyses}) == 231, len({row["identity"] for row in analyses}))
    check("analysis_identity_set", {row["identity"] for row in analyses} == {row["identity"] for row in source_parses}, "231/231")
    renderability_expected = Counter({"COMPOSITIONAL_SINGLE_ATTESTED_RENDERING": 175, "COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE": 48, "MEMORIZED_EXACT_FORM": 8})
    check("renderability_split", Counter(row["renderability"] for row in analyses) == renderability_expected, Counter(row["renderability"] for row in analyses))
    recipe_families: dict[str, set[str]] = defaultdict(set)
    for row in source_parses:
        recipe_families[row["component_recipe"]].add(row["surface"])
    check("unique_recipe_count", len(recipe_families) == 190, len(recipe_families))
    check("multi_allograph_recipe_count", sum(len(values) > 1 for values in recipe_families.values()) == 16, sum(len(values) > 1 for values in recipe_families.values()))
    check("surface_families_exact", all(set(row["attested_surface_family"].split(" | ")) == recipe_families[row["component_recipe"]] for row in analyses), "231/231")
    check("allograph_choice_counts", all(int(row["allograph_choices"]) == len(recipe_families[row["component_recipe"]]) for row in analyses), "231/231")
    check("skeletons_nonempty", all(row["renderer_skeleton"].strip() for row in analyses), "231/231")
    check("rules_nonempty_known", all(row["renderer_rules"].strip() and set(row["renderer_rules"].split(" | ")) <= expected_rules for row in analyses), "231/231")

    q_rows = [row for row in analyses if "OPTIONAL_Q_CARRIER" in row["renderer_rules"].split(" | ")]
    check("q_carrier_exact", len(q_rows) == 30 and all(row["surface"].startswith("q") for row in q_rows), len(q_rows))
    dy_rows = [row for row in analyses if "DY_CLOSED_ENDPOINT" in row["renderer_rules"].split(" | ")]
    check("dy_rule_final_component", len(dy_rows) == 40 and all(recipe_tokens(row["component_recipe"])[-1] == "DY" for row in dy_rows), len(dy_rows))
    y_rows = [row for row in analyses if "Y_OPEN_ENDPOINT" in row["renderer_rules"].split(" | ")]
    check("y_rule_final_component", len(y_rows) == 78 and all(recipe_tokens(row["component_recipe"])[-1] == "Y" for row in y_rows), len(y_rows))
    repeated = [row for row in analyses if "REPEATED_ROOT_COPY" in row["renderer_rules"].split(" | ")]
    check("repeated_rule_exact", len(repeated) == 12 and all(len(recipe_tokens(row["component_recipe"])) != len(set(recipe_tokens(row["component_recipe"]))) for row in repeated), len(repeated))
    memorized = [row for row in analyses if row["renderability"] == "MEMORIZED_EXACT_FORM"]
    check("memorized_rule_alignment", len(memorized) == 8 and all("MEMORIZED_WHOLE_FORM" in row["renderer_rules"].split(" | ") for row in memorized), len(memorized))

    check("mark_count", len(marks) == 437, len(marks))
    check("mark_unique", len({row["order_mark_id"] for row in marks}) == 437, len({row["order_mark_id"] for row in marks}))
    source_mark_by_id = {row["order_mark_id"]: row for row in source_marks}
    analysis_by_id = {row["identity"]: row for row in analyses}
    check("mark_order_preserved", [row["order_mark_id"] for row in marks] == [row["order_mark_id"] for row in source_marks], "437/437")
    check("mark_semantics_preserved", all(
        row["surface"] == source_mark_by_id[row["order_mark_id"]]["surface"]
        and row["identity"] == source_mark_by_id[row["order_mark_id"]]["identity"]
        and row["component_recipe"] == source_mark_by_id[row["order_mark_id"]]["component_recipe"]
        and row["concrete_default_de"] == source_mark_by_id[row["order_mark_id"]]["concrete_default_de"]
        for row in marks
    ), "437/437")
    check("mark_renderer_alignment", all(
        row["renderer_skeleton"] == analysis_by_id[row["identity"]]["renderer_skeleton"]
        and row["renderer_rules"] == analysis_by_id[row["identity"]]["renderer_rules"]
        and row["attested_surface_family"] == analysis_by_id[row["identity"]]["attested_surface_family"]
        and row["renderability"] == analysis_by_id[row["identity"]]["renderability"]
        for row in marks
    ), "437/437")

    check("unit_count", len(units) == 118, len(units))
    check("unit_unique", len({row["master_unit_id"] for row in units}) == 118, len({row["master_unit_id"] for row in units}))
    source_unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in source_units}
    marks_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        marks_by_unit[source_unit_lookup[(row["order_id"], row["stage"], row["unit"])]["master_unit_id"]].append(row)
    check("unit_mark_total", sum(len(rows) for rows in marks_by_unit.values()) == 437, sum(len(rows) for rows in marks_by_unit.values()))
    check("unit_skeleton_sequences", all(row["renderer_skeleton_sequence"] == " || ".join(mark["renderer_skeleton"] for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("unit_renderability_sequences", all(row["renderability_sequence"] == " | ".join(mark["renderability"] for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("units_complete", all(row["renderer_complete"] == "YES" for row in units), "118/118")

    check("job_card_count", len(cards) == 6, len(cards))
    check("job_card_mark_total", sum(int(row["renderer_parsed_marks"]) for row in cards) == 437, sum(int(row["renderer_parsed_marks"]) for row in cards))
    check("job_cards_complete", all(row["renderer_complete"] == "YES" for row in cards), "6/6")
    check("roundtrip_count", len(roundtrips) == 10, len(roundtrips))
    check("roundtrip_attested_in_family", all(row["attested_surface"] in row["predicted_surface_family"].split(" | ") for row in roundtrips), "10/10")
    check("roundtrip_family_size", all(int(row["family_size"]) == len(row["predicted_surface_family"].split(" | ")) for row in roundtrips), "10/10")
    check("roundtrip_forward_split", Counter(row["forward_result"] for row in roundtrips) == Counter({"EXACT": 9, "FAMILY_PREDICTED__ALLOGRAPH_CHOICE_LEARNED": 1}), Counter(row["forward_result"] for row in roundtrips))

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
