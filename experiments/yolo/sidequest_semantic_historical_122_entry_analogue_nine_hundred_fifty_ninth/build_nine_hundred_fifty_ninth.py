#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CODEBOOK = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_122_ENTRY_CODEBOOK.tsv"
PAGES = ROOT / "experiments/yolo/sidequest_semantic_canonical_122_entry_edition_nine_hundred_fifty_eighth/PASS958_14_CANONICAL_PAGE_READINGS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SOURCES = [
    {
        "source_id": "S01", "date": "c.1425", "object": "Wellcome MS.8515",
        "mechanism": "PRACTICAL_ASTRO_MEDICAL_COMPENDIUM",
        "direct_parallel_de": "Kalender-, Astronomie- und Astrologietafeln; Tierkreis und Arzneigabe; später eingetragene Rezepte im selben kleinen Arbeitsband.",
        "supports": "BOOK_PURPOSE|CELESTIAL_LOOKUP|MEDICAL_RECIPE_ADDITION",
        "url": "https://wellcomecollection.org/works/w9nkm98w",
    },
    {
        "source_id": "S02", "date": "c.1454", "object": "Wellcome MS.8004",
        "mechanism": "UNIFIED_MEDICAL_ASTROLOGICAL_BOOK_CAMPAIGN",
        "direct_parallel_de": "Medizinische und astronomische Texte und Tafeln als einheitlich hergestelltes Fachkompendium für einen Besitzer.",
        "supports": "BOOK_PURPOSE|MULTIPLE_REGISTER_TYPES|WORKSHOP_PRODUCTION",
        "url": "https://wellcomecollection.org/works/gcgpe44f",
    },
    {
        "source_id": "S03", "date": "1420", "object": "British Library Royal MS 17 A XVI",
        "mechanism": "PICTORIAL_ALMANAC_AND_ADDRESS_TABLES",
        "direct_parallel_de": "Bildkalender, Tierkreis, Planetentafeln, Fixsternpositionen, Piktogramm-Prognostik und Volvelle in einem kleinen Pergamentband.",
        "supports": "PICTURE_ADDRESS|CELESTIAL_NAMESPACE|TABLE_AND_RING_LAYOUT",
        "url": "https://searcharchives.bl.uk/catalog/040-002107247",
    },
    {
        "source_id": "S04", "date": "15. Jh.", "object": "Bodleian MS Rawlinson c.299",
        "mechanism": "REMEDY_BOOK_WITH_ABBREVIATION_AND_PICTORIAL_ENTRY_KEYS",
        "direct_parallel_de": "Rezeptbuch mit Abbreviaturzeichen, eigenem Unzenzeichen, bebilderten Uringlas-Einträgen und einer Tierkreisliste.",
        "supports": "TECHNICAL_ABBREVIATION|MEASURE_SIGN|PICTURE_OWNED_ENTRY",
        "url": "https://www.cambridge.org/core/journals/medical-history/article/evidence-for-the-continued-use-of-medieval-medical-prescriptions-in-the-sixteenth-century-a-fifteenthcentury-remedy-book-and-its-later-owner/95663D54A46819495D78EE9BF7FC88EA",
    },
    {
        "source_id": "S05", "date": "ca.1400–1560 corpus", "object": "English practical miscellanies",
        "mechanism": "PRACTICAL_MISCELLANY_AND_REFERENCE_ORGANIZATION",
        "direct_parallel_de": "Herbalglossare, Gewichts- und Maßtexte, Rezeptkalender und Indizes begegnen gemeinsam in praxisorientierten Sammelhandschriften.",
        "supports": "RECIPE_REGISTER|MEASURE_VOCABULARY|MIXED_REFERENCE_BOOK",
        "url": "https://www.cambridge.org/core/journals/journal-of-british-studies/article/abs/here-is-a-good-boke-to-lerne-practical-books-the-coming-of-the-press-and-the-search-for-knowledge-ca-14001560/8217EBC4F6CE53F1084709587B7C2E12",
    },
    {
        "source_id": "S06", "date": "1379–1435", "object": "Northern Italian diplomatic cipher keys",
        "mechanism": "PRODUCTIVE_SIGN_SYSTEM_PLUS_NOMENCLATOR",
        "direct_parallel_de": "Kleine produktive Zeichenmenge neben auswendig gelernten ganzen Codeeinträgen; stärkstes Architekturanalogon für Stamm plus Ganzkarte.",
        "supports": "ROOT_PLUS_WHOLE_CARD_ARCHITECTURE|MULTISCRIBE_TEACHABILITY",
        "url": "https://archive.org/details/diegeheimschrif00meisgoog",
    },
]


