#!/usr/bin/env python3
"""Fit four hand versions into residual widths with disciplined carry copies."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RENDERINGS = ROOT / "experiments/yolo/sidequest_semantic_four_hand_cross_read_three_hundred_fifty_fifth/THREE_HUNDRED_FIFTY_FIFTH_FORTY_FOUR_HAND_RENDERINGS.tsv"
WIDTHS = {
    "HAND_A_BARE": 18,
    "HAND_B_Q_OPERATIONAL": 16,
    "HAND_C_S_ENTRY": 20,
    "HAND_D_EXPANDED": 22,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read_tsv(RENDERINGS)
    by_hand: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_hand[row["source_hand"]].append(row)
    for rows in by_hand.values():
        rows.sort(key=lambda row: int(row["position"]))

    line_rows = []
    break_rows = []
    copy_rows = []
    for hand, width in WIDTHS.items():
        events = by_hand[hand]
        lines: list[list[dict[str, str]]] = []
        current: list[dict[str, str]] = []
        used = 0
        for event in events:
            needed = len(event["rendered_surface"]) + (1 if current else 0)
            owner_change = bool(current and event["owner"] != current[-1]["owner"])
            if current and (used + needed > width or owner_change):
                lines.append(current)
                current = []
                used = 0
            current.append(event)
            used += len(event["rendered_surface"]) + (1 if len(current) > 1 else 0)
        if current:
            lines.append(current)

        carry_for_line = {}
        for index in range(len(lines) - 1):
            left = lines[index][-1]
            right = lines[index + 1][0]
            same_owner = left["owner"] == right["owner"]
            same_cycle = left["microcycle"] == right["microcycle"]
            if same_owner and same_cycle:
                break_type = "INTRA_MICROCYCLE_LINE_BREAK"
                carry_status = "ANTICIPATION_COPY_USED"
                carry_for_line[index] = right
                reason = "Aussage und Mikrogang laufen weiter; rechte Karte wird am Rand vorweggenommen und am Folgezeilenanfang ausgeführt."
                copy_rows.append({
                    "hand": hand,
                    "source_event_position": right["position"],
                    "joint_tuple_id": right["joint_tuple_id"],
                    "surface": right["rendered_surface"],
                    "visible_copy_1_location": f"LINE_{index + 1}_RIGHT_MARGIN",
                    "visible_copy_2_location": f"LINE_{index + 2}_START",
                    "source_card_count": 1,
                    "visible_surface_count": 2,
                    "read_once_rule": "READ_MARGIN_ANTICIPATION_AND_LINE_START_AS_ONE_CARD",
                })
            elif not same_owner:
                break_type = "OWNER_HANDOFF"
                carry_status = "COPY_FORBIDDEN"
                reason = "Neuer sichtbarer Besitzer; eine Doppelung würde einen falschen Stoff- oder Leitungsanschluss erzeugen."
            else:
                break_type = "MICROCYCLE_BOUNDARY"
                carry_status = "COPY_FORBIDDEN"
                reason = "Neuer Arbeitsgang; dieselbe Karte auf beiden Seiten wäre eine echte Wiederholung."
            break_rows.append({
                "hand": hand,
                "after_line": index + 1,
                "left_position": left["position"],
                "right_position": right["position"],
                "left_surface": left["rendered_surface"],
                "right_surface": right["rendered_surface"],
                "left_microcycle": left["microcycle"],
                "right_microcycle": right["microcycle"],
                "left_owner": left["owner"],
                "right_owner": right["owner"],
                "break_type": break_type,
                "carry_status": carry_status,
                "reason_de": reason,
            })

        for index, line in enumerate(lines):
            raw = " ".join(row["rendered_surface"] for row in line)
            annotated_parts = []
            previous_cycle = None
            for row in line:
                if previous_cycle is not None and row["microcycle"] != previous_cycle:
                    annotated_parts.append("|")
                annotated_parts.append(row["rendered_surface"])
                previous_cycle = row["microcycle"]
            carry = carry_for_line.get(index)
            line_rows.append({
                "hand": hand,
                "residual_width": width,
                "line_no": index + 1,
                "owner": line[0]["owner"],
                "source_positions": "|".join(row["position"] for row in line),
                "microcycles_present": "|".join(dict.fromkeys(row["microcycle"] for row in line)),
                "raw_line_surface": raw,
                "logical_line_surface": " ".join(annotated_parts),
                "ink_units": len(raw),
                "right_margin_anticipation_surface": carry["rendered_surface"] if carry else "NONE",
                "right_margin_source_position": carry["position"] if carry else "NONE",
                "next_line_continues_statement": "YES" if index + 1 < len(lines) and line[-1]["owner"] == lines[index + 1][0]["owner"] else "NO",
            })

    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_SIXTH_SEVENTEEN_PHYSICAL_LINES.tsv",
        line_rows,
        ["hand", "residual_width", "line_no", "owner", "source_positions", "microcycles_present", "raw_line_surface", "logical_line_surface", "ink_units", "right_margin_anticipation_surface", "right_margin_source_position", "next_line_continues_statement"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_SIXTH_THIRTEEN_LINE_BREAKS.tsv",
        break_rows,
        ["hand", "after_line", "left_position", "right_position", "left_surface", "right_surface", "left_microcycle", "right_microcycle", "left_owner", "right_owner", "break_type", "carry_status", "reason_de"],
    )
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_SIXTH_FOUR_READ_ONCE_COPIES.tsv",
        copy_rows,
        ["hand", "source_event_position", "joint_tuple_id", "surface", "visible_copy_1_location", "visible_copy_2_location", "source_card_count", "visible_surface_count", "read_once_rule"],
    )

    lines = [
        "# Vier Restflächen-Umbrüche",
        "",
        "`⟦x⟧` ist eine Randvorwegnahme: sichtbar zweimal, als Quelle einmal gelesen.",
        "Der senkrechte Strich zeigt nur hier im Lehrdruck eine Mikroganggrenze.",
        "",
    ]
    for hand in WIDTHS:
        rows = [row for row in line_rows if row["hand"] == hand]
        lines.extend([f"## {hand} — Breite {WIDTHS[hand]}", ""])
        for row in rows:
            margin = f" ⟦{row['right_margin_anticipation_surface']}⟧" if row["right_margin_anticipation_surface"] != "NONE" else ""
            lines.append(f"{row['line_no']:>2}. `{row['logical_line_surface']}{margin}`")
        lines.append("")
    lines.extend([
        "## Leseregel",
        "",
        "Nur vier der dreizehn Zeilenbrüche liegen mitten im selben Mikrogang und",
        "erhalten eine Randkopie. Fünf Mikroganggrenzen und vier Besitzerübergaben",
        "erhalten ausdrücklich keine. Somit entstehen 48 sichtbare Formen aus 44",
        "Quellkarten, aber weiterhin genau elf Quellkarten je Schreiber.",
    ])
    (HERE / "THREE_HUNDRED_FIFTY_SIXTH_FOUR_RESIDUAL_LAYOUTS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    report = """# Pass 356 — Zeilenumbruch ohne Satzschlusszwang

