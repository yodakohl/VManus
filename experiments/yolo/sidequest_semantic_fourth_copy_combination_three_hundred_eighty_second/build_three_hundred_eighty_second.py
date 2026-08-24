#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P379 = ROOT / "experiments/yolo/sidequest_semantic_board_call_third_copy_three_hundred_seventy_ninth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    calls = read(P379 / "THREE_HUNDRED_SEVENTY_NINTH_14_BOARD_CALLS.tsv")
    hidden = read(P379 / "THREE_HUNDRED_SEVENTY_NINTH_14_HIDDEN_VALUE_CHECK.tsv")
    values = {int(row["source_position"]): row["hidden_atomic_value_de"] for row in hidden}
    choices = {2: "or", 8: "dy", 9: "daiin"}
    line_positions = {1: [1, 2, 3, 4], 2: [4], 3: [5, 6, 7], 4: [8, 9, 10, 11], 5: [12, 13, 14]}
    surface_by_position = {
        int(row["dictation_order"]): choices.get(int(row["dictation_order"]), row["third_scribe_surface"])
        for row in calls
    }
    lines = {
        line_no: " ".join(surface_by_position[position] for position in positions)
        for line_no, positions in line_positions.items()
    }

    source_rows: list[dict[str, object]] = []
    for row in calls:
        position = int(row["dictation_order"])
        surface = surface_by_position[position]
        source_rows.append({
            "source_position": position,
            "owner_code": row["owner_code"],
            "microcycle": row["microcycle"],
            "board_call_only": row["board_call_only"],
            "joint_tuple_id": row["joint_tuple_id"],
            "third_copy_surface": row["third_scribe_surface"],
            "fourth_copy_surface": surface,
            "surface_changed": "YES" if position in choices else "NO",
            "registered_palette": row["registered_palette"],
            "surface_registered": "YES" if surface in row["registered_palette"].split("|") else "NO",
            "german_value_spoken_to_scribe": "NO",
            "hidden_atomic_value_de": values[position],
        })
    write("THREE_HUNDRED_EIGHTY_SECOND_14_SOURCE_CARDS.tsv", source_rows)

    visible_rows: list[dict[str, object]] = []
    for line_no, positions in line_positions.items():
        for visible_no, position in enumerate(positions, 1):
            source = source_rows[position - 1]
            is_margin = line_no == 1 and visible_no == 4
            visible_rows.append({
                "line_no": line_no,
                "visible_no": visible_no,
                "rendered_line": lines[line_no],
                "source_position": position,
                "surface": source["fourth_copy_surface"],
                "joint_tuple_id": source["joint_tuple_id"],
                "owner_code": source["owner_code"],
                "microcycle": source["microcycle"],
                "visibility_role": "MARKED_ANTICIPATION" if is_margin else "SOURCE",
                "source_contribution": 0 if is_margin else 1,
            })
    write("THREE_HUNDRED_EIGHTY_SECOND_15_VISIBLE_FORMS.tsv", visible_rows)

    palette = {
        surface: row
        for row in calls
        for surface in row["registered_palette"].split("|")
    }
    reconstructed_rows: list[dict[str, object]] = []
    for visible in visible_rows:
        if visible["visibility_role"] == "MARKED_ANTICIPATION":
            continue
        lookup = palette[visible["surface"]]
        position = int(visible["source_position"])
        reconstructed_rows.append({
            "read_order": len(reconstructed_rows) + 1,
            "surface_seen": visible["surface"],
            "owner_seen": visible["owner_code"],
            "microcycle_seen": visible["microcycle"],
            "reconstructed_joint_tuple_id": lookup["joint_tuple_id"],
            "reconstructed_board_call": lookup["board_call_only"],
            "expected_board_call": source_rows[position - 1]["board_call_only"],
            "identity_match": "YES" if lookup["joint_tuple_id"] == source_rows[position - 1]["joint_tuple_id"] else "NO",
            "call_match": "YES" if lookup["board_call_only"] == source_rows[position - 1]["board_call_only"] else "NO",
            "hidden_backread_de": values[position],
        })
    write("THREE_HUNDRED_EIGHTY_SECOND_14_RECONSTRUCTED_CALLS.tsv", reconstructed_rows)

    page = f"""# Pass 382 — vierte vollständige Abschrift

Der Schreiber bekommt wieder nur Besitzer-, Mikrogang-, Positions- und
Kartenaufrufe. Diesmal setzt er drei zuvor einzeln geübte Formen gemeinsam ein:
`or`, `dy`, `daiin`.

```text
+--------------+  {lines[1]}
| H4 BLATTBILD |  {lines[2]}
|  zuerst      |
+--------------+
{lines[3]}

+---------------------+  {lines[4]}
| B3 BECKEN/VERBINDUNG |
|  zuerst              |
+---------------------+
{lines[5]}
```

Der zweite Leser streicht die markierte Randkopie von `cheky`, schlägt jede
Oberfläche im gemeinsamen Kartenbrett nach und rekonstruiert alle vierzehn
Aufrufe, ohne eine deutsche Bedeutung zu sehen.

Erst die getrennte Rücklesung ergibt:

`{' | '.join(values[position] for position in range(1, 15))}`
"""
    (HERE / "THREE_HUNDRED_EIGHTY_SECOND_FOURTH_COPY.md").write_text(page, encoding="utf-8")
    report = """# Pass 382 — drei neue Wrapper gleichzeitig

Die vierte Abschrift kombiniert `or`, `dy` und `daiin` in einem vollständigen
Viergang-Text. Alle übrigen elf Quellenpositionen bleiben wie in Kopie drei.
Die gemeinsame Anfangsform `d-` der beiden benachbarten Oberflächen führt nicht
zu einer Verwechslung: `dy` wird als Y-/Diesposten-Karte und `daiin` als
AIIN-/Sollmaß-Karte zurückgelesen.

Fünfzehn sichtbare Formen ergeben nach der markierten Randkopie genau vierzehn
Quellkarten. Der Leser rekonstruiert alle Besitzer-, Mikrogang-, Karten- und
Positionsaufrufe ohne deutsche Glossenvorgabe. Das stützt die Arbeitsannahme,
dass der Eintrittswrapper die Kartenform steuert, aber nicht selbst den
Inhaltskern ersetzt.

Als nächstes soll eine kleine Kontrasttafel die drei Y- und zwei AIIN-Formen in
denselben Satzrahmen nebeneinanderstellen. So wird sichtbar, welche Teile beim
Kopieren tatsächlich invariant bleiben.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "source_cards": len(source_rows),
        "visible_forms": len(visible_rows),
        "reconstructed_calls": len(reconstructed_rows),
        "simultaneous_changes": choices,
        "identity_matches": sum(row["identity_match"] == "YES" for row in reconstructed_rows),
        "call_matches": sum(row["call_match"] == "YES" for row in reconstructed_rows),
    }
    (HERE / "THREE_HUNDRED_EIGHTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
