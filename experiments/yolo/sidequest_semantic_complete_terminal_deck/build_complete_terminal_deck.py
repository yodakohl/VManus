#!/usr/bin/env python3
"""Build the complete creative deck of all 37 exact terminal cards."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_program_composition_completion"
STEP_BASE = HERE.parent / "sidequest_semantic_step_closure_completion"

DICT_IN = BASE / "SELECTED_173_PROGRAM_COMPOSITION_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_PROGRAM_COMPOSITION_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_PROGRAM_COMPOSITION_SENTENCES.tsv"
PROGRAM_IN = BASE / "PROGRAM_COMPOSITION_REGISTER.tsv"
COMPONENT_IN = BASE / "PROGRAM_COMPONENT_LEXICON.tsv"
STEP_DECK_IN = STEP_BASE / "STEP_CLOSURE_DECK.tsv"

DICT_OUT = HERE / "SELECTED_173_COMPLETE_TERMINAL_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_COMPLETE_TERMINAL_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_COMPLETE_TERMINAL_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_COMPLETE_TERMINAL_RECORDS.md"
DECK_OUT = HERE / "COMPLETE_TERMINAL_CARD_DECK.tsv"
COMPONENT_OUT = HERE / "COMPLETE_TERMINAL_COMPONENT_LEXICON.tsv"
FAMILY_OUT = HERE / "COMPLETE_TERMINAL_FAMILY_GRID.tsv"
REMAINDER_OUT = HERE / "ELEVEN_REMAINING_TERMINAL_INSTRUCTIONS.tsv"
CHECK_OUT = HERE / "BUILD_CHECK.json"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


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


def new_card(
    status: str,
    parse: str,
    components: str,
    core: str,
    order_direction: str,
    grade: str,
    reading: str,
    rationale: str,
    exception: str,
) -> dict[str, str]:
    return {
        "composition_status": status,
        "component_parse": parse,
        "component_ids": components,
        "action_core_de": core,
        "order_direction_de": order_direction,
        "grade_de": grade,
        "close_construction": "EXACT_CARD_CLOSE",
        "ignored_surface_elements": "RENDERER/FRAME AS MARKED IN PARSE" if "renderer" in parse else "KEINE",
        "composed_reading_de": reading,
        "composition_rationale_de": rationale,
        "exception_note_de": exception,
    }


NEW_CARDS = {
    "03626ca94cb17800d767": new_card("PRODUCTIVE_COMPOSITION", "SHED + EE + CLOSE_EXACT", "CORE_SHED|GRADE_EE|CLOSE_EXACT", "absetzen", "KEIN", "länger", "länger absetzen; schließen", "Lange Stufe der selbständigen SHED-Reihe.", "Nur ein langer Beleg, aber die Grundkarte ist zwölfmal vorhanden."),
    "07913ef9b1fb773cd325": new_card("PRODUCTIVE_COMPOSITION", "[Q renderer] + OK + CHED + CLOSE_EXACT", "CORE_OK|CORE_CHED|CLOSE_EXACT", "umsetzen", "Arbeitsgang ansetzen", "KEIN", "Umsetzgang ansetzen; schließen", "Zweite exakte OK+CHED-Karte mit derselben knappen Lesung.", "Nicht mit einer Temperaturbedeutung des sichtbaren E überladen."),
    "2e2027b1951d79911e24": new_card("MEMORIZED_WHOLE_CARD", "[ABKÜHLEN-GANZKARTE] + CLOSE_EXACT", "CLOSE_EXACT", "abkühlen", "KEIN", "KEIN", "abkühlen; schließen", "Herbal-Spezialkarte am Ende einer Auszugsfolge.", "TCHO besitzt in diesem Deck keinen unabhängigen zweiten Beleg."),
    "2e7e89e0bd12b999c280": new_card("PRODUCTIVE_COMPOSITION", "LSH + CLOSE_EXACT", "CORE_LSH|CLOSE_EXACT", "waschen", "KEIN", "KEIN", "waschen; schließen", "Zwei terminale Belege plus die offene Grundkarte lsho ergeben eine kleine Waschreihe.", "LSH bleibt ein ganzer Kern und wird nicht L+SHED zerlegt."),
    "95987d6f198d6d247511": new_card("MEMORIZED_WHOLE_CARD", "[AUFTRAGEN-GANZKARTE] + CLOSE_EXACT", "CLOSE_EXACT", "auftragen", "KEIN", "KEIN", "auftragen; schließen", "Gelernte Herbal-Anwendungskarte.", "CHEECKHO wird nicht mit CKHE=Seihen vermischt."),
    "97cc9ac109148723c472": new_card("MEMORIZED_WHOLE_CARD", "[KÜHL-GANZKARTE] + CLOSE_EXACT", "CLOSE_EXACT", "kühlen", "KEIN", "KEIN", "kühlen; schließen", "Gelernte kurze Kühlkarte.", "O wird nicht global zu KÜHL promoviert."),
    "cbb42a4fe68068325d6b": new_card("MEMORIZED_WHOLE_CARD", "[FRISCHWASSER-GANZKARTE] + CLOSE_EXACT", "CLOSE_EXACT", "Frischwasser zugeben", "KEIN", "KEIN", "Frischwasser zugeben; schließen", "Gelernte lokale Zulaufkarte.", "DSHE wird nicht aus dem ähnlich sichtbaren SHED-Absetzkern abgeleitet."),
    "d225b7a7b95da7aee437": new_card("PRODUCTIVE_COMPOSITION", "[D renderer] + CHD + CLOSE_EXACT", "CORE_CHED|CLOSE_EXACT", "umsetzen", "KEIN", "KEIN", "umsetzen; schließen", "Kurze CHD-Realisierung der Transferfamilie.", "D trägt keinen eigenen Handlungswert."),
    "d25110e0d8488927278f": new_card("PRODUCTIVE_COMPOSITION", "[Q renderer] + OK + EEE + CLOSE_EXACT", "CORE_OK|GRADE_EEE|CLOSE_EXACT", "Arbeitsgang ansetzen", "KEIN", "vollständig", "vollständig ansetzen; schließen", "Oberste belegte Stufe des OK+E/EE/EEE-Rasters.", "EEE ist nur in dieser lizenzierten Reihe ein Vollgrad."),
}


FAMILIES = {
    "SET_GRADE": ("OK + E/EE/EEE + Schluss", "kurz, länger oder vollständig ansetzen", ["7db18b2f0fb7ed0fcfd3", "7d25241b0e56c836372a", "d25110e0d8488927278f"]),
    "FOLLOW_GRADE": ("OT + E/EE + Schluss", "kurze oder lange Folge", ["c45ebac60774620561e2", "ff178343c18e287ce3b7"]),
    "TRANSFER_GRID": ("Richtung/Folge + CHD~CHED + Schluss", "umsetzen, einführen, fortsetzen oder abführen", ["259b2b3b0bf859882e2c", "28ffbc88b97772a75f1e", "4de12cf322dfb76ded1e", "601b77449028deed39de", "65df3cd9e59060042d47", "87411f84689b4f93a303", "de7321bface5628e35d6", "2bc2ed2630dbdaaa6b59", "1b1ffdd869fb1429ad03", "07913ef9b1fb773cd325", "d225b7a7b95da7aee437"]),
    "SETTLING_GRID": ("OK/OL + SHED + optional EE + Schluss", "absetzen, länger absetzen oder weiter absetzen", ["bc4f1f5c006c74a4d26d", "db167f8e9b53eefb58f8", "daa1347f456415fe8737", "03626ca94cb17800d767"]),
    "STRAIN_GRID": ("L oder Renderer + CKHE + Schluss", "seihen oder nach außen abseihen", ["d68bc8de3bcee09db23c", "c1db6b0a28d5cbb5d3d2"]),
    "PROCESS_GRADE": ("CHK/OLK + EE + Schluss", "länger wärmen oder sammeln", ["a84fbe3ad380df345b97", "3b70942557b3a40e8030"]),
    "WASH_CORE": ("LSH + Schluss", "waschen", ["2e7e89e0bd12b999c280"]),
    "PARTIAL_ADDRESS": ("bekannte Adresse + gelernter Innenwert + Schluss", "Abziehen, Nebenöffnung, Lauf schließen, Rest abführen", ["04a3877f0fc81b7597c9", "78b3b3140714da19090d", "8aedd154964a78e555d6", "f2af6326898fb5b490a4"]),
    "MEMORIZED_SPECIAL": ("unteilbare Spezialkarte + Schlussrolle", "acht gelernte lokale Fachbefehle", ["54e32e9c1414b20640e9", "7f68f60279efe6b28cd7", "b958a512ca6a3559e86e", "eb2e4bc143f623ee03ac", "2e2027b1951d79911e24", "95987d6f198d6d247511", "97cc9ac109148723c472", "cbb42a4fe68068325d6b"]),
}


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentences = read_tsv(SENTENCE_IN)
    old_programs = read_tsv(PROGRAM_IN)
    old_components = read_tsv(COMPONENT_IN)
    step_deck = read_tsv(STEP_DECK_IN)
    if (len(dictionary), len(events), len(sentences), len(old_programs), len(old_components), len(step_deck)) != (173, 381, 116, 28, 15, 37):
        raise AssertionError("unexpected input dimensions")

    old_ids = {row["program_card_id"] for row in old_programs}
    step_ids = {row["joint_tuple_id"] for row in step_deck}
    if set(NEW_CARDS) != step_ids - old_ids:
        raise AssertionError("new-card map must equal the nine terminal types outside the 28-card menu")

    event_count_by_card = Counter(row["joint_tuple_id"] for row in events)
    step_by_card = {row["joint_tuple_id"]: row for row in step_deck}
    deck_rows: list[dict[str, str]] = []
    for old in old_programs:
        deck_rows.append({
            "terminal_card_id": old["program_card_id"],
            "surfaces": old["surfaces"],
            "deck_origin": "VARIANT_PROGRAM_28",
            "occurrence_count": str(event_count_by_card[old["program_card_id"]]),
            "pages": step_by_card[old["program_card_id"]]["pages"],
            "statement_ids": step_by_card[old["program_card_id"]]["statement_ids"],
            "action_de": step_by_card[old["program_card_id"]]["action_core_de"],
            **{key: old[key] for key in ("composition_status", "component_parse", "component_ids", "action_core_de", "order_direction_de", "grade_de", "close_construction", "ignored_surface_elements", "composed_reading_de", "composition_rationale_de", "exception_note_de")},
        })
    for card_id, item in NEW_CARDS.items():
        source = step_by_card[card_id]
        deck_rows.append({
            "terminal_card_id": card_id,
            "surfaces": source["surface_family"],
            "deck_origin": "OTHER_TERMINAL_9",
            "occurrence_count": source["occurrences"],
            "pages": source["pages"],
            "statement_ids": source["statement_ids"],
            "action_de": source["action_core_de"],
            **item,
        })
    deck_rows.sort(key=lambda row: row["terminal_card_id"])
    deck_map = {row["terminal_card_id"]: row for row in deck_rows}

    component_defs = {
        row["component_id"]: (row["component_type"], row["value_de"], row["teaching_rule_de"])
        for row in old_components
    }
    component_defs["CORE_LSH"] = ("OPERATION", "waschen oder spülen", "Offene Grundkarte LSHO und terminale LSHEDY-Karte bilden eine begrenzte Waschreihe.")
    component_defs["GRADE_EEE"] = ("GRADE", "vollständig", "Oberer Vollgrad ausschließlich in der lizenzierten OK-Reihe.")
    component_rows: list[dict[str, str]] = []
    for component_id, (component_type, value_de, rule_de) in component_defs.items():
        cards = [row for row in deck_rows if component_id in row["component_ids"].split("|")]
        component_rows.append({
            "component_id": component_id,
            "component_type": component_type,
            "value_de": value_de,
            "terminal_card_types": str(len(cards)),
            "terminal_occurrences": str(sum(int(row["occurrence_count"]) for row in cards)),
            "terminal_cards": "|".join(row["surfaces"] for row in cards),
            "teaching_rule_de": rule_de,
        })

    family_rows: list[dict[str, str]] = []
    for family_id, (pattern, command, card_ids) in FAMILIES.items():
        rows_here = [deck_map[card_id] for card_id in card_ids]
        family_rows.append({
            "family_id": family_id,
            "productive_pattern": pattern,
            "apprentice_command_de": command,
            "terminal_card_types": str(len(rows_here)),
            "terminal_occurrences": str(sum(int(row["occurrence_count"]) for row in rows_here)),
            "surfaces": "|".join(row["surfaces"] for row in rows_here),
            "status_inventory": "|".join(dict.fromkeys(row["composition_status"] for row in rows_here)),
        })

    out_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        item = deck_map.get(row["joint_tuple_id"])
        if item:
            row["complete_terminal_status"] = item["composition_status"]
            row["complete_terminal_parse"] = item["component_parse"]
            row["complete_terminal_components"] = item["component_ids"]
            row["complete_terminal_reading_de"] = item["composed_reading_de"]
            row["complete_terminal_note"] = item["exception_note_de"]
        else:
            row["complete_terminal_status"] = "NOT_TERMINAL_CARD"
            row["complete_terminal_parse"] = "NOT_APPLICABLE"
            row["complete_terminal_components"] = "NOT_APPLICABLE"
            row["complete_terminal_reading_de"] = "NOT_APPLICABLE"
            row["complete_terminal_note"] = "Keine terminale Exaktkarte dieser Ausgabe."
        out_dictionary.append(row)

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        item = deck_map.get(row["joint_tuple_id"])
        if item:
            row["complete_terminal_status"] = item["composition_status"]
            row["complete_terminal_parse"] = item["component_parse"]
            row["complete_terminal_components"] = item["component_ids"]
            row["complete_terminal_reading_de"] = item["composed_reading_de"]
            row["complete_terminal_role"] = "EXACT_TERMINAL_CARD_AT_CELL_COMMIT"
        else:
            row["complete_terminal_status"] = "NOT_TERMINAL_CARD"
            row["complete_terminal_parse"] = "NOT_APPLICABLE"
            row["complete_terminal_components"] = "NOT_APPLICABLE"
            row["complete_terminal_reading_de"] = "NOT_APPLICABLE"
            row["complete_terminal_role"] = "NOT_APPLICABLE"
        out_events.append(row)

    out_sentences: list[dict[str, str]] = []
    for original in sentences:
        row = dict(original)
        item = deck_map.get(row["step_ending_card_id"])
        if item:
            row["complete_terminal_status"] = item["composition_status"]
            row["complete_terminal_parse"] = item["component_parse"]
            row["complete_terminal_command_de"] = item["composed_reading_de"]
            row["complete_terminal_note"] = item["exception_note_de"]
        elif row["step_ending_class"] == "RELEASE_RECORD":
            row["complete_terminal_status"] = "RECORD_LAYOUT_RELEASE"
            row["complete_terminal_parse"] = "RECORDLAYOUT"
            row["complete_terminal_command_de"] = "Record freigeben"
            row["complete_terminal_note"] = "Kein terminaler Kartenbefehl."
        else:
            row["complete_terminal_status"] = "OPEN_HANDOFF"
            row["complete_terminal_parse"] = "KEIN SCHLUSSPROGRAMM"
            row["complete_terminal_command_de"] = "Arbeitsstand weiterreichen"
            row["complete_terminal_note"] = "Offene Übergabe statt Zellschluss."
        out_sentences.append(row)

    remainder_rows: list[dict[str, str]] = []
    for row in out_sentences:
        if row["step_ending_card_id"] in NEW_CARDS:
            card = deck_map[row["step_ending_card_id"]]
            remainder_rows.append({
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "terminal_card_id": row["step_ending_card_id"],
                "surface": row["step_ending_surface"],
                "composition_status": card["composition_status"],
                "component_parse": card["component_parse"],
                "command_de": card["composed_reading_de"],
                "surface_sequence": row["surface_sequence"],
                "complete_instruction_de": row["workshop_sentence_de"],
            })

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(DECK_OUT, deck_rows)
    write_tsv(COMPONENT_OUT, component_rows)
    write_tsv(FAMILY_OUT, family_rows)
    write_tsv(REMAINDER_OUT, remainder_rows)

    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        by_record[row["record_unit_id"]].append(row)
    lines = [
        "# Elf Records mit vollständigem terminalem Befehlsdeck",
        "",
        "Alle 89 geschlossenen Anweisungen zeigen ihren kompositionellen oder gelernten terminalen Bauplan.",
        "",
    ]
    for record in RECORD_ORDER:
        rows_here = by_record[record]
        lines.extend([f"## {record} — {rows_here[0]['page']}", ""])
        for row in rows_here:
            suffix = ""
            if row["complete_terminal_status"] in {"PRODUCTIVE_COMPOSITION", "LICENSED_PARTIAL", "MEMORIZED_WHOLE_CARD"}:
                suffix = f" **[SCHLUSSKARTE: {row['complete_terminal_parse']}]**"
            lines.append(f"- **{row['statement_id']}** — {row['workshop_sentence_de']}{suffix}")
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    terminal_events = [row for row in out_events if row["joint_tuple_id"] in deck_map]
    card_status = Counter(row["composition_status"] for row in deck_rows)
    event_status = Counter(row["complete_terminal_status"] for row in terminal_events)
    sentence_status = Counter(row["complete_terminal_status"] for row in out_sentences)
    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(by_record) == set(RECORD_ORDER),
        "terminal_types_37": len(deck_rows) == 37,
        "terminal_events_89": len(terminal_events) == 89,
        "components_17": len(component_rows) == 17,
        "families_9": len(family_rows) == 9,
        "remaining_instructions_11": len(remainder_rows) == 11,
        "remaining_types_9": len({row["terminal_card_id"] for row in remainder_rows}) == 9,
        "card_status_25_4_8": card_status == Counter({"PRODUCTIVE_COMPOSITION": 25, "LICENSED_PARTIAL": 4, "MEMORIZED_WHOLE_CARD": 8}),
        "event_status_76_5_8": event_status == Counter({"PRODUCTIVE_COMPOSITION": 76, "LICENSED_PARTIAL": 5, "MEMORIZED_WHOLE_CARD": 8}),
        "sentence_status_89_19_8": sentence_status == Counter({"PRODUCTIVE_COMPOSITION": 76, "LICENSED_PARTIAL": 5, "MEMORIZED_WHOLE_CARD": 8, "OPEN_HANDOFF": 19, "RECORD_LAYOUT_RELEASE": 8}),
        "all_terminal_events_commit": all(row["step_closure_role"] == "COMMIT_CELL" for row in terminal_events),
        "all_terminal_events_statement_final": all(row["event_id"] == next(s for s in out_sentences if s["statement_id"] == row["statement_id"])["event_ids"].split("|")[-1] for row in terminal_events),
        "all_exact_close": all(row["close_construction"] == "EXACT_CARD_CLOSE" and "CLOSE_EXACT" in row["component_ids"].split("|") for row in deck_rows),
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
            "terminal_card_types": len(deck_rows),
            "terminal_events": len(terminal_events),
            "components": len(component_rows),
            "families": len(family_rows),
            "remaining_instructions": len(remainder_rows),
            "remaining_types": len({row["terminal_card_id"] for row in remainder_rows}),
            "card_status": dict(sorted(card_status.items())),
            "event_status": dict(sorted(event_status.items())),
        },
        "working_rule": "37 EXACT TERMINAL CARDS = 25 PRODUCTIVE + 4 PARTIAL + 8 MEMORIZED; 17 REUSABLE COMPONENTS",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, DECK_OUT, COMPONENT_OUT, FAMILY_OUT, REMAINDER_OUT, CHECK_OUT]
    summary = {
        "status": result["status"],
        "counts": result["counts"],
        "input_hashes": {path.name: sha256(path) for path in [DICT_IN, EVENT_IN, SENTENCE_IN, PROGRAM_IN, COMPONENT_IN, STEP_DECK_IN]},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "sealed": result["sealed"],
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise AssertionError(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
