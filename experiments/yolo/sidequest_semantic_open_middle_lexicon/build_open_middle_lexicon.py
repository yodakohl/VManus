#!/usr/bin/env python3
"""Build the creative lexicon architecture for the 292 nonterminal events."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_complete_terminal_deck"

DICT_IN = BASE / "SELECTED_173_COMPLETE_TERMINAL_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_COMPLETE_TERMINAL_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_COMPLETE_TERMINAL_SENTENCES.tsv"
TERMINAL_IN = BASE / "COMPLETE_TERMINAL_CARD_DECK.tsv"

DICT_OUT = HERE / "SELECTED_173_OPEN_MIDDLE_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_OPEN_MIDDLE_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_OPEN_MIDDLE_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_OPEN_MIDDLE_RECORDS.md"
MIDDLE_OUT = HERE / "OPEN_MIDDLE_136_CARD_LEXICON.tsv"
CORE_OUT = HERE / "OPEN_MIDDLE_CORE_16_DECK.tsv"
WHOLE_OUT = HERE / "RECURRENT_WHOLE_WORD_DECK.tsv"
SLOT_OUT = HERE / "OPEN_MIDDLE_SLOT_SUMMARY.tsv"
UNIFIED_OUT = HERE / "UNIFIED_173_CARD_ARCHITECTURE.tsv"
CHECK_OUT = HERE / "BUILD_CHECK.json"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}

PRODUCTIVE_BASE_SEGMENTATIONS = {
    "AIIN_TARGET_MEASURE",
    "OL_CONTINUE",
    "Y_CURRENT_ITEM_CARD",
    "AL_TO",
    "AR_FROM",
    "OR_BATCH",
    "HO_INGREDIENT",
    "AIN_PORTION",
    "IIN_TARGET_STAGE",
    "LSH_WASH",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def classify_middle(segmentation: str, occurrences: int) -> str:
    if segmentation in PRODUCTIVE_BASE_SEGMENTATIONS:
        return "PRODUCTIVE_BASE"
    if "+" in segmentation and "WHOLE" not in segmentation and "=" not in segmentation:
        return "PRODUCTIVE_COMPOSITION"
    if occurrences > 1:
        return "MEMORIZED_RECURRENT_CARD"
    return "LOCAL_EXEMPLAR_SINGLETON"


def teaching_rule(status: str) -> str:
    return {
        "PRODUCTIVE_BASE": "Grundbauteil direkt lesen und in den passenden Slot setzen.",
        "PRODUCTIVE_COMPOSITION": "Die bereits lizenzierten Bauteile der exakten Karte zusammensetzen.",
        "MEMORIZED_RECURRENT_CARD": "Die ganze exakte Karte als wiederkehrendes Fachwort lernen.",
        "LOCAL_EXEMPLAR_SINGLETON": "Die lokale Einzelkarte mit ihrem konkreten Exemplarwert kopieren.",
    }[status]


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentences = read_tsv(SENTENCE_IN)
    terminal_deck = read_tsv(TERMINAL_IN)
    if (len(dictionary), len(events), len(sentences), len(terminal_deck)) != (173, 381, 116, 37):
        raise AssertionError("unexpected input dimensions")

    dmap = {row["joint_tuple_id"]: row for row in dictionary}
    terminal_map = {row["terminal_card_id"]: row for row in terminal_deck}
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_card[row["joint_tuple_id"]].append(row)
    middle_events = [row for row in events if row["step_closure_role"] != "COMMIT_CELL"]
    middle_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in middle_events:
        middle_by_card[row["joint_tuple_id"]].append(row)
    if set(middle_by_card) & set(terminal_map):
        raise AssertionError("terminal and open-middle exact-card inventories must be disjoint")

    middle_rows: list[dict[str, str]] = []
    for card_id, card_events in sorted(middle_by_card.items(), key=lambda item: (-len(item[1]), item[0])):
        source = dmap[card_id]
        count = len(card_events)
        slots = Counter(slot for event in card_events for slot in event["workshop_slots"].split("+") if slot)
        max_slot = max(slots.values())
        dominant = [slot for slot, value in slots.items() if value == max_slot]
        status = classify_middle(source["semantic_segmentation"], count)
        tier = "CORE_16" if count >= 4 else ("SECONDARY_RECURRENT" if count >= 2 else "LOCAL_SINGLETON")
        middle_rows.append({
            "joint_tuple_id": card_id,
            "surface_family": source["surface_family"],
            "occurrence_count": str(count),
            "event_ids": "|".join(event["event_id"] for event in card_events),
            "statement_ids": "|".join(unique([event["statement_id"] for event in card_events])),
            "records": "|".join(unique([event["record_unit_id"] for event in card_events])),
            "pages": "|".join(unique([event["page"] for event in card_events])),
            "slot_memberships": "|".join(f"{slot}:{value}" for slot, value in slots.most_common()),
            "dominant_slots": "|".join(dominant),
            "semantic_segmentation": source["semantic_segmentation"],
            "concrete_reading_de": source["concrete_word_reading_de"],
            "middle_lexicon_status": status,
            "frequency_tier": tier,
            "apprentice_rule_de": teaching_rule(status),
        })
    middle_map = {row["joint_tuple_id"]: row for row in middle_rows}
    core_rows = [dict(row) for row in middle_rows if row["frequency_tier"] == "CORE_16"]
    running = 0
    for rank, row in enumerate(core_rows, 1):
        running += int(row["occurrence_count"])
        row["core_rank"] = str(rank)
        row["cumulative_events"] = str(running)
        row["cumulative_middle_coverage"] = f"{running / len(middle_events):.6f}"
    core_rows = [
        {"core_rank": row.pop("core_rank"), **row, "cumulative_events": row.pop("cumulative_events"), "cumulative_middle_coverage": row.pop("cumulative_middle_coverage")}
        for row in core_rows
    ]
    recurrent_whole_rows = [dict(row) for row in middle_rows if row["middle_lexicon_status"] == "MEMORIZED_RECURRENT_CARD"]

    slot_rows: list[dict[str, str]] = []
    all_slots = sorted({slot for event in middle_events for slot in event["workshop_slots"].split("+") if slot})
    core_ids = {row["joint_tuple_id"] for row in core_rows}
    for slot in all_slots:
        slot_events = [event for event in middle_events if slot in event["workshop_slots"].split("+")]
        counts = Counter(event["joint_tuple_id"] for event in slot_events)
        top = counts.most_common(8)
        slot_rows.append({
            "slot": slot,
            "event_memberships": str(len(slot_events)),
            "distinct_card_types": str(len(counts)),
            "core_16_event_memberships": str(sum(1 for event in slot_events if event["joint_tuple_id"] in core_ids)),
            "top_cards_de": "|".join(f"{dmap[card_id]['concrete_word_reading_de']}:{count}" for card_id, count in top),
            "apprentice_question_de": {
                "OWNER_ITEM": "Welcher aktuelle Posten ist gemeint?",
                "SOURCE": "Woher kommt er?",
                "PREPARATION": "Welcher Ansatz oder Zustand liegt vor?",
                "QUANTITY": "Welche Portion, welches Maß oder welche Stufe?",
                "TARGET": "Wohin oder an welche Stelle?",
                "ORDER": "Weiter, danach oder vom Vorposten?",
                "MEDIUM": "Welches Arbeitsmedium?",
                "FLOW_TRANSFER": "Welcher lokale Lauf oder Übergang?",
                "OPERATION": "Welche Handlung wird vorbereitet?",
                "STATE_GRADE": "Welcher Zustand oder Grad?",
            }[slot],
        })

    unified_rows: list[dict[str, str]] = []
    for source in dictionary:
        card_id = source["joint_tuple_id"]
        occurrences = len(by_card[card_id])
        if card_id in terminal_map:
            terminal = terminal_map[card_id]
            if terminal["composition_status"] == "PRODUCTIVE_COMPOSITION":
                architecture = "PRODUCTIVE_COMPONENT_OR_COMPOSITION"
            elif terminal["composition_status"] == "LICENSED_PARTIAL":
                architecture = "LICENSED_PARTIAL_COMPOSITION"
            else:
                architecture = "TERMINAL_SPECIALIST_WHOLE_CARD"
            layer = "TERMINAL"
            inner_status = terminal["composition_status"]
            rule = (
                "Komponenten lesen und ganze exakte Karte als Schluss ausführen."
                if architecture == "PRODUCTIVE_COMPONENT_OR_COMPOSITION"
                else "Gelernte terminale Karte oder Teilkomposition als Ganzes ausführen."
            )
        else:
            middle = middle_map[card_id]
            architecture = (
                "PRODUCTIVE_COMPONENT_OR_COMPOSITION"
                if middle["middle_lexicon_status"] in {"PRODUCTIVE_BASE", "PRODUCTIVE_COMPOSITION"}
                else middle["middle_lexicon_status"]
            )
            layer = "OPEN_MIDDLE"
            inner_status = middle["middle_lexicon_status"]
            rule = middle["apprentice_rule_de"]
        unified_rows.append({
            "joint_tuple_id": card_id,
            "surface_family": source["surface_family"],
            "occurrence_count": str(occurrences),
            "layer": layer,
            "architecture_status": architecture,
            "inner_status": inner_status,
            "semantic_segmentation": source["semantic_segmentation"],
            "concrete_reading_de": source["concrete_word_reading_de"],
            "apprentice_rule_de": rule,
        })

    out_dictionary: list[dict[str, str]] = []
    unified_map = {row["joint_tuple_id"]: row for row in unified_rows}
    for original in dictionary:
        row = dict(original)
        middle = middle_map.get(row["joint_tuple_id"])
        unified = unified_map[row["joint_tuple_id"]]
        row["open_middle_status"] = middle["middle_lexicon_status"] if middle else "TERMINAL_CARD"
        row["open_middle_frequency_tier"] = middle["frequency_tier"] if middle else "NOT_APPLICABLE"
        row["unified_lexicon_architecture"] = unified["architecture_status"]
        row["unified_apprentice_rule_de"] = unified["apprentice_rule_de"]
        out_dictionary.append(row)

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        middle = middle_map.get(row["joint_tuple_id"])
        unified = unified_map[row["joint_tuple_id"]]
        row["open_middle_status"] = middle["middle_lexicon_status"] if middle else "TERMINAL_CARD"
        row["open_middle_frequency_tier"] = middle["frequency_tier"] if middle else "NOT_APPLICABLE"
        row["unified_lexicon_architecture"] = unified["architecture_status"]
        row["open_middle_layer_role"] = "OPEN_ARGUMENT_OR_ACTION" if middle else "TERMINAL_PROGRAM"
        out_events.append(row)

    out_sentences: list[dict[str, str]] = []
    event_out_map = {row["event_id"]: row for row in out_events}
    for original in sentences:
        row = dict(original)
        statement_events = [event_out_map[event_id] for event_id in row["event_ids"].split("|")]
        open_events = [event for event in statement_events if event["open_middle_layer_role"] == "OPEN_ARGUMENT_OR_ACTION"]
        statuses = Counter(event["open_middle_status"] for event in open_events)
        row["open_middle_event_count"] = str(len(open_events))
        row["open_middle_productive_events"] = str(statuses["PRODUCTIVE_BASE"] + statuses["PRODUCTIVE_COMPOSITION"])
        row["open_middle_recurrent_whole_events"] = str(statuses["MEMORIZED_RECURRENT_CARD"])
        row["open_middle_singleton_events"] = str(statuses["LOCAL_EXEMPLAR_SINGLETON"])
        row["open_middle_core16_events"] = str(sum(event["joint_tuple_id"] in core_ids for event in open_events))
        row["open_middle_reading_de"] = " · ".join(event["concrete_word_reading_de"] for event in open_events) or "KEINE OFFENE MITTE"
        out_sentences.append(row)

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(MIDDLE_OUT, middle_rows)
    write_tsv(CORE_OUT, core_rows)
    write_tsv(WHOLE_OUT, recurrent_whole_rows)
    write_tsv(SLOT_OUT, slot_rows)
    write_tsv(UNIFIED_OUT, unified_rows)

    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        by_record[row["record_unit_id"]].append(row)
    lines = [
        "# Elf Records mit offener Mittellexik",
        "",
        "Jede Anweisung zeigt die offene Kartenfolge vor ihrem terminalen Programm und deren Lernaufwand.",
        "",
    ]
    for record in RECORD_ORDER:
        rows_here = by_record[record]
        lines.extend([f"## {record} — {rows_here[0]['page']}", ""])
        for row in rows_here:
            lines.append(
                f"- **{row['statement_id']}** — {row['workshop_sentence_de']} "
                f"*[Mitte: {row['open_middle_productive_events']} produktiv, "
                f"{row['open_middle_recurrent_whole_events']} gelernt-wiederkehrend, "
                f"{row['open_middle_singleton_events']} lokal; {row['open_middle_reading_de']}]*"
            )
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    middle_status = Counter(row["middle_lexicon_status"] for row in middle_rows)
    middle_event_status = Counter()
    for row in middle_rows:
        middle_event_status[row["middle_lexicon_status"]] += int(row["occurrence_count"])
    unified_type_status = Counter(row["architecture_status"] for row in unified_rows)
    unified_event_status = Counter()
    for row in unified_rows:
        unified_event_status[row["architecture_status"]] += int(row["occurrence_count"])
    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(by_record) == set(RECORD_ORDER),
        "middle_events_292": len(middle_events) == 292,
        "middle_types_136": len(middle_rows) == 136,
        "core_types_16": len(core_rows) == 16,
        "core_events_148": sum(int(row["occurrence_count"]) for row in core_rows) == 148,
        "core_productive_15_whole_1": Counter(row["middle_lexicon_status"] for row in core_rows) == Counter({"PRODUCTIVE_BASE": 7, "PRODUCTIVE_COMPOSITION": 8, "MEMORIZED_RECURRENT_CARD": 1}),
        "middle_status_10_66_5_55": middle_status == Counter({"PRODUCTIVE_BASE": 10, "PRODUCTIVE_COMPOSITION": 66, "MEMORIZED_RECURRENT_CARD": 5, "LOCAL_EXEMPLAR_SINGLETON": 55}),
        "middle_event_status_89_136_12_55": middle_event_status == Counter({"PRODUCTIVE_BASE": 89, "PRODUCTIVE_COMPOSITION": 136, "MEMORIZED_RECURRENT_CARD": 12, "LOCAL_EXEMPLAR_SINGLETON": 55}),
        "recurrent_whole_types_5": len(recurrent_whole_rows) == 5,
        "recurrent_whole_events_12": sum(int(row["occurrence_count"]) for row in recurrent_whole_rows) == 12,
        "slot_types_10": len(slot_rows) == 10,
        "unified_types_173": len(unified_rows) == 173,
        "unified_type_architecture": unified_type_status == Counter({"PRODUCTIVE_COMPONENT_OR_COMPOSITION": 101, "LOCAL_EXEMPLAR_SINGLETON": 55, "TERMINAL_SPECIALIST_WHOLE_CARD": 8, "MEMORIZED_RECURRENT_CARD": 5, "LICENSED_PARTIAL_COMPOSITION": 4}),
        "unified_event_architecture": unified_event_status == Counter({"PRODUCTIVE_COMPONENT_OR_COMPOSITION": 301, "LOCAL_EXEMPLAR_SINGLETON": 55, "MEMORIZED_RECURRENT_CARD": 12, "TERMINAL_SPECIALIST_WHOLE_CARD": 8, "LICENSED_PARTIAL_COMPOSITION": 5}),
        "terminal_middle_disjoint": not (set(middle_map) & set(terminal_map)),
        "dictionary_unchanged": all(all(row[key] == old[key] for key in old) for row, old in zip(out_dictionary, dictionary)),
        "events_unchanged": all(all(row[key] == old[key] for key in old) for row, old in zip(out_events, events)),
        "sentences_unchanged": all(all(row[key] == old[key] for key in old) for row, old in zip(out_sentences, sentences)),
        "fixed_pages_only": {row["page"] for row in out_events} == ALLOWED_PAGES,
        "sealed_absent": not any(row["page"].startswith("f84") for row in out_events),
        "records_markdown_complete": all(f"## {record} —" in RECORD_OUT.read_text(encoding="utf-8") for record in RECORD_ORDER),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(out_dictionary),
            "events": len(out_events),
            "sentences": len(out_sentences),
            "records": len(by_record),
            "middle_events": len(middle_events),
            "middle_types": len(middle_rows),
            "core_types": len(core_rows),
            "core_events": sum(int(row["occurrence_count"]) for row in core_rows),
            "middle_type_status": dict(sorted(middle_status.items())),
            "middle_event_status": dict(sorted(middle_event_status.items())),
            "unified_type_status": dict(sorted(unified_type_status.items())),
            "unified_event_status": dict(sorted(unified_event_status.items())),
        },
        "working_rule": "OPEN MIDDLE = PRODUCTIVE ARGUMENT/ACTION GRAMMAR + FIVE RECURRENT WHOLE CARDS + LOCAL SINGLETON EXEMPLAR TAIL",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, MIDDLE_OUT, CORE_OUT, WHOLE_OUT, SLOT_OUT, UNIFIED_OUT, CHECK_OUT]
    summary = {
        "status": result["status"],
        "counts": result["counts"],
        "input_hashes": {path.name: sha256(path) for path in [DICT_IN, EVENT_IN, SENTENCE_IN, TERMINAL_IN]},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "sealed": result["sealed"],
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise AssertionError(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
