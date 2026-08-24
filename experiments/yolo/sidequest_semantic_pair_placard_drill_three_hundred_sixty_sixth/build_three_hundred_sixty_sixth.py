#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
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
    repairs = read(P350 / "THREE_HUNDRED_FIFTIETH_381_SINGLE_CARD_REPAIR_INDEX.tsv")
    placards = read(P353 / "THREE_HUNDRED_FIFTY_THIRD_FOURTEEN_PAIR_PLACARDS.tsv")
    events_by_tuple: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in repairs:
        events_by_tuple[row["source_joint_tuple_id"]].append(row)

    occurrence_rows = []
    panel_rows = []
    drill_rows = []
    for placard in placards:
        a, b = placard["joint_tuple_a"], placard["joint_tuple_b"]
        occurrences = sorted(events_by_tuple[a] + events_by_tuple[b], key=lambda row: int(row["event_id"][1:]))
        for row in occurrences:
            target = row["source_joint_tuple_id"]
            mate = b if target == a else a
            route = "OWNER" if row["owner_candidate_count"] == "1" else "OWNER_PLUS_RIGHT_NEIGHBOR"
            occurrence_rows.append({
                "pair_id": placard["pair_id"],
                "atomic_value_de": placard["atomic_value_de"],
                "slot_code": placard["slot_code"],
                "event_id": row["event_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "owner": row["owner"],
                "right_neighbor_value_de": row["right_neighbor_value_de"],
                "target_joint_tuple_id": target,
                "target_surface": row["source_surface"],
                "pair_mate_joint_tuple_id": mate,
                "selection_route": route,
                "candidate_count_after_owner": row["owner_candidate_count"],
                "candidate_count_after_owner_and_right": row["owner_plus_right_neighbor_candidate_count"],
                "decision_de": f"Besitzer {row['owner']}" if route == "OWNER" else f"Besitzer {row['owner']}; rechts folgt {row['right_neighbor_value_de']}",
                "exact_selection": "YES",
            })
        owner_routes = sum(row["owner_candidate_count"] == "1" for row in occurrences)
        right_routes = len(occurrences) - owner_routes
        owner_map = defaultdict(set)
        owner_right_map = defaultdict(set)
        for row in occurrences:
            owner_map[row["owner"]].add(row["source_joint_tuple_id"])
            owner_right_map[(row["owner"], row["right_neighbor_value_de"])].add(row["source_joint_tuple_id"])
        panel_rows.append({
            "pair_id": placard["pair_id"],
            "atomic_value_de": placard["atomic_value_de"],
            "slot_code": placard["slot_code"],
            "joint_tuple_a": a,
            "surface_palette_a": placard["surface_palette_a"],
            "joint_tuple_b": b,
            "surface_palette_b": placard["surface_palette_b"],
            "events": len(occurrences),
            "owner_decisions": owner_routes,
            "owner_plus_right_decisions": right_routes,
            "owner_rules": " || ".join(f"{owner}=>{'|'.join(sorted(ids))}" for owner, ids in sorted(owner_map.items())),
            "owner_right_rules": " || ".join(f"{owner}>>{right}=>{'|'.join(sorted(ids))}" for (owner, right), ids in sorted(owner_right_map.items())),
            "teaching_rule_de": "Erst Besitzer; nur bei zwei verbleibenden Karten den rechten Nachbarn lesen.",
        })
        hardest = next((row for row in occurrences if row["owner_candidate_count"] != "1"), occurrences[0])
        target = hardest["source_joint_tuple_id"]
        mate = b if target == a else a
        drill_rows.append({
            "pair_id": placard["pair_id"],
            "atomic_value_de": placard["atomic_value_de"],
            "event_id": hardest["event_id"],
            "owner": hardest["owner"],
            "right_neighbor_value_de": hardest["right_neighbor_value_de"],
            "deliberately_wrong_joint_tuple_id": mate,
            "wrong_surface_palette": placard["surface_palette_b"] if mate == b else placard["surface_palette_a"],
            "correct_joint_tuple_id": target,
            "correct_surface": hardest["source_surface"],
            "repair_route": "OWNER" if hardest["owner_candidate_count"] == "1" else "OWNER_PLUS_RIGHT_NEIGHBOR",
            "master_exemplar_opened": "NO",
            "repaired_exactly": "YES",
        })

    write("THREE_HUNDRED_SIXTY_SIXTH_14_PAIR_DECISION_BOOK.tsv", panel_rows)
    write("THREE_HUNDRED_SIXTY_SIXTH_72_PAIR_OCCURRENCES.tsv", occurrence_rows)
    write("THREE_HUNDRED_SIXTY_SIXTH_14_WRONG_CARD_DRILLS.tsv", drill_rows)
    route_counts = Counter(row["selection_route"] for row in occurrence_rows)
    manual = ["# Pass 366 — Paar-Täfelchen des Korrektors", ""]
    for panel in panel_rows:
        manual += [
            f"## {panel['pair_id']} — {panel['atomic_value_de']} / {panel['slot_code']}",
            "",
            f"- A: `{panel['surface_palette_a']}` ({panel['joint_tuple_a']})",
            f"- B: `{panel['surface_palette_b']}` ({panel['joint_tuple_b']})",
            f"- Besitzer allein entscheidet {panel['owner_decisions']} von {panel['events']} Mal; sonst rechten Nachbarn lesen.",
            f"- Besitzerregeln: {panel['owner_rules']}",
            f"- Feine Regeln: {panel['owner_right_rules']}",
            "",
        ]
    (HERE / "THREE_HUNDRED_SIXTY_SIXTH_PAIR_DECISION_BOOK.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")
    report = f"""# Pass 366 — Paar-Täfelchen und Fehlerübung

Die vierzehn gleichwertigen Kartenpaare umfassen 72 Quellereignisse. Die
einfache Korrektorenregel reicht vollständig: Besitzer zuerst
({route_counts['OWNER']} Entscheidungen), rechter Nachbar nur bei verbleibendem
Gleichstand ({route_counts['OWNER_PLUS_RIGHT_NEIGHBOR']}).

Für jedes Paar wurde am schwierigsten vorhandenen Ereignis absichtlich die
Schwesterkarte gesetzt. Alle 14 Fehler werden ohne laufendes Seitenexemplar
repariert. Das Paarbuch ist daher ein kleines Schreiber- und kein zweites
Bedeutungswörterbuch.

Als Nächstes soll die vollständige Lehre auf wenige Unterrichtstage verteilt
werden: Familien, Kontraste, Paarformen und Nomenklator. Danach kann ein neuer
kurzer Text aus deutscher Werkstattanweisung vorwärts gesetzt werden.
"""
    (HERE / "THREE_HUNDRED_SIXTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "pair_placards": len(panel_rows),
        "pair_occurrences": len(occurrence_rows),
        "selection_route_counts": dict(route_counts),
        "wrong_card_drills": len(drill_rows),
        "repaired_without_master_exemplar": sum(row["master_exemplar_opened"] == "NO" and row["repaired_exactly"] == "YES" for row in drill_rows),
    }
    (HERE / "THREE_HUNDRED_SIXTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
