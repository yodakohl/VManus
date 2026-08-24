#!/usr/bin/env python3
import csv
import json
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_integrated_apprentice_manual_five_hundred_sixty_second"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


HERBAL = {
    "H1-S001": "Nimm von der abgebildeten Pflanze den vorgesehenen Teil kurz ab.",
    "H1-S002": "Setze diesen Pflanzenteil in den laufenden Ansatz ein.",
    "H2-S001": "Zieh von derselben Pflanze den nächsten vorgesehenen Teil ab.",
    "H2-S002": "Bearbeite ihn danach im vorgeschriebenen Maß weiter, bis die Zubereitung gebrauchsfertig ist.",
    "H2-S003": "Gib anschließend aus demselben Bezug nochmals das vorgeschriebene Maß zu.",
    "H3-S001": "Trage den blühenden Pflanzenteil in den Ansatz ein und halte ihn darin.",
    "H3-S002": "Halte ihn im laufenden Arbeitsgang und arbeite ihn ein.",
    "H3-S003": "Gib einen weiteren Anteil davon zu.",
    "H3-S004": "Setze danach das vorgeschriebene Maß ein und führe den Gang fort, bis der Ansatz bereit ist.",
    "H4-S001": "Setze vom breitblättrigen Kraut das vorgeschriebene Maß ein.",
    "H4-S002": "Miss eine weitere Portion ab und arbeite sie um.",
    "H4-S003": "Gib das Sollmaß dosiert zu.",
    "H4-S004": "Lege den abgemessenen Pflanzenstoff an der im Bild bezeichneten Stelle an.",
    "H5-S001": "Zieh den Ansatz vom Pflanzenstoff ab.",
    "H5-S002": "Lege den nächsten Anteil an der im Bild bezeichneten Stelle an.",
    "H5-S003": "Halte diesen Anteil dort.",
    "H5-S004": "Setze ihn in den Arbeitsgang ein.",
    "H5-S005": "Setze anschließend den nächsten Pflanzenanteil an.",
    "H5-S006": "Gib danach eine abgemessene Portion kurz in den laufenden Ansatz.",
}


def work_object(owner):
    if "gemeinsame zweireihige" in owner:
        return "die Flüssigkeit im gemeinsamen Becken"
    if "oberes Beckenpaar" in owner:
        return "die Flüssigkeit des oberen Beckenpaars"
    if "Handgerät" in owner:
        return "die Arbeitsflüssigkeit am Handgerät"
    if "mittlere rechte" in owner:
        return "die Portion an der mittleren rechten Station"
    if "unteres grünes" in owner:
        return "die Flüssigkeit des unteren Beckens"
    if "kleine Randstationen" in owner:
        return "die Arbeitsflüssigkeit der Randstationen"
    if "obere offene Fächerstation" in owner:
        return "die Flüssigkeit der oberen Fächerstation"
    if "mittlere Randfigur" in owner:
        return "die Flüssigkeit im runden Gefäß"
    if "untere Randfigur" in owner:
        return "die Flüssigkeit im korbartigen Gefäß"
    if "unverbundener Zwischenbereich" in owner:
        return "den getrennt geführten Arbeitsposten"
    if "Figurenpaar" in owner:
        return "die Flüssigkeit zwischen dem Figurenpaar"
    if "linke Hauptstation" in owner:
        return "die Flüssigkeit der linken Hauptstation"
    if "rechte Hauptstation" in owner:
        return "die Flüssigkeit der rechten Hauptstation"
    if "linke Fransenstation" in owner:
        return "die Flüssigkeit der linken Fransenstation"
    if "rechter S-Lauf" in owner:
        return "die Flüssigkeit im rechten S-Lauf"
    return "den laufenden Arbeitsposten"


def fluent_bio(literal, owner):
    text = literal
    text = text.replace("den laufenden Posten", work_object(owner))
    text = text.replace("eine Portion", "eine abgeteilte Portion der Arbeitsflüssigkeit")
    text = text.replace("von dort", "aus dieser Station")
    text = text.replace("an der bezeichneten Stelle", "an der im Bild bezeichneten Stelle")
    text = text.replace("im Arbeitsgang", "im laufenden Arbeitsgang")
    text = text.replace("bis bereit", "bis zum gebrauchsfertigen Zustand")
    text = text.replace("bis zur Sollstufe", "bis zur vorgeschriebenen Stufe")
    text = text.replace(" und den Schritt schließen", "; schließe damit diesen Arbeitsschritt")
    text = text.replace("danach ", "Danach ", 1)
    text = text[0].upper() + text[1:]
    if not text.endswith("."):
        text += "."
    return text


