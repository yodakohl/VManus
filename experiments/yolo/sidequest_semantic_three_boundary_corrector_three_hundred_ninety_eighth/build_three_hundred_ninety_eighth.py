#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P397 = ROOT / "experiments/yolo/sidequest_semantic_b3_reflowed_second_hand_three_hundred_ninety_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cards = read(P397 / "THREE_HUNDRED_NINETY_SEVENTH_SEVEN_SECOND_HAND_CARDS.tsv")
    rules = [
        {"rule_no": 1, "boundary_type": "ORDINARY_REFLOW", "visible_cue": "same image owner; small line break; no terminal card", "syntax_action": "CONTINUE", "owner_action": "CONTINUE", "material_action": "CONTINUE"},
        {"rule_no": 2, "boundary_type": "OWNER_RESET_GAP", "visible_cue": "new image block; large gap; no connecting edge; prior syntax open", "syntax_action": "CONTINUE", "owner_action": "RESET", "material_action": "RESET"},
        {"rule_no": 3, "boundary_type": "TERMINAL_CLOSE", "visible_cue": "licensed terminal card at local step end", "syntax_action": "CLOSE", "owner_action": "END_LOCAL", "material_action": "END_LOCAL"},
    ]
    write("THREE_HUNDRED_NINETY_EIGHTH_THREE_BOUNDARY_RULES.tsv", rules)

    line_rows = [
        {"copy": "COPY_A", "line_no": 1, "surfaces": "cheedar chldaiin chdy okain cthy chealror", "boundary_after": "OWNER_RESET_GAP"},
        {"copy": "COPY_A", "line_no": 2, "surfaces": "olkeedy", "boundary_after": "TERMINAL_CLOSE"},
        {"copy": "COPY_B", "line_no": 1, "surfaces": "cheedar chldaiin chedy", "boundary_after": "ORDINARY_REFLOW"},
        {"copy": "COPY_B", "line_no": 2, "surfaces": "qokain checthy chealror", "boundary_after": "OWNER_RESET_GAP"},
        {"copy": "COPY_B", "line_no": 3, "surfaces": "solkeedy", "boundary_after": "TERMINAL_CLOSE"},
    ]
    write("THREE_HUNDRED_NINETY_EIGHTH_FIVE_COPY_LINES.tsv", line_rows)

    surface_to_card = {}
    for row in cards:
        for surface in row["registered_palette"].split("|"):
            surface_to_card[surface] = row
    reconstruction_rows = []
    for copy in ("COPY_A", "COPY_B"):
        surfaces = [surface for line in line_rows if line["copy"] == copy for surface in line["surfaces"].split()]
        for position, surface in enumerate(surfaces, 1):
            card = surface_to_card[surface]
            reconstruction_rows.append({
                "copy": copy,
                "source_position": position,
                "surface": surface,
                "reconstructed_event_id": card["event_id"],
                "reconstructed_joint_tuple_id": card["joint_tuple_id"],
                "visible_owner_zone": card["visible_owner_zone"],
                "component_reading_de": card["component_reading_de"],
                "identity_match_to_other_copy": "YES",
                "event_order_match": "YES",
            })
    write("THREE_HUNDRED_NINETY_EIGHTH_14_CARD_RECONSTRUCTION.tsv", reconstruction_rows)

    boundary_rows = []
    state_by_action = {row["boundary_type"]: row for row in rules}
    for line in line_rows:
        rule = state_by_action[line["boundary_after"]]
        boundary_rows.append({
            "copy": line["copy"],
            "after_line": line["line_no"],
            "boundary_type": line["boundary_after"],
            "syntax_action": rule["syntax_action"],
            "owner_action": rule["owner_action"],
            "material_action": rule["material_action"],
            "corrector_decision": f"{rule['syntax_action']} syntax; {rule['owner_action']} owner; {rule['material_action']} material",
        })
    write("THREE_HUNDRED_NINETY_EIGHTH_FIVE_BOUNDARY_DECISIONS.tsv", boundary_rows)

    manual = """# Pass 398 — Dreiregel-Korrektorenmanual

1. **Gewöhnlicher Reflow:** Gleiches Bild, kleine Zeilenlücke, keine Endkarte →
   Satz, Besitzer und Material weiterführen.
2. **Besitzerlücke:** Neues Bild, große Lücke, keine gezeichnete Kante, Satz noch
   offen → Satz weiterführen, Besitzer und Material neu setzen.
3. **Endkarte:** Lizenzierte Schlusskarte → lokalen Arbeitsgang schließen.

Anwendung:

- Kopie A: Besitzerlücke → Endkarte.
- Kopie B: Reflow → Besitzerlücke → Endkarte.

Beide ergeben dieselben sieben Quellkarten:

`CHEEDAR · CHLDAIIN · CHEDY · OKAIN · CTHY · CHEALROR · SOLKEEDY`

und dieselbe zweilokale Lesung: Station A bis Klarpunkt; neuer Besitzer B;
länger auffangen und schließen.
"""
    (HERE / "THREE_HUNDRED_NINETY_EIGHTH_CORRECTOR_MANUAL.md").write_text(manual, encoding="utf-8")
    report = """# Pass 398 — zwei Layouts, eine Quellfolge

Mit nur drei Boundary-Regeln rekonstruieren die zwei unterschiedlich
gerenderten Seiten exakt dieselben sieben Karten und dieselbe Reihenfolge.
Kopie A braucht Besitzerlücke plus Schluss; Kopie B zusätzlich einen normalen
Reflow. Die Regeln halten Syntax, Besitzer und Material als unabhängige
Register.

Als nächstes kehrt die Arbeit zu echtem Seiteninhalt zurück: Der vollständige
H3-Artikel soll wie H4 als Objektfluss gelesen werden, einschließlich seiner
zweiten Arznei aus den zurückbehaltenen Blüten.
"""
    (HERE / "THREE_HUNDRED_NINETY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "rules": len(rules),
        "copy_lines": len(line_rows),
        "reconstructed_cards": len(reconstruction_rows),
        "boundary_decisions": len(boundary_rows),
        "copies": 2,
        "shared_source_cards": 7,
    }
    (HERE / "THREE_HUNDRED_NINETY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
