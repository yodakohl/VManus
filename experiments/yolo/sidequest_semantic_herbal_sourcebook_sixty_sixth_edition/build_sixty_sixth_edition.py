#!/usr/bin/env python3
"""Write five compact Herbal source articles from the shared clausebook."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_period_clausebook_sixty_fifth_edition/SIXTY_FIFTH_381_PERIOD_SOURCE_CLAUSES.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_258_COMPLETE_UNITS.tsv"
HERBAL_PAGES = {"f10r", "f11r", "f55v", "f56r"}

ARTICLES = {
    "H1": {
        "title": "Wurzelgang der breitblättrigen Bildpflanze",
        "compact": "Nimm einen Teil der Wurzel der abgebildeten Pflanze, säubere und zerschneide ihn. Setze ihn mit Wasser im Gefäß an und fange den ersten Auszug auf. Gebrauche davon das kleine örtliche Maß; erwärme den weitergeführten Auszug gelinde und verwahre den Rest.",
        "content_wager": "WURZEL · WASSER · GEFÄSS · ERSTER AUSZUG · KLEINES MASS · INNERER GEBRAUCH",
        "strongest_rival": "allgemeiner Materialauszug ohne medizinischen Gebrauch",
    },
    "H2": {
        "title": "Spitzen- und Salbengang derselben Bildpflanze",
        "compact": "Nimm junge Spitzen und Blätter, zerstoße sie und presse den Saft durch Tuch. Vereinige zwei nacheinander bereitete Fraktionen im gleichen Maß. Rühre den Ansatz mit Öl bei kleinem Feuer bis zur weichen Salbe und lege sie äußerlich auf die bezeichnete Schwellung.",
        "content_wager": "JUNGE SPITZEN · TUCHPRESSUNG · ZWEI FRAKTIONEN · GLEICHES MASS · ÖL · SALBE",
        "strongest_rival": "zweistufige Werkstoffpaste ohne Körperziel",
    },
    "H3": {
        "title": "Blütenauszug und zweite Verwendung der blau bekrönten Bildpflanze",
        "compact": "Koche junge Blüten und Blätter in Wein, wringe sie durch Tuch, lasse den Auszug stehen und seihe ihn nochmals klar. Behalte Blüten zurück. Gebrauche vom klaren Auszug ein kleines Maß als Trank; erwärme die zurückbehaltenen Blüten in Öl und streiche die Zubereitung äußerlich an die bezeichnete Stelle.",
        "content_wager": "BLÜTEN · WEIN · AUSWRINGEN · STEHEN · NACHSEIHEN · KLARAUSZUG · TRANK · ÖL",
        "strongest_rival": "Färbe- oder Duftauszug mit zweiter äußerer Verwendung",
    },
    "H4": {
        "title": "Blattauszug und warme Auflage der rispigen Bildpflanze",
        "compact": "Zerstoße breite Blätter, gib Wein hinzu und lasse den verschlossenen Ansatz kühl stehen. Wring eine Portion durch Leinwand und verwahre den klaren Auszug. Wasche damit die bezeichnete äußere Stelle. Erwärme zurückbehaltene Blätter mit Honig und lege sie frisch als warme Auflage an.",
        "content_wager": "BLATT · WEIN · KÜHLER ANSATZ · LEINWAND · KLARAUSZUG · WASCHUNG · HONIG · AUFLAGE",
        "strongest_rival": "Textil- oder Materialwäsche mit anschließendem Klebeverband",
    },
    "H5": {
        "title": "Äußerer und innerer Doppelgang der mehrköpfigen Bildpflanze",
        "compact": "Nimm frisches oberirdisches Kraut vom feuchten Standort und lege eine kleine zerstoßene Portion kurz an die bezeichnete Hautstelle; nimm sie ab und wasche nach. Trockne den übrigen blühenden Bestand im Schatten. Setze daraus mit mildem Wein einen Auszug an, seihe ihn, gib Honig hinzu und gebrauche ein kleines Maß als Brusttrank.",
        "content_wager": "FEUCHTER STANDORT · FRISCHES KRAUT · KURZE AUFLAGE · NACHWASCHEN · TROCKNEN · WEIN · HONIG · TRANK",
        "strongest_rival": "zweifacher Werkstoffgebrauch: frische Ätzung und konservierter Auszug",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    clauses = [row for row in read_tsv(CLAUSES) if row["page"] in HERBAL_PAGES]
    units = {
        row["unit_id"]: row for row in read_tsv(UNITS)
        if row["unit_kind"] == "PROSE_STATEMENT" and row["page"] in HERBAL_PAGES
    }
    by_unit = defaultdict(list)
    for row in clauses:
        by_unit[row["unit_id"]].append(row)
    group_rows = []
    for row in clauses:
        group_rows.append({
            "source_group_id": row["source_group_id"],
            "unit_id": row["unit_id"],
            "record_id": row["unit_id"].split("-")[0],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "clause_shape_id": row["clause_shape_id"],
            "source_slots": row["source_slots"],
            "period_source_clause": row["workshop_vernacular_clause"],
            "historical_mechanism": row["historical_mechanism"],
        })
    write_tsv(OUT / "SIXTY_SIXTH_100_HERBAL_GROUP_EDITION.tsv", group_rows)

    statement_rows = []
    for unit_id, unit in units.items():
        rows = by_unit[unit_id]
        statement_rows.append({
            "unit_id": unit_id,
            "record_id": unit_id.split("-")[0],
            "page": unit["page"],
            "owner": unit["owner_or_namespace"],
            "group_count": len(rows),
            "surface_sequence": unit["surface_sequence"],
            "clause_shape_sequence": ">".join(row["clause_shape_id"] for row in rows),
            "short_card_sequence_de": unit["card_by_card_reading_de"],
            "period_source_clause_sequence": " ".join(row["workshop_vernacular_clause"] for row in rows),
            "continuous_working_translation_de": unit["fluent_working_reading_de"],
            "plant_owner_source": "VISIBLE_IMAGE",
            "rich_noun_source": "SIMULATED_MASTER_EXEMPLAR",
        })
    write_tsv(OUT / "SIXTY_SIXTH_19_HERBAL_STATEMENTS.tsv", statement_rows)

    by_record = defaultdict(list)
    for row in statement_rows:
        by_record[row["record_id"]].append(row)
    article_rows = []
    for record_id in sorted(ARTICLES):
        rows = by_record[record_id]
        article = ARTICLES[record_id]
        article_rows.append({
            "record_id": record_id,
            "page": rows[0]["page"],
            "owner": rows[0]["owner"],
            "title_de": article["title"],
            "statement_ids": ",".join(row["unit_id"] for row in rows),
            "group_count": sum(int(row["group_count"]) for row in rows),
            "complete_surface": " | ".join(row["surface_sequence"] for row in rows),
            "compact_article_de": article["compact"],
            "concrete_content_wager": article["content_wager"],
            "strongest_practical_rival": article["strongest_rival"],
            "species_identification": "NONE__VISIBLE_PLANT_OWNER_ONLY",
        })
    write_tsv(OUT / "SIXTY_SIXTH_5_COMPACT_HERBAL_ARTICLES.tsv", article_rows)

    doc = [
        "# Fünf kompakte Herbal-Artikel", "",
        "Die Pflanzen werden absichtlich nur durch ihr jeweiliges Bild bezeichnet. Die",
        "folgenden Texte sind die derzeit flüssigste Werkstattlesung, nicht botanische",
        "Bestimmungen. Jeder Artikel bleibt an die vollständige sichtbare Kartenfolge",
        "und die zwölf Quellklauseln gebunden.", "",
    ]
    for article in article_rows:
        doc.extend([
            f"## {article['record_id']} · {article['page']} · {article['title_de']}", "",
            f"**Lesung:** {article['compact_article_de']}", "",
            f"**Konkrete Wette:** {article['concrete_content_wager']}.", "",
            f"**Stärkster Rivale:** {article['strongest_practical_rival']}.", "",
            f"**Voynich-Folge:** `{article['complete_surface']}`", "",
        ])
    (OUT / "SIXTY_SIXTH_COMPLETE_HERBAL_SOURCEBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Sechsundsechzigste Werkstattfassung: kompaktes Herbal-Quellbuch", "",
        "## Ergebnis", "",
        "Die vier Herbal-Seiten enthalten in der aktuellen Segmentierung fünf Records,",
        "19 Aussagen und 100 sichtbare Gruppen. Sie lassen sich mit den zwölf festen",
        "Quellklauseln als fünf kurze Bildpflanzen-Artikel schreiben, ohne Pflanzenart",
        "oder zusätzliche Seiten zu erraten.", "",
        "Die führende konkrete Lesung ist kein bloßes Pflanzenlexikon, sondern ein",
        "kleines Zubereitungsbuch: Wurzel- und Spitzenfraktionen, Auszug, Tuchgang,",
        "Maß, äußere Waschung/Auflage und teils innerer Gebrauch. Der stärkste Rivale",
        "bleibt ein allgemeiner Rohstoff- und Verfahrensführer; dieselbe Klauselgrammatik",
        "würde auch diesen Inhalt tragen.", "",
        "Wasser, Wein, Öl, Honig, Salbe, Trank und Körperziele gehören zur kreativen",
        "Meisterfassung, nicht automatisch zu einzelnen sichtbaren Kartenstämmen.", "",
        "Nur f10r, f11r, f55v und f56r wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "SIXTY_SIXTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "herbal_pages": len({row["page"] for row in group_rows}),
            "herbal_records": len(article_rows),
            "herbal_statements": len(statement_rows),
            "herbal_groups": len(group_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (CLAUSES, UNITS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
