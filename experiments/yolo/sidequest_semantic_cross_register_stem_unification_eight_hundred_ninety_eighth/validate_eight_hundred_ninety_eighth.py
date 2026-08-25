#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_speakable_condition_lexicon_eight_hundred_ninety_seventh"
PREFIX = "EIGHT_HUNDRED_NINETY_EIGHTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    source_marks = read(SOURCE / "EIGHT_HUNDRED_NINETY_SEVENTH_437_ALL_SPEAKABLE_MARK_DECK.tsv")
    source_vocab = read(SOURCE / "EIGHT_HUNDRED_NINETY_SEVENTH_231_COMPLETE_WORKSHOP_VOCABULARY.tsv")
    source_units = read(SOURCE / "EIGHT_HUNDRED_NINETY_SEVENTH_118_ALL_EXECUTABLE_UNITS.tsv")
    surface = read(HERE / f"{PREFIX}_8_EXACT_SURFACE_BRIDGES.tsv")
    components = read(HERE / f"{PREFIX}_22_SHARED_COMPONENT_ROOTS.tsv")
    conditions = read(HERE / f"{PREFIX}_73_PORTABLE_CONDITION_READINGS.tsv")
    vocabulary = read(HERE / f"{PREFIX}_231_UNIFIED_WORKSHOP_VOCABULARY.tsv")
    marks = read(HERE / f"{PREFIX}_437_UNIFIED_MARK_DECK.tsv")
    units = read(HERE / f"{PREFIX}_118_UNIFIED_UNIT_EDITION.tsv")
    cards = read(HERE / f"{PREFIX}_6_UNIFIED_JOB_CARDS.tsv")

    check("surface_bridge_count", len(surface) == 8, len(surface))
    check("surface_bridge_unique", len({row["surface"] for row in surface}) == 8, len({row["surface"] for row in surface}))
    check("surface_mark_total", sum(int(row["total_marks"]) for row in surface) == 65, sum(int(row["total_marks"]) for row in surface))
    check("every_surface_crosses_register", all(int(row["prose_marks"]) > 0 and int(row["condition_marks"]) > 0 for row in surface), "8/8")
    check("component_root_count", len(components) == 22, len(components))
    check("component_unique", len({row["component"] for row in components}) == 22, len({row["component"] for row in components}))
    check("every_component_crosses_register", all(int(row["prose_marks"]) > 0 and int(row["condition_marks"]) > 0 for row in components), "22/22")
    check("condition_count", len(conditions) == 73, len(conditions))
    check("condition_id_unique", len({row["opaque_local_id"] for row in conditions}) == 73, len({row["opaque_local_id"] for row in conditions}))
    check("condition_source_split", Counter(row["reading_source"] for row in conditions) == Counter({"PORTABLE_COMPONENT_COMPOSITION": 58, "EXACT_SURFACE_BRIDGE": 13, "LOCAL_WHOLE_WORD": 2}), Counter(row["reading_source"] for row in conditions))
    check("local_expansions_retained", all(row["local_expansion_de"].strip() for row in conditions), "73/73")
    check("portable_readings_nonempty", all(row["portable_workshop_reading_de"].strip() for row in conditions), "73/73")

    check("vocabulary_count", len(vocabulary) == 231, len(vocabulary))
    check("vocabulary_unique", len({row["identity"] for row in vocabulary}) == 231, len({row["identity"] for row in vocabulary}))
    check("mark_count", len(marks) == 437, len(marks))
    check("mark_ids_unique", len({row["order_mark_id"] for row in marks}) == 437, len({row["order_mark_id"] for row in marks}))
    check("unit_count", len(units) == 118, len(units))
    check("unit_ids_unique", len({row["master_unit_id"] for row in units}) == 118, len({row["master_unit_id"] for row in units}))
    check("job_card_count", len(cards) == 6, len(cards))

    surface_roots = {row["surface"]: row["portable_root_de"] for row in surface}
    for name, root in surface_roots.items():
        values = {row["concrete_default_de"] for row in marks if row["surface"] == name}
        check(f"surface_{name}_single_value", values == {root}, sorted(values))
    check("surface_bridge_mark_revisions", sum(row["ninth_lesson"] == "EXACT_SURFACE_BRIDGE" for row in marks) == 52, sum(row["ninth_lesson"] == "EXACT_SURFACE_BRIDGE" for row in marks))
    check("condition_component_revisions", sum(row["ninth_lesson"] == "CONDITION_COMPONENT_COMPOSITION" for row in marks) == 73, sum(row["ninth_lesson"] == "CONDITION_COMPONENT_COMPOSITION" for row in marks))
    check("unchanged_marks", sum(row["ninth_lesson"] == "NO_CHANGE" for row in marks) == 312, sum(row["ninth_lesson"] == "NO_CHANGE" for row in marks))

    condition_by_id = {row["opaque_local_id"]: row for row in conditions}
    condition_marks = [row for row in marks if row["master_section"] == "WHEN"]
    check("condition_mark_count", len(condition_marks) == 73, len(condition_marks))
    check("condition_mark_values_exact", all(row["concrete_default_de"] == condition_by_id[row["source_id"]]["portable_workshop_reading_de"] for row in condition_marks), "73/73")
    check("condition_mark_actions_retained", all(row["apprentice_action"] == "READ_LOCAL_CONDITION_WORD" for row in condition_marks), Counter(row["apprentice_action"] for row in condition_marks))

    identity_values: dict[str, set[str]] = defaultdict(set)
    for row in marks:
        identity_values[row["identity"]].add(row["concrete_default_de"])
    check("identity_value_invariance", all(len(values) == 1 for values in identity_values.values()), {key: sorted(values) for key, values in identity_values.items() if len(values) > 1})
    vocab_by_id = {row["identity"]: row for row in vocabulary}
    check("vocabulary_mark_alignment", all(vocab_by_id[row["identity"]]["short_value_de"] == row["concrete_default_de"] for row in marks), "437/437")
    check("vocabulary_id_set_preserved", {row["identity"] for row in vocabulary} == {row["identity"] for row in source_vocab}, len(vocabulary))

    source_mark_by_id = {row["order_mark_id"]: row for row in source_marks}
    check("source_order_preserved", [row["order_mark_id"] for row in marks] == [row["order_mark_id"] for row in source_marks], "437/437")
    check("surface_and_identity_preserved", all(
        row["surface"] == source_mark_by_id[row["order_mark_id"]]["surface"]
        and row["identity"] == source_mark_by_id[row["order_mark_id"]]["identity"]
        and row["component_recipe"] == source_mark_by_id[row["order_mark_id"]]["component_recipe"]
        for row in marks
    ), "437/437")
    check("no_model_copy_action", not any(row["apprentice_action"] == "COPY_LOCAL_MODEL" for row in marks), Counter(row["apprentice_action"] for row in marks))

    source_unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in source_units}
    marks_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in marks:
        marks_by_unit[source_unit_lookup[(row["order_id"], row["stage"], row["unit"])]["master_unit_id"]].append(row)
    check("unit_mark_total", sum(len(rows) for rows in marks_by_unit.values()) == 437, sum(len(rows) for rows in marks_by_unit.values()))
    check("unit_literal_sequences_exact", all(row["literal_sequence_de"] == "; ".join(mark["concrete_default_de"] for mark in marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("condition_sequences_exact", all(
        row["speakable_condition_sequence_de"] == " -> ".join(mark["concrete_default_de"] for mark in marks_by_unit[row["master_unit_id"]])
        for row in units if row["section"] == "WHEN"
    ), "6/6")
    check("all_units_executable", Counter(row["execution_status"] for row in units) == Counter({"SHARED_OR_TAUGHT_EXECUTABLE": 112, "LOCAL_CONDITION_LEXICON_EXECUTABLE": 6}), Counter(row["execution_status"] for row in units))
    check("all_units_zero_model", all(int(row["model_marks"]) == 0 for row in units), "118/118")
    check("all_cards_complete", all(row["portable_grammar_complete"] == "YES" and row["all_units_readable"] == "YES" for row in cards), "6/6")

    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    observed_pages = {row["page"] for row in marks}
    check("fixed_page_allowlist", observed_pages <= allowed_pages, sorted(observed_pages))
    check("sealed_pages_absent_from_data", not any(page.lower().startswith("f84") for page in observed_pages), "0")
    external = re.compile(r"\b(?:SONNE|MOND|MARS|JUPITER|SATURN|VENUS|MERKUR|WIDDER|STIER|ZWILLINGE?|KREBS|LOEWE|JUNGFRAU|WAAGE|SKORPION|SCHUETZE|STEINBOCK|WASSERMANN|FISCHE)\b", re.I)
    check("no_external_names_in_condition_readings", not any(external.search(row["portable_workshop_reading_de"]) for row in conditions), "0")

    passed = all(item["passed"] for item in checks)
    result = {"status": "PASS" if passed else "FAIL", "checks": len(checks), "passed": sum(bool(item["passed"]) for item in checks), "failed": [item for item in checks if not item["passed"]], "details": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(json.dumps(result["failed"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
