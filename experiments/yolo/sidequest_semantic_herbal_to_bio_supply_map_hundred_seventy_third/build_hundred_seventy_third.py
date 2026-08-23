#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth/HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth/HUNDRED_SIXTY_FOURTH_116_ATOMIC_CLAUSES.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


JOBS = {
    "J1": ("H1|H2", "f10r", "MULTI_BATCH_ROOT_AND_FLOWER_MOTHER_EXTRACT", "mehrteiliger Grundauszug"),
    "J2": ("H3", "f11r", "CLARIFIED_ASTRINGENT_WASH", "geklaerter adstringierender Waschauszug"),
    "J3": ("H4", "f55v", "STORED_TWO_PART_PLANT_STOCK", "verwahrter zweipartiger Pflanzenansatz"),
    "J4": ("H5", "f56r", "REPEATED_TARGET_APPLICATION_ADDITIVE", "Wirkzusatz fuer Zielanwendungen"),
}


SELECTIONS = {
    ("J1", "B1"): "PRIMARY_SUPPLY",
    ("J2", "B2"): "PRIMARY_SUPPLY",
    ("J3", "B3"): "PRIMARY_SUPPLY",
    ("J2", "B4"): "CARRIER_SUPPLY",
    ("J4", "B4"): "ACTIVE_ADDITIVE",
    ("J3", "B5"): "PRIMARY_SUPPLY",
    ("J4", "B6"): "PRIMARY_SUPPLY",
}


RECORD_PLAN = [
    ("B1", "f81v", "J1", "gemeinsames Figurenbecken", "Grundauszug chargenweise bemessen temperieren mischen baden und nachspuelen", "sechs exakte Bruecken und volle Misch-/Badekette"),
    ("B2", "f82r", "J2", "fuenf lokale Becken- und Koerperstationen", "Klarauszug durch obere Stationen zum Teilbad und zu den Randwaschungen fuehren", "exakte Klarauszugkarte plus Sollmass und laufender Posten"),
    ("B3", "f83r", "J3", "mehrere Gefaess- und Randstationen", "Vorratsansatz portionsweise in verschiedene Gefaesse ueberfuehren erwaermen mischen und bereitstellen", "sechs exakte Bruecken inklusive bemessen ueberfuehren Ansatz und dorthin einsetzen"),
    ("B4", "f83r", "J2+J4", "Bogenpaar linker Unterlauf und rechter Zielknoten", "Klarauszug mit Wirkzusatz laden zweimal durch Einlage fuehren teilen und an Ziele bringen", "J2 liefert exakten Klarauszug; J4 liefert Ziel- und Wiederanwendungsgrammatik"),
    ("B5", "f83r", "J3", "linker offener Endposten", "eine verwahrte vorige Mischung abziehen kurz erwaermen bemessen und an zweiter Oeffnung mischen", "Vorratsrolle erklaert vorige Mischung und Wiedererwaermen"),
    ("B6", "f83r", "J4", "rechter S-Lauf-/Mehrarm-Endposten", "fertigen Wirkzusatz ohne Kochen durch Tuch geben bemessen und an Zielstelle einsetzen", "kein Kochen plus Portion Tuch und Ziel passen zum fertigen Anwendungszusatz"),
]


def main() -> None:
    events = read(EVENTS)
    by_record: dict[str, set[str]] = defaultdict(set)
    value = {}
    for row in events:
        by_record[row["record_unit_id"]].add(row["master_card_id"])
        value[row["master_card_id"]] = row["card_value_de"]

    matrix = []
    for job_id, (records, page, job, product) in JOBS.items():
        herbal_cards = set().union(*(by_record[record] for record in records.split("|")))
        for bio in ["B1", "B2", "B3", "B4", "B5", "B6"]:
            bridge = sorted(herbal_cards & by_record[bio])
            selection = SELECTIONS.get((job_id, bio), "NOT_SELECTED")
            matrix.append(
                {
                    "job_id": job_id,
                    "herbal_page": page,
                    "selected_job": job,
                    "product_de": product,
                    "bio_record": bio,
                    "exact_bridge_count": len(bridge),
                    "exact_bridge_cards": "|".join(f"{card}:{value[card]}" for card in bridge) or "NONE",
                    "selection": selection,
                    "selection_reason_de": "Produktfunktion und sichtbare Stationsarbeit passen" if selection != "NOT_SELECTED" else "weniger spezifisch als ausgewaehlte Versorgung",
                }
            )
    write(OUT / "HUNDRED_SEVENTY_THIRD_24_PRODUCT_STATION_MATRIX.tsv", matrix)

    plan_rows = [
        {
            "bio_record": bio,
            "page": page,
            "source_job_ids": jobs,
            "visible_station_class_de": owner,
            "continuous_supply_reading_de": reading,
            "decisive_reason_de": reason,
            "cross_page_status": "WORKSHOP_SUPPLY_PLAN_NOT_VISIBLE_POINTER",
        }
        for bio, page, jobs, owner, reading, reason in RECORD_PLAN
    ]
    write(OUT / "HUNDRED_SEVENTY_THIRD_6_RECORD_SUPPLY_PLAN.tsv", plan_rows)

    plan_by_record = {row["bio_record"]: row for row in plan_rows}
    clause_rows = []
    for row in read(CLAUSES):
        record = row["record_unit_id"]
        if not record.startswith("B"):
            continue
        plan = plan_by_record[record]
        clause_rows.append(
            {
                "statement_id": row["statement_id"],
                "record_unit_id": record,
                "page": row["page"],
                "source_job_ids": plan["source_job_ids"],
                "visible_owner": row["owner_trace"],
                "unchanged_atomic_chain_de": row["atomic_card_chain_de"],
                "product_supplied_clause_de": f"Mit {plan['continuous_supply_reading_de']}: {row['continuous_atomic_clause_de']}",
                "terminal_status": row["terminal_status"],
                "dictionary_change": "NO",
            }
        )
    write(OUT / "HUNDRED_SEVENTY_THIRD_97_BIO_CLAUSE_SUPPLY_EDITION.tsv", clause_rows)

    summary = {
        "source_events_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "source_clauses_sha256": hashlib.sha256(CLAUSES.read_bytes()).hexdigest(),
        "matrix_cells": len(matrix),
        "selected_links": sum(row["selection"] != "NOT_SELECTED" for row in matrix),
        "bio_records": len(plan_rows),
        "bio_clauses": len(clause_rows),
        "bio_events": sum(1 for row in events if row["record_unit_id"].startswith("B")),
        "dictionary_changes": 0,
        "visible_cross_page_pointer_claim": False,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
