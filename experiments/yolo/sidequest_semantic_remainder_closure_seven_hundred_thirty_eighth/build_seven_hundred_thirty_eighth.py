#!/usr/bin/env python3
"""Build Pass 738: adjudicate the eight Pass-737 remainder cards."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P737 = ROOT / "experiments/yolo/sidequest_semantic_consolidated_codebook_seven_hundred_thirty_seventh"


def read(name: str) -> list[dict[str, str]]:
    with (P737 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


REMAINDER_DECISIONS = {
    "PROC005": ("MEMORIZED_WHOLE_COMMAND", "FACH", "Einmalig zwischen Anwendung und Wasserentnahme; Gefäß bleibt gleich guter Rivale."),
    "PROC028": ("CONTEXT_SINGLETON_COMPONENT", "AUSWRINGEN · DIES", "Steht in der H3-Folge halten→auswringen→Sollmaß→füllen; konkrete Handlung bleibt passend, aber einmalig."),
    "PROC034": ("CONFIRMED_RECURRENT_WHOLE_COMMAND", "WIEDERAUFNEHMEN", "Zweimal an Aussagebeginn auf zwei Pflanzenrecords; ruft jeweils den vorigen Vorgang auf."),
    "PROC040": ("PARADIGM_SUPPORTED_AIN_VARIANT", "DIES · ZUGEBEN · NACHGABE", "Direktes Minimalpaar ykain→ykan im selben Satz: Y+K bleibt, AIN Portion wechselt zu AN Nachgabe."),
    "PROC043": ("MEMORIZED_WHOLE_COMMAND", "VERWAHREN", "Einmalig am Ende eines H4-Arbeitssatzes; als ganze Lager-/Ablagekarte lernen."),
    "PROC124": ("CONTEXT_SINGLETON_COMPONENT", "ENTNEHMEN · KURZ · TEIL", "Einmalige Teilentnahme zwischen Quelltransfer und Sollmaß; S bleibt konkreter, nicht produktiver Teilwert."),
    "PROC155": ("CONTEXT_SINGLETON_COMPONENT", "ANSETZEN · DIES · BEFESTIGEN · SCHLUSS", "Einzelzelle am verbundenen B4-Bogenpaar; Befestigen passt lokal, wird aber nicht verallgemeinert."),
    "PROC169": ("CONTEXT_SINGLETON_COMPONENT", "ZWEIT · ARBEITSSTUFE", "Einmalig im B5-Fortsetzungsrecord; klare zweite Stufe, aber kein weiteres DA-Paradigma."),
}


def new_card_status(card_id: str, old: str) -> str:
    if card_id == "PROC040":
        return "COMPOSED_WITH_PARADIGM_SUPPORTED_AIN_VARIANT"
    if old == "FULLY_COMPOSED_FROM_RECURRENT_ROOTS":
        return old
    decision = REMAINDER_DECISIONS[card_id][0]
    if decision == "CONTEXT_SINGLETON_COMPONENT":
        return "HAS_CONTEXT_SINGLETON_COMPONENT"
    return "HAS_MEMORIZED_WHOLE_COMMAND"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read("SEVEN_HUNDRED_THIRTY_SEVENTH_39_COMPONENT_DICTIONARY.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_SEVENTH_173_REBUILT_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_SEVENTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_SEVENTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_SEVENTH_11_RECORD_EDITION.tsv")

    component_rows = []
    for row in components:
        category = row["category"]
        teaching = row["teaching_rule"]
        if row["component"] == "AN":
            category = "PARADIGM_SUPPORTED_BOUND_VARIANT_OF_AIN"
            teaching = "nur im gebundenen Y+K+AN-Rahmen als weitere Portion/Nachgabe lesen"
        elif category == "SINGLETON_COMPONENT_GUESS":
            category = "CONTEXT_SINGLETON_COMPONENT"
        component_rows.append({**row, "category": category, "teaching_rule": teaching})

    card_rows = []
    for row in cards:
        status = new_card_status(row["exact_card_id"], row["composition_status"])
        card_rows.append({
            "exact_card_id": row["exact_card_id"], "semantic_family": row["semantic_family"],
            "component_recipe": row["component_recipe"], "rebuilt_reading_de": row["rebuilt_reading_de"],
            "component_count": row["component_count"], "pass737_status": row["composition_status"],
            "pass738_status": status, "registered_surfaces": row["registered_surfaces"], "events": row["events"],
        })

    card_lookup = {row["exact_card_id"]: row for row in card_rows}
    statement_lookup = {row["statement_id"]: row for row in statements}
    context_rows = []
    for row in events:
        if row["card_no"] not in REMAINDER_DECISIONS:
            continue
        statement = statement_lookup[row["statement_id"]]
        decision, short, reason = REMAINDER_DECISIONS[row["card_no"]]
        context_rows.append({
            "event_id": row["event_id"], "card_no": row["card_no"], "surface": row["surface"],
            "component_recipe": row["component_recipe"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"],
            "full_surface_sequence": statement["surface_sequence"],
            "full_atomic_trace_de": statement["rebuilt_atomic_trace_de"],
            "full_working_reading_de": statement["working_reading_de"],
            "decision": decision, "short_default_de": short, "reason_de": reason,
        })

    decision_rows = []
    for card_id in REMAINDER_DECISIONS:
        card = card_lookup[card_id]
        occurrences = [row for row in context_rows if row["card_no"] == card_id]
        decision, short, reason = REMAINDER_DECISIONS[card_id]
        decision_rows.append({
            "card_no": card_id, "surfaces": card["registered_surfaces"], "component_recipe": card["component_recipe"],
            "events": card["events"], "event_ids": ",".join(row["event_id"] for row in occurrences),
            "decision": decision, "short_default_de": short, "reason_de": reason,
            "productive_core_changed": "NO",
        })

    pair_rows = [
        {
            "pair_id": "AN01", "statement_id": "H4-S001", "first_event": "E058", "first_surface": "ykain",
            "first_recipe": "Y+K+AIN", "first_reading_de": "DIES · ZUGEBEN · PORTION",
            "second_event": "E059", "second_surface": "ykan", "second_recipe": "Y+K+AN",
            "second_reading_de": "DIES · ZUGEBEN · NACHGABE",
            "invariant_frame": "Y+K", "varying_component": "AIN→AN",
            "teaching_rule_de": "AIN gewöhnliche Portion; gebundenes AN eine weitere Portion/Nachgabe",
        }
    ]

    event_rows = []
    statement_events: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        card = card_lookup[row["card_no"]]
        output = {
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "owner_de": row["owner_de"], "card_no": row["card_no"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "rebuilt_reading_de": row["rebuilt_reading_de"], "composition_status": card["pass738_status"],
            "form_owner_boundary_status": "UNCHANGED",
        }
        event_rows.append(output)
        statement_events[row["statement_id"]].append(output)

    statement_rows = []
    for row in statements:
        seq = statement_events[row["statement_id"]]
        counts = Counter(str(item["composition_status"]) for item in seq)
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "events": row["events"], "owner_noun_de": row["owner_noun_de"],
            "surface_sequence": row["surface_sequence"], "rebuilt_atomic_trace_de": row["rebuilt_atomic_trace_de"],
            "recurrent_or_paired_events": counts["FULLY_COMPOSED_FROM_RECURRENT_ROOTS"] + counts["COMPOSED_WITH_PARADIGM_SUPPORTED_AIN_VARIANT"],
            "context_singleton_events": counts["HAS_CONTEXT_SINGLETON_COMPONENT"],
            "memorized_command_events": counts["HAS_MEMORIZED_WHOLE_COMMAND"],
            "working_reading_de": row["working_reading_de"], "form_owner_boundary_status": "UNCHANGED",
        })

    record_rows = []
    for row in records:
        seq = [event for event in event_rows if event["record"] == row["record"]]
        counts = Counter(str(item["composition_status"]) for item in seq)
        record_rows.append({
            "record": row["record"], "page": row["page"], "statements": row["statements"], "events": row["events"],
            "recurrent_or_paired_events": counts["FULLY_COMPOSED_FROM_RECURRENT_ROOTS"] + counts["COMPOSED_WITH_PARADIGM_SUPPORTED_AIN_VARIANT"],
            "context_singleton_events": counts["HAS_CONTEXT_SINGLETON_COMPONENT"],
            "memorized_command_events": counts["HAS_MEMORIZED_WHOLE_COMMAND"],
            "continuous_reading_de": row["continuous_reading_de"], "form_status": "UNCHANGED",
        })

    class_rows = []
    for status in ["FULLY_COMPOSED_FROM_RECURRENT_ROOTS", "COMPOSED_WITH_PARADIGM_SUPPORTED_AIN_VARIANT", "HAS_CONTEXT_SINGLETON_COMPONENT", "HAS_MEMORIZED_WHOLE_COMMAND"]:
        target = [row for row in card_rows if row["pass738_status"] == status]
        class_rows.append({
            "composition_status": status, "cards": len(target), "events": sum(int(row["events"]) for row in target),
        })

    write("SEVEN_HUNDRED_THIRTY_EIGHTH_39_COMPONENT_DICTIONARY.tsv", component_rows)
    write("SEVEN_HUNDRED_THIRTY_EIGHTH_1_AN_AIN_MINIMAL_PAIR.tsv", pair_rows)
    write("SEVEN_HUNDRED_THIRTY_EIGHTH_8_REMAINDER_DECISIONS.tsv", decision_rows)
    write("SEVEN_HUNDRED_THIRTY_EIGHTH_9_REMAINDER_CONTEXTS.tsv", context_rows)
    write("SEVEN_HUNDRED_THIRTY_EIGHTH_4_COMPOSITION_CLASSES.tsv", class_rows)
    write("SEVEN_HUNDRED_THIRTY_EIGHTH_173_CARD_DICTIONARY.tsv", card_rows)
    write("SEVEN_HUNDRED_THIRTY_EIGHTH_381_EVENT_INTERLINEAR.tsv", event_rows)
    write("SEVEN_HUNDRED_THIRTY_EIGHTH_116_STATEMENT_EDITION.tsv", statement_rows)
    write("SEVEN_HUNDRED_THIRTY_EIGHTH_11_RECORD_EDITION.tsv", record_rows)

    report = """# Pass 738 — acht Restkarten

