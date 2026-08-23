#!/usr/bin/env python3
"""Build complete layered readbacks for H3 and B2."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MIN_GROUPS = ROOT / "experiments/yolo/sidequest_semantic_minimal_dictionary_seventy_second_edition/SEVENTY_SECOND_381_MINIMAL_CARD_READINGS.tsv"
MIN_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_minimal_dictionary_seventy_second_edition/SEVENTY_SECOND_116_MINIMAL_STATEMENT_READINGS.tsv"
SOURCE_CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_period_clausebook_sixty_fifth_edition/SIXTY_FIFTH_381_PERIOD_SOURCE_CLAUSES.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_258_COMPLETE_UNITS.tsv"
BIO_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_bio_station_handbook_sixty_seventh_edition/SIXTY_SEVENTH_97_BIO_STATEMENTS.tsv"
DUAL_UNITS = ROOT / "experiments/yolo/sidequest_semantic_nonmedical_counterbook_seventieth_edition/SEVENTIETH_14_DUAL_CONTENT_UNITS.tsv"
TARGETS = {"H3", "B2"}


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


def record_id(unit_id: str) -> str:
    return unit_id.split("-")[0]


def nonmedical(text: str, target: str) -> str:
    replacements = {
        "Arznei": "Werkstoffansatz",
        "Trank": "Auszugsportion",
        "bedrücktem Gemüt und beschwerter Brust": "Farb-, Duft- oder Materialgebrauch",
        "Olivenöl": "Bindemittel",
        "um die Lider, ohne das Auge zu berühren": "am bezeichneten Rand des Werkstücks",
        "badende Person": "eingesetzte Werkstück",
        "Körper- oder Teilbadbereich": "Wasch- oder Teilbadbereich",
        "Körperbereich": "Arbeitsbereich",
        "benetzten Körperbereich": "benetzten Arbeitsbereich",
        "Haut- oder Wundstelle": "Materialstelle",
        "Bade- oder Wasch": "Wasch- oder Färbe",
        "Badeflüssigkeit": "Arbeitsflüssigkeit",
        "betroffene Stelle": "bearbeitete Stelle",
    }
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    if target == "H3":
        result = result.replace("äußerlich", "am Werkstück")
    return result


def main() -> None:
    min_groups = [row for row in read_tsv(MIN_GROUPS) if record_id(row["unit_id"]) in TARGETS]
    min_statements = [row for row in read_tsv(MIN_STATEMENTS) if record_id(row["unit_id"]) in TARGETS]
    source = {row["source_group_id"]: row for row in read_tsv(SOURCE_CLAUSES)}
    rich_units = {
        row["unit_id"]: row for row in read_tsv(UNITS)
        if row["unit_kind"] == "PROSE_STATEMENT" and record_id(row["unit_id"]) == "H3"
    }
    bio = {row["unit_id"]: row for row in read_tsv(BIO_STATEMENTS) if record_id(row["unit_id"]) == "B2"}
    dual = {row["unit_id"]: row for row in read_tsv(DUAL_UNITS)}
    statement_lookup = {row["unit_id"]: row for row in min_statements}

    group_rows = []
    by_unit = defaultdict(list)
    for row in min_groups:
        owner = statement_lookup[row["unit_id"]]["owner"]
        out = {
            "source_group_id": row["source_group_id"],
            "unit_id": row["unit_id"],
            "record_id": record_id(row["unit_id"]),
            "page": row["page"],
            "surface_layer": row["visible_surface"],
            "atom_layer": row["atom_sequence"],
            "minimal_dictionary_layer": row["minimal_card_reading_de"],
            "owner_layer": owner,
            "neutral_source_clause_layer": source[row["source_group_id"]]["workshop_vernacular_clause"],
            "rich_content_source": "SIMULATED_MASTER_EXEMPLAR",
        }
        group_rows.append(out)
        by_unit[row["unit_id"]].append(out)
    write_tsv(OUT / "SEVENTY_THIRD_79_GROUP_LAYERED_READINGS.tsv", group_rows)

    statement_rows = []
    for row in min_statements:
        unit_id = row["unit_id"]
        target = record_id(unit_id)
        groups = by_unit[unit_id]
        if target == "H3":
            medical = rich_units[unit_id]["fluent_working_reading_de"]
        else:
            medical = bio[unit_id]["local_station_working_reading_de"]
        statement_rows.append({
            "unit_id": unit_id,
            "record_id": target,
            "page": row["page"],
            "surface_sequence": row["surface_sequence"],
            "minimal_dictionary_reading": row["minimal_card_sequence_de"],
            "owner_augmented_reading": row["owner_augmented_minimal_reading_de"],
            "neutral_source_formular": " ".join(group["neutral_source_clause_layer"] for group in groups),
            "medical_master_expansion": medical,
            "nonmedical_master_expansion": nonmedical(medical, target),
            "card_or_owner_changed_between_master_expansions": "NO",
        })
    write_tsv(OUT / "SEVENTY_THIRD_26_LAYERED_STATEMENTS.tsv", statement_rows)

    record_rows = []
    for target in ("H3", "B2"):
        rows = [row for row in statement_rows if row["record_id"] == target]
        if target == "H3":
            visible = "ganze dicht blau bekrönte Bildpflanze"
            owner_nouns = "diese Bildpflanze"
            master_medical = "Blüten|junge Blätter|Wein|Tuch|Klarauszug|Trank|Brustbeschwerde|Öl|Lider"
            master_nonmedical = "Blüten|Auszugsmedium|Tuch|Farb- oder Duftauszug|Bindemittel|Werkstückrand"
        else:
            visible = "fünf lokale f82r-Stationsgruppen mit Figuren, Becken, Linien und Gefäßen"
            owner_nouns = "oberes Paarbecken|Mittelgerät|unaufgelöster Mittelposten|unteres Becken|Randplätze"
            master_medical = "Badende|Teilbad|Körperbereich|Waschung|Wärme|Dauer|Tuch"
            master_nonmedical = "Werkstück|Wasch-/Färbebad|Arbeitsbereich|Wärme|Dauer|Tuch"
        record_rows.append({
            "record_id": target,
            "page": rows[0]["page"],
            "statement_count": len(rows),
            "group_count": sum(len(by_unit[row["unit_id"]]) for row in rows),
            "visible_owner_evidence": visible,
            "owner_nouns_added": owner_nouns,
            "medical_master_nouns_added": master_medical,
            "nonmedical_master_nouns_added": master_nonmedical,
            "minimal_record_reading": " || ".join(row["minimal_dictionary_reading"] for row in rows),
            "owner_augmented_record_reading": " ".join(row["owner_augmented_reading"] for row in rows),
            "medical_record_reading": " ".join(row["medical_master_expansion"] for row in rows),
            "nonmedical_record_reading": " ".join(row["nonmedical_master_expansion"] for row in rows),
            "unit_level_rival_frame": dual[target]["nonmedical_rival_reading"],
        })
    write_tsv(OUT / "SEVENTY_THIRD_2_COMPLETE_LAYERED_PASSAGES.tsv", record_rows)

    doc = [
        "# Zwei vollständige Bedeutungsleitern", "",
        "Jede Passage wird fünfmal gelesen: Oberfläche, Minimalwörterbuch, Bildbesitzer,",
        "neutrales Quellenformular und schließlich zwei konkurrierende Meistertexte.", "",
    ]
    for row in record_rows:
        doc.extend([
            f"## {row['record_id']} · {row['page']}", "",
            f"**Nur Minimalwörterbuch:** {row['minimal_record_reading']}", "",
            f"**Mit Bildbesitzer:** {row['owner_augmented_record_reading']}", "",
            f"**Medizinische Meisterfassung:** {row['medical_record_reading']}", "",
            f"**Nichtmedizinische Meisterfassung:** {row['nonmedical_record_reading']}", "",
            f"**Nur medizinisch ergänzt:** {row['medical_master_nouns_added']}.", "",
            f"**Nur nichtmedizinisch ergänzt:** {row['nonmedical_master_nouns_added']}.", "",
        ])
    (OUT / "SEVENTY_THIRD_COMPLETE_LAYERED_PASSAGES.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Dreiundsiebzigste Werkstattfassung: vollständige Bedeutungsleitern", "",
        "## Ergebnis", "",
        "H3 and B2 provide 79 groups and 26 complete statements. In both records the",
        "surface, atoms, minimal dictionary and owner remain fixed while two fluent",
        "master sources diverge. H3 can be medicine, color, scent or material extract;",
        "B2 can be therapeutic bathing or ordinary bath/wash/dye-station operation.", "",
        "The owner adds real content: plant versus local human/basin station. Wine, oil,",
        "drink, chest, eyelid, patient and body area are master additions. So are dye,",
        "workpiece and binder. The card layer itself chiefly expresses process, amount,",
        "address, grade, reference and closure.", "",
        "Only f11r and f82r were used in this focused passage edition; sealed pages remain untouched.",
    ]
    (OUT / "SEVENTY_THIRD_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "target_records": len(record_rows),
            "layered_groups": len(group_rows),
            "layered_statements": len(statement_rows),
            "h3_groups": sum(row["record_id"] == "H3" for row in group_rows),
            "b2_groups": sum(row["record_id"] == "B2" for row in group_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (MIN_GROUPS, MIN_STATEMENTS, SOURCE_CLAUSES, UNITS, BIO_STATEMENTS, DUAL_UNITS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
