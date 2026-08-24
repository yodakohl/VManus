#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}

LADDER = [
    ("OK+Y", "276a7c2d74d1143446f4", "choky|oky|qoky", "NONE", "Y_OPEN", "Arbeitsgang ansetzen; Diesposten bleibt offen", 10),
    ("OK+E+Y", "08bd5ca0c2ad137a056d", "okey|qokey", "SHORT", "Y_OPEN", "kurz in Kontakt setzen; Diesposten bleibt offen", 2),
    ("OK+EE+Y", "0275fbf14e07935b0a45", "okeey|qokeey", "LONG", "Y_OPEN", "länger in Kontakt halten; Diesposten bleibt offen", 7),
    ("OK+E+DY", "7db18b2f0fb7ed0fcfd3", "qokedy", "SHORT", "DY_CLOSE", "kurz in Kontakt setzen; Schritt schließen", 8),
    ("OK+EE+DY", "7d25241b0e56c836372a", "qokeedy", "LONG", "DY_CLOSE", "länger in Kontakt halten; Schritt schließen", 10),
    ("OK+EEE+DY", "d25110e0d8488927278f", "qokeeedy", "FULL", "DY_CLOSE", "vollständig in Kontakt bringen; Schritt schließen", 1),
]

EXTENSIONS = [
    ("OK+EE+AL", "93f69c38fdedee1598e9", "qokeedal", "länger an der Zielstelle halten"),
    ("OK+EE+OL", "daf32e6db9e04413ce7f", "okeeol", "länger mit dem vorigen Gang fortfahren"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read(SOURCE)
    if {row["page"] for row in source} - PAGES:
        raise SystemExit("unexpected page")
    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_field[row["field_id"]].append(row)
    for rows in by_field.values():
        rows.sort(key=lambda row: int(row["event_serial"]))

    ladder_rows: list[dict[str, object]] = []
    occurrence_rows: list[dict[str, object]] = []
    ladder_by_id = {joint_id: (parse, surfaces, grade, endpoint, reading, expected) for parse, joint_id, surfaces, grade, endpoint, reading, expected in LADDER}
    for parse, joint_id, surfaces, grade, endpoint, reading, expected in LADDER:
        selected = [row for row in source if row["joint_tuple_id"] == joint_id]
        pages = Counter(row["page"] for row in selected)
        ladder_rows.append({
            "composition": parse,
            "joint_tuple_id": joint_id,
            "registered_surfaces": surfaces,
            "ok_value": "ARBEITSGANG_ANSETZEN",
            "e_grade": grade,
            "endpoint": endpoint,
            "short_default_de": reading,
            "real_occurrences": len(selected),
            "expected_occurrences": expected,
            "page_profile": "|".join(f"{page}:{count}" for page, count in sorted(pages.items())),
            "teaching_status": "PRODUCTIVE_LADDER_CELL",
        })
    for field_id, rows in by_field.items():
        for ordinal, row in enumerate(rows, 1):
            if row["joint_tuple_id"] not in ladder_by_id:
                continue
            parse, surfaces, grade, endpoint, reading, _ = ladder_by_id[row["joint_tuple_id"]]
            occurrence_rows.append({
                "event_serial": row["event_serial"],
                "event_id": row["event_id"],
                "page": row["page"],
                "locus": row["locus"],
                "field_id": field_id,
                "statement_id": row["statement_id"],
                "field_ordinal": ordinal,
                "field_length": len(rows),
                "surface": row["surface_display"],
                "joint_tuple_id": row["joint_tuple_id"],
                "composition": parse,
                "e_grade": grade,
                "endpoint": endpoint,
                "short_default_de": reading,
            })
    occurrence_rows.sort(key=lambda row: int(row["event_serial"]))
    write("THREE_HUNDRED_EIGHTY_FOURTH_SIX_CELL_LADDER.tsv", ladder_rows)
    write("THREE_HUNDRED_EIGHTY_FOURTH_38_REAL_OCCURRENCES.tsv", occurrence_rows)

    extension_rows: list[dict[str, object]] = []
    for parse, joint_id, surfaces, reading in EXTENSIONS:
        selected = [row for row in source if row["joint_tuple_id"] == joint_id]
        extension_rows.append({
            "composition": parse,
            "joint_tuple_id": joint_id,
            "registered_surfaces": surfaces,
            "real_occurrences": len(selected),
            "event_ids": "|".join(row["event_id"] for row in selected),
            "predicted_reading_de": reading,
            "role": "EXISTING_ENDPOINT_SUBSTITUTION",
        })
    write("THREE_HUNDRED_EIGHTY_FOURTH_TWO_ENDPOINT_EXTENSIONS.tsv", extension_rows)

    boundary_rows = [
        {"surface_family": "chey|cheey", "reason_not_in_ladder": "different exact cards; extra E does not preserve the Y card", "workshop_treatment": "memorize separately"},
        {"surface_family": "chdy|chedy", "reason_not_in_ladder": "this exact card is repeatedly nonterminal", "workshop_treatment": "CHED work card; do not split as D+Y close"},
        {"surface_family": "chokchy|okchy|qokchy", "reason_not_in_ladder": "second exact identity with the same broad use reading", "workshop_treatment": "learned duplicate/nomenclator card"},
        {"surface_family": "qokokchy", "reason_not_in_ladder": "double OK has one occurrence and may mark repetition", "workshop_treatment": "whole-card repeat instruction"},
        {"surface_family": "qokshedy", "reason_not_in_ladder": "contains independent SHED operation", "workshop_treatment": "OK+SHED compound, not E-grade cell"},
        {"surface_family": "qokchdy|qokchedy", "reason_not_in_ladder": "contains CHED operation core", "workshop_treatment": "OK+CHED compound, not contact grade"},
    ]
    write("THREE_HUNDRED_EIGHTY_FOURTH_BOUNDARY_CARDS.tsv", boundary_rows)

    chart = """# Pass 384 — OK-Grad-Endpunkt-Leiter

|                | offen: Y | geschlossen: DY |
|---|---|---|
| unmarkiert | `oky` — Arbeitsgang ansetzen | — |
| kurz E | `okey` — kurz ansetzen | `qokedy` — kurz ansetzen; Schluss |
| länger EE | `okeey` — länger halten | `qokeedy` — länger halten; Schluss |
| vollständig EEE | — | `qokeeedy` — vollständig in Kontakt; Schluss |

Die Werkstatt liest nicht sechs lange Wörter auswendig. Sie lernt:

1. **OK** — Arbeitsgang ansetzen.
2. **E / EE / EEE** — kurz / länger / vollständig.
3. **Y** — laufender Diesposten bleibt verfügbar.
4. **DY** — nur in diesen lizenzierten Karten: Schritt schließen.

Zwei bereits vorhandene Seitenformen zeigen, dass der Endslot austauschbar ist:
`qokeedal` = länger an der Zielstelle halten; `okeeol` = länger mit dem vorigen
Gang fortfahren.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_FOURTH_LADDER_SHEET.md").write_text(chart, encoding="utf-8")
    report = """# Pass 384 — die bislang beste produktive Fachkürzung

Sechs Kartenfamilien mit zusammen 38 echten Vorkommen bilden eine kompakte
OK-Leiter. OK setzt den Arbeitsgang an; E, EE und EEE staffeln kurz, länger und
vollständig; Y lässt den Diesposten offen, während die lizenzierte DY-Endform den
Schritt schließt. Damit werden sechs Karten aus vier lehrbaren Entscheidungen
gebaut.

Die Leiter ist absichtlich lokal. Sichtbares `dy` ist nicht überall Schluss,
und sichtbares `e` ist nicht überall Grad. Sechs benachbarte Ganzkartenfamilien
bleiben außerhalb der Regel. Das ist genau die gesuchte Mischung aus produktiver
Fachkürzung und gelerntem Nomenklator.

Die existierenden Karten `qokeedal` und `okeeol` liefern zwei sofort lesbare
Endslot-Erweiterungen: Zielstelle statt Y/DY sowie Fortsetzung statt Y/DY.
Als nächstes soll ein Lehrling aus der Leiter neue vollständige Arbeitsgänge nur
mit bereits belegten Karten bauen und anschließend die lange deutsche
Umschreibung wieder auf vier kurze Komponenten reduzieren.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "ladder_cells": len(ladder_rows),
        "real_occurrences": len(occurrence_rows),
        "endpoint_extensions": len(extension_rows),
        "boundary_families": len(boundary_rows),
        "selected_rule": "OK + E_GRADE + Y_OR_LICENSED_DY_ENDPOINT",
    }
    (HERE / "THREE_HUNDRED_EIGHTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
