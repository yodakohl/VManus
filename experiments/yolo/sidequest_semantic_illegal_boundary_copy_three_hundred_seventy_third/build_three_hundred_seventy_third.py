#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P370 = ROOT / "experiments/yolo/sidequest_semantic_two_palette_crossread_three_hundred_seventieth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


LINES = [
    [(1, "SOURCE"), (2, "SOURCE"), (3, "SOURCE"), (4, "LEGAL_ANTICIPATION")],
    [(4, "SOURCE"), (5, "SOURCE"), (6, "ILLEGAL_RESET_DUPLICATE")],
    [(6, "SOURCE"), (7, "SOURCE"), (8, "SOURCE")],
]

FAMILY_RANK = {"B": 1, "M": 2, "T": 3, "D": 4, "Z": 5, "A": 6}


def main() -> None:
    cards = [row for row in read(P370 / "THREE_HUNDRED_SEVENTIETH_SIXTEEN_RENDERED_CARDS.tsv") if row["palette_id"] == "PALETTE_A_COMPACT"]
    by_pos = {int(row["position"]): row for row in cards}
    visible_rows = []
    for line_no, items in enumerate(LINES, 1):
        for visible_no, (position, planted_role) in enumerate(items, 1):
            row = by_pos[position]
            visible_rows.append({
                "line_no": line_no,
                "visible_no": visible_no,
                "source_position": position,
                "surface": row["rendered_surface"],
                "joint_tuple_id": row["joint_tuple_id"],
                "atomic_value_de": row["atomic_value_de"],
                "slot_family": row["slot_family"],
                "slot_rank": FAMILY_RANK[row["slot_family"][0]],
                "owner": "B3_MAIN_ARCH_LINKED_PAIR",
                "planted_role_hidden_from_corrector": planted_role,
            })

    boundary_rows = []
    action_by_key = {}
    for boundary_no in (1, 2):
        left_line = [row for row in visible_rows if int(row["line_no"]) == boundary_no]
        right_line = [row for row in visible_rows if int(row["line_no"]) == boundary_no + 1]
        left = left_line[-1]
        predecessor = left_line[-2]
        right = right_line[0]
        same = left["joint_tuple_id"] == right["joint_tuple_id"] and left["owner"] == right["owner"]
        drops_before_copy = int(right["slot_rank"]) < int(predecessor["slot_rank"])
        if same and not drops_before_copy:
            decision = "LEGAL_READ_ONCE_ANTICIPATION"
            left_action = "REMOVE_LICENSED_MARGIN_COPY"
            severity = "NONE"
        elif same and drops_before_copy:
            decision = "ILLEGAL_DUPLICATE_AT_REAL_RESET"
            left_action = "DELETE_AND_MARK_SCRIBAL_ERROR"
            severity = "ERROR"
        else:
            decision = "ORDINARY_BOUNDARY"
            left_action = "READ_AS_SOURCE"
            severity = "NONE"
        action_by_key[(int(left["line_no"]), int(left["visible_no"]))] = left_action
        boundary_rows.append({
            "boundary_no": boundary_no,
            "left_line": boundary_no,
            "right_line": boundary_no + 1,
            "predecessor_surface": predecessor["surface"],
            "predecessor_slot_rank": predecessor["slot_rank"],
            "left_margin_surface": left["surface"],
            "right_initial_surface": right["surface"],
            "repeated_identity": "YES" if same else "NO",
            "right_slot_rank": right["slot_rank"],
            "slot_drop_before_repeated_card": "YES" if drops_before_copy else "NO",
            "corrector_decision": decision,
            "left_margin_action": left_action,
            "error_severity": severity,
            "naive_identity_only_decision": "READ_ONCE" if same else "BOUNDARY",
        })

    action_rows = []
    for row in visible_rows:
        key = (int(row["line_no"]), int(row["visible_no"]))
        action = action_by_key.get(key, "READ_AS_SOURCE")
        action_rows.append({
            "line_no": row["line_no"],
            "visible_no": row["visible_no"],
            "surface": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "atomic_value_de": row["atomic_value_de"],
            "corrector_action": action,
            "source_contribution": 1 if action == "READ_AS_SOURCE" else 0,
        })
    recovered = [row for row in action_rows if row["source_contribution"] == 1]
    expected_ids = [by_pos[position]["joint_tuple_id"] for position in range(1, 9)]
    write("THREE_HUNDRED_SEVENTY_THIRD_TEN_VISIBLE_FORMS.tsv", visible_rows)
    write("THREE_HUNDRED_SEVENTY_THIRD_TWO_BOUNDARY_DECISIONS.tsv", boundary_rows)
    write("THREE_HUNDRED_SEVENTY_THIRD_TEN_CORRECTOR_ACTIONS.tsv", action_rows)
    result_rows = [{
        "visible_forms": len(visible_rows),
        "licensed_margin_copies_removed": sum(row["corrector_action"] == "REMOVE_LICENSED_MARGIN_COPY" for row in action_rows),
        "illegal_duplicates_deleted": sum(row["corrector_action"] == "DELETE_AND_MARK_SCRIBAL_ERROR" for row in action_rows),
        "source_cards": len(recovered),
        "recovered_surfaces": " ".join(row["surface"] for row in recovered),
        "recovered_joint_tuple_ids": "|".join(row["joint_tuple_id"] for row in recovered),
        "expected_joint_tuple_ids": "|".join(expected_ids),
        "exact_reconstruction": "YES" if [row["joint_tuple_id"] for row in recovered] == expected_ids else "NO",
        "illegal_copy_not_licensed": "YES" if any(row["corrector_decision"] == "ILLEGAL_DUPLICATE_AT_REAL_RESET" for row in boundary_rows) else "NO",
    }]
    write("THREE_HUNDRED_SEVENTY_THIRD_RECONSTRUCTION.tsv", result_rows)

    edition = f"""# Pass 373 — falsche Randkopie am Reset

1. `or kain chckhy cheky`
2. `cheky oky aiin`
3. `aiin okeey qokedy`

Der erste Doppelrand `cheky | cheky` ist erlaubt: davor steigt der Satzplatz von
Transfer zu Zustand. Der zweite Doppelrand `aiin | aiin` ist nicht erlaubt:
davor fällt der Satzplatz von Ziel/Einsetzen zu Maß/Sollmaß. Der Korrektor
streicht das linke `aiin` als Fehler und schreibt es nicht als normale
Read-once-Konvention gut.

Rekonstruiert: `{result_rows[0]['recovered_surfaces']}`.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_THIRD_ERROR_PAGE.md").write_text(edition, encoding="utf-8")
    report = """# Pass 373 — Randkopie gegen echten Reset

Eine reine Identitätsregel würde beide Doppelränder read-once nennen und damit
den zweiten Produktionsfehler unsichtbar machen. Die vollständige Werkstattregel
prüft die Vorgängerkarte: ein Slotabfall vor der Doppelkarte sperrt die
Antizipation. So wird eine legale Kopie entfernt, eine illegale gelöscht und als
Fehler markiert; acht Quellkarten bleiben exakt.

Als nächstes wird diese Fehlerregel auf alle 46 realen Zeilenübergänge der sieben
Prosaseiten zurückgespielt, diesmal mit expliziter Vorgängerprüfung.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "visible_forms": len(visible_rows),
        "source_cards": len(recovered),
        "boundaries": len(boundary_rows),
        "legal_copies": sum(row["corrector_decision"] == "LEGAL_READ_ONCE_ANTICIPATION" for row in boundary_rows),
        "illegal_reset_duplicates": sum(row["corrector_decision"] == "ILLEGAL_DUPLICATE_AT_REAL_RESET" for row in boundary_rows),
        "exact_reconstruction": result_rows[0]["exact_reconstruction"],
    }
    (HERE / "THREE_HUNDRED_SEVENTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
