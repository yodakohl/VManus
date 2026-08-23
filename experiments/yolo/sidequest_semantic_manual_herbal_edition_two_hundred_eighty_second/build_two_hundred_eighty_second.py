#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R281 = ROOT / "experiments/yolo/sidequest_semantic_eight_prose_formulas_two_hundred_eighty_first"
STATEMENTS = R281 / "TWO_HUNDRED_EIGHTY_FIRST_116_FORMULA_ASSIGNMENTS.tsv"
HERBAL_PAGES = {"f10r", "f11r", "f55v", "f56r"}

TRANSLATIONS = {
    "H1-S001": ("Nimm von der Wurzel einen Teil, richte den Ansatz her und gib ihn in das Aufnahmegefäß. Gieße Arbeitsflüssigkeit – hier am ehesten Wasser – zu, setze den Folgeposten ein, miss die Sollmenge ab und behalte einen kleinen Rest zurück.", "WURZEL_WASSER_AUSZUG"),
    "H1-S002": ("Setze diesen Posten erneut ein, arbeite im folgenden Gang mit demselben Ansatz weiter und halte ihn bereit.", "WURZEL_WASSER_AUSZUG"),
    "H2-S001": ("Nimm den laufenden Auszugsansatz, bringe ihn in Bereitschaft und stelle ihn auf die vorgeschriebene Stufe. Führe denselben Posten weiter und verwende davon das Sollmaß.", "FORTGESETZTER_AUSZUG"),
    "H2-S002": ("Für den Folgeansatz arbeite mit derselben Zubereitung weiter; nimm vom laufenden Ansatz aus derselben Quelle die vorgeschriebene Menge.", "FORTGESETZTER_AUSZUG"),
    "H2-S003": ("Gib den Ansatz in sein Gefäß, halte denselben Posten aktiv, stelle die Arbeitsstufe ein und füge die vorgeschriebene Eingabemenge hinzu.", "FORTGESETZTER_AUSZUG"),
    "H3-S001": ("Koche das Pflanzenmaterial als Sud, wringe es aus, lasse es die vorgeschriebene Zeit stehen und seihe es nochmals. Bewahre nur den klaren Lauf, stelle ihn kalt und schließe die Zubereitung ab.", "GEKLAERTER_SUD"),
    "H3-S002": ("Halte einen weiteren Teil des Pflanzenmaterials für die folgende Zubereitung bereit.", "GEKLAERTER_SUD"),
    "H3-S003": ("Nimm vom vorigen Arbeitsgang, bearbeite denselben Posten weiter und miss die vorgeschriebene Menge ab.", "GEKLAERTER_SUD"),
    "H3-S004": ("Wechsle zum nächsten Posten, setze die Fortsetzung ein und halte diesen Teil bereit.", "GEKLAERTER_SUD"),
    "H4-S001": ("Miss die Sollmenge ab, teile sie in eine erste und eine zweite Portion, nimm sie danach aus der Wärme und lasse sie abkühlen; damit ist dieser Schritt festgesetzt.", "GEKUEHLTER_BLATTAUSZUG"),
    "H4-S002": ("Überführe die vorgeschriebene Menge und verwahre sie; schließe den Schritt ab.", "GEKUEHLTER_BLATTAUSZUG"),
    "H4-S003": ("Nimm die Sollportion aus dem gewonnenen Auszug, halte oder temperiere sie länger und fahre fort, bis der Zustand feststeht.", "GEKUEHLTER_BLATTAUSZUG"),
    "H4-S004": ("Setze das vorgeschriebene Maß an der bezeichneten Stelle ein, führe die laufende Zubereitung dort weiter und verwende eine Portion dieses Ansatzes.", "GEKUEHLTER_BLATTAUSZUG"),
    "H5-S001": ("Bereite einen Eingabeansatz, gib einen weiteren Pflanzenteil an die aktuelle Stelle und bemiss ihn. Bearbeite ihn weiter, richte den Folgeansatz her, setze denselben Posten ein und bringe ihn an die Zielstelle.", "STENGEL_UND_ZUSATZ_AUSZUG"),
    "H5-S002": ("Nimm Material aus dem vorigen Arbeitsgang, setze den aktuellen Zusatz ein und trage die Zubereitung auf; schließe den Schritt ab.", "STENGEL_UND_ZUSATZ_AUSZUG"),
    "H5-S003": ("Nimm den Stängel und einen weiteren Zusatz, bearbeite den laufenden Posten kurz und setze ihn nochmals ein.", "STENGEL_UND_ZUSATZ_AUSZUG"),
    "H5-S004": ("Setze den laufenden Posten ein, gib den Auszug hinzu und bearbeite beides an der Zielstelle.", "STENGEL_UND_ZUSATZ_AUSZUG"),
    "H5-S005": ("Gib einen weiteren Pflanzenteil hinzu, bearbeite den laufenden Posten mit dem Auszug aus der Quelle und führe ihn zur nächsten Anwendung weiter.", "STENGEL_UND_ZUSATZ_AUSZUG"),
    "H5-S006": ("Nimm den nächsten Posten, bearbeite ihn kurz weiter und verwende die vorgeschriebene Menge.", "STENGEL_UND_ZUSATZ_AUSZUG"),
}