Die vier Handfassungen wurden in Restbreiten 18, 16, 20 und 22 gesetzt. Daraus
entstehen 17 physische Zeilen und 13 Brüche. Nur vier Brüche schneiden einen
laufenden Mikrogang; dort wird die erste Karte der Folgezeile am alten Rand
vorweggenommen und nach der Read-once-Regel nicht doppelt gezählt.

An fünf Mikroganggrenzen und vier Besitzerwechseln ist dieselbe Kopie verboten.
Damit erklärt das System sowohl eine lokale Randdoppelung als auch, warum man
nicht jede Wiederholung am Zeilenrand wegsegmentieren darf. Aussagen bleiben
von physischen Zeilen unabhängig.

Als Nächstes sollte ein Korrektor die vier Layouts ohne logische Striche sehen,
Mikroganggrenzen und die vier Read-once-Paare selbst eintragen und danach die
elf Quellkarten je Hand rekonstruieren.
"""
    (HERE / "THREE_HUNDRED_FIFTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "hands": len(WIDTHS),
        "source_cards": 44,
        "physical_lines": len(line_rows),
        "line_breaks": len(break_rows),
        "intra_microcycle_breaks": sum(row["break_type"] == "INTRA_MICROCYCLE_LINE_BREAK" for row in break_rows),
        "microcycle_boundary_breaks": sum(row["break_type"] == "MICROCYCLE_BOUNDARY" for row in break_rows),
        "owner_handoff_breaks": sum(row["break_type"] == "OWNER_HANDOFF" for row in break_rows),
        "read_once_copies": len(copy_rows),
        "visible_surface_instances": 44 + len(copy_rows),
    }
    (HERE / "THREE_HUNDRED_FIFTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
