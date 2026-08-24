#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P358 = ROOT / "experiments/yolo/sidequest_semantic_seven_page_continuous_reading_three_hundred_fifty_eighth"


def read(name: str) -> list[dict[str, str]]:
    with (P358 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RANK = {
    "S1_BEZUG_FOLGE": 1,
    "S2_MATERIAL_MASS": 2,
    "S3_PROZESS_TRANSFER": 3,
    "S4_DAUER_ZUSTAND": 4,
    "S5_ZIEL_ANWENDUNG": 5,
    "S6_BEREIT_ABSCHLUSS": 6,
}


def main() -> None:
    events = read("THREE_HUNDRED_FIFTY_EIGHTH_381_VISIBLE_380_SOURCE_EDITION.tsv")
    transitions = read("THREE_HUNDRED_FIFTY_EIGHTH_FORTY_SIX_LINE_TRANSITIONS.tsv")
    event_index = {row["event_id"]: index for index, row in enumerate(events)}
    rows = []
    for transition in transitions:
        left_index = event_index[transition["left_event_id"]]
        predecessor = events[left_index - 1] if left_index > 0 and events[left_index - 1]["locus"] == transition["left_locus"] else None
        pred_slot = predecessor["slot_code"] if predecessor else "NONE"
        predecessor_drop = bool(predecessor) and RANK[transition["left_slot"]] < RANK[pred_slot]
        identical_margin = transition["same_exact_card"] == "YES" and transition["same_owner"] == "YES"
        if identical_margin and predecessor_drop:
            strict = "REJECT_AS_RESET_DUPLICATE"
            strict_matches_selected = "NO" if transition["decision"] == "READ_ONCE_CARRY" else "YES"
        elif identical_margin:
            strict = "READ_ONCE_CARRY"
            strict_matches_selected = "YES" if transition["decision"] == "READ_ONCE_CARRY" else "NO"
        else:
            strict = transition["decision"]
            strict_matches_selected = "YES"
        rows.append({
            "transition_no": transition["transition_no"],
            "record_unit_id": transition["record_unit_id"],
            "page": transition["page"],
            "left_event_id": transition["left_event_id"],
            "left_surface": transition["left_surface"],
            "predecessor_event_id": predecessor["event_id"] if predecessor else "NONE",
            "predecessor_surface": predecessor["surface"] if predecessor else "NONE",
            "predecessor_slot": pred_slot,
            "left_slot": transition["left_slot"],
            "predecessor_to_left_slot_drop": "YES" if predecessor_drop else "NO",
            "right_event_id": transition["right_event_id"],
            "right_surface": transition["right_surface"],
            "same_exact_card": transition["same_exact_card"],
            "same_owner": transition["same_owner"],
            "same_statement": transition["same_statement"],
            "same_microcycle_across_margin": transition["same_microcycle"],
            "selected_pass358_decision": transition["decision"],
            "strict_predecessor_rule_decision": strict,
            "strict_rule_matches_selected": strict_matches_selected,
            "final_pass374_decision": transition["decision"],
            "pass373_rule_status": "COUNTEREXAMPLE_WITHDRAW_RULE" if strict_matches_selected == "NO" else "NO_EFFECT",
        })
    write("THREE_HUNDRED_SEVENTY_FOURTH_46_TRANSITION_REAUDIT.tsv", rows)
    conflicts = [row for row in rows if row["strict_rule_matches_selected"] == "NO"]
    selected_counts = Counter(row["selected_pass358_decision"] for row in rows)
    correction_rows = [
        {
            "pass": "373",
            "old_claim": "Ein Slotabfall vor einer identischen Randkarte macht die Doppelung unzulässig.",
            "real_counterexample": "E179 chckhy S3 -> E180/E181 qokaiin S2; neuer Mikrogang wird am alten Rand vorweggenommen.",
            "new_status": "WITHDRAWN",
            "replacement_rule": "Gleiche exakte Karte an altem Rand und neuem Zeilenanfang unter demselben Besitzer darf read-once sein, auch wenn sie einen neuen Mikrogang eröffnet.",
        },
        {
            "pass": "373_SYNTHETIC_AIIIN",
            "old_claim": "Das linke aiin ist als Fehler erkennbar.",
            "real_counterexample": "Strukturell isomorph zu E180/E181; intern kein unterscheidendes Merkmal.",
            "new_status": "RECLASSIFIED_AS_POSSIBLE_NEW_CYCLE_ANTICIPATION",
            "replacement_rule": "Ohne zusätzliche sichtbare Markierung kann der Korrektor Fehler und erlaubte Antizipation nicht trennen.",
        },
    ]
    write("THREE_HUNDRED_SEVENTY_FOURTH_CORRECTIONS.tsv", correction_rows)
    report = f"""# Pass 374 — reale Zeilenübergänge korrigieren die neue Regel

Die Vorgängerregel aus Pass 373 scheitert genau am einzigen realen
Read-once-Fall. Vor E180 steht E179 `chckhy` im Transferslot; E180/E181
`qokaiin` steht im niedrigeren Maßslot und eröffnet einen neuen Mikrogang. Die
Karte wird trotzdem am alten Rand antizipiert und am neuen Anfang ausgeführt.

Darum wird "Slotabfall sperrt Randkopie" vollständig zurückgezogen. Die 46
realen Entscheidungen bleiben {selected_counts['CONTINUE_ACROSS_LINE']} Fortsetzungen,
{selected_counts['READ_ONCE_CARRY']} Read-once und
{selected_counts['REAL_CYCLE_OR_OWNER_RESET']} Resets. Der synthetische
`aiin | aiin`-Fall aus Pass 373 ist intern strukturgleich und darf nicht mehr als
erkennbarer Fehler bezeichnet werden.

Als nächstes braucht die Werkstatt eine positive sichtbare Konvention, wenn sie
Fehler von Antizipation unterscheiden will: etwa ein Randpunkt, kleinerer
Abstand oder eine feste marginale Stellung. Auf den realen sieben Seiten wird
nichts davon erfunden; die neue Markierung wird nur an der Übungszeile getestet.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "real_transitions": len(rows),
        "strict_predecessor_conflicts": len(conflicts),
        "conflict_transition_numbers": [row["transition_no"] for row in conflicts],
        "selected_decision_counts": dict(selected_counts),
        "pass373_predecessor_rule": "WITHDRAWN",
        "synthetic_aiin_case": "INTERNALLY_INDISTINGUISHABLE_FROM_ALLOWED_NEW_CYCLE_ANTICIPATION",
    }
    (HERE / "THREE_HUNDRED_SEVENTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
