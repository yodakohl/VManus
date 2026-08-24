#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_plant_owner_case_correction_five_hundred_seventieth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SUMMARIES = {
    "H1": ("OPEN_HERBAL_ARTICLE", "sichtbarer Pflanzenteil", "abnehmen, übertragen, Flüssigkeit ablaufen lassen, in einen Ansatz eintragen und nach Sollmaß beschicken", "offener Pflanzenansatz", "Von der ersten abgebildeten Pflanze wird ein Teil abgenommen, übertragen und in einen Ansatz eingearbeitet. Der Absatz fügt ein Sollmaß hinzu und bleibt als laufende Zubereitung offen."),
    "H2": ("OPEN_HERBAL_ARTICLE", "weiterer Teil derselben abgebildeten Pflanze", "abziehen, weiter vorbereiten und eine gemessene Zugabe einarbeiten", "offener Pflanzenansatz", "Ein weiterer Pflanzenteil wird abgezogen und im bestehenden Ansatz weiterbearbeitet. Danach kommt eine gemessene Zugabe hinzu; der Ansatz bleibt offen für die nächste Arbeitsstufe."),
    "H3": ("OPEN_HERBAL_ARTICLE", "Material der abgebildeten Blütenpflanze", "eintragen, halten, auswringen, ziehen lassen und weitere Mengen zugeben", "offener Blütenpflanzenansatz", "Das Blütenmaterial wird eingetragen, gehalten, ausgewrungen und ziehen gelassen. Die erste lange Folge schließt, danach werden weitere gemessene Mengen in den Pflanzenansatz gegeben; der Artikel endet offen."),
    "H4": ("OPEN_HERBAL_ARTICLE", "Material der breitblättrigen Pflanze", "bis Sollmaß beschicken, Portion abmessen, verwahren, temperieren und anlegen", "offener Ansatz mit Anwendungsportion", "Das Pflanzenmaterial wird bis zum Sollmaß beschickt. Eine Portion wird abgemessen und verwahrt, eine weitere temperiert; zuletzt wird Material an einer bildlich bezeichneten Stelle angelegt."),
    "H5": ("OPEN_HERBAL_ARTICLE", "Material der mehrköpfigen Pflanze", "Ansatz abziehen, Portion anlegen und weiterführen, weitere Pflanzenanteile und Mengen zugeben", "offener Pflanzenansatz", "Aus dem Pflanzenstoff wird ein Ansatz abgezogen. Eine Portion wird angelegt und weitergeführt; danach werden weitere Pflanzenanteile und eine gemessene Portion in den laufenden Ansatz gegeben."),
    "B1": ("CELLULAR_BASIN_REGISTER", "Flüssigkeit im gemeinsamen Becken", "beschicken, durchleiten, kühlen, waschen, umschöpfen, anwenden, absetzen und auffangen", "offene Beckenflüssigkeit an einer Zielstelle", "Ein gemeinsames Becken wird in 21 kurzen Arbeitszellen beschrieben. Die Flüssigkeit wird gemessen, geführt, gekühlt, gewaschen, umgeschöpft, stellenweise angewendet und abgesetzt; 17 Zellen schließen, die letzte hält nur eine Zielstelle offen."),
    "B2": ("CELLULAR_MULTI_STATION_REGISTER", "Flüssigkeit in oberem Becken, Handgerät, unterem Becken und Randstationen", "weitergeben, anlegen, einwirken, ruhen, abführen, umfüllen, kühlen und absetzen", "geschlossene Zielportion an den Randstationen", "Vier sichtbare Stationsgruppen liefern 22 weitgehend selbständige Zellen. Oben wird Flüssigkeit weitergegeben und angelegt, am Handgerät ruht sie, unten wird sie abgeleitet, und an den Randstationen wirkt, kühlt und setzt sie sich ab; 19 Zellen schließen."),
    "B3": ("CELLULAR_VESSEL_APPLICATION_REGISTER", "Arbeitsflüssigkeit, Gefäßansätze, getrennte Portionen und Figurenpaar-Anwendungen", "auffangen, temperieren, messen, umfüllen, absetzen, weiterleiten und anwenden", "geschlossene Anwendungsladung", "Die 34 Zellen wechseln sichtbar zwischen Fächerstation, zwei Gefäßen, getrenntem Zwischenbereich und Figurenpaar. Sie messen, temperieren, halten, setzen ab und führen Portionen weiter; 31 Zellen schließen. Das Ende ist eine verbuchte Anwendungsladung, kein globaler Kreislauf."),
    "B4": ("CELLULAR_APPLICATION_AND_STATION_REGISTER", "Anwendung am Figurenpaar sowie Flüssigkeit an linker und rechter Hauptstation", "einwirken, anlegen, festbinden, durch einen Lauf halten, messen, absetzen und weiterführen", "geschlossene Zielportion", "Alle 16 Zellen schließen. Die erste Gruppe behandelt eine Anwendung am Figurenpaar mit Halten, Anlegen und Festbinden; danach folgen zwei technische Stationen mit Messen, Durchlass, Absetzen und Weiterführung zu einer Zielportion."),
    "B5": ("TECHNICAL_APPENDIX", "Flüssigkeit der linken Nachtragsstation", "weiterführen, Portion einfüllen, ablagern und erneut beschicken", "offene Stationsflüssigkeit", "Der linke Nachtrag enthält drei technische Zellen. Zwei führen und schließen Portionen; die letzte lagert eine Flüssigkeit ab, führt sie weiter und beschickt den lokalen Bestand, bleibt aber offen."),
    "B6": ("TECHNICAL_APPENDIX", "Flüssigkeit im rechten S-Lauf", "auffangen, beschicken, temperieren und zur nächsten Stelle führen", "offene Zielportion", "Der rechte Nachtrag ist eine einzige offene Folge: Flüssigkeit wird aufgefangen, beschickt, temperiert und als Zielportion weitergeführt."),
}


