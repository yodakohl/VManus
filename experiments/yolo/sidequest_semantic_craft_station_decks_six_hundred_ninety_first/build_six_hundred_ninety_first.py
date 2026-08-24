#!/usr/bin/env python3
"""Split the 26 specialist roots into five physical craft-station decks."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P690 = ROOT / "experiments/yolo/sidequest_semantic_statement_core_projection_six_hundred_ninetieth"
RECORDS = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


STATION = {
    "AIN": "PREPARATION_INPUT", "HO": "PREPARATION_INPUT", "AN": "PREPARATION_INPUT", "S": "PREPARATION_INPUT",
    "CKH": "WET_HANDLING", "AIR": "WET_HANDLING", "LSH": "WET_HANDLING", "P": "WET_HANDLING", "CFH": "WET_HANDLING", "SOLK": "WET_HANDLING",
    "CHD": "TRANSFER_EDIT", "L": "TRANSFER_EDIT", "CH": "TRANSFER_EDIT", "T": "TRANSFER_EDIT",
    "SH": "STATE_CONTROL", "SHED": "STATE_CONTROL", "CTH": "STATE_CONTROL", "CHK": "STATE_CONTROL", "R": "STATE_CONTROL", "IIN": "STATE_CONTROL", "EEE": "STATE_CONTROL",
    "RESUME_CARD": "LOCAL_COMMAND", "DA": "LOCAL_COMMAND", "LD": "LOCAL_COMMAND", "OS": "LOCAL_COMMAND", "TALAM": "LOCAL_COMMAND",
}

STATION_RULE = {
    "PREPARATION_INPUT": "Portion Zutat Nachgabe und Teilung vor dem Hauptgang bereitstellen.",
    "WET_HANDLING": "Durchlass Lauf Waschen Einfuellen Auswringen und Auffangen am Nassplatz ausfuehren.",
    "TRANSFER_EDIT": "Posten abnehmen eintragen umsetzen oder weiterleiten.",
    "STATE_CONTROL": "Halten Absetzen Bereitschaft Waerme Kuehlung Stufe und Vollgrad ueberwachen.",
    "LOCAL_COMMAND": "Seltene Recordbefehle als ganze lokale Karten lernen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    usage = read(P690 / "SIX_HUNDRED_NINETIETH_26_SPECIALIST_USAGE.tsv")
    statements = read(P690 / "SIX_HUNDRED_NINETIETH_116_STATEMENT_CORE_PROJECTION.tsv")
    events = read(P690 / "SIX_HUNDRED_NINETIETH_381_EVENT_CORE_PROJECTION.tsv")
    roots = {row["component"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")}

    root_rows = []
    for row in usage:
        component = row["component"]
        station = STATION[component]
        root_rows.append({
            "station": station,
            "component": component,
            "compact_value_de": row["value_de"],
            "token_uses": row["token_uses"],
            "statements": row["statements"],
            "records": row["records"],
            "station_rule_de": STATION_RULE[station],
            "physical_storage_de": "eigene beschriftete Musterkarte im Stationskasten",
        })

    station_order = ["PREPARATION_INPUT", "WET_HANDLING", "TRANSFER_EDIT", "STATE_CONTROL", "LOCAL_COMMAND"]
    station_rows = []
    for station_no, station in enumerate(station_order, start=1):
        members = [row for row in root_rows if row["station"] == station]
        station_rows.append({
            "station_no": station_no,
            "station": station,
            "root_cards": len(members),
            "components": " ".join(str(row["component"]) for row in members),
            "values_de": " | ".join(str(row["compact_value_de"]) for row in members),
            "token_uses": sum(int(row["token_uses"]) for row in members),
            "work_rule_de": STATION_RULE[station],
        })

    record_rows = []
    matrix_rows = []
    for record in RECORDS:
        record_statements = [row for row in statements if row["record"] == record]
        specialist_tokens = [token for row in record_statements for token in row["specialist_sequence"].split() if token != "NONE"]
        specialist_roots = sorted(set(specialist_tokens))
        specialist_events = [row for row in events if row["record"] == record and row["event_class"] == "MIXED_OR_SPECIALIST_CARD"]
        stations = [station for station in station_order if any(STATION[root] == station for root in specialist_roots)]
        record_rows.append({
            "record": record,
            "page": record_statements[0]["page"],
            "statements": len(record_statements),
            "events": sum(int(row["events"]) for row in record_statements),
            "specialist_token_uses": len(specialist_tokens),
            "minimal_specialist_root_cards": len(specialist_roots),
            "specialist_roots": " ".join(specialist_roots),
            "craft_stations_needed": len(stations),
            "station_decks": "|".join(stations),
            "exact_specialist_bearing_cards": len({row["surface"] for row in specialist_events}),
            "physical_deck_rule_de": "13er Taschenkern tragen; nur diese Spezialwurzelkarten und die belegten Oberflaechen am Arbeitsplatz bereithalten.",
        })
        for station in station_order:
            station_tokens = [token for token in specialist_tokens if STATION[token] == station]
            matrix_rows.append({
                "record": record,
                "station": station,
                "root_cards_needed": len(set(station_tokens)),
                "components": " ".join(sorted(set(station_tokens))) if station_tokens else "NONE",
                "token_uses": len(station_tokens),
            })

    write("SIX_HUNDRED_NINETY_FIRST_26_SPECIALIST_ROOT_STATIONS.tsv", root_rows)
    write("SIX_HUNDRED_NINETY_FIRST_5_CRAFT_STATION_DECKS.tsv", station_rows)
    write("SIX_HUNDRED_NINETY_FIRST_11_MINIMAL_RECORD_DECKS.tsv", record_rows)
    write("SIX_HUNDRED_NINETY_FIRST_55_RECORD_STATION_MATRIX.tsv", matrix_rows)

    summary = {
        "status": "PASS",
        "specialist_roots": len(root_rows),
        "specialist_token_uses": sum(int(row["token_uses"]) for row in root_rows),
        "craft_station_decks": len(station_rows),
        "station_token_load": {row["station"]: int(row["token_uses"]) for row in station_rows},
        "records": len(record_rows),
        "smallest_record_deck": min(int(row["minimal_specialist_root_cards"]) for row in record_rows),
        "largest_record_deck": max(int(row["minimal_specialist_root_cards"]) for row in record_rows),
        "largest_deck_records": [row["record"] for row in record_rows if int(row["minimal_specialist_root_cards"]) == max(int(item["minimal_specialist_root_cards"]) for item in record_rows)],
    }
    (HERE / "SIX_HUNDRED_NINETY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
