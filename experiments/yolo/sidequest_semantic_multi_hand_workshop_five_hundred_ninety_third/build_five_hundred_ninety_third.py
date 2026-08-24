#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P577 = YOLO / "sidequest_semantic_gloss_free_reconstruction_five_hundred_seventy_seventh"
P583 = YOLO / "sidequest_semantic_apprentice_phrasebook_five_hundred_eighty_third"
P587 = YOLO / "sidequest_semantic_uniform_three_line_edition_five_hundred_eighty_seventh"
P592 = YOLO / "sidequest_semantic_ten_page_workshop_architecture_five_hundred_ninety_second"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    units = read(P592 / "FIVE_HUNDRED_NINETY_SECOND_FOURTEEN_UNIT_ARCHITECTURE.tsv")
    statements = read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_ONE_HUNDRED_SIXTEEN_THREE_LINE_STATEMENTS.tsv")
    s577 = load_json(P577 / "FIVE_HUNDRED_SEVENTY_SEVENTH_BUILD_SUMMARY.json")
    s583 = load_json(P583 / "FIVE_HUNDRED_EIGHTY_THIRD_BUILD_SUMMARY.json")
    s587 = load_json(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_BUILD_SUMMARY.json")

    roles = [
        {
            "task_role": "MASTER_COMPILER",
            "minimum_skill_de": "Bildinhalt, Quelltext oder Meisterexemplar kennen; Einheit und Register waehlen",
            "input_de": "Bildplan plus praktischer oder himmlischer Inhalt",
            "output_de": "Besitzer, Reihenfolge und lokale Bedeutungsfuellung",
            "may_be_same_person_as": "CORRECTOR_FINISHER|DRAUGHTSPERSON",
            "need_not_know_de": "jede Oberflaechenvariante auswendig",
        },
        {
            "task_role": "DRAUGHTSPERSON",
            "minimum_skill_de": "Pflanze, Figur, Becken, Rad, Paneel und freien Textraum vor dem Text setzen",
            "input_de": "Layoutvorgabe des Meisters",
            "output_de": "sichtbare Besitzer und Schreibflaechen",
            "may_be_same_person_as": "MASTER_COMPILER",
            "need_not_know_de": "Prosa-Komposition oder konkreten Astro-Wert",
        },
        {
            "task_role": "PROSE_SCRIBE",
            "minimum_skill_de": "38 graphische Komponenten, 56 Rahmen, 37 gesprochene Werte und 15 haeufige Formeln",
            "input_de": "Besitzer plus kurze Arbeitsfolge",
            "output_de": "Herbal- oder Biological-Kartenfolge",
            "may_be_same_person_as": "DIAGRAM_SCRIBE",
            "need_not_know_de": "Astroetiketten semantisch zerlegen",
        },
        {
            "task_role": "DIAGRAM_SCRIBE",
            "minimum_skill_de": "13 Astro-Namensraeume unterscheiden und 142 Etiketten am gezeigten Ort exakt kopieren",
            "input_de": "Instrument, Bildplatz und lokales Exemplar",
            "output_de": "395 Gruppen in korrekter lokaler Reihenfolge",
            "may_be_same_person_as": "PROSE_SCRIBE",
            "need_not_know_de": "37 Prosa-Werte oder Himmelsnamen ausserhalb des lokalen Exemplars",
        },
        {
            "task_role": "CORRECTOR_FINISHER",
            "minimum_skill_de": "Besitzer, Kartenfolge, Zellschluss, Randfortsetzung und Instrumentreset pruefen",
            "input_de": "fertige Seite plus Meisterexemplar",
            "output_de": "korrigierte lokale Einheiten ohne falsche Joins",
            "may_be_same_person_as": "MASTER_COMPILER",
            "need_not_know_de": "eine verborgene Lautschrift oder Universalsprache",
        },
    ]

    curriculum = [
        (1, "OWNER_FIRST", 10, "auf jeder Seite zuerst Bildbesitzer und Schreibraum erkennen", "ALL"),
        (2, "GRAPHIC_COMPONENTS", s577["components"], "38 wiederkehrende graphische Bestandteile schreiben", "PROSE"),
        (3, "CARD_FRAMES", s577["frames"], "56 gelernte Kartenrahmen einsetzen", "PROSE"),
        (4, "SPOKEN_VALUES", 37, "kurze Werte wie dies, fort, Mass, Ziel, Ansatz und Handlungen sprechen", "PROSE"),
        (5, "COMMON_MACROS", s583["taught_macros"], "15 haeufige Kartenfolgen als Formeln schreiben", "PROSE"),
        (6, "SIMPLE_VARIANTS", 21, "ein Element in einer bekannten Formel einsetzen oder ersetzen", "PROSE"),
        (7, "MASTER_LONG_FORMS", 22, "lange Zweiedit- und freie Aussagen in Atemgruppen vom Exemplar kopieren", "PROSE"),
        (8, "LOCAL_CLOSE", 1, "Schluss gilt nur fuer die aktuelle Zelle, nicht fuer die physische Zeile", "PROSE"),
        (9, "ASTRO_NAMESPACES", 13, "vor jedem Astroetikett Rad, Paneel oder lokalen Sternraum ausrufen", "ASTRO"),
        (10, "ASTRO_LABELS", 142, "vollstaendige lokale Etiketten nach Bildadresse kopieren, nicht auswendig lernen", "ASTRO"),
        (11, "RESET_RULE", 1, "bei Register- oder Instrumentwechsel Besitzer und lokale Schluessel loeschen", "ALL"),
        (12, "CORRECTION", 5, "Oberflaeche, Besitzer, Reihenfolge, Schluss und Namensraum getrennt kontrollieren", "ALL"),
    ]
    curriculum_rows = [{"lesson": n, "skill": skill, "learning_items_or_examples": count, "instruction_de": text, "scope": scope} for n, skill, count, text, scope in curriculum]

    assignment_rows = []
    for unit in units:
        prose = unit["section"] != "ASTRO"
        assignment_rows.append({
            "unit_id": unit["unit_id"], "page": unit["page"], "section": unit["section"],
            "visible_groups": unit["visible_groups"], "internal_units": unit["internal_units"],
            "layout_role": "DRAUGHTSPERSON",
            "content_role": "MASTER_COMPILER",
            "copy_role": "PROSE_SCRIBE" if prose else "DIAGRAM_SCRIBE",
            "finish_role": "CORRECTOR_FINISHER",
            "apprentice_can_copy_after_basic_course": "YES",
            "master_needed_for_de": "konkrete Besitzer-/Inhaltsfuellung" if prose else "lokalen Himmelswert und richtigen Namensraum",
            "handoff_package_de": "Bildbesitzer + Arbeitsfolge + Kartenexemplar" if prose else "Instrument + Bildplatz + vollstaendige Lokaletikette",
        })

    workload_rows = [
        {"workload": "PROSE_COMMON_MACROS", "units": 73, "visible_groups": sum(int(row["event_count"]) for row in statements if row["formula_mode"] == "TAUGHT_MACRO"), "worker_level": "APPRENTICE_AFTER_LESSON_5", "copy_method_de": "Formel aus kleinem Deck"},
        {"workload": "PROSE_SIMPLE_VARIANTS", "units": 21, "visible_groups": sum(int(row["event_count"]) for row in statements if row["formula_mode"] == "SIMPLE_ONE_EDIT_VARIANT"), "worker_level": "TRAINED_PROSE_SCRIBE", "copy_method_de": "eine Einsetzung oder Ersetzung"},
        {"workload": "PROSE_LONG_OR_FREE", "units": 22, "visible_groups": sum(int(row["event_count"]) for row in statements if row["formula_mode"] in {"EXTENDED_TWO_EDIT_VARIANT", "FREE_COMPOSITION"}), "worker_level": "MASTER_OR_EXEMPLAR_SUPERVISION", "copy_method_de": "45 Atemgruppen aus Meisterexemplar"},
        {"workload": "ASTRO_LOCAL_LABELS", "units": 142, "visible_groups": 395, "worker_level": "DIAGRAM_APPRENTICE", "copy_method_de": "Bildort zeigen und Lokaletikette abschreiben"},
    ]

    errors = [
        ("OWNER_SKIPPED", "Text wird ohne Pflanzen-, Becken- oder Instrumentbesitzer gelesen", "Besitzer erneut zeigen; Inhalt nicht aus Wortform erraten"),
        ("LINE_END_EQUALS_SENTENCE", "Aussage wird am physischen Rand zu frueh beendet", "am naechsten Textlauf weiterlesen, bis die lokale Einheit endet"),
        ("GLOBAL_CLOSE", "ein Zellschluss beendet Artikel oder ganze Station", "nur aktuelle Zelle schliessen"),
        ("PROSE_VALUE_ON_ASTRO", "Astrooberflaeche wird mit den 37 Prosa-Werten zerlegt", "Astro-Namensraum ausrufen und Etikette ganz kopieren"),
        ("ASTRO_VALUE_IN_PROSE", "lokale Himmelsbeschriftung wird in eine Arbeitsaussage eingesetzt", "zum Prosa-Komponentendeck zurueckkehren"),
        ("F67_WHEELS_JOINED", "linkes und rechtes Rad werden indexweise verbunden", "beide Instrumente getrennt zuruecksetzen"),
        ("F68_F69_JOINED", "die beiden 28er-Bestaende werden gepaart", "nur lokalen Bildplatz lesen"),
        ("EDITORIAL_ORDER_AS_ROTATION", "Locusnummer wird als Kreisrichtung behandelt", "Ort zeigen; Richtung ungelesen lassen"),
        ("MEMORY_HANDOFF_INVENTED", "bestimmte Pflanze wird ohne Vorgabe einer Badstation zugeordnet", "nur thematische WHAT/HOW-Kopplung behalten"),
        ("ROLE_EQUALS_PERSON", "jede Aufgabe wird vorschnell einer bestimmten Manuskripthand zugeschrieben", "Aufgabenmodell und palaeographische Handidentitaet getrennt halten"),
    ]
    error_rows = [{"error": error, "symptom_de": symptom, "correction_de": correction} for error, symptom, correction in errors]

    staffing = [
        {"shop_model": "THREE_PERSON_MINIMUM", "people": 3, "allocation_de": "Meister zeichnet/kompiliert/korrigiert; zwei Schreiber wechseln zwischen Prosa und Diagramm", "strength_de": "klein und lehrbar", "cost_de": "Meister bleibt Engpass fuer seltene Formen und lokale Inhalte", "working_rank": 1},
        {"shop_model": "FOUR_PERSON_SPECIALIZED", "people": 4, "allocation_de": "Meister/Korrektor, Zeichner, Prosaschreiber, Diagrammschreiber", "strength_de": "weniger Registerwechsel und klare Fehlerverantwortung", "cost_de": "mehr Spezialisierung als fuer die Grundgrammatik noetig", "working_rank": 2},
        {"shop_model": "UNIVERSAL_INDIVIDUAL_SCRIBE", "people": 1, "allocation_de": "jede Hand zeichnet, komponiert, kopiert Astro und korrigiert alles", "strength_de": "keine Uebergaben", "cost_de": "unnuetig grosse Lernlast und schlechte Erklaerung fuer unterschiedliche Gewohnheiten", "working_rank": 3},
    ]

    write("FIVE_HUNDRED_NINETY_THIRD_FIVE_TASK_ROLES.tsv", roles)
    write("FIVE_HUNDRED_NINETY_THIRD_TWELVE_LESSON_CURRICULUM.tsv", curriculum_rows)
    write("FIVE_HUNDRED_NINETY_THIRD_FOURTEEN_UNIT_ASSIGNMENTS.tsv", assignment_rows)
    write("FIVE_HUNDRED_NINETY_THIRD_WORKLOAD_LEVELS.tsv", workload_rows)
    write("FIVE_HUNDRED_NINETY_THIRD_TEN_ERROR_DRILLS.tsv", error_rows)
    write("FIVE_HUNDRED_NINETY_THIRD_STAFFING_MODELS.tsv", staffing)

    summary = {
        "status": "PASS", "task_roles": len(roles), "curriculum_lessons": len(curriculum_rows),
        "assigned_units": len(assignment_rows), "assigned_visible_groups": sum(int(row["visible_groups"]) for row in assignment_rows),
        "prose_statements": len(statements), "macro_statements": s587["taught_macro"], "simple_variants": s587["simple_variant"],
        "master_supervised_statements": s587["extended_variant"] + s587["free_composition"],
        "astro_labels": 142, "astro_groups": 395, "minimum_people": 3,
        "decision": "THREE_PERSON_WORKSHOP_WITH_TASK_LOCAL_SPECIALIZATION",
    }
    (HERE / "FIVE_HUNDRED_NINETY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# Fuenfhundertdreiundneunzigste Runde: die kleine Mehrschreiberwerkstatt

## Ergebnis

Die Zehn-Seiten-Theorie braucht keine zehn Spezialisten und auch keinen Universaldecoder. Die einfachste plausible Besetzung sind **drei Menschen**:

1. ein Meister, der Inhalt, Bildbesitzer und Reihenfolge festlegt und am Ende korrigiert;
2. zwei Schreiber, die beide die gemeinsame Kopiergrundlage koennen, sich bei der Arbeit aber zwischen Prosa und Diagrammetiketten aufteilen.

Der Zeichner ist eine Aufgabe, nicht zwingend eine vierte Person. Der Meister kann die Bilder und Schreibflaechen selbst vorgeben; in einer groesseren Werkstatt kann ein eigener Zeichner dazukommen.

## Was ein Lehrling wirklich lernen muss

Fuer die Prosa braucht er 38 graphische Komponenten, 56 Rahmen und 37 kurze gesprochene Werte. Mit 15 Formeln kann er bereits {s587['taught_macro']}/116 Aussagen setzen; mit einfachen Einsetzungen weitere {s587['simple_variant']}. Nur {summary['master_supervised_statements']} lange oder freie Aussagen brauchen die 45 Atemgruppen des Meisterexemplars.

Fuer Astro lernt er nicht 395 Bedeutungen. Er lernt 13 Namensraeume und kopiert 142 vollstaendige lokale Etiketten am gezeigten Bildort. Das ist fuer einen Diagrammschreiber sogar leichter als die Prosa, solange er nicht versucht, die Etiketten mit dem Prosa-Woerterbuch zu lesen.

## Der Arbeitsgang

```text
Meister bestimmt Inhalt und lokalen Besitzer
-> Bild/Layout wird zuerst gesetzt
-> Prosaschreiber komponiert Karten ODER Diagrammschreiber kopiert Lokaletikette
-> Korrektor prueft Ort, Reihenfolge, lokalen Schluss und Registerreset
```

Die zwei Schreibmaschinen duerfen von derselben Person gelernt werden; sie werden nur nie gleichzeitig angewandt. Der harte Registerruf `HERBAL/BIOLOGICAL/ASTRO` ist der wichtigste Schutz gegen falsche Bedeutungen.

## Was dieses Modell erklaert

- mehrere Haende koennen dieselbe Grundgrammatik mit verschiedenen Schreibgewohnheiten benutzen;
- Bilder koennen vor dem Text fertig sein, weil der Besitzer vor der Kartenwahl feststeht;
- lange Prosa wird nicht an Zeilengrenzen geplant, sondern in Atemgruppen in Restflaechen gesetzt;
- Biological kann viele kurze geschlossene Zellen haben, obwohl Herbal offene Artikel benutzt;
- Astro kann voellig andere Etiketten besitzen, ohne aus einer anderen Werkstatt zu stammen;
- seltene oder schwierige Folgen muessen nicht produktiv beherrscht werden: sie werden aus dem Meisterexemplar kopiert.

## Grenze

Das ist ein Aufgabenmodell, keine Identifikation realer palaeographischer Haende. Wir sagen nicht, welche bekannte Voynich-Hand Meister, Prosa- oder Diagrammschreiber war. Die Theorie verlangt nur, dass verschiedene Personen diese Rollen ausueben konnten.

## Naechster Schritt

Als naechstes werden die sichtbaren Oberflaechenvarianten der Prosa als Schreibergewohnheiten geordnet: Welche Unterschiede veraendern nur den Kartenrahmen, welche den gesprochenen Wert, und welche muessen als echte gelernte Ausnahme bleiben?
"""
    (HERE / "FIVE_HUNDRED_NINETY_THIRD_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
