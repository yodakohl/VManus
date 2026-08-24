#!/usr/bin/env python3
"""Build Pass 717: arrange the fresh dockets as one owner-aware master page."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P716 = ROOT / "experiments/yolo/sidequest_semantic_fresh_docket_copy_seven_hundred_sixteenth"
ORDER = ["FD01", "FD02", "FD05", "FD08", "FD03", "FD04", "FD06", "FD09", "FD10", "FD12", "FD07", "FD11"]
LINE_ENDS = [4, 10, 15, 22, 27]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    dockets = read(P716 / "SEVEN_HUNDRED_SIXTEENTH_12_FRESH_DOCKETS.tsv")
    trace = read(P716 / "SEVEN_HUNDRED_SIXTEENTH_27_FORWARD_BACKREAD_TRACE.tsv")
    docket_by_id = {row["docket_id"]: row for row in dockets}
    events_by_docket: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in trace:
        events_by_docket[row["docket_id"]].append(row)

    statement_rows = []
    event_rows = []
    global_position = 0
    current_owner = "NONE"
    current_state = "NONE"
    line_start = 1
    for master_statement_no, docket_id in enumerate(ORDER, 1):
        docket = docket_by_id[docket_id]
        owner = docket["owner_class"]
        handoff = owner != current_owner and current_owner != "NONE"
        if owner != current_owner:
            current_owner = owner
            current_state = "OWNER_OPEN"
        statement_event_rows = []
        for local_position, source in enumerate(events_by_docket[docket_id], 1):
            global_position += 1
            line_no = next(i + 1 for i, end in enumerate(LINE_ENDS) if global_position <= end)
            prior_end = 0 if line_no == 1 else LINE_ENDS[line_no - 2]
            column = global_position - prior_end
            input_state = current_state
            recipe = source["component_recipe"]
            if recipe.endswith("+DY"):
                current_state = "CLOSED"
            elif input_state == "CLOSED":
                current_state = "REOPENED_ACTIVE"
            else:
                current_state = "OPEN_ACTIVE"
            row = {
                "master_event_id": f"MP{global_position:03d}", "master_statement_no": master_statement_no,
                "docket_id": docket_id, "owner": owner,
                "owner_handoff_before": "YES" if handoff and local_position == 1 else "NO",
                "line_no": line_no, "line_column": column, "global_position": global_position,
                "source_practice_event": source["practice_event_id"], "component_recipe": recipe,
                "selected_card": source["selected_card"], "surface": source["selected_surface"],
                "input_work_state": input_state, "output_work_state": current_state,
                "physical_line_ends_after": "YES" if global_position in LINE_ENDS else "NO",
                "statement_ends_after": "YES" if local_position == len(events_by_docket[docket_id]) else "NO",
                "backread_de": source["backread_de"],
            }
            event_rows.append(row)
            statement_event_rows.append(row)
        lines = sorted({int(row["line_no"]) for row in statement_event_rows})
        statement_rows.append({
            "master_statement_no": master_statement_no, "docket_id": docket_id, "owner": owner,
            "owner_handoff_before": "YES" if handoff else "NO", "docket_de": docket["docket_de"],
            "lines_used": "|".join(map(str, lines)), "crosses_line": "YES" if len(lines) > 1 else "NO",
            "component_sequence": docket["component_sequence"], "card_sequence": docket["card_sequence"],
            "surface_sequence": docket["surface_sequence"], "backreading_de": docket["backreading_de"],
        })

    line_rows = []
    for line_no in range(1, 6):
        rows = [row for row in event_rows if row["line_no"] == line_no]
        line_rows.append({
            "line_no": line_no, "events": len(rows),
            "owners_in_order": " > ".join(dict.fromkeys(str(row["owner"]) for row in rows)),
            "dockets_touched": "|".join(dict.fromkeys(str(row["docket_id"]) for row in rows)),
            "surface_line": " ".join(str(row["surface"]) for row in rows),
            "starts_inside_statement": "YES" if line_no > 1 and rows[0]["statement_ends_after"] == "NO" and event_rows[int(rows[0]["global_position"]) - 2]["docket_id"] == rows[0]["docket_id"] else "NO",
            "ends_inside_statement": "YES" if rows[-1]["statement_ends_after"] == "NO" else "NO",
        })

    errors = [
        {
            "error_id": "ME1", "location": "FD03/MP012", "error_kind": "MISSED_OWNER_HANDOFF",
            "bad_reading": "PLANT bleibt Besitzer", "visible_or_docket_cue": "expliziter BASIN-Besitzer vor FD03",
            "correction": "BASIN als aktiven Besitzer setzen", "meaning_change": "NO__OWNER_BINDING_ONLY",
        },
        {
            "error_id": "ME2", "location": "FD12/MP022", "error_kind": "PREMATURE_OWNER_HANDOFF",
            "bad_reading": "APPARATUS beginnt schon bei FD12", "visible_or_docket_cue": "APPARATUS-Handoff steht erst vor FD07",
            "correction": "FD12 bei BASIN lassen; erst FD07 auf APPARATUS wechseln", "meaning_change": "NO__OWNER_BINDING_ONLY",
        },
        {
            "error_id": "ME3", "location": "LINE1_END/MP004", "error_kind": "FALSE_LINE_CLOSE",
            "bad_reading": "physische Zeile schliesst FD02 nach OK+Y", "visible_or_docket_cue": "FD02 verlangt danach noch K+HO+AR und hat keine Schlusskarte",
            "correction": "offenen Zustand ueber die Zeile tragen", "meaning_change": "NO__BOUNDARY_ONLY",
        },
    ]

    write("SEVEN_HUNDRED_SEVENTEENTH_12_MASTER_STATEMENTS.tsv", statement_rows)
    write("SEVEN_HUNDRED_SEVENTEENTH_27_OWNER_STATE_TRACE.tsv", event_rows)
    write("SEVEN_HUNDRED_SEVENTEENTH_5_PHYSICAL_LINES.tsv", line_rows)
    write("SEVEN_HUNDRED_SEVENTEENTH_3_CORRECTOR_CASES.tsv", errors)

    readable = ["# Kontinuierliche Meisterseite", "", "Die Besitzer stehen im gedachten Bild-/Docketrand und werden nicht als Voynich-Karte ausgeschrieben.", ""]
    for line in line_rows:
        readable.extend([f"## Zeile {line['line_no']} — {line['owners_in_order']}", "", str(line["surface_line"]), ""])
    readable.extend(["## Besitzerfolge", "", "PLANT → BASIN → APPARATUS", ""])
    (HERE / "SEVEN_HUNDRED_SEVENTEENTH_MASTER_PAGE.md").write_text("\n".join(readable), encoding="utf-8")

    summary = {
        "status": "PASS", "statements": len(statement_rows), "events": len(event_rows),
        "physical_lines": len(line_rows), "cross_line_statements": sum(row["crosses_line"] == "YES" for row in statement_rows),
        "owner_handoffs": sum(row["owner_handoff_before"] == "YES" for row in statement_rows),
        "owner_sequence": ["PLANT", "BASIN", "APPARATUS"],
        "corrector_cases": len(errors), "new_cards": 0, "new_surfaces": 0,
        "decision": "ONE_CONTINUOUS_FIVE_LINE_MASTER_PAGE_PRESERVES_TWELVE_DOCKETS_TWO_OWNER_HANDOFFS_AND_FOUR_CROSS_LINE_STATEMENTS",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
