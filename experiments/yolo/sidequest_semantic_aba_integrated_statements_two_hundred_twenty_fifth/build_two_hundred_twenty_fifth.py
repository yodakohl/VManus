#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R221 = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first"
R224 = ROOT / "experiments/yolo/sidequest_semantic_aba_return_frame_two_hundred_twenty_fourth"
EVENTS = R221 / "TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"
STATEMENTS = R221 / "TWO_HUNDRED_TWENTY_FIRST_116_STATEMENT_PROSE.tsv"
ABA = R224 / "TWO_HUNDRED_TWENTY_FOURTH_NINE_ABA_WINDOWS.tsv"

REWRITES = {
    "H2-S001": "Auszugsansatz bereitstellen und Folgeansatz vorbereiten; diesen und den folgenden Posten führen, den folgenden auf Sollwert setzen und als aktuellen Posten halten.",
    "H2-S002": "Folgeansatz ansetzen; im Fortgang denselben Ansatz ohne Wechsel weiterführen und davon den Sollwert nehmen.",
    "H2-S003": "Im Zubereitungsgefäß den Ansatz führen, denselben Posten durch die Bearbeitungsstufe halten und das Zugabemaß einsetzen.",
    "H3-S003": "Vom vorigen Ansatz denselben Posten bearbeiten und behalten, dann auf Sollwert bringen.",
    "B1-S002": "Eine Portion ansetzen, weiterführen und am Ziel einsetzen; denselben Sollwert während des langen Zieleinsatzes halten, durchleiten und überführen; Schluss.",
    "B1-S008": "Denselben laufenden Gang kurz wärmen und weiterführen, dann kurz absetzen; Schluss.",
    "B2-S011": "Anteil zugeben, davon nehmen, denselben Zugabegang wiederholen und länger einwirken; Schluss.",
    "B3-S003": "Diesen Bestand auf Sollwert setzen, als denselben Bestand aktiv halten und abführen; Schluss.",
    "B6-S001": "Länger sammeln und kurz bearbeiten; am Endposten den laufenden Gang auf Sollwert bringen und fortsetzen, dann die Einlage zum Endziel führen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    statements = read(STATEMENTS)
    aba = read(ABA)
    aba_by_start = {row["start_event"]: row for row in aba}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    units: list[dict[str, object]] = []
    statement_rows: list[dict[str, object]] = []
    for statement in statements:
        rows = by_statement[statement["statement_id"]]
        segments: list[str] = []
        unit_ids: list[str] = []
        index = 0
        construction_count = 0
        while index < len(rows):
            row = rows[index]
            unit_id = f"U{len(units) + 1:03d}"
            if row["event_id"] in aba_by_start:
                frame = aba_by_start[row["event_id"]]
                source_rows = rows[index:index + 3]
                if len(source_rows) != 3 or source_rows[-1]["master_card_id"] != row["master_card_id"]:
                    raise ValueError(f"broken ABA at {row['event_id']}")
                event_ids = "|".join(item["event_id"] for item in source_rows)
                visible = " ".join(item["visible_surface"] for item in source_rows)
                literal = frame["value_window"]
                reading = frame["selected_working_reading_de"]
                kind = "ABA_RETURN_FRAME"
                segments.append(f"[ABA:{reading}]")
                index += 3
                construction_count += 1
            else:
                event_ids = row["event_id"]
                visible = row["visible_surface"]
                literal = row["portable_value_de"]
                reading = row["portable_value_de"]
                kind = "ATOMIC_CARD"
                segments.append(f"[KARTE:{reading}]")
                index += 1
            unit_ids.append(unit_id)
            units.append({
                "parse_unit_id": unit_id,
                "statement_id": statement["statement_id"],
                "record_unit_id": statement["record_unit_id"],
                "unit_kind": kind,
                "source_event_ids": event_ids,
                "visible_surface_sequence": visible,
                "literal_value_sequence": literal,
                "construction_reading_de": reading,
            })
        statement_rows.append({
            "statement_id": statement["statement_id"],
            "record_unit_id": statement["record_unit_id"],
            "visible_owner": statement["visible_owner"],
            "visible_sequence": statement["visible_sequence"],
            "source_event_count": len(rows),
            "parse_unit_count": len(unit_ids),
            "aba_frame_count": construction_count,
            "parse_unit_ids": "|".join(unit_ids),
            "construction_aware_reading": " ".join(segments),
            "fluent_construction_aware_de": REWRITES.get(statement["statement_id"], statement["r221_owner_expansion_de"]),
            "revision_status": "ABA_REWRITTEN" if statement["statement_id"] in REWRITES else "UNCHANGED",
        })
    write(OUT / "TWO_HUNDRED_TWENTY_FIFTH_363_PARSE_UNITS.tsv", units)
    write(OUT / "TWO_HUNDRED_TWENTY_FIFTH_116_ABA_INTEGRATED_STATEMENTS.tsv", statement_rows)

    lines = ["# Satzedition mit A–B–A-Rückkehrrahmen", ""]
    for record in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"):
        rows = [row for row in statement_rows if row["record_unit_id"] == record]
        lines.extend([f"## {record} — {rows[0]['visible_owner']}", ""])
        for row in rows:
            marker = "RAHMEN" if int(row["aba_frame_count"]) else "EINZELKARTEN"
            lines.extend([
                f"- **{row['statement_id']} · {marker}** `{row['visible_sequence']}`",
                f"  - Bau: {row['construction_aware_reading']}",
                f"  - Lesung: {row['fluent_construction_aware_de']}",
            ])
        lines.append("")
    (OUT / "TWO_HUNDRED_TWENTY_FIFTH_READABLE_ABA_EDITION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "statement_source_sha256": hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),
        "aba_source_sha256": hashlib.sha256(ABA.read_bytes()).hexdigest(),
        "source_events": len(events),
        "statements": len(statement_rows),
        "parse_units": len(units),
        "atomic_units": sum(row["unit_kind"] == "ATOMIC_CARD" for row in units),
        "aba_units": sum(row["unit_kind"] == "ABA_RETURN_FRAME" for row in units),
        "rewritten_statements": sum(row["revision_status"] == "ABA_REWRITTEN" for row in statement_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
