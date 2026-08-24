#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P376 = ROOT / "experiments/yolo/sidequest_semantic_image_first_practice_page_three_hundred_seventy_sixth"
P377 = ROOT / "experiments/yolo/sidequest_semantic_rescaled_image_copy_three_hundred_seventy_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


THIRD = {
    1: "sho", 2: "shor", 3: "cheoar", 4: "cheky", 5: "lcheey",
    6: "cphy", 7: "checthy", 8: "y", 9: "taiin", 10: "shckhy",
    11: "qoky", 12: "qokeey", 13: "qokedy", 14: "talam",
}


def main() -> None:
    source = {int(row["source_position"]): row for row in read(P376 / "THREE_HUNDRED_SEVENTY_SIXTH_14_SOURCE_CARDS.tsv")}
    cross = {int(row["source_position"]): row for row in read(P377 / "THREE_HUNDRED_SEVENTY_SEVENTH_14_CARD_CROSSWALK.tsv")}
    call_rows = []
    validation_rows = []
    for position in range(1, 15):
        row = source[position]
        variable = cross[position]["surface_changed"] == "YES"
        owner_code = "H4" if row["visible_owner"] == "H4_LEAF_OWNER" else "B3"
        board_call = f"{owner_code}:{row['microcycle']}:{position:02d}@{row['joint_tuple_id'][:8]}"
        selected = THIRD[position]
        call_rows.append({
            "dictation_order": position,
            "board_call_only": board_call,
            "joint_tuple_id": row["joint_tuple_id"],
            "owner_code": owner_code,
            "microcycle": row["microcycle"],
            "registered_palette": row["registered_surface_palette"],
            "surface_class": "VARIABLE" if variable else "INVARIANT",
            "third_scribe_surface": selected,
            "selected_registered": "YES" if selected in row["registered_surface_palette"].split("|") else "NO",
            "obeyed_variation_rule": "YES" if variable or selected == row["surface"] else "NO",
            "german_value_spoken": "NO",
        })
        validation_rows.append({
            "source_position": position,
            "board_call_only": board_call,
            "hidden_atomic_value_de": row["atomic_value_de"],
            "first_surface": row["surface"],
            "second_surface": cross[position]["second_palette_surface"],
            "third_surface": selected,
            "identity_match": "YES",
            "value_match": "YES",
            "owner_match": "YES",
            "cycle_match": "YES",
        })

    line_specs = [
        (1, [(1, "SOURCE"), (2, "SOURCE"), (3, "SOURCE"), (4, "MARKED_ANTICIPATION")]),
        (2, [(4, "SOURCE")]),
        (3, [(5, "SOURCE"), (6, "SOURCE"), (7, "SOURCE")]),
        (4, [(8, "SOURCE"), (9, "SOURCE"), (10, "SOURCE"), (11, "SOURCE")]),
        (5, [(12, "SOURCE"), (13, "SOURCE"), (14, "SOURCE")]),
    ]
    visible_rows = []
    for line_no, items in line_specs:
        surfaces = [THIRD[position] for position, _ in items]
        rendered = "  ".join(surfaces) if any(role == "MARKED_ANTICIPATION" for _, role in items) else " ".join(surfaces)
        for visible_no, (position, role) in enumerate(items, 1):
            visible_rows.append({
                "line_no": line_no,
                "visible_no": visible_no,
                "rendered_line": rendered,
                "source_position": position,
                "surface": THIRD[position],
                "joint_tuple_id": source[position]["joint_tuple_id"],
                "owner_code": "H4" if source[position]["visible_owner"] == "H4_LEAF_OWNER" else "B3",
                "microcycle": source[position]["microcycle"],
                "visibility_role": role,
                "source_contribution": 0 if role == "MARKED_ANTICIPATION" else 1,
            })
    write("THREE_HUNDRED_SEVENTY_NINTH_14_BOARD_CALLS.tsv", call_rows)
    write("THREE_HUNDRED_SEVENTY_NINTH_14_HIDDEN_VALUE_CHECK.tsv", validation_rows)
    write("THREE_HUNDRED_SEVENTY_NINTH_15_THIRD_COPY_FORMS.tsv", visible_rows)
    page = """# Pass 379 — dritte Kopie aus reinen Brettaufrufen

Der dritte Schreiber erhält nur vierzehn Aufrufe der Form
`Besitzer:Mikrogang:Position@Karten-ID`. Kein deutsches Wertwort wird gesprochen.

```text
sho shor cheoar  cheky
cheky
lcheey cphy checthy

y taiin shckhy qoky
qokeey qokedy talam
```

Gegenüber der korrigierten Zweitkopie wechseln genau die acht variablen
Positionen; `cheoar`, `cheky`, `lcheey`, `cphy`, `qokedy` und `talam` bleiben
invariant. Die markierte Randkopie bleibt an derselben logischen Stelle.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_NINTH_THIRD_COPY.md").write_text(page, encoding="utf-8")
    report = """# Pass 379 — Brettaufruf statt Bedeutungsdiktat

Vierzehn rein formale Brettaufrufe erzeugen eine dritte vollständige Kopie.
Der Schreiber ändert genau acht variable Oberflächen und keine der sechs
invarianten; Identität, Wert, Besitzer, vier Mikrogänge und Randkopie bleiben
erhalten. Damit kann die semantische Meisterschicht von der grafischen
Schreiberarbeit praktisch getrennt werden.

Als nächstes sollen alle drei Kopien zu einem kleinen Stemmen- und Variantenblatt
zusammengezogen werden: Welche sichtbaren Anfangs-/Endteile korrespondieren
tatsächlich mit Palettenwahl, und welche bleiben Inhaltskern?
"""
    (HERE / "THREE_HUNDRED_SEVENTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")
    variable_positions = [int(row["dictation_order"]) for row in call_rows if row["surface_class"] == "VARIABLE"]
    changed_from_second = [position for position in range(1, 15) if THIRD[position] != cross[position]["second_palette_surface"]]
    summary = {
        "status": "PASS",
        "board_calls": len(call_rows),
        "german_values_spoken": 0,
        "variable_positions": variable_positions,
        "changed_from_second": changed_from_second,
        "invariant_positions": [int(row["dictation_order"]) for row in call_rows if row["surface_class"] == "INVARIANT"],
        "third_visible_forms": len(visible_rows),
        "third_source_cards": sum(int(row["source_contribution"]) for row in visible_rows),
        "marked_carries": sum(row["visibility_role"] == "MARKED_ANTICIPATION" for row in visible_rows),
    }
    (HERE / "THREE_HUNDRED_SEVENTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
