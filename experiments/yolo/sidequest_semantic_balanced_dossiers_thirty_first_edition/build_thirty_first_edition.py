#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / "experiments/yolo/sidequest_semantic_integrated_workshop_casebook/FOUR_WORKSHOP_DOSSIERS.tsv"
BALANCED = ROOT / "experiments/yolo/sidequest_semantic_balanced_continuous_twenty_seventh_edition/TWENTY_SEVENTH_11_BALANCED_RECORDS.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


REVISIONS = {
    "D1_ROOT_BATH_RIGHT_WHEEL": {
        "title": "Wurzel und zwei Pflanzenfraktionen im gemeinsamen Becken",
        "condition": "Am rechten f67r2-Rad einen sichtbaren Sektor wählen, zugehörige Ringregel und Phasenstelle lesen und den lokalen Wert zum Arbeitsfall notieren.",
        "output": "bemessener Pflanzen-/Wurzelauszug nach gemeinsamem Becken-, Wasch- und Ablaufprogramm",
        "rival": "Pflanzenmaterial- und Badehausauftrag mit astronomischer Kalendernotiz",
    },
    "D2_CLEAR_EXTRACT_STAR_ATLAS": {
        "title": "Zweistufig geklärter Pflanzenauszug im Sternstationsprogramm",
        "condition": "Auf f68r1 zuerst den sichtbaren Paneelmodus und dann eine Sternstation wählen; Zentrum oder Legende nur als lokalen Grad-/Zielschlüssel benutzen.",
        "output": "ausgewrungener, abgesetzter und nachgeseihter Auszug nach lokaler Mehrstationsfolge",
        "rival": "Filtrations- und Wasserwerksauftrag mit astronomischer Ortsklasse",
    },
    "D3_STORED_APPLICATION_THREE_WHEELS": {
        "title": "Gelagerter Auszug, Tuchgang und drei getrennte Radablesungen",
        "condition": "Auf f69v den linken 28-Platz-Eintrag, die mittlere Qualitätsablesung und den rechten Zustandswert getrennt wählen; keine gemeinsame Drehrichtung voraussetzen.",
        "output": "bemessener Tuch-/Einsatzgang mit linker und rechter Unterlaufstation",
        "rival": "Material-, Wasch- und Filterauftrag mit separater astronomischer Arbeitsnotiz",
    },
    "D4_FRESH_PLANT_LEFT_WHEEL": {
        "title": "Kurze Pflanzenauflage und langer Stationsweg am linken Doppelrad",
        "condition": "Am linken f67r2-Rad sichtbares Feld, Aspekt, Quelle und Ziel wählen; äußere Station und Ringregel bleiben lokale Nachschlagewerte.",
        "output": "kurze äußere Pflanzenportion plus getrennte Auszugsportion nach langem Stations- und Übergabeweg",
        "rival": "Frischmaterial- und Beckenbetriebsauftrag mit astronomischem Quellen-/Zielvergleich",
    },
}

