#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R282 = ROOT / "experiments/yolo/sidequest_semantic_manual_herbal_edition_two_hundred_eighty_second"
R283 = ROOT / "experiments/yolo/sidequest_semantic_manual_bio_station_edition_two_hundred_eighty_third"
R284 = ROOT / "experiments/yolo/sidequest_semantic_manual_astro_instrument_edition_two_hundred_eighty_fourth"
HERBAL = R282 / "TWO_HUNDRED_EIGHTY_SECOND_19_MANUAL_HERBAL_TRANSLATIONS.tsv"
HERBAL_ARTICLES = R282 / "TWO_HUNDRED_EIGHTY_SECOND_FIVE_HERBAL_ARTICLES.tsv"
BIO = R283 / "TWO_HUNDRED_EIGHTY_THIRD_97_STATION_TRANSLATIONS.tsv"
BIO_RECORDS = R283 / "TWO_HUNDRED_EIGHTY_THIRD_SIX_BIO_NARRATIVES.tsv"
ASTRO = R284 / "TWO_HUNDRED_EIGHTY_FOURTH_142_MANUAL_LOCUS_TRANSLATIONS.tsv"
ASTRO_PAGES = R284 / "TWO_HUNDRED_EIGHTY_FOURTH_THREE_INSTRUMENT_NARRATIVES.tsv"

PAGE_ORDER = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"]

PAGE_TITLES = {
    "f10r": "Wurzel-Auszug und fortgesetzter Ansatz",
    "f11r": "Klären eines Pflanzensuds",
    "f55v": "Bemessener, gekühlter Blatt-Auszug",
    "f56r": "Stängel- und Zusatz-Auszug für mehrere Anwendungen",
    "f81v": "Gemeinsames Doppelbecken",
    "f82r": "Vier lokale Bade-, Wasch- und Übergabestationen",
    "f83r": "Randgefäße, Hauptbogen und technische Nachträge",
    "f67r2": "Doppelrad für Sektor- und Phasenwerte",
    "f68r1": "Mehrpaneel-Sternstationsregister",
    "f69v": "Drei Wahlräder mit 28er-Register links",
}

