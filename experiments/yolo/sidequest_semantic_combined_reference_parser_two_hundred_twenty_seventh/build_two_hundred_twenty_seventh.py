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
R226 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_card_grammar_two_hundred_twenty_sixth"
EVENTS = R221 / "TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"
ABA = R224 / "TWO_HUNDRED_TWENTY_FOURTH_NINE_ABA_WINDOWS.tsv"
DUPLICATES = R226 / "TWO_HUNDRED_TWENTY_SIXTH_SIX_DUPLICATE_PAIRS.tsv"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


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
    aba = {row["start_event"]: row for row in read(ABA)}
    duplicates = {row["first_event"]: row for row in read(DUPLICATES)}
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_record[row["record_unit_id"]].append(row)

    units: list[dict[str, object]] = []
    for record in RECORD_ORDER:
        rows = by_record[record]
        index = 0
        while index < len(rows):
            first = rows[index]
            event_id = first["event_id"]
            visible_count = 1
            source_count = 1
            rule_applications = 0
            kind = "ATOMIC_CARD"
            reading = first["portable_value_de"]
            if event_id == "E020":
                visible_count = 4
                source_count = 4
                rule_applications = 2
                kind = "PAIR_PLUS_ABA_RETURN"
                reading = "dieser und dieser Posten; den zweiten auf Sollwert setzen und als denselben Posten aktiv halten"
            elif event_id in aba and event_id != "E021":
                visible_count = 3
                source_count = 3
                rule_applications = 1
                kind = "ABA_RETURN_FRAME"
                reading = aba[event_id]["selected_working_reading_de"]
            elif event_id in duplicates:
                duplicate = duplicates[event_id]
                visible_count = 2
                source_count = int(duplicate["source_token_count"])
                rule_applications = 1
                if duplicate["selected_rule"] == "PAIR_TWO_SETTINGS":
                    kind = "OPEN_PAIR"
                elif duplicate["selected_rule"] == "REPEAT_COMPLETE_OPERATION":
                    kind = "REPEATED_CLOSED_OPERATION"
                elif duplicate["selected_rule"] == "READ_ONCE_CARRY":
                    kind = "CARRY_SINGLE_SOURCE"
                elif duplicate["selected_rule"] == "PAIR_TWO_REFERENTS":
                    raise ValueError("E020 pair must be consumed by combined frame")
                else:
                    raise ValueError(duplicate["selected_rule"])
                reading = duplicate["pair_reading_de"]
            source_rows = rows[index:index + visible_count]
            if len(source_rows) != visible_count:
                raise ValueError(f"truncated construction at {event_id}")
            units.append({
                "reading_unit_id": f"R{len(units) + 1:03d}",
                "record_unit_id": record,
                "statement_ids": "|".join(dict.fromkeys(row["statement_id"] for row in source_rows)),
                "unit_kind": kind,
                "source_event_ids": "|".join(row["event_id"] for row in source_rows),
                "visible_card_count": visible_count,
                "source_token_count": source_count,
                "rule_applications": rule_applications,
                "visible_surface_sequence": " ".join(row["visible_surface"] for row in source_rows),
                "literal_value_sequence": " > ".join(row["portable_value_de"] for row in source_rows),
                "construction_reading_de": reading,
            })
            index += visible_count
    write(OUT / "TWO_HUNDRED_TWENTY_SEVENTH_357_READING_UNITS.tsv", units)

    summaries: list[dict[str, object]] = []
    for record in RECORD_ORDER:
        rows = [row for row in units if row["record_unit_id"] == record]
        summaries.append({
            "record_unit_id": record,
            "visible_cards": sum(int(row["visible_card_count"]) for row in rows),
            "source_tokens": sum(int(row["source_token_count"]) for row in rows),
            "reading_units": len(rows),
            "atomic_units": sum(row["unit_kind"] == "ATOMIC_CARD" for row in rows),
            "composite_units": sum(row["unit_kind"] != "ATOMIC_CARD" for row in rows),
            "rule_applications": sum(int(row["rule_applications"]) for row in rows),
            "unit_kinds": "|".join(sorted({str(row["unit_kind"]) for row in rows})),
        })
    write(OUT / "TWO_HUNDRED_TWENTY_SEVENTH_ELEVEN_RECORD_SUMMARIES.tsv", summaries)

    composites = [row for row in units if row["unit_kind"] != "ATOMIC_CARD"]
    lines = [
        "# Kombinierte Referenz- und Wiederholungsgrammatik",
        "",
        "Die Prosa hat drei Zählebenen: **381 sichtbare Karten**, **380 Quelltoken** und **357 Leseeinheiten**.",
        "",
        "Das einzige verschachtelte Fenster ist `dy chy taiin shy`: eine offene Zweiergruppe plus ein überlappender Y–AIIN–Y-Rückkehrrahmen.",
        "",
    ]
    for row in composites:
        lines.extend([
            f"## {row['reading_unit_id']} · {row['record_unit_id']} · {row['unit_kind']}",
            "",
            f"`{row['visible_surface_sequence']}` → **{row['construction_reading_de']}**",
            "",
            f"Sichtbar {row['visible_card_count']}; Quelle {row['source_token_count']}; Regelanwendungen {row['rule_applications']}.",
            "",
        ])
    (OUT / "TWO_HUNDRED_TWENTY_SEVENTH_COMPOSITE_READING_MANUAL.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "aba_source_sha256": hashlib.sha256(ABA.read_bytes()).hexdigest(),
        "duplicate_source_sha256": hashlib.sha256(DUPLICATES.read_bytes()).hexdigest(),
        "visible_cards": sum(int(row["visible_card_count"]) for row in units),
        "source_tokens": sum(int(row["source_token_count"]) for row in units),
        "reading_units": len(units),
        "atomic_units": sum(row["unit_kind"] == "ATOMIC_CARD" for row in units),
        "composite_units": len(composites),
        "rule_applications": sum(int(row["rule_applications"]) for row in units),
        "records": len(summaries),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
