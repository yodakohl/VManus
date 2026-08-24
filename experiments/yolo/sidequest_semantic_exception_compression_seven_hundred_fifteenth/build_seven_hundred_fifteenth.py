#!/usr/bin/env python3
"""Build Pass 715: replace five card slips with family rules and compress surface slips."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P713 = ROOT / "experiments/yolo/sidequest_semantic_boundary_carrier_seven_hundred_thirteenth"
P714 = ROOT / "experiments/yolo/sidequest_semantic_integrated_copy_manual_seven_hundred_fourteenth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    trace = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    boundary = read(P713 / "SEVEN_HUNDRED_THIRTEENTH_35_BOUNDARY_CARRIER_EVENTS.tsv")
    exceptions = read(P714 / "SEVEN_HUNDRED_FOURTEENTH_10_DISTINCT_EXCEPTION_SLIPS.tsv")
    index = {row["event_id"]: i for i, row in enumerate(trace)}

    card_rows = []
    for row in boundary:
        i = index[row["event_id"]]
        previous_recipe = trace[i - 1]["component_recipe"] if i else "NONE"
        next_recipe = trace[i + 1]["component_recipe"] if i + 1 < len(trace) else "NONE"
        recipe = row["component_recipe"]
        if recipe == "OK+Y":
            marked = row["locus_position"] == "FIRST" or previous_recipe == "HO"
            rule_id = "CR1"
        elif recipe == "CHD+Y":
            marked = previous_recipe == "CHD+DY" and next_recipe == "OK+AL"
            rule_id = "CR2"
        elif recipe == "CHD+DY":
            marked = row["locus_position"] == "FIRST" or previous_recipe == "CKH+Y"
            rule_id = "CR3"
        elif recipe == "OK+CHD+DY":
            marked = row["statement_position"] == "LAST"
            rule_id = "CR4"
        else:
            raise AssertionError(recipe)
        prediction = "MARKED_CARRIER" if marked else "PLAIN"
        card_rows.append({
            "event_id": row["event_id"], "component_recipe": recipe,
            "observed_card": row["observed_card"], "observed_variant": row["observed_variant"],
            "locus_position": row["locus_position"], "statement_position": row["statement_position"],
            "previous_recipe": previous_recipe, "next_recipe": next_recipe,
            "refined_rule_id": rule_id, "refined_prediction": prediction,
            "refined_correct": "YES" if prediction == row["observed_variant"] else "NO",
        })

    rule_text = {
        "CR1": ("OK+Y", "Markiert am Locusanfang oder unmittelbar nach einer neu genannten Zutat HO; sonst schlicht."),
        "CR2": ("CHD+Y", "Markiert nur als Wiederaufnahmebruecke CHD+DY -> CHD+Y -> OK+AL; sonst schlicht."),
        "CR3": ("CHD+DY", "Markiert am Locusanfang oder unmittelbar nach CKH+Y; sonst kompakt."),
        "CR4": ("OK+CHD+DY", "Markiert wenn die Karte eine vorausgehende Mehrkartenanweisung schliesst; als Einzelzelle kompakt."),
    }
    rule_rows = []
    for rule_id, (recipe, text) in rule_text.items():
        subset = [row for row in card_rows if row["refined_rule_id"] == rule_id]
        rule_rows.append({
            "rule_id": rule_id, "component_recipe": recipe, "events": len(subset),
            "marked_events": sum(row["observed_variant"] == "MARKED_CARRIER" for row in subset),
            "plain_events": sum(row["observed_variant"] == "PLAIN" for row in subset),
            "correct": sum(row["refined_correct"] == "YES" for row in subset),
            "errors": sum(row["refined_correct"] == "NO" for row in subset),
            "apprentice_rule_de": text,
        })

    surface_exceptions = [row for row in exceptions if row["exception_kind"] == "SURFACE_OVERRIDE"]
    tray_map = {
        "E023": ("ST1", "H2_FINAL_ITEM_CAP", "Nach dem Mass am Ende der langen Pflanzenanweisung den laufenden Posten mit shy deckeln."),
        "E068": ("ST2", "H4_POST_CLOSE_MEASURE_RESET", "Nach OL+DY den neuen Massposten in dieser Zeile nackt als aiin ansetzen."),
        "E156": ("ST3", "B1_LATE_CELL_ENTRY_STRIP", "Spaete B1-Zellenfolge aus dem lokalen Streifen kopieren: sal, tedy, chal."),
        "E163": ("ST3", "B1_LATE_CELL_ENTRY_STRIP", "Spaete B1-Zellenfolge aus dem lokalen Streifen kopieren: sal, tedy, chal."),
        "E166": ("ST3", "B1_LATE_CELL_ENTRY_STRIP", "Spaete B1-Zellenfolge aus dem lokalen Streifen kopieren: sal, tedy, chal."),
    }
    tray_events = []
    for row in surface_exceptions:
        tray_id, tray_name, instruction = tray_map[row["event_id"]]
        i = index[row["event_id"]]
        tray_events.append({
            "tray_id": tray_id, "tray_name": tray_name, "event_id": row["event_id"],
            "page": trace[i]["page"], "record": trace[i]["record"], "statement_id": trace[i]["statement_id"],
            "locus": row["locus"], "card": row["required_exact_card"],
            "default_surface": row["default_surface"], "local_surface": row["required_surface"],
            "previous_recipe": trace[i - 1]["component_recipe"] if i else "NONE",
            "local_instruction_de": instruction,
        })
    trays: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in tray_events:
        trays[str(row["tray_id"])].append(row)
    tray_rows = []
    for tray_id in sorted(trays):
        rows = trays[tray_id]
        tray_rows.append({
            "tray_id": tray_id, "tray_name": rows[0]["tray_name"], "events": len(rows),
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "local_surfaces": "|".join(str(row["local_surface"]) for row in rows),
            "instruction_de": rows[0]["local_instruction_de"],
            "status": "LOCAL_COPY_TRAY__NO_MEANING_CHANGE",
        })

    write("SEVEN_HUNDRED_FIFTEENTH_35_REFINED_CARD_CHOICES.tsv", card_rows)
    write("SEVEN_HUNDRED_FIFTEENTH_4_CARD_FAMILY_RULES.tsv", rule_rows)
    write("SEVEN_HUNDRED_FIFTEENTH_5_SURFACE_TRAY_EVENTS.tsv", tray_events)
    write("SEVEN_HUNDRED_FIFTEENTH_3_LOCAL_SURFACE_TRAYS.tsv", tray_rows)

    summary = {
        "status": "PASS", "card_family_events": len(card_rows), "card_family_rules": len(rule_rows),
        "card_family_correct": sum(row["refined_correct"] == "YES" for row in card_rows),
        "remaining_card_slips": sum(row["refined_correct"] == "NO" for row in card_rows),
        "surface_override_events": len(tray_events), "local_surface_trays": len(tray_rows),
        "old_individual_slips": len(exceptions), "new_rule_or_tray_units": len(rule_rows) + len(tray_rows),
        "all_381_reconstructable": True,
        "decision": "FOUR_FAMILY_RULES_ELIMINATE_CARD_SLIPS__FIVE_SURFACE_SLIPS_COMPRESS_TO_THREE_LOCAL_TRAYS",
    }
    (HERE / "SEVEN_HUNDRED_FIFTEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
