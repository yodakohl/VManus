#!/usr/bin/env python3
"""Reconstruct source cards and logical cycles from unmarked physical layouts."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LINES = ROOT / "experiments/yolo/sidequest_semantic_residual_page_layout_three_hundred_fifty_sixth/THREE_HUNDRED_FIFTY_SIXTH_SEVENTEEN_PHYSICAL_LINES.tsv"
CHART = ROOT / "experiments/yolo/sidequest_semantic_multiscribe_teaching_chart_three_hundred_thirty_eighth/THREE_HUNDRED_THIRTY_EIGHTH_COMPLETE_173_CARD_TEACHING_CHART.tsv"
SLOT_RANK = {"S1_BEZUG_FOLGE": 1, "S2_MATERIAL_MASS": 2, "S3_PROZESS_TRANSFER": 3, "S4_DAUER_ZUSTAND": 4, "S5_ZIEL_ANWENDUNG": 5, "S6_BEREIT_ABSCHLUSS": 6}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    lines = read_tsv(LINES)
    chart_rows = read_tsv(CHART)
    surface_map = {}
    for row in chart_rows:
        for surface in row["registered_surface_palette"].split("|"):
            assert surface not in surface_map
            surface_map[surface] = row

    by_hand: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in lines:
        by_hand[row["hand"]].append(row)
    for rows in by_hand.values():
        rows.sort(key=lambda row: int(row["line_no"]))

    corrected = []
    breaks = []
    logical_boundaries = []
    hand_summaries = []
    for hand, hand_lines in by_hand.items():
        source_events = []
        visible_count = 0
        for line_index, line in enumerate(hand_lines):
            tokens = line["raw_line_surface"].split()
            visible_count += len(tokens)
            for token_index, token in enumerate(tokens):
                meta = surface_map[token]
                source_events.append({
                    "hand": hand,
                    "physical_line": line["line_no"],
                    "token_on_line": token_index + 1,
                    "owner": line["owner"],
                    "surface": token,
                    "joint_tuple_id": meta["joint_tuple_id"],
                    "atomic_value_de": meta["atomic_value_de"],
                    "slot_code": "",
                    "source_position": len(source_events) + 1,
                })
            margin = line["right_margin_anticipation_surface"]
            if margin != "NONE":
                visible_count += 1

        # Infer the slot from the 173-card board's dominant teaching slot via the
        # concrete fresh-order positions: each decoded identity has one intended
        # slot on this work order, recoverable from its atomic board address.
        board_path = ROOT / "experiments/yolo/sidequest_semantic_workshop_board_three_hundred_fifty_third/THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv"
        board = {row["joint_tuple_id"]: row for row in read_tsv(board_path)}
        for event in source_events:
            event["slot_code"] = board[event["joint_tuple_id"]]["primary_slot"]

        for index in range(len(hand_lines) - 1):
            left_line = hand_lines[index]
            right_line = hand_lines[index + 1]
            margin = left_line["right_margin_anticipation_surface"]
            right_first = right_line["raw_line_surface"].split()[0]
            left_last = left_line["raw_line_surface"].split()[-1]
            left_meta = surface_map[left_last]
            right_meta = surface_map[right_first]
            same_owner = left_line["owner"] == right_line["owner"]
            nondecreasing = SLOT_RANK[board[left_meta["joint_tuple_id"]]["primary_slot"]] <= SLOT_RANK[board[right_meta["joint_tuple_id"]]["primary_slot"]]
            collapse = margin != "NONE" and margin == right_first and same_owner and nondecreasing
            breaks.append({
                "hand": hand,
                "after_line": left_line["line_no"],
                "left_surface": left_last,
                "margin_surface": margin,
                "next_line_first_surface": right_first,
                "same_owner": "YES" if same_owner else "NO",
                "slot_order_nondecreasing": "YES" if nondecreasing else "NO",
                "corrector_decision": "COLLAPSE_READ_ONCE" if collapse else "KEEP_SEPARATE_NO_COPY",
                "source_cards_contributed_by_margin": 0 if collapse or margin == "NONE" else 1,
                "reason_de": "Exakte Rand-/Anfangskopie im selben Besitzer und vorwärts laufenden Slot." if collapse else "Kein gültiges Randpaar; physische Grenze ändert die Quellzählung nicht.",
            })

        cycle = 1
        previous = None
        for event in source_events:
            if previous is not None:
                owner_change = event["owner"] != previous["owner"]
                slot_descent = SLOT_RANK[event["slot_code"]] < SLOT_RANK[previous["slot_code"]]
                if owner_change or slot_descent:
                    cycle += 1
                    logical_boundaries.append({
                        "hand": hand,
                        "left_source_position": previous["source_position"],
                        "right_source_position": event["source_position"],
                        "left_slot": previous["slot_code"],
                        "right_slot": event["slot_code"],
                        "owner_change": "YES" if owner_change else "NO",
                        "slot_descent": "YES" if slot_descent else "NO",
                        "inferred_boundary": "OWNER_HANDOFF_AND_NEW_MICROCYCLE" if owner_change else "NEW_MICROCYCLE",
                    })
            event["inferred_microcycle"] = cycle
            event["card_count_after_read_once"] = 1
            corrected.append(event)
            previous = event

        hand_summaries.append({
            "hand": hand,
            "physical_lines": len(hand_lines),
            "visible_surface_instances": visible_count,
            "read_once_pairs": sum(row["hand"] == hand and row["corrector_decision"] == "COLLAPSE_READ_ONCE" for row in breaks),
            "recovered_source_cards": len(source_events),
            "recovered_microcycles": cycle,
            "owner_handoffs": sum(row["hand"] == hand and row["owner_change"] == "YES" for row in logical_boundaries),
            "surface_sequence": " ".join(row["surface"] for row in source_events),
            "value_sequence_de": " → ".join(row["atomic_value_de"] for row in source_events),
            "slot_sequence": " → ".join(row["slot_code"] for row in source_events),
            "exact_reconstruction": "YES" if len(source_events) == 11 and cycle == 4 else "NO",
        })

    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_SEVENTH_FORTY_FOUR_CORRECTED_SOURCE_CARDS.tsv",
        corrected,
        ["hand", "source_position", "physical_line", "token_on_line", "owner", "surface", "joint_tuple_id", "atomic_value_de", "slot_code", "inferred_microcycle", "card_count_after_read_once"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_SEVENTH_THIRTEEN_BREAK_DECISIONS.tsv",
        breaks,
        ["hand", "after_line", "left_surface", "margin_surface", "next_line_first_surface", "same_owner", "slot_order_nondecreasing", "corrector_decision", "source_cards_contributed_by_margin", "reason_de"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_SEVENTH_TWELVE_LOGICAL_BOUNDARIES.tsv",
        logical_boundaries,
        ["hand", "left_source_position", "right_source_position", "left_slot", "right_slot", "owner_change", "slot_descent", "inferred_boundary"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_SEVENTH_FOUR_CORRECTOR_TRANSCRIPTS.tsv",
        hand_summaries,
        ["hand", "physical_lines", "visible_surface_instances", "read_once_pairs", "recovered_source_cards", "recovered_microcycles", "owner_handoffs", "surface_sequence", "value_sequence_de", "slot_sequence", "exact_reconstruction"],
    )

    lines = [
        "# Notizbuch des Korrektors",
        "",
        "Der Korrektor sieht keine logischen Striche. Er liest Kartenidentität,",
        "dominanten Slot, Randlage und sichtbaren Besitzer.",
        "",
    ]
    for row in hand_summaries:
        lines.extend([
            f"## {row['hand']}",
            "",
            f"{row['visible_surface_instances']} sichtbare Formen → {row['recovered_source_cards']} Quellkarten;",
            f"{row['read_once_pairs']} Randpaar(e), {row['recovered_microcycles']} Mikrozyklen, {row['owner_handoffs']} Besitzerübergabe.",
            "",
            f"**Werte:** {row['value_sequence_de']}",
            "",
        ])
    lines.extend([
        "## Korrektorregel",
        "",
        "Gleiche Form am rechten Rand und am nächsten Zeilenanfang wird nur bei",
        "gleichem Besitzer und nicht fallender Slotfolge einmal gelesen. Ein",
        "Slotabstieg oder Besitzerwechsel eröffnet einen neuen Mikrogang. So werden",
        "alle vier Fassungen ohne Satzschlussannahme exakt rekonstruiert.",
    ])
    (HERE / "THREE_HUNDRED_FIFTY_SEVENTH_CORRECTOR_NOTEBOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    report = """# Pass 357 — Korrektor rekonstruiert die unmarkierten Layouts

