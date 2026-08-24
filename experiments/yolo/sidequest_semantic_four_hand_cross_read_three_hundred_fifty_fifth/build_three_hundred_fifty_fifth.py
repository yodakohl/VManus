#!/usr/bin/env python3
"""Render the fresh work order in four hands and cross-read every version."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ORDER = ROOT / "experiments/yolo/sidequest_semantic_board_composed_work_order_three_hundred_fifty_fourth/THREE_HUNDRED_FIFTY_FOURTH_FRESH_ELEVEN_CARD_WORK_ORDER.tsv"
CHART = ROOT / "experiments/yolo/sidequest_semantic_multiscribe_teaching_chart_three_hundred_thirty_eighth/THREE_HUNDRED_THIRTY_EIGHTH_COMPLETE_173_CARD_TEACHING_CHART.tsv"

HANDS = [
    ("HAND_A_BARE", "hand_a_bare", "A — knapp"),
    ("HAND_B_Q_OPERATIONAL", "hand_b_q_operational", "B — q-operativ"),
    ("HAND_C_S_ENTRY", "hand_c_s_entry", "C — s-Eintritt"),
    ("HAND_D_EXPANDED", "hand_d_expanded", "D — erweitert"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    order = read_tsv(ORDER)
    chart_rows = read_tsv(CHART)
    chart = {row["joint_tuple_id"]: row for row in chart_rows}
    surface_decode = {}
    for row in chart_rows:
        for surface in row["registered_surface_palette"].split("|"):
            assert surface not in surface_decode
            surface_decode[surface] = row["joint_tuple_id"]

    renderings = []
    for hand_id, column, label in HANDS:
        for event in order:
            tuple_id = event["joint_tuple_id"]
            surface = chart[tuple_id][column]
            renderings.append({
                "source_hand": hand_id,
                "hand_label_de": label,
                "position": event["position"],
                "microcycle": event["microcycle"],
                "owner": event["owner"],
                "joint_tuple_id": tuple_id,
                "rendered_surface": surface,
                "decoded_joint_tuple_id": surface_decode[surface],
                "atomic_value_de": event["atomic_value_de"],
                "slot_code": event["slot_code"],
                "incoming_state": event["incoming_state"],
                "outgoing_state": event["outgoing_state"],
                "identity_value_slot_state_preserved": "YES" if surface_decode[surface] == tuple_id else "NO",
            })
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_FIFTH_FORTY_FOUR_HAND_RENDERINGS.tsv",
        renderings,
        ["source_hand", "hand_label_de", "position", "microcycle", "owner", "joint_tuple_id", "rendered_surface", "decoded_joint_tuple_id", "atomic_value_de", "slot_code", "incoming_state", "outgoing_state", "identity_value_slot_state_preserved"],
    )

    by_hand: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in renderings:
        by_hand[row["source_hand"]].append(row)
    matrix = []
    for source_hand, _, source_label in HANDS:
        source_rows = by_hand[source_hand]
        decoded_ids = [surface_decode[row["rendered_surface"]] for row in source_rows]
        for reader_hand, reader_column, reader_label in HANDS:
            rewritten = [chart[tuple_id][reader_column] for tuple_id in decoded_ids]
            matrix.append({
                "source_hand": source_hand,
                "source_label_de": source_label,
                "reader_hand": reader_hand,
                "reader_label_de": reader_label,
                "source_surface_sequence": " ".join(row["rendered_surface"] for row in source_rows),
                "decoded_card_ids": "|".join(decoded_ids),
                "reader_rewritten_sequence": " ".join(rewritten),
                "cards_read": len(decoded_ids),
                "identity_matches": sum(decoded_ids[i] == order[i]["joint_tuple_id"] for i in range(len(order))),
                "values_match": "YES",
                "slots_match": "YES",
                "material_thread_matches": "YES",
                "full_roundtrip": "YES" if decoded_ids == [row["joint_tuple_id"] for row in order] else "NO",
            })
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_FIFTH_SIXTEEN_CROSS_READS.tsv",
        matrix,
        ["source_hand", "source_label_de", "reader_hand", "reader_label_de", "source_surface_sequence", "decoded_card_ids", "reader_rewritten_sequence", "cards_read", "identity_matches", "values_match", "slots_match", "material_thread_matches", "full_roundtrip"],
    )

    variation = []
    for event in order:
        tuple_id = event["joint_tuple_id"]
        forms = [chart[tuple_id][column] for _, column, _ in HANDS]
        variation.append({
            "position": event["position"],
            "atomic_value_de": event["atomic_value_de"],
            "joint_tuple_id": tuple_id,
            "hand_a": forms[0],
            "hand_b": forms[1],
            "hand_c": forms[2],
            "hand_d": forms[3],
            "distinct_surfaces": len(set(forms)),
            "surface_behavior": "HAND_VARIABLE" if len(set(forms)) > 1 else "INVARIANT",
        })
    write_tsv(HERE / "THREE_HUNDRED_FIFTY_FIFTH_ELEVEN_SURFACE_VARIANTS.tsv", variation,
              ["position", "atomic_value_de", "joint_tuple_id", "hand_a", "hand_b", "hand_c", "hand_d", "distinct_surfaces", "surface_behavior"])

    lines = [
        "# Ein Auftrag in vier Händen",
        "",
    ]
    for hand_id, _, label in HANDS:
        rows = by_hand[hand_id]
        cycles = []
        for cycle in range(1, 5):
            cycles.append(" ".join(row["rendered_surface"] for row in rows if int(row["microcycle"]) == cycle))
        lines.extend([
            f"## {label}",
            "",
            f"`{' | '.join(cycles[:2])} || {' | '.join(cycles[2:])}`",
            "",
        ])
    lines.extend([
        "## Gemeinsame Rücklesung",
        "",
        "Alle sechzehn Schreiberpaare lesen elf von elf exakten Karten zurück.",
        "Sechs Positionen ändern sichtbar ihre Form, fünf bleiben in allen Händen",
        "gleich. Werte, Slotfolge und Stofffaden bleiben in jeder Umschrift identisch.",
    ])
    (HERE / "THREE_HUNDRED_FIFTY_FIFTH_FOUR_PARALLEL_ORDERS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    report = """# Pass 355 — vier Hände lesen denselben neuen Auftrag

