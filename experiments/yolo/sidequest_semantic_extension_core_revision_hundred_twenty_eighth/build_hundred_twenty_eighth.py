#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R121 = ROOT / "experiments/yolo/sidequest_semantic_complete_working_edition_hundred_twenty_first"
R126 = ROOT / "experiments/yolo/sidequest_semantic_shared_card_meaning_revision_hundred_twenty_sixth"

DECISIONS = {
    "MC034": ("HERBAL", "weitere Zutat", "Zutat", "Pflanzenstoff", "Bindestoff"),
    "MC103": ("HERBAL", "diesen Posten weiterbearbeiten", "ansetzen+Posten", "wieder aufnehmen", "Flüssigkeit zugeben"),
    "MC013": ("HERBAL", "nächster Arbeitsansatz", "danach+Ansatz", "danach", "zweite Zubereitung"),
    "MC142": ("HERBAL", "vom vorigen Posten", "vorher", "davon", "derselbe Pflanzenstoff"),
    "MC128": ("BIO", "kurz absetzen; schließen", "absetzen+kurz+Schluss", "ruhen lassen", "kurz warten"),
    "MC082": ("BIO", "länger einwirken; schließen", "ansetzen+länger+Schluss", "länger baden", "länger bearbeiten"),
    "MC083": ("BIO", "kurz einwirken; schließen", "ansetzen+kurz+Schluss", "kurz baden", "kurz bearbeiten"),
    "MC155": ("BIO", "abführen; schließen", "abführen+umsetzen+Schluss", "ablassen", "zum Auslass führen"),
    "MC002": ("BIO", "länger einwirken", "ansetzen+länger+Posten", "länger halten", "länger baden"),
    "MC017": ("BIO", "einen Anteil zugeben", "ansetzen+Anteil", "Portion nehmen", "Anteil einsetzen"),
    "MC025": ("BIO", "übertragen; schließen", "umsetzen+Schluss", "umfüllen", "weitergeben"),
    "MC035": ("BIO", "durchführen", "Durchlass+Posten", "durch den Gang leiten", "durchseihen"),
    "MC028": ("BIO", "weiter übertragen; schließen", "weiter+umsetzen+Schluss", "weiterführen", "weiter umfüllen"),
    "MC045": ("BIO", "länger auffangen; schließen", "sammeln+länger+Schluss", "länger sammeln", "länger halten"),
    "MC060": ("BIO", "nächstes Sollmaß", "danach+Sollmaß", "Folgemaß", "zweites Maß"),
    "MC088": ("BIO", "einsetzen, übertragen; schließen", "ansetzen+umsetzen+Schluss", "umsetzen", "Arbeitsgang wechseln"),
    "MC093": ("BIO", "danach dorthin", "danach+Ziel", "zum nächsten Ziel", "von dort weiter"),
    "MC105": ("BIO", "einen Anteil", "Anteil", "Portion", "Teilcharge"),
    "MC143": ("BIO", "seihen; schließen", "trennen+Schluss", "abtrennen", "Durchlass schließen"),
    "MC147": ("BIO", "kurz wärmen", "wärmen+kurz+Posten", "handwarm machen", "kurz halten"),
    "MC004": ("BIO", "abziehen; schließen", "abführen+Schluss", "ablassen", "entnehmen"),
    "MC005": ("BIO", "einsetzen, übertragen; schließen", "ansetzen+umsetzen+Schluss", "umfüllen", "neuen Lauf beginnen"),
    "MC007": ("BIO", "kurz einwirken", "ansetzen+kurz+Posten", "kurz baden", "kurz bearbeiten"),
    "MC012": ("BIO", "Zusatz", "Zusatz", "weitere Portion", "Hilfsstoff"),
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
    cards = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_173_TEACHING_DICTIONARY.tsv")
    events = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_381_EVENT_INTERLINEAR.tsv")
    shared = read_tsv(R126 / "HUNDRED_TWENTY_SIXTH_SEVENTEEN_REVISED_MEANINGS.tsv")
    shared_value = {row["master_card_id"]: row["revised_portable_default_de"] for row in shared}
    card_by_id = {row["master_card_id"]: row for row in cards}

    decision_rows = []
    for card_id, (section, revised, old, rival_a, rival_b) in DECISIONS.items():
        row = card_by_id[card_id]
        decision_rows.append({
            "section": section,
            "master_card_id": card_id,
            "master_form": row["master_form"],
            "registered_surfaces": row["all_registered_surfaces"],
            "semantic_atoms": row["semantic_atoms"],
            "event_count": row["event_count"],
            "records": row["records"],
            "old_short_default_de": old,
            "revised_short_default_de": revised,
            "concrete_rival_a": rival_a,
            "concrete_rival_b": rival_b,
        })
    decision_rows.sort(key=lambda row: (row["section"], -int(row["event_count"]), row["master_card_id"]))
    write_tsv("HUNDRED_TWENTY_EIGHTH_TWENTY_FOUR_EXTENSION_DECISIONS.tsv", decision_rows)

    occurrence_rows = []
    for row in events:
        if row["master_card_id"] not in DECISIONS:
            continue
        section, revised, old, _, _ = DECISIONS[row["master_card_id"]]
        occurrence_rows.append({
            "event_serial": row["event_serial"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "section": section,
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "old_short_default_de": old,
            "revised_short_default_de": revised,
            "continuous_statement_context_de": row["current_statement_reading_de"],
        })
    write_tsv("HUNDRED_TWENTY_EIGHTH_103_EXTENSION_OCCURRENCES.tsv", occurrence_rows)

    dictionary_rows = []
    current_value = {}
    for row in cards:
        card_id = row["master_card_id"]
        if card_id in shared_value:
            value = shared_value[card_id]
            layer = "REVISED_SHARED_17"
        elif card_id in DECISIONS:
            value = DECISIONS[card_id][1]
            layer = "REVISED_EXTENSION_CORE_24"
        else:
            value = row["short_default_de"]
            layer = "UNCHANGED_LEARNED_SECTION_CARD"
        current_value[card_id] = value
        dictionary_rows.append({
            "master_card_id": card_id,
            "master_form": row["master_form"],
            "registered_surfaces": row["all_registered_surfaces"],
            "semantic_atoms": row["semantic_atoms"],
            "current_short_default_de": value,
            "current_layer": layer,
            "event_count": row["event_count"],
            "records": row["records"],
        })
    write_tsv("HUNDRED_TWENTY_EIGHTH_173_CARD_OVERLAY.tsv", dictionary_rows)

    event_rows = []
    statement_values = defaultdict(list)
    for row in events:
        value = current_value[row["master_card_id"]]
        layer = next(card["current_layer"] for card in dictionary_rows if card["master_card_id"] == row["master_card_id"])
        event_rows.append({
            "event_serial": row["event_serial"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "current_short_default_de": value,
            "current_layer": layer,
        })
        statement_values[row["statement_id"]].append(value)
    write_tsv("HUNDRED_TWENTY_EIGHTH_381_EVENT_OVERLAY.tsv", event_rows)

    statement_rows = []
    seen = set()
    for row in events:
        statement_id = row["statement_id"]
        if statement_id in seen:
            continue
        seen.add(statement_id)
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "literal_current_card_reading_de": " | ".join(statement_values[statement_id]),
            "fluent_context_de": row["current_statement_reading_de"],
        })
    write_tsv("HUNDRED_TWENTY_EIGHTH_116_LITERAL_STATEMENTS.tsv", statement_rows)

    revised_events = sum(int(row["event_count"]) for row in decision_rows)
    report = [
        "# Hundertachtundzwanzigste Runde: der häufige Herbal-/Bio-Fachkern", "",
        "Vier wiederkehrende Herbal-Karten und zwanzig häufige Bio-Karten decken 103 zusätzliche",
        "Ereignisse. Zusammen mit dem gemeinsamen Deck haben nun 41 Karten mit 239 Vorkommen kurze,",
        "sprechbare Arbeitswerte; die übrigen 132 Kartentypen tragen nur 142 Ereignisse und bleiben vorerst",
        "gelernte Fachwörter.", "",
        "Herbal erhält `weitere Zutat`, `diesen Posten weiterbearbeiten`, `nächster Arbeitsansatz` und",
        "`vom vorigen Posten`. Bio erhält ein kleines Prozessraster: kurz/länger einwirken, kurz absetzen,",
        "abführen, abziehen, übertragen, durchführen, seihen, auffangen, kurz wärmen, Anteil zugeben und",
        "nächstes Sollmaß. Offene und geschlossene Varianten bleiben getrennt.", "",
        "Das ist erstmals ein ökonomisches Fachwörterbuch: wenige sehr häufige Befehle werden aktiv gelernt,",
        "seltene genaue Geräte-, Stoff- und Resultatkarten werden aus dem Exemplar übernommen. Der nächste",
        "Schritt ist eine ehrliche Einmalkartenrunde: die 132 Restkarten in kleine Sachschubladen legen und",
        "jeder genau ein kurzes konkretes Ganzwort geben, ohne neue Universalstämme zu erfinden.",
    ]
    (OUT / "HUNDRED_TWENTY_EIGHTH_EXTENSION_CORE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE",
        "extension_cards_revised": len(decision_rows),
        "extension_occurrences_revised": revised_events,
        "current_revised_cards": len(shared_value) + len(DECISIONS),
        "current_revised_events": sum(int(row["event_count"]) for row in dictionary_rows if row["current_layer"] != "UNCHANGED_LEARNED_SECTION_CARD"),
        "remaining_learned_card_types": sum(row["current_layer"] == "UNCHANGED_LEARNED_SECTION_CARD" for row in dictionary_rows),
        "remaining_learned_events": sum(int(row["event_count"]) for row in dictionary_rows if row["current_layer"] == "UNCHANGED_LEARNED_SECTION_CARD"),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