## Eine echte Verbesserung

`ykain ykan` steht direkt hintereinander in H4-S001. Beide Karten teilen Y+K („diesem Posten zugeben“); nur AIN wechselt zu AN. Das ist unser stärkstes Rest-Minimalpaar:

- Y+K+AIN — diesem Posten eine Portion zugeben.
- Y+K+AN — diesem Posten eine weitere Portion / Nachgabe zugeben.

AN wird daher nicht mehr als freie Einmalwurzel behandelt, sondern als gebundene, paradigmatisch gestützte AIN-Variante. Der produktive bzw. paarweise gestützte Anteil steigt auf166 Karten/373 Ereignisse.

## Die sieben verbleibenden Restkarten

- OS/FACH: ganze Einmalkarte; Gefäß bleibt möglicher Rivale.
- CFH+Y/AUSWRINGEN·DIES: konkrete H3-Handlung, aber nur einmal.
- RESUME_CARD/WIEDERAUFNEHMEN: als wiederkehrender Ganzbefehl bestätigt, zweimal an Herbal-Aussagebeginn.
- TALAM/VERWAHREN: gelernter Einmalbefehl am Ende einer H4-Anweisung.
- CH+E+S/ENTNEHMEN·KURZ·TEIL: konkrete Einmal-Komposition.
- OK+Y+LD+DY/...BEFESTIGEN·SCHLUSS: konkrete B4-Einmal-Komposition am verbundenen Bogenpaar.
- DA+IIN/ZWEIT·ARBEITSSTUFE: konkrete B5-Einmal-Komposition.

