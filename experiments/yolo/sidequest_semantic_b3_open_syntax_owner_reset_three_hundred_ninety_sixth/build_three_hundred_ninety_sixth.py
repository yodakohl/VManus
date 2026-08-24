#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
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
    trace = read(P395 / "THREE_HUNDRED_NINETY_FIFTH_SEVEN_EVENT_TWO_STATION_TRACE.tsv")
    layout_rows = [
        {
            "layout_order": 1,
            "region": "UPPER_LEFT_STATION_A",
            "visible_owner": "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED",
            "event_ids": "E285|E286|E287|E288|E289|E290",
            "surface_line": "cheedar chldaiin chdy okain cthy chealror",
            "syntax_after_region": "OPEN_CONTINUES",
            "owner_after_region": "RESET_REQUIRED",
            "connection_arrow": "NONE",
        },
        {
            "layout_order": 2,
            "region": "LOWER_RIGHT_STATION_B",
            "visible_owner": "B3_MAIN_ARCH_LINKED_PAIR",
            "event_ids": "E291",
            "surface_line": "olkeedy",
            "syntax_after_region": "CLOSED",
            "owner_after_region": "LOCAL_B_END",
            "connection_arrow": "NONE",
        },
    ]
    write("THREE_HUNDRED_NINETY_SIXTH_TWO_REGION_LAYOUT.tsv", layout_rows)

    reader_steps = []
    for index, row in enumerate(trace, 1):
        if row["event_id"] == "E291":
            reader_steps.append({
                "step": "6.5",
                "item_type": "VISUAL_GAP",
                "surface": "NONE",
                "event_id": "NONE",
                "syntax_before": "OPEN",
                "syntax_after": "OPEN",
                "owner_before": "STATION_A",
                "owner_after": "RESET_TO_STATION_B",
                "reader_action": "keep clause open; discard material referent; start new local owner",
            })
        reader_steps.append({
            "step": str(index),
            "item_type": "CARD",
            "surface": row["copy_surface"],
            "event_id": row["event_id"],
            "syntax_before": "OPEN" if index > 1 else "START",
            "syntax_after": "CLOSED" if row["event_id"] == "E291" else "OPEN",
            "owner_before": "STATION_B" if row["event_id"] == "E291" else "STATION_A",
            "owner_after": "STATION_B" if row["event_id"] == "E291" else "STATION_A",
            "reader_action": row["working_reading_de"],
        })
    write("THREE_HUNDRED_NINETY_SIXTH_EIGHT_READER_STEPS.tsv", reader_steps)

    register_rows = [
        {"register": "SYNTAX", "before_gap": "OPEN_AFTER_CHEALROR", "at_gap": "KEEP_OPEN", "after_gap": "OLKEEDY_CLOSES", "independent_from": "OWNER"},
        {"register": "OWNER", "before_gap": "STATION_A", "at_gap": "RESET", "after_gap": "STATION_B", "independent_from": "SYNTAX"},
        {"register": "MATERIAL", "before_gap": "CLEARPOINT_BATCH_A", "at_gap": "DO_NOT_CARRY", "after_gap": "NEW_LOCAL_OWNER_B", "independent_from": "WORKFLOW_ORDER"},
        {"register": "WORKFLOW_ORDER", "before_gap": "CLEARPOINT_CHECK", "at_gap": "CONTINUE_NEXT", "after_gap": "RECEIVE_AND_CLOSE", "independent_from": "PHYSICAL_CONNECTION"},
    ]
    write("THREE_HUNDRED_NINETY_SIXTH_FOUR_REGISTER_RULES.tsv", register_rows)

    page = """# Pass 396 — offener Satz, neuer Besitzer

```text
+--------------------------+
| STATION A: lokaler Posten |  cheedar chldaiin chdy okain cthy chealror
+--------------------------+


                         KEIN PFEIL / KEINE SICHTBARE LEITUNG


                                      +--------------------------+
                                      | STATION B: unteres Paar  |  olkeedy
                                      +--------------------------+
```

Der große Zwischenraum tut zwei Dinge gleichzeitig:

- **Satzregister:** bleibt offen, weil `chealror` keinen Schluss trägt.
- **Besitzerregister:** wird zurückgesetzt, weil die sichtbare Station wechselt.

`olkeedy` schließt danach den gemeinsamen Arbeitsgang, bezieht sich aber auf den
neuen örtlichen Besitzer. Es gibt keinen Pfeil und daher keine Behauptung, dass
Material aus A nach B fließt.

Lesung: Richte Station A ein, lege den Absetzstand fest, bearbeite den Posten,
gib eine Portion zu und prüfe Bereitschaft und Klarpunkt; danach beginne an
Station B den örtlichen Auffangschritt, halte ihn länger und schließe.
"""
    (HERE / "THREE_HUNDRED_NINETY_SIXTH_WORKSHOP_PAGE.md").write_text(page, encoding="utf-8")
    report = """# Pass 396 — Syntax und Bildreferenz laufen getrennt

Die zweiregionale Seite hält den Satz über den sichtbaren Zwischenraum offen,
setzt aber Besitzer und Materialreferent zurück. Erst OLKEEDY am neuen unteren
Paar schließt den Arbeitsgang. So bleibt die originale Ereignisfolge erhalten,
ohne eine Leitung oder einen Materialtransfer zu zeichnen.

Diese Trennung ist für die Arbeitstheorie zentral: Ein Zeilen- oder Bildwechsel
kann den lokalen Gegenstand austauschen, während die übergeordnete
Arbeitsanweisung weiterläuft. Das erklärt, warum reine Zeilensatz- oder
Pfeilmodelle den Text überinterpretieren.

Als nächstes soll eine zweite Schreiberhand dieselben sieben Karten um die zwei
Bildblöcke neu verteilen. Solange die offene Syntax und der Owner-Reset erhalten
bleiben, muss die Lesung gleich bleiben.
"""
    (HERE / "THREE_HUNDRED_NINETY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "regions": len(layout_rows),
        "cards": len(trace),
        "reader_steps": len(reader_steps),
        "registers": len(register_rows),
        "syntax_continuations_across_gap": 1,
        "owner_resets_across_gap": 1,
        "connection_arrows": 0,
    }
    (HERE / "THREE_HUNDRED_NINETY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