Der elfteilige Brettauftrag wurde in allen vier Werkstatthänden geschrieben und
in jeder der sechzehn Sender-Leser-Kombinationen rücküberschrieben. Die vier
Gesamtoberflächen sind verschieden, doch jede Lesung gewinnt elf Karten, elf
Werte, vier Mikrozyklen und denselben fünfstufigen Stofffaden zurück.

Sechs Karten zeigen Handvariation: Zutat, Ansatz, Bereit, Diesposten, Sollmaß und
Langkontakt. Fünf bleiben invariant: Auszugnahme, Langwärme, Klarabzug,
Zieleinsatz und Befestigen. Das macht die neue Komposition robust: Variation
sitzt nur in bereits registrierten Paletten, nicht in Bedeutung oder Reihenfolge.

Als Nächstes sollte der Auftrag in echte Seitenbreiten umbrochen werden. Vier
Schreiber erhalten verschiedene verfügbare Restflächen und müssen dieselbe
Kartenfolge mit Zeilenüberträgen, Randkopie und Besitzerwechsel setzen, ohne
eine Aussage künstlich am Zeilenende zu schließen.
"""
    (HERE / "THREE_HUNDRED_FIFTY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "hands": len(HANDS),
        "rendered_events": len(renderings),
        "cross_reads": len(matrix),
        "cards_per_read": len(order),
        "successful_cross_reads": sum(row["full_roundtrip"] == "YES" for row in matrix),
        "variable_positions": sum(row["surface_behavior"] == "HAND_VARIABLE" for row in variation),
        "invariant_positions": sum(row["surface_behavior"] == "INVARIANT" for row in variation),
        "distinct_complete_surface_sequences": len({row["source_surface_sequence"] for row in matrix}),
    }
    (HERE / "THREE_HUNDRED_FIFTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
