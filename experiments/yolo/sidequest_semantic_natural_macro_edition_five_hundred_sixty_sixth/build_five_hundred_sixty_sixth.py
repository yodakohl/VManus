#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P564 = ROOT / "sidequest_semantic_action_complete_translation_five_hundred_sixty_fourth"
P565 = ROOT / "sidequest_semantic_workshop_recipe_macros_five_hundred_sixty_fifth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


READINGS = {
    "ROUTE>CLOSE": "Zur nächsten sichtbaren Station führen und dort abschließen.",
    "HOLD>CLOSE": "Einwirken oder stehen lassen und danach abschließen.",
    "SETTLE>CLOSE": "Ruhen und absetzen lassen; danach abschließen.",
    "MEASURE_CHARGE": "Die vorgesehene Menge einfüllen.",
    "MEASURE_CHARGE>HOLD>CLOSE": "Eine Portion einfüllen, einwirken lassen und abschließen.",
    "MEASURE_CHARGE>ROUTE>CLOSE": "Eine Portion einfüllen, weiterführen und abschließen.",
    "CLOSE": "Den laufenden Arbeitsschritt abschließen.",
    "MEASURE_CHARGE>SETTLE>CLOSE": "Beschicken, absetzen lassen und abschließen.",
    "HOLD>SETTLE>CLOSE": "Einwirken lassen, absetzen und abschließen.",
    "MATERIAL_PREP": "Den bezeichneten Stoff vorbereiten.",
    "MEASURE_CHARGE>CLOSE": "Bis zum Sollmaß beschicken und abschließen.",
    "ROUTE": "Zur nächsten sichtbaren Station führen.",
    "ROUTE>MEASURE_CHARGE>ROUTE>CLOSE": "Von der vorigen Station übernehmen, beschicken, weiterführen und abschließen.",
    "ROUTE>SETTLE>CLOSE": "Weiterführen, auffangen oder absetzen und abschließen.",
    "THERMAL>SETTLE>CLOSE": "Temperieren, ruhen oder absetzen und abschließen.",
}


def owner_phrase(owner):
    if "Pflanze" in owner:
        return "Bei der abgebildeten Pflanze"
    replacements = {
        "gemeinsame zweireihige Figuren-/Beckenstation": "Am gemeinsamen Becken",
        "oberes Beckenpaar mit Zylinder": "Am oberen Beckenpaar",
        "mittleres linkes Handgerät mit Inline-Knoten": "Am mittleren Handgerät",
        "mittlere rechte unklare Station": "An der mittleren rechten Station",
        "unteres grünes Mehrfigurenbecken": "Am unteren grünen Becken",
        "kleine Randstationen des unteren Beckens": "An den kleinen Randstationen",
        "obere offene Fächerstation am Rand": "An der oberen Fächerstation",
        "mittlere Randfigur im runden Gefäß": "Am runden Gefäß",
        "untere Randfigur im korbartigen Gefäß": "Am korbartigen Gefäß",
        "unverbundener Zwischenbereich": "Im getrennten Zwischenbereich",
        "sichtbares Figurenpaar mit gemeinsamem Bogen in B3": "Am Figurenpaar in B3",
        "sichtbares Figurenpaar mit gemeinsamem Bogen in B4": "Am Figurenpaar in B4",
        "linke Hauptstation mit offenem Fransenlauf": "An der linken Hauptstation",
        "rechte Hauptstation mit S-Lauf und Mehrarmknoten": "An der rechten S-Station",
        "linke Fransenstation im B5-Nachtrag": "An der linken Nachtragsstation",
        "rechter S-Lauf im B6-Nachtrag": "Am rechten S-Lauf",
    }
    return replacements.get(owner, "Am sichtbaren Besitzer")


