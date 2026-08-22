#!/usr/bin/env python3
"""Build the independent V78 R3 continuous eleven-record edition.

This script does not decode surface strings.  It binds the already selected
V73/V74 occurrence expansions to exact opaque-card order and applies the
frozen V77 dictionary mechanically.  All content prose remains explicitly a
bracketed master-exemplar expansion.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

V77_DICT = ROOT / "experiments/yolo/sidequest_theory_candidates_v77/V77_SELECTED_CARD_DICTIONARY.tsv"
V77_OCC = ROOT / "experiments/yolo/sidequest_theory_candidates_v77/V77_SELECTED_197_OCCURRENCE_AUDIT.tsv"
V72_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v72/V72_SELECTED_116_STATEMENTS.tsv"
V73_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_100_EVENT_INTERLINEAR.tsv"
V73_ARTICLES = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_FIVE_ARTICLES.tsv"
V74_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_281_EVENT_INTERLINEAR.tsv"
V74_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_SIX_RECORD_EDITION.tsv"

EVENT_OUT = HERE / "V78_R3_381_EVENT_CONTINUITY.tsv"
STATEMENT_OUT = HERE / "V78_R3_116_STATEMENT_CONTINUITY.tsv"
RECORD_OUT = HERE / "V78_R3_11_RECORD_CONTINUITY.tsv"
CONFLICT_OUT = HERE / "V78_R3_CONFLICTS.tsv"
SUMMARY_OUT = HERE / "V78_R3_BUILD_SUMMARY.json"

ET_ID = "dcda95c81a5460feb191"
PER_ID = "b5fcea1eaed06b2f2291"
PARAMETER_ID = "2f1c5e56e8f0ff459065"
RELATION_ID = "308e8ea2d5d190c498e8"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


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


def punctuate(text: str) -> str:
    text = " ".join(text.strip().split())
    if not text:
        return "[KEINE EXEMPLAR-EXPANSION]."
    return text if text[-1] in ".!?" else text + "."


def short_card(card_id: str) -> str:
    return card_id


def classify_dictionary(row: dict[str, str] | None) -> tuple[str, str, str, str, str]:
    """Return status, phrase, source entry, attestation, V77 target flag."""
    if row is None:
        return (
            "EXEMPLAR_VALUE_UNKNOWN__NOT_V77_TARGET",
            "[EXEMPLARWERT_UNBEKANNT]",
            "NONE",
            "NONE",
            "NO",
        )
    decision = row["decision"]
    card_id = row["joint_tuple_id"]
    if decision == "CODEBOOK_ATTESTED_CATEGORY":
        if card_id == ET_ID:
            phrase = "ET?"
        elif card_id == PER_ID:
            phrase = "PER?"
        else:
            raise AssertionError(f"unexpected V78 portable word: {card_id}")
        return decision, phrase, row["exact_source_language_entry"], row["historical_attestation"], "YES"
    if decision == "FORMAL_LABEL_NOT_WORD":
        if card_id == PARAMETER_ID:
            phrase = "[FORMAL_PARAMETER_CHANNEL; KEIN_WORT]"
        elif card_id == RELATION_ID:
            phrase = "[FORMAL_RELATION_SLOT_CHANNEL; KEIN_WORT]"
        else:
            raise AssertionError(f"unexpected formal nonword: {card_id}")
        return decision, phrase, "NONE__NONWORD", "NOT_APPLICABLE__STRUCTURAL_EDITORIAL_LABEL", "YES"
    if decision == "EXEMPLAR_VALUE_UNKNOWN":
        return decision, "[EXEMPLARWERT_UNBEKANNT]", "NONE", row["historical_attestation"], "YES"
    raise AssertionError(f"unknown V77 decision: {decision}")


def record_rivals(record_id: str, source_row: dict[str, str]) -> tuple[str, str]:
    if record_id.startswith("H"):
        process = source_row["strongest_alternative_article"]
        notation = (
            "Bildgebundenes Pflanzenmaterial-Register: die opaque Karten setzen lokale Einträge, "
            "Links und exemplarabhängige Werte; Arzneizweck und Sachwörter werden nicht aus den Karten gelesen."
        )
    else:
        process = (
            "Badehaus-/Waschhaus-Betriebsregister: örtliche Stationen werden eingerichtet, bemessen, "
            "benutzt, gespült oder abgeschlossen, ohne therapeutische Patientensemantik."
        )
        notation = (
            "Formaler Stationsatlas beziehungsweise Bildlegende: Karten sind Eintrags-, Link-, "
            "Parameter- oder Commit-Stellen; Stoff und Richtung werden an jeder sichtbaren Lücke gelöscht."
        )
    return process, notation


def formal_rival(entry: int, terminal: int, total: int) -> str:
    medial = total - entry - terminal
    # A one-event field can be both entry and terminal; the aggregate counts are
    # deliberately reported separately, so choose on the strongest ratio only.
    ratios = {
        "FORMAL_ENTRY_OR_RESET_MARK": entry / total,
        "FORMAL_CLOSE_OR_COMMIT_MARK": terminal / total,
        "FORMAL_INTRA_FIELD_LINK_OR_SLOT_FILLER": max(0, medial) / total,
    }
    label, score = max(ratios.items(), key=lambda item: (item[1], item[0]))
    if score >= 0.60:
        return label
    return "FORMAL_POLYPOSITIONAL_ENTRY_LINK_OR_CLOSE_CARD"


def main() -> None:
    dictionary_rows = read_tsv(V77_DICT)
    dictionary = {row["joint_tuple_id"]: row for row in dictionary_rows}
    v77_occurrences = read_tsv(V77_OCC)
    statement_source_rows = read_tsv(V72_STATEMENTS)
    statement_source = {row["statement_id"]: row for row in statement_source_rows}
    herbal_rows = read_tsv(V73_EVENTS)
    bio_rows = read_tsv(V74_EVENTS)
    article_rows = {row["record_unit_id"]: row for row in read_tsv(V73_ARTICLES)}
    bio_record_rows = {row["record_unit_id"]: row for row in read_tsv(V74_RECORDS)}

    assert len(dictionary_rows) == 24
    assert Counter(row["decision"] for row in dictionary_rows) == {
        "EXEMPLAR_VALUE_UNKNOWN": 20,
        "FORMAL_LABEL_NOT_WORD": 2,
        "CODEBOOK_ATTESTED_CATEGORY": 2,
    }
    assert len(v77_occurrences) == 197
    assert len(statement_source_rows) == 116
    assert len(herbal_rows) == 100 and len(bio_rows) == 281

    raw_events: list[dict[str, str]] = []
    for row in herbal_rows:
        raw_events.append(
            {
                **row,
                "section": "HERBAL",
                "local_owner": row["whole_plant_owner"],
                "owner_status_v73_v74": row["owner_status"],
                "owner_break_before_raw": "RECORD_START__RESET_ALL_LOCAL_STATE"
                if int(row["event_serial"]) in {1, 15, 39, 56, 74}
                else "SAME_WHOLE_PLANT_OWNER",
                "source_support_class": row["v69_support_class"],
                "context_expansion": row["concrete_german_meaning_in_context"],
                "context_confidence": row["meaning_in_context_confidence"],
                "event_rival": row["strongest_alternative"],
                "contradiction": row["strongest_contradiction"],
            }
        )
    for row in bio_rows:
        raw_events.append(
            {
                **row,
                "section": "BIOLOGICAL",
                "local_owner": row["local_image_owner"],
                "owner_status_v73_v74": row["owner_status"],
                "owner_break_before_raw": row["owner_break_before"],
                "source_support_class": row["v69_source_status"],
                "context_expansion": row["concrete_german_meaning_in_context"],
                "context_confidence": row["meaning_in_context_confidence"],
                "event_rival": row["strongest_bathhouse_technical_or_formal_rival"],
                "contradiction": row["strongest_contradiction"],
            }
        )

    raw_events.sort(key=lambda row: int(row["event_serial"]))
    assert [int(row["event_serial"]) for row in raw_events] == list(range(1, 382))
    assert {row["page"] for row in raw_events} == ALLOWED_PAGES
    assert len({row["joint_tuple_id"] for row in raw_events}) == 173

    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in raw_events:
        by_record[row["record_unit_id"]].append(row)
        by_field[row["field_id"]].append(row)
        by_statement[row["statement_id"]].append(row)
        by_locus[(row["record_unit_id"], row["locus"])].append(row)

    assert list(by_record) == RECORD_ORDER
    assert len(by_field) == 135 and len(by_statement) == 116
    assert set(statement_source) == set(by_statement)

    record_pos: dict[int, tuple[int, int]] = {}
    field_pos: dict[int, tuple[int, int]] = {}
    statement_pos: dict[int, tuple[int, int]] = {}
    line_pos: dict[int, tuple[int, int]] = {}
    for grouping, target in (
        (by_record, record_pos),
        (by_field, field_pos),
        (by_statement, statement_pos),
        (by_locus, line_pos),
    ):
        for rows in grouping.values():
            rows.sort(key=lambda row: int(row["event_serial"]))
            for index, row in enumerate(rows, 1):
                target[int(row["event_serial"])] = (index, len(rows))

    # Verify that V72 sentence membership is exactly the occurrence membership.
    for statement_id, rows in by_statement.items():
        actual = pipe([row["event_serial"] for row in rows])
        assert statement_source[statement_id]["event_serials"] == actual, (statement_id, actual)

    event_rows: list[dict[str, object]] = []
    previous_by_record: dict[str, dict[str, str]] = {}
    for row in raw_events:
        serial = int(row["event_serial"])
        record_id = row["record_unit_id"]
        stmt_id = row["statement_id"]
        card_id = row["joint_tuple_id"]
        dstatus, event_phrase, source_entry, attestation, is_v77_target = classify_dictionary(dictionary.get(card_id))
        rpos, rlen = record_pos[serial]
        fpos, flen = field_pos[serial]
        spos, slen = statement_pos[serial]
        lpos, llen = line_pos[serial]

        layout_breaks: list[str] = []
        pressure: list[str] = []
        previous = previous_by_record.get(record_id)
        if previous is None:
            layout_breaks.append("RECORD_START")
        else:
            if previous["statement_id"] != stmt_id:
                layout_breaks.append("SENTENCE_BOUNDARY")
            if previous["field_id"] != row["field_id"]:
                layout_breaks.append("FIELD_BOUNDARY")
            if previous["locus"] != row["locus"]:
                layout_breaks.append("PHYSICAL_LINE_BOUNDARY")
        owner_break = row["owner_break_before_raw"]
        if owner_break == "BREAK_VISIBLE_GAP__RESET_SUBSTANCE_TARGET_DIRECTION":
            layout_breaks.append("VISIBLE_OWNER_RESET")
            if spos > 1:
                pressure.append("OWNER_RESET_INSIDE_SENTENCE")

        is_terminal = row["terminal_status"] == "TERMINAL"
        if card_id == ET_ID:
            if fpos == 1:
                pressure.append("ET_AT_FIELD_ENTRY")
            if spos == 1:
                pressure.append("ET_AT_SENTENCE_ENTRY")
            if lpos == 1:
                pressure.append("ET_AT_PHYSICAL_LINE_ENTRY")
            if is_terminal:
                pressure.append("ET_AT_FIELD_CLOSE")
        elif card_id == PER_ID:
            if fpos != 1:
                pressure.append("PER_NOT_AT_FIELD_ENTRY")
            if is_terminal:
                pressure.append("PER_AT_FIELD_CLOSE")

        if dstatus == "FORMAL_LABEL_NOT_WORD":
            pressure.append("FORMAL_NONWORD_REQUIRES_EXEMPLAR_EXPANSION")

        expansion = punctuate(row["context_expansion"])
        bracketed = f"[MASTER-EXEMPLAR; KEINE WORTBEDEUTUNG: {expansion}]"
        statement_fields = [part for part in statement_source[stmt_id]["constituent_fields"].split("|") if part]
        statement_loci = list(dict.fromkeys(item["locus"] for item in by_statement[stmt_id]))
        formal_position_rival = (
            "FORMAL_ENTRY_OR_RESET_MARK"
            if fpos == 1
            else "FORMAL_CLOSE_OR_COMMIT_MARK"
            if is_terminal
            else "FORMAL_INTRA_FIELD_LINK_OR_SLOT_FILLER"
        )
        event_rows.append(
            {
                "event_serial": str(serial),
                "record_unit_id": record_id,
                "section": row["section"],
                "page": row["page"],
                "locus": row["locus"],
                "field_id": row["field_id"],
                "statement_id": stmt_id,
                "event_index_in_record": str(rpos),
                "event_index_in_field": str(fpos),
                "event_index_in_statement": str(spos),
                "event_index_in_physical_line": str(lpos),
                "joint_tuple_id": card_id,
                "literal_exact_card_order": f"E{serial:03d}=[OPAQUE_EXACT_CARD:{short_card(card_id)}]",
                "dictionary_status": dstatus,
                "event_phrase": event_phrase,
                "exact_source_language_entry": source_entry,
                "historical_attestation": attestation,
                "v77_target": is_v77_target,
                "bracketed_exemplar_expansion": bracketed,
                "event_bound_working_reading": f"E{serial:03d}={event_phrase} {bracketed}",
                "statement_membership": (
                    f"{stmt_id}:E{int(by_statement[stmt_id][0]['event_serial']):03d}"
                    f"-E{int(by_statement[stmt_id][-1]['event_serial']):03d}"
                ),
                "statement_constituent_fields": pipe(statement_fields),
                "statement_physical_lines": pipe(statement_loci),
                "statement_crosses_field": "YES" if len(statement_fields) > 1 else "NO",
                "statement_crosses_physical_line": "YES" if len(statement_loci) > 1 else "NO",
                "local_owner": row["local_owner"],
                "owner_status_v73_v74": row["owner_status_v73_v74"],
                "owner_break_before": owner_break,
                "layout_break_before": pipe(layout_breaks),
                "terminal_status": row["terminal_status"],
                "formal_link_or_entry_rival": formal_position_rival,
                "local_grammar_pressure_flags": pipe(pressure),
                "source_support_class": row["source_support_class"],
                "context_confidence": row["context_confidence"],
                "process_or_content_rival": row["event_rival"],
                "strongest_contradiction": row["contradiction"],
                "semantic_ceiling": "WORKING_EXEMPLAR_EXPANSION_NOT_DECIPHERMENT_OR_PORTABLE_GLOSS",
            }
        )
        previous_by_record[record_id] = row

    # Cross-check the selected 197-row V77 occurrence packet exactly.
    selected_pairs = {(row["event_serial"], row["joint_tuple_id"]) for row in v77_occurrences}
    reconstructed_pairs = {
        (str(row["event_serial"]), str(row["joint_tuple_id"]))
        for row in event_rows
        if str(row["joint_tuple_id"]) in dictionary
    }
    assert selected_pairs == reconstructed_pairs

    event_fields = [
        "event_serial",
        "record_unit_id",
        "section",
        "page",
        "locus",
        "field_id",
        "statement_id",
        "event_index_in_record",
        "event_index_in_field",
        "event_index_in_statement",
        "event_index_in_physical_line",
        "joint_tuple_id",
        "literal_exact_card_order",
        "dictionary_status",
        "event_phrase",
        "exact_source_language_entry",
        "historical_attestation",
        "v77_target",
        "bracketed_exemplar_expansion",
        "event_bound_working_reading",
        "statement_membership",
        "statement_constituent_fields",
        "statement_physical_lines",
        "statement_crosses_field",
        "statement_crosses_physical_line",
        "local_owner",
        "owner_status_v73_v74",
        "owner_break_before",
        "layout_break_before",
        "terminal_status",
        "formal_link_or_entry_rival",
        "local_grammar_pressure_flags",
        "source_support_class",
        "context_confidence",
        "process_or_content_rival",
        "strongest_contradiction",
        "semantic_ceiling",
    ]
    write_tsv(EVENT_OUT, event_rows, event_fields)

    event_by_serial = {int(row["event_serial"]): row for row in event_rows}
    raw_by_serial = {int(row["event_serial"]): row for row in raw_events}
    statement_rows: list[dict[str, object]] = []
    statement_order_in_record: Counter[str] = Counter()
    for source in statement_source_rows:
        statement_id = source["statement_id"]
        record_id = source["record_unit_id"]
        statement_order_in_record[record_id] += 1
        serials = [int(part) for part in source["event_serials"].split("|")]
        events = [event_by_serial[serial] for serial in serials]
        fields = list(dict.fromkeys(str(event["field_id"]) for event in events))
        loci = list(dict.fromkeys(str(event["locus"]) for event in events))
        field_transitions = sum(a["field_id"] != b["field_id"] for a, b in zip(events, events[1:]))
        line_transitions = sum(a["locus"] != b["locus"] for a, b in zip(events, events[1:]))
        owner_resets = sum("VISIBLE_OWNER_RESET" in str(event["layout_break_before"]) for event in events)
        pressure_events = [
            str(event["event_serial"])
            for event in events
            if event["local_grammar_pressure_flags"] != "NONE"
        ]
        continuous = " ".join(
            punctuate(raw_by_serial[serial]["context_expansion"]) for serial in serials
        )
        event_aligned = " ".join(str(event["event_bound_working_reading"]) for event in events)
        literal = " > ".join(f"[{event['joint_tuple_id']}]" for event in events)
        phrase_layer = " > ".join(str(event["event_phrase"]) for event in events)
        statement_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": record_id,
                "section": str(events[0]["section"]),
                "page": source["page"],
                "sentence_index_in_record": str(statement_order_in_record[record_id]),
                "constituent_fields": pipe(fields),
                "physical_lines": pipe(loci),
                "event_serials": pipe([str(serial) for serial in serials]),
                "event_count": str(len(events)),
                "literal_exact_card_order": literal,
                "dictionary_phrase_order": phrase_layer,
                "event_aligned_bracketed_expansion": event_aligned,
                "continuous_sentence_text": continuous,
                "v72_owner_aware_source_paraphrase": source["selected_concrete_paraphrase"],
                "source_class": source["source_class"],
                "owner_transition": source["owner_transition"],
                "cross_field_transitions": str(field_transitions),
                "cross_physical_line_transitions": str(line_transitions),
                "visible_owner_resets": str(owner_resets),
                "local_grammar_pressure_event_serials": pipe(pressure_events),
                "local_grammar_pressure_count": str(len(pressure_events)),
                "line_crossing_v72": source["line_crossing"],
                "process_or_content_rival": source["strongest_rival"],
                "notation_rival": (
                    "Formaler Satz-/Eintragsrahmen: genaue Kartenfolge und sichtbare Grenzen bleiben erhalten; "
                    "die ausgeschriebene Sachhandlung stammt ausschließlich aus dem Masterexemplar."
                ),
                "repair_cost_0_4_v72": source["repair_cost_0_4"],
                "hardest_contradiction": source["hardest_contradiction"],
                "semantic_ceiling": "CONTINUOUS_SOURCE_CLASS_EXPANSION_NOT_PLAINTEXT",
            }
        )

    statement_fields = [
        "statement_id",
        "record_unit_id",
        "section",
        "page",
        "sentence_index_in_record",
        "constituent_fields",
        "physical_lines",
        "event_serials",
        "event_count",
        "literal_exact_card_order",
        "dictionary_phrase_order",
        "event_aligned_bracketed_expansion",
        "continuous_sentence_text",
        "v72_owner_aware_source_paraphrase",
        "source_class",
        "owner_transition",
        "cross_field_transitions",
        "cross_physical_line_transitions",
        "visible_owner_resets",
        "local_grammar_pressure_event_serials",
        "local_grammar_pressure_count",
        "line_crossing_v72",
        "process_or_content_rival",
        "notation_rival",
        "repair_cost_0_4_v72",
        "hardest_contradiction",
        "semantic_ceiling",
    ]
    write_tsv(STATEMENT_OUT, statement_rows, statement_fields)

    statements_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_record[str(row["record_unit_id"])].append(row)

    record_rows: list[dict[str, object]] = []
    for record_id in RECORD_ORDER:
        events = [event_by_serial[int(row["event_serial"])] for row in by_record[record_id]]
        statements = statements_by_record[record_id]
        fields = list(dict.fromkeys(str(event["field_id"]) for event in events))
        loci = list(dict.fromkeys(str(event["locus"]) for event in events))
        if record_id.startswith("H"):
            source = article_rows[record_id]
            fluent = source["fluent_article"]
            selected_complete = source["event_bound_continuous_text"]
            synopsis = source["historical_source_structure"]
            contradiction = source["strongest_contradiction"]
        else:
            source = bio_record_rows[record_id]
            fluent = source["continuous_event_bound_reading"]
            selected_complete = source["continuous_event_bound_reading"]
            synopsis = source["fluent_record_synopsis"]
            contradiction = source["strongest_contradiction"]
        process, notation = record_rivals(record_id, source)
        event_bound = " || ".join(
            f"{statement['statement_id']} {{{statement['event_aligned_bracketed_expansion']}}}"
            for statement in statements
        )
        literal = " > ".join(f"[{event['joint_tuple_id']}]" for event in events)
        phrase_layer = " > ".join(str(event["event_phrase"]) for event in events)
        field_transitions = sum(a["field_id"] != b["field_id"] for a, b in zip(events, events[1:]))
        line_transitions = sum(a["locus"] != b["locus"] for a, b in zip(events, events[1:]))
        owner_resets = sum("VISIBLE_OWNER_RESET" in str(event["layout_break_before"]) for event in events)
        pressure = [event for event in events if event["local_grammar_pressure_flags"] != "NONE"]
        record_rows.append(
            {
                "record_unit_id": record_id,
                "section": str(events[0]["section"]),
                "page": str(events[0]["page"]),
                "field_ids": pipe(fields),
                "statement_ids": pipe([str(row["statement_id"]) for row in statements]),
                "physical_lines": pipe(loci),
                "event_serials": pipe([str(event["event_serial"]) for event in events]),
                "event_count": str(len(events)),
                "field_count": str(len(fields)),
                "statement_count": str(len(statements)),
                "literal_exact_card_order": literal,
                "dictionary_phrase_order": phrase_layer,
                "complete_event_bound_record_text": event_bound,
                "selected_continuous_exemplar_text": selected_complete,
                "fluent_record_text": fluent,
                "record_synopsis_or_structure": synopsis,
                "cross_field_transitions": str(field_transitions),
                "cross_physical_line_transitions": str(line_transitions),
                "sentences_crossing_multiple_fields": str(
                    sum(int(row["cross_field_transitions"]) > 0 for row in statements)
                ),
                "sentences_crossing_multiple_lines": str(
                    sum(int(row["cross_physical_line_transitions"]) > 0 for row in statements)
                ),
                "visible_owner_resets": str(owner_resets),
                "local_grammar_pressure_events": str(len(pressure)),
                "local_grammar_pressure_serials": pipe([str(event["event_serial"]) for event in pressure]),
                "et_occurrences": str(sum(event["joint_tuple_id"] == ET_ID for event in events)),
                "per_occurrences": str(sum(event["joint_tuple_id"] == PER_ID for event in events)),
                "formal_nonword_occurrences": str(
                    sum(event["dictionary_status"] == "FORMAL_LABEL_NOT_WORD" for event in events)
                ),
                "unknown_or_unaudited_occurrences": str(
                    sum("EXEMPLAR_VALUE_UNKNOWN" in str(event["dictionary_status"]) for event in events)
                ),
                "process_rival": process,
                "notation_rival": notation,
                "strongest_contradiction": contradiction,
                "semantic_ceiling": "ELEVEN_RECORD_WORKING_EDITION_NOT_TRANSLATION_OR_DECIPHERMENT",
            }
        )

    record_fields = [
        "record_unit_id",
        "section",
        "page",
        "field_ids",
        "statement_ids",
        "physical_lines",
        "event_serials",
        "event_count",
        "field_count",
        "statement_count",
        "literal_exact_card_order",
        "dictionary_phrase_order",
        "complete_event_bound_record_text",
        "selected_continuous_exemplar_text",
        "fluent_record_text",
        "record_synopsis_or_structure",
        "cross_field_transitions",
        "cross_physical_line_transitions",
        "sentences_crossing_multiple_fields",
        "sentences_crossing_multiple_lines",
        "visible_owner_resets",
        "local_grammar_pressure_events",
        "local_grammar_pressure_serials",
        "et_occurrences",
        "per_occurrences",
        "formal_nonword_occurrences",
        "unknown_or_unaudited_occurrences",
        "process_rival",
        "notation_rival",
        "strongest_contradiction",
        "semantic_ceiling",
    ]
    write_tsv(RECORD_OUT, record_rows, record_fields)

    # One row for every one of the 173 exact cards, including all 149 cards not
    # selected for the bounded V77 dictionary audit.
    card_events: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in event_rows:
        card_events[str(event["joint_tuple_id"])].append(event)

    conflict_rows: list[dict[str, object]] = []
    for card_id in sorted(card_events):
        events = card_events[card_id]
        total = len(events)
        entry = sum(int(event["event_index_in_field"]) == 1 for event in events)
        terminal = sum(event["terminal_status"] == "TERMINAL" for event in events)
        line_entry = sum(int(event["event_index_in_physical_line"]) == 1 for event in events)
        statement_entry = sum(int(event["event_index_in_statement"]) == 1 for event in events)
        sections = sorted({str(event["section"]) for event in events})
        records = sorted({str(event["record_unit_id"]) for event in events}, key=RECORD_ORDER.index)
        pages = sorted({str(event["page"]) for event in events})
        expansions = sorted({str(event["bracketed_exemplar_expansion"]) for event in events})
        rival = formal_rival(entry, terminal, total)
        if rival == "FORMAL_ENTRY_OR_RESET_MARK":
            counter = [event for event in events if int(event["event_index_in_field"]) != 1]
        elif rival == "FORMAL_CLOSE_OR_COMMIT_MARK":
            counter = [event for event in events if event["terminal_status"] != "TERMINAL"]
        elif rival == "FORMAL_INTRA_FIELD_LINK_OR_SLOT_FILLER":
            counter = [
                event
                for event in events
                if int(event["event_index_in_field"]) == 1 or event["terminal_status"] == "TERMINAL"
            ]
        else:
            counter = events
        status, phrase, source_entry, attestation, is_target = classify_dictionary(dictionary.get(card_id))
        if card_id == ET_ID:
            pressure_summary = (
                f"ET?_PRESSURE: field_entry={entry}/{total}; statement_entry={statement_entry}/{total}; "
                f"terminal={terminal}/{total}; formal rival={rival}."
            )
        elif card_id == PER_ID:
            pressure_summary = (
                f"PER?_PRESSURE: field_entry={entry}/{total}; nonentry={total-entry}/{total}; "
                f"terminal={terminal}/{total}; formal rival={rival}."
            )
        elif status == "FORMAL_LABEL_NOT_WORD":
            pressure_summary = "NONWORD_BY_RULE; compare only the formal channel with the placement rival."
        else:
            pressure_summary = "NO_PORTABLE_READING_TO_CONFIRM; exemplar expansions remain occurrence-bound."
        conflict_rows.append(
            {
                "joint_tuple_id": card_id,
                "occurrences": str(total),
                "records": pipe(records),
                "pages": pipe(pages),
                "sections": pipe(sections),
                "v77_target": is_target,
                "dictionary_status": status,
                "dictionary_phrase": phrase,
                "exact_source_language_entry": source_entry,
                "historical_attestation": attestation,
                "field_entry_occurrences": str(entry),
                "field_entry_rate": f"{entry/total:.6f}",
                "field_terminal_occurrences": str(terminal),
                "field_terminal_rate": f"{terminal/total:.6f}",
                "physical_line_entry_occurrences": str(line_entry),
                "statement_entry_occurrences": str(statement_entry),
                "distinct_exemplar_expansions": str(len(expansions)),
                "whole_card_polyfunctionality_pressure": (
                    "HIGH" if len(expansions) >= 4 else "MEDIUM" if len(expansions) >= 2 else "LOW"
                ),
                "formal_link_or_entry_rival": rival,
                "portable_reading_comparison": pressure_summary,
                "strongest_counterexample_event_serials": pipe(
                    [str(event["event_serial"]) for event in counter[:8]]
                ),
                "cross_herbal_bio_status": "BOTH" if len(sections) == 2 else f"{sections[0]}_ONLY",
                "decision": (
                    "KEEP_ET_QUESTIONED"
                    if card_id == ET_ID
                    else "KEEP_PER_QUESTIONED"
                    if card_id == PER_ID
                    else "KEEP_FORMAL_NONWORD"
                    if status == "FORMAL_LABEL_NOT_WORD"
                    else "KEEP_UNKNOWN"
                ),
                "semantic_ceiling": "FORMAL_PLACEMENT_COMPARISON_NOT_WORD_POS_OR_MEANING",
            }
        )

    conflict_fields = [
        "joint_tuple_id",
        "occurrences",
        "records",
        "pages",
        "sections",
        "v77_target",
        "dictionary_status",
        "dictionary_phrase",
        "exact_source_language_entry",
        "historical_attestation",
        "field_entry_occurrences",
        "field_entry_rate",
        "field_terminal_occurrences",
        "field_terminal_rate",
        "physical_line_entry_occurrences",
        "statement_entry_occurrences",
        "distinct_exemplar_expansions",
        "whole_card_polyfunctionality_pressure",
        "formal_link_or_entry_rival",
        "portable_reading_comparison",
        "strongest_counterexample_event_serials",
        "cross_herbal_bio_status",
        "decision",
        "semantic_ceiling",
    ]
    write_tsv(CONFLICT_OUT, conflict_rows, conflict_fields)

    et_events = [event for event in event_rows if event["joint_tuple_id"] == ET_ID]
    per_events = [event for event in event_rows if event["joint_tuple_id"] == PER_ID]
    pressure_counter: Counter[str] = Counter()
    for event in event_rows:
        flags = str(event["local_grammar_pressure_flags"])
        if flags != "NONE":
            pressure_counter.update(flags.split("|"))
    summary = {
        "status": "BUILT",
        "role": "R3_TECHNICAL_REGISTER_NOTATION_SCRIBE",
        "scope": "FIXED_TEN_PAGE_PROSE_PACKET_ONLY",
        "counts": {
            "events": len(event_rows),
            "statements": len(statement_rows),
            "records": len(record_rows),
            "fields": len(by_field),
            "exact_cards": len(conflict_rows),
            "v77_targets": len(dictionary_rows),
            "v77_target_occurrences": len(v77_occurrences),
            "v77_unknown_targets": sum(row["decision"] == "EXEMPLAR_VALUE_UNKNOWN" for row in dictionary_rows),
            "formal_nonword_targets": sum(row["decision"] == "FORMAL_LABEL_NOT_WORD" for row in dictionary_rows),
            "portable_questioned_words": sum(row["decision"] == "CODEBOOK_ATTESTED_CATEGORY" for row in dictionary_rows),
        },
        "portable_word_checks": {
            "dcda_as_et": len(et_events),
            "dcda_non_et_phrases": sum(event["event_phrase"] != "ET?" for event in et_events),
            "b5fcea_as_per": len(per_events),
            "b5fcea_non_per_phrases": sum(event["event_phrase"] != "PER?" for event in per_events),
            "other_events_printing_et_or_per": sum(
                event["event_phrase"] in {"ET?", "PER?"}
                and event["joint_tuple_id"] not in {ET_ID, PER_ID}
                for event in event_rows
            ),
        },
        "continuity": {
            "statements_crossing_fields": sum(int(row["cross_field_transitions"]) > 0 for row in statement_rows),
            "statements_crossing_physical_lines": sum(
                int(row["cross_physical_line_transitions"]) > 0 for row in statement_rows
            ),
            "field_transitions_inside_statements": sum(int(row["cross_field_transitions"]) for row in statement_rows),
            "physical_line_transitions_inside_statements": sum(
                int(row["cross_physical_line_transitions"]) for row in statement_rows
            ),
            "visible_owner_resets": sum(int(row["visible_owner_resets"]) for row in statement_rows),
        },
        "grammar_pressure": dict(sorted(pressure_counter.items())),
        "input_sha256": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in [V77_DICT, V77_OCC, V72_STATEMENTS, V73_EVENTS, V73_ARTICLES, V74_EVENTS, V74_RECORDS]
        },
        "output_sha256": {
            path.name: sha256(path) for path in [EVENT_OUT, STATEMENT_OUT, RECORD_OUT, CONFLICT_OUT]
        },
        "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
        "interpretation_ceiling": "CREATIVE_CONTINUOUS_EXEMPLAR_EDITION_NOT_DECIPHERMENT",
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
