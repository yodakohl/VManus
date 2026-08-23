#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R127 = ROOT / "experiments/yolo/sidequest_semantic_revised_continuous_prose_hundred_twenty_seventh"
R129 = ROOT / "experiments/yolo/sidequest_semantic_specialist_drawers_hundred_twenty_ninth"

JOBS = [
    ("J1_ROOT_AND_LEAF_BASIN", ["H1", "H2", "B1"], "Wurzel-, Spross- und Blattauszug im gemeinsamen Beckenprogramm",
     "Bereite den ersten Wurzelauszug und den zweiten Blatt-/Sprossansatz nach Sollmaß. Übergib beide an das gemeinsame Beckenprogramm, führe sie durch die lokalen Ziel-, Wasch-, Wärme-, Absetz- und Ablaufzellen und schließe jeden Arbeitsschritt."),
    ("J2_CLEAR_EXTRACT_STATIONS", ["H3", "B2"], "Klarlauf durch die mehrteilige Stationsfolge",
     "Wringe den Blüten-/Blattansatz aus, lass ihn stehen, seih nach und nimm den Klarlauf. Setze ihn an den sichtbaren Stationen ein, führe ihn durch, lass ihn einwirken, trenne den Ablauf und führe ihn am Ende ab."),
    ("J3_BOUND_APPLICATION_SERVICE", ["H4", "B4", "B5", "B6"], "Gebundene Zubereitung, Tuchanwendung und Dienststationen",
     "Stelle die Zubereitung auf Sollmaß, teile einen Anwendungsanteil ab und verwahre den Rest. Setze den Anteil an der sichtbaren Tuchanwendung ein, binde ihn fest, führe die Wasch- und Absetzschritte aus und nutze die beiden Dienststationen für Ablauf, Sammlung und Endziel."),
    ("J4_FRESH_PLANT_LONG_ROUTE", ["H5", "B3"], "Frische Pflanze durch die lange Transfer- und Zustandsstrecke",
     "Bereite aus der frischen Pflanze eine Waschung und einen zweiten gebundenen Ansatz. Führe die aktive Zubereitung durch die lange Folge aus Transfer, Ziel, Sollmaß, Wärme, Absetzen, Sammlung und Klarlauf; schließe die lokalen Zellen einzeln."),
]


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(R129 / "HUNDRED_TWENTY_NINTH_COMPLETE_381_EVENT_DICTIONARY.tsv")
    records = read_tsv(R127 / "HUNDRED_TWENTY_SEVENTH_ELEVEN_REVISED_RECORDS.tsv")
    record_by_id = {row["record_unit_id"]: row for row in records}
    event_by_record = defaultdict(list)
    for row in events:
        event_by_record[row["record_unit_id"]].append(row)

    job_by_record = {}
    profile_rows = []
    step_rows = []
    md = ["# Vier vollständige praktische Arbeitsaufträge", ""]
    for job_id, job_records, title, instruction in JOBS:
        for record in job_records:
            if record in job_by_record:
                raise ValueError(record)
            job_by_record[record] = job_id
        members = [event for record in job_records for event in event_by_record[record]]
        herbal = [record for record in job_records if record.startswith("H")]
        bio = [record for record in job_records if record.startswith("B")]
        profile_rows.append({
            "job_id": job_id,
            "title_de": title,
            "herbal_records": "|".join(herbal),
            "biological_records": "|".join(bio),
            "record_count": str(len(job_records)),
            "event_count": str(len(members)),
            "material_side": " + ".join(record_by_id[record]["continuous_record_de"] for record in herbal),
            "operation_side": " + ".join(record_by_id[record]["continuous_record_de"] for record in bio),
            "complete_job_instruction_de": instruction,
            "link_status": "WORKSHOP_COMPATIBILITY_RECONSTRUCTION__NO_WRITTEN_CROSS_PAGE_POINTER_CLAIM",
        })
        md += [f"## {job_id}: {title}", "", instruction, ""]
        for order, record in enumerate(job_records, 1):
            record_row = record_by_id[record]
            step_rows.append({
                "job_id": job_id,
                "step_order": str(order),
                "record_unit_id": record,
                "page": record_row["page"],
                "step_role": "WHAT_MATERIAL_OR_PRODUCT" if record.startswith("H") else "HOW_OPERATION_PROGRAM",
                "event_count": str(len(event_by_record[record])),
                "continuous_record_de": record_row["continuous_record_de"],
            })
            md += [f"### Schritt {order}: {record} · {record_row['page']}", "", record_row["continuous_record_de"], ""]
    write_tsv("HUNDRED_THIRTY_SECOND_FOUR_JOB_PROFILES.tsv", profile_rows)
    write_tsv("HUNDRED_THIRTY_SECOND_ELEVEN_JOB_STEPS.tsv", step_rows)
    (OUT / "HUNDRED_THIRTY_SECOND_FOUR_COMPLETE_WORK_ORDERS.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    ledger_rows = []
    for row in events:
        ledger_rows.append({
            "job_id": job_by_record[row["record_unit_id"]],
            "event_serial": row["event_serial"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "statement_id": row["statement_id"],
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "current_spoken_default_de": row["current_spoken_default_de"],
            "drawer": row["drawer"],
        })
    write_tsv("HUNDRED_THIRTY_SECOND_381_EVENT_JOB_LEDGER.tsv", ledger_rows)

    report = [
        "# Hundertzweiunddreißigste Runde: vier plausible Werkstattaufträge", "",
        "All eleven prose records now occur exactly once in four practical WHAT→HOW orders. J1 joins the two",
        "f10r preparations to the common f81v basin program. J2 joins the wrung clear extract to the f82r",
        "station path. J3 joins the measured bound f55v preparation to the cloth/application and two service",
        "tails on f83r. J4 joins the fresh f56r plant preparations to the long f83r transfer/state route.", "",
        "These jobs are the strongest current use scenarios, not claims of written references. Their value is",
        "that all 381 events remain in original record order while the drawer architecture supplies a coherent",
        "material input and operation program. No record is reused or discarded.", "",
        "Next step: restore the three celestial pages as optional WHEN cards for these four jobs, using only",
        "visible module ownership and never inventing a common f68-to-f69 key or cyclic reading direction.",
    ]
    (OUT / "HUNDRED_THIRTY_SECOND_FOUR_JOB_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "jobs": len(profile_rows), "records": len(step_rows), "events": len(ledger_rows), "record_assignments_unique": len(job_by_record)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
