#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_mixed_root_codebook_eight_hundred_ninety_ninth"
PREFIX = "NINE_HUNDREDTH"


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

    source_roots = read(SOURCE / "EIGHT_HUNDRED_NINETY_NINTH_36_MIXED_ROOT_CODEBOOK.tsv")
    source_vocab = read(SOURCE / "EIGHT_HUNDRED_NINETY_NINTH_231_MIXED_CODEBOOK_VOCABULARY.tsv")
    source_marks = read(SOURCE / "EIGHT_HUNDRED_NINETY_NINTH_437_MIXED_CODEBOOK_MARK_DECK.tsv")
    source_units = read(SOURCE / "EIGHT_HUNDRED_NINETY_NINTH_118_MIXED_CODEBOOK_UNITS.tsv")
    symbols = read(HERE / f"{PREFIX}_48_GRAMMAR_SYMBOLS.tsv")
    patterns = read(HERE / f"{PREFIX}_8_CARD_PATTERNS.tsv")
    parses = read(HERE / f"{PREFIX}_231_IDENTITY_SLOT_PARSES.tsv")
    marks = read(HERE / f"{PREFIX}_437_MARK_SLOT_PARSES.tsv")
    units = read(HERE / f"{PREFIX}_118_UNIT_SLOT_GRAMMAR.tsv")
    cards = read(HERE / f"{PREFIX}_6_JOB_CARD_SLOT_SUMMARY.tsv")
    roundtrips = read(HERE / f"{PREFIX}_10_WORKED_ROUNDTRIPS.tsv")

    check("source_root_count", len(source_roots) == 36, len(source_roots))
    check("grammar_symbol_count", len(symbols) == 48, len(symbols))
    check("grammar_symbol_unique", len({row["symbol"] for row in symbols}) == 48, len({row["symbol"] for row in symbols}))
    symbol_by_name = {row["symbol"]: row for row in symbols}
    check("all_source_roots_present", {row["root"] for row in source_roots} <= set(symbol_by_name), len({row["root"] for row in source_roots} & set(symbol_by_name)))
    check("utility_symbol_count", len(set(symbol_by_name) - {row["root"] for row in source_roots}) == 12, len(set(symbol_by_name) - {row["root"] for row in source_roots}))
    check("utility_symbols_exact", set(symbol_by_name) - {row["root"] for row in source_roots} == {"A_ADDR", "AM_ADDR", "D_ADDR", "D_LABEL", "S_ADDR", "S_LABEL", "CHEO", "WHOLE[cheey|shey]", "NONE", "CFH", "OS", "RESUME_CARD"}, sorted(set(symbol_by_name) - {row["root"] for row in source_roots}))
    check("slot_roles_nonempty", all(row["slot_role"].strip() for row in symbols), "48/48")
    check("key_slot_roles", {name: symbol_by_name[name]["slot_role"] for name in ["OT", "OK", "E", "OR", "AL", "R", "Y", "DY"]} == {"OT": "ORDER", "OK": "OPERATION", "E": "GRADE", "OR": "MATERIAL", "AL": "ADDRESS", "R": "STATE", "Y": "REFERENT", "DY": "ENDPOINT"}, "8/8")

    expected_patterns = {"WHOLE_LEXICON", "CLOSING_INSTRUCTION", "ORDERED_INSTRUCTION", "OPERATION_INSTRUCTION", "TRANSFER_OR_PATH", "STATE_OR_GRADE", "ARGUMENT_OR_ADDRESS", "REFERENT_OR_LABEL"}
    check("pattern_count", len(patterns) == 8, len(patterns))
    check("pattern_set_exact", {row["pattern"] for row in patterns} == expected_patterns, sorted(row["pattern"] for row in patterns))
    check("pattern_precedence", [int(row["precedence"]) for row in patterns] == list(range(1, 9)), [row["precedence"] for row in patterns])
    check("pattern_identity_total", sum(int(row["identity_count"]) for row in patterns) == 231, sum(int(row["identity_count"]) for row in patterns))
    check("pattern_mark_total", sum(int(row["mark_count"]) for row in patterns) == 437, sum(int(row["mark_count"]) for row in patterns))
    check("all_patterns_used", all(int(row["identity_count"]) > 0 and int(row["mark_count"]) > 0 for row in patterns), "8/8")

    check("identity_parse_count", len(parses) == 231, len(parses))
    check("identity_parse_unique", len({row["identity"] for row in parses}) == 231, len({row["identity"] for row in parses}))
    check("identity_set_preserved", {row["identity"] for row in parses} == {row["identity"] for row in source_vocab}, "231/231")
    check("identity_mark_total", sum(int(row["marks"]) for row in parses) == 437, sum(int(row["marks"]) for row in parses))
    check("all_identities_patterned", all(row["primary_pattern"] in expected_patterns for row in parses), "231/231")
    check("all_identities_have_slots", all(row["slot_signature"].strip() and row["root_reading_de"].strip() for row in parses), "231/231")
    for row in parses:
        parts = recipe_tokens(row["component_recipe"])
        roles = row["slot_signature"].split(">")
        values = row["root_reading_de"].split(" · ")
        if not (len(parts) == len(roles) == len(values)):
            check("recipe_slot_value_arity", False, row["identity"])
            break
    else:
        check("recipe_slot_value_arity", True, "231/231")
    check("all_recipe_symbols_known", all(all(token in symbol_by_name for token in recipe_tokens(row["component_recipe"])) for row in parses), "231/231")

    check("mark_count", len(marks) == 437, len(marks))
    check("mark_unique", len({row["order_mark_id"] for row in marks}) == 437, len({row["order_mark_id"] for row in marks}))
    source_mark_by_id = {row["order_mark_id"]: row for row in source_marks}
    parse_by_id = {row["identity"]: row for row in parses}
    check("mark_order_preserved", [row["order_mark_id"] for row in marks] == [row["order_mark_id"] for row in source_marks], "437/437")
    check("mark_form_preserved", all(
        row["surface"] == source_mark_by_id[row["order_mark_id"]]["surface"]
        and row["identity"] == source_mark_by_id[row["order_mark_id"]]["identity"]
        and row["component_recipe"] == source_mark_by_id[row["order_mark_id"]]["component_recipe"]
        and row["concrete_default_de"] == source_mark_by_id[row["order_mark_id"]]["concrete_default_de"]
        for row in marks
    ), "437/437")
    check("mark_parse_alignment", all(
        row["slot_signature"] == parse_by_id[row["identity"]]["slot_signature"]
        and row["primary_card_pattern"] == parse_by_id[row["identity"]]["primary_pattern"]
        and row["root_reading_de"] == parse_by_id[row["identity"]]["root_reading_de"]
        for row in marks
    ), "437/437")

    check("unit_count", len(units) == 118, len(units))
    check("unit_unique", len({row["master_unit_id"] for row in units}) == 118, len({row["master_unit_id"] for row in units}))
    source_unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in source_units}
    marks_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        marks_by_unit[source_unit_lookup[(row["order_id"], row["stage"], row["unit"])]["master_unit_id"]].append(row)
    check("unit_mark_total", sum(len(rows) for rows in marks_by_unit.values()) == 437, sum(len(rows) for rows in marks_by_unit.values()))
    check("unit_pattern_sequences", all(row["card_pattern_sequence"] == " -> ".join(mark["primary_card_pattern"] for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("unit_slot_sequences", all(row["slot_signature_sequence"] == " || ".join(mark["slot_signature"] for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("unit_root_sequences", all(row["root_reading_sequence_de"] == " ; ".join(mark["root_reading_de"] for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("all_units_complete", all(row["slot_grammar_complete"] == "YES" for row in units), "118/118")

    check("job_card_count", len(cards) == 6, len(cards))
    check("job_card_mark_total", sum(int(row["slot_parsed_marks"]) for row in cards) == 437, sum(int(row["slot_parsed_marks"]) for row in cards))
    check("job_cards_complete", all(row["slot_grammar_complete"] == "YES" for row in cards), "6/6")
    check("roundtrip_count", len(roundtrips) == 10, len(roundtrips))
    check("roundtrip_recipes_unique", len({row["root_recipe"] for row in roundtrips}) == 10, len({row["root_recipe"] for row in roundtrips}))
    vocab_recipe_surfaces: dict[str, set[str]] = defaultdict(set)
    for row in source_vocab:
        vocab_recipe_surfaces[row["component_recipe"]].add(row["house_surface"])
    check("roundtrip_surfaces_attested", all(row["attested_surface"] in vocab_recipe_surfaces[row["root_recipe"]] for row in roundtrips), "10/10")
    check("roundtrip_slots_exact", all(len(recipe_tokens(row["root_recipe"])) == len(row["slot_signature"].split(">")) for row in roundtrips), "10/10")

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
