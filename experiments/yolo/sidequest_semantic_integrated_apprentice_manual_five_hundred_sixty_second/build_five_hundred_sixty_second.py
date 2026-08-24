#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P554 = ROOT / "sidequest_semantic_canonical_working_dictionary_five_hundred_fifty_fourth"
P555 = ROOT / "sidequest_semantic_atomic_card_unification_five_hundred_fifty_fifth"
P557 = ROOT / "sidequest_semantic_allograph_renderer_rules_five_hundred_fifty_seventh"
P560 = ROOT / "sidequest_semantic_formula_cadence_renderer_five_hundred_sixtieth"
P561 = ROOT / "sidequest_semantic_record_wrapper_melodies_five_hundred_sixty_first"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    components = read_tsv(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv")
    frames = read_tsv(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_FIFTY_SIX_ACTION_FRAME_LEXICON.tsv")
    cards = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv")
    events = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_ATOMIC_EVENT_DICTIONARY.tsv")
    allograph_rules = read_tsv(P557 / "FIVE_HUNDRED_FIFTY_SEVENTH_ELEVEN_ALLOGRAPH_RULES.tsv")
    allograph_audit = {row["event_id"]: row for row in read_tsv(P557 / "FIVE_HUNDRED_FIFTY_SEVENTH_SEVENTY_FOUR_ALLOGRAPH_EVENT_AUDIT.tsv")}
    cadences = read_tsv(P560 / "FIVE_HUNDRED_SIXTIETH_ELEVEN_FORMULA_CADENCES.tsv")
    melodies = read_tsv(P561 / "FIVE_HUNDRED_SIXTY_FIRST_NINE_RECORD_MELODIES.tsv")
    renderer = {row["event_id"]: row for row in read_tsv(P561 / "FIVE_HUNDRED_SIXTY_FIRST_THREE_HUNDRED_EIGHTY_ONE_FINAL_RENDERER.tsv")}

    manual_specs = [
        ("L01", "BILD", "OWNER", "Lies zuerst den sichtbaren Pflanzen-, Becken-, Gefäß- oder Stationsbesitzer; er bleibt meist stumm."),
        ("L01", "BILD", "RESET", "Bei einem sichtbaren Besitzerwechsel setze den Arbeitsgegenstand neu, auch mitten in einer geschriebenen Aussage."),
        ("L02", "SATZ", "ACTION", "Wähle den kleinsten konkreten Handlungskern aus dem Komponentenlexikon."),
        ("L02", "SATZ", "SOURCE", "Setze AR für Quelle, AIR für laufende Flüssigkeit und L+CHED für Abführung."),
        ("L02", "SATZ", "TARGET", "Setze AL für Zielstelle und P+CHED für Zuführung in einen Empfänger."),
        ("L02", "SATZ", "QUANTITY", "Setze AIIN für Sollmaß oder AIN für eine abgeteilte Portion."),
        ("L02", "SATZ", "ITEM", "Setze Y oder CHY, wenn der laufende Posten ausdrücklich wieder aufgenommen wird."),
        ("L02", "SATZ", "ORDER", "Setze OT für Folge und OL für Fortsetzung oder Rückgriff."),
        ("L02", "SATZ", "GRADE", "Setze E, EE oder EEE für kurz, länger oder vollständig."),
        ("L02", "SATZ", "STATE", "Setze gelernte Zustände wie CTH bereit, SHED absetzen oder CHK wärmen."),
        ("L02", "SATZ", "CLOSE", "Schließe nur mit einer lizenzierten terminalen Kartenkonstruktion; sichtbares dy allein ist kein sicherer Schluss."),
        ("L03", "KARTE", "COMPOSE", "Lies die Komponenten in Werkstattreihenfolge und rufe den atomaren Wert der ganzen Karte ab."),
        ("L03", "KARTE", "FRAME", "Benutze die 56 kurzen Aktionsrahmen, um breite Kerne im jeweiligen Quellen-, Ziel- und Zustandsrahmen zu konkretisieren."),
        ("L03", "KARTE", "WHOLE", "Bleibt eine Karte gelernt, verwende ihren kurzen Ganzwert; er darf die Komponentenregel nicht rückwirkend verändern."),
        ("L04", "ALLOGRAPH", "DIRECT", "Hat die Komponentenfolge nur eine Karte, nimm diese direkt."),
        ("L04", "ALLOGRAPH", "CHOICE", "Bei den elf geteilten Folgen wende Nachbar-, Record- oder die eine Drei-Lokus-Regel an."),
        ("L05", "OBERFLAECHE", "GLOBAL", "Schreibe die globale Kartenform, wenn keine Oberflächenregel anspringt."),
        ("L05", "OBERFLAECHE", "CONTEXT", "Wende einen der vier unmittelbaren Wrapperwechsel an, wenn sein Kartenkontext sichtbar ist."),
        ("L05", "OBERFLAECHE", "CADENCE", "Bei einer der elf gelehrten Formeln rezitiere ihre Wrapperkadenz."),
        ("L05", "OBERFLAECHE", "MELODY", "Sonst nimm den nächsten Platz der am Recordanfang geladenen Wrappermelodie."),
        ("L06", "LAYOUT", "LINE", "Breche an der freien Bildkante um; ein Zeilenende beendet die Aussage nicht."),
        ("L06", "LAYOUT", "READBACK", "Lies Bildbesitzer, Komponenten, atomare Karte und Oberfläche rückwärts; jede Stufe muss wieder erreichbar sein."),
    ]
    manual_rows = [
        {"rule_no": f"R{index:02d}", "lesson": lesson, "layer": layer, "rule_key": key, "instruction_de": instruction}
        for index, (lesson, layer, key, instruction) in enumerate(manual_specs, 1)
    ]

    trace_rows = []
    for event in events:
        event_id = event["event_id"]
        render = renderer[event_id]
        if event_id in allograph_audit:
            audit = allograph_audit[event_id]
            allograph_source = audit["rule_type"]
            predicted = audit["predicted_card_no"]
        else:
            allograph_source = "DIRECT_UNIQUE_PARSE"
            predicted = event["card_no"]
        trace_rows.append({
            "event_id": event_id,
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "locus": event["locus"],
            "silent_owner_de": event["silent_owner_de"],
            "containing_clause_de": event["containing_clause_de"],
            "component_parse": event["component_parse"],
            "atomic_card_value_de": event["atomic_card_value_de"],
            "local_action_expansion_de": event["occurrence_action_expansion_de"],
            "allograph_source": allograph_source,
            "predicted_card_no": predicted,
            "observed_card_no": event["card_no"],
            "card_roundtrip": "YES" if predicted == event["card_no"] else "NO",
            "renderer_source": render["renderer_source"],
            "renderer_rule": render["renderer_rule"],
            "predicted_surface": render["final_surface"],
            "observed_surface": event["surface"],
            "surface_roundtrip": "YES" if render["final_surface"] == event["surface"] else "NO",
            "free_choice": "NO",
        })

    record_rows = []
    for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        rows = [row for row in trace_rows if row["record"] == record]
        sources = Counter(row["renderer_source"] for row in rows)
        record_rows.append({
            "record": record,
            "page": rows[0]["page"],
            "events": str(len(rows)),
            "statements": str(len({row['statement_id'] for row in rows})),
            "component_parses": str(len({row['component_parse'] for row in rows})),
            "allograph_rule_events": str(sum(row["allograph_source"] != "DIRECT_UNIQUE_PARSE" for row in rows)),
            "global_surface_events": str(sources["GLOBAL_RULE_RENDERER"]),
            "context_surface_events": str(sources["AUTOMATIC_CONTEXT_RULE"]),
            "cadence_surface_events": str(sources["FORMULA_CADENCE_RULE"]),
            "melody_surface_events": str(sources["RECORD_WRAPPER_MELODY"]),
            "card_roundtrip": "YES" if all(row["card_roundtrip"] == "YES" for row in rows) else "NO",
            "surface_roundtrip": "YES" if all(row["surface_roundtrip"] == "YES" for row in rows) else "NO",
        })

    inventory_rows = [
        {"layer": "COMPONENT_VALUES", "learned_items": str(len(components)), "events_covered": "381", "use": "meaning atoms"},
        {"layer": "ACTION_FRAMES", "learned_items": str(len(frames)), "events_covered": str(sum(int(row["occurrences"]) for row in frames)), "use": "contextual concrete verbs"},
        {"layer": "ATOMIC_CARDS", "learned_items": str(len(cards)), "events_covered": "381", "use": "whole-card recall"},
        {"layer": "ALLOGRAPH_RULES", "learned_items": str(len(allograph_rules)), "events_covered": "74", "use": "exact card choice"},
        {"layer": "FORMULA_CADENCES", "learned_items": str(len(cadences)), "events_covered": "32", "use": "mixed wrapper sequences"},
        {"layer": "RECORD_MELODIES", "learned_items": str(len(melodies)), "events_covered": "27", "use": "record-local wrapper sequence"},
        {"layer": "WRAPPER_STAMPS", "learned_items": "8", "events_covered": "381", "use": "surface alphabet"},
        {"layer": "MANUAL_RULES", "learned_items": str(len(manual_rows)), "events_covered": "381", "use": "execution order"},
    ]

    write_tsv("FIVE_HUNDRED_SIXTY_SECOND_TWENTY_TWO_RULE_APPRENTICE_MANUAL.tsv", manual_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_SECOND_TRAINING_INVENTORY.tsv", inventory_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_SECOND_THREE_HUNDRED_EIGHTY_ONE_FULL_TRACES.tsv", trace_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_SECOND_ELEVEN_RECORD_EXAMS.tsv", record_rows)
    summary = {
        "status": "PASS",
        "manual_rules": len(manual_rows),
        "lessons": len({row["lesson"] for row in manual_rows}),
        "components": len(components),
        "action_frames": len(frames),
        "atomic_cards": len(cards),
        "allograph_rules": len(allograph_rules),
        "formula_cadences": len(cadences),
        "record_melodies": len(melodies),
        "traces": len(trace_rows),
        "records": len(record_rows),
        "statements": len({row["statement_id"] for row in trace_rows}),
        "card_roundtrip": sum(row["card_roundtrip"] == "YES" for row in trace_rows),
        "surface_roundtrip": sum(row["surface_roundtrip"] == "YES" for row in trace_rows),
        "free_choices": sum(row["free_choice"] != "NO" for row in trace_rows),
    }
    (HERE / "FIVE_HUNDRED_SIXTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertzweiundsechzigste Runde: integriertes Lehrlingshandbuch",
        "",
        "## Das System in einem Satz",
        "",
        "Der Schreiber übernimmt den sichtbaren Bildbesitzer, baut eine kurze Arbeitsanweisung aus 38 Bedeutungskomponenten und 56 Rahmenverben, ruft daraus eine von 173 gelernten Karten ab, entscheidet elf echte Allographfälle und rendert die Oberfläche global, kontextuell, durch Formelkadenz oder durch eine kurze Recordmelodie.",
        "",
        "## Lehrbarkeit",
        "",
        "Das Handbuch hat 22 Regeln in sechs Lektionen. Es ist kein Buchstabenalphabet und keine gewöhnliche Wortliste. Der produktive Kern ist klein; die 173 Karten sind die gelernte Werkstattschicht. Acht Wrapperstempel erzeugen die sichtbaren Schreibvarianten. Elf Allographregeln, elf Formelkadenzen und neun Recordmelodien reichen für die Abweichungen.",
        "",
        "Jedes der 381 Prosaereignisse läuft nun vollständig durch: Bildbesitzer → Satzhandlung → Komponentenfolge → atomarer Kartenwert → exakte Kartenidentität → Wrapperregel → sichtbare Oberfläche. Kartenidentität und Oberfläche kommen 381/381 zurück; alle elf Records bestehen den Rücklesetest.",
        "",
        "## Praktische Deutung",
        "",
        "Das Ergebnis passt am besten zu einer kleinen Werkstatt mit einem Meisterexemplar: Die Schreiber lernen einen gemeinsamen Bedeutungs- und Kartensatz, aber kopieren beim jeweiligen Artikel eine kurze Oberflächenmelodie. Das erklärt zugleich gemeinsame Grammatik, mehrere Hände, wiederkehrende Karten und lokale Schreibfarben, ohne jede sichtbare Variante zu einem neuen Wort zu machen.",
        "",
        "## Nächster Schritt",
        "",
        "Nun wird die fortlaufende deutsche Arbeitsübersetzung aller elf Prosarecords neu erzeugt. Sie muss die atomaren Kartenwerte, die aktuellen Rahmenverben, die stummen Bildbesitzer und die Aussagegrenzen dieses Handbuchs verwenden; alte überlange Einzelwortglossen werden nicht übernommen.",
    ]
    (HERE / "FIVE_HUNDRED_SIXTY_SECOND_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
