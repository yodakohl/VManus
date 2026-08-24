#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle, delimiter="\t"))
    by_id = {row["event_id"]: row for row in events}

    cards = [
        {
            "event_id": "E001", "surface": by_id["E001"]["surface_display"], "joint_tuple_id": by_id["E001"]["joint_tuple_id"],
            "old_value_de": "Wurzelteil", "selected_value_de": "Knolle", "card_kind": "MEMORIZED_PICTURE_ADDRESSED_NOUN",
            "visual_anchor": "zwei rote geschlossene Endkörper am verzweigten unterirdischen Organ",
            "strongest_rival": "Wurzel", "why_selected": "the marked swelling is more distinctive than the whole rootstock",
        },
        {
            "event_id": "E002", "surface": by_id["E002"]["surface_display"], "joint_tuple_id": by_id["E002"]["joint_tuple_id"],
            "old_value_de": "säubern", "selected_value_de": "abschaben", "card_kind": "MEMORIZED_PREPARATION_VERB",
            "visual_anchor": "operation follows the selected underground swelling; no tool is drawn",
            "strongest_rival": "säubern", "why_selected": "separate CHOY and LSH cards already cover washing",
        },
    ]
    write("FOUR_HUNDRED_SIXTEENTH_TWO_OPENING_CARDS.tsv", cards)

    image = [
        {"feature": "WHOLE_PLANT", "visible": "YES", "interpretation": "silent page owner", "used_for_card": "NO"},
        {"feature": "FORKED_ROOTSTOCK", "visible": "YES", "interpretation": "underground part", "used_for_card": "DCHEY_RIVAL_ROOT"},
        {"feature": "TWO_RED_TERMINAL_SWELLINGS", "visible": "YES", "interpretation": "paired tuber/storage-organ candidates", "used_for_card": "DCHEY_SELECTED_KNOLLE"},
        {"feature": "WATER_OR_VESSEL", "visible": "NO", "interpretation": "later preparation is text-supplied", "used_for_card": "NONE"},
        {"feature": "SCRAPING_TOOL", "visible": "NO", "interpretation": "CTHOOR action is inferred from sequence", "used_for_card": "CTHOOR_CAUTION"},
    ]
    write("FOUR_HUNDRED_SIXTEENTH_F10_IMAGE_ANCHORS.tsv", image)

    operation_contrast = [
        {"card": "CTHOOR", "events": 1, "small_value_de": "abschaben", "object": "Knolle", "phase": "initial surface preparation"},
        {"card": "CHOY", "events": 1, "small_value_de": "waschen", "object": "local plant preparation", "phase": "explicit wash operation"},
        {"card": "LSH", "events": 3, "small_value_de": "waschen/spülen", "object": "running item", "phase": "Bio wash cycle"},
        {"card": "CHED", "events": 47, "small_value_de": "umsetzen", "object": "running item", "phase": "transfer"},
        {"card": "CHET", "events": 2, "small_value_de": "bearbeiten", "object": "material or charge", "phase": "general work"},
    ]
    write("FOUR_HUNDRED_SIXTEENTH_FIVE_PREPARATION_OPERATIONS.tsv", operation_contrast)

    values = ["Knolle", "abschaben", "aus demselben Vorrat", "bearbeiten", "Topf", "Wasserzulauf", "Auszug", "Posten ansetzen", "Sollmaß", "Gabe", "Posten ansetzen", "anwärmen", "fortsetzen", "bereit"]
    trace = []
    for index, value in enumerate(values, start=1):
        event_id = f"E{index:03d}"
        row = by_id[event_id]
        trace.append({"order": index, "event_id": event_id, "surface": row["surface_display"], "small_value_de": value, "statement_id": row["statement_id"]})
    write("FOUR_HUNDRED_SIXTEENTH_H1_FOURTEEN_CARD_READING.tsv", trace)

    summary = {
        "status": "PASS",
        "opening_cards": len(cards),
        "visual_anchors": len(image),
        "operation_contrasts": len(operation_contrast),
        "h1_events": len(trace),
        "decision": "DCHEY_TUBER__CTHOOR_SCRAPE",
    }
    (HERE / "FOUR_HUNDRED_SIXTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
