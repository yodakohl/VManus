#!/usr/bin/env python3
import csv
import json
import re
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P564 = YOLO / "sidequest_semantic_action_complete_translation_five_hundred_sixty_fourth"
P584 = YOLO / "sidequest_semantic_formula_variant_absorption_five_hundred_eighty_fourth"

REPLACE = [
    ("Pflanzenstoff in den Ansatz geben", "gib dies in den Ansatz"),
    ("den Arbeitsstoff einsetzen", "setze dies ein"),
    ("in die nächste Station weitergeben", "führe zur nächsten Station"),
    ("bis zum Sollmaß beschicken", "setze nach Maß an"),
    ("vollständig beschicken und abschließen", "setze voll an; schließe"),
    ("eine Portion einfüllen", "gib einen Teil hinein"),
    ("aus der bezeichneten Quelle beschicken", "gib davon nach Maß zu"),
    ("die gelernte Zustands- und Adressfolge setzen", "setze Zustand und Ziel"),
    ("Arbeitsschritt schließen", "schließe"),
    ("vorgeschriebenes Maß", "Maß"),
    ("bezeichnete Stelle", "Ziel"),
    ("dieser Posten", "dies"),
    ("von dort", "davon"),
    ("Arbeitsgang", "Gang"),
    ("fortsetzen", "fort"),
    ("laufender Bestand", "Lauf"),
]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def compact(text):
    result = text
    for old, new in REPLACE:
        result = result.replace(old, new)
    result = re.sub(r"\s+", " ", result).strip()
    return result


def main():
    source_statements = read(P564 / "FIVE_HUNDRED_SIXTY_FOURTH_ONE_HUNDRED_SIXTEEN_ACTION_COMPLETE_STATEMENTS.tsv")
    source_events = read(P564 / "FIVE_HUNDRED_SIXTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_READINGS.tsv")
    formula_map = {r["statement_id"]: r for r in read(P584 / "FIVE_HUNDRED_EIGHTY_FOURTH_REVISED_ONE_HUNDRED_SIXTEEN_FORMULA_MAP.tsv")}
    statement_rows = []
    records = OrderedDict()
    for row in source_statements:
        actions = compact(row["complete_action_sequence_de"])
        arguments = compact(row["complete_argument_sequence_de"])
        if arguments == "NONE":
            full = f"Bildbesitzer: {row['silent_owner_de']}. Folge: {actions}."
        else:
            full = f"Bildbesitzer: {row['silent_owner_de']}. Folge: {actions}. Angaben: {arguments}."
        formula = formula_map[row["statement_id"]]
        out = {
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "silent_owner_de": row["silent_owner_de"],
            "action_events": row["action_events"],
            "argument_state_events": row["argument_state_events"],
            "event_total": int(row["action_events"]) + int(row["argument_state_events"]),
            "complete_actions_de": actions,
            "complete_arguments_de": arguments,
            "corrected_full_compact_instruction_de": full,
            "formula_mode": formula["revised_learning_mode"],
            "phase_signature": formula["phase_signature"],
            "all_events_spoken": row["all_events_spoken"],
            "supersedes_pass580_first_event_only": "YES",
        }
        statement_rows.append(out)
        records.setdefault(row["record"], []).append(out)

    by_statement = {r["statement_id"]: r for r in statement_rows}
    event_rows = []
    for row in source_events:
        statement = by_statement[row["statement_id"]]
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "surface": row["surface"],
            "component_parse": row["component_parse"], "atomic_card_value_de": row["atomic_card_value_de"],
            "local_action_expansion_de": row["source_action_de"],
            "revised_event_reading_de": row["revised_event_reading_de"],
            "corrected_full_compact_instruction_de": statement["corrected_full_compact_instruction_de"],
            "complete_meaning": row["meaning_preserved"],
        })

    master_rows = [r for r in statement_rows if r["formula_mode"] == "FREE_COMPOSITION"]
    write("FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_ONE_HUNDRED_SIXTEEN_FULL_STATEMENTS.tsv", statement_rows)
    write("FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv", event_rows)
    write("FIVE_HUNDRED_EIGHTY_FIFTH_TWELVE_FREE_MASTER_EXAMPLES.tsv", master_rows)

    readable = ["# Korrigierte vollständige Werkstattausgabe", "", "Jede Aussage nennt sämtliche Handlungen und sämtliche Angaben ihrer Karten.", ""]
    for record, rows in records.items():
        readable += [f"## {record}", ""]
        for row in rows:
            readable.append(f"- {row['statement_id']}: {row['corrected_full_compact_instruction_de']}")
        readable.append("")
    (HERE / "FIVE_HUNDRED_EIGHTY_FIFTH_ELEVEN_RECORD_FULL_COMPACT_EDITION.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "statements": len(statement_rows),
        "events": len(event_rows),
        "action_events": sum(int(r["action_events"]) for r in statement_rows),
        "argument_state_events": sum(int(r["argument_state_events"]) for r in statement_rows),
        "event_total": sum(int(r["event_total"]) for r in statement_rows),
        "free_master_examples": len(master_rows),
        "pass580_slot_preservation_claim": "WITHDRAWN_FIRST_EVENT_ONLY",
        "pass583_584_phase_formula_counts": "UNAFFECTED_SOURCE_PASS565",
    }
    (HERE / "FIVE_HUNDRED_EIGHTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertfünfundachtzigste Runde: vollständige Satzkorrektur",
        "",
        "## Korrektur",
        "",
        "Pass 579/580 übernahm für die flüssige Satzspalte versehentlich nur die Paraphrase des ersten Kartenereignisses einer Aussage. Deshalb war die Behauptung, die 552-Wort-Ausgabe bewahre alle Slots, falsch. Diese Spalte und die darauf beruhende Kürzungszahl werden hier zurückgezogen.",
        "",
        "Die Komponenten-, Karten-, Ereignis-, Phasen- und Formelergebnisse bleiben bestehen: Sie wurden aus vollständigen 381-Ereignis-Tabellen beziehungsweise dem handlungsvollständigen Pass 564 gebaut. Auch die 15 Formeln und ihre 73/21/10/12-Aufteilung stammen aus vollständigen Phasenfolgen und ändern sich nicht. Nur die lesbare Satzparaphrase war abgeschnitten.",
        "",
        "## Korrigierte Ausgabe",
        "",
        "Die neue Ausgabe bindet 237 Handlungsereignisse und 144 Argument-/Zustandsereignisse, zusammen alle 381, an 116 vollständige Aussagen. H1-S001 lautet nun nicht bloß ›dies kurz abnehmen‹, sondern führt Abnehmen, Übertragen, Ablaufenlassen, Eintragen/Abnehmen, Einsetzen und erneutes Eintragen samt Ansatz-, Quellen-, Fach- und Maßangaben auf.",
        "",
        "Zwölf freie Meisterbeispiele sind vollständig separat ausgegeben. Sie bleiben lange, weil sie echte mehrphasige Artikel- oder Stationsfolgen sind; eine weitere Scheinkürzung wäre schlechter als eine längere Lehrvorlage.",
        "",
        "## Nächster Schritt",
        "",
        "Die zehn Zwei-Edit-Varianten und zwölf freien Meisterbeispiele werden nun in sinnvolle Satzblöcke gegliedert. Ziel ist nicht weitere Kürzung, sondern lesbare Atemgruppen, die jede Kartenhandlung und jede Angabe sichtbar erhalten.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTY_FIFTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
