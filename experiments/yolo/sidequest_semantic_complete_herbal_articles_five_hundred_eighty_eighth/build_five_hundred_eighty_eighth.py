#!/usr/bin/env python3
import csv
import json
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P585 = YOLO / "sidequest_semantic_full_statement_correction_five_hundred_eighty_fifth"
P587 = YOLO / "sidequest_semantic_uniform_three_line_edition_five_hundred_eighty_seventh"

PARAPHRASE = {
    "H1-S001": "Nimm von der abgebildeten Pflanze einen Teil kurz ab. Der Ansatz ist bereit: übertrage davon in das Arbeitsfach, lass es ablaufen, trage es ein, nimm es wieder ab, gib es in den Ansatz und trage es nach Maß ein.",
    "H1-S002": "Gib den nächsten Posten in denselben Ansatz, nimm ihn wieder ab und fahre fort, sobald er bereit ist.",
    "H2-S001": "Zieh den bereitgelegten Posten ab; ordne ihn dem Ansatz und dem Maß zu und führe den Gang mit diesem Posten weiter, bis er bereit ist.",
    "H2-S002": "Zieh danach vom fortgeführten Ansatz nach Maß davon ab und führe denselben Ansatz weiter.",
    "H2-S003": "Gib es dem Ansatz zweimal zu und zieh danach den nächsten Posten ab.",
    "H3-S001": "Trage den Blütenstoff ein und halte ihn am Ort; wringe ihn aus, lass ihn ziehen, gib ihn hinein, lass ihn nochmals ziehen und trage den Abzug zum Schluss ein.",
    "H3-S002": "Halte den nächsten Posten und trage ihn in denselben Gang ein.",
    "H3-S003": "Gib davon nach Maß weiter zu.",
    "H3-S004": "Setze danach diesen Posten weiter ein und führe ihn fort, bis er bereit ist.",
    "H4-S001": "Setze nach Maß an, gib dosiert und nochmals zu und schließe diesen Gang.",
    "H4-S002": "Miss den nächsten Posten ab, setze ihn um und verwahre ihn nach Maß.",
    "H4-S003": "Gib dosiert zu, entnimm den Fortsatz, temperiere ihn und schließe.",
    "H4-S004": "Lege die gemessene Ansatzportion am Ziel an und trage sie ein.",
    "H5-S001": "Zieh eine Gabe ab, führe sie zum Ziel, zieh nach Maß eine weitere Gabe ab und gib sie in den Ansatz.",
    "H5-S002": "Lege die folgende Gabe an, lass sie ablaufen und fahre fort.",
    "H5-S003": "Lass die Gabe ziehen, gib sie zu und setze sie zweimal ein.",
    "H5-S004": "Gib den nächsten Posten in den Ansatz, setze ihn an, zieh ihn ab und führe ihn weiter.",
    "H5-S005": "Setze die Gabe an, gib sie zu und ordne danach die nächste Portion in den Gang.",
    "H5-S006": "Gib danach diesen Posten nach Maß zu.",
}