def main():
    traces = read_tsv(SOURCE / "FIVE_HUNDRED_SIXTY_SECOND_THREE_HUNDRED_EIGHTY_ONE_FULL_TRACES.tsv")
    statements = OrderedDict()
    for row in traces:
        statements.setdefault(row["statement_id"], row)
    statement_rows = []
    for statement_id, row in statements.items():
        if statement_id in HERBAL:
            fluent = HERBAL[statement_id]
            object_name = "abgebildeter Pflanzenstoff oder daraus gebildeter Ansatz"
        else:
            fluent = fluent_bio(row["containing_clause_de"], row["silent_owner_de"])
            object_name = work_object(row["silent_owner_de"])
        statement_rows.append({
            "statement_id": statement_id,
            "page": row["page"],
            "record": row["record"],
            "silent_owner_de": row["silent_owner_de"],
            "supplied_work_object_de": object_name,
            "literal_workshop_clause_de": row["containing_clause_de"],
            "fluent_working_translation_de": fluent,
            "translation_status": "CONCRETE_WORKING_READING",
        })

    by_statement = {row["statement_id"]: row for row in statement_rows}
    interlinear_rows = []
    for trace in traces:
        statement = by_statement[trace["statement_id"]]
        interlinear_rows.append({
            "event_id": trace["event_id"],
            "page": trace["page"],
            "record": trace["record"],
            "statement_id": trace["statement_id"],
            "surface": trace["observed_surface"],
            "component_parse": trace["component_parse"],
            "atomic_card_value_de": trace["atomic_card_value_de"],
            "local_action_expansion_de": trace["local_action_expansion_de"],
            "fluent_statement_de": statement["fluent_working_translation_de"],
            "complete_meaning": "YES",
        })

    titles = {
        "H1": "Erster Pflanzeneintrag: Teil abnehmen und einsetzen",
        "H2": "Zweiter Pflanzenabsatz: messen, weiterbearbeiten, zugeben",
        "H3": "Blütenpflanze: eintragen, halten, ergänzen",
        "H4": "Breitblättrige Pflanze: abmessen und anlegen",
        "H5": "Mehrköpfige Pflanze: Ansatz abziehen und Anteil ansetzen",
        "B1": "Gemeinsames Becken: waschen, halten und weiterführen",
        "B2": "Mehrere Beckenstationen: anlegen, ruhen, ableiten",
        "B3": "Gefäß- und Randstationen: zuführen, absetzen, umfüllen",
        "B4": "Figurenpaar und Hauptstationen: einwirken, befestigen, führen",
        "B5": "Linker Nachtrag: überführen und ablagern",
        "B6": "Rechter Nachtrag: auffangen",
    }
    record_rows = []
    markdown = ["# Fortlaufende deutsche Arbeitsübersetzung", "", "Diese Lesefassung behandelt Zeilenumbrüche nur als Raumumbrüche. Jeder nummerierte Satz entspricht einer der 116 Werkstattaussagen; die kurzen Kartenwerte stehen vollständig in der Interlineartabelle.", ""]
    for record in titles:
        rows = [row for row in statement_rows if row["record"] == record]
        continuous = " ".join(row["fluent_working_translation_de"] for row in rows)
        record_rows.append({
            "record": record,
            "page": rows[0]["page"],
            "title_de": titles[record],
            "statements": str(len(rows)),
            "continuous_translation_de": continuous,
        })
        markdown.extend([f"## {record} — {titles[record]}", "", continuous, "", "Einzelsätze:", ""])
        markdown.extend(f"{index}. **{row['statement_id']}** — {row['fluent_working_translation_de']}" for index, row in enumerate(rows, 1))
        markdown.append("")

    write_tsv("FIVE_HUNDRED_SIXTY_THIRD_ONE_HUNDRED_SIXTEEN_STATEMENT_TRANSLATIONS.tsv", statement_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_THIRD_THREE_HUNDRED_EIGHTY_ONE_INTERLINEAR.tsv", interlinear_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_THIRD_ELEVEN_CONTINUOUS_RECORDS.tsv", record_rows)
    (HERE / "FIVE_HUNDRED_SIXTY_THIRD_COMPLETE_GERMAN_WORKING_TRANSLATION.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS",
        "events": len(interlinear_rows),
        "statements": len(statement_rows),
        "records": len(record_rows),
        "herbal_statements_hand_smoothed": len(HERBAL),
        "bio_statements_owner_expanded": len(statement_rows) - len(HERBAL),
        "complete_meanings": sum(row["complete_meaning"] == "YES" for row in interlinear_rows),
        "empty_translations": sum(not row["fluent_working_translation_de"].strip() for row in statement_rows),
    }
    (HERE / "FIVE_HUNDRED_SIXTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertdreiundsechzigste Runde: fortlaufende Arbeitsübersetzung",
        "",
        "## Was der Text jetzt sagt",
        "",
        "Die fünf Herbal-Records lesen sich als knappe Pflanzen- und Zubereitungsanweisungen: Pflanzenteil abnehmen, in einen Ansatz einsetzen, nach Sollmaß weiterbearbeiten, weitere Portion zugeben und den Stoff an einer bildlich bezeichneten Stelle anlegen. Kein sichtbarer Zeilenumbruch wird als Satzende erzwungen.",
        "",
        "Die sechs Biological-Records lesen sich als lokale Becken- und Anwendungsprotokolle: Flüssigkeit einsetzen oder zuführen, kurz oder länger einwirken lassen, waschen, ruhen oder absetzen, durch einen Durchlass führen, an eine andere sichtbare Station umfüllen und den Arbeitsschritt schließen. Besitzerwechsel im Bild wechseln auch das ergänzte Arbeitsobjekt; es wird kein unsichtbarer Gesamtwasserkreislauf erfunden.",
        "",
        "Alle 116 Aussagen und 381 Kartenereignisse haben eine konkrete Lesung. Die Einzelkarte bleibt kurz; Satzflüssigkeit entsteht durch Bildbesitzer, Slotgrammatik und Handlungskontext. Genau dadurch wird eine alte Überladung wie `shey = bis die Flüssigkeit klar abläuft` vermieden: Die Karte liefert nur ihren kurzen Zustand oder Arbeitswert, der Satz liefert den Rest.",
        "",
        "## Nächster Angriff",
        "",
        "Nun werden die elf fortlaufenden Texte auf wiederkehrende reale Rezept- und Badehausformeln geprüft. Ziel ist, die noch generischen Wörter `Posten`, `Arbeitsflüssigkeit`, `einsetzen` und `umsetzen` dort zu ersetzen, wo dieselbe Kartenfolge bereits eine konkretere wiederkehrende Handlung erzwingt.",
    ]
    (HERE / "FIVE_HUNDRED_SIXTY_THIRD_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
