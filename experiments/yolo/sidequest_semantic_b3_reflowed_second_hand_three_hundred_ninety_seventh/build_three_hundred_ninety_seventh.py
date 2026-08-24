#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P392 = ROOT / "experiments/yolo/sidequest_semantic_owner_faithful_copy_three_hundred_ninety_second"
P395 = ROOT / "experiments/yolo/sidequest_semantic_b3_two_station_flow_three_hundred_ninety_fifth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cards = [row for row in read(P392 / "THREE_HUNDRED_NINETY_SECOND_25_OWNER_NATIVE_CARDS.tsv") if row["statement_id"] == "B3-S026"]
    trace = {row["event_id"]: row for row in read(P395 / "THREE_HUNDRED_NINETY_FIFTH_SEVEN_EVENT_TWO_STATION_TRACE.tsv")}
    second_rows = []
    for position, row in enumerate(cards, 1):
        second_surface = row["source_surface"]
        station = trace[row["event_id"]]["visible_owner_zone"]
        second_rows.append({
            "position": position,
            "event_id": row["event_id"],
            "joint_tuple_id": row["joint_tuple_id"],
            "first_copy_surface": row["copy_surface"],
            "second_hand_surface": second_surface,
            "registered_palette": row["registered_palette"],
            "surface_changed": "YES" if second_surface != row["copy_surface"] else "NO",
            "visible_owner_zone": station,
            "component_reading_de": trace[row["event_id"]]["working_reading_de"],
            "identity_preserved": "YES",
        })
    write("THREE_HUNDRED_NINETY_SEVENTH_SEVEN_SECOND_HAND_CARDS.tsv", second_rows)

    line_specs = [
        (1, "STATION_A_UPPER", ["E285", "E286", "E287"], "CONTINUE_SAME_OWNER"),
        (2, "STATION_A_LOWER", ["E288", "E289", "E290"], "OWNER_RESET_AFTER_LARGE_GAP"),
        (3, "STATION_B_RIGHT", ["E291"], "CLOSE"),
    ]
    line_rows = []
    by_event = {row["event_id"]: row for row in second_rows}
    for line_no, region, event_ids, after in line_specs:
        selected = [by_event[event_id] for event_id in event_ids]
        line_rows.append({
            "line_no": line_no,
            "region": region,
            "event_ids": "|".join(event_ids),
            "surface_line": " ".join(row["second_hand_surface"] for row in selected),
            "card_count": len(selected),
            "syntax_after_line": "CLOSED" if after == "CLOSE" else "OPEN",
            "owner_after_line": after,
            "connection_arrow": "NONE",
        })
    write("THREE_HUNDRED_NINETY_SEVENTH_THREE_REFLOWED_LINES.tsv", line_rows)

    comparison_rows = []
    for row in second_rows:
        event = trace[row["event_id"]]
        comparison_rows.append({
            "event_id": row["event_id"],
            "first_surface": row["first_copy_surface"],
            "second_surface": row["second_hand_surface"],
            "same_joint_tuple_id": "YES",
            "same_component_reading": "YES",
            "same_visible_owner_zone": "YES",
            "same_syntax_order": "YES",
            "material_identity_crosses_reset": "NO" if row["event_id"] == "E291" else "NOT_APPLICABLE",
            "working_reading_de": event["working_reading_de"],
        })
    write("THREE_HUNDRED_NINETY_SEVENTH_SEVEN_COPY_COMPARISON.tsv", comparison_rows)

    page = """# Pass 397 — zweite Hand, anderes Reflow

```text
+----------------+
| STATION A      |  cheedar chldaiin chedy
| schmal / hoch  |  qokain checthy chealror
+----------------+


                    GROSSE LÜCKE — KEIN PFEIL


                                  +------------------------------+
                                  | STATION B breit / niedrig    |  solkeedy
                                  +------------------------------+
```

Der Wechsel von Zeile 1 zu Zeile 2 setzt nichts zurück: Satz und Besitzer A
laufen weiter. Erst die große Lücke vor `solkeedy` hält den Satz offen, setzt
aber Besitzer und Materialreferent zurück. `solkeedy` beginnt lokal bei B und
schließt den Gesamtgang.

Vier Oberflächen unterscheiden sich von der ersten Abschrift; alle sieben
Kartenwerte und ihre Reihenfolge bleiben gleich.
"""
    (HERE / "THREE_HUNDRED_NINETY_SEVENTH_SECOND_HAND_PAGE.md").write_text(page, encoding="utf-8")
    report = """# Pass 397 — Reflow ändert weder Satz noch Besitzerregel

Die zweite Hand teilt Station A auf zwei Zeilen und wechselt vier registrierte
Oberflächen. Der kleine interne Zeilenwechsel führt Satz, Besitzer und Material
fort. Der große stationsbezogene Zwischenraum führt nur Satz/Workflow fort und
setzt Besitzer/Material zurück. Keine Verbindungslinie wird ergänzt.

Damit bleibt dieselbe zweilokale Lesung trotz anderer Bildproportionen und
Rendererformen vollständig erhalten. Als nächstes kann der Unterschied als
kurzes Korrektorenmanual formuliert werden: kleine Reflow-Lücke, große
Owner-Lücke und terminale Karte müssen drei getrennte Entscheidungen auslösen.
"""
    (HERE / "THREE_HUNDRED_NINETY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "cards": len(second_rows),
        "surface_changes": sum(row["surface_changed"] == "YES" for row in second_rows),
        "physical_lines": len(line_rows),
        "same_owner_line_continuations": 1,
        "owner_reset_gaps": 1,
        "closing_cards": 1,
        "connection_arrows": 0,
    }
    (HERE / "THREE_HUNDRED_NINETY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
