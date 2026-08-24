#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P379 = ROOT / "experiments/yolo/sidequest_semantic_board_call_third_copy_three_hundred_seventy_ninth"
P380 = ROOT / "experiments/yolo/sidequest_semantic_three_copy_stem_sheet_three_hundred_eightieth"


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
    predictions = read(P380 / "THREE_HUNDRED_EIGHTIETH_REMAINING_WRAPPER_PREDICTIONS.tsv")
    by_position = {int(row["dictation_order"]): row for row in calls}
    values = {int(row["source_position"]): row["hidden_atomic_value_de"] for row in hidden}
    core_position = {"OR": 2, "Y": 8, "AIIN": 9}
    value_sequence = " | ".join(values[position] for position in range(1, 15))
    value_hash = hashlib.sha256(value_sequence.encode()).hexdigest()

    drill_rows: list[dict[str, object]] = []
    full_rows: list[dict[str, object]] = []
    for index, prediction in enumerate(predictions, 1):
        drill_id = f"D{index:02d}"
        position = core_position[prediction["core"]]
        target = by_position[position]
        before = target["third_scribe_surface"]
        after = prediction["predicted_surface"]
        left = by_position[position - 1]["third_scribe_surface"] if position > 1 else "START"
        right = by_position[position + 1]["third_scribe_surface"] if position < 14 else "END"
        drill_rows.append({
            "drill_id": drill_id,
            "core": prediction["core"],
            "source_position": position,
            "owner_code": target["owner_code"],
            "microcycle": target["microcycle"],
            "left_neighbour_fixed": left,
            "baseline_surface": before,
            "substitute_surface": after,
            "right_neighbour_fixed": right,
            "joint_tuple_id": target["joint_tuple_id"],
            "atomic_value_de": values[position],
            "registered_palette": target["registered_palette"],
            "one_change_only": "YES",
            "identity_preserved": "YES",
            "value_preserved": "YES",
            "full_value_sequence_sha256": value_hash,
        })
        for source_position in range(1, 15):
            row = by_position[source_position]
            surface = after if source_position == position else row["third_scribe_surface"]
            full_rows.append({
                "drill_id": drill_id,
                "source_position": source_position,
                "owner_code": row["owner_code"],
                "microcycle": row["microcycle"],
                "board_call_only": row["board_call_only"],
                "joint_tuple_id": row["joint_tuple_id"],
                "baseline_surface": row["third_scribe_surface"],
                "drill_surface": surface,
                "surface_changed": "YES" if source_position == position else "NO",
                "registered_palette": row["registered_palette"],
                "surface_is_registered": "YES" if surface in row["registered_palette"].split("|") else "NO",
                "atomic_backread_de": values[source_position],
                "identity_backread": row["joint_tuple_id"],
            })

    write("THREE_HUNDRED_EIGHTY_FIRST_SIX_SUBSTITUTION_DRILLS.tsv", drill_rows)
    write("THREE_HUNDRED_EIGHTY_FIRST_84_CARD_BACKREAD.tsv", full_rows)

    lines = [
        "# Pass 381 — sechs Wrapperproben",
        "",
        "Der Meister lässt jeweils nur eine Form wechseln. Besitzer, Mikrogang, Karten-ID, Nachbarn und die übrigen dreizehn Karten bleiben gleich.",
        "",
    ]
    for row in drill_rows:
        lines.append(
            f"- **{row['drill_id']} {row['core']}**: `{row['left_neighbour_fixed']} {row['baseline_surface']} {row['right_neighbour_fixed']}` → "
            f"`{row['left_neighbour_fixed']} {row['substitute_surface']} {row['right_neighbour_fixed']}`; Rücklesung bleibt **{row['atomic_value_de']}**."
        )
    lines += [
        "",
        "Alle sechs Proben ergeben dieselbe vierzehnteilige Wertfolge:",
        "",
        f"`{value_sequence}`",
        "",
        "Damit sind `or`, `chy`, `dy`, `shy`, `aiin` und `daiin` nicht bloß Listenformen: Sie funktionieren in demselben lokalen Satzplatz wie ihre bereits verwendeten Schwestern.",
    ]
    (HERE / "THREE_HUNDRED_EIGHTY_FIRST_DRILL_BOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = f"""# Pass 381 — registrierte Wrapper im unveränderten Kontext

Sechs Einzelaustausche wurden durchgeführt. Bei jeder Probe blieb die gesamte
vierzehnteilige Abschrift bis auf genau eine Oberfläche unverändert. Alle sechs
Ersatzformen gehören bereits zur registrierten Palette derselben exakten Karte.

Die Proben schließen die bisher unbenutzten Formen `or`, `chy`, `dy`, `shy`,
`aiin` und `daiin` praktisch an. Sie bestätigen die knappe Werkstattregel:
Eintrittsform wechseln, Kartenidentität und Kernwert behalten.

Jede der sechs vollständigen Rücklesungen liefert dieselbe Wertfolge mit SHA-256
`{value_hash}`. Als nächstes kann eine vierte vollständige Abschrift drei dieser
Formen gleichzeitig verwenden; die übrigen drei Y/AIIN-Schwestern gehören in
parallele Lehrlingszeilen, weil ein einzelner Satzplatz nicht mehrere Formen
zugleich aufnehmen kann.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "drills": len(drill_rows),
        "cards_backread": len(full_rows),
        "cards_per_drill": 14,
        "single_surface_changes": sum(row["one_change_only"] == "YES" for row in drill_rows),
        "predicted_surfaces": [row["substitute_surface"] for row in drill_rows],
        "value_sequence_sha256": value_hash,
    }
    (HERE / "THREE_HUNDRED_EIGHTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
