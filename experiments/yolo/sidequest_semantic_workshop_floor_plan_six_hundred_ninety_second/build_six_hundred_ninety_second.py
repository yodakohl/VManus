#!/usr/bin/env python3
"""Build a four-role floor plan from the five specialist station decks."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P691 = ROOT / "experiments/yolo/sidequest_semantic_craft_station_decks_six_hundred_ninety_first"
RECORDS = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


ROLE_FOR_STATION = {
    "PREPARATION_INPUT": "S02_PREPARATION_WET",
    "WET_HANDLING": "S02_PREPARATION_WET",
    "TRANSFER_EDIT": "S03_TRANSFER",
    "STATE_CONTROL": "S04_STATE_CONTROL",
    "LOCAL_COMMAND": "S01_MASTER_CORRECTOR",
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
    root_stations = read(P691 / "SIX_HUNDRED_NINETY_FIRST_26_SPECIALIST_ROOT_STATIONS.tsv")
    record_decks = {row["record"]: row for row in read(P691 / "SIX_HUNDRED_NINETY_FIRST_11_MINIMAL_RECORD_DECKS.tsv")}
    matrix = read(P691 / "SIX_HUNDRED_NINETY_FIRST_55_RECORD_STATION_MATRIX.tsv")

    assignment_rows = []
    for row in root_stations:
        assignment_rows.append({
            "scribe_role": ROLE_FOR_STATION[row["station"]],
            "station_deck": row["station"],
            "component": row["component"],
            "value_de": row["compact_value_de"],
            "token_uses": row["token_uses"],
            "storage_de": "Musterkarte an diesem Schreibtisch; 13er Taschenkern zusaetzlich gemeinsam.",
        })

    role_specs = {
        "S01_MASTER_CORRECTOR": ("Meister und Korrektor", "Bildbesitzer setzen; Nomenklator und seltene Befehle verwalten; Record abschliessen"),
        "S02_PREPARATION_WET": ("Vorbereitungs- und Nassschreiber", "Portionen Zutaten Teilung Durchlass Lauf Waschen Einfuellen Auswringen und Auffangen einsetzen"),
        "S03_TRANSFER": ("Transferschreiber", "Abnehmen Eintragen Umsetzen und Weiterleiten einsetzen"),
        "S04_STATE_CONTROL": ("Zustandsschreiber", "Halten Absetzen Bereitschaft Waerme Kuehlung Stufe und Vollgrad einsetzen"),
    }
    role_rows = []
    for role, (title, duty) in role_specs.items():
        assigned = [row for row in assignment_rows if row["scribe_role"] == role]
        role_rows.append({
            "scribe_role": role,
            "historical_role_de": title,
            "specialist_root_cards": len(assigned),
            "components": " ".join(str(row["component"]) for row in assigned),
            "specialist_token_uses": sum(int(row["token_uses"]) for row in assigned),
            "main_duty_de": duty,
            "shared_material": "13er Taschenkern und aktuelles Seiten-/Recordpaket",
        })

    by_record_station = {(row["record"], row["station"]): row for row in matrix}
    route_rows = []
    for record in RECORDS:
        prepwet = sum(int(by_record_station[(record, station)]["token_uses"]) for station in ["PREPARATION_INPUT", "WET_HANDLING"])
        transfer = int(by_record_station[(record, "TRANSFER_EDIT")]["token_uses"])
        state = int(by_record_station[(record, "STATE_CONTROL")]["token_uses"])
        local = int(by_record_station[(record, "LOCAL_COMMAND")]["token_uses"])
        route = ["S01_MASTER_START"]
        if prepwet:
            route.append("S02_PREPARATION_WET")
        route.extend(["S03_TRANSFER", "S04_STATE_CONTROL", "S01_MASTER_CLOSE"])
        route_rows.append({
            "record": record,
            "page": record_decks[record]["page"],
            "events": record_decks[record]["events"],
            "minimal_specialist_root_cards": record_decks[record]["minimal_specialist_root_cards"],
            "prep_wet_token_uses": prepwet,
            "transfer_token_uses": transfer,
            "state_token_uses": state,
            "local_command_uses": local,
            "scribe_route": " > ".join(route),
            "desk_visits": len(route),
            "handoffs": len(route) - 1,
            "record_packet_de": "Seite mit Bildbesitzer,13er Kernprompt, lokale Rezeptadressen und nur benoetigte Spezialkarten.",
        })

    handoff_rows = [
        {"step": 1, "from_role": "S01_MASTER_CORRECTOR", "to_role": "S02_PREPARATION_WET_OR_SKIP", "packet_rule_de": "Besitzer und Kernprompt oben auf das Recordpaket schreiben."},
        {"step": 2, "from_role": "S02_PREPARATION_WET", "to_role": "S03_TRANSFER", "packet_rule_de": "Vorbereitungs- und Nasskarten positionsgetreu einsetzen; Oberflaeche nicht normalisieren."},
        {"step": 3, "from_role": "S03_TRANSFER", "to_role": "S04_STATE_CONTROL", "packet_rule_de": "Transferkarten einfuegen und offene DIES-Karte von Schlusskarte unterscheiden."},
        {"step": 4, "from_role": "S04_STATE_CONTROL", "to_role": "S01_MASTER_CORRECTOR", "packet_rule_de": "Grad Zustand und Endkarte pruefen; physische Zeile nicht als Satzgrenze behandeln."},
        {"step": 5, "from_role": "S01_MASTER_CORRECTOR", "to_role": "COPY_COMPLETE", "packet_rule_de": "Seltene Ganzbefehle einsetzen und jede Karte atomar ruecklesen."},
        {"step": 6, "from_role": "COPY_COMPLETE", "to_role": "MASTER_EXEMPLAR_SHELF", "packet_rule_de": "Recordpaket mit der Mustertafel ablegen damit die naechste Hand dieselbe Variante kopiert."},
    ]

    write("SIX_HUNDRED_NINETY_SECOND_4_SCRIBE_ROLES.tsv", role_rows)
    write("SIX_HUNDRED_NINETY_SECOND_26_ROOT_ASSIGNMENTS.tsv", assignment_rows)
    write("SIX_HUNDRED_NINETY_SECOND_11_RECORD_ROUTES.tsv", route_rows)
    write("SIX_HUNDRED_NINETY_SECOND_6_HANDOFF_RULES.tsv", handoff_rows)

    summary = {
        "status": "PASS",
        "scribe_roles": len(role_rows),
        "specialist_roots_assigned": len(assignment_rows),
        "role_token_load": {row["scribe_role"]: int(row["specialist_token_uses"]) for row in role_rows},
        "records": len(route_rows),
        "records_visiting_prep_wet": sum(int(row["prep_wet_token_uses"]) > 0 for row in route_rows),
        "records_visiting_transfer": sum(int(row["transfer_token_uses"]) > 0 for row in route_rows),
        "records_visiting_state": sum(int(row["state_token_uses"]) > 0 for row in route_rows),
        "records_using_local_commands": sum(int(row["local_command_uses"]) > 0 for row in route_rows),
        "total_desk_visits": sum(int(row["desk_visits"]) for row in route_rows),
        "total_handoffs": sum(int(row["handoffs"]) for row in route_rows),
    }
    (HERE / "SIX_HUNDRED_NINETY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
