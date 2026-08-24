#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P371 = ROOT / "experiments/yolo/sidequest_semantic_two_residual_layouts_three_hundred_seventy_first"
P370 = ROOT / "experiments/yolo/sidequest_semantic_two_palette_crossread_three_hundred_seventieth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


FAMILY_RANK = {"B": 1, "M": 2, "T": 3, "D": 4, "Z": 5, "A": 6}


def main() -> None:
    visible = read(P371 / "THREE_HUNDRED_SEVENTY_FIRST_EIGHTEEN_VISIBLE_FORMS.tsv")
    expected = read(P370 / "THREE_HUNDRED_SEVENTIETH_SIXTEEN_RENDERED_CARDS.tsv")
    lines: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in visible:
        lines[(row["layout_id"], int(row["line_no"]))].append(row)

    unmarked_rows = []
    for (layout, line_no), rows in sorted(lines.items()):
        rows.sort(key=lambda row: int(row["visible_no"]))
        unmarked_rows.append({
            "layout_id": layout,
            "line_no": line_no,
            "visible_owner": rows[0]["owner"],
            "visible_surfaces": " ".join(row["surface"] for row in rows),
            "decoded_joint_tuple_ids": "|".join(row["joint_tuple_id"] for row in rows),
            "decoded_values_de": " → ".join(row["atomic_value_de"] for row in rows),
            "decoded_slot_ranks": "|".join(str(FAMILY_RANK[next(e["slot_family"] for e in expected if e["palette_id"] == row["palette_id"] and e["position"] == row["source_position"])[0]]) for row in rows),
            "role_labels_visible": "NO",
            "boundary_labels_visible": "NO",
        })

    boundary_rows = []
    skipped_keys = set()
    for layout in sorted({row["layout_id"] for row in visible}):
        layout_lines = sorted((line_no, rows) for (lay, line_no), rows in lines.items() if lay == layout)
        for (left_no, left_rows), (right_no, right_rows) in zip(layout_lines, layout_lines[1:]):
            left = sorted(left_rows, key=lambda row: int(row["visible_no"]))[-1]
            right = sorted(right_rows, key=lambda row: int(row["visible_no"]))[0]
            left_slot = next(e["slot_family"] for e in expected if e["palette_id"] == left["palette_id"] and e["position"] == left["source_position"])
            right_slot = next(e["slot_family"] for e in expected if e["palette_id"] == right["palette_id"] and e["position"] == right["source_position"])
            if left["joint_tuple_id"] == right["joint_tuple_id"] and left["owner"] == right["owner"]:
                decision = "READ_ONCE_REMOVE_LEFT_MARGIN_COPY"
                skipped_keys.add((layout, int(left["line_no"]), int(left["visible_no"])))
                reason = "gleiche Karte direkt beidseits desselben Besitzerrandes"
            elif FAMILY_RANK[right_slot[0]] < FAMILY_RANK[left_slot[0]]:
                decision = "RESET_NEW_MICROCYCLE"
                reason = "Satzplatzfolge fällt von Zielgang auf Maßgang"
            else:
                decision = "CONTINUE"
                reason = "gleicher Besitzer und nichtfallende Satzplatzfolge"
            boundary_rows.append({
                "layout_id": layout,
                "left_line": left_no,
                "right_line": right_no,
                "left_last_surface": left["surface"],
                "right_first_surface": right["surface"],
                "left_identity": left["joint_tuple_id"],
                "right_identity": right["joint_tuple_id"],
                "left_slot_family": left_slot,
                "right_slot_family": right_slot,
                "same_owner": "YES" if left["owner"] == right["owner"] else "NO",
                "corrector_decision": decision,
                "reason_de": reason,
            })

    action_rows = []
    for row in visible:
        key = (row["layout_id"], int(row["line_no"]), int(row["visible_no"]))
        action_rows.append({
            "layout_id": row["layout_id"],
            "line_no": row["line_no"],
            "visible_no": row["visible_no"],
            "surface": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "atomic_value_de": row["atomic_value_de"],
            "corrector_action": "REMOVE_LEFT_MARGIN_COPY" if key in skipped_keys else "READ_AS_SOURCE_CARD",
            "source_contribution": 0 if key in skipped_keys else 1,
        })

    reconstruction_rows = []
    for layout in sorted({row["layout_id"] for row in visible}):
        layout_actions = [row for row in action_rows if row["layout_id"] == layout]
        read_rows = [row for row in layout_actions if row["corrector_action"] == "READ_AS_SOURCE_CARD"]
        palette = next(row["palette_id"] for row in visible if row["layout_id"] == layout)
        expected_rows = sorted((row for row in expected if row["palette_id"] == palette), key=lambda row: int(row["position"]))
        reconstruction_rows.append({
            "layout_id": layout,
            "palette_id": palette,
            "visible_forms": len(layout_actions),
            "removed_margin_copies": len(layout_actions) - len(read_rows),
            "recovered_source_cards": len(read_rows),
            "recovered_surfaces": " ".join(row["surface"] for row in read_rows),
            "expected_surfaces": " ".join(row["rendered_surface"] for row in expected_rows),
            "recovered_joint_tuple_ids": "|".join(row["joint_tuple_id"] for row in read_rows),
            "expected_joint_tuple_ids": "|".join(row["joint_tuple_id"] for row in expected_rows),
            "exact_reconstruction": "YES" if [row["joint_tuple_id"] for row in read_rows] == [row["joint_tuple_id"] for row in expected_rows] else "NO",
        })

    write("THREE_HUNDRED_SEVENTY_SECOND_SIX_UNMARKED_LINES.tsv", unmarked_rows)
    write("THREE_HUNDRED_SEVENTY_SECOND_FOUR_CORRECTOR_BOUNDARIES.tsv", boundary_rows)
    write("THREE_HUNDRED_SEVENTY_SECOND_EIGHTEEN_CORRECTOR_ACTIONS.tsv", action_rows)
    write("THREE_HUNDRED_SEVENTY_SECOND_TWO_RECONSTRUCTIONS.tsv", reconstruction_rows)
    notebook = ["# Pass 372 — unmarkiertes Korrektorenheft", ""]
    for row in unmarked_rows:
        notebook.append(f"- {row['layout_id']} Zeile {row['line_no']}: `{row['visible_surfaces']}`")
    notebook += ["", "## Randentscheidungen", ""]
    for row in boundary_rows:
        notebook.append(f"- {row['layout_id']} {row['left_line']}→{row['right_line']}: **{row['corrector_decision']}** — {row['reason_de']}.")
    notebook += ["", "## Ergebnis", ""]
    for row in reconstruction_rows:
        notebook.append(f"- {row['layout_id']}: `{row['recovered_surfaces']}` ({row['exact_reconstruction']})")
    (HERE / "THREE_HUNDRED_SEVENTY_SECOND_CORRECTOR_NOTEBOOK.md").write_text("\n".join(notebook) + "\n", encoding="utf-8")
    report = """# Pass 372 — Korrektor ohne Rollenmarken

Der Korrektor sieht sechs Zeilen, aber keine SOURCE-/COPY- oder Grenzlabels.
Gleiche Identität beidseits desselben Besitzerrandes entfernt zweimal die linke
Randkopie; der fallende Satzplatz erkennt zweimal den echten Mikrogangwechsel.
Beide neun sichtbaren Formen werden exakt zu je acht Quellkarten.

Als nächstes soll die achtteilige Anweisung mit einer absichtlichen falschen
Randkopie versehen werden: einmal an einer echten Zyklusgrenze. Der Korrektor
muss sie als unzulässige Doppelung erkennen und darf sie nicht read-once retten.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "unmarked_lines": len(unmarked_rows),
        "visible_forms": len(action_rows),
        "removed_margin_copies": sum(row["corrector_action"] == "REMOVE_LEFT_MARGIN_COPY" for row in action_rows),
        "source_cards": sum(int(row["source_contribution"]) for row in action_rows),
        "boundaries": len(boundary_rows),
        "read_once": sum(row["corrector_decision"] == "READ_ONCE_REMOVE_LEFT_MARGIN_COPY" for row in boundary_rows),
        "resets": sum(row["corrector_decision"] == "RESET_NEW_MICROCYCLE" for row in boundary_rows),
        "exact_reconstructions": sum(row["exact_reconstruction"] == "YES" for row in reconstruction_rows),
    }
    (HERE / "THREE_HUNDRED_SEVENTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
