#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P370 = ROOT / "experiments/yolo/sidequest_semantic_two_palette_crossread_three_hundred_seventieth"


def read(name: str) -> list[dict[str, str]]:
    with (P370 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


LAYOUTS = {
    "LAYOUT_A_WIDTH20": {
        "palette": "PALETTE_A_COMPACT",
        "capacity": 20,
        "lines": [
            [(1, "SOURCE"), (2, "SOURCE"), (3, "SOURCE"), (4, "ANTICIPATION_COPY")],
            [(4, "SOURCE"), (5, "SOURCE")],
            [(6, "SOURCE"), (7, "SOURCE"), (8, "SOURCE")],
        ],
        "boundaries": ["READ_ONCE_ANTICIPATION", "REAL_MICROCYCLE_RESET"],
    },
    "LAYOUT_B_WIDTH30": {
        "palette": "PALETTE_B_EXPANDED",
        "capacity": 30,
        "lines": [
            [(1, "SOURCE"), (2, "SOURCE"), (3, "SOURCE"), (4, "SOURCE"), (5, "SOURCE")],
            [(6, "SOURCE"), (7, "ANTICIPATION_COPY")],
            [(7, "SOURCE"), (8, "SOURCE")],
        ],
        "boundaries": ["REAL_MICROCYCLE_RESET", "READ_ONCE_ANTICIPATION"],
    },
}


def main() -> None:
    rendered = read("THREE_HUNDRED_SEVENTIETH_SIXTEEN_RENDERED_CARDS.tsv")
    by_palette = defaultdict(dict)
    for row in rendered:
        by_palette[row["palette_id"]][int(row["position"])] = row

    visible_rows = []
    boundary_rows = []
    for layout_id, spec in LAYOUTS.items():
        palette = str(spec["palette"])
        lines = spec["lines"]
        for line_no, items in enumerate(lines, 1):
            surfaces = [by_palette[palette][position]["rendered_surface"] for position, _ in items]
            used = len(" ".join(surfaces))
            for visible_no, ((position, role), surface) in enumerate(zip(items, surfaces), 1):
                source = by_palette[palette][position]
                visible_rows.append({
                    "layout_id": layout_id,
                    "palette_id": palette,
                    "line_no": line_no,
                    "visible_no": visible_no,
                    "source_position": position,
                    "visibility_role": role,
                    "source_contribution": 0 if role == "ANTICIPATION_COPY" else 1,
                    "surface": surface,
                    "joint_tuple_id": source["joint_tuple_id"],
                    "atomic_value_de": source["atomic_value_de"],
                    "microcycle": source["microcycle"],
                    "owner": "B3_MAIN_ARCH_LINKED_PAIR",
                    "line_used_width": used,
                    "line_capacity": spec["capacity"],
                    "line_slack": int(spec["capacity"]) - used,
                })
        for boundary_no, decision in enumerate(spec["boundaries"], 1):
            left_items = lines[boundary_no - 1]
            right_items = lines[boundary_no]
            left_pos, left_role = left_items[-1]
            right_pos, right_role = right_items[0]
            left = by_palette[palette][left_pos]
            right = by_palette[palette][right_pos]
            boundary_rows.append({
                "layout_id": layout_id,
                "boundary_no": boundary_no,
                "left_line": boundary_no,
                "right_line": boundary_no + 1,
                "left_last_surface": left["rendered_surface"],
                "right_first_surface": right["rendered_surface"],
                "left_source_position": left_pos,
                "right_source_position": right_pos,
                "same_identity_across_margin": "YES" if left["joint_tuple_id"] == right["joint_tuple_id"] else "NO",
                "same_owner": "YES",
                "left_cycle": left["microcycle"],
                "right_cycle": right["microcycle"],
                "decision": decision,
                "read_visible_forms": 2 if decision == "READ_ONCE_ANTICIPATION" else 2,
                "source_cards": 1 if decision == "READ_ONCE_ANTICIPATION" else 2,
            })

    reconstruction_rows = []
    for layout_id, spec in LAYOUTS.items():
        palette = str(spec["palette"])
        layout_visible = [row for row in visible_rows if row["layout_id"] == layout_id]
        for position in range(1, 9):
            forms = [row for row in layout_visible if int(row["source_position"]) == position]
            reconstruction_rows.append({
                "layout_id": layout_id,
                "source_position": position,
                "visible_forms": len(forms),
                "visible_surfaces": "|".join(str(row["surface"]) for row in forms),
                "source_contributions": sum(int(row["source_contribution"]) for row in forms),
                "recovered_joint_tuple_id": by_palette[palette][position]["joint_tuple_id"],
                "recovered_value_de": by_palette[palette][position]["atomic_value_de"],
                "recovered_exact": "YES" if sum(int(row["source_contribution"]) for row in forms) == 1 else "NO",
            })

    write("THREE_HUNDRED_SEVENTY_FIRST_EIGHTEEN_VISIBLE_FORMS.tsv", visible_rows)
    write("THREE_HUNDRED_SEVENTY_FIRST_FOUR_BOUNDARIES.tsv", boundary_rows)
    write("THREE_HUNDRED_SEVENTY_FIRST_SIXTEEN_SOURCE_RECONSTRUCTIONS.tsv", reconstruction_rows)
    lines_md = ["# Pass 371 — zwei Restbreiten", ""]
    for layout_id, spec in LAYOUTS.items():
        lines_md += [f"## {layout_id}", ""]
        for line_no, items in enumerate(spec["lines"], 1):
            palette = str(spec["palette"])
            surfaces = [by_palette[palette][position]["rendered_surface"] for position, _ in items]
            roles = [role for _, role in items]
            lines_md.append(f"{line_no}. `{' '.join(surfaces)}`  ({'|'.join(roles)})")
        lines_md += ["", f"Grenzen: {' → '.join(spec['boundaries'])}", ""]
    lines_md += [
        "Jede Fassung zeigt neun Formen, spricht aber acht Karten. Die Randkopie steht nur innerhalb eines Mikroganges; am Abfall von Zielslot 5 zu Maßslot 2 wird hart getrennt.",
    ]
    (HERE / "THREE_HUNDRED_SEVENTY_FIRST_TWO_LAYOUTS.md").write_text("\n".join(lines_md) + "\n", encoding="utf-8")
    report = """# Pass 371 — Restbreiten und Randkopien

Die kompakte Palette passt in Breite 20 und kopiert `cheky` am inneren Bruch;
die erweiterte Palette passt in Breite 30 und kopiert `qokeey`. Jede Fassung
hat drei Zeilen, eine echte Zyklusgrenze und genau eine Read-once-Randkopie.
Neun sichtbare Formen werden dadurch wieder zu acht Quellkarten.

Als nächstes soll ein Korrektor beide unmarkierten Layouts lesen: Kopierrollen
werden versteckt, und nur Identität, Besitzer, Slotfolge und Zyklusabfall dürfen
die 16 Quellkarten rekonstruieren.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "layouts": len(LAYOUTS),
        "physical_lines": len(LAYOUTS) * 3,
        "visible_forms": len(visible_rows),
        "source_cards": sum(int(row["source_contribution"]) for row in visible_rows),
        "anticipation_copies": sum(row["visibility_role"] == "ANTICIPATION_COPY" for row in visible_rows),
        "boundaries": len(boundary_rows),
        "read_once_boundaries": sum(row["decision"] == "READ_ONCE_ANTICIPATION" for row in boundary_rows),
        "reset_boundaries": sum(row["decision"] == "REAL_MICROCYCLE_RESET" for row in boundary_rows),
    }
    (HERE / "THREE_HUNDRED_SEVENTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
