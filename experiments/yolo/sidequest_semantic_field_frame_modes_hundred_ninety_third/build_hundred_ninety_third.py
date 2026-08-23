#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv"
FIELDS = ROOT / "experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_135_FIELD_PRESSURE_TEST.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv"


MODE_READING = {
    "CH": "GRUNDZUBEREITUNG_ODER_AUFBAU",
    "D": "RUECKGRIFF_ODER_UEBERNAHME",
    "O": "FORTSETZUNG_IM_AKTIVEN_ANSATZ",
    "Q": "AKTIVIERTER_TEILSCHRITT",
    "S": "ZUSTAND_ERGEBNIS_ODER_NEBENZWEIG",
    "T": "FOLGE_ODER_ZIELUEBERGANG",
    "K": "BEARBEITUNG_ODER_DURCHGANG",
    "L": "ABGANG_ODER_ANSCHLUSS",
    "X": "UNGERAHMTER_POSTEN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    names = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def frame(surface: str) -> str:
    for prefix, name in (("q", "Q"), ("sh", "S"), ("s", "S"), ("ch", "CH"), ("d", "D"), ("t", "T"), ("o", "O"), ("k", "K"), ("l", "L")):
        if surface.startswith(prefix):
            return name
    return "X"


def main() -> None:
    events = read(EVENTS)
    field_source = {row["field_id"]: row for row in read(FIELDS)}
    dictionary = {row["master_card_id"]: row for row in read(DICTIONARY)}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        grouped[row["field_id"]].append(row)

    field_rows: list[dict[str, object]] = []
    mode_by_field: dict[str, str] = {}
    for field_id in sorted(grouped, key=lambda value: int(value[1:])):
        rows = grouped[field_id]
        diagnostics = [row for row in rows if "|" in dictionary[row["master_card_id"]]["registered_surfaces"]]
        counts = Counter(frame(row["surface"]) for row in diagnostics)
        if len(diagnostics) < 2:
            mode = "LOW_DATA"
            mode_count = max(counts.values(), default=0)
        else:
            candidate, mode_count = counts.most_common(1)[0]
            mode = candidate if mode_count >= 2 and mode_count * 2 >= len(diagnostics) else "MIXED"
        mode_by_field[field_id] = mode
        field_rows.append(
            {
                "field_id": field_id,
                "statement_id": rows[0]["statement_id"],
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "event_count": len(rows),
                "multi_surface_diagnostic_events": len(diagnostics),
                "distinct_diagnostic_cards": len({row["master_card_id"] for row in diagnostics}),
                "frame_distribution": "|".join(f"{key}:{value}" for key, value in sorted(counts.items())) or "NONE",
                "field_frame_mode": mode,
                "mode_reading_de": MODE_READING.get(mode, "NICHT_FESTGELEGT"),
                "mode_support_events": mode_count,
                "mode_share": f"{mode_count}/{len(diagnostics)}" if diagnostics else "0/0",
                "close_count": field_source[field_id]["close_count"],
                "restart_count": field_source[field_id]["restart_count"],
                "slot_path": field_source[field_id]["compacted_slot_path"],
                "surface_sequence": field_source[field_id]["surface_sequence"],
            }
        )
    write(OUT / "HUNDRED_NINETY_THIRD_135_FIELD_FRAME_MODES.tsv", field_rows)

    event_rows: list[dict[str, object]] = []
    for row in events:
        card = dictionary[row["master_card_id"]]
        diagnostic = "|" in card["registered_surfaces"]
        event_frame = frame(row["surface"])
        mode = mode_by_field[row["field_id"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "field_id": row["field_id"],
                "field_position": row["field_position"],
                "master_card_id": row["master_card_id"],
                "surface": row["surface"],
                "atomic_value_de": row["atomic_value_de"],
                "multi_surface_diagnostic": "YES" if diagnostic else "NO",
                "surface_frame": event_frame,
                "field_frame_mode": mode,
                "aligns_with_mode": "YES" if diagnostic and event_frame == mode else "NO" if diagnostic and mode not in {"LOW_DATA", "MIXED"} else "NOT_SCORED",
                "primary_grammar_slot": row["primary_grammar_slot"],
                "field_close_role": row["field_close_role"],
            }
        )
    write(OUT / "HUNDRED_NINETY_THIRD_381_EVENT_FRAME_TRACE.tsv", event_rows)

    candidate_fields = [row for row in field_rows if row["field_frame_mode"] not in {"LOW_DATA", "MIXED"}]
    write(
        OUT / "HUNDRED_NINETY_THIRD_20_MODE_FIELDS.tsv",
        candidate_fields,
        list(field_rows[0]),
    )

    summary_rows: list[dict[str, object]] = []
    for mode in sorted({row["field_frame_mode"] for row in field_rows}):
        selected = [row for row in field_rows if row["field_frame_mode"] == mode]
        summary_rows.append(
            {
                "field_frame_mode": mode,
                "mode_reading_de": MODE_READING.get(mode, "NICHT_FESTGELEGT"),
                "fields": len(selected),
                "events": sum(int(row["event_count"]) for row in selected),
                "diagnostic_events": sum(int(row["multi_surface_diagnostic_events"]) for row in selected),
                "mode_support_events": sum(int(row["mode_support_events"]) for row in selected),
                "closed_fields": sum(int(row["close_count"]) > 0 for row in selected),
                "pages": "|".join(sorted({str(row["page"]) for row in selected})),
                "field_ids": "|".join(str(row["field_id"]) for row in selected),
            }
        )
    write(OUT / "HUNDRED_NINETY_THIRD_MODE_SUMMARY.tsv", summary_rows)

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "field_source_sha256": hashlib.sha256(FIELDS.read_bytes()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(DICTIONARY.read_bytes()).hexdigest(),
        "events": len(event_rows),
        "fields": len(field_rows),
        "candidate_mode_fields": len(candidate_fields),
        "low_data_fields": sum(row["field_frame_mode"] == "LOW_DATA" for row in field_rows),
        "mixed_fields": sum(row["field_frame_mode"] == "MIXED" for row in field_rows),
        "mode_distribution": dict(Counter(str(row["field_frame_mode"]) for row in field_rows)),
        "candidate_diagnostic_events": sum(int(row["multi_surface_diagnostic_events"]) for row in candidate_fields),
        "candidate_mode_aligned_events": sum(int(row["mode_support_events"]) for row in candidate_fields),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
