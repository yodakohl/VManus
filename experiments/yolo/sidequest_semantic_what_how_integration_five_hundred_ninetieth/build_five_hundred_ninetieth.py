#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P565 = YOLO / "sidequest_semantic_workshop_recipe_macros_five_hundred_sixty_fifth"
P574 = YOLO / "sidequest_semantic_cross_section_portable_cards_five_hundred_seventy_fourth"

HANDOFF_CLASSES = {
    "PORTABLE_QUANTITY", "PORTABLE_MEASURED_ACTION", "PORTABLE_STATE",
    "PORTABLE_PREPARATION", "PORTABLE_PREPARATION_ORDER", "PORTABLE_TARGET_ACTION",
    "PORTABLE_HOLD", "PORTABLE_THERMAL",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    portable = read(P574 / "FIVE_HUNDRED_SEVENTY_FOURTH_SEVENTEEN_PORTABLE_CARDS.tsv")
    phase_events = read(P565 / "FIVE_HUNDRED_SIXTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_PHASE_EVENTS.tsv")
    bridge_rows = []
    for row in portable:
        capable = row["portable_function_class"] in HANDOFF_CLASSES
        bridge_rows.append({
            **row,
            "integration_role": "CONTENT_HANDOFF_CAPABLE" if capable else "SHARED_WORKSHOP_GRAMMAR",
            "what_how_reading_de": (
                f"Herbal erzeugt/kennzeichnet {row['herbal_owner_filled_reading_de']}; Biological übernimmt denselben Arbeitswert als {row['biological_owner_filled_reading_de']}"
                if capable else
                f"gleiche grammatische Operation in beiden Registern: {row['invariant_atomic_value_de']}"
            ),
            "explicit_cross_record_pointer": "NO",
        })

    primitive_counts = {"HERBAL": Counter(), "BIOLOGICAL": Counter()}
    for row in phase_events:
        section = "HERBAL" if row["record"].startswith("H") else "BIOLOGICAL"
        for primitive in row["workshop_phase"].split(">"):
            primitive_counts[section][primitive] += 1
    primitives = sorted(set(primitive_counts["HERBAL"]) | set(primitive_counts["BIOLOGICAL"]))
    phase_rows = [{
        "primitive_phase": phase,
        "herbal_events": primitive_counts["HERBAL"][phase],
        "biological_events": primitive_counts["BIOLOGICAL"][phase],
        "present_both": "YES" if primitive_counts["HERBAL"][phase] and primitive_counts["BIOLOGICAL"][phase] else "NO",
        "workflow_role_de": {
            "ARGUMENT_OR_STATE": "gemeinsame Maß-/Ziel-/Zustandsangaben", "MATERIAL_PREP": "Material abnehmen/vorbereiten",
            "MEASURE_CHARGE": "Menge oder Portion setzen", "APPLY": "am Ziel anwenden", "HOLD": "halten/einwirken",
            "THERMAL": "wärmen/kühlen", "WASH": "waschen", "SETTLE": "absetzen/auffangen",
            "ROUTE": "führen/umsetzen", "SPECIALIST": "seltene Fachhandlung",
        }[phase],
    } for phase in primitives]

    criteria = [
        ("17 exakte portable Karten", 3, 2, "starker gemeinsamer Kern"),
        ("9 gemeinsame primitive Phasen", 3, 2, "fast kompletter gemeinsamer Arbeitszyklus"),
        ("Herbal offen; Biological lokal geschlossen", 3, 1, "komplementäre Artikel- und Zellform"),
        ("Maß/Ansatz/bereit/halten/temperieren als Brücken", 3, 1, "inhaltlich passende Übergabewerte"),
        ("kein expliziter Cross-Record-Zeiger", -2, 3, "direkte Paarung fehlt"),
        ("156 sektionslokale Karten", -1, 3, "große lokale Ausgestaltung"),
        ("Bildbesitzer verschieden, Grammatik identisch", 2, 2, "passt zu stummer Objektfüllung und auch zu Mehrzwecknotation"),
        ("sichtbare Pflanzen plus Bad-/Anwendungsszenen", 4, 0, "inhaltliche Bildfolge stützt praktisches Kompendium"),
    ]
    model_rows = [{
        "criterion": criterion, "integrated_what_how_score": a, "shared_grammar_independent_score": b,
        "reason_de": reason,
    } for criterion, a, b, reason in criteria]
    model_rows.append({
        "criterion": "TOTAL", "integrated_what_how_score": sum(x[1] for x in criteria),
        "shared_grammar_independent_score": sum(x[2] for x in criteria),
        "reason_de": "thematische Integration führt knapp; direkte Item-zu-Station-Übergabe bleibt ungeschrieben",
    })
    write("FIVE_HUNDRED_NINETIETH_SEVENTEEN_CROSS_SECTION_BRIDGES.tsv", bridge_rows)
    write("FIVE_HUNDRED_NINETIETH_PRIMITIVE_PHASE_COMPARISON.tsv", phase_rows)
    write("FIVE_HUNDRED_NINETIETH_TWO_MODEL_SCORECARD.tsv", model_rows)
    summary = {
        "status": "PASS", "portable_cards": len(bridge_rows),
        "handoff_capable_cards": sum(r["integration_role"] == "CONTENT_HANDOFF_CAPABLE" for r in bridge_rows),
        "grammar_only_cards": sum(r["integration_role"] == "SHARED_WORKSHOP_GRAMMAR" for r in bridge_rows),
        "shared_primitive_phases": sum(r["present_both"] == "YES" for r in phase_rows),
        "all_primitive_phases": len(phase_rows),
        "integrated_score": model_rows[-1]["integrated_what_how_score"],
        "independent_score": model_rows[-1]["shared_grammar_independent_score"],
        "explicit_cross_record_pointers": 0,
        "decision": "THEMATIC_WHAT_HOW_WORKFLOW_WITHOUT_EXPLICIT_ITEM_HANDOFF",
    }
    (HERE / "FIVE_HUNDRED_NINETIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertneunzigste Runde: Herbal WHAT / Biological HOW", "",
        "## Arbeitsentscheidung", "",
        "Die beste Arbeitstheorie ist jetzt eine thematische WHAT/HOW-Kopplung ohne ausgeschriebene Item-zu-Station-Verweise. Herbal beschreibt abgebildetes Material und seine offenen Zubereitungsfolgen; Biological beschreibt geschlossene lokale Handhabungs-, Bad-, Transfer- und Anwendungszellen. Beides benutzt dieselbe Werkstattgrammatik.", "",
        f"Siebzehn exakte Karten laufen durch beide Register; {summary['handoff_capable_cards']} davon können inhaltlich eine Übergabe tragen (Maß, Ansatz, bereit, gemessener Einsatz, Zielanwendung, Halten, Temperieren). Neun von zehn primitiven Arbeitsphasen erscheinen in beiden Registern; nur WASH ist auf den ausgewählten Herbal-Seiten nicht explizit.", "",
        "Trotzdem gibt es keinen geschriebenen Zeiger ›Artikel Hx gehört zu Station By‹. Deshalb ist nicht jeder Pflanzenartikel automatisch die Zutat einer bestimmten Badfigur. Die vorsichtige konkrete Lesung lautet: ein gemeinsames praktisches Kompendium mit Materialteil und Handhabungs-/Anwendungsteil, verbunden durch Werkstattwissen und Bilder, nicht durch sichtbare Querverweise.", "",
        "Der reine Mehrzweck-Notationsrivale bleibt möglich, verliert aber knapp: Die offene Herbal-Form, die geschlossene Biological-Zellform und die tragfähigen Maß/Ansatz/Zustandsbrücken bilden gemeinsam mehr als bloße graphische Wiederverwendung.", "",
        "## Nächster Schritt", "",
        "Nun wird der Astro-Anhang getrennt geprüft. Gesucht wird keine Übersetzung seiner 395 Gruppen mit dem Prosa-Wörterbuch, sondern eine einfache Werkstattfunktion: wann/nach welcher Himmelslage eine Material- oder Stationshandlung gewählt wird – oder alternativ ein unabhängiger Bild-/Merkatlas.",
    ]
    (HERE / "FIVE_HUNDRED_NINETIETH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