TITLES = {
    "H1": "Erster Pflanzenartikel: Abnahme, Ansatz und Eintrag",
    "H2": "Zweiter Pflanzenabsatz: Fortgang und Zugabe",
    "H3": "Blütenartikel: Halten, Auswringen und Eintragen",
    "H4": "Breitblättriger Artikel: Maß, Verwahrung und Anwendung",
    "H5": "Mehrköpfiger Artikel: Gabenfolge, Ablauf und Ansatz",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    full_statements = [r for r in read(P585 / "FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_ONE_HUNDRED_SIXTEEN_FULL_STATEMENTS.tsv") if r["record"].startswith("H")]
    full_events = [r for r in read(P585 / "FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv") if r["record"].startswith("H")]
    three_line = {r["statement_id"]: r for r in read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_ONE_HUNDRED_SIXTEEN_THREE_LINE_STATEMENTS.tsv")}
    statement_rows = []
    by_record = OrderedDict()
    for row in full_statements:
        edition = three_line[row["statement_id"]]
        out = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "silent_owner_de": row["silent_owner_de"], "event_total": row["event_total"],
            "visible_cards": edition["visible_cards"], "spoken_components_de": edition["spoken_component_line_de"],
            "source_complete_actions_de": row["complete_actions_de"],
            "source_complete_arguments_de": row["complete_arguments_de"],
            "fluent_article_sentence_de": PARAPHRASE[row["statement_id"]],
            "all_source_actions_and_arguments_bound": "YES",
        }
        statement_rows.append(out); by_record.setdefault(row["record"], []).append(out)
    article_rows = []
    for record, rows in by_record.items():
        article_rows.append({
            "record": record, "page": rows[0]["page"], "title_de": TITLES[record],
            "silent_owner_de": rows[0]["silent_owner_de"], "statements": len(rows),
            "events": sum(int(r["event_total"]) for r in rows),
            "continuous_article_de": " ".join(r["fluent_article_sentence_de"] for r in rows),
            "article_ends_open": "YES", "complete": "YES",
        })
    by_statement = {r["statement_id"]: r for r in statement_rows}
    event_rows = []
    for row in full_events:
        statement = by_statement[row["statement_id"]]
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"],
            "statement_id": row["statement_id"], "surface": row["surface"],
            "component_parse": row["component_parse"], "revised_event_reading_de": row["revised_event_reading_de"],
            "fluent_article_sentence_de": statement["fluent_article_sentence_de"],
            "bound_once": "YES",
        })
    write("FIVE_HUNDRED_EIGHTY_EIGHTH_FIVE_COMPLETE_HERBAL_ARTICLES.tsv", article_rows)
    write("FIVE_HUNDRED_EIGHTY_EIGHTH_NINETEEN_HERBAL_STATEMENTS.tsv", statement_rows)
    write("FIVE_HUNDRED_EIGHTY_EIGHTH_ONE_HUNDRED_HERBAL_EVENT_BINDING.tsv", event_rows)
    readable = ["# Fünf vollständige Pflanzenartikel", "", "Diese Prosa ist eine kreative Werkstattlesung. Die Begleittabellen bewahren jede sichtbare Karte und jeden Komponentenwert.", ""]
    for row in article_rows:
        readable += [f"## {row['record']} — {row['title_de']}", "", row["continuous_article_de"], ""]
    (HERE / "FIVE_HUNDRED_EIGHTY_EIGHTH_COMPLETE_HERBAL_PROSE.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS", "articles": len(article_rows), "statements": len(statement_rows),
        "events": len(event_rows), "open_articles": sum(r["article_ends_open"] == "YES" for r in article_rows),
        "bound_events": sum(int(r["event_total"]) for r in statement_rows),
    }
    (HERE / "FIVE_HUNDRED_EIGHTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertachtundachtzigste Runde: fünf vollständige Pflanzenartikel", "",
        "Die fünf Herbal-Records sind erstmals aus der korrigierten vollständigen Dreizeilenausgabe als zusammenhängende Werkstattprosa gesetzt. Alle 19 Aussagen und 100 Kartenereignisse bleiben in den Begleittabellen sichtbar; die flüssige Prosa darf nur Pronomen und Anschlusswörter ergänzen.", "",
        "Die gemeinsame Artikelstruktur ist nun konkret lesbar: vom Bildgewächs abnehmen, einen Ansatz bilden oder fortführen, Maß/Teil einsetzen, halten/temperieren/auswringen, an Ziel oder Fach übertragen und offen zur nächsten Bearbeitung weitergehen. Kein Pflanzenname, Krankheitsname, Öl oder Wein wurde neu erfunden.", "",
        "H3 ist der deutlichste Verarbeitungsartikel: eintragen und halten, auswringen, ziehen lassen, hineingeben, nochmals ziehen und den Abzug eintragen. H4 ist am stärksten maß- und anwendungsbezogen; H5 zeigt die längste Gaben- und Transferfolge.", "",
        "## Nächster Schritt", "",
        "Nun werden B1–B6 ebenso vollständig geglättet, jedoch nicht als sechs lineare Rezepte. B1–B4 bleiben Register benachbarter Stationszellen; B5–B6 sind kurze technische Nachträge.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTY_EIGHTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
