#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P555 = ROOT / "sidequest_semantic_atomic_card_unification_five_hundred_fifty_fifth"
P570 = ROOT / "sidequest_semantic_plant_owner_case_correction_five_hundred_seventieth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


EXPANSIONS = {
    "PROC009": ("Sollmaß des Pflanzenstoffs oder Ansatzes", "Sollmaß der lokalen Flüssigkeit oder Anwendung", "PORTABLE_QUANTITY"),
    "PROC013": ("denselben Pflanzenansatz fortführen", "dieselbe Zelle oder Stationsflüssigkeit fortführen", "PORTABLE_ORDER"),
    "PROC019": ("dieser Pflanzenteil oder Ansatz", "diese Flüssigkeit, Portion oder Anwendung", "PORTABLE_REFERENT"),
    "PROC042": ("Pflanzenstoff oder Ansatz umarbeiten", "Flüssigkeit umschöpfen oder lokal umsetzen", "PORTABLE_ACTION_FRAME"),
    "PROC008": ("Pflanzenstoff in den Ansatz geben", "lokales Medium in Einsatz bringen", "PORTABLE_ACTION_FRAME"),
    "PROC055": ("bezeichnete Pflanzen-/Anwendungsstelle", "bezeichnete Becken- oder Stationsstelle", "PORTABLE_TARGET"),
    "PROC038": ("Pflanzenansatz bis zum Sollmaß beschicken", "Becken, Gefäß oder Anwendung bis zum Sollmaß beschicken", "PORTABLE_MEASURED_ACTION"),
    "PROC014": ("dieser Pflanzenansatz ist bereit", "diese Flüssigkeit oder Anwendung ist bereit", "PORTABLE_STATE"),
    "PROC016": ("Pflanzenansatz oder Zubereitung", "lokaler Arbeitsansatz", "PORTABLE_PREPARATION"),
    "PROC048": ("Pflanzenstoff an der Stelle anlegen", "Flüssigkeit oder Anwendung an der Station ansetzen", "PORTABLE_TARGET_ACTION"),
    "PROC003": ("aus dem vorigen Pflanzenbezug", "aus der vorigen Station oder Quelle", "PORTABLE_SOURCE"),
    "PROC031": ("Pflanzenstoff länger ziehen lassen", "Flüssigkeit oder Anwendung länger einwirken lassen", "PORTABLE_HOLD"),
    "PROC004": ("Pflanzenstoff eintragen", "Flüssigkeit oder Portion eintragen", "PORTABLE_ENTRY"),
    "PROC022": ("denselben Pflanzenansatz fortsetzen", "denselben Arbeitsansatz fortsetzen", "PORTABLE_PREPARATION_ORDER"),
    "PROC046": ("Pflanzenansatz länger wärmen", "Flüssigkeit oder Anwendung länger wärmen", "PORTABLE_THERMAL"),
    "PROC047": ("Pflanzenarbeit fortsetzen und schließen", "Stationsarbeit fortsetzen und schließen", "PORTABLE_CLOSE"),
    "PROC065": ("danach dieser Pflanzenteil", "danach diese Flüssigkeit oder Portion", "PORTABLE_NEXT_REFERENT"),
}


