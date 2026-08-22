#!/usr/bin/env python3
"""Strict validator for the deterministic V80 R3 canonical third edition."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

DICT = HERE / "V80_R3_173_CARD_DICTIONARY.tsv"
EVENTS = HERE / "V80_R3_381_EVENT_INTERLINEAR.tsv"
FIELDS = HERE / "V80_R3_135_FIELD_EDITION.tsv"
STATEMENTS = HERE / "V80_R3_116_STATEMENT_EDITION.tsv"
ASTRO = HERE / "V80_R3_395_ASTRO_GROUPS.tsv"
UNIFIED = HERE / "V80_R3_776_UNIFIED_LEDGER.tsv"
READABLE = HERE / "V80_R3_TEN_PAGE_READABLE_EDITION.md"
MANUAL = HERE / "V80_R3_EXECUTABLE_MANUAL.tsv"
CONTRADICTIONS = HERE / "V80_R3_CONTRADICTION_LEDGER.tsv"
SUMMARY = HERE / "V80_R3_BUILD_SUMMARY.json"
REPORT = HERE / "V80_R3_CANONICAL_THIRD_EDITION_REPORT.md"
BUILDER = HERE / "build_v80_r3_canonical_third_edition.py"
VALIDATION = HERE / "V80_R3_VALIDATION.json"

V69_DICT = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
V69_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
V69_ASTRO = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_395_ASTRO_GROUPS.tsv"
V73_FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_20_FIELD_EDITION.tsv"
V74_FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_115_FIELD_EDITION.tsv"
V75_GROUPS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"
V75_LOCI = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
V75_NAMESPACES = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_NAMESPACE_REGISTRY.tsv"
V75_INSTRUMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_THREE_INSTRUMENTS.tsv"
V76_PURPOSES = ROOT / "experiments/yolo/sidequest_theory_candidates_v76/V76_SELECTED_BOOK_PURPOSE_COMPETITION.tsv"
V76_CONTRADICTIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v76/V76_SELECTED_CONTRADICTIONS.tsv"
V77_DICT = ROOT / "experiments/yolo/sidequest_theory_candidates_v77/V77_SELECTED_CARD_DICTIONARY.tsv"
V78_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_381_EVENT_INTERLINEAR.tsv"
V78_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_116_STATEMENTS.tsv"
V78_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_11_CONTINUOUS_RECORDS.tsv"
V79_TRANSITIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_19_LINE_TRANSITION_AUDIT.tsv"
V79_MANUAL = ROOT / "experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_MACHINE_MANUAL.tsv"
V79_REPAIRS = ROOT / "experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_REPAIR_DECISIONS.tsv"

ET_ID = "dcda95c81a5460feb191"
PER_ID = "b5fcea1eaed06b2f2291"
PARAMETER_ID = "2f1c5e56e8f0ff459065"
RELATION_ID = "308e8ea2d5d190c498e8"
FORMAL_IDS = {ET_ID, PER_ID, PARAMETER_ID, RELATION_ID}
LEADING = "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM"
RIVAL = "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK"
PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO_PAGES = {"f67r2", "f68r1", "f69v"}
ALL_PAGES = PROSE_PAGES | ASTRO_PAGES
RESET_EVENTS = {"E203", "E264", "E291", "E356"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_pipe(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


checks: list[str] = []
errors: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        checks.append(name)
    else:
        errors.append(f"{name}: {detail or 'condition failed'}")


def all_equal(rows: list[dict[str, str]], field: str, value: str) -> bool:
    return all(row[field] == value for row in rows)


def validate() -> dict[str, object]:
    required = [
        DICT, EVENTS, FIELDS, STATEMENTS, ASTRO, UNIFIED, READABLE, MANUAL,
        CONTRADICTIONS, SUMMARY, REPORT, BUILDER,
    ]
    for path in required:
        check(f"file_exists::{path.name}", path.is_file() and path.stat().st_size > 0)
    if errors:
        return result(False, {})

    dictionary = read_tsv(DICT)
    events = read_tsv(EVENTS)
    fields = read_tsv(FIELDS)
    statements = read_tsv(STATEMENTS)
    astro = read_tsv(ASTRO)
    unified = read_tsv(UNIFIED)
    manual = read_tsv(MANUAL)
    contradictions = read_tsv(CONTRADICTIONS)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    readable = READABLE.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")

    v69_dictionary = read_tsv(V69_DICT)
    v69_events = read_tsv(V69_EVENTS)
    v69_astro = read_tsv(V69_ASTRO)
    v73_fields = read_tsv(V73_FIELDS)
    v74_fields = read_tsv(V74_FIELDS)
    v75_groups = read_tsv(V75_GROUPS)
    v75_loci = read_tsv(V75_LOCI)
    v75_namespaces = read_tsv(V75_NAMESPACES)
    v75_instruments = read_tsv(V75_INSTRUMENTS)
    v76_purposes = read_tsv(V76_PURPOSES)
    v76_contradictions = read_tsv(V76_CONTRADICTIONS)
    v77_dictionary = read_tsv(V77_DICT)
    v78_events = read_tsv(V78_EVENTS)
    v78_statements = read_tsv(V78_STATEMENTS)
    v78_records = read_tsv(V78_RECORDS)
    v79_transitions = read_tsv(V79_TRANSITIONS)
    v79_manual = read_tsv(V79_MANUAL)
    v79_repairs = read_tsv(V79_REPAIRS)

    expected_counts = {
        "dictionary_types": 173, "prose_visible_events": 381,
        "prose_independent_source_positions": 380, "fields": 135,
        "statements": 116, "records": 11, "Astro_groups": 395,
        "Astro_loci": 142, "Astro_namespaces": 13, "unified_groups": 776,
        "manual_rules": 22, "contradictions": 23, "pages": 10,
    }
    actual_counts = {
        "dictionary_types": len(dictionary), "prose_visible_events": len(events),
        "prose_independent_source_positions": sum(int(row["source_position_contribution"]) for row in events),
        "fields": len(fields), "statements": len(statements), "records": len(v78_records),
        "Astro_groups": len(astro), "Astro_loci": len(v75_loci),
        "Astro_namespaces": len(v75_namespaces), "unified_groups": len(unified),
        "manual_rules": len(manual), "contradictions": len(contradictions),
        "pages": len({row["page"] for row in unified}),
    }
    check("canonical_counts", actual_counts == expected_counts, f"{actual_counts!r}")
    check("summary_counts", summary["counts"] == expected_counts, f"{summary['counts']!r}")
    check("fixed_page_set", {row["page"] for row in unified} == ALL_PAGES)

    # Dictionary identity, occurrence accounting and strict form/gloss layers.
    dict_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    source_dict_by_id = {row["joint_tuple_id"]: row for row in v69_dictionary}
    event_counts = Counter(row["joint_tuple_id"] for row in events)
    source_counts = Counter()
    for row in events:
        source_counts[row["joint_tuple_id"]] += int(row["source_position_contribution"])
    check("dictionary_unique_173", len(dict_by_id) == len(dictionary) == 173)
    check("dictionary_exact_source_ids", set(dict_by_id) == set(source_dict_by_id))
    check("dictionary_visible_counts_match_events", all(int(row["visible_occurrences"]) == event_counts[row["joint_tuple_id"]] for row in dictionary))
    check("dictionary_source_counts_match_events", all(int(row["independent_source_positions"]) == source_counts[row["joint_tuple_id"]] for row in dictionary))
    check("dictionary_surface_and_formula_copied", all(
        row["surface_examples_display_only"] == source_dict_by_id[row["joint_tuple_id"]]["surface_examples"]
        and row["formal_formula_opaque"] == source_dict_by_id[row["joint_tuple_id"]]["formal_formula_opaque"]
        for row in dictionary
    ))
    expected_operational = {
        ET_ID: "FORMAL_LINK_OR_SLOT",
        PER_ID: "FORMAL_RELATION_OR_ENTRY",
        PARAMETER_ID: "FORMAL_PARAMETER_CHANNEL__NOT_A_WORD",
        RELATION_ID: "FORMAL_RELATION_SLOT_CHANNEL__NOT_A_WORD",
    }
    check("four_exact_operational_values", all(dict_by_id[key]["operational_value"] == value for key, value in expected_operational.items()))
    check("four_derived_formal_types", {row["joint_tuple_id"] for row in dictionary if row["operational_value_class"] == "DERIVED_FORMAL"} == FORMAL_IDS)
    check("169_unknown_exemplar_types", sum(row["operational_value_class"] == "EXEMPLAR_VALUE_UNKNOWN" for row in dictionary) == 169)
    check("unknown_types_exact_value", all(
        row["operational_value"] == "OPAQUE_EXACT_CARD__EXEMPLAR_VALUE_UNKNOWN"
        for row in dictionary if row["joint_tuple_id"] not in FORMAL_IDS
    ))
    check("two_formal_nonword_channels", {row["joint_tuple_id"] for row in dictionary if row["formal_nonword_channel"] == "YES"} == {PARAMETER_ID, RELATION_ID})
    check("optional_gloss_only_et_per", {row["joint_tuple_id"] for row in dictionary if row["optional_questioned_master_gloss"] != "NONE"} == {ET_ID, PER_ID})
    check("et_optional_gloss_exact", dict_by_id[ET_ID]["optional_questioned_master_gloss"] == "ET?" and dict_by_id[ET_ID]["optional_master_expansion"] == "UND/AUCH?")
    check("per_optional_gloss_exact", dict_by_id[PER_ID]["optional_questioned_master_gloss"] == "PER?" and dict_by_id[PER_ID]["optional_master_expansion"] == "DURCH/GEMÄSS?")
    check("zero_dictionary_words", all_equal(dictionary, "new_word_contribution", "0") and all_equal(dictionary, "confirmed_word", "NO"))
    check("zero_dictionary_semantic_recovery", all_equal(dictionary, "semantic_recovery_without_master", "NO"))
    v77_by_id = {row["joint_tuple_id"]: row for row in v77_dictionary}
    check("et_per_attestation_copied", all(dict_by_id[key]["historical_attestation"] == v77_by_id[key]["historical_attestation"] for key in [ET_ID, PER_ID]))

    # Event identity and master/formal separation.
    source_event_by_serial = {row["event_serial"]: row for row in v78_events}
    v69_event_by_serial = {row["event_serial"]: row for row in v69_events}
    check("event_serials_1_381", [int(row["event_serial"]) for row in events] == list(range(1, 382)))
    check("event_ids_E001_E381", [row["event_id"] for row in events] == [f"E{index:03d}" for index in range(1, 382)])
    check("event_exact_ids_and_context_copied", all(
        row["joint_tuple_id"] == source_event_by_serial[row["event_serial"]]["joint_tuple_id"]
        and row["field_id"] == source_event_by_serial[row["event_serial"]]["field_id"]
        and row["statement_id"] == source_event_by_serial[row["event_serial"]]["statement_id"]
        and row["image_owner_id"] == source_event_by_serial[row["event_serial"]]["image_owner_id"]
        and row["surface_display_only"] == v69_event_by_serial[row["event_serial"]]["surface_display_only"]
        for row in events
    ))
    check("event_master_content_copied", all(
        row["master_memorized_selected_token"] == source_event_by_serial[row["event_serial"]]["selected_continuous_event_token"]
        and row["master_memorized_source_expansion_de"] == source_event_by_serial[row["event_serial"]]["source_expansion_de"]
        for row in events
    ))
    check("event_layers_strict", all_equal(events, "operational_value_provenance", "DERIVED_FORMAL") and all_equal(events, "content_provenance", "MASTER_MEMORIZED"))
    check("event_zero_semantics_and_words", all_equal(events, "semantic_recovery_without_master", "NO") and all_equal(events, "new_word_contribution", "0"))
    check("event_one_content_model_pair", all_equal(events, "leading_content_model", LEADING) and all_equal(events, "rival_content_model", RIVAL))
    check("54_formal_visible_occurrences", sum(row["joint_tuple_id"] in FORMAL_IDS for row in events) == 54)
    check("53_formal_source_positions", sum(row["joint_tuple_id"] in FORMAL_IDS and row["source_position_contribution"] == "1" for row in events) == 53)

    zero_sources = [row for row in events if row["source_position_contribution"] == "0"]
    check("one_zero_source_visible_copy", len(zero_sources) == 1 and zero_sources[0]["event_id"] == "E180")
    check("copy_points_to_E181", zero_sources[0]["source_position_id"] == "COPY_OF:E181" and zero_sources[0]["visible_read_action"] == "ANTICIPATORY_EDGE_COPY__NO_SOURCE_EMIT")
    event181 = next(row for row in events if row["event_id"] == "E181")
    check("E181_single_source_read", event181["source_position_contribution"] == "1" and event181["visible_read_action"] == "MAIN_SOURCE_POSITION__READ_ONCE_WITH_PRECEDING_COPY")
    source_ids = [row["source_position_id"] for row in events if row["source_position_contribution"] == "1"]
    check("source_ids_S001_S380", source_ids == [f"S{index:03d}" for index in range(1, 381)])

    # Fields and statements cover every event once and preserve selected content.
    field_event_serials = [serial for row in fields for serial in split_pipe(row["event_serials"])]
    statement_event_serials = [serial for row in statements for serial in split_pipe(row["event_serials"])]
    check("field_ids_F001_F135", [row["field_id"] for row in fields] == [f"F{index:03d}" for index in range(1, 136)])
    check("fields_cover_events_exactly_once", Counter(field_event_serials) == Counter(str(index) for index in range(1, 382)))
    check("statements_cover_events_exactly_once", Counter(statement_event_serials) == Counter(str(index) for index in range(1, 382)))
    check("field_counts_sum_381", sum(int(row["visible_event_count"]) for row in fields) == 381)
    check("field_source_positions_sum_380", sum(int(row["independent_source_positions"]) for row in fields) == 380)
    check("statement_counts_sum_381", sum(int(row["visible_event_count"]) for row in statements) == 381)
    check("statement_source_positions_sum_380", sum(int(row["independent_source_positions"]) for row in statements) == 380)
    check("fields_strict_layers", all_equal(fields, "semantic_recovery_without_master", "0") and all_equal(fields, "new_word_contribution", "0"))
    check("statements_strict_layers", all_equal(statements, "semantic_recovery_without_master", "0") and all_equal(statements, "new_word_contribution", "0"))
    check("fields_one_model_pair", all_equal(fields, "leading_content_model", LEADING) and all_equal(fields, "rival_content_model", RIVAL))
    check("statements_one_model_pair", all_equal(statements, "leading_content_model", LEADING) and all_equal(statements, "rival_content_model", RIVAL))

    source_fields = {row["field_id"]: row["third_edition_field_text"] for row in v73_fields}
    source_fields.update({row["field_id"]: row["balneological_field_text"] for row in v74_fields})
    check("135_selected_field_contents_copied", len(source_fields) == 135 and all(row["master_memorized_field_content"] == source_fields[row["field_id"]] for row in fields))
    source_statement_by_id = {row["statement_id"]: row for row in v78_statements}
    check("116_selected_statement_contents_copied", all(row["master_memorized_statement_content"] == source_statement_by_id[row["statement_id"]]["continuous_sentence_text"] for row in statements))

    transition_positives = [row for row in v79_transitions if row["rule_prediction"] == "ANTICIPATORY_MARGIN_COPY"]
    check("19_frozen_line_opportunities", len(v79_transitions) == 19 and sum(int(row["cross_physical_line_transitions"]) for row in statements) == 19)
    check("one_generic_copy_positive", len(transition_positives) == 1 and transition_positives[0]["line_final_event"] == "E180" and transition_positives[0]["line_initial_event"] == "E181")
    check("copy_rule_no_locus_exception", transition_positives[0]["locus_specific_exception"] == "NO")
    emitted_reset_events = {event for row in statements for event in split_pipe(row["cross_line_owner_reset_events"])}
    expected_reset_events = {row["line_initial_event"] for row in v79_transitions if row["same_visible_owner"] == "NO"}
    check("four_cross_line_owner_resets", emitted_reset_events == expected_reset_events == RESET_EVENTS)
    check("one_statement_contains_copy_pair", sum(row["read_once_visible_pair"] == "E180->E181" for row in statements) == 1)

    # Celestial local namespaces only.
    source_group_by_serial = {row["group_serial"]: row for row in v75_groups}
    v69_astro_by_serial = {row["group_serial"]: row for row in v69_astro}
    check("astro_serials_1_395", [int(row["group_serial"]) for row in astro] == list(range(1, 396)))
    check("astro_exact_group_identity_copied", all(
        row["opaque_local_id"] == source_group_by_serial[row["group_serial"]]["opaque_local_id"]
        and row["locus"] == source_group_by_serial[row["group_serial"]]["locus"]
        and row["surface_display_only"] == v69_astro_by_serial[row["group_serial"]]["surface_display_only"]
        for row in astro
    ))
    namespace_map: dict[tuple[str, str], str] = {}
    for namespace in v75_namespaces:
        for locus in namespace["source_loci"].split("|"):
            key = (namespace["page"], locus)
            check(f"namespace_unique_owner::{namespace['namespace_id']}::{locus}", key not in namespace_map)
            namespace_map[key] = namespace["namespace_id"]
    check("142_loci_map_to_13_namespaces", len(namespace_map) == 142 and len(set(namespace_map.values())) == 13)
    check("all_395_groups_use_exact_local_namespace", all(row["canonical_namespace_id"] == namespace_map[(row["page"], row["locus"])] for row in astro))
    check("astro_form_content_layers", all_equal(astro, "operational_value_provenance", "DERIVED_FORMAL") and all_equal(astro, "content_provenance", "MASTER_MEMORIZED"))
    check("astro_zero_semantics_and_words", all_equal(astro, "semantic_recovery_without_master", "NO") and all_equal(astro, "new_word_contribution", "0"))
    check("astro_no_selected_orientation", set(row["orientation_status"] for row in astro) == {"LOCAL_EDITORIAL_ADDRESS_ONLY__NO_AUTHORIAL_START_ROTATION_OR_DIRECTION"})
    check("astro_no_f68_f69_join", set(row["f68_f69_mapping"] for row in astro) == {"NONE__NO_VISIBLE_KEY"})
    check("astro_no_prose_import", set(row["prose_card_import"] for row in astro) == {"NONE"})
    check("astro_one_model_pair", all_equal(astro, "leading_content_model", LEADING) and all_equal(astro, "rival_content_model", RIVAL))
    f69_left_registry = next(row for row in v75_namespaces if row["namespace_id"] == "F69_LEFT_WHEEL_NS")
    check(
        "f69_28_slots_only_in_left_namespace",
        f69_left_registry["visible_kind"] == "LEFT_WHEEL_WITH_28_UNORDERED_SLOTS"
        and f69_left_registry["locus_count"] == "29"
        and "28 editorial source slots" in f69_left_registry["entry_rule"]
        and all("28" not in row["visible_kind"] for row in v75_namespaces if row["namespace_id"] != "F69_LEFT_WHEEL_NS"),
    )

    # Unified exact concatenation and provenance totals.
    check("unified_indices_1_776", [int(row["global_index"]) for row in unified] == list(range(1, 777)))
    check("unified_sections_381_395", Counter(row["section"] for row in unified) == Counter({"PROSE": 381, "ASTRO": 395}))
    check("unified_formal_provenance_776", all_equal(unified, "formal_provenance", "DERIVED_FORMAL"))
    check("unified_content_provenance_776", all_equal(unified, "content_provenance", "MASTER_MEMORIZED"))
    check("unified_zero_semantic_recovery", all_equal(unified, "semantic_recovery_without_master", "NO"))
    check("unified_zero_new_words", all_equal(unified, "new_word_contribution", "0"))
    check("unified_one_model_pair", all_equal(unified, "leading_content_model", LEADING) and all_equal(unified, "rival_content_model", RIVAL))
    check("unified_prose_identity_order", [row["opaque_identity"] for row in unified[:381]] == [row["joint_tuple_id"] for row in events])
    check("unified_astro_identity_order", [row["opaque_identity"] for row in unified[381:]] == [row["opaque_local_id"] for row in astro])

    # Manual and contradictions are selected V79/V76 material plus fixed release rules.
    manual_columns = ["state", "visible_input", "condition", "operation", "state_update", "forward_output", "backward_output", "failure_if_omitted"]
    check("first_16_manual_rules_exact", all(
        all(manual[index][column] == v79_manual[index][column] for column in manual_columns)
        and manual[index]["source_round"] == "V79_SELECTED"
        for index in range(16)
    ))
    check("six_canonical_release_rules", [row["canonical_rule_order"] for row in manual[16:]] == [str(index) for index in range(17, 23)] and all(row["source_round"] == "CANONICAL_RELEASE" for row in manual[16:]))
    check("manual_form_first", all_equal(manual, "content_rule", "FORM_FIRST__MASTER_CONTENT_OPTIONAL"))
    check("contradiction_sources_16_7", Counter(row["source_round"] for row in contradictions) == Counter({"V76_SELECTED": 16, "V79_SELECTED": 7}))
    check("v76_contradictions_exact", all(
        contradictions[index]["issue_or_contradiction"] == v76_contradictions[index]["contradiction"]
        and contradictions[index]["affected_units"] == v76_contradictions[index]["affected_units"]
        for index in range(16)
    ))
    check("v79_repairs_exact", all(
        contradictions[16 + index]["formal_decision"] == v79_repairs[index]["formal_decision"]
        and contradictions[16 + index]["semantic_decision"] == v79_repairs[index]["semantic_decision"]
        for index in range(7)
    ))

    # Readable edition and report contain the complete but explicitly nondecoded release.
    check("readable_all_ten_pages_once", all(readable.count(f"## {page}\n") == 1 for page in ALL_PAGES))
    check("readable_all_11_records_once", all(readable.count(f"### {record}\n") == 1 for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]))
    check("readable_three_instruments_included", all(row["continuous_instrument_description"] in readable for row in v75_instruments))
    check("readable_nontranslation_label", "keine Übersetzung oder Entzifferung" in readable and "MASTER_MEMORIZED" in readable)
    check("readable_zero_recovery_claim", "Ohne Masterexemplar werden 0/776 konkrete Inhalte zurückgewonnen. Neue Wörter: 0." in readable)
    check("report_complete_counts", all(token in report for token in ["173", "381", "135", "116", "395", "776", "380"] ))
    check("report_provenance_separation", "DERIVED_FORMAL" in report and "MASTER_MEMORIZED" in report and "Konkrete Inhalte ohne Master" in report)
    check("report_models_exact", LEADING in report and RIVAL in report)
    check("report_resets_exact", all(event in report for event in sorted(RESET_EVENTS)))
    check("report_seals", "`f84` und `f84r` blieben versiegelt" in report)
    check("report_zero_new_words", "Neu bestätigte Wörter" in report and "| 0 |" in report)

    # Purpose registry and summary contracts.
    check("purpose_source_exact_two", {row["purpose_id"] for row in v76_purposes} == {LEADING, RIVAL})
    check("summary_dictionary_layers", summary["dictionary_layers"] == {
        "DERIVED_FORMAL_operational_types": 4,
        "EXEMPLAR_VALUE_UNKNOWN_types": 169,
        "formal_nonword_types": 2,
        "optional_questioned_master_gloss_types": 2,
        "new_words": 0,
    })
    check("summary_provenance_counts", summary["provenance_counts"] == {
        "prose_DERIVED_FORMAL_visible_atoms": 381,
        "prose_MASTER_MEMORIZED_visible_expansions": 381,
        "prose_selected_operational_formal_visible_occurrences": 54,
        "prose_selected_operational_formal_source_positions": 53,
        "Astro_DERIVED_FORMAL_visible_atoms": 395,
        "Astro_MASTER_MEMORIZED_visible_expansions": 395,
        "unified_DERIVED_FORMAL_visible_atoms": 776,
        "unified_MASTER_MEMORIZED_visible_expansions": 776,
        "semantic_content_recovered_without_master": 0,
    })
    check("summary_copy_rule", summary["read_once"]["pair"] == "E180->E181" and summary["read_once"]["opportunities"] == 19 and summary["read_once"]["positives"] == 1)
    check("summary_resets", set(summary["cross_line_owner_resets"]) == RESET_EVENTS)
    check("summary_models", summary["content_models"] == {
        "leading_exactly_one": LEADING,
        "rival_exactly_one": RIVAL,
        "decoded_status": "NEITHER_DECODED_OR_SCORED_AS_TRUE",
    })
    check("summary_astro_constraints", summary["Astro_constraints"] == {
        "local_namespaces": 13, "selected_orientation": "NONE",
        "f68_f69_join": "FORBIDDEN", "prose_card_import": "FORBIDDEN",
    })
    check("summary_seals", summary["seals"] == {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"})
    check("summary_ceiling", summary["canonical_ceiling"] == "COMPLETE_EXEMPLAR_DEPENDENT_FORMAL_EDITION__ZERO_CONFIRMED_WORDS_OR_PLAINTEXT")

    # Hash provenance and byte-identical deterministic rebuild.
    source_paths = [
        V69_DICT, V69_EVENTS, V69_ASTRO, V73_FIELDS, V74_FIELDS, V75_GROUPS, V75_LOCI,
        V75_NAMESPACES, V75_INSTRUMENTS, V76_PURPOSES, V76_CONTRADICTIONS, V77_DICT,
        V78_EVENTS, V78_STATEMENTS, V78_RECORDS, V79_TRANSITIONS, V79_MANUAL, V79_REPAIRS,
    ]
    output_paths = [DICT, EVENTS, FIELDS, STATEMENTS, ASTRO, UNIFIED, READABLE, MANUAL, CONTRADICTIONS]
    check("input_hashes_current", summary["input_sha256"] == {str(path.relative_to(ROOT)): sha256(path) for path in source_paths})
    check("output_hashes_current", summary["output_sha256"] == {path.name: sha256(path) for path in output_paths})
    before = {path.name: sha256(path) for path in output_paths + [SUMMARY]}
    rebuild = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, text=True, capture_output=True)
    after = {path.name: sha256(path) for path in output_paths + [SUMMARY]}
    check("builder_rebuild_exit_zero", rebuild.returncode == 0, rebuild.stderr[-1000:])
    check("byte_identical_deterministic_rebuild", before == after, f"before={before!r}; after={after!r}")

    diagnostics = {
        "counts": actual_counts,
        "dictionary": {
            "derived_formal_types": 4,
            "unknown_exemplar_types": 169,
            "formal_nonword_types": 2,
            "optional_questioned_gloss_types": 2,
            "new_words": 0,
        },
        "provenance": {
            "DERIVED_FORMAL_visible_atoms": 776,
            "MASTER_MEMORIZED_visible_expansions": 776,
            "semantic_content_recovered_without_master": 0,
        },
        "read_once": {"opportunities": 19, "positives": 1, "pair": "E180->E181", "visible": 2, "source": 1},
        "cross_line_owner_resets": sorted(RESET_EVENTS),
        "Astro": {"loci": 142, "namespaces": 13, "orientation": "NONE", "f68_f69_join": "NONE", "prose_import": "NONE"},
        "content_models": {"leading": LEADING, "rival": RIVAL, "decoded": False},
        "deterministic_rebuild": before == after and rebuild.returncode == 0,
        "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
    }
    return result(not errors, diagnostics)


def result(passed: bool, diagnostics: dict[str, object]) -> dict[str, object]:
    return {
        "status": "PASS" if passed else "FAIL",
        "experiment": "V80_R3_DETERMINISTIC_CANONICAL_THIRD_EDITION",
        "checks_passed": len(checks),
        "checks_failed": len(errors),
        "passed_checks": checks,
        "errors": errors,
        "diagnostics": diagnostics,
        "canonical_ceiling": "COMPLETE_EXEMPLAR_DEPENDENT_FORMAL_EDITION__ZERO_CONFIRMED_WORDS_OR_PLAINTEXT",
    }


if __name__ == "__main__":
    validation = validate()
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    raise SystemExit(0 if validation["status"] == "PASS" else 1)