ADDRESS_ROOTS = {"AL", "AR", "AM_ADDR", "A_ADDR", "S_ADDR", "Z_ADDR", "D_LABEL", "S_LABEL", "M_LOCAL", "LOCAL_CHAR_B", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_J", "LOCAL_CHAR_Z"}
MEASURE_ROOTS = {"AIIN", "AIN", "IIN", "E", "EE", "EEE", "DA", "T"}
PROCESS_ROOTS = {"OK", "O", "OL", "OT", "CH", "SH", "K", "CHD", "L", "P", "CTH", "SHED", "CKH", "CHEO", "AIR", "CHK", "SOLK", "LSH", "CPH", "CFH", "LD"}


def mechanism_for_root(root: str) -> tuple[str, str, str]:
    if root in ADDRESS_ROOTS:
        return "PICTORIAL_TABLE_ADDRESS", "S03|S04", "Bild, Ring oder Tabelle liefert den Besitzer; das Zeichen wählt nur die Stelle."
    if root in MEASURE_ROOTS:
        return "TECHNICAL_MEASURE_OR_GRADE_ABBREVIATION", "S04|S05", "Kurze Maß-, Stufen- und Gradzeichen sind in praktischen Fachbüchern erwartbar."
    if root in PROCESS_ROOTS:
        return "PRODUCTIVE_WORKSHOP_BREVIGRAPH", "S04|S05|S06", "Wiederverwendbares Handlungskürzel; die konkrete Sache kommt aus Bild und Eintrag."
    return "SMALL_PRODUCTIVE_CONTROL_SIGN", "S03|S06", "Kurzes Steuer- oder Verweiszeichen innerhalb eines bildgestützten Registers."


def main() -> None:
    entries = read_tsv(CODEBOOK)
    pages = read_tsv(PAGES)
    write_tsv(OUT / "PASS959_HISTORICAL_SOURCES.tsv", SOURCES)

    crosswalk: list[dict[str, object]] = []
    for row in entries:
        if row["entry_type"] == "PRODUCTIVE_ROOT":
            mechanism, sources, explanation = mechanism_for_root(row["recognition_form"])
            predicted_behavior = "produktiv mit anderen Einträgen kombinierbar"
        else:
            mechanism = "MEMORIZED_NOMENCLATOR_OR_FORMULA_CARD"
            sources = "S04|S06"
            explanation = "Mehrteilige Karte wird als gelernter Werkstatteintrag erkannt; ihre innere Form unterstützt das Merken, muss aber nicht frei erzeugt werden."
            predicted_behavior = "als ganze Karte stabil, nur ihre belegten Rendererformen verwenden"
        crosswalk.append({
            "codebook_entry_id": row["codebook_entry_id"],
            "entry_type": row["entry_type"],
            "recognition_form": row["recognition_form"],
            "short_value_de": row["short_value_de"],
            "historical_mechanism": mechanism,
            "source_ids": sources,
            "why_it_fits_de": explanation,
            "predicted_scribal_behavior_de": predicted_behavior,
        })
    write_tsv(OUT / "PASS959_122_ENTRY_HISTORICAL_CROSSWALK.tsv", crosswalk)

    page_rows: list[dict[str, object]] = []
    for row in pages:
        page = row["physical_page"]
        if page.startswith("f6") or page.startswith("f70"):
            archetype, sources = "PICTORIAL_CELESTIAL_LOOKUP", "S01|S02|S03"
        elif page in {"f75r", "f81v", "f82r", "f83r"}:
            archetype, sources = "PICTURE_OWNED_APPLICATION_OR_STATION_REGISTER", "S01|S04|S05"
        elif page == "f88r":
            archetype, sources = "MEASURED_PREPARATION_REGISTER", "S04|S05"
        else:
            archetype, sources = "ILLUSTRATED_SIMPLE_OR_RECIPE_ARTICLE", "S01|S04|S05"
        page_rows.append({
            "physical_page": page,
            "register": row["book_stage"],
            "historical_archetype": archetype,
            "source_ids": sources,
            "current_reading_de": row["canonical_page_reading_de"],
        })
    write_tsv(OUT / "PASS959_14_PAGE_HISTORICAL_CROSSWALK.tsv", page_rows)

    mech = Counter(row["historical_mechanism"] for row in crosswalk)
    report = f"""# Pass 959 — das historische Mischsystem hinter dem 122er-Codebuch

## Bester Treffer

Kein einzelnes erhaltenes Buch liefert exakt unsere 56 Stämme und 66 Karten.
Die passende **Werkstattmechanik** existiert aber in unmittelbarer zeitlicher
Nähe: ein kleines produktives Kürzelalphabet, gelernte ganze Fachkarten,
bild- oder tabellengetragene Besitzer und mehrere Sachregister in einem
praktischen Kompendium.

Der engste Zweckvergleich ist **Wellcome MS.8515, um 1425**: ein sorgfältig
zusammengestelltes Handbuch der Kalenderrechnung, Astronomie und astrologischen
Medizin, in das medizinische Rezepte eingetragen wurden. **Royal MS 17 A XVI,
1420** zeigt, wie Bildkalender, Tierkreis, Fixsternpositionen, Piktogramme,
Tabellen und ein drehbares Rad gemeinsam als Adress- und Nachschlagesystem
funktionieren. **Rawlinson c.299** zeigt die andere Hälfte: Fachabbreviaturen,
ein eigenes Maßzeichen, Bildbesitzer am Eintragsbeginn und medizinische
Rezeptfolgen. Die italienischen Chiffreschlüssel liefern die genaue
Lernarchitektur: produktive Zeichen plus gelernter Nomenklator.

## Was das für unsere Karten bedeutet

- Die **56 Stämme** verhalten sich wie ein kleines technisches Kürzel- und
  Adressalphabet. Sie müssen nicht 56 Wörter einer gesprochenen Sprache sein.
- Die **66 Mehrteilkarten** verhalten sich wie Nomenklator- oder
  Formulareinträge: ihre Teile helfen beim Erkennen, die Karte wird dennoch als
  ganzer Werkstattwert gelernt.
- Pflanzen, Becken, Figuren und Sternplätze liefern stille Besitzer. Deshalb
  kann dieselbe Adresskarte im Kräuterartikel, Badregister und Himmelsrad
  vorkommen, ohne dort dasselbe Substantiv zu bedeuten.
- Mehrere Hände lernen 122 Einträge plausibel aus einer Meistertafel: zuerst
  die produktiven Stämme, danach häufige Ganzkarten, zuletzt lokale Bildkarten.

## Historische Aufteilung des Inventars

{dict(mech)}

## Ergebnis

Die stärkste Arbeitstheorie ist jetzt kein gewöhnlicher Geheimtext und auch
keine reine natürliche Wortschrift. Sie ist ein **bildadressiertes
Werkstattregister mit Fachbrevigrafen und gelerntem Nomenklator**. Das erklärt
zugleich Komposition, memorierte Ausnahmen, mehrere Hände und den Wechsel von
Pflanzen über Bade-/Stationsbilder zu Himmelsrädern. Es bestätigt nicht jedes
deutsche Lemma; es liefert aber genau den historischen Mechanismus, mit dem
unsere Lemmas und Formelkarten erzeugt und gelehrt werden können.

## Quellen

- Wellcome MS.8515: https://wellcomecollection.org/works/w9nkm98w
- Wellcome MS.8004: https://wellcomecollection.org/works/gcgpe44f
- Royal MS 17 A XVI: https://searcharchives.bl.uk/catalog/040-002107247
- Rawlinson c.299: https://www.cambridge.org/core/journals/medical-history/article/evidence-for-the-continued-use-of-medieval-medical-prescriptions-in-the-sixteenth-century-a-fifteenthcentury-remedy-book-and-its-later-owner/95663D54A46819495D78EE9BF7FC88EA
- Practical miscellanies: https://www.cambridge.org/core/journals/journal-of-british-studies/article/abs/here-is-a-good-boke-to-lerne-practical-books-the-coming-of-the-press-and-the-search-for-knowledge-ca-14001560/8217EBC4F6CE53F1084709587B7C2E12
- Northern Italian cipher keys: https://archive.org/details/diegeheimschrif00meisgoog
"""
    (OUT / "PASS959_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS959_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "sources": len(SOURCES),
        "codebook_entries": len(crosswalk),
        "productive_roots": sum(row["entry_type"] == "PRODUCTIVE_ROOT" for row in crosswalk),
        "learned_formulas": sum(row["entry_type"] == "LEARNED_FORMULA" for row in crosswalk),
        "pages": len(page_rows),
        "mechanism_counts": mech,
        "outputs": outputs,
    }
    (OUT / "PASS959_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
