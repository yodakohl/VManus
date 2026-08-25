#!/usr/bin/env python3
"""Build Pass 1000: recover apparently missing root pairs inside longer cards."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EMPTY = ROOT / "experiments/yolo/sidequest_semantic_layered_composition_grid_correction_nine_hundred_ninety_seventh/PASS997_TWENTY_FIVE_TRUE_EMPTY_CELLS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth/PASS996_2511_EVENT_INTERLINEAR.tsv"


ABSENCE_NOTES = {
    ("OK", "CTH"): ("NIEDRIG", "gebrauchsfertig setzen", "CTH wird in laengeren Karten von einem Traeger oder Endpunkt gestuetzt; OK+CTH allein bleibt ungebraucht."),
    ("OT", "CTH"): ("NIEDRIG", "danach den bereiten Posten nehmen", "Der Folgeschritt nimmt eine ganze Bereitschaftskarte, nicht den nackten Zustand CTH."),
    ("CH", "AIN"): ("HOCH", "eine Portion nehmen", "Staerkste echte Vorhersage: CH+AIIN ist belegt, AIN ist sonst produktiv, und die Kurzform kollidiert mit nichts."),
    ("L", "AIR"): ("SEHR_NIEDRIG", "den Lauf leiten", "L und AIR tragen beide bereits Weg/Lauf; die Zweierform waere wahrscheinlich absichtlich redundant."),
    ("L", "CTH"): ("SEHR_NIEDRIG", "den bereiten Posten leiten", "Ein Bereitschaftszustand ist kein Leitungsargument; die Werkstatt setzt erst den Posten und markiert danach CTH."),
    ("P", "AIN"): ("MITTEL", "eine Portion einsetzen", "P setzt bevorzugt einen konkreten Posten oder eine Quelle ein; Portion kann als getrennte Mengenkarte folgen."),
    ("P", "AIIN"): ("MITTEL", "nach Mass einsetzen", "P setzt bevorzugt einen konkreten Posten oder eine Quelle ein; Mass kann als getrennte Vorgabekarte folgen."),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    empty_rows = read_tsv(EMPTY)
    events = read_tsv(EVENTS)
    output_rows: list[dict[str, object]] = []

    for gap in empty_rows:
        left, right = gap["left_root"], gap["right_root"]
        adjacent_events: list[dict[str, str]] = []
        ordered_only_events: list[dict[str, str]] = []
        for event in events:
            tokens = event["component_recipe"].split("+")
            adjacent = any(tokens[i] == left and tokens[i + 1] == right for i in range(len(tokens) - 1))
            ordered = any(tokens[i] == left and tokens[j] == right for i in range(len(tokens)) for j in range(i + 1, len(tokens)))
            if adjacent:
                adjacent_events.append(event)
            elif ordered:
                ordered_only_events.append(event)

        if adjacent_events:
            status = "IN_LAENGERER_KARTE_DIREKT_BELEGT"
            rule = "Als inneres Paar produktiv; nur die nackte Zweierkarte fehlt."
        elif ordered_only_events:
            status = "IN_LAENGERER_KARTE_GETRENNT_BELEGT"
            rule = "Die Reihenfolge ist produktiv, braucht aber auf diesen Seiten einen Zwischenkern."
        else:
            status = "ECHTE_OFFENE_ZWEIERKOMBINATION"
            rule = ABSENCE_NOTES[(left, right)][2]

        collision = gap["candidate_surface_collision"] == "JA"
        if collision and adjacent_events:
            status = "KURZFORM_KOLLIDIERT__ERWEITERTE_FORM_BELEGT"
            rule = "Die Bedeutung ist produktiv; die kollidierende Kurzform wird durch eine laengere Karte eindeutig gemacht."

        embedded = adjacent_events + ordered_only_events
        output_rows.append({
            "left_root": left,
            "right_root": right,
            "literal_prediction_de": gap["literal_prediction_de"],
            "simple_candidate_surface": gap["simple_candidate_surface"],
            "candidate_surface_collision": gap["candidate_surface_collision"],
            "collision_with": gap["collision_with"],
            "adjacent_events": len(adjacent_events),
            "ordered_nonadjacent_events": len(ordered_only_events),
            "ordered_total_events": len(embedded),
            "adjacent_surfaces": "|".join(sorted({e["surface"] for e in adjacent_events})) or "KEINE",
            "adjacent_recipes": "|".join(sorted({e["component_recipe"] for e in adjacent_events})) or "KEINE",
            "embedded_pages": "|".join(sorted({e["physical_page"] for e in embedded})) or "KEINE",
            "revised_status": status,
            "workshop_rule_de": rule,
        })

    fields = list(output_rows[0])
    full_path = OUT / "PASS1000_25_GAP_RECLASSIFICATION.tsv"
    write_tsv(full_path, output_rows, fields)

    embedded_rows = [row for row in output_rows if int(row["adjacent_events"]) > 0]
    embedded_path = OUT / "PASS1000_12_EMBEDDED_ADJACENCIES.tsv"
    write_tsv(embedded_path, embedded_rows, fields)

    absent_rows = []
    for row in output_rows:
        if row["revised_status"] != "ECHTE_OFFENE_ZWEIERKOMBINATION":
            continue
        priority, reading, explanation = ABSENCE_NOTES[(str(row["left_root"]), str(row["right_root"]))]
        absent_rows.append({
            "prediction_rank": 0,
            "left_root": row["left_root"],
            "right_root": row["right_root"],
            "candidate_surface": row["simple_candidate_surface"],
            "predicted_reading_de": reading,
            "prediction_priority": priority,
            "current_interpretation_de": explanation,
        })
    priority_order = {"HOCH": 0, "MITTEL": 1, "NIEDRIG": 2, "SEHR_NIEDRIG": 3}
    absent_rows.sort(key=lambda row: (priority_order[str(row["prediction_priority"])], str(row["candidate_surface"])))
    for index, row in enumerate(absent_rows, 1):
        row["prediction_rank"] = index
    absent_path = OUT / "PASS1000_7_REAL_ABSENCES_AND_PREDICTIONS.tsv"
    write_tsv(absent_path, absent_rows, list(absent_rows[0]))

    collision_rows = []
    for row in output_rows:
        if row["candidate_surface_collision"] != "JA":
            continue
        collision_rows.append({
            "pair": f'{row["left_root"]}+{row["right_root"]}',
            "blocked_short_surface": row["simple_candidate_surface"],
            "collision_with": row["collision_with"],
            "embedded_adjacent_events": row["adjacent_events"],
            "observed_expanded_surfaces": row["adjacent_surfaces"],
            "workshop_solution_de": "zusaetzlichen Rahmen/Kern schreiben; Bedeutung bleibt zusammensetzbar",
        })
    collision_path = OUT / "PASS1000_3_COLLISION_REPAIRS.tsv"
    write_tsv(collision_path, collision_rows, list(collision_rows[0]))

    counts = defaultdict(int)
    for row in output_rows:
        counts[str(row["revised_status"])] += 1
    summary = {
        "pass": 1000,
        "source_exact_pair_gaps": len(output_rows),
        "embedded_adjacent_pairs": len(embedded_rows),
        "embedded_ordered_only_pairs": sum(1 for row in output_rows if row["revised_status"] == "IN_LAENGERER_KARTE_GETRENNT_BELEGT"),
        "genuine_absent_pairs": len(absent_rows),
        "collision_pairs_recovered_in_expanded_cards": len(collision_rows),
        "adjacent_event_total": sum(int(row["adjacent_events"]) for row in output_rows),
        "ordered_nonadjacent_event_total": sum(int(row["ordered_nonadjacent_events"]) for row in output_rows),
        "status_counts": dict(sorted(counts.items())),
        "strongest_new_surface_prediction": "chain",
        "strongest_new_reading_de": "eine Portion nehmen",
        "input_sha256": {str(EMPTY.relative_to(ROOT)): sha256(EMPTY), str(EVENTS.relative_to(ROOT)): sha256(EVENTS)},
        "output_sha256": {
            full_path.name: sha256(full_path),
            embedded_path.name: sha256(embedded_path),
            absent_path.name: sha256(absent_path),
            collision_path.name: sha256(collision_path),
        },
    }
    (OUT / "PASS1000_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