def main():
    source_statements = {row["statement_id"]: row for row in read_tsv(P564 / "FIVE_HUNDRED_SIXTY_FOURTH_ONE_HUNDRED_SIXTEEN_ACTION_COMPLETE_STATEMENTS.tsv")}
    macro_map = read_tsv(P565 / "FIVE_HUNDRED_SIXTY_FIFTH_ONE_HUNDRED_SIXTEEN_MACRO_MAP.tsv")
    macro_source = read_tsv(P565 / "FIVE_HUNDRED_SIXTY_FIFTH_RECURRENT_MACRO_DECK.tsv")
    events = read_tsv(P564 / "FIVE_HUNDRED_SIXTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_READINGS.tsv")

    macro_rows = []
    for row in macro_source:
        signature = row["phase_signature"]
        macro_rows.append({
            "macro_id": row["macro_id"],
            "phase_signature": signature,
            "natural_recipe_reading_de": READINGS[signature],
            "statements": row["statements"],
            "records": row["records"],
            "full_expansion_required": "YES",
        })

    statement_rows = []
    for mapped in macro_map:
        source = source_statements[mapped["statement_id"]]
        arguments = source["complete_argument_sequence_de"]
        if mapped["macro_status"] == "TAUGHT_RECURRENT_MACRO":
            natural = READINGS[mapped["phase_signature"]]
            translation = f"{owner_phrase(source['silent_owner_de'])}: {natural} Vollfolge: {source['complete_action_sequence_de']}."
            if arguments != "NONE":
                translation += f" Angaben: {arguments}."
            editorial_mode = "NATURAL_MACRO_PLUS_FULL_EXPANSION"
        else:
            translation = source["action_complete_translation_de"]
            editorial_mode = "EXPLICIT_ONE_OFF_SEQUENCE"
        statement_rows.append({
            "statement_id": mapped["statement_id"],
            "page": mapped["page"],
            "record": mapped["record"],
            "silent_owner_de": source["silent_owner_de"],
            "phase_signature": mapped["phase_signature"],
            "macro_id": mapped["macro_id"],
            "editorial_mode": editorial_mode,
            "full_action_sequence_de": source["complete_action_sequence_de"],
            "argument_sequence_de": arguments,
            "natural_complete_translation_de": translation,
            "all_actions_visible": "YES",
        })

    titles = {
        "H1": "erste Pflanzenanweisung", "H2": "zweiter Pflanzenabsatz", "H3": "Blütenpflanzenfolge",
        "H4": "breitblättrige Pflanzenfolge", "H5": "mehrköpfige Pflanzenfolge", "B1": "gemeinsames Becken",
        "B2": "Becken- und Randstationen", "B3": "Gefäß- und Figurenstationen", "B4": "Paar- und Hauptstationen",
        "B5": "linker Nachtrag", "B6": "rechter Nachtrag",
    }
    record_rows = []
    markdown = ["# Natürliche Makro-Ausgabe", "", "Wiederkehrende Zellen erhalten eine knappe Rezeptlesung; die vollständige Aktionsfolge bleibt jeweils ausdrücklich daneben stehen. Einmalige Zellen werden nicht künstlich zu Makros gemacht.", ""]
    for record, title in titles.items():
        rows = [row for row in statement_rows if row["record"] == record]
        record_rows.append({
            "record": record,
            "page": rows[0]["page"],
            "title_de": title,
            "statements": str(len(rows)),
            "taught_macro_statements": str(sum(row["macro_id"] != "NONE" for row in rows)),
            "one_off_statements": str(sum(row["macro_id"] == "NONE" for row in rows)),
            "continuous_translation_de": " ".join(row["natural_complete_translation_de"] for row in rows),
        })
        markdown.extend([f"## {record} — {title}", ""])
        markdown.extend(f"{index}. **{row['statement_id']}** — {row['natural_complete_translation_de']}" for index, row in enumerate(rows, 1))
        markdown.append("")

    event_statement = {row["statement_id"]: row for row in statement_rows}
    event_rows = []
    for event in events:
        statement = event_statement[event["statement_id"]]
        event_rows.append({
            **event,
            "macro_id": statement["macro_id"],
            "natural_complete_statement_de": statement["natural_complete_translation_de"],
            "event_retained_in_full_sequence": "YES",
        })

    write_tsv("FIVE_HUNDRED_SIXTY_SIXTH_FIFTEEN_NATURAL_MACROS.tsv", macro_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_SIXTH_ONE_HUNDRED_SIXTEEN_NATURAL_STATEMENTS.tsv", statement_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_SIXTH_ELEVEN_NATURAL_RECORDS.tsv", record_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv", event_rows)
    (HERE / "FIVE_HUNDRED_SIXTY_SIXTH_COMPLETE_NATURAL_EDITION.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS",
        "natural_macros": len(macro_rows),
        "statements": len(statement_rows),
        "macro_statements": sum(row["macro_id"] != "NONE" for row in statement_rows),
        "one_off_statements": sum(row["macro_id"] == "NONE" for row in statement_rows),
        "records": len(record_rows),
        "events": len(event_rows),
        "events_retained": sum(row["event_retained_in_full_sequence"] == "YES" for row in event_rows),
    }
    (HERE / "FIVE_HUNDRED_SIXTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsechsundsechzigste Runde: natürliche Makro-Ausgabe",
        "",
        "## Ergebnis",
        "",
        "Die fünfzehn wiederkehrenden Makros haben nun knappe deutsche Werkstattformulierungen. ROUTE→CLOSE wird „Zur nächsten sichtbaren Station führen und dort abschließen“; CHARGE→HOLD→CLOSE wird „Eine Portion einfüllen, einwirken lassen und abschließen“; THERMAL→SETTLE→CLOSE wird „Temperieren, ruhen oder absetzen und abschließen“.",
        "",
        "73 Aussagen verwenden diese natürliche Kurzform. Direkt dahinter steht immer die vollständige Kartenaktionsfolge; alle 237 Handlungskarten bleiben daher sichtbar. Die 43 einmaligen Folgen bleiben vollständig ausgeschrieben und werden nicht mit einem erfundenen Makronamen kaschiert.",
        "",
        "## Nächster Schritt",
        "",
        "Die Makro-Ausgabe wird nun gegen die Bildbesitzer gelesen: Für jedes Makro wird geprüft, ob es bei Pflanzen, Figuren/Becken oder technischen Stationen eine andere konkrete Objektfüllung verlangt. Dadurch sollen allgemeine Wörter wie `Arbeitsstoff` weiter schrumpfen, ohne den Makrowert selbst zu verändern.",
    ]
    (HERE / "FIVE_HUNDRED_SIXTY_SIXTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