old = {row["dossier_id"]: row for row in read(OLD)}
balanced = {row["record_id"]: row for row in read(BALANCED)}
dossier_rows = []
step_rows = []
for dossier_id in (
    "D1_ROOT_BATH_RIGHT_WHEEL",
    "D2_CLEAR_EXTRACT_STAR_ATLAS",
    "D3_STORED_APPLICATION_THREE_WHEELS",
    "D4_FRESH_PLANT_LEFT_WHEEL",
):
    source = old[dossier_id]
    revision = REVISIONS[dossier_id]
    record_ids = source["record_units"].split(";")
    what_ids = [record_id for record_id in record_ids if record_id.startswith("H")]
    how_ids = [record_id for record_id in record_ids if record_id.startswith("B")]
    what_text = " ".join(balanced[record_id]["balanced_continuous_reading_de"] for record_id in what_ids)
    how_text = " ".join(balanced[record_id]["balanced_continuous_reading_de"] for record_id in how_ids)
    what_groups = sum(int(balanced[record_id]["group_count"]) for record_id in what_ids)
    how_groups = sum(int(balanced[record_id]["group_count"]) for record_id in how_ids)
    what_statements = sum(int(balanced[record_id]["statement_count"]) for record_id in what_ids)
    how_statements = sum(int(balanced[record_id]["statement_count"]) for record_id in how_ids)
    when_groups = int(source["astro_group_count"])
    when_loci = int(source["astro_locus_count"])
    dossier_rows.append(
        {
            "dossier_id": dossier_id,
            "title_de": revision["title"],
            "what_records": ";".join(what_ids),
            "how_records": ";".join(how_ids),
            "when_modules": source["astro_modules"],
            "book_order": "WHAT>HOW>WHEN",
            "bench_order": "WHEN>WHAT>HOW",
            "prose_statement_count": what_statements + how_statements,
            "prose_group_count": what_groups + how_groups,
            "astro_locus_count": when_loci,
            "astro_group_count": when_groups,
            "total_group_count": what_groups + how_groups + when_groups,
            "balanced_what_de": what_text,
            "balanced_how_de": how_text,
            "visible_condition_de": revision["condition"],
            "workshop_output_de": revision["output"],
            "strongest_nonmedical_rival_de": revision["rival"],
            "cross_page_pointer": "NONE__MASTER_ASSEMBLES_CASE",
        }
    )
    step_rows.extend(
        [
            {
                "dossier_id": dossier_id,
                "bench_step": 1,
                "phase": "WHEN",
                "source_units": source["astro_modules"],
                "statement_or_locus_count": when_loci,
                "visible_group_count": when_groups,
                "master_instruction_de": revision["condition"],
                "handoff_de": "gewählten sichtbaren Bedingungswert auf dem Arbeitszettel notieren",
            },
            {
                "dossier_id": dossier_id,
                "bench_step": 2,
                "phase": "WHAT",
                "source_units": ";".join(what_ids),
                "statement_or_locus_count": what_statements,
                "visible_group_count": what_groups,
                "master_instruction_de": what_text,
                "handoff_de": "vorbereiteten Pflanzenposten an die lokale Station übergeben",
            },
            {
                "dossier_id": dossier_id,
                "bench_step": 3,
                "phase": "HOW",
                "source_units": ";".join(how_ids),
                "statement_or_locus_count": how_statements,
                "visible_group_count": how_groups,
                "master_instruction_de": how_text,
                "handoff_de": "örtlichen Arbeitsgang schließen und Ergebnis unter der gewählten Bedingung verbuchen",
            },
        ]
    )
write(HERE / "THIRTY_FIRST_FOUR_BALANCED_DOSSIERS.tsv", list(dossier_rows[0]), dossier_rows)
write(HERE / "THIRTY_FIRST_TWELVE_BENCH_STEPS.tsv", list(step_rows[0]), step_rows)

doc = [
    "# Vier ausgewogene Werkstattdossiers",
    "",
    "Das Buch zeigt WHAT → HOW → WHEN; der Meister arbeitet meist WHEN → WHAT →",
    "HOW. Er wählt eine sichtbare Himmelsbedingung, bereitet den Pflanzenposten",
    "und führt danach das lokale Becken-, Tuch- oder Stationsprogramm aus. Diese",
    "Zusammenstellung ist eine Werkstattbenutzung, kein geschriebener Seitenzeiger.",
    "",
]
for row in dossier_rows:
    doc.extend(
        [
            f"## {row['dossier_id']} — {row['title_de']}",
            "",
            f"### 1. WHEN\n\n{row['visible_condition_de']}",
            "",
            f"### 2. WHAT\n\n{row['balanced_what_de']}",
            "",
            f"### 3. HOW\n\n{row['balanced_how_de']}",
            "",
            f"Ausgabe: **{row['workshop_output_de']}**.",
            "",
            f"Nichtmedizinischer Rivale: {row['strongest_nonmedical_rival_de']}",
            "",
        ]
    )
(HERE / "THIRTY_FIRST_FOUR_COMPLETE_BALANCED_DOSSIERS.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

summary = {
    "status": "PASS",
    "counts": {
        "dossiers": len(dossier_rows),
        "bench_steps": len(step_rows),
        "prose_statements": sum(int(row["prose_statement_count"]) for row in dossier_rows),
        "prose_groups": sum(int(row["prose_group_count"]) for row in dossier_rows),
        "astro_loci": sum(int(row["astro_locus_count"]) for row in dossier_rows),
        "astro_groups": sum(int(row["astro_group_count"]) for row in dossier_rows),
        "total_groups": sum(int(row["total_group_count"]) for row in dossier_rows),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
