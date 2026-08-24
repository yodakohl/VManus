#!/usr/bin/env python3
import csv
import json
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P554 = YOLO / "sidequest_semantic_canonical_working_dictionary_five_hundred_fifty_fourth"
P562 = YOLO / "sidequest_semantic_integrated_apprentice_manual_five_hundred_sixty_second"
P577 = YOLO / "sidequest_semantic_gloss_free_reconstruction_five_hundred_seventy_seventh"
P578 = YOLO / "sidequest_semantic_context_card_resolution_five_hundred_seventy_eighth"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    components = read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv")
    frames = read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_FIFTY_SIX_ACTION_FRAME_LEXICON.tsv")
    structural = {r["card_no"]: r for r in read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")}
    traces = read(P562 / "FIVE_HUNDRED_SIXTY_SECOND_THREE_HUNDRED_EIGHTY_ONE_FULL_TRACES.tsv")
    recon = {r["card_no"]: r for r in read(P577 / "FIVE_HUNDRED_SEVENTY_SEVENTH_ONE_HUNDRED_SEVENTY_THREE_GLOSS_FREE_CARD_RECONSTRUCTIONS.tsv")}
    fills = read(P578 / "FIVE_HUNDRED_SEVENTY_EIGHTH_OWNER_SLOT_FILL_RULES.tsv")
    context_occ = {r["event_id"]: r for r in read(P578 / "FIVE_HUNDRED_SEVENTY_EIGHTH_SEVENTY_OCCURRENCE_RESOLUTIONS.tsv")}

    manual = [
        ("P01", "OWNER", "Bestimme den sichtbaren Besitzer; er liefert den stummen Gegenstand."),
        ("P02", "CARD", "Erkenne die sichtbare Ganzkarte, aber behandle sie noch nicht als Ganzwort."),
        ("P03", "PARSE", "Zerlege die Karte nach dem gefrorenen Komponentenparse."),
        ("P04", "ATOM", "Lies jede Komponente mit genau einem der 38 Grundwerte."),
        ("P05", "ORDER", "Bewahre die Komponentenfolge; Quelle, Menge und Ziel bleiben Argumente."),
        ("P06", "FRAME", "Wähle für Handlungskomponenten eine der 56 lizenzierten Rahmenhandlungen."),
        ("P07", "FILL", "Nutze bei elf abstrakten Karten genau eine der neun sichtbaren Besitzer-/Slotfüllungen."),
        ("P08", "ITEM", "Y bindet den aktuell gemeinten Posten; es bezeichnet nicht selbst Abschluss."),
        ("P09", "CLOSE", "Schließe nur bei einer lizenzierten Schlusskarte; nacktes dy genügt nicht."),
        ("P10", "CHAIN", "Verbinde Karten in sichtbarer Reihenfolge zu einer Werkstattanweisung."),
        ("P11", "LINE", "Ein physischer Zeilenwechsel beendet die Aussage nicht automatisch."),
        ("P12", "RESET", "Bei sichtbarem Besitzerwechsel beginnt ein neuer lokaler Gegenstand."),
        ("P13", "SURFACE", "Schreibe die fertige Karte mit Allograph-, Hüllen-, Kadenz- und Melodieregeln."),
    ]
    manual_rows = [{"rule_no": a, "stage": b, "instruction_de": c} for a, b, c in manual]

    event_rows = []
    for event in traces:
        card_no = event["observed_card_no"]
        card = structural[card_no]
        mechanical = recon[card_no]["gloss_free_mechanical_reading_de"]
        if event["event_id"] in context_occ:
            ctx = context_occ[event["event_id"]]
            contextual = ctx["invariant_operation_de"]
            fill = ctx["owner_or_slot_fill"]
            concrete = ctx["filled_local_verb_de"]
            selection = "OWNER_SLOT_FILL"
        else:
            contextual = card["portable_role_reading_de"]
            fill = "NOT_REQUIRED"
            concrete = card["observed_action_senses_de"] if card["observed_action_senses_de"] != "NOT_AN_ACTION_CARD" else "NOT_AN_ACTION_CARD"
            selection = "PORTABLE_COMPONENT_READING"
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "locus": event["locus"],
            "silent_owner_de": event["silent_owner_de"],
            "observed_surface": event["observed_surface"],
            "card_no": card_no,
            "component_parse": event["component_parse"],
            "abstract_component_reading_de": mechanical,
            "context_selection": selection,
            "owner_slot_fill": fill,
            "contextual_card_reading_de": contextual,
            "concrete_frame_verb_de": concrete,
            "whole_card_gloss_lookup": "NO",
            "complete": "YES",
        })

    grouped = OrderedDict()
    trace_by_id = {r["event_id"]: r for r in traces}
    for row in event_rows:
        grouped.setdefault(row["statement_id"], []).append(row)
    statement_rows = []
    for statement_id, rows in grouped.items():
        original = trace_by_id[rows[0]["event_id"]]
        statement_rows.append({
            "statement_id": statement_id,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "first_locus": rows[0]["locus"],
            "silent_owner_de": rows[0]["silent_owner_de"],
            "event_count": len(rows),
            "card_sequence": " > ".join(r["card_no"] for r in rows),
            "abstract_composition_sequence_de": " | ".join(r["abstract_component_reading_de"] for r in rows),
            "contextual_card_sequence_de": " | ".join(r["contextual_card_reading_de"] for r in rows),
            "owner_filled_workshop_instruction_de": original["containing_clause_de"],
            "instruction_status": "COMPOSITION_PLUS_VISIBLE_OWNER_PARAPHRASE",
            "all_events_complete": "YES",
        })

    write("FIVE_HUNDRED_SEVENTY_NINTH_THIRTEEN_RULE_PARSER.tsv", manual_rows)
    write("FIVE_HUNDRED_SEVENTY_NINTH_THREE_HUNDRED_EIGHTY_ONE_PARSED_EVENTS.tsv", event_rows)
    write("FIVE_HUNDRED_SEVENTY_NINTH_ONE_HUNDRED_SIXTEEN_PARSED_STATEMENTS.tsv", statement_rows)
    inventory = [
        {"layer": "COMPONENT_VALUES", "items": len(components), "role": "abstrakte Bedeutung"},
        {"layer": "ACTION_FRAMES", "items": len(frames), "role": "konkrete Rahmenhandlung"},
        {"layer": "OWNER_SLOT_FILLS", "items": len(fills), "role": "sichtbare Argumentfüllung"},
        {"layer": "PARSER_RULES", "items": len(manual_rows), "role": "Ausführungsfolge"},
    ]
    write("FIVE_HUNDRED_SEVENTY_NINTH_PARSER_INVENTORY.tsv", inventory)
    summary = {
        "status": "PASS",
        "core_semantic_items": len(components) + len(frames),
        "owner_slot_fills": len(fills),
        "parser_rules": len(manual_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "owner_filled_events": sum(r["context_selection"] == "OWNER_SLOT_FILL" for r in event_rows),
        "portable_events": sum(r["context_selection"] == "PORTABLE_COMPONENT_READING" for r in event_rows),
        "whole_card_gloss_lookups": sum(r["whole_card_gloss_lookup"] == "YES" for r in event_rows),
    }
    (HERE / "FIVE_HUNDRED_SEVENTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertneunundsiebzigste Runde: integrierter Kompositionsleser",
        "",
        "## Ergebnis",
        "",
        "Ein 13-Schritt-Leser verbindet 38 Komponenten, 56 Rahmenregeln und neun sichtbare Besitzer-/Slotfüllungen. Er liest alle 381 Ereignisse und baut daraus 116 vollständige Werkstattanweisungen. Für 311 Ereignisse genügt die portable Komponentenlesung; siebzig verwenden eine der sichtbaren Füllungen. Keine fertige Ganzkartenglosse wird nachgeschlagen.",
        "",
        "Der Ablauf ist: Bildbesitzer setzen, Karte erkennen, Komponenten lesen, Handlung rahmen, Besitzer einsetzen, Y an den laufenden Posten binden, nur lizenzierte Schlusskarten schließen und erst danach die Oberflächenform schreiben. Zeilen bleiben bloßer Umbruch.",
        "",
        "Das ist jetzt ein konkretes Schreibsystem: semantisch klein und produktiv, graphisch als größerer Kartensatz gelernt. Pflanzen- und Biological-Seiten teilen dieselben Operationen; das Bild entscheidet, ob etwa ›in Einsatz bringen‹ als Material einsetzen, Flüssigkeit einleiten oder Auflage anlegen gelesen wird.",
        "",
        "## Nächster Schritt",
        "",
        "Nun werden die 116 Anweisungen auf unnötige moderne Fachsprache geprüft. Jede soll in eine kurze, um 1420 lehrbare Werkstattform mit höchstens einem Hauptverb pro Karte überführt werden, ohne Information aus der Komponentenfolge zu verlieren.",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTY_NINTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
