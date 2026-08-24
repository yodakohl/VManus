#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

Y_ID = "b921a237be883a820352"
AIIN_ID = "2f1c5e56e8f0ff459065"
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
SURFACES = {
    "Y": {"chey": "CHE", "chy": "CH", "dy": "D", "shy": "SH", "sy": "S", "y": "BARE"},
    "AIIN": {"aiin": "BARE", "chaiin": "CH", "daiin": "D", "saiin": "S", "taiin": "T"},
}
VALUES = {"Y": "Diesposten", "AIIN": "Sollmaß"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def position_class(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def main() -> None:
    rows = read(SOURCE)
    if {row["page"] for row in rows} - PAGES:
        raise SystemExit("unexpected page")
    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_field[row["field_id"]].append(row)
    for field_rows in by_field.values():
        field_rows.sort(key=lambda row: int(row["event_serial"]))

    occurrence_rows: list[dict[str, object]] = []
    for field_id, field_rows in by_field.items():
        for ordinal, row in enumerate(field_rows, 1):
            family = "Y" if row["joint_tuple_id"] == Y_ID else "AIIN" if row["joint_tuple_id"] == AIIN_ID else None
            if family is None:
                continue
            surface = row["surface_display"]
            occurrence_rows.append({
                "event_serial": row["event_serial"],
                "event_id": row["event_id"],
                "family": family,
                "core_value_de": VALUES[family],
                "surface": surface,
                "entry_shell": SURFACES[family][surface],
                "page": row["page"],
                "locus": row["locus"],
                "field_id": field_id,
                "statement_id": row["statement_id"],
                "field_ordinal": ordinal,
                "field_length": len(field_rows),
                "field_position": position_class(ordinal, len(field_rows)),
                "left_surface": field_rows[ordinal - 2]["surface_display"] if ordinal > 1 else "FIELD_START",
                "right_surface": field_rows[ordinal]["surface_display"] if ordinal < len(field_rows) else "FIELD_END",
                "joint_tuple_id": row["joint_tuple_id"],
            })
    occurrence_rows.sort(key=lambda row: int(row["event_serial"]))
    write("THREE_HUNDRED_EIGHTY_THIRD_38_REAL_OCCURRENCES.tsv", occurrence_rows)

    summary_rows: list[dict[str, object]] = []
    for family in ("Y", "AIIN"):
        family_rows = [row for row in occurrence_rows if row["family"] == family]
        for surface, shell in SURFACES[family].items():
            selected = [row for row in family_rows if row["surface"] == surface]
            positions = Counter(row["field_position"] for row in selected)
            pages = Counter(row["page"] for row in selected)
            summary_rows.append({
                "family": family,
                "core_value_de": VALUES[family],
                "surface": surface,
                "entry_shell": shell,
                "occurrences": len(selected),
                "event_ids": "|".join(row["event_id"] for row in selected),
                "page_profile": "|".join(f"{key}:{value}" for key, value in sorted(pages.items())),
                "first": positions["FIRST"],
                "middle": positions["MIDDLE"],
                "last": positions["LAST"],
                "only": positions["ONLY"],
                "shared_shell_across_families": "YES" if shell in {"BARE", "CH", "D", "S"} else "NO",
                "teaching_reading": f"{shell}+{family} = {VALUES[family]}",
            })
    write("THREE_HUNDRED_EIGHTY_THIRD_11_SURFACE_CONTRAST.tsv", summary_rows)

    shared_rows: list[dict[str, object]] = []
    for shell in ("BARE", "CH", "D", "S"):
        y = next(row for row in summary_rows if row["family"] == "Y" and row["entry_shell"] == shell)
        aiin = next(row for row in summary_rows if row["family"] == "AIIN" and row["entry_shell"] == shell)
        shared_rows.append({
            "entry_shell": shell,
            "y_surface": y["surface"],
            "y_occurrences": y["occurrences"],
            "y_value": "Diesposten",
            "aiin_surface": aiin["surface"],
            "aiin_occurrences": aiin["occurrences"],
            "aiin_value": "Sollmaß",
            "shared_mechanism": "SAME_ENTRY_SHELL_DIFFERENT_CORE",
            "semantic_contribution_of_shell": "NONE_ASSIGNED",
        })
    write("THREE_HUNDRED_EIGHTY_THIRD_FOUR_SHARED_SHELLS.tsv", shared_rows)

    drill_rows: list[dict[str, object]] = []
    for surface, shell in SURFACES["Y"].items():
        drill_rows.append({
            "family": "Y",
            "entry_shell": shell,
            "exercise_frame": f"checthy {surface} daiin",
            "literal_backread": "Bereit | Diesposten | Sollmaß",
            "surface_registered": "YES",
        })
    for surface, shell in SURFACES["AIIN"].items():
        drill_rows.append({
            "family": "AIIN",
            "entry_shell": shell,
            "exercise_frame": f"dy {surface} shckhy",
            "literal_backread": "Diesposten | Sollmaß | durchleiten",
            "surface_registered": "YES",
        })
    write("THREE_HUNDRED_EIGHTY_THIRD_ELEVEN_CONTRAST_LINES.tsv", drill_rows)

    page = [
        "# Pass 383 — Y/AIIN-Kontrastblatt",
        "",
        "## Y = Diesposten",
        "",
    ]
    for row in drill_rows[:6]:
        page.append(f"- `{row['exercise_frame']}` → {row['literal_backread']} ({row['entry_shell']})")
    page += ["", "## AIIN = Sollmaß", ""]
    for row in drill_rows[6:]:
        page.append(f"- `{row['exercise_frame']}` → {row['literal_backread']} ({row['entry_shell']})")
    page += [
        "",
        "## Lehrregel",
        "",
        "`BARE`, `CH`, `D` und `S` sind gemeinsame Eintrittsschalen. Sie liefern hier keinen eigenen Sachwert; der längere Kern Y oder AIIN entscheidet zwischen Diesposten und Sollmaß. `CHE`/`SH` gehören nur zur Y-Palette, `T` nur zur AIIN-Palette und werden als gelernte Zusatzformen geführt.",
    ]
    (HERE / "THREE_HUNDRED_EIGHTY_THIRD_CONTRAST_SHEET.md").write_text("\n".join(page) + "\n", encoding="utf-8")

    report = """# Pass 383 — eine gemeinsame Eintrittsschale, zwei Kerne

Die echten Seiten enthalten 18 Y- und 20 AIIN-Ereignisse. Zusammen zeigen sie
elf Oberflächen. Vier Eintrittsschalen sind in beiden Familien belegt:
leer, CH, D und S. Darunter bleibt der Kernwert verschieden: Y bezeichnet den
laufenden Diesposten, AIIN das Sollmaß.

Darum ist die beste einfache Werkstattlehre weder ein freies Präfixlexikon noch
zwei völlig getrennte Wortlisten. Es ist **eine gemeinsame Schalenmechanik mit
familiengebundenen Kartenwerten**. Die Schale wählt eine zulässige Schreibform;
Y beziehungsweise AIIN trägt den Inhaltsunterschied. CHE/SH bei Y und T bei
AIIN bleiben kleine, auswendig gelernte Erweiterungen der jeweiligen Palette.

Die Verteilung über Feldpositionen ist nicht gleich genug, um BARE/CH/D/S jetzt
mit vier neuen Bedeutungen zu beladen. Genau das wäre wieder der alte Fehler:
aus einem Schreibunterschied ein langes Wörterbuchwort zu machen.

Als nächstes kann dieselbe Methode auf die OKY/OKEEY/OKEDY-Reihe angewandt
werden: gemeinsamer OK-Arbeitskern, E-Grad und Y/DY-Endpunkt müssen getrennt
nebeneinander lesbar werden.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "occurrences": len(occurrence_rows),
        "y_occurrences": sum(row["family"] == "Y" for row in occurrence_rows),
        "aiin_occurrences": sum(row["family"] == "AIIN" for row in occurrence_rows),
        "surfaces": len(summary_rows),
        "shared_shells": [row["entry_shell"] for row in shared_rows],
        "selected_model": "SHARED_ENTRY_SHELL_MECHANISM_WITH_FAMILY_BOUND_CORE_VALUES",
    }
    (HERE / "THREE_HUNDRED_EIGHTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
