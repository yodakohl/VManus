#!/usr/bin/env python3
"""Build the creative work-cell closure layer over the reference edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_reference_continuity_completion"

DICT_IN = BASE / "SELECTED_173_REFERENCE_CONTINUITY_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_REFERENCE_CONTINUITY_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_REFERENCE_CONTINUITY_SENTENCES.tsv"

DICT_OUT = HERE / "SELECTED_173_STEP_CLOSURE_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_STEP_CLOSURE_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_STEP_CLOSURE_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_STEP_CLOSURE_RECORDS.md"
CLOSE_DECK_OUT = HERE / "STEP_CLOSURE_DECK.tsv"
ENDING_OUT = HERE / "STATEMENT_ENDINGS.tsv"
LINE_CARRY_OUT = HERE / "LINE_CARRY.tsv"
COUNTER_OUT = HERE / "OPEN_DY_COUNTERCARDS.tsv"
CHECK_OUT = HERE / "BUILD_CHECK.json"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"no rows for {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def has_close(row: dict[str, str]) -> bool:
    return "CLOSE" in row["workshop_slots"].split("+")


def action_core(gloss: str) -> str:
    return gloss.removesuffix("; Schluss").removesuffix("; Ende")


def close_family(segmentation: str) -> str:
    if "OT_FOLLOW" in segmentation:
        return "NEXT_CLOSE"
    if "OL_CONTINUE" in segmentation:
        return "CONTINUE_CLOSE"
    if "OK_SET+GRADE" in segmentation:
        return "GRADED_SET_CLOSE"
    if "SHED_SETTLE" in segmentation:
        return "SETTLE_CLOSE"
    if "CHED_TRANSFER" in segmentation or "CHD_TRANSFER" in segmentation:
        return "TRANSFER_CLOSE"
    if "CKHE_STRAIN" in segmentation:
        return "STRAIN_CLOSE"
    return "LEARNED_SPECIALIST_CLOSE"


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentences = read_tsv(SENTENCE_IN)
    if (len(dictionary), len(events), len(sentences)) != (173, 381, 116):
        raise AssertionError("unexpected input dimensions")

    close_events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_statement: dict[str, list[dict[str, str]]] = OrderedDict()
    for event in events:
        events_by_statement.setdefault(event["statement_id"], []).append(event)
        if has_close(event):
            close_events_by_card[event["joint_tuple_id"]].append(event)

    statement_by_id = {row["statement_id"]: row for row in sentences}
    statements_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sentences:
        statements_by_record[row["record_unit_id"]].append(row)

    ending_by_statement: dict[str, dict[str, str]] = {}
    ending_rows: list[dict[str, str]] = []
    for record in RECORD_ORDER:
        record_rows = statements_by_record[record]
        for index, sentence in enumerate(record_rows):
            statement_events = events_by_statement[sentence["statement_id"]]
            close_events = [event for event in statement_events if has_close(event)]
            is_last = index == len(record_rows) - 1
            if close_events:
                ending = "COMMIT_CELL"
                register_effect = "CLEAR_OPERATION_SOURCE_TARGET__KEEP_OWNER_ITEM_AVAILABLE"
                teaching_command = "Handlung ausführen; Arbeitszelle abhaken"
                ending_card = close_events[-1]
            elif is_last:
                ending = "RELEASE_RECORD"
                register_effect = "CLEAR_OWNER_ITEM_SOURCE_TARGET_OPERATION"
                teaching_command = "Record endet; alle laufenden Register zurücksetzen"
                ending_card = None
            else:
                ending = "HANDOFF_OPEN"
                register_effect = "KEEP_OWNER_ITEM_SOURCE_TARGET_OPERATION_AVAILABLE"
                teaching_command = "Arbeitsgang offen an die nächste Zelle weiterreichen"
                ending_card = None
            next_id = "" if is_last else record_rows[index + 1]["statement_id"]
            info = {
                "statement_id": sentence["statement_id"],
                "record_unit_id": record,
                "page": sentence["page"],
                "loci": sentence["loci"],
                "event_count": sentence["event_count"],
                "ending_class": ending,
                "ending_card_id": ending_card["joint_tuple_id"] if ending_card else "",
                "ending_surface": ending_card["surface_display"] if ending_card else "",
                "ending_action_de": action_core(ending_card["concrete_word_reading_de"]) if ending_card else "",
                "next_statement_id": next_id,
                "register_effect": register_effect,
                "teaching_command_de": teaching_command,
                "crosses_physical_line": "YES" if "|" in sentence["loci"] else "NO",
                "workshop_sentence_de": sentence["workshop_sentence_de"],
            }
            ending_by_statement[sentence["statement_id"]] = info
            ending_rows.append(info)

    out_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        ident = row["joint_tuple_id"]
        close_rows = close_events_by_card.get(ident, [])
        surfaces = {event["surface_display"].lower() for event in events if event["joint_tuple_id"] == ident}
        open_dy = not close_rows and any(surface.endswith("dy") for surface in surfaces)
        row["step_closure_role"] = (
            "EXACT_TERMINAL_ACTION_CARD" if close_rows else
            "OPEN_DY_COUNTERCARD" if open_dy else
            "NONTERMINAL_CARD"
        )
        row["step_closure_family"] = close_family(row["semantic_segmentation"]) if close_rows else "NONE"
        row["step_action_core_de"] = action_core(row["concrete_word_reading_de"])
        row["step_exit_value_de"] = "ARBEITSZELLE SCHLIESSEN" if close_rows else "KEIN EIGENER ZELLSCHLUSS"
        row["step_closure_occurrences"] = str(len(close_rows))
        row["step_closure_teaching_note"] = (
            "Ganze Karte als Handlung plus Zellschluss lernen."
            if close_rows else
            "Trotz sichtbarem -dy offen: exakte Kartenidentität geht vor Schriftende."
            if open_dy else
            "Kein eigener Schlusswert."
        )
        out_dictionary.append(row)

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        close = has_close(row)
        row["step_closure_role"] = "COMMIT_CELL" if close else "NO_EVENT_CLOSE"
        row["step_action_core_de"] = action_core(row["concrete_word_reading_de"])
        row["step_exit_value_de"] = "ARBEITSZELLE SCHLIESSEN" if close else ""
        row["statement_ending_class"] = ending_by_statement[row["statement_id"]]["ending_class"]
        row["statement_register_effect"] = ending_by_statement[row["statement_id"]]["register_effect"]
        out_events.append(row)

    out_sentences: list[dict[str, str]] = []
    for original in sentences:
        row = dict(original)
        info = ending_by_statement[row["statement_id"]]
        row["step_ending_class"] = info["ending_class"]
        row["step_ending_card_id"] = info["ending_card_id"]
        row["step_ending_surface"] = info["ending_surface"]
        row["step_ending_action_de"] = info["ending_action_de"]
        row["step_next_statement_id"] = info["next_statement_id"]
        row["step_register_effect"] = info["register_effect"]
        row["step_teaching_command_de"] = info["teaching_command_de"]
        row["step_editor_label"] = {
            "COMMIT_CELL": "[ZELLE ZU]",
            "HANDOFF_OPEN": "[WEITER]",
            "RELEASE_RECORD": "[RECORD ENDE]",
        }[info["ending_class"]]
        out_sentences.append(row)

    close_deck_rows: list[dict[str, str]] = []
    dmap = {row["joint_tuple_id"]: row for row in out_dictionary}
    for ident, selected in sorted(close_events_by_card.items(), key=lambda item: (-len(item[1]), item[0])):
        drow = dmap[ident]
        close_deck_rows.append({
            "joint_tuple_id": ident,
            "surface_family": drow["surface_family"],
            "occurrences": str(len(selected)),
            "pages": "|".join(sorted({row["page"] for row in selected})),
            "closure_family": drow["step_closure_family"],
            "action_core_de": drow["step_action_core_de"],
            "exit_value_de": "ARBEITSZELLE SCHLIESSEN",
            "complete_card_reading_de": drow["concrete_word_reading_de"],
            "event_ids": "|".join(row["event_id"] for row in selected),
            "statement_ids": "|".join(row["statement_id"] for row in selected),
            "apprentice_rule_de": "Handlung ausführen und lokale Zelle abhaken",
        })

    line_carry_rows = [
        {
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "loci": row["loci"],
            "ending_class": ending_by_statement[row["statement_id"]]["ending_class"],
            "event_count": row["event_count"],
            "line_break_rule_de": "Nur Feder neu ansetzen; alle laufenden Register behalten",
            "workshop_sentence_de": row["workshop_sentence_de"],
        }
        for row in sentences if "|" in row["loci"]
    ]

    counter_rows = [
        {
            "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "joint_tuple_id": row["joint_tuple_id"],
            "surface_display": row["surface_display"],
            "selected_value_de": row["concrete_word_reading_de"],
            "why_open_de": "Exakte offene Karte; sichtbares -dy ist kein selbständiger Schluss",
        }
        for row in events
        if row["surface_display"].lower().endswith("dy") and not has_close(row)
    ]

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(CLOSE_DECK_OUT, close_deck_rows)
    write_tsv(ENDING_OUT, ending_rows)
    write_tsv(LINE_CARRY_OUT, line_carry_rows)
    write_tsv(COUNTER_OUT, counter_rows)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        records[row["record_unit_id"]].append(row)
    lines = [
        "# Elf Records mit Werkstattklammer",
        "",
        "Editorische Marken: `[ZELLE ZU]` bestätigt den lokalen Arbeitsschritt; "
        "`[WEITER]` reicht ihn weiter; `[RECORD ENDE]` setzt alle Register zurück.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = records[record]
        lines.extend([f"## {record} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            lines.append(
                f"{index}. **{row['statement_id']}** — "
                f"{row['workshop_sentence_de'].rstrip('.')} {row['step_editor_label']}"
            )
        lines.extend(["", "### Fortlaufend", ""])
        lines.append(" ".join(
            f"{row['workshop_sentence_de'].rstrip('.')} {row['step_editor_label']}"
            for row in rows
        ))
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    ending_counts = Counter(row["ending_class"] for row in ending_rows)
    close_family_counts = Counter(row["closure_family"] for row in close_deck_rows)
    close_family_events = Counter()
    for row in close_deck_rows:
        close_family_events[row["closure_family"]] += int(row["occurrences"])

    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(records) == set(RECORD_ORDER),
        "close_card_types_37": len(close_deck_rows) == 37,
        "close_events_89": sum(len(rows) for rows in close_events_by_card.values()) == 89,
        "committed_statements_89": ending_counts["COMMIT_CELL"] == 89,
        "open_handoffs_19": ending_counts["HANDOFF_OPEN"] == 19,
        "record_releases_8": ending_counts["RELEASE_RECORD"] == 8,
        "line_carries_18": len(line_carry_rows) == 18,
        "open_dy_counterevents_16": len(counter_rows) == 16,
        "close_always_final": all(
            not any(has_close(event) for event in rows[:-1]) and has_close(rows[-1])
            for rows in events_by_statement.values() if any(has_close(event) for event in rows)
        ),
        "no_double_close": all(sum(has_close(event) for event in rows) <= 1 for rows in events_by_statement.values()),
        "event_dictionary_match": all(
            row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"]
            for row in out_events
        ),
        "all_cards_readable": all(row["concrete_word_reading_de"] for row in out_dictionary),
        "all_events_readable": all(row["contextual_event_reading_de"] for row in out_events),
        "only_fixed_pages": {row["page"] for row in out_events} == ALLOWED_PAGES,
        "sealed_absent": not any(row["page"].startswith("f84") for row in out_events),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(out_dictionary),
            "events": len(out_events),
            "sentences": len(out_sentences),
            "records": len(records),
            "close_card_types": len(close_deck_rows),
            "close_events": sum(len(rows) for rows in close_events_by_card.values()),
            "ending_classes": dict(sorted(ending_counts.items())),
            "line_carries": len(line_carry_rows),
            "open_dy_counterevents": len(counter_rows),
            "closure_family_card_types": dict(sorted(close_family_counts.items())),
            "closure_family_events": dict(sorted(close_family_events.items())),
        },
        "workshop_rule": "COMMIT CELL / HAND OFF OPEN / RELEASE RECORD; PHYSICAL LINE BREAK DOES NOTHING",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, CLOSE_DECK_OUT, ENDING_OUT, LINE_CARRY_OUT, COUNTER_OUT, CHECK_OUT]
    summary = {
        "status": result["status"],
        "counts": result["counts"],
        "input_hashes": {path.name: sha256(path) for path in [DICT_IN, EVENT_IN, SENTENCE_IN]},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "sealed": result["sealed"],
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)
