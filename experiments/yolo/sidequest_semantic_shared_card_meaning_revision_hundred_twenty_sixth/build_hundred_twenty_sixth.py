#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R121 = ROOT / "experiments/yolo/sidequest_semantic_complete_working_edition_hundred_twenty_first"
R122 = ROOT / "experiments/yolo/sidequest_semantic_shared_deck_network_hundred_twenty_second"
R123 = ROOT / "experiments/yolo/sidequest_semantic_two_register_source_grammar_hundred_twenty_third"

DECISIONS = {
    "oldy": ("fortsetzen; abschließen", "weiter+Schluss", "nur schließen", "beiseitestellen", "NATURALIZE_CLOSE"),
    "choky": ("diesen Posten einsetzen", "ansetzen+Posten", "nehmen", "mit Wasser ansetzen", "BROADEN_ACTION"),
    "cheeky": ("länger bearbeiten", "wärmen+länger+Posten", "länger wärmen", "länger halten", "REMOVE_THERMAL_OVERLOAD"),
    "aiin": ("Sollmaß", "Sollmaß", "Portion", "Zahl", "KEEP"),
    "okal": ("dorthin einsetzen", "ansetzen+Ziel", "dort wärmen", "Ziel markieren", "NATURALIZE_TARGET_ACTION"),
    "char": ("davon", "Quelle", "aus dem Gefäß", "Zutat", "ANAPHORIC_SOURCE"),
    "chdy": ("diesen Posten übertragen", "umsetzen+Posten", "umrühren", "abgießen", "BROADEN_TRANSFER"),
    "chor": ("Arbeitsansatz", "Ansatz", "Flüssigkeit", "Gefäßinhalt", "KEEP_WITH_NOUN"),
    "chety": ("einen Teil abtrennen", "teilen+Teil", "zerkleinern", "Portion nehmen", "NATURALIZE_PARTITION"),
    "cheey": ("Klarlauf", "Ergebnis", "bis klar abläuft", "fertig", "SHORTEN_TO_CONCRETE_RESULT"),
    "okaiin": ("auf Sollmaß stellen", "ansetzen+Sollmaß", "messen", "Sollmaß wiederholen", "NATURALIZE_VALUE_ACTION"),
    "chey": ("dieser Posten", "Posten", "dies", "aktiver Stoff", "ADD_ANAPHORIC_FORCE"),
    "cheol": ("weiter", "weiter", "und", "derselbe Weg", "KEEP"),
    "al": ("dorthin", "Ziel", "an die Stelle", "zum Gefäß", "ANAPHORIC_TARGET"),
    "cholor": ("damit weiter", "weiter+Ansatz", "voriger Ansatz", "nochmals", "NATURALIZE_CARRY"),
    "checthy": ("diesen Posten bereitstellen", "bereit+Posten", "fertig", "warm halten", "NATURALIZE_STATE_ACTION"),
    "otchey": ("der nächste Posten", "danach+Posten", "wiederholen", "zweiter Teil", "NATURALIZE_ORDER_ITEM"),
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    deck = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_17_SHARED_CARDS.tsv")
    events = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_381_EVENT_INTERLINEAR.tsv")
    skeletons = read_tsv(R122 / "HUNDRED_TWENTY_SECOND_116_SHARED_CARD_SKELETONS.tsv")
    exercises = read_tsv(R123 / "HUNDRED_TWENTY_THIRD_TWELVE_SOURCE_TO_CARD_EXERCISES.tsv")
    by_id = {row["master_card_id"]: row for row in deck}
    form_by_id = {row["master_card_id"]: row["master_form"] for row in deck}
    shared_ids = set(by_id)

    decision_rows = []
    for row in deck:
        chosen, old, rival_a, rival_b, revision = DECISIONS[row["master_form"]]
        decision_rows.append({
            "deck_order": row["deck_order"],
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "old_short_default_de": old,
            "revised_portable_default_de": chosen,
            "concrete_rival_a": rival_a,
            "concrete_rival_b": rival_b,
            "revision_type": revision,
            "records": row["records"],
            "event_count": row["event_count"],
        })
    write_tsv("HUNDRED_TWENTY_SIXTH_SEVENTEEN_REVISED_MEANINGS.tsv", decision_rows)

    by_statement = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    context_rows = []
    for statement_events in by_statement.values():
        for index, row in enumerate(statement_events):
            if row["master_card_id"] not in shared_ids:
                continue
            form = form_by_id[row["master_card_id"]]
            context_rows.append({
                "event_serial": row["event_serial"],
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "visible_surface": row["visible_surface"],
                "master_form": form,
                "previous_visible_surface": statement_events[index - 1]["visible_surface"] if index else "STATEMENT_START",
                "next_visible_surface": statement_events[index + 1]["visible_surface"] if index + 1 < len(statement_events) else "STATEMENT_END",
                "revised_portable_default_de": DECISIONS[form][0],
                "continuous_statement_context_de": row["current_statement_reading_de"],
            })
    write_tsv("HUNDRED_TWENTY_SIXTH_136_OCCURRENCE_CONTEXTS.tsv", context_rows)

    revised_skeletons = []
    for row in skeletons:
        if row["shared_surface_skeleton"] == "NONE":
            continue
        forms = row["shared_surface_skeleton"].split()
        revised_skeletons.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "shared_surface_skeleton": row["shared_surface_skeleton"],
            "old_literal_reading_de": row["source_phrase_expansion_de"],
            "revised_literal_reading_de": " ".join(DECISIONS[form][0] for form in forms),
            "current_fluent_statement_de": row["current_statement_reading_de"],
        })
    write_tsv("HUNDRED_TWENTY_SIXTH_57_REVISED_SHARED_READINGS.tsv", revised_skeletons)

    exercise_rows = []
    for row in exercises:
        forms = row["compiled_master_cards"].split()
        exercise_rows.append({
            "exercise_id": row["exercise_id"],
            "ordinary_source_command_de": row["ordinary_source_command_de"],
            "master_cards": row["compiled_master_cards"],
            "old_literal_backreading_de": row["literal_card_backreading_de"],
            "revised_literal_backreading_de": " ".join(DECISIONS[form][0] for form in forms),
            "status": row["manuscript_status"],
        })
    write_tsv("HUNDRED_TWENTY_SIXTH_TWELVE_REVISED_EXERCISES.tsv", exercise_rows)

    report = [
        "# Hundertsechsundzwanzigste Runde: die siebzehn Karten sprechen kürzer", "",
        "Die gemeinsamen Karten werden jetzt als knappe Werkstattwörter gelesen, nicht als Mini-Sätze.",
        "Drei wichtige Überladungen fallen: `cheeky` ist nicht zwingend Wärme, sondern **länger bearbeiten**;",
        "`choky` heißt **diesen Posten einsetzen**; `chdy` **diesen Posten übertragen**. Wärme, Wasser oder",
        "Gefäßrichtung kommen erst aus der lokalen Fachkarte und dem Bildbesitzer.", "",
        "Quell- und Zielkarten werden als sprechbare Anaphern behandelt: `char = davon`, `al = dorthin`.",
        "`chey = dieser Posten`, `otchey = der nächste Posten` und `cholor = damit weiter` machen den",
        "Formularcharakter deutlicher. `okaiin` wird zu **auf Sollmaß stellen**.", "",
        "`cheey/shey` bekommt gerade nicht die alte Satzglosse 'bis die Flüssigkeit klar abläuft'. Der kurze",
        "Ganzkartenwert ist **Klarlauf**. In einem Befehl kann daraus 'nimm den Klarlauf' oder 'führe bis zum",
        "Klarlauf' werden; die Syntax, nicht die Karte allein, liefert den ganzen Satz.", "",
        "Alle 136 Vorkommen, 57 gemeinsamen Gerüste und zwölf Vorwärtsübungen sind mit den neuen Kurzformen",
        "neu gelesen. Nächster Schritt: die sieben stärker revidierten Karten in ihren vollständigen Aussagen",
        "umschreiben und prüfen, ob daraus natürlichere kontinuierliche Herbal- und Bio-Passagen entstehen.",
    ]
    (OUT / "HUNDRED_TWENTY_SIXTH_SHARED_MEANING_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE",
        "shared_cards": len(decision_rows),
        "shared_occurrences": len(context_rows),
        "shared_skeletons": len(revised_skeletons),
        "revised_exercises": len(exercise_rows),
        "unchanged_defaults": sum(row["old_short_default_de"] == row["revised_portable_default_de"] for row in decision_rows),
        "revised_defaults": sum(row["old_short_default_de"] != row["revised_portable_default_de"] for row in decision_rows),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
