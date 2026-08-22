#!/usr/bin/env python3
"""Build the deterministic V80 R3 canonical third edition.

Only centrally selected V69/V73--V79 artifacts are consumed.  Exact formal
structure and occurrence-bound master content remain separate throughout.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

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

DICT_OUT = HERE / "V80_R3_173_CARD_DICTIONARY.tsv"
EVENT_OUT = HERE / "V80_R3_381_EVENT_INTERLINEAR.tsv"
FIELD_OUT = HERE / "V80_R3_135_FIELD_EDITION.tsv"
STATEMENT_OUT = HERE / "V80_R3_116_STATEMENT_EDITION.tsv"
ASTRO_OUT = HERE / "V80_R3_395_ASTRO_GROUPS.tsv"
UNIFIED_OUT = HERE / "V80_R3_776_UNIFIED_LEDGER.tsv"
READABLE_OUT = HERE / "V80_R3_TEN_PAGE_READABLE_EDITION.md"
MANUAL_OUT = HERE / "V80_R3_EXECUTABLE_MANUAL.tsv"
CONTRADICTION_OUT = HERE / "V80_R3_CONTRADICTION_LEDGER.tsv"
SUMMARY_OUT = HERE / "V80_R3_BUILD_SUMMARY.json"

ET_ID = "dcda95c81a5460feb191"
PER_ID = "b5fcea1eaed06b2f2291"
PARAMETER_ID = "2f1c5e56e8f0ff459065"
RELATION_ID = "308e8ea2d5d190c498e8"
FORMAL_IDS = {ET_ID, PER_ID, PARAMETER_ID, RELATION_ID}
LEADING_MODEL = "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM"
RIVAL_MODEL = "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK"
PROSE_PAGES = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"]
ASTRO_PAGES = ["f67r2", "f68r1", "f69v"]
PAGE_ORDER = PROSE_PAGES + ASTRO_PAGES
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def pipe(values: list[str]) -> str:
    return "|".join(values) if values else "NONE"


def field_number(field_id: str) -> int:
    return int(field_id[1:])


def dictionary_values(card_id: str, v77: dict[str, str] | None) -> dict[str, str]:
    if card_id == ET_ID:
        assert v77 and v77["exact_source_language_entry"] == "et"
        return {
            "operational_value": "FORMAL_LINK_OR_SLOT",
            "operational_value_class": "DERIVED_FORMAL",
            "optional_questioned_master_gloss": "ET?",
            "optional_master_expansion": "UND/AUCH?",
            "optional_gloss_provenance": "MASTER_MEMORIZED_OPTIONAL_HISTORICAL_QUESTION_GLOSS",
            "historical_attestation": v77["historical_attestation"],
            "formal_nonword_channel": "NO",
            "exemplar_status": "FORMAL_OPERATION_WITH_OPTIONAL_MASTER_GLOSS",
        }
    if card_id == PER_ID:
        assert v77 and v77["exact_source_language_entry"] == "per"
        return {
            "operational_value": "FORMAL_RELATION_OR_ENTRY",
            "operational_value_class": "DERIVED_FORMAL",
            "optional_questioned_master_gloss": "PER?",
            "optional_master_expansion": "DURCH/GEMÄSS?",
            "optional_gloss_provenance": "MASTER_MEMORIZED_OPTIONAL_HISTORICAL_QUESTION_GLOSS",
            "historical_attestation": v77["historical_attestation"],
            "formal_nonword_channel": "NO",
            "exemplar_status": "FORMAL_OPERATION_WITH_OPTIONAL_MASTER_GLOSS",
        }
    if card_id == PARAMETER_ID:
        return {
            "operational_value": "FORMAL_PARAMETER_CHANNEL__NOT_A_WORD",
            "operational_value_class": "DERIVED_FORMAL",
            "optional_questioned_master_gloss": "NONE",
            "optional_master_expansion": "NONE",
            "optional_gloss_provenance": "NONE__FORMAL_NONWORD",
            "historical_attestation": "NOT_APPLICABLE__FORMAL_NONWORD",
            "formal_nonword_channel": "YES",
            "exemplar_status": "FORMAL_LABEL_NOT_WORD",
        }
    if card_id == RELATION_ID:
        return {
            "operational_value": "FORMAL_RELATION_SLOT_CHANNEL__NOT_A_WORD",
            "operational_value_class": "DERIVED_FORMAL",
            "optional_questioned_master_gloss": "NONE",
            "optional_master_expansion": "NONE",
            "optional_gloss_provenance": "NONE__FORMAL_NONWORD",
            "historical_attestation": "NOT_APPLICABLE__FORMAL_NONWORD",
            "formal_nonword_channel": "YES",
            "exemplar_status": "FORMAL_LABEL_NOT_WORD",
        }
    return {
        "operational_value": "OPAQUE_EXACT_CARD__EXEMPLAR_VALUE_UNKNOWN",
        "operational_value_class": "EXEMPLAR_VALUE_UNKNOWN",
        "optional_questioned_master_gloss": "NONE",
        "optional_master_expansion": "NONE",
        "optional_gloss_provenance": "NONE",
        "historical_attestation": "NONE",
        "formal_nonword_channel": "NO",
        "exemplar_status": "EXEMPLAR_VALUE_UNKNOWN",
    }


def main() -> None:
    v69_dictionary = read_tsv(V69_DICT)
    v69_events = read_tsv(V69_EVENTS)
    v69_astro = read_tsv(V69_ASTRO)
    v73_fields = read_tsv(V73_FIELDS)
    v74_fields = read_tsv(V74_FIELDS)
    v75_groups = read_tsv(V75_GROUPS)
    v75_loci = read_tsv(V75_LOCI)
    v75_namespaces = read_tsv(V75_NAMESPACES)
    v75_instruments = read_tsv(V75_INSTRUMENTS)
    purposes = read_tsv(V76_PURPOSES)
    v76_contradictions = read_tsv(V76_CONTRADICTIONS)
    v77_rows = read_tsv(V77_DICT)
    v78_events = read_tsv(V78_EVENTS)
    v78_statements = read_tsv(V78_STATEMENTS)
    v78_records = read_tsv(V78_RECORDS)
    v79_transitions = read_tsv(V79_TRANSITIONS)
    v79_manual = read_tsv(V79_MANUAL)
    v79_repairs = read_tsv(V79_REPAIRS)

    assert len(v69_dictionary) == 173 and len(v69_events) == 381 and len(v69_astro) == 395
    assert len(v73_fields) == 20 and len(v74_fields) == 115
    assert len(v75_groups) == 395 and len(v75_loci) == 142 and len(v75_namespaces) == 13
    assert len(v78_events) == 381 and len(v78_statements) == 116 and len(v78_records) == 11
    assert len(v79_transitions) == 19 and len(v79_manual) == 16 and len(v79_repairs) == 7
    assert {row["purpose_id"] for row in purposes} == {LEADING_MODEL, RIVAL_MODEL}
    purpose_by_id = {row["purpose_id"]: row for row in purposes}
    v77_by_card = {row["joint_tuple_id"]: row for row in v77_rows}

    # Canonical dictionary: operational formal value first, optional questioned
    # historical gloss second.  The two layers are never collapsed.
    occurrence_counts = Counter(row["joint_tuple_id"] for row in v78_events)
    dictionary_rows: list[dict[str, object]] = []
    dictionary_by_card: dict[str, dict[str, object]] = {}
    for source in sorted(v69_dictionary, key=lambda row: row["joint_tuple_id"]):
        card_id = source["joint_tuple_id"]
        values = dictionary_values(card_id, v77_by_card.get(card_id))
        source_positions = int(source["occurrences"]) - (1 if card_id == PER_ID else 0)
        row: dict[str, object] = {
            "joint_tuple_id": card_id,
            "surface_examples_display_only": source["surface_examples"],
            "visible_occurrences": source["occurrences"],
            "independent_source_positions": str(source_positions),
            "pages": source["pages"],
            "formal_formula_opaque": source["formal_formula_opaque"],
            **values,
            "v77_audit_status": v77_by_card[card_id]["decision"] if card_id in v77_by_card else "NOT_IN_BOUNDED_V77_TARGET_SET",
            "new_word_contribution": "0",
            "confirmed_word": "NO",
            "semantic_recovery_without_master": "NO",
            "canonical_ceiling": "OPERATIONAL_FORM_FIRST__OPTIONAL_MASTER_GLOSS_NOT_DECODED_WORD",
        }
        assert int(source["occurrences"]) == occurrence_counts[card_id]
        dictionary_rows.append(row)
        dictionary_by_card[card_id] = row

    dictionary_fields = [
        "joint_tuple_id", "surface_examples_display_only", "visible_occurrences", "independent_source_positions",
        "pages", "formal_formula_opaque", "operational_value", "operational_value_class",
        "optional_questioned_master_gloss", "optional_master_expansion", "optional_gloss_provenance",
        "historical_attestation", "formal_nonword_channel", "exemplar_status", "v77_audit_status",
        "new_word_contribution", "confirmed_word", "semantic_recovery_without_master", "canonical_ceiling",
    ]
    write_tsv(DICT_OUT, dictionary_rows, dictionary_fields)

    # Positive V79 read-once pair is selected by the generic audit result, not
    # by hard-coding its card identity.
    positive_transitions = [row for row in v79_transitions if row["rule_prediction"] == "ANTICIPATORY_MARGIN_COPY"]
    assert len(positive_transitions) == 1
    copy_left = positive_transitions[0]["line_final_event"]
    copy_right = positive_transitions[0]["line_initial_event"]
    assert positive_transitions[0]["classification"] == "TP"

    v69_event_by_serial = {row["event_serial"]: row for row in v69_events}
    source_position_index = 0
    event_rows: list[dict[str, object]] = []
    event_by_serial: dict[str, dict[str, object]] = {}
    for source in v78_events:
        serial = source["event_serial"]
        event_id = source["event_id"]
        old = v69_event_by_serial[serial]
        assert old["joint_tuple_id"] == source["joint_tuple_id"]
        card = dictionary_by_card[source["joint_tuple_id"]]
        is_copy = event_id == copy_left
        if not is_copy:
            source_position_index += 1
            source_position = f"S{source_position_index:03d}"
        else:
            source_position = f"COPY_OF:{copy_right}"
        read_action = (
            "ANTICIPATORY_EDGE_COPY__NO_SOURCE_EMIT"
            if event_id == copy_left
            else "MAIN_SOURCE_POSITION__READ_ONCE_WITH_PRECEDING_COPY"
            if event_id == copy_right
            else "READ_VISIBLE_EVENT_ONCE"
        )
        operational = str(card["operational_value"])
        autonomous = (
            f"VISIBLE_COPY_OF:{operational}"
            if is_copy
            else operational
        )
        row = {
            "event_serial": serial,
            "event_id": event_id,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "locus": source["locus"],
            "field_id": source["field_id"],
            "statement_id": source["statement_id"],
            "joint_tuple_id": source["joint_tuple_id"],
            "surface_display_only": old["surface_display_only"],
            "image_owner_id": source["image_owner_id"],
            "owner_break_before": source["owner_break_before"],
            "visible_read_action": read_action,
            "source_position_id": source_position,
            "source_position_contribution": "0" if is_copy else "1",
            "autonomous_operational_readback": autonomous,
            "operational_value_provenance": "DERIVED_FORMAL",
            "optional_questioned_master_gloss": card["optional_questioned_master_gloss"],
            "optional_gloss_provenance": card["optional_gloss_provenance"],
            "formal_nonword_channel": card["formal_nonword_channel"],
            "master_memorized_selected_token": source["selected_continuous_event_token"],
            "master_memorized_source_expansion_de": source["source_expansion_de"],
            "content_provenance": "MASTER_MEMORIZED",
            "leading_content_model": LEADING_MODEL,
            "rival_content_model": RIVAL_MODEL,
            "rival_occurrence_reading": source["strongest_source_rival"],
            "source_class": source["source_class"],
            "terminal_status": source["terminal_status"],
            "line_crossing": source["line_crossing"],
            "central_repair": source["central_repair"],
            "strongest_contradiction": source["strongest_contradiction"],
            "semantic_recovery_without_master": "NO",
            "new_word_contribution": "0",
            "canonical_ceiling": "FORMAL_OPERATION_AND_MASTER_CONTENT_SEPARATE__NOT_PLAINTEXT",
        }
        event_rows.append(row)
        event_by_serial[serial] = row
    assert source_position_index == 380

    event_fields = [
        "event_serial", "event_id", "record_unit_id", "page", "locus", "field_id", "statement_id",
        "joint_tuple_id", "surface_display_only", "image_owner_id", "owner_break_before",
        "visible_read_action", "source_position_id", "source_position_contribution",
        "autonomous_operational_readback", "operational_value_provenance",
        "optional_questioned_master_gloss", "optional_gloss_provenance", "formal_nonword_channel",
        "master_memorized_selected_token", "master_memorized_source_expansion_de", "content_provenance",
        "leading_content_model", "rival_content_model", "rival_occurrence_reading", "source_class",
        "terminal_status", "line_crossing", "central_repair", "strongest_contradiction",
        "semantic_recovery_without_master", "new_word_contribution", "canonical_ceiling",
    ]
    write_tsv(EVENT_OUT, event_rows, event_fields)

    # Fields inherit current V73/V74 occurrence-bound content, while their exact
    # formal sequences are rebuilt from canonical events.
    source_fields: dict[str, dict[str, str]] = {}
    for row in v73_fields:
        source_fields[row["field_id"]] = {
            "selected_content": row["third_edition_field_text"],
            "rival": row["strongest_alternative"],
            "contradiction": row["strongest_contradiction"],
            "owner": row["whole_plant_owner"],
            "parse_status": row["parse_status"],
        }
    for row in v74_fields:
        source_fields[row["field_id"]] = {
            "selected_content": row["balneological_field_text"],
            "rival": row["strongest_rival"],
            "contradiction": row["strongest_contradiction"],
            "owner": row["local_image_owner"],
            "parse_status": row["parse_status"],
        }
    events_by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_field[str(row["field_id"])].append(row)
    assert len(events_by_field) == 135 and len(source_fields) == 135

    field_rows: list[dict[str, object]] = []
    for field_id in sorted(events_by_field, key=field_number):
        rows = events_by_field[field_id]
        source = source_fields[field_id]
        resets = [str(row["event_id"]) for row in rows if row["owner_break_before"] == "BREAK_VISIBLE_GAP__RESET_SUBSTANCE_TARGET_DIRECTION"]
        field_rows.append({
            "field_id": field_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "locus": rows[0]["locus"],
            "statement_id": rows[0]["statement_id"],
            "visible_event_count": str(len(rows)),
            "independent_source_positions": str(sum(int(row["source_position_contribution"]) for row in rows)),
            "event_serials": pipe([str(row["event_serial"]) for row in rows]),
            "source_position_ids": pipe([str(row["source_position_id"]) for row in rows]),
            "exact_card_order": pipe([str(row["joint_tuple_id"]) for row in rows]),
            "operational_formal_order": pipe([str(row["autonomous_operational_readback"]) for row in rows]),
            "optional_master_gloss_order": pipe([str(row["optional_questioned_master_gloss"]) for row in rows]),
            "local_owner": source["owner"],
            "owner_reset_events": pipe(resets),
            "parse_status": source["parse_status"],
            "derived_formal_visible_atoms": str(len(rows)),
            "master_memorized_visible_expansions": str(len(rows)),
            "master_memorized_field_content": source["selected_content"],
            "leading_content_model": LEADING_MODEL,
            "rival_content_model": RIVAL_MODEL,
            "rival_field_content": source["rival"],
            "strongest_contradiction": source["contradiction"],
            "semantic_recovery_without_master": "0",
            "new_word_contribution": "0",
            "canonical_ceiling": "FIELD_FORM_DERIVED__CONTENT_MASTER_MEMORIZED__NOT_TRANSLATION",
        })
    field_fields = [
        "field_id", "record_unit_id", "page", "locus", "statement_id", "visible_event_count",
        "independent_source_positions", "event_serials", "source_position_ids", "exact_card_order",
        "operational_formal_order", "optional_master_gloss_order", "local_owner", "owner_reset_events",
        "parse_status", "derived_formal_visible_atoms", "master_memorized_visible_expansions",
        "master_memorized_field_content", "leading_content_model", "rival_content_model",
        "rival_field_content", "strongest_contradiction", "semantic_recovery_without_master",
        "new_word_contribution", "canonical_ceiling",
    ]
    write_tsv(FIELD_OUT, field_rows, field_fields)

    # Cross-line reset opportunities are fixed by the selected V79 audit.
    cross_line_reset_by_statement: dict[str, list[str]] = defaultdict(list)
    for transition in v79_transitions:
        if transition["same_visible_owner"] == "NO":
            cross_line_reset_by_statement[transition["statement_id"]].append(transition["line_initial_event"])
    assert sum(map(len, cross_line_reset_by_statement.values())) == 4

    statement_rows: list[dict[str, object]] = []
    for source in v78_statements:
        serials = source["event_serials"].split("|")
        rows = [event_by_serial[serial] for serial in serials]
        statement_rows.append({
            "statement_id": source["statement_id"],
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "sentence_index_in_record": source["sentence_index_in_record"],
            "constituent_fields": source["constituent_fields"],
            "physical_lines": source["physical_lines"],
            "visible_event_count": str(len(rows)),
            "independent_source_positions": str(sum(int(row["source_position_contribution"]) for row in rows)),
            "event_serials": source["event_serials"],
            "exact_card_order": pipe([str(row["joint_tuple_id"]) for row in rows]),
            "operational_formal_order": pipe([str(row["autonomous_operational_readback"]) for row in rows]),
            "optional_master_gloss_order": pipe([str(row["optional_questioned_master_gloss"]) for row in rows]),
            "cross_field_transitions": source["cross_field_transitions"],
            "cross_physical_line_transitions": source["cross_physical_line_transitions"],
            "cross_line_owner_reset_events": pipe(cross_line_reset_by_statement[source["statement_id"]]),
            "read_once_visible_pair": f"{copy_left}->{copy_right}" if copy_left[1:] in serials and copy_right[1:] in serials else "NONE",
            "derived_formal_visible_atoms": str(len(rows)),
            "master_memorized_visible_expansions": str(len(rows)),
            "master_memorized_statement_content": source["continuous_sentence_text"],
            "leading_content_model": LEADING_MODEL,
            "rival_content_model": RIVAL_MODEL,
            "rival_statement_content": source["process_or_content_rival"],
            "strongest_contradiction": source["hardest_contradiction"],
            "semantic_recovery_without_master": "0",
            "new_word_contribution": "0",
            "canonical_ceiling": "STATEMENT_FORM_DERIVED__CONTENT_MASTER_MEMORIZED__NOT_PLAINTEXT",
        })
    statement_fields = [
        "statement_id", "record_unit_id", "page", "sentence_index_in_record", "constituent_fields",
        "physical_lines", "visible_event_count", "independent_source_positions", "event_serials",
        "exact_card_order", "operational_formal_order", "optional_master_gloss_order",
        "cross_field_transitions", "cross_physical_line_transitions", "cross_line_owner_reset_events",
        "read_once_visible_pair", "derived_formal_visible_atoms", "master_memorized_visible_expansions",
        "master_memorized_statement_content", "leading_content_model", "rival_content_model",
        "rival_statement_content", "strongest_contradiction", "semantic_recovery_without_master",
        "new_word_contribution", "canonical_ceiling",
    ]
    write_tsv(STATEMENT_OUT, statement_rows, statement_fields)

    # Canonical Astro namespace map; every locus maps to exactly one of 13
    # selected local namespaces.
    namespace_by_page_locus: dict[tuple[str, str], str] = {}
    for namespace in v75_namespaces:
        for locus in namespace["source_loci"].split("|"):
            key = (namespace["page"], locus)
            assert key not in namespace_by_page_locus
            namespace_by_page_locus[key] = namespace["namespace_id"]
    v69_astro_by_serial = {row["group_serial"]: row for row in v69_astro}
    astro_rows: list[dict[str, object]] = []
    for source in v75_groups:
        old = v69_astro_by_serial[source["group_serial"]]
        assert old["opaque_local_id"] == source["opaque_local_id"]
        namespace_id = namespace_by_page_locus[(source["page"], source["locus"])]
        astro_rows.append({
            "group_serial": source["group_serial"],
            "diagram_id": source["diagram_id"],
            "page": source["page"],
            "locus": source["locus"],
            "event_index": source["event_index"],
            "opaque_local_id": source["opaque_local_id"],
            "surface_display_only": old["surface_display_only"],
            "canonical_namespace_id": namespace_id,
            "local_image_owner": source["local_image_owner"],
            "owner_status": source["owner_status"],
            "operational_formal_value": "LOCAL_NAMESPACE_ADDRESS_AND_SEGMENT_MEMBERSHIP",
            "operational_value_provenance": "DERIVED_FORMAL",
            "local_content_class": source["local_content_class"],
            "master_memorized_copied_label_segment": source["copied_local_meaning_or_label"],
            "content_provenance": "MASTER_MEMORIZED",
            "leading_content_model": LEADING_MODEL,
            "rival_content_model": RIVAL_MODEL,
            "rival_local_reading": source["strongest_astronomical_calendar_or_formal_rival"],
            "orientation_status": source["orientation_status"],
            "f68_f69_mapping": source["f68_f69_mapping"],
            "prose_card_import": source["prose_card_import"],
            "strongest_contradiction": source["strongest_contradiction"],
            "semantic_recovery_without_master": "NO",
            "new_word_contribution": "0",
            "canonical_ceiling": "LOCAL_ASTRO_FORM_DERIVED__LABEL_MASTER_MEMORIZED__NO_ORIENTATION_OR_MEANING",
        })
    astro_fields = [
        "group_serial", "diagram_id", "page", "locus", "event_index", "opaque_local_id",
        "surface_display_only", "canonical_namespace_id", "local_image_owner", "owner_status",
        "operational_formal_value", "operational_value_provenance", "local_content_class",
        "master_memorized_copied_label_segment", "content_provenance", "leading_content_model",
        "rival_content_model", "rival_local_reading", "orientation_status", "f68_f69_mapping",
        "prose_card_import", "strongest_contradiction", "semantic_recovery_without_master",
        "new_word_contribution", "canonical_ceiling",
    ]
    write_tsv(ASTRO_OUT, astro_rows, astro_fields)

    unified_rows: list[dict[str, object]] = []
    global_index = 0
    for event in event_rows:
        global_index += 1
        unified_rows.append({
            "global_index": str(global_index), "section": "PROSE", "page": event["page"],
            "unit_id": event["record_unit_id"], "locus": event["locus"],
            "opaque_identity": event["joint_tuple_id"], "surface_display_only": event["surface_display_only"],
            "formal_owner_or_namespace": event["image_owner_id"],
            "operational_formal_value": event["autonomous_operational_readback"],
            "formal_provenance": "DERIVED_FORMAL", "visible_read_action": event["visible_read_action"],
            "source_position_id": event["source_position_id"],
            "source_position_contribution": event["source_position_contribution"],
            "optional_questioned_master_gloss": event["optional_questioned_master_gloss"],
            "leading_master_memorized_content": event["master_memorized_source_expansion_de"],
            "rival_master_memorized_content": event["rival_occurrence_reading"],
            "content_provenance": "MASTER_MEMORIZED", "leading_content_model": LEADING_MODEL,
            "rival_content_model": RIVAL_MODEL, "semantic_recovery_without_master": "NO",
            "new_word_contribution": "0", "canonical_ceiling": event["canonical_ceiling"],
        })
    for group in astro_rows:
        global_index += 1
        unified_rows.append({
            "global_index": str(global_index), "section": "ASTRO", "page": group["page"],
            "unit_id": group["diagram_id"], "locus": group["locus"],
            "opaque_identity": group["opaque_local_id"], "surface_display_only": group["surface_display_only"],
            "formal_owner_or_namespace": group["canonical_namespace_id"],
            "operational_formal_value": group["operational_formal_value"],
            "formal_provenance": "DERIVED_FORMAL", "visible_read_action": "COPY_LOCAL_GROUP_ONCE",
            "source_position_id": f"ASTRO_G{int(group['group_serial']):03d}",
            "source_position_contribution": "1", "optional_questioned_master_gloss": "NONE",
            "leading_master_memorized_content": group["master_memorized_copied_label_segment"],
            "rival_master_memorized_content": group["rival_local_reading"],
            "content_provenance": "MASTER_MEMORIZED", "leading_content_model": LEADING_MODEL,
            "rival_content_model": RIVAL_MODEL, "semantic_recovery_without_master": "NO",
            "new_word_contribution": "0", "canonical_ceiling": group["canonical_ceiling"],
        })
    assert global_index == 776
    unified_fields = [
        "global_index", "section", "page", "unit_id", "locus", "opaque_identity",
        "surface_display_only", "formal_owner_or_namespace", "operational_formal_value",
        "formal_provenance", "visible_read_action", "source_position_id", "source_position_contribution",
        "optional_questioned_master_gloss", "leading_master_memorized_content",
        "rival_master_memorized_content", "content_provenance", "leading_content_model",
        "rival_content_model", "semantic_recovery_without_master", "new_word_contribution",
        "canonical_ceiling",
    ]
    write_tsv(UNIFIED_OUT, unified_rows, unified_fields)

    # Selected 16-rule apprentice machine plus six deterministic release rules.
    manual_rows: list[dict[str, object]] = []
    for source in v79_manual:
        manual_rows.append({
            "canonical_rule_order": source["rule_order"], "source_round": "V79_SELECTED",
            "state": source["state"], "visible_input": source["visible_input"],
            "condition": source["condition"], "operation": source["operation"],
            "state_update": source["state_update"], "forward_output": source["forward_output"],
            "backward_output": source["backward_output"], "failure_if_omitted": source["failure_if_omitted"],
            "content_rule": "FORM_FIRST__MASTER_CONTENT_OPTIONAL",
        })
    release_rules = [
        ("17", "CANONICAL_RELEASE", "EXACT_CARD", "joint_tuple_id", "always", "LOOKUP_OPERATIONAL_VALUE_FIRST", "return one of four formal operations or opaque unknown", "operational formal value", "same exact card", "optional ET?/PER? must never replace formal readback"),
        ("18", "CANONICAL_RELEASE", "PROSE_EVENTS", "field_id", "same frozen field", "ASSEMBLE_135_FIELDS", "preserve exact event order and E180 source contribution zero", "field form plus master content", "same events", "field prose may hide missing cards"),
        ("19", "CANONICAL_RELEASE", "PROSE_FIELDS", "statement_id", "same frozen statement", "ASSEMBLE_116_STATEMENTS", "allow 19 physical-line transitions and four owner resets", "statement form plus master content", "same fields", "physical line may be mistaken for sentence"),
        ("20", "CANONICAL_RELEASE", "PROSE_STATEMENTS", "record_unit_id", "same frozen record", "ASSEMBLE_11_RECORDS", "keep H1-H5 and B1-B6 separate", "continuous record lookup", "same statements", "B5/B6 or Bio owners may merge"),
        ("21", "CANONICAL_RELEASE", "ASTRO_GROUP", "page+locus", "exactly one selected local namespace", "ASSEMBLE_13_ASTRO_NAMESPACES", "forbid orientation, f68-f69 join and prose-card import", "local group and optional copied label", "same local group", "editorial address may become false cycle"),
        ("22", "CANONICAL_RELEASE", "ALL_FORMAL_ATOMS", "canonical counts", "381 prose + 395 Astro", "VERIFY_776_RELEASE", "verify 173/381/135/116/395/776 and zero new words", "PASS/FAIL", "same release", "completeness or layer separation may drift"),
    ]
    for order, source_round, state_name, visible, condition, operation, update, forward, backward, failure in release_rules:
        manual_rows.append({
            "canonical_rule_order": order, "source_round": source_round, "state": state_name,
            "visible_input": visible, "condition": condition, "operation": operation,
            "state_update": update, "forward_output": forward, "backward_output": backward,
            "failure_if_omitted": failure, "content_rule": "FORM_FIRST__MASTER_CONTENT_OPTIONAL",
        })
    manual_fields = [
        "canonical_rule_order", "source_round", "state", "visible_input", "condition", "operation",
        "state_update", "forward_output", "backward_output", "failure_if_omitted", "content_rule",
    ]
    write_tsv(MANUAL_OUT, manual_rows, manual_fields)

    contradiction_rows: list[dict[str, object]] = []
    for source in v76_contradictions:
        contradiction_rows.append({
            "canonical_contradiction_id": f"V76_{source['contradiction_id']}", "source_round": "V76_SELECTED",
            "model": source["model"], "affected_units": source["affected_units"],
            "issue_or_contradiction": source["contradiction"], "severity": source["severity"],
            "formal_decision": "UNCHANGED_FROM_V76", "semantic_decision": "NOT_DECODED",
            "containment_or_apprentice_rule": source["containment"], "status": source["status"],
            "canonical_ceiling": "CONTENT_MODEL_CONTRADICTION_NOT_DECIPHERMENT_SCORE",
        })
    for index, source in enumerate(v79_repairs, 1):
        contradiction_rows.append({
            "canonical_contradiction_id": f"V79_R{index:02d}", "source_round": "V79_SELECTED",
            "model": "SHARED_FORMAL_MACHINE", "affected_units": source["issue"],
            "issue_or_contradiction": source["failure_or_limit"], "severity": "NOT_SCORED",
            "formal_decision": source["formal_decision"], "semantic_decision": source["semantic_decision"],
            "containment_or_apprentice_rule": source["apprentice_rule"], "status": "RETAIN_LIMIT",
            "canonical_ceiling": "FORMAL_REPAIR_OR_LIMIT_NOT_NEW_SEMANTICS",
        })
    contradiction_fields = [
        "canonical_contradiction_id", "source_round", "model", "affected_units",
        "issue_or_contradiction", "severity", "formal_decision", "semantic_decision",
        "containment_or_apprentice_rule", "status", "canonical_ceiling",
    ]
    write_tsv(CONTRADICTION_OUT, contradiction_rows, contradiction_fields)

    # Ten-page readable artifact.  It is intentionally explicit that all fluent
    # text is a master lookup and not autonomous readback.
    records_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in v78_records:
        records_by_page[row["page"]].append(row)
    instrument_by_page = {row["page"]: row for row in v75_instruments}
    event_page_counts = Counter(str(row["page"]) for row in event_rows)
    astro_page_counts = Counter(str(row["page"]) for row in astro_rows)
    readable: list[str] = [
        "# V80 R3 — lesbare Zehnseiten-Ausgabe", "",
        "Status: vollständige kreative Masterexemplar-Ausgabe; keine Übersetzung oder Entzifferung.", "",
        f"Führendes eingefrorenes Inhaltsmodell: `{LEADING_MODEL}`.", "",
        f"Einziger Rivale: `{RIVAL_MODEL}`. Beide bleiben unentziffert und unbewiesen.", "",
        "Autonome Lektüre druckt ausschließlich formale Operationen oder opake Werte. Die folgenden flüssigen Inhalte sind `[MASTER_MEMORIZED]`.", "",
    ]
    for page in PAGE_ORDER:
        readable.extend([f"## {page}", ""])
        if page in PROSE_PAGES:
            readable.append(f"Formaler Bestand: {event_page_counts[page]} exakte sichtbare Karten.")
            readable.append("")
            for record in records_by_page[page]:
                readable.extend([
                    f"### {record['record_unit_id']}", "",
                    "`[MASTER_MEMORIZED; LEADING MODEL; NOT DECODED]`", "",
                    record["selected_continuous_german_working_reading"], "",
                    "`[MASTER_MEMORIZED RIVAL; NOT DECODED]`", "",
                    record["strongest_global_rival"], "",
                ])
        else:
            instrument = instrument_by_page[page]
            readable.extend([
                f"Formaler Bestand: {astro_page_counts[page]} opake Gruppen in lokalen Namespaces.", "",
                "`[MASTER_MEMORIZED; LEADING MODEL; NOT DECODED]`", "",
                instrument["continuous_instrument_description"], "",
                "`[MASTER_MEMORIZED RIVAL; NOT DECODED]`", "",
                instrument["strongest_competing_instrument"], "",
                f"Orientierung: `{instrument['orientation_status']}`; Crosspage-Mapping: `{instrument['crosspage_mapping']}`; Prosaimport: `{instrument['prose_card_import']}`.", "",
            ])
    readable.extend([
        "## Abschluss", "",
        "Alle 776 sichtbaren Gruppen besitzen eine exakte formale Zeile und eine occurrence-gebundene Masterausschreibung. Ohne Masterexemplar werden 0/776 konkrete Inhalte zurückgewonnen. Neue Wörter: 0.", "",
    ])
    READABLE_OUT.write_text("\n".join(readable), encoding="utf-8")

    dictionary_class_counts = Counter(str(row["operational_value_class"]) for row in dictionary_rows)
    operational_visible = sum(str(row["joint_tuple_id"]) in FORMAL_IDS for row in event_rows)
    operational_source = sum(
        str(row["joint_tuple_id"]) in FORMAL_IDS and row["source_position_contribution"] == "1"
        for row in event_rows
    )
    output_paths = [
        DICT_OUT, EVENT_OUT, FIELD_OUT, STATEMENT_OUT, ASTRO_OUT, UNIFIED_OUT,
        READABLE_OUT, MANUAL_OUT, CONTRADICTION_OUT,
    ]
    input_paths = [
        V69_DICT, V69_EVENTS, V69_ASTRO, V73_FIELDS, V74_FIELDS, V75_GROUPS, V75_LOCI,
        V75_NAMESPACES, V75_INSTRUMENTS, V76_PURPOSES, V76_CONTRADICTIONS, V77_DICT,
        V78_EVENTS, V78_STATEMENTS, V78_RECORDS, V79_TRANSITIONS, V79_MANUAL, V79_REPAIRS,
    ]
    summary = {
        "status": "BUILT",
        "role": "R3_TECHNICAL_REGISTER_NOTATION_SCRIBE",
        "counts": {
            "dictionary_types": len(dictionary_rows), "prose_visible_events": len(event_rows),
            "prose_independent_source_positions": source_position_index, "fields": len(field_rows),
            "statements": len(statement_rows), "records": len(v78_records), "Astro_groups": len(astro_rows),
            "Astro_loci": len(v75_loci), "Astro_namespaces": len(v75_namespaces),
            "unified_groups": len(unified_rows), "manual_rules": len(manual_rows),
            "contradictions": len(contradiction_rows), "pages": len(PAGE_ORDER),
        },
        "dictionary_layers": {
            "DERIVED_FORMAL_operational_types": dictionary_class_counts["DERIVED_FORMAL"],
            "EXEMPLAR_VALUE_UNKNOWN_types": dictionary_class_counts["EXEMPLAR_VALUE_UNKNOWN"],
            "formal_nonword_types": sum(row["formal_nonword_channel"] == "YES" for row in dictionary_rows),
            "optional_questioned_master_gloss_types": sum(row["optional_questioned_master_gloss"] != "NONE" for row in dictionary_rows),
            "new_words": 0,
        },
        "provenance_counts": {
            "prose_DERIVED_FORMAL_visible_atoms": len(event_rows),
            "prose_MASTER_MEMORIZED_visible_expansions": len(event_rows),
            "prose_selected_operational_formal_visible_occurrences": operational_visible,
            "prose_selected_operational_formal_source_positions": operational_source,
            "Astro_DERIVED_FORMAL_visible_atoms": len(astro_rows),
            "Astro_MASTER_MEMORIZED_visible_expansions": len(astro_rows),
            "unified_DERIVED_FORMAL_visible_atoms": len(unified_rows),
            "unified_MASTER_MEMORIZED_visible_expansions": len(unified_rows),
            "semantic_content_recovered_without_master": 0,
        },
        "read_once": {
            "rule": "same exact card at line end/start + same statement + same owner + no close => first visible copy, second read once",
            "opportunities": 19, "positives": 1, "pair": f"{copy_left}->{copy_right}",
            "visible_events": 2, "source_positions": 1,
        },
        "cross_line_owner_resets": sorted(
            [event for events_ in cross_line_reset_by_statement.values() for event in events_],
            key=lambda value: int(value[1:]),
        ),
        "content_models": {
            "leading_exactly_one": LEADING_MODEL,
            "rival_exactly_one": RIVAL_MODEL,
            "decoded_status": "NEITHER_DECODED_OR_SCORED_AS_TRUE",
        },
        "Astro_constraints": {
            "local_namespaces": 13, "selected_orientation": "NONE",
            "f68_f69_join": "FORBIDDEN", "prose_card_import": "FORBIDDEN",
        },
        "page_counts": {**dict(event_page_counts), **dict(astro_page_counts)},
        "input_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "output_sha256": {path.name: sha256(path) for path in output_paths},
        "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
        "canonical_ceiling": "COMPLETE_EXEMPLAR_DEPENDENT_FORMAL_EDITION__ZERO_CONFIRMED_WORDS_OR_PLAINTEXT",
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
