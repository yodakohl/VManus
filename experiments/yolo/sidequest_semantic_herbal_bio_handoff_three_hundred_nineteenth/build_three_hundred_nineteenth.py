#!/usr/bin/env python3
"""Build the five Herbal-to-Bio workshop handoff cards."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BIO = ROOT / "experiments/yolo/sidequest_semantic_bio_station_sequences_three_hundred_eighteenth/THREE_HUNDRED_EIGHTEENTH_118_STATION_WORK_UNITS.tsv"

OUTPUTS = [
    {
        "herbal_record": "H1",
        "page": "f10r",
        "pictured_owner": "abgebildete Wurzelpflanze",
        "preparation_output": "BEMESSENER_WURZEL_AUSZUG_MIT_REST",
        "output_instruction": "Den abgemessenen Wurzelauszug mitsamt kleinem Rest als gebrauchsfertigen Ansatz ausgeben.",
        "handoff_terms": "Zusatz|Gleichansatz|Sollmaß|Ziellanghalt",
        "primary_bio_unit": "B1-S002-M03",
        "secondary_bio_units": "B1-S002-M04|B1-S006",
    },
    {
        "herbal_record": "H2",
        "page": "f10r",
        "pictured_owner": "abgebildete Pflanzenzubereitung, zweiter Artikel",
        "preparation_output": "FORTGESETZTER_AUSZUGSANSATZ_AUF_SOLLSTUFE",
        "output_instruction": "Den fortgesetzten Auszugsansatz auf Sollstufe einstellen und als bemessenen Folgeansatz ausgeben.",
        "handoff_terms": "Sollmaß|Ziellanghalt|Zieleinsatz|Sollsammlung",
        "primary_bio_unit": "B1-S002-M04",
        "secondary_bio_units": "B2-S005-M01|B2-S012-M03",
    },
    {
        "herbal_record": "H3",
        "page": "f11r",
        "pictured_owner": "abgebildete Pflanze",
        "preparation_output": "GEKLAERTER_KALTER_SUD",
        "output_instruction": "Den ausgewrungenen, abgesetzten und nachgeseihten klaren Sud kalt als Klarlauf ausgeben.",
        "handoff_terms": "Klarlauf|Klarabzug|Langkontakt|Auslass",
        "primary_bio_unit": "B2-S012-M02",
        "secondary_bio_units": "B2-S010|B2-S015",
    },
    {
        "herbal_record": "H4",
        "page": "f55v",
        "pictured_owner": "abgebildete Blattpflanze",
        "preparation_output": "BEMESSENER_GEKEUHLTER_BLATTAUSZUG",
        "output_instruction": "Den gekühlten Blattauszug in Sollportionen teilen und für längeren Zielkontakt ausgeben.",
        "handoff_terms": "Sollmaß|Langbearbeitung|Langhalt|Kurzkontakt|Portion",
        "primary_bio_unit": "B4-S008",
        "secondary_bio_units": "B3-S013|B4-S015-M01",
    },
    {
        "herbal_record": "H5",
        "page": "f56r",
        "pictured_owner": "abgebildete Stängel-/Zusatzpflanze",
        "preparation_output": "STAENGEL_ZUSATZ_AUSZUG_FUER_FOLGEANWENDUNGEN",
        "output_instruction": "Den Stängel- und Zusatzauszug als Folgeposten für wiederholte Zielanwendungen ausgeben.",
        "handoff_terms": "Folgeposten|Langkontakt|einsetzen|Zugabe|Zielpassage",
        "primary_bio_unit": "B4-S003-M02",
        "secondary_bio_units": "B4-S015-M01|B1-S006",
    },
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    bio_rows = read_tsv(BIO)
    by_id = {row["station_work_unit_id"]: row for row in bio_rows}

    output_rows = []
    candidate_rows = []
    selected_rows = []
    for item in OUTPUTS:
        primary = by_id[item["primary_bio_unit"]]
        row = dict(item)
        row.update(
            {
                "selected_bio_owner": primary["owner_id"],
                "selected_station_role": primary["station_role"],
                "selected_bio_page": primary["page"],
                "selected_atomic_chain": primary["atomic_chain"],
                "cross_page_pointer": "NONE",
                "connection_kind": "WORKSHOP_OUTPUT_TO_COMPATIBLE_STATION_INPUT",
            }
        )
        output_rows.append(row)

        candidate_ids = [item["primary_bio_unit"], *item["secondary_bio_units"].split("|")]
        terms = item["handoff_terms"].split("|")
        for candidate_id in candidate_ids:
            bio = by_id[candidate_id]
            matched = [term for term in terms if term.lower() in bio["atomic_chain"].lower()]
            candidate_rows.append(
                {
                    "herbal_record": item["herbal_record"],
                    "preparation_output": item["preparation_output"],
                    "bio_unit": candidate_id,
                    "bio_page": bio["page"],
                    "bio_owner": bio["owner_id"],
                    "station_role": bio["station_role"],
                    "bio_atomic_chain": bio["atomic_chain"],
                    "matched_handoff_terms": "|".join(matched),
                    "matched_term_count": str(len(matched)),
                    "selection": "PRIMARY" if candidate_id == item["primary_bio_unit"] else "SECONDARY",
                    "connection_kind": "THEMATIC_WORKSHOP_HANDOFF_NOT_DRAWN_POINTER",
                }
            )

        selected_rows.append(
            {
                "herbal_record": item["herbal_record"],
                "herbal_page": item["page"],
                "preparation_output": item["preparation_output"],
                "bio_unit": primary["station_work_unit_id"],
                "bio_page": primary["page"],
                "bio_owner": primary["owner_id"],
                "station_role": primary["station_role"],
                "source_work_instruction": primary["work_instruction_de"],
                "integrated_handoff_reading": f'{item["output_instruction"]} Danach an {primary["station_role"]}: {primary["work_instruction_de"]}',
                "direct_pointer": "NO",
            }
        )

    write_tsv(
        HERE / "THREE_HUNDRED_NINETEENTH_FIVE_HERBAL_OUTPUTS.tsv",
        output_rows,
        list(output_rows[0]),
    )
    write_tsv(
        HERE / "THREE_HUNDRED_NINETEENTH_HERBAL_TO_BIO_CANDIDATES.tsv",
        candidate_rows,
        list(candidate_rows[0]),
    )
    write_tsv(
        HERE / "THREE_HUNDRED_NINETEENTH_FIVE_SELECTED_HANDOFFS.tsv",
        selected_rows,
        list(selected_rows[0]),
    )

    hashes = {}
    for name in [
        "THREE_HUNDRED_NINETEENTH_FIVE_HERBAL_OUTPUTS.tsv",
        "THREE_HUNDRED_NINETEENTH_HERBAL_TO_BIO_CANDIDATES.tsv",
        "THREE_HUNDRED_NINETEENTH_FIVE_SELECTED_HANDOFFS.tsv",
    ]:
        hashes[name] = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    summary = {
        "status": "PASS",
        "herbal_outputs": len(output_rows),
        "candidate_handoffs": len(candidate_rows),
        "selected_handoffs": len(selected_rows),
        "direct_cross_page_pointers": 0,
        "source_bio_units": len(bio_rows),
        "hashes": hashes,
    }
    (HERE / "THREE_HUNDRED_NINETEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
