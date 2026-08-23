#!/usr/bin/env python3
"""Build the creative selector grammar for the 13 local variant modules."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_work_module_completion"

DICT_IN = BASE / "SELECTED_173_WORK_MODULE_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_WORK_MODULE_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_WORK_MODULE_SENTENCES.tsv"
MODULE_IN = BASE / "WORK_MODULE_REGISTER.tsv"

DICT_OUT = HERE / "SELECTED_173_VARIANT_SELECTOR_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_VARIANT_SELECTOR_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_VARIANT_SELECTOR_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_VARIANT_SELECTOR_RECORDS.md"
REGISTER_OUT = HERE / "VARIANT_SELECTOR_REGISTER.tsv"
MODULE_SUMMARY_OUT = HERE / "MODULE_SELECTOR_SUMMARY.tsv"
PROGRAM_DECK_OUT = HERE / "PROGRAM_CARD_DECK.tsv"
AXIS_OUT = HERE / "SELECTOR_AXIS_LEXICON.tsv"
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


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


AXES = {
    "CONTACT_DURATION": {
        "label_de": "Kontakt- oder Folgegrad",
        "question_de": "Wie lange beziehungsweise in welcher kurzen oder langen Folge wird angesetzt?",
        "rule_de": "Die Programmmarke wählt kurz, länger, kurze Folge oder lange Folge; davor stehen gegebenenfalls Posten, Maß und Ziel.",
    },
    "SETTLING": {
        "label_de": "Absetzen",
        "question_de": "Soll der aktuelle oder vorige Posten jetzt absetzen oder weiter absetzen?",
        "rule_de": "ABSETZEN schließt die lokale Ruhe-/Klärzelle; WEITER ABSETZEN behält den Vorposten bei.",
    },
    "TRANSFER_CONTINUE": {
        "label_de": "Umsetzen oder fortführen",
        "question_de": "Wird umgesetzt, eingeführt, fortgesetzt oder als Folge umgesetzt?",
        "rule_de": "Quelle, Ziel und Folge stehen vor der terminalen Transfer-/Fortsetzungskarte.",
    },
    "OUTFLOW_WITHDRAW": {
        "label_de": "Abführen oder abziehen",
        "question_de": "Wird der ganze Posten abgeführt, der Rest abgeführt oder nur eine Fraktion abgezogen?",
        "rule_de": "Die Schlusskarte unterscheidet Abfluss, Restabfluss und Fraktionsentnahme.",
    },
    "STRAINING": {
        "label_de": "Seihen",
        "question_de": "Ist ein normaler Seihgang oder ein Abseih-/Folgegang fällig?",
        "rule_de": "Tuch, Ziel und Vorbehandlung stehen vor der gelernten Seihschlusskarte.",
    },
    "APPARATUS_CONFIGURATION": {
        "label_de": "Gerätestellung",
        "question_de": "Welche Öffnung, Verbindung oder Befestigung wird für diese Station gesetzt?",
        "rule_de": "Die terminale Karte bestätigt die lokale Gerätehandlung, nicht den Stoffnamen.",
    },
    "WASHING": {
        "label_de": "Waschen",
        "question_de": "Ist dies die Hauptwaschung oder ein Nachwaschgang?",
        "rule_de": "Die Programmkarten trennen Waschung und Nachwaschen; Medium und Ziel können davor ergänzt werden.",
    },
    "HEATING": {
        "label_de": "Erwärmen",
        "question_de": "Soll diese Station länger wärmen?",
        "rule_de": "Der Wärmegrad sitzt in der terminalen Programmkartenfamilie; Maß und Ziel stehen davor.",
    },
    "COLLECTION": {
        "label_de": "Sammeln",
        "question_de": "Soll die Station diesen Posten länger sammeln?",
        "rule_de": "Die terminale Sammelkarte wählt das lange Sammelprogramm; Auffangziel und Anwendung können davor stehen.",
    },
    "SWIVEL_MIX": {
        "label_de": "Schwenken",
        "question_de": "Soll der Posten an dieser Station geschwenkt oder durchmischt werden?",
        "rule_de": "Die gelernte Schwenkkarte ist ein eigenes Stationsprogramm, keine allgemeine Transferendung.",
    },
    "RECORD_RELEASE": {
        "label_de": "Recordausgang",
        "question_de": "Welcher Arbeitsstand wird am Recordende hinterlassen oder vorgemerkt?",
        "rule_de": "Hier ersetzt das Recordlayout die terminale Programmkarte; der ganze letzte Eintrag beschreibt den Ausgangszustand.",
    },
}


ACTION_GROUPS = {
    "CONTACT_DURATION": {"kurz ansetzen", "länger ansetzen", "kurze Folge", "lange Folge"},
    "SETTLING": {"absetzen", "weiter absetzen"},
    "TRANSFER_CONTINUE": {"Folgeumsetzung", "dorthin umsetzen", "einführen", "fortsetzen", "umsetzen"},
    "OUTFLOW_WITHDRAW": {"Rest abführen", "abführen", "abziehen"},
    "STRAINING": {"abseihen", "seihen"},
    "APPARATUS_CONFIGURATION": {"Nebenöffnung", "Wasserlauf schließen", "befestigen"},
    "WASHING": {"Waschung", "nachwaschen"},
    "HEATING": {"länger wärmen"},
    "COLLECTION": {"länger sammeln"},
    "SWIVEL_MIX": {"schwenken"},
}
ACTION_TO_AXIS = {action: axis for axis, actions in ACTION_GROUPS.items() for action in actions}


MODULE_GUIDE = {
    "WM10": ("Welches Grundprogramm braucht der gemeinsame Pool?", "Kontakt, Vollansatz, Schwenken, Absetzen oder bloßes Fortführen.", "Die fünf Einträge könnten trotzdem Phasen eines langen Bades sein."),
    "WM12": ("Welche kurze Haltevariante gilt für diesen oder den nächsten Posten?", "Warm-absetzen, kurz ansetzen oder den nächsten Posten kurz ansetzen.", "Zwei gleiche Kurzprogramme können bloße Wiederholung sein."),
    "WM15": ("Wie endet dieser Poolposten?", "Sammeln/einreiben, absetzen, wärmen/seihen oder zum Ziel führen.", "Die vier Einträge könnten eine einzige Abschlussfolge bilden."),
    "WM16": ("Welche Behandlung gilt an den oberen Paarbecken?", "Umsetzen, fortsetzen, Portion länger halten, durch Auslass seihen oder am Tuch angleichen.", "Die sichtbare Paarung könnte eine feste Reihenfolge statt Auswahl bedeuten."),
    "WM18": ("Welcher Posten soll am linken Mittelgerät absetzen?", "Neues Folgemaß ansetzen oder den vorigen Posten weiter absetzen.", "Beide Einträge könnten erste und zweite Absetzphase sein."),
    "WM22": ("Welches Randstationsprogramm wird ausgeführt?", "Einführen, Warmwasser/Öffnung, Langkontakt, Waschung, lange Folge oder Restablauf.", "Die sieben Einträge könnten ein vollständiger Wartungszyklus sein."),
    "WM23": ("Was geschieht an der oberen Fächerstation?", "Länger sammeln, länger wärmen oder nach Sollmaß abführen.", "Die drei Einträge könnten sammeln→wärmen→abführen bedeuten."),
    "WM25": ("Welche Rundgefäßroutine gilt?", "Umsetzen/fortführen, nach Sollmaß länger ansetzen oder abführen.", "Die drei Einträge könnten eine kurze Gefäßfolge sein."),
    "WM29": ("Welche Routine gehört zur ungelösten Zwischenstation?", "Langkontakt, Absetzen, Abführen, Folgeumsetzung oder einfache Umsetzung.", "Ohne sicheren Bildbesitzer kann dies auch ein heterogener Textrest sein."),
    "WM31": ("Welches Programm des Hauptbogenpaars wird gewählt?", "Kontaktgrade, Spülfolge, Wasserweitergabe, Wanne, Abziehen oder unteres Ziel.", "Die acht Einträge könnten Abschnitte eines einzigen großen Programms sein."),
    "WM32": ("Welche Behandlung läuft am Hauptpaar?", "Kontakt, Becken, Befestigung, Tuch, Seihen, Wärme/Ablauf, Absetzen oder Fortsetzen.", "Medizinische Auflage und technische Filterbedienung bleiben isomorph."),
    "WM33": ("Welche lokale Funktion übernimmt der linke Fransenposten?", "Nachwaschen, Abführen, Fortsetzung/Absetzen oder Wasserlauf schließen.", "Die vier Einträge könnten ein gemeinsamer Reinigungsablauf sein."),
    "WM36": ("Welcher Nachtrag gilt an der linken offenen Station?", "Folgeumsetzung, einfache Umsetzung oder ein mehrstufiger warmer Recordausgang.", "Der kurze Nachtrag könnte chronologisch an B4 anschließen."),
}


RELEASE_VALUES = {
    "B1-S021": "Posten zum Ziel führen",
    "B5-S003": "absetzen, warm halten, Öffnungsstufe einstellen und erneut umsetzen",
}

SENTENCE_REPAIRS = {
    "B1-S001": "Setze kurz an und schließe",
    "B1-S010": "Setze kurz an und schließe",
    "B1-S021": "Führe den Posten dorthin",
    "B2-S009": "Lass weiter absetzen und schließe",
    "B4-S007": "Seih und schließe",
}


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    input_sentences = read_tsv(SENTENCE_IN)
    sentences: list[dict[str, str]] = []
    for original in input_sentences:
        row = dict(original)
        if row["statement_id"] in SENTENCE_REPAIRS:
            row["workshop_sentence_de"] = SENTENCE_REPAIRS[row["statement_id"]]
        sentences.append(row)
    modules = read_tsv(MODULE_IN)
    if (len(dictionary), len(events), len(sentences), len(modules)) != (173, 381, 116, 37):
        raise AssertionError("unexpected input dimensions")

    event_map = {row["event_id"]: row for row in events}
    module_map = {row["module_id"]: row for row in modules}
    variant_modules = {row["module_id"] for row in modules if row["module_type"] == "LOCAL_STATION_VARIANTS"}
    if variant_modules != set(MODULE_GUIDE):
        raise AssertionError("module guide must cover exactly 13 variant modules")
    variant_sentences = [row for row in sentences if row["work_module_id"] in variant_modules]
    if len(variant_sentences) != 66:
        raise AssertionError("expected 66 variant statements")

    selector_rows: list[dict[str, str]] = []
    for sentence in variant_sentences:
        statement_id = sentence["statement_id"]
        event_ids = sentence["event_ids"].split("|")
        event_rows = [event_map[event_id] for event_id in event_ids]
        is_release = sentence["step_ending_class"] == "RELEASE_RECORD"
        if is_release:
            axis = "RECORD_RELEASE"
            program_card_id = "RECORD_LAYOUT"
            program_surface = "[RECORDENDE]"
            program_event_id = ""
            program_value = RELEASE_VALUES[statement_id]
            modifier_events = event_rows
            modifier_cards = sentence["card_sequence_de"]
        else:
            action = sentence["step_ending_action_de"]
            if action not in ACTION_TO_AXIS:
                raise AssertionError(f"unclassified program action {statement_id}: {action}")
            axis = ACTION_TO_AXIS[action]
            program_card_id = sentence["step_ending_card_id"]
            program_surface = sentence["step_ending_surface"]
            program_event_id = event_ids[-1]
            if event_rows[-1]["joint_tuple_id"] != program_card_id:
                raise AssertionError(f"program card is not final event in {statement_id}")
            program_value = action
            modifier_events = event_rows[:-1]
            card_parts = sentence["card_sequence_de"].split(" · ")
            modifier_cards = " · ".join(card_parts[:-1]) if len(card_parts) > 1 else "KEINE"
        modifier_slots = unique([
            slot
            for event in modifier_events
            for slot in event["workshop_slots"].split("+")
            if slot and slot != "CLOSE"
        ])
        module_question, module_logic, module_confusion = MODULE_GUIDE[sentence["work_module_id"]]
        axis_info = AXES[axis]
        selector_rows.append({
            "selector_row": f"VS{len(selector_rows) + 1:03d}",
            "statement_id": statement_id,
            "record_unit_id": sentence["record_unit_id"],
            "page": sentence["page"],
            "work_module_id": sentence["work_module_id"],
            "work_module_title_de": sentence["work_module_title_de"],
            "owner_sequence": sentence["work_module_owner_sequence"],
            "program_card_id": program_card_id,
            "program_surface": program_surface,
            "program_event_id": program_event_id,
            "selector_axis": axis,
            "selector_axis_de": axis_info["label_de"],
            "selector_value_de": program_value,
            "axis_question_de": axis_info["question_de"],
            "module_question_de": module_question,
            "modifier_event_ids": "|".join(event["event_id"] for event in modifier_events) or "KEINE",
            "modifier_cards_de": modifier_cards,
            "modifier_slots": "|".join(modifier_slots) or "KEINE",
            "surface_sequence": sentence["surface_sequence"],
            "card_sequence_de": sentence["card_sequence_de"],
            "selected_instruction_de": sentence["workshop_sentence_de"],
            "selector_reading_de": (
                f"Wähle Recordausgang „{program_value}“; die ganze letzte Zelle beschreibt den hinterlassenen Arbeitsstand."
                if is_release
                else f"Wähle Programm „{program_value}“; fülle davor {modifier_cards}."
            ),
            "module_choice_logic_de": module_logic,
            "strongest_confusion_de": module_confusion,
        })

    # Reuse counts make clear which program cards are learned recurring commands.
    use_by_program: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selector_rows:
        use_by_program[row["program_card_id"]].append(row)
    for row in selector_rows:
        uses = use_by_program[row["program_card_id"]]
        row["program_reuse_count"] = str(len(uses))
        row["program_reuse_modules"] = "|".join(unique([item["work_module_id"] for item in uses]))
        row["program_reuse_statements"] = "|".join(item["statement_id"] for item in uses)

    program_rows: list[dict[str, str]] = []
    for program_id, uses in sorted(use_by_program.items()):
        if program_id == "RECORD_LAYOUT":
            continue
        actions = unique([row["selector_value_de"] for row in uses])
        axes = unique([row["selector_axis"] for row in uses])
        if len(actions) != 1 or len(axes) != 1:
            raise AssertionError(f"non-invariant program card {program_id}")
        program_rows.append({
            "program_card_id": program_id,
            "surfaces": "|".join(unique([row["program_surface"] for row in uses])),
            "program_action_de": actions[0],
            "selector_axis": axes[0],
            "selector_axis_de": AXES[axes[0]]["label_de"],
            "occurrence_count": str(len(uses)),
            "statement_ids": "|".join(row["statement_id"] for row in uses),
            "module_ids": "|".join(unique([row["work_module_id"] for row in uses])),
            "pages": "|".join(unique([row["page"] for row in uses])),
            "owner_sequences": "|".join(unique([row["owner_sequence"] for row in uses])),
            "modifier_slot_inventory": "|".join(unique([
                slot for row in uses for slot in row["modifier_slots"].split("|") if slot != "KEINE"
            ])) or "KEINE",
            "teaching_rule_de": AXES[axes[0]]["rule_de"],
        })

    axis_counts = Counter(row["selector_axis"] for row in selector_rows)
    axis_rows = [
        {
            "selector_axis": axis,
            "selector_axis_de": info["label_de"],
            "entry_count": str(axis_counts[axis]),
            "distinct_program_cards": str(len({
                row["program_card_id"] for row in selector_rows if row["selector_axis"] == axis
            })),
            "values_de": "|".join(unique([
                row["selector_value_de"] for row in selector_rows if row["selector_axis"] == axis
            ])),
            "apprentice_question_de": info["question_de"],
            "composition_rule_de": info["rule_de"],
        }
        for axis, info in AXES.items()
    ]

    module_rows: list[dict[str, str]] = []
    for module_id in sorted(variant_modules):
        rows_here = [row for row in selector_rows if row["work_module_id"] == module_id]
        source = module_map[module_id]
        question, logic, confusion = MODULE_GUIDE[module_id]
        module_rows.append({
            "work_module_id": module_id,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "work_module_title_de": source["workshop_title_de"],
            "owner_sequence": source["owner_sequence"],
            "entry_count": str(len(rows_here)),
            "module_question_de": question,
            "selector_axes": "|".join(unique([row["selector_axis"] for row in rows_here])),
            "program_values_de": "|".join(row["selector_value_de"] for row in rows_here),
            "module_choice_logic_de": logic,
            "strongest_confusion_de": confusion,
        })

    selector_by_statement = {row["statement_id"]: row for row in selector_rows}
    out_sentences: list[dict[str, str]] = []
    for original in sentences:
        row = dict(original)
        old_sentence = next(item for item in input_sentences if item["statement_id"] == row["statement_id"])
        row["variant_selector_previous_workshop_sentence_de"] = old_sentence["workshop_sentence_de"]
        row["variant_selector_sentence_revision"] = (
            "REMOVE_POSITIONAL_CHRONOLOGY" if row["statement_id"] in SENTENCE_REPAIRS else "UNCHANGED"
        )
        selector = selector_by_statement.get(row["statement_id"])
        if selector:
            row["variant_selector_status"] = "LOCAL_VARIANT_ENTRY"
            row["variant_selector_axis"] = selector["selector_axis"]
            row["variant_selector_value_de"] = selector["selector_value_de"]
            row["variant_program_card_id"] = selector["program_card_id"]
            row["variant_program_surface"] = selector["program_surface"]
            row["variant_modifier_cards_de"] = selector["modifier_cards_de"]
            row["variant_module_question_de"] = selector["module_question_de"]
            row["variant_selector_reading_de"] = selector["selector_reading_de"]
        else:
            row["variant_selector_status"] = "NOT_LOCAL_VARIANT_MODULE"
            row["variant_selector_axis"] = "NOT_APPLICABLE"
            row["variant_selector_value_de"] = "NOT_APPLICABLE"
            row["variant_program_card_id"] = "NOT_APPLICABLE"
            row["variant_program_surface"] = "NOT_APPLICABLE"
            row["variant_modifier_cards_de"] = "NOT_APPLICABLE"
            row["variant_module_question_de"] = "NOT_APPLICABLE"
            row["variant_selector_reading_de"] = "Bestehende Ketten-, Übergabe-, Besitzerbruch- oder Einzelroutine; keine Auswahl aus einem lokalen Variantenmenü."
        out_sentences.append(row)

    sentence_out_map = {row["statement_id"]: row for row in out_sentences}
    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        selector = selector_by_statement.get(row["statement_id"])
        if selector:
            row["variant_selector_status"] = "LOCAL_VARIANT_EVENT"
            row["variant_selector_axis"] = selector["selector_axis"]
            row["variant_selector_value_de"] = selector["selector_value_de"]
            row["variant_program_card"] = "YES" if row["event_id"] == selector["program_event_id"] else "NO"
            row["variant_program_card_id"] = selector["program_card_id"]
            row["variant_selector_layer_note"] = "PROGRAM_CARD_SELECTS_ROUTINE__PRECEDING_CARDS_FILL_PARAMETERS"
        else:
            row["variant_selector_status"] = "NOT_LOCAL_VARIANT_MODULE"
            row["variant_selector_axis"] = "NOT_APPLICABLE"
            row["variant_selector_value_de"] = "NOT_APPLICABLE"
            row["variant_program_card"] = "NOT_APPLICABLE"
            row["variant_program_card_id"] = "NOT_APPLICABLE"
            row["variant_selector_layer_note"] = "EXISTING_EVENT_VALUE_UNCHANGED"
        out_events.append(row)

    program_by_card = {row["program_card_id"]: row for row in program_rows}
    out_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        program = program_by_card.get(row["joint_tuple_id"])
        row["variant_program_card_usage"] = "YES" if program else "NO"
        row["variant_program_axis"] = program["selector_axis"] if program else "NOT_APPLICABLE"
        row["variant_program_occurrences"] = program["occurrence_count"] if program else "0"
        row["variant_selector_layer"] = "CARD_VALUE_UNCHANGED__USAGE_AS_TERMINAL_PROGRAM_SELECTOR"
        out_dictionary.append(row)

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(REGISTER_OUT, selector_rows)
    write_tsv(MODULE_SUMMARY_OUT, module_rows)
    write_tsv(PROGRAM_DECK_OUT, program_rows)
    write_tsv(AXIS_OUT, axis_rows)

    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        by_record[row["record_unit_id"]].append(row)
    lines = [
        "# Elf Records mit Varianten-Auswahlfragen",
        "",
        "Bei Variantenmodulen steht zuerst die Auswahlfrage. `[PROGRAMM]` bezeichnet die gelernte terminale Arbeitskarte; davor stehen ihre Parameter.",
        "",
    ]
    for record in RECORD_ORDER:
        record_sentences = by_record[record]
        lines.extend([f"## {record} — {record_sentences[0]['page']}", ""])
        record_module_ids = unique([row["work_module_id"] for row in record_sentences])
        for module_id in record_module_ids:
            module = module_map[module_id]
            module_sentences = [row for row in record_sentences if row["work_module_id"] == module_id]
            lines.extend([f"### {module_id} — {module['workshop_title_de']}", ""])
            if module_id in MODULE_GUIDE:
                lines.extend([f"**Auswahlfrage:** {MODULE_GUIDE[module_id][0]}", ""])
            else:
                lines.extend([f"**Modus:** {module['chronology_rule_de']}", ""])
            for sentence in module_sentences:
                if sentence["variant_selector_status"] == "LOCAL_VARIANT_ENTRY":
                    lines.append(
                        f"- **{sentence['statement_id']} [PROGRAMM: {sentence['variant_selector_value_de']}]** — "
                        f"{sentence['workshop_sentence_de']} *(Vorfelder: {sentence['variant_modifier_cards_de']})*"
                    )
                else:
                    lines.append(f"- **{sentence['statement_id']}** — {sentence['workshop_sentence_de']}")
            lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    program_event_ids = {row["program_event_id"] for row in selector_rows if row["program_event_id"]}
    axis_expected = {
        "CONTACT_DURATION": 18,
        "SETTLING": 11,
        "TRANSFER_CONTINUE": 14,
        "OUTFLOW_WITHDRAW": 8,
        "STRAINING": 4,
        "APPARATUS_CONFIGURATION": 3,
        "WASHING": 2,
        "HEATING": 1,
        "COLLECTION": 2,
        "SWIVEL_MIX": 1,
        "RECORD_RELEASE": 2,
    }
    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(by_record) == set(RECORD_ORDER),
        "variant_modules_13": len(variant_modules) == 13,
        "variant_entries_66": len(selector_rows) == 66,
        "variant_events_183": sum(1 for row in out_events if row["variant_selector_status"] == "LOCAL_VARIANT_EVENT") == 183,
        "terminal_program_events_64": len(program_event_ids) == 64,
        "record_layout_selectors_2": sum(row["program_card_id"] == "RECORD_LAYOUT" for row in selector_rows) == 2,
        "exact_program_cards_28": len(program_rows) == 28,
        "axis_counts_exact": dict(axis_counts) == axis_expected,
        "top_five_exact_program_cards_32": sum(
            int(row["occurrence_count"])
            for row in program_rows
            if set(row["surfaces"].split("|")) & {"qokeedy", "shedy", "qokedy", "lchedy", "shckhedy"}
        ) == 32,
        "all_closed_program_cards_final": all(
            row["program_card_id"] == "RECORD_LAYOUT" or row["program_event_id"] == sentence_out_map[row["statement_id"]]["event_ids"].split("|")[-1]
            for row in selector_rows
        ),
        "program_card_values_invariant": all(len({row["selector_value_de"] for row in uses}) == 1 for card, uses in use_by_program.items() if card != "RECORD_LAYOUT"),
        "dictionary_values_unchanged": all(
            row["concrete_word_reading_de"] == original["concrete_word_reading_de"]
            for row, original in zip(out_dictionary, dictionary)
        ),
        "event_values_unchanged": all(
            row["contextual_event_reading_de"] == original["contextual_event_reading_de"]
            for row, original in zip(out_events, events)
        ),
        "sentence_repairs_exact_5": {
            row["statement_id"] for row in out_sentences if row["variant_selector_sentence_revision"] == "REMOVE_POSITIONAL_CHRONOLOGY"
        } == set(SENTENCE_REPAIRS),
        "other_111_sentence_values_unchanged": all(
            row["workshop_sentence_de"] == original["workshop_sentence_de"]
            for row, original in zip(out_sentences, input_sentences)
            if row["statement_id"] not in SENTENCE_REPAIRS
        ),
        "fixed_pages_only": {row["page"] for row in out_events} == ALLOWED_PAGES,
        "sealed_absent": not any(row["page"].startswith("f84") for row in out_events),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(out_dictionary),
            "events": len(out_events),
            "sentences": len(out_sentences),
            "records": len(by_record),
            "variant_modules": len(variant_modules),
            "variant_entries": len(selector_rows),
            "variant_events": sum(1 for row in out_events if row["variant_selector_status"] == "LOCAL_VARIANT_EVENT"),
            "terminal_program_events": len(program_event_ids),
            "record_layout_selectors": sum(row["program_card_id"] == "RECORD_LAYOUT" for row in selector_rows),
            "exact_program_cards": len(program_rows),
            "axis_counts": dict(sorted(axis_counts.items())),
        },
        "working_rule": "PARAMETER CARDS FIRST; TERMINAL WHOLE CARD SELECTS LOCAL PROGRAM; RECORD LAYOUT SELECTS TWO RELEASES",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, REGISTER_OUT, MODULE_SUMMARY_OUT, PROGRAM_DECK_OUT, AXIS_OUT, CHECK_OUT]
    summary = {
        "status": result["status"],
        "counts": result["counts"],
        "input_hashes": {path.name: sha256(path) for path in [DICT_IN, EVENT_IN, SENTENCE_IN, MODULE_IN]},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "sealed": result["sealed"],
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise AssertionError(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