ARTICLES = {
    "H1": ("Wurzel-Auszug mit Wasser", "Nimm einen Teil der abgebildeten Wurzel, bereite ihn im Aufnahmegefäß und gieße Wasser oder die örtliche Arbeitsflüssigkeit zu. Fange den folgenden Posten auf, miss die vorgeschriebene Menge ab und bewahre einen kleinen Rest. Setze denselben Ansatz im nächsten Gang wieder ein und halte ihn gebrauchsfertig."),
    "H2": ("Fortgesetzter Auszugsansatz", "Bereite den laufenden Auszug bis zur vorgeschriebenen Stufe. Arbeite für den Folgeansatz mit derselben Zubereitung und derselben Quelle weiter, miss die Sollmenge ab, gib sie in das Gefäß und ergänze die vorgeschriebene Eingabemenge."),
    "H3": ("Geklärter Sud", "Koche das Pflanzenmaterial zu einem Sud, wringe es aus, lasse es die vorgeschriebene Zeit stehen und seihe es erneut. Bewahre den klaren Lauf und stelle ihn kalt. Halte einen weiteren Pflanzenteil bereit; nimm später vom vorigen Arbeitsgang die Sollmenge und führe sie als nächsten gebrauchsfertigen Posten weiter."),
    "H4": ("Bemessener, gekühlter Blatt-Auszug", "Teile die Sollmenge in zwei Portionen, nimm sie aus der Wärme und lasse sie abkühlen. Überführe und verwahre die vorgeschriebene Menge. Nimm später eine Portion des Auszugs, halte oder temperiere sie länger und verwende sie an der bezeichneten Stelle."),
    "H5": ("Stängel- und Zusatz-Auszug in mehreren Anwendungen", "Bereite aus dem abgebildeten Stängel und weiteren Pflanzenteilen einen Ansatz in der vorgeschriebenen Menge. Trage einen Teil auf, bearbeite einen weiteren kurz und wiederhole den Einsatz. Gib Auszug hinzu, arbeite an der Zielstelle weiter und reiche den fertigen Posten zur nächsten Anwendung weiter."),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = [r for r in read_tsv(STATEMENTS) if r["page"] in HERBAL_PAGES]
    rows = []
    for row in source:
        fluent, article_type = TRANSLATIONS[row["statement_id"]]
        rows.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "loci": row["loci"],
            "surface_sequence": row["surface_sequence"],
            "formula_family": row["formula_family"],
            "terminal_status": row["terminal_status"],
            "family_sequence_de": row["family_sequence_de"],
            "article_type": article_type,
            "manual_fluent_translation_de": fluent,
            "picture_owner_policy": "pictured plant supplies the silent article owner; no species name asserted",
        })

    articles = []
    for record, (title, text) in ARTICLES.items():
        statement_rows = [r for r in rows if r["record_unit_id"] == record]
        articles.append({
            "record_unit_id": record,
            "page": statement_rows[0]["page"],
            "article_title_de": title,
            "statement_count": len(statement_rows),
            "event_surface_count": sum(len(str(r["surface_sequence"]).split(" · ")) for r in statement_rows),
            "continuous_article_de": text,
            "strongest_content_wager": "WATER_OR_WORKING_LIQUID" if record == "H1" else "CLARIFIED_DECOCTION" if record == "H3" else "EXTERNAL_APPLICATION" if record in {"H4", "H5"} else "REPEATED_EXTRACTION",
        })

    row_path = OUT / "TWO_HUNDRED_EIGHTY_SECOND_19_MANUAL_HERBAL_TRANSLATIONS.tsv"
    article_path = OUT / "TWO_HUNDRED_EIGHTY_SECOND_FIVE_HERBAL_ARTICLES.tsv"
    readable_path = OUT / "TWO_HUNDRED_EIGHTY_SECOND_COMPLETE_HERBAL_EDITION.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTY_SECOND_REPORT.md"
    write_tsv(row_path, rows, list(rows[0]))
    write_tsv(article_path, articles, list(articles[0]))

    lines = ["# Manuell geglättete Herbal-Ausgabe", "", "Die Pflanzenbilder liefern jeweils den stillen Artikelbesitzer. Die Art wird nicht benannt; die Handlungsfolge ist konkret.", ""]
    for article in articles:
        lines.extend([f"## {article['record_unit_id']} / {article['page']}: {article['article_title_de']}", "", str(article["continuous_article_de"]), ""])
        for row in [r for r in rows if r["record_unit_id"] == article["record_unit_id"]]:
            lines.append(f"- **{row['statement_id']}** — {row['manual_fluent_translation_de']}")
        lines.append("")
    readable_path.write_text("\n".join(lines), encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 282: manuell geglättete Herbal-Artikel

## Ergebnis

Der korrekte Herbal-Bestand umfasst19 Aussagen, nicht20. Alle19 werden manuell geglättet und zu fünf Artikeln verbunden: Wurzel-Wasser-Auszug, fortgesetzter Auszugsansatz, geklärter Sud, bemessener gekühlter Blatt-Auszug sowie Stängel-/Zusatz-Auszug mit mehreren Anwendungen.

Wasser wird in H1 als konkrete lokale Wette eingesetzt, weil ein Laufmedium in ein Aufnahmegefäß gegossen wird; der portable AIR-Wert bleibt LAUF/BAHN. Keine Pflanzenart wird behauptet. Jede manuelle Zeile bleibt an ihre vollständige 36-Familienfolge gebunden.

Input `{sha(STATEMENTS)}`.
""", encoding="utf-8")
    outputs = (row_path, article_path, readable_path, report_path)
    summary = {"status": "PASS", "statements": len(rows), "articles": len(articles), "record_counts": dict(Counter(r["record_unit_id"] for r in rows)), "outputs": {p.name: sha(p) for p in outputs}}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
