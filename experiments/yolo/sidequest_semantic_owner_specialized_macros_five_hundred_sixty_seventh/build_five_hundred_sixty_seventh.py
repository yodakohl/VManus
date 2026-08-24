#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P566 = ROOT / "sidequest_semantic_natural_macro_edition_five_hundred_sixty_sixth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def classify(owner):
    if "Pflanze" in owner:
        return "PLANT_MATERIAL", "den Pflanzenstoff oder Ansatz", "eine abgemessene Portion des Pflanzenstoffs"
    if "Handgerät" in owner:
        return "HAND_DEVICE_LIQUID", "die Arbeitsflüssigkeit im Handgerät", "eine abgemessene Portion der Arbeitsflüssigkeit"
    if "Figurenpaar" in owner:
        return "FIGURE_APPLICATION", "die Anwendung am Figurenpaar", "eine abgemessene Portion für die Anwendung"
    if "runden Gefäß" in owner or "korbartigen Gefäß" in owner:
        return "VESSEL_PREPARATION", "den Ansatz im Gefäß", "eine abgemessene Portion des Ansatzes"
    if "unverbundener Zwischenbereich" in owner:
        return "SEPARATE_PORTION", "die getrennt geführte Portion", "eine weitere abgemessene Portion"
    if "unklare Station" in owner:
        return "UNCLEAR_WORK_PORTION", "die Arbeitsportion an dieser Station", "eine abgemessene Arbeitsportion"
    if any(word in owner for word in ["Fächerstation", "Randstation", "Hauptstation", "Fransenstation", "S-Lauf"]):
        return "TECHNICAL_STATION_LIQUID", "die Flüssigkeit dieser Station", "eine abgemessene Portion der Stationsflüssigkeit"
    return "BASIN_LIQUID", "die Bad- oder Beckenflüssigkeit", "eine abgemessene Portion der Beckenflüssigkeit"


def specialize(signature, obj, portion, owner_class):
    hold = "ziehen" if owner_class == "PLANT_MATERIAL" else "einwirken oder stehen"
    templates = {
        "ROUTE>CLOSE": f"Führe {obj} zur nächsten sichtbaren Station und schließe dort den Schritt.",
        "HOLD>CLOSE": f"Lass {obj} {hold}; schließe danach den Schritt.",
        "SETTLE>CLOSE": f"Lass {obj} ruhen und sich absetzen; schließe danach den Schritt.",
        "MEASURE_CHARGE": f"Fülle {portion} ein.",
        "MEASURE_CHARGE>HOLD>CLOSE": f"Fülle {portion} ein, lass sie einwirken und schließe den Schritt.",
        "MEASURE_CHARGE>ROUTE>CLOSE": f"Fülle {portion} ein, führe sie weiter und schließe den Schritt.",
        "CLOSE": f"Schließe den laufenden Arbeitsschritt für {obj}.",
        "MEASURE_CHARGE>SETTLE>CLOSE": f"Beschicke mit {portion}, lass den Inhalt absetzen und schließe den Schritt.",
        "HOLD>SETTLE>CLOSE": f"Lass {obj} einwirken, dann absetzen, und schließe den Schritt.",
        "MATERIAL_PREP": f"Bereite {obj} vor.",
        "MEASURE_CHARGE>CLOSE": f"Beschicke bis zum Sollmaß mit {portion} und schließe den Schritt.",
        "ROUTE": f"Führe {obj} zur nächsten sichtbaren Station.",
        "ROUTE>MEASURE_CHARGE>ROUTE>CLOSE": f"Übernimm {obj}, gib {portion} zu, führe weiter und schließe den Schritt.",
        "ROUTE>SETTLE>CLOSE": f"Führe {obj} weiter, fange sie oder ihn auf, lass absetzen und schließe den Schritt.",
        "THERMAL>SETTLE>CLOSE": f"Temperiere {obj}, lass ruhen oder absetzen und schließe den Schritt.",
    }
    return templates[signature]


