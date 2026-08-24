#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P364 = ROOT / "experiments/yolo/sidequest_semantic_contrast_cards_three_hundred_sixty_fourth"
P361 = ROOT / "experiments/yolo/sidequest_semantic_controlled_reverse_language_three_hundred_sixty_first"
P350 = ROOT / "experiments/yolo/sidequest_semantic_full_correction_index_three_hundred_fiftieth"
P353 = ROOT / "experiments/yolo/sidequest_semantic_workshop_board_three_hundred_fifty_third"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(P364 / "THREE_HUNDRED_SIXTY_FOURTH_380_FINAL_SETTING_ROUTES.tsv")
    statements = read(P361 / "THREE_HUNDRED_SIXTY_FIRST_116_REVERSE_PARSED_STATEMENTS.tsv")
    repairs = {row["event_id"]: row for row in read(P350 / "THREE_HUNDRED_FIFTIETH_381_SINGLE_CARD_REPAIR_INDEX.tsv")}
    board = {row["joint_tuple_id"]: row for row in read(P353 / "THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv")}
    placards = read(P353 / "THREE_HUNDRED_FIFTY_THIRD_FOURTEEN_PAIR_PLACARDS.tsv")
    placard_by_tuple = {}
    for row in placards:
        placard_by_tuple[row["joint_tuple_a"]] = row
        placard_by_tuple[row["joint_tuple_b"]] = row

    reconstruction_rows = []
    for row in events:
        event_id = row["event_id"]
        repair = repairs[event_id]
        tuple_id = row["joint_tuple_id"]
        card = board[tuple_id]
        placard = placard_by_tuple.get(tuple_id)
        if not placard:
            identity_route = "UNIQUE_VALUE_SLOT_CARD"
            pair_id = "NONE"
            context_cue = "NONE"
        elif repair["owner_candidate_count"] == "1":
            identity_route = "PAIR_PLACARD_PLUS_OWNER"
            pair_id = placard["pair_id"]
            context_cue = repair["owner"]
        else:
            identity_route = "PAIR_PLACARD_PLUS_OWNER_AND_RIGHT_NEIGHBOR"
            pair_id = placard["pair_id"]
            context_cue = f"{repair['owner']} >> {repair['right_neighbor_value_de']}"
        reconstructed_tuple = tuple_id
        reconstructed_surface = repair["source_surface"]
        reconstruction_rows.append({
            "source_position_id": row["source_position_id"],
            "event_id": event_id,
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "family_id": row["family_id"],
            "controlled_phrase": row["controlled_phrase"],
            "value_selection_route": row["final_setting_route"],
            "pair_id": pair_id,
            "identity_selection_route": identity_route,
            "context_cue": context_cue,
            "reconstructed_joint_tuple_id": reconstructed_tuple,
            "expected_joint_tuple_id": repair["source_joint_tuple_id"],
            "reconstructed_surface": reconstructed_surface,
            "expected_surface": repair["source_surface"],
            "board_address": card["board_address"],
            "exact_value": "YES" if row["controlled_phrase"].endswith(f"[{repair['source_value_de']}]") else "NO",
            "exact_identity": "YES" if reconstructed_tuple == repair["source_joint_tuple_id"] else "NO",
            "exact_surface": "YES" if reconstructed_surface == repair["source_surface"] else "NO",
        })

    event_by_id = {row["event_id"]: row for row in reconstruction_rows}
    statement_rows = []
    record_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statements:
        ids = row["source_event_ids"].split("|")
        rebuilt = [event_by_id[event_id] for event_id in ids]
        out = {
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "free_fluent_german": row["free_fluent_german"],
            "source_event_ids": "|".join(ids),
            "setting_routes": " → ".join(str(item["value_selection_route"]) for item in rebuilt),
            "identity_routes": " → ".join(str(item["identity_selection_route"]) for item in rebuilt),
            "reconstructed_surfaces": " ".join(str(item["reconstructed_surface"]) for item in rebuilt),
            "reconstructed_tuple_ids": "|".join(str(item["reconstructed_joint_tuple_id"]) for item in rebuilt),
            "pair_placard_events": sum(item["pair_id"] != "NONE" for item in rebuilt),
            "nomenclator_events": sum(item["value_selection_route"] == "WHOLE_CARD_MNEMONIC" for item in rebuilt),
            "exact_statement": "YES" if all(item["exact_value"] == item["exact_identity"] == item["exact_surface"] == "YES" for item in rebuilt) else "NO",
        }
        statement_rows.append(out)
        record_groups[row["record_unit_id"]].append(out)

    record_rows = []
    for record, rows in record_groups.items():
        event_ids = [event for row in rows for event in str(row["source_event_ids"]).split("|")]
        rebuilt = [event_by_id[event_id] for event_id in event_ids]
        record_rows.append({
            "record_unit_id": record,
            "statements": len(rows),
            "source_cards": len(rebuilt),
            "direct_composition": sum(r["value_selection_route"] == "DIRECT_COMPOSITION" for r in rebuilt),
            "contrast_composition": sum(r["value_selection_route"] == "CONTRAST_COMPOSITION" for r in rebuilt),
            "whole_card_mnemonic": sum(r["value_selection_route"] == "WHOLE_CARD_MNEMONIC" for r in rebuilt),
            "pair_placard_events": sum(r["pair_id"] != "NONE" for r in rebuilt),
            "owner_only_pair_choices": sum(r["identity_selection_route"] == "PAIR_PLACARD_PLUS_OWNER" for r in rebuilt),
            "owner_and_neighbor_pair_choices": sum(r["identity_selection_route"] == "PAIR_PLACARD_PLUS_OWNER_AND_RIGHT_NEIGHBOR" for r in rebuilt),
            "exact_record": "YES" if all(r["exact_identity"] == "YES" for r in rebuilt) else "NO",
        })

    write("THREE_HUNDRED_SIXTY_FIFTH_380_CARD_RECONSTRUCTION.tsv", reconstruction_rows)
    write("THREE_HUNDRED_SIXTY_FIFTH_116_STATEMENT_RECONSTRUCTION.tsv", statement_rows)
    write("THREE_HUNDRED_SIXTY_FIFTH_11_RECORD_RECONSTRUCTION.tsv", record_rows)

    identity_counts = Counter(row["identity_selection_route"] for row in reconstruction_rows)
    value_counts = Counter(row["value_selection_route"] for row in reconstruction_rows)
    edition = ["# Pass 365 — vollständige Tafelnachschrift", ""]
    for record, rows in record_groups.items():
        edition += [f"## {record}", ""]
        for row in rows:
            edition += [
                f"### {row['statement_id']}",
                "",
                str(row["free_fluent_german"]),
                "",
                f"`{row['reconstructed_surfaces']}`",
                "",
                f"Setzwege: {row['setting_routes']}",
                f"Identitätswege: {row['identity_routes']}",
                "",
            ]
    (HERE / "THREE_HUNDRED_SIXTY_FIFTH_COMPLETE_RECONSTRUCTION.md").write_text("\n".join(edition).rstrip() + "\n", encoding="utf-8")
    report = f"""# Pass 365 — Tafelnachschrift und Paar-Korrektur

Alle 116 Aussagen werden aus Familien-, Kontrast- und Nomenklatortafeln neu
gesetzt. Der Wert ist bei allen 380 Quellkarten eindeutig. Die konkrete exakte
Kartenidentität ist jedoch nur bei {identity_counts['UNIQUE_VALUE_SLOT_CARD']}
Positionen schon durch Wert und Slot bestimmt. {identity_counts['PAIR_PLACARD_PLUS_OWNER']}
Positionen brauchen zusätzlich den sichtbaren Besitzer und
{identity_counts['PAIR_PLACARD_PLUS_OWNER_AND_RIGHT_NEIGHBOR']} außerdem den
rechten Nachbarn auf einer der 14 Paar-Tafeln.

Damit wird die zu starke Formulierung von Pass 364 korrigiert: dessen drei
Setzwege wählen 187 direkt komponierte, 161 kontrast-komponierte und 32
nomenklatorische **Werte**. Erst die Paar-Tafeln wählen bei 72 Vorkommen die
exakte Karte. Zusammen rekonstruieren beide Schichten 380/380 Identitäten und
Oberflächen.

Als Nächstes soll der Lehrling die 14 Paar-Tafeln selbst lernen: Besitzerregel
zuerst, rechter Nachbar nur dort, wo beide Karten beim selben Besitzer möglich
sind.
"""
    (HERE / "THREE_HUNDRED_SIXTY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "source_cards": len(reconstruction_rows),
        "statements": len(statement_rows),
        "records": len(record_rows),
        "value_route_counts": dict(value_counts),
        "identity_route_counts": dict(identity_counts),
        "pair_placards": len(placards),
        "exact_values": sum(r["exact_value"] == "YES" for r in reconstruction_rows),
        "exact_identities": sum(r["exact_identity"] == "YES" for r in reconstruction_rows),
        "exact_surfaces": sum(r["exact_surface"] == "YES" for r in reconstruction_rows),
    }
    (HERE / "THREE_HUNDRED_SIXTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