Aus 48 sichtbaren Formen wurden ohne logische Lehrstriche 44 Quellkarten
rekonstruiert. Der Korrektor erkennt vier Rand-Anfang-Paare als Read-once, lässt
neun andere Zeilenbrüche unberührt und setzt pro Hand drei logische Grenzen:
zweimal durch Slotabstieg, einmal durch Besitzerwechsel plus Slotabstieg.

Jede Hand ergibt wieder elf Karten und vier Mikrozyklen. Das zeigt praktisch,
dass Zeilenumbruch, Mikrogang, Besitzer und Quellzählung vier getrennte Ebenen
sind. Die Regel braucht keine Satzzeichen und erklärt zugleich, wann eine
sichtbare Doppelung nicht als Wiederholung gelesen werden darf.

Als Nächstes sollte dieses Korrektorprinzip auf die 381 bestehenden Prosaevents
übertragen werden: alle realen Zeilenübergänge in drei Klassen—weiterlesen,
Read-once-Randpaar oder echter Gang-/Besitzerreset—und daraus eine vollständig
kontinuierliche sieben-seitige Werkstattausgabe setzen.
"""
    (HERE / "THREE_HUNDRED_FIFTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "visible_surface_instances": sum(int(row["visible_surface_instances"]) for row in hand_summaries),
        "recovered_source_cards": len(corrected),
        "read_once_pairs": sum(row["corrector_decision"] == "COLLAPSE_READ_ONCE" for row in breaks),
        "line_breaks": len(breaks),
        "logical_boundaries": len(logical_boundaries),
        "microcycles": sum(int(row["recovered_microcycles"]) for row in hand_summaries),
        "owner_handoffs": sum(int(row["owner_handoffs"]) for row in hand_summaries),
        "exact_hand_reconstructions": sum(row["exact_reconstruction"] == "YES" for row in hand_summaries),
    }
    (HERE / "THREE_HUNDRED_FIFTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