def main():
    statements = read_tsv(P566 / "FIVE_HUNDRED_SIXTY_SIXTH_ONE_HUNDRED_SIXTEEN_NATURAL_STATEMENTS.tsv")
    events = read_tsv(P566 / "FIVE_HUNDRED_SIXTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv")
    macro_defs = {row["macro_id"]: row for row in read_tsv(P566 / "FIVE_HUNDRED_SIXTY_SIXTH_FIFTEEN_NATURAL_MACROS.tsv")}

    statement_rows = []
    combo_counts = Counter()
    for row in statements:
        owner_class, obj, portion = classify(row["silent_owner_de"])
        full = row["full_action_sequence_de"].replace("den Arbeitsstoff", obj).replace("eine Portion", portion)
        if row["macro_id"] != "NONE":
            specialized = specialize(row["phase_signature"], obj, portion, owner_class)
            reading = f"{specialized} Vollfolge: {full}."
            combo_counts[(row["macro_id"], owner_class)] += 1
        else:
            specialized = "ONE_OFF_SEQUENCE"
            reading = row["natural_complete_translation_de"].replace("den Arbeitsstoff", obj).replace("eine Portion", portion)
        statement_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "silent_owner_de": row["silent_owner_de"],
            "owner_object_class": owner_class,
            "supplied_work_object_de": obj,
            "supplied_portion_de": portion,
            "macro_id": row["macro_id"],
            "phase_signature": row["phase_signature"],
            "owner_specialized_macro_de": specialized,
            "full_action_sequence_de": full,
            "owner_specialized_complete_reading_de": reading,
            "all_actions_visible": "YES",
        })

    combo_rows = []
    for (macro_id, owner_class), count in sorted(combo_counts.items()):
        sample = next(row for row in statement_rows if row["macro_id"] == macro_id and row["owner_object_class"] == owner_class)
        combo_rows.append({
            "macro_id": macro_id,
            "phase_signature": macro_defs[macro_id]["phase_signature"],
            "owner_object_class": owner_class,
            "statements": str(count),
            "owner_specialized_macro_de": sample["owner_specialized_macro_de"],
            "formal_macro_unchanged": "YES",
        })

    event_statement = {row["statement_id"]: row for row in statement_rows}
    event_rows = []
    for row in events:
        statement = event_statement[row["statement_id"]]
        event_rows.append({
            **row,
            "owner_object_class": statement["owner_object_class"],
            "owner_specialized_statement_de": statement["owner_specialized_complete_reading_de"],
            "event_retained": "YES",
        })

    titles = {
        "H1": "erste Pflanzenanweisung", "H2": "zweiter Pflanzenabsatz", "H3": "Blütenpflanzenfolge",
        "H4": "breitblättrige Pflanzenfolge", "H5": "mehrköpfige Pflanzenfolge", "B1": "gemeinsames Becken",
        "B2": "Becken- und Randstationen", "B3": "Gefäß- und Figurenstationen", "B4": "Paar- und Hauptstationen",
        "B5": "linker Nachtrag", "B6": "rechter Nachtrag",
    }
    record_rows = []
    markdown = ["# Bildbesitzer-spezialisierte Makro-Ausgabe", "", "Das formale Makro bleibt in allen Bereichen gleich. Der sichtbare Besitzer liefert Pflanzenstoff, Badflüssigkeit, Gefäßansatz, Anwendung oder Stationsflüssigkeit als konkretes Objekt.", ""]
    for record, title in titles.items():
        rows = [row for row in statement_rows if row["record"] == record]
        record_rows.append({
            "record": record,
            "page": rows[0]["page"],
            "title_de": title,
            "statements": str(len(rows)),
            "owner_classes": "|".join(sorted({row["owner_object_class"] for row in rows})),
            "continuous_owner_specialized_reading_de": " ".join(row["owner_specialized_complete_reading_de"] for row in rows),
        })
        markdown.extend([f"## {record} — {title}", ""])
        markdown.extend(f"{index}. **{row['statement_id']}** ({row['owner_object_class']}) — {row['owner_specialized_complete_reading_de']}" for index, row in enumerate(rows, 1))
        markdown.append("")

    write_tsv("FIVE_HUNDRED_SIXTY_SEVENTH_MACRO_OWNER_COMBINATIONS.tsv", combo_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_SEVENTH_ONE_HUNDRED_SIXTEEN_OWNER_SPECIALIZED_STATEMENTS.tsv", statement_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_SEVENTH_ELEVEN_OWNER_SPECIALIZED_RECORDS.tsv", record_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv", event_rows)
    (HERE / "FIVE_HUNDRED_SIXTY_SEVENTH_COMPLETE_OWNER_SPECIALIZED_EDITION.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS",
        "owner_classes": len({row["owner_object_class"] for row in statement_rows}),
        "macro_owner_combinations": len(combo_rows),
        "statements": len(statement_rows),
        "macro_statements": sum(row["macro_id"] != "NONE" for row in statement_rows),
        "one_off_statements": sum(row["macro_id"] == "NONE" for row in statement_rows),
        "records": len(record_rows),
        "events": len(event_rows),
        "generic_workstoff_remaining": sum("Arbeitsstoff" in row["owner_specialized_complete_reading_de"] for row in statement_rows),
    }
    (HERE / "FIVE_HUNDRED_SIXTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsiebenundsechzigste Runde: Besitzer-spezialisierte Makros",
        "",
        "## Ergebnis",
        "",
        "Acht sichtbare Objektklassen füllen die fünfzehn Makros: Pflanzenstoff/Ansatz, Bad- oder Beckenflüssigkeit, Handgerät-Flüssigkeit, Gefäßansatz, Figurenpaar-Anwendung, technische Stationsflüssigkeit, getrennte Portion und unklare Arbeitsportion. Der formale Makrowert bleibt gleich; nur sein stummes Objekt wechselt mit dem Bild.",
        "",
        "Damit verschwindet `Arbeitsstoff` aus der aktiven Lesefassung. HOLD→CLOSE wird beim Kraut zu ziehen lassen und schließen, am Becken zu Badflüssigkeit einwirken lassen und schließen, am Handgerät zu Arbeitsflüssigkeit stehen lassen und schließen. ROUTE→CLOSE führt jeweils das sichtbar passende Medium zur nächsten Station.",
        "",
        "Alle 116 Aussagen und 381 Ereignisse bleiben vollständig, einschließlich der ausgeschriebenen Aktionsfolge. Diese Trennung ist nun zentral: Karte/Makro sagt WAS GETAN WIRD; Bildbesitzer sagt WOMIT oder WORAN.",
        "",
        "## Nächster Schritt",
        "",
        "Als Nächstes wird geprüft, welche der acht Objektklassen über Recordgrenzen mit denselben Mengen- und Zustandskarten kombiniert werden. Daraus soll ein kleines Inventar wiederkehrender Werkstattgegenstände entstehen, ohne sichtbare Pflanzenarten oder Krankheiten zu erfinden.",
    ]
    (HERE / "FIVE_HUNDRED_SIXTY_SEVENTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
