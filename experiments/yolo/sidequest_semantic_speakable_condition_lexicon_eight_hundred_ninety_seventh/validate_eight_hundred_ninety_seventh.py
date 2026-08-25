#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROSE = ROOT / "sidequest_semantic_prose_complete_workshop_edition_eight_hundred_ninety_sixth"
CONDITIONS = ROOT / "sidequest_semantic_concrete_condition_matching_eight_hundred_eighty_seventh"
PREFIX = "EIGHT_HUNDRED_NINETY_SEVENTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "observed": observed})

    source_vocab = read(PROSE / "EIGHT_HUNDRED_NINETY_SIXTH_231_COMPLETE_WORKSHOP_VOCABULARY.tsv")
    source_marks = read(PROSE / "EIGHT_HUNDRED_NINETY_SIXTH_437_COMPLETE_MARK_DECK.tsv")
    source_units = read(PROSE / "EIGHT_HUNDRED_NINETY_SIXTH_118_COMPLETE_UNIT_EXECUTION.tsv")
    source_groups = read(CONDITIONS / "EIGHT_HUNDRED_EIGHTY_SEVENTH_73_COMPLETE_CONDITION_GROUPS.tsv")
    vocabulary = read(HERE / f"{PREFIX}_231_COMPLETE_WORKSHOP_VOCABULARY.tsv")
    marks = read(HERE / f"{PREFIX}_437_ALL_SPEAKABLE_MARK_DECK.tsv")
    units = read(HERE / f"{PREFIX}_118_ALL_EXECUTABLE_UNITS.tsv")
    lexicon = read(HERE / f"{PREFIX}_73_SPEAKABLE_CONDITION_LEXICON.tsv")
    phrases = read(HERE / f"{PREFIX}_6_SPEAKABLE_CONDITION_PHRASES.tsv")
    cards = read(HERE / f"{PREFIX}_6_COMPLETE_JOB_CARDS.tsv")

    check("vocabulary_count", len(vocabulary) == 231, len(vocabulary))
    check("vocabulary_unique", len({row["identity"] for row in vocabulary}) == 231, len({row["identity"] for row in vocabulary}))
    check("mark_count", len(marks) == 437, len(marks))
    check("mark_ids_unique", len({row["order_mark_id"] for row in marks}) == 437, len({row["order_mark_id"] for row in marks}))
    check("unit_count", len(units) == 118, len(units))
    check("unit_ids_unique", len({row["master_unit_id"] for row in units}) == 118, len({row["master_unit_id"] for row in units}))
    check("condition_lexicon_count", len(lexicon) == 73, len(lexicon))
    check("condition_ids_unique", len({row["opaque_local_id"] for row in lexicon}) == 73, len({row["opaque_local_id"] for row in lexicon}))
    check("condition_phrase_count", len(phrases) == 6, len(phrases))
    check("job_card_count", len(cards) == 6, len(cards))

    source_group_by_id = {row["opaque_local_id"]: row for row in source_groups}
    source_mark_by_id = {row["order_mark_id"]: row for row in source_marks}
    source_vocab_by_id = {row["identity"]: row for row in source_vocab}
    lexicon_by_id = {row["opaque_local_id"]: row for row in lexicon}
    check("condition_id_set_exact", set(lexicon_by_id) == set(source_group_by_id), len(set(lexicon_by_id) ^ set(source_group_by_id)))
    check("condition_source_alignment", all(
        row["page"] == source_group_by_id[row["opaque_local_id"]]["page"]
        and row["locus"] == source_group_by_id[row["opaque_local_id"]]["locus"]
        and row["surface"] == source_group_by_id[row["opaque_local_id"]]["surface"]
        and row["component_parse"] == source_group_by_id[row["opaque_local_id"]]["component_parse"]
        for row in lexicon
    ), "73/73")

    condition_marks = [row for row in marks if row["master_section"] == "WHEN"]
    prose_marks = [row for row in marks if row["master_section"] != "WHEN"]
    check("condition_mark_count", len(condition_marks) == 73, len(condition_marks))
    check("prose_mark_count", len(prose_marks) == 364, len(prose_marks))
    check("condition_mark_id_set_exact", {row["source_id"] for row in condition_marks} == set(lexicon_by_id), len({row["source_id"] for row in condition_marks}))
    check("condition_marks_speakable", all(row["apprentice_action"] == "READ_LOCAL_CONDITION_WORD" for row in condition_marks), Counter(row["apprentice_action"] for row in condition_marks))
    check("condition_values_match_lexicon", all(row["concrete_default_de"] == lexicon_by_id[row["source_id"]]["speakable_condition_word_de"] for row in condition_marks), "73/73")
    check("no_copy_local_model", not any(row["apprentice_action"] == "COPY_LOCAL_MODEL" for row in marks), Counter(row["apprentice_action"] for row in marks))
    check("prose_marks_unchanged", all(
        row["concrete_default_de"] == source_mark_by_id[row["order_mark_id"]]["concrete_default_de"]
        and row["apprentice_action"] == source_mark_by_id[row["order_mark_id"]]["apprentice_action"]
        for row in prose_marks
    ), "364/364")

    condition_vocab = [row for row in vocabulary if row["sections"] == "WHEN"]
    prose_vocab = [row for row in vocabulary if row["sections"] != "WHEN"]
    check("condition_vocab_count", len(condition_vocab) == 73, len(condition_vocab))
    check("condition_vocab_values", all(row["short_value_de"] == lexicon_by_id[row["identity"]]["speakable_condition_word_de"] for row in condition_vocab), "73/73")
    check("prose_vocab_unchanged", all(
        row["short_value_de"] == source_vocab_by_id[row["identity"]]["short_value_de"]
        and row["apprentice_action"] == source_vocab_by_id[row["identity"]]["apprentice_action"]
        for row in prose_vocab
    ), "158/158")

    surface_values: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in lexicon:
        surface_values[(row["condition_handle"], row["surface"])].add(row["speakable_condition_word_de"])
    inconsistent = {f"{handle}:{surface}": sorted(values) for (handle, surface), values in surface_values.items() if len(values) > 1}
    check("same_surface_same_value_inside_handle", not inconsistent, inconsistent)
    check("short_values_nonempty", all(row["speakable_condition_word_de"].strip() for row in lexicon), "73/73")
    check("short_values_bounded", max(len(row["speakable_condition_word_de"].split()) for row in lexicon) <= 6, max(len(row["speakable_condition_word_de"].split()) for row in lexicon))
    generic = re.compile(r"BEDINGUNGSTEIL|KOPIEREN|LOCAL_MODEL|UNKNOWN|EXEMPLAR", re.I)
    check("no_generic_placeholder", not any(generic.search(row["speakable_condition_word_de"]) for row in lexicon), "0")
    celestial = re.compile(r"\b(?:SONNE|MOND|MARS|JUPITER|SATURN|VENUS|MERKUR|WIDDER|STIER|ZWILLINGE?|KREBS|LOEWE|JUNGFRAU|WAAGE|SKORPION|SCHUETZE|STEINBOCK|WASSERMANN|FISCHE|JANUAR|FEBRUAR|MAERZ|APRIL|MAI|JUNI|JULI|AUGUST|SEPTEMBER|OKTOBER|NOVEMBER|DEZEMBER)\b", re.I)
    check("no_external_celestial_names", not any(celestial.search(row["speakable_condition_word_de"]) for row in lexicon), "0")

    unit_by_id = {row["master_unit_id"]: row for row in units}
    marks_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    source_unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row["master_unit_id"] for row in source_units}
    for mark in marks:
        marks_by_unit[source_unit_lookup[(mark["order_id"], mark["stage"], mark["unit"])]].append(mark)
    check("unit_mark_total", sum(len(rows) for rows in marks_by_unit.values()) == 437, sum(len(rows) for rows in marks_by_unit.values()))
    check("all_units_zero_model_marks", all(int(row["model_marks"]) == 0 for row in units), Counter(row["model_marks"] for row in units))
    check("all_units_core_count_exact", all(int(row["core_marks"]) == len(marks_by_unit[row["master_unit_id"]]) for row in units), "118/118")
    check("unit_status_split", Counter(row["execution_status"] for row in units) == Counter({"SHARED_OR_TAUGHT_EXECUTABLE": 112, "LOCAL_CONDITION_LEXICON_EXECUTABLE": 6}), Counter(row["execution_status"] for row in units))
    check("condition_unit_sequence_exact", all(
        row["speakable_condition_sequence_de"] == " -> ".join(mark["concrete_default_de"] for mark in marks_by_unit[row["master_unit_id"]])
        for row in units if row["section"] == "WHEN"
    ), "6/6")
    check("condition_phrase_mark_total", sum(int(row["marks"]) for row in phrases) == 73, sum(int(row["marks"]) for row in phrases))
    check("condition_phrase_surfaces_exact", all(
        row["surface_sequence"] == " ".join(mark["surface"] for mark in marks_by_unit[row["master_unit_id"]])
        for row in phrases
    ), "6/6")
    check("condition_phrase_words_exact", all(
        row["speakable_sequence_de"] == unit_by_id[row["master_unit_id"]]["speakable_condition_sequence_de"]
        for row in phrases
    ), "6/6")
    check("all_job_cards_readable", all(row["all_units_readable"] == "YES" and row["condition_speakable"] == "YES" for row in cards), "6/6")

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
