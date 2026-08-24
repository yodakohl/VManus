#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P389 = ROOT / "experiments/yolo/sidequest_semantic_five_card_reanalysis_three_hundred_eighty_ninth"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_173_THERMAL_TEMPORAL_DICTIONARY.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_116_THERMAL_TEMPORAL_SENTENCES.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    practice = read(P389 / "THREE_HUNDRED_EIGHTY_NINTH_REVISED_14_LAYERED_READINGS.tsv")
    dictionary = {row["joint_tuple_id"]: row for row in read(DICTIONARY)}
    provenance_rows = []
    for row in practice:
        entry = dictionary[row["joint_tuple_id"]]
        records = entry["records"].split("|")
        practice_owner = row["owner_code"]
        native = practice_owner in records
        provenance_rows.append({
            "source_position": row["source_position"],
            "surface": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "practice_owner": row["owner_code"],
            "atomic_reading_de": row["atomic_reading_de"],
            "real_records": entry["records"],
            "real_pages": entry["pages"],
            "practice_owner_native_card": "YES" if native else "NO",
            "provenance_role": f"{practice_owner}_ATTESTED" if native else "CROSS_REGISTER_TEACHING_BORROWING",
            "claim_limit": "TEACHING_SYNTHESIS_NOT_H4_TRANSLATION",
        })
    write("THREE_HUNDRED_NINETY_FIRST_14_PRACTICE_CARD_PROVENANCE.tsv", provenance_rows)

    selected_statements = [row for row in read(STATEMENTS) if row["record_unit_id"] in {"H3", "H4"}]
    genuine_rows = []
    for row in selected_statements:
        genuine_rows.append({
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "field_ids": row["field_ids"],
            "event_ids": row["event_ids"],
            "surface_sequence": row["surface_sequence"],
            "card_sequence_de": row["card_sequence_de"],
            "workshop_sentence_de": row["workshop_sentence_de"],
            "status": "GENUINE_FIXED_PAGE_SEQUENCE",
        })
    write("THREE_HUNDRED_NINETY_FIRST_EIGHT_GENUINE_H3_H4_STATEMENTS.tsv", genuine_rows)

    stages = [
        ("MATERIAL", "tshol", "sho", "silent pictured owner", "practice uses an H5 material card; H4 genuine leaves plant owner elliptic"),
        ("MEASURE_PREPARE", "schoal", "or", "qokaiin/chaiin/ykaiin/aiin/or/orain", "both genuine entries prepare material but H4 foregrounds measure and portion"),
        ("EXTRACT", "cfhy", "cheoar", "cheoar", "CHEOAR is the strongest exact H4-native bridge"),
        ("HEAT", "schoal", "cheky", "cheeky/oltchy", "H3 boils; H4 genuine uses longer warming and warming-up cards"),
        ("STAND", "shfydaiin", "NONE", "NONE", "only genuine H3 explicitly names standing time"),
        ("SECOND_SEPARATION", "cphy", "cphy", "NONE", "exact match is a deliberate H3 borrowing in the practice page"),
        ("RESULT_STATE", "shey", "checthy", "or/orain/oldy", "practice generalizes ready; genuine H4 continues the batch instead"),
        ("TARGET", "NONE", "lcheey", "okal", "practice borrows B2 wet-site card; genuine H4 uses the portable AL target"),
        ("COOL_STORE_CLOSE", "tchody", "talam", "ody/talam/oldy", "TALAM is genuinely H4-native; H3 cools and closes"),
    ]
    stage_rows = [
        {
            "functional_stage": stage,
            "genuine_h3": h3,
            "practice_h4_owner": practice_value,
            "genuine_h4": h4,
            "interpretation": note,
        }
        for stage, h3, practice_value, h4, note in stages
    ]
    write("THREE_HUNDRED_NINETY_FIRST_NINE_STAGE_ALIGNMENT.tsv", stage_rows)

    correction = """# Pass 391 — echte Folgen und Lehrstück getrennt

## Echte H3-Kernfolge

`tshol schoal cfhy shfydaiin cphy shey tchody`

Blütenkraut; Sud; auswringen; Stehzeit; nachseihen; Klarauszug; abkühlen und
schließen.

## Echte H4-Folge in vier Aussagen

`qokaiin chaiin ykain ykan ody | daiin chedy talam | ykaiin cheoar cheeky oldy | aiin okal oltchy or y orain`

H4 arbeitet stärker mit Sollmaß, Portion, Zielstelle, Auszug, Wärme,
Fortsetzung und Verwahrung.

## Unser H4-besessenes Lehrstück

`sho or cheoar cheky | lcheey cphy checthy`

Es ist eine **registergemischte Werkstattübung**, keine Übersetzung eines echten
H4-Satzes. Nur die Provenanztabelle entscheidet, welche Karte H4 selbst belegt.
Die exakte CPHY-Gemeinsamkeit mit H3 entstand durch unsere bewusste Übernahme und
darf nicht als unabhängiger Crosspage-Fund gezählt werden.
"""
    (HERE / "THREE_HUNDRED_NINETY_FIRST_CORRECTION_NOTE.md").write_text(correction, encoding="utf-8")
    native_count = sum(row["practice_owner_native_card"] == "YES" for row in provenance_rows)
    h4_native = sum(row["practice_owner"] == "H4" and row["practice_owner_native_card"] == "YES" for row in provenance_rows)
    b3_native = sum(row["practice_owner"] == "B3" and row["practice_owner_native_card"] == "YES" for row in provenance_rows)
    report = f"""# Pass 391 — Provenienzkorrektur der Übungsseite

In der oberen H4-Hälfte sind {h4_native}/7 Karten auch im echten H4-Record
belegt; in der unteren B3-Hälfte sind es {b3_native}/7. Insgesamt sind damit
{native_count}/14 Karten beim jeweils sichtbaren Besitzer belegt, während
{14 - native_count} aus anderen festen Seitenregistern in die Übung übernommen
wurden. Das ist für ein Werkstatt-Lehrblatt zulässig, macht es aber nicht zu
einer Übersetzung der beiden echten Records.

Der dreiwegige Vergleich schärft die Inhaltsunterschiede. H3 bildet eine
Trennkette mit Stehzeit, Nachseihen und Klarauszug. H4 bildet eine Maß-,
Portions-, Ziel-, Wärme- und Verwahrungskette. Unser Lehrstück mischt beide, um
die gemeinsame Kartengrammatik zu üben.

Als nächstes soll eine zweite Praxisabschrift ausschließlich aus echten
H4-Karten und in echter H4-Reihenfolge gesetzt werden. Renderer dürfen wechseln,
aber keine fremde Funktionskarte darf hineingelangen.
"""
    (HERE / "THREE_HUNDRED_NINETY_FIRST_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "practice_cards": len(provenance_rows),
        "owner_native_cards": native_count,
        "h4_native_cards": h4_native,
        "b3_native_cards": b3_native,
        "cross_register_borrowings": len(provenance_rows) - native_count,
        "genuine_statements": len(genuine_rows),
        "stage_alignment_rows": len(stage_rows),
        "practice_status": "CROSS_REGISTER_TEACHING_SYNTHESIS_NOT_TRANSLATION",
    }
    (HERE / "THREE_HUNDRED_NINETY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