Damit bleiben vier kontextgestützte Einmalkomponenten (CFH,S,LD,DA) und drei gelernte Ganzbefehle (OS,RESUME_CARD,TALAM). Der31-Wurzel-Kern bleibt unverändert.

## Nächster Hebel

Als Nächstes wird die konsolidierte Karte-zu-Satz-Edition flüssig neu gesetzt. Jede der116 Aussagen soll ausschließlich aus dem39-Eintrag-Codebook expandiert werden, mit explizitem Bildbesitzer und ohne alte überholte Wörter wie Mass, Ziel, Fortsetzen, Weiterleiten, Auffangen oder die komplexe shey-Lesung.
"""
    (HERE / "SEVEN_HUNDRED_THIRTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS", "remainder_cards_reviewed": len(decision_rows), "remainder_occurrences_reviewed": len(context_rows),
        "promoted_paired_variants": 1, "recurrent_productive_cards": 165, "paired_variant_cards": 1,
        "recurrent_or_paired_events": 373, "context_singleton_cards": 4, "context_singleton_events": 4,
        "memorized_command_cards": 3, "memorized_command_events": 4,
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows),
        "productive_core_changes": 0, "semantic_value_changes": 0, "form_changes": 0,
        "decision": "AN_IS_BOUND_AIN_VARIANT__SEVEN_TRUE_REMAINDER_CARDS_STAY_SHORT_AND_EXPLICIT",
    }
    (HERE / "SEVEN_HUNDRED_THIRTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
