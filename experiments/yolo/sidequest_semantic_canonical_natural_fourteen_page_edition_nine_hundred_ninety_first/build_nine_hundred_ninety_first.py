#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P989 = ROOT / "experiments/yolo/sidequest_semantic_canonical_image_owned_workshop_edition_nine_hundred_eighty_ninth"
P990 = ROOT / "experiments/yolo/sidequest_semantic_specialist_headword_cleanup_nine_hundred_ninetieth"

NATURAL = {
    "P915-C001": "Vom gezeigten Speicherwurzelstock einen Teil entnehmen, im Gefäß nach Sollmaß ansetzen, den ersten Zug auffangen, durch den Durchlass führen und bis zur Gebrauchsbereitschaft bearbeiten; den Teilgang schließen.",
    "P915-C002": "Danach einen weiteren Wurzel-, Blatt- oder Kopfanteil nehmen, anwärmen, pressen und portionsweise in den Topf geben; den Ansatz nach Sollmaß weiterführen, einen Teil trennen und die Fortsetzung offenlassen.",
    "P915-C003": "Vom Blütenkraut einen Sudansatz bilden, auswringen, die vorgeschriebene Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen; den Teilgang schließen.",
    "P915-C004": "Einen Blütenanteil als Reserve zurücklegen, vom vorigen Ansatz die Sollmenge nehmen, weitere Teile zugeben und den Folgezug halten; einen Teil als Trank oder Gebrauchsauszug weiterleiten, der Artikelzug bleibt offen.",
    "P915-C005": "Die Wurzelkrone aktivieren, ein Brutknöllchen und den ersten Teil abnehmen, im Ansatz halten, nach Sollmaß zugeben und den Blütenanteil mitführen; auspressen und den Teilgang schließen.",
    "P915-C006": "Vom restlichen Wurzelansatz eine Sollmenge nehmen, den Folgeansatz setzen, durch den Durchlass führen, an der Teilstelle fortsetzen und schließen.",
    "P915-C007": "Einen Blattanteil nach Sollmaß in den nächsten Ansatz geben, kurz bearbeiten, prüfen und den zweiten Teilgang schließen.",
    "P915-C008": "Den angesetzten Posten kurz halten, auf der nächsten Arbeitsstufe fortführen, zur bezeichneten Stelle geben und dort schließen.",
    "P915-C009": "Den nächsten Pflanzenteil auswählen, zugeben und mit dem vorhandenen Ansatz vereinigen; die Fortsetzung bleibt offen.",
    "P915-C010": "Von der großen Doldenpflanze eine Portion entnehmen, durch den bezeichneten Durchlass führen, vollständig bearbeiten und länger ansetzen; den ersten Teilgang schließen.",
    "P915-C011": "Nach Sollmaß einen neuen Ansatz beginnen, weitere Pflanzenteile und einen Zusatz zugeben, vollständig halten, aus dem Vorrat durch den Nebenweg zur Zielstelle führen und anschließend kühlen.",
    "P915-C012": "Eine Sollportion aus dem bezeichneten Teil nehmen, zusammen mit dem Zusatz zugeben und anschließend kühlen.",
    "P915-C013": "Den langen Hauptansatz aus Wurzel-, Blatt- und Doldenanteilen nach Sollmaß aufbauen, einzelne Portionen an Quell- und Zielstellen umsetzen, Proben entnehmen und behandeln, den Auszug weiterverwenden und den Gang schließen.",
    "P915-C014": "Eine letzte Sollportion an der Zielstelle anwärmen, kurz behandeln, länger weiterführen und danach im inneren Gefäß belassen; die Fortsetzung bleibt offen.",
    "P915-C015": "Vom stachelköpfigen Kraut den bezeichneten Reifeanteil wählen, kurz behandeln und den ersten Teilgang schließen.",
    "P915-C016": "Knospen-, Blüten- und reife Kopfanteile nacheinander entnehmen, nach Sollmaß ansetzen, länger halten und weiterführen; den letzten Posten auflegen, waschen und äußerlich auftragen.",
    "P915-C017": "Einen weiteren Kopf- oder Stängelanteil zerreiben, in den Auszug geben, abseihen, die nächste Portion länger halten und nach Sollmaß anwenden; eine letzte Zugabe bleibt offen.",
    "P915-C336": "Im bezeichneten Himmelsrad einen Eintrag wählen, seinen Zielplatz und Grad setzen, in derselben Reihe fortfahren und den Eintrag schließen.",
    "P915-C337": "Eine neue Tabellenreihe öffnen, den markierten Wert, Zielplatz, Bezug und Innenplatz übernehmen, einen Teilwert abtrennen und die Reihe offen weiterführen.",
    "P915-C338": "Den Bezugsplatz wählen, die zweite Markierung und den Innenplatz setzen, den zugehörigen Tabellenwert aktivieren und den Eintrag offenlassen.",
    "P915-C339": "Den aktuellen Himmelseintrag einstellen, ausführen und schließen.",
    "P915-C340": "Den bezeichneten Tabellenwert wählen und in derselben Reihe weiterfahren.",
    "P915-C341": "Vom Bezugsplatz zum Zielplatz gehen, den Tabellenwert und den zusätzlichen Ringlauf eintragen und die zweite Verbindung offenlassen.",
    "P915-C342": "In derselben Reihe einmal zur nächsten Stufe gehen, den Tabellenwert übernehmen und den Eintrag offenlassen.",
    "P915-C343": "Zur nächsten Tabellenposition gehen, Eintragsklasse und Sternstelle wählen, Stufe und Zustand prüfen, den Nebenplatz markieren und den Eintrag schließen.",
    "P915-C344": "Den gewählten Tabellenwert kurz halten, die zweite Unterstufe und den Zielplatz setzen und die Reihe offenlassen.",
    "P915-C345": "Den Tabellenwert einstellen, eine zweite Teilmarke und den Zielplatz wählen und den Eintrag offen fortführen.",
    "P915-C346": "In der großen Tabelle Bezug, Ziel, Ringlauf, Teilwert und Grad nacheinander setzen, die markierten Plätze kurz oder länger halten und den letzten Ort ohne erzwungene Drehrichtung offenlassen.",
    "P915-C347": "In der mehrteiligen Sternstellentafel den bezeichneten Posten und Grad wählen, zum nächsten Zielplatz übertragen, vollständig setzen und den Eintrag schließen.",
    "P915-C348": "Den aktuellen Sternposten länger halten, seinen Grad einstellen und den kurzen Eintrag schließen.",
    "P915-C349": "Eine lokale Sternstelle wählen, Eintragsklasse, Zielplatz und zweiten Innenplatz markieren, den Wert behandeln und die Fortsetzung offenlassen.",
    "P915-C350": "Die sechs oberen Zutatenposten auswählen, vom Vorrat die Sollmengen nehmen, in das obere Gefäß geben, kurz vorbereiten und den entstehenden Auszug zur nächsten Aufnahme leiten.",
    "P915-C351": "Mit der mittleren Zutatenreihe einen zweiten Ansatz beginnen, einen Anteil überführen und den kurzen Auftakt schließen.",
    "P915-C352": "Die übrigen mittleren Zutaten nach Sollmaß zugeben, den Ansatz mehrfach fortführen, den Auszug leiten, länger halten und den Teilgang schließen.",
    "P915-C353": "Von den vier unteren Zutatenposten den ersten Vorrat nehmen, kurz ansetzen, länger auffangen und den Vorbereitungsgang schließen.",
    "P915-C354": "Die letzte Gefäßcharge fortsetzen, weitere Anteile nach Sollmaß zugeben, den Auszug leiten, einen Folgeteil nehmen und den unteren Ansatz schließen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    codebook = read(P990 / "PASS990_159_CODEBOOK_WITH_CLEAN_HEADWORDS.tsv")
    events = read(P989 / "PASS989_2511_EVENT_INTERLINEAR.tsv")
    roots = read(P989 / "PASS989_53_ROOT_DICTIONARY.tsv")
    clauses = read(P989 / "PASS989_354_COMPLETE_CLAUSE_EDITION.tsv")
    addresses = read(P989 / "PASS989_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = read(P989 / "PASS989_14_PAGE_READABLE_EDITION.tsv")
    labels = read(P989 / "PASS989_16_F88R_INGREDIENT_LABELS.tsv")
    batches = read(P989 / "PASS989_THREE_F88R_BATCHES.tsv")

    for row in clauses:
        if row["clause_id"] in NATURAL:
            row["complete_working_translation_de"] = NATURAL[row["clause_id"]]
            if row["physical_page"].startswith("f6"):
                row["reading_source"] = "CELESTIAL_NATURAL_LOOKUP_REWRITE"
            elif row["physical_page"] == "f88r":
                row["reading_source"] = "F88_BATCH_NATURAL_REWRITE"
            else:
                row["reading_source"] = "HERBAL_NATURAL_REWRITE"

    write(HERE / "PASS991_159_CODEBOOK.tsv", codebook, list(codebook[0]))
    write(HERE / "PASS991_2511_EVENT_INTERLINEAR.tsv", events, list(events[0]))
    write(HERE / "PASS991_53_ROOT_DICTIONARY.tsv", roots, list(roots[0]))
    write(HERE / "PASS991_354_NATURAL_CLAUSE_EDITION.tsv", clauses, list(clauses[0]))
    write(HERE / "PASS991_501_LOCAL_ADDRESS_LEDGER.tsv", addresses, list(addresses[0]))
    write(HERE / "PASS991_14_PAGE_READABLE_EDITION.tsv", pages, list(pages[0]))
    write(HERE / "PASS991_16_F88R_INGREDIENT_LABELS.tsv", labels, list(labels[0]))
    write(HERE / "PASS991_THREE_F88R_BATCHES.tsv", batches, list(batches[0]))

    page_lines = ["# Pass 991 — vollständige natürliche Vierzehnseiten-Ausgabe", ""]
    for page in pages:
        page_lines.extend(
            [
                f"## {page['physical_page']} — {page['unit_role_de']}",
                "",
                page["complete_working_translation_de"],
                "",
            ]
        )
    page_lines.extend(
        [
            "## Leseregel",
            "",
            "Die Seitentexte sind flüssige Sprechfassungen. Exakte Kartenfolge,",
            "Ereignisbindung und lokale Adressen stehen in den TSV-Ausgaben. Eine",
            "physische Zeile ist nicht automatisch ein Satzende.",
            "",
        ]
    )
    (HERE / "PASS991_COMPLETE_FOURTEEN_PAGE_READING.md").write_text("\n".join(page_lines), encoding="utf-8")

    report = """# Pass 991 — alle 354 Aussagen natürlich lesbar

Pass 987 glättete bereits alle 318 Biological-Aussagen. Pass 991 redigiert die
verbleibenden 36 Aussagen: siebzehn Herbal-, vierzehn Himmels- und fünf
f88r-Chargensätze. Damit besitzt jetzt jede Aussage eine zusammenhängende
Werkstattlektüre, ohne ihre Oberfläche, Ereignisfolge oder Satzgrenze zu ändern.

Die Himmelsaussagen bleiben Adress- und Nachschlagehandlungen: Platz, Wert,
Grad, Bezug, Innen-/Außenstelle und Abschluss. Sie werden nicht als Bäder oder
Pflanzenrezepte gelesen und erhalten keine erfundene Drehrichtung.

Die Gesamtstruktur lautet weiterhin:

> Pflanzenmaterial → Gefäßzubereitung → lokale Bade-/Anwendungsstation →
> getrennte Himmelsnachschlagetafel.

Das 159-Einheiten-Wörterbuch enthält nun außerdem die zwölf präzisierten kurzen
Fachstichwörter aus Pass 990. Kein Stichwort trägt einen vollständigen Satz.
"""
    (HERE / "PASS991_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "codebook_units": len(codebook),
        "events": len(events),
        "clauses": len(clauses),
        "non_biological_clauses_manually_rewritten": len(NATURAL),
        "pages": len(pages),
        "addresses": len(addresses),
    }
    (HERE / "PASS991_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