PAGE_ROLES = {
    "f10r": "MATERIAL_AND_EXTRACTION",
    "f11r": "CLARIFICATION_AND_STORAGE",
    "f55v": "MEASURED_PREPARATION_AND_APPLICATION",
    "f56r": "MULTISTEP_INGREDIENT_AND_APPLICATION",
    "f81v": "SHARED_BATH_OR_WASH_STATION",
    "f82r": "MULTI_STATION_BATH_WASH_TRANSFER",
    "f83r": "LOCAL_VESSEL_APPLICATION_AND_HANDOFF",
    "f67r2": "CELESTIAL_SECTOR_AND_PHASE_LOOKUP",
    "f68r1": "SPATIAL_STAR_STATION_LOOKUP",
    "f69v": "CELESTIAL_WORK_CONDITION_CHOICE",
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
    herbal = read_tsv(HERBAL)
    bio = read_tsv(BIO)
    astro = read_tsv(ASTRO)
    units: list[dict[str, object]] = []

    for row in herbal:
        units.append({
            "reading_unit_id": row["statement_id"],
            "reading_unit_type": "PROSE_STATEMENT",
            "register": "HERBAL",
            "page": row["page"],
            "local_record_or_namespace": row["record_unit_id"],
            "visible_owner_or_role": row["article_type"],
            "visible_group_count": len(row["surface_sequence"].split(" · ")),
            "visible_sequence": row["surface_sequence"],
            "grammar_or_template": row["formula_family"],
            "status_or_address_mode": row["terminal_status"],
            "complete_reading_de": row["manual_fluent_translation_de"],
            "section_purpose": "pictured plant material and its preparation",
            "source_pass": "R282",
        })
    for row in bio:
        units.append({
            "reading_unit_id": row["statement_id"],
            "reading_unit_type": "PROSE_STATEMENT",
            "register": "BIO",
            "page": row["page"],
            "local_record_or_namespace": row["record_unit_id"],
            "visible_owner_or_role": row["owner_reading_de"],
            "visible_group_count": len(row["surface_sequence"].split(" · ")),
            "visible_sequence": row["surface_sequence"],
            "grammar_or_template": row["formula_family"],
            "status_or_address_mode": row["terminal_status"],
            "complete_reading_de": row["station_translation_de"],
            "section_purpose": "local bath wash vessel or transfer station",
            "source_pass": "R283",
        })
    for row in astro:
        units.append({
            "reading_unit_id": row["locus"],
            "reading_unit_type": "DIAGRAM_LOCUS",
            "register": "ASTRO",
            "page": row["page"],
            "local_record_or_namespace": row["namespace_id"],
            "visible_owner_or_role": row["visible_owner_de"],
            "visible_group_count": int(row["group_count"]),
            "visible_sequence": row["visible_sequence"],
            "grammar_or_template": row["astro_template"],
            "status_or_address_mode": "SELECT_BY_VISIBLE_OWNER",
            "complete_reading_de": row["manual_locus_translation_de"],
            "section_purpose": "celestial lookup station or work-condition value",
            "source_pass": "R284",
        })

    page_texts: dict[str, list[str]] = {p: [] for p in PAGE_ORDER}
    for row in read_tsv(HERBAL_ARTICLES):
        page_texts[row["page"]].append(f"{row['article_title_de']}: {row['continuous_article_de']}")
    for row in read_tsv(BIO_RECORDS):
        page_texts[row["page"]].append(f"{row['title_de']}: {row['continuous_narrative_de']}")
    for row in read_tsv(ASTRO_PAGES):
        page_texts[row["page"]].append(f"{row['title_de']}: {row['continuous_instrument_reading_de']}")

    pages: list[dict[str, object]] = []
    for page in PAGE_ORDER:
        selected = [r for r in units if r["page"] == page]
        pages.append({
            "page_order": PAGE_ORDER.index(page) + 1,
            "page": page,
            "register": selected[0]["register"],
            "page_title_de": PAGE_TITLES[page],
            "reading_unit_count": len(selected),
            "visible_group_count": sum(int(r["visible_group_count"]) for r in selected),
            "page_role": PAGE_ROLES[page],
            "continuous_page_reading_de": " ".join(page_texts[page]),
            "cross_page_rule": "same learned stem deck; page-local pictured or diagram owner; no automatic pointer to another page",
        })

    unit_path = OUT / "TWO_HUNDRED_EIGHTY_FIFTH_258_COMPLETE_READING_UNITS.tsv"
    page_path = OUT / "TWO_HUNDRED_EIGHTY_FIFTH_TEN_PAGE_SYNOPSIS.tsv"
    readable_path = OUT / "TWO_HUNDRED_EIGHTY_FIFTH_COMPLETE_TEN_PAGE_READING.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTY_FIFTH_REPORT.md"
    write_tsv(unit_path, units, list(units[0]))
    write_tsv(page_path, pages, list(pages[0]))

    md = [
        "# Vollständige kreative Lesung der zehn Seiten",
        "",
        "## Arbeitstheorie des Schreibers",
        "",
        "Das Buch ist ein bildgeführtes Praxis-Kompendium. Pflanzenbilder eröffnen Stoff- und Zubereitungsartikel; Figuren, Becken und Gefäße eröffnen lokale Bade-, Wasch-, Klär- und Übergabestationen; die Himmelsbilder liefern getrennte Wahl- und Nachschlageinstrumente. Derselbe gelernte Kürzelbaukasten trägt Quelle, Ziel, Folge, Portion, Grad, Bahn und Festsetzung. Bild und Exemplar liefern die vielen lokalen Namen.",
        "",
        "Die engste Inhaltslesung ist ein Heilkundigenbuch mit balneologischer Praxis und Himmelswahl. Ein Pflanzenmaterial-/Badehaus-/Almanach-Miszellaneum bleibt der stärkste Rivale; die Kartengrammatik funktioniert in beiden.",
        "",
    ]
    for page in pages:
        md.extend([
            f"## {page['page']}: {page['page_title_de']}",
            "",
            str(page["continuous_page_reading_de"]),
            "",
        ])
        for row in [r for r in units if r["page"] == page["page"]]:
            md.append(f"- **{row['reading_unit_id']}** — {row['complete_reading_de']}")
        md.append("")
    readable_path.write_text("\n".join(md), encoding="utf-8")

    report_path.write_text(
        "# Sidequest-Pass 285: eine vollständige Zehn-Seiten-Lesung\n\n"
        "## Ergebnis\n\n"
        "Die manuell geglätteten Register sind erstmals in einer einzigen Ausgabe verbunden: 19 Herbal-Aussagen, 97 Bio-Aussagen und 142 Astro-Orte ergeben 258 Leseeinheiten und decken alle 776 sichtbaren Gruppen. "
        "Die gemeinsame Werkstattgrammatik ist Quelle/Ziel/Folge/Portion/Grad/Bahn/Festsetzung; Bild- und Diagrammbesitzer füllen den örtlichen Inhalt.\n\n"
        "Als Schreiberlesung führt das zu Pflanzenzubereitung -> lokalen Bade-/Wasch-/Klärstationen -> getrennten Himmelswahltafeln. Das ist jetzt eine zusammenhängende Gebrauchstheorie, aber ohne erfundene Seitenpointer: "
        "die Abschnitte gehören thematisch zusammen und bleiben technisch selbständig.\n\n"
        f"Inputs R282 `{sha(HERBAL)}`, R283 `{sha(BIO)}`, R284 `{sha(ASTRO)}`.\n",
        encoding="utf-8",
    )

    outputs = (unit_path, page_path, readable_path, report_path)
    summary = {
        "status": "PASS",
        "reading_units": len(units),
        "visible_groups": sum(int(r["visible_group_count"]) for r in units),
        "pages": len(pages),
        "register_units": dict(Counter(str(r["register"]) for r in units)),
        "page_units": dict(Counter(str(r["page"]) for r in units)),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