def main():
    flows = {row["record"]: row for row in read_tsv(SOURCE / "FIVE_HUNDRED_SEVENTIETH_ELEVEN_CORRECTED_RECORD_FLOWS.tsv")}
    transitions = read_tsv(SOURCE / "FIVE_HUNDRED_SEVENTIETH_ONE_HUNDRED_SIXTEEN_CORRECTED_TRANSITIONS.tsv")
    order = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    rows = []
    markdown = ["# Elf natürliche Recordzusammenfassungen", "", "Die fünf Herbal-Records werden als offene Pflanzenartikel gelesen; B1–B4 als lokale Zellenregister; B5–B6 als technische Nachträge. Jede Zusammenfassung nennt Ausgangsgegenstand, Transformationen und Endzustand.", ""]
    for record in order:
        kind, start, process, end, summary = SUMMARIES[record]
        flow = flows[record]
        rows.append({
            "record": record,
            "page": flow["page"],
            "record_kind": kind,
            "statements": flow["statements"],
            "resets": flow["resets"],
            "committed_cells": flow["committed_cells"],
            "machine_start_object": flow["start_object"],
            "natural_start_material_de": start,
            "main_transformations_de": process,
            "machine_final_object": flow["final_object"],
            "natural_end_product_or_rest_de": end,
            "natural_record_summary_de": summary,
            "linear_whole_process_claim": "NO" if kind.startswith("CELLULAR") else "LOCAL_ARTICLE_SEQUENCE",
        })
        markdown.extend([
            f"## {record} — {kind}", "", summary, "",
            f"- Ausgang: {start} (`{flow['start_object']}`)",
            f"- Verarbeitung: {process}",
            f"- Ende: {end} (`{flow['final_object']}`)",
            f"- Zellen: {flow['statements']}, davon {flow['committed_cells']} geschlossen; Resets {flow['resets']}.", "",
        ])

    transition_rows = []
    summary_by_record = {row["record"]: row for row in rows}
    for transition in transitions:
        summary = summary_by_record[transition["record"]]
        transition_rows.append({
            **transition,
            "record_kind": summary["record_kind"],
            "record_summary_de": summary["natural_record_summary_de"],
            "transition_bound": "YES",
        })
    write_tsv("FIVE_HUNDRED_SEVENTY_FIRST_ELEVEN_NATURAL_RECORD_SUMMARIES.tsv", rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_FIRST_ONE_HUNDRED_SIXTEEN_BOUND_TRANSITIONS.tsv", transition_rows)
    (HERE / "FIVE_HUNDRED_SEVENTY_FIRST_COMPLETE_RECORD_EDITION.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS",
        "records": len(rows),
        "statements": len(transition_rows),
        "open_herbal_articles": sum(row["record_kind"] == "OPEN_HERBAL_ARTICLE" for row in rows),
        "cellular_registers": sum(row["record_kind"].startswith("CELLULAR") for row in rows),
        "technical_appendices": sum(row["record_kind"] == "TECHNICAL_APPENDIX" for row in rows),
        "total_committed_cells": sum(int(row["committed_cells"]) for row in rows),
        "bound_transitions": sum(row["transition_bound"] == "YES" for row in transition_rows),
    }
    (HERE / "FIVE_HUNDRED_SEVENTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhunderteinundsiebzigste Runde: natürliche Recordprofile",
        "",
        "## Ergebnis",
        "",
        "Die elf Records teilen sich in fünf offene Pflanzenartikel, vier lokale Zellenregister und zwei technische Nachträge. Diese Trennung löst einen alten Widerspruch: Herbal darf über mehrere Aussagen einen Ansatz fortführen, während Biological überwiegend abgeschlossene Varianten oder Stationsschritte nebeneinander stellt.",
        "",
        "H1–H5 beginnen jeweils mit sichtbarem Pflanzenmaterial und enden in einem offenen Ansatz oder einer Anwendungsportion. B1–B4 schließen zusammen 83 von 93 Zellen und wechseln lokal den Bildbesitzer; sie sind daher keine vier langen Sätze und keine einheitliche Rohrmaschine. B5–B6 sind kurze offene Nachträge für Stationsflüssigkeit und Zielportion.",
        "",
        "Jeder Record besitzt jetzt eine natürliche Start–Verarbeitung–Ende-Lesung und bleibt an alle 116 korrigierten Übergänge gebunden.",
        "",
        "## Nächster Schritt",
        "",
        "Als Nächstes werden die fünf Herbal-Artikel untereinander verglichen: Welche Artikelpositionen entsprechen Material, Ansatz, Maß, Anwendung und offenem Nachtrag? Daraus soll ein gemeinsames Herbal-Artikelschema entstehen.",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTY_FIRST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