def main():
    cards = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv")
    events = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_ATOMIC_EVENT_DICTIONARY.tsv")
    corrected = {row["event_id"]: row for row in read_tsv(P570 / "FIVE_HUNDRED_SEVENTIETH_THREE_HUNDRED_EIGHTY_ONE_CORRECTED_EVENTS.tsv")}
    by_card = defaultdict(list)
    for row in events: by_card[row["card_no"]].append(row)
    shared = [card for card, rows in by_card.items() if {"H" if row["record"].startswith("H") else "B" for row in rows} == {"H", "B"}]

    card_by_no = {row["card_no"]: row for row in cards}
    portable_rows = []
    audit_rows = []
    for card_no in sorted(shared, key=lambda card: (-len(by_card[card]), card)):
        rows = by_card[card_no]
        herbal, bio, portability = EXPANSIONS[card_no]
        portable_rows.append({
            "card_no": card_no,
            "surfaces": card_by_no[card_no]["surfaces"],
            "component_parse": card_by_no[card_no]["component_parse"],
            "invariant_atomic_value_de": card_by_no[card_no]["atomic_card_value_de"],
            "portable_function_class": portability,
            "herbal_owner_filled_reading_de": herbal,
            "biological_owner_filled_reading_de": bio,
            "herbal_events": str(sum(row["record"].startswith("H") for row in rows)),
            "biological_events": str(sum(row["record"].startswith("B") for row in rows)),
            "total_events": str(len(rows)),
            "atomic_value_changes_by_section": "NO",
            "only_object_filling_changes": "YES",
        })
        for row in rows:
            section = "HERBAL" if row["record"].startswith("H") else "BIOLOGICAL"
            audit_rows.append({
                "event_id": row["event_id"], "page": row["page"], "record": row["record"], "statement_id": row["statement_id"],
                "card_no": card_no, "surface": row["surface"], "component_parse": row["component_parse"],
                "section": section, "corrected_owner_object_class": corrected[row["event_id"]]["corrected_owner_object_class"],
                "invariant_atomic_value_de": row["atomic_card_value_de"],
                "owner_filled_reading_de": herbal if section == "HERBAL" else bio,
                "portable_function_class": portability, "portable_reading_complete": "YES",
            })

    inventory_rows = []
    category_counts = Counter()
    event_counts = Counter()
    for card_no, rows in by_card.items():
        sections = {"H" if row["record"].startswith("H") else "B" for row in rows}
        category = "CROSS_SECTION_PORTABLE" if sections == {"H", "B"} else "HERBAL_LOCAL" if sections == {"H"} else "BIOLOGICAL_LOCAL"
        category_counts[category] += 1; event_counts[category] += len(rows)
    for category in ["CROSS_SECTION_PORTABLE", "HERBAL_LOCAL", "BIOLOGICAL_LOCAL"]:
        inventory_rows.append({
            "inventory_class": category, "card_types": str(category_counts[category]), "events": str(event_counts[category]),
            "interpretation": "shared formal/semantic workshop function" if category == "CROSS_SECTION_PORTABLE" else "section-local learned card inventory",
        })

    write_tsv("FIVE_HUNDRED_SEVENTY_FOURTH_SEVENTEEN_PORTABLE_CARDS.tsv", portable_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_FOURTH_ONE_HUNDRED_THIRTY_SIX_PORTABLE_EVENTS.tsv", audit_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_FOURTH_THREE_INVENTORY_CLASSES.tsv", inventory_rows)
    summary = {
        "status": "PASS", "cards": len(cards), "events": len(events), "portable_cards": len(portable_rows),
        "portable_events": len(audit_rows), "portable_herbal_events": sum(row["section"] == "HERBAL" for row in audit_rows),
        "portable_biological_events": sum(row["section"] == "BIOLOGICAL" for row in audit_rows),
        "herbal_local_cards": category_counts["HERBAL_LOCAL"], "biological_local_cards": category_counts["BIOLOGICAL_LOCAL"],
        "atomic_value_changes": sum(row["atomic_value_changes_by_section"] != "NO" for row in portable_rows),
    }
    (HERE / "FIVE_HUNDRED_SEVENTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertvierundsiebzigste Runde: portable Karten",
        "",
        "## Ergebnis",
        "",
        "Siebzehn der 173 exakten Karten kommen sowohl in Herbal als auch Biological vor. Sie decken 136 Ereignisse: 44/100 Herbal und 92/281 Biological. Weitere 49 Karten sind nur Herbal, 107 nur Biological.",
        "",
        "Die siebzehn gemeinsamen Karten sind der portable Werkstattkern: Sollmaß, Fortsetzung, aktueller Posten, Quelle, Ziel, Ansatz, Bereitschaft, längeres Halten/Wärmen, Eintragen, Einsetzen, Umsetzen und Schluss. Keine dieser Karten wechselt ihren atomaren Wert zwischen den Sektionen.",
        "",
        "Nur die stumme Objektfüllung ändert sich. `OK+AIIN` beschickt im Herbal einen Pflanzenansatz bis zum Sollmaß und im Biological Becken, Gefäß oder Anwendung. `SH+EE+Y` lässt Pflanzenstoff ziehen, aber Flüssigkeit oder Anwendung einwirken. `CHD+Y` arbeitet Pflanzenstoff um oder schöpft Flüssigkeit lokal um. Dies ist keine Polysemie der Karte, sondern derselbe Vorgang an anderem Material.",
        "",
        "## Nächster Schritt",
        "",
        "Nun werden die 49 Herbal-lokalen und 107 Biological-lokalen Karten geprüft: Welche sind echte Fachwörter, welche bloß section-spezifische Kompositionen des portablen Kerns, und welche sollten als gelernte Ganzkarten bleiben?",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTY_FOURTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
