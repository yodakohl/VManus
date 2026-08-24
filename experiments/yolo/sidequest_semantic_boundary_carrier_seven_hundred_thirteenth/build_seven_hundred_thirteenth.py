#!/usr/bin/env python3
"""Build Pass 713: shared boundary-carrier rule for four same-owner doublets."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P698 = ROOT / "experiments/yolo/sidequest_semantic_entry_frame_selection_six_hundred_ninety_eighth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


FAMILIES = {
    "OK+Y": {"plain": "PROC008", "marked": "PROC011", "marked_device": "ITEM_CARRIER_CH"},
    "CHD+Y": {"plain": "PROC042", "marked": "PROC133", "marked_device": "ITEM_CARRIER_CH"},
    "CHD+DY": {"plain": "PROC094", "marked": "PROC076", "marked_device": "CHD_E_JOINT"},
    "OK+CHD+DY": {"plain": "PROC082", "marked": "PROC091", "marked_device": "CHD_E_JOINT"},
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    statements = read(P700 / "SEVEN_HUNDREDTH_116_STATEMENT_EDITION.tsv")
    entry = read(P698 / "SIX_HUNDRED_NINETY_EIGHTH_381_ENTRY_FRAME_EVENTS.tsv")
    entry_by_event = {row["event_id"]: row for row in entry}
    statement_by_id = {row["statement_id"]: row for row in statements}
    statement_events: dict[str, list[str]] = defaultdict(list)
    for event in events:
        statement_events[event["statement_id"]].append(event["event_id"])

    target_ids = {info[key] for info in FAMILIES.values() for key in ("plain", "marked")}
    rows = []
    for event in events:
        if event["card_no"] not in target_ids:
            continue
        recipe = event["component_recipe"]
        info = FAMILIES[recipe]
        observed_variant = "MARKED_CARRIER" if event["card_no"] == info["marked"] else "PLAIN"
        position = entry_by_event[event["event_id"]]["locus_position"]
        predicted_variant = "MARKED_CARRIER" if position == "FIRST" else "PLAIN"
        ids = statement_events[event["statement_id"]]
        statement_position = "ONLY" if len(ids) == 1 else "FIRST" if ids[0] == event["event_id"] else "LAST" if ids[-1] == event["event_id"] else "MIDDLE"
        rows.append({
            "event_id": event["event_id"], "page": event["page"], "record": event["record"],
            "statement_id": event["statement_id"], "locus": event["locus"], "owner_de": event["owner_de"],
            "component_recipe": recipe, "marked_device": info["marked_device"],
            "observed_card": event["card_no"], "observed_surface": event["observed_surface"],
            "observed_variant": observed_variant, "locus_position": position,
            "statement_position": statement_position, "statement_events": statement_by_id[event["statement_id"]]["events"],
            "entry_frame": event["entry_frame"],
            "boundary_prior_prediction": predicted_variant,
            "boundary_prior_correct": "YES" if predicted_variant == observed_variant else "NO",
            "copy_instruction_de": "Am Locusanfang Traeger/Gelenkform bevorzugen; sonst schlichte Form; Ausnahmezettel hat Vorrang.",
        })

    family_rows = []
    for recipe, info in FAMILIES.items():
        subset = [row for row in rows if row["component_recipe"] == recipe]
        family_rows.append({
            "component_recipe": recipe, "plain_card": info["plain"], "marked_card": info["marked"],
            "marked_device": info["marked_device"], "events": len(subset),
            "plain_events": sum(row["observed_variant"] == "PLAIN" for row in subset),
            "marked_events": sum(row["observed_variant"] == "MARKED_CARRIER" for row in subset),
            "locus_first_events": sum(row["locus_position"] == "FIRST" for row in subset),
            "boundary_prior_correct": sum(row["boundary_prior_correct"] == "YES" for row in subset),
            "semantic_decision": "ONE_RECIPE__NO_MEANING_SPLIT",
            "copy_decision": "BOUNDARY_CARRIER_PRIOR_PLUS_LOCAL_OVERRIDE",
        })

    marked = sum(row["observed_variant"] == "MARKED_CARRIER" for row in rows)
    plain = len(rows) - marked
    first_marked = sum(row["locus_position"] == "FIRST" and row["observed_variant"] == "MARKED_CARRIER" for row in rows)
    first_plain = sum(row["locus_position"] == "FIRST" and row["observed_variant"] == "PLAIN" for row in rows)
    nonfirst_marked = sum(row["locus_position"] != "FIRST" and row["observed_variant"] == "MARKED_CARRIER" for row in rows)
    nonfirst_plain = sum(row["locus_position"] != "FIRST" and row["observed_variant"] == "PLAIN" for row in rows)
    statement_entry_correct = sum((row["statement_position"] in {"FIRST", "ONLY"}) == (row["observed_variant"] == "MARKED_CARRIER") for row in rows)
    q_prior_correct = sum((row["entry_frame"] == "q") == (row["observed_variant"] == "MARKED_CARRIER") for row in rows)
    model_rows = [
        {"model": "ALL_PLAIN", "correct": plain, "errors": marked, "rule_de": "Immer schlichte Unterkarte."},
        {"model": "ALL_MARKED", "correct": marked, "errors": plain, "rule_de": "Immer Traeger-/Gelenkunterkarte."},
        {"model": "STATEMENT_ENTRY_MARKED", "correct": statement_entry_correct, "errors": len(rows) - statement_entry_correct, "rule_de": "Am Statementanfang markiert, sonst schlicht."},
        {"model": "Q_FRAME_MARKED", "correct": q_prior_correct, "errors": len(rows) - q_prior_correct, "rule_de": "Bei q-Rahmen markiert, sonst schlicht."},
        {"model": "LOCUS_FIRST_MARKED", "correct": first_marked + nonfirst_plain, "errors": first_plain + nonfirst_marked, "rule_de": "Am Locusanfang markiert, sonst schlicht."},
        {"model": "EXACT_EXEMPLAR", "correct": len(rows), "errors": 0, "rule_de": "Exakte Unterkarte aus Exemplar kopieren."},
    ]

    overrides = []
    for row in rows:
        if row["boundary_prior_correct"] == "YES":
            continue
        overrides.append({
            "override_id": f"BCO{len(overrides) + 1:02d}", "event_id": row["event_id"],
            "component_recipe": row["component_recipe"], "locus": row["locus"], "owner_de": row["owner_de"],
            "locus_position": row["locus_position"], "default_prediction": row["boundary_prior_prediction"],
            "required_variant": row["observed_variant"], "required_card": row["observed_card"],
            "required_surface": row["observed_surface"],
            "master_note_de": "Lokale Unterkarte kopieren; keine neue Bedeutung ansetzen.",
        })

    write("SEVEN_HUNDRED_THIRTEENTH_35_BOUNDARY_CARRIER_EVENTS.tsv", rows)
    write("SEVEN_HUNDRED_THIRTEENTH_4_FAMILY_RULES.tsv", family_rows)
    write("SEVEN_HUNDRED_THIRTEENTH_6_MODEL_COMPARISON.tsv", model_rows)
    write("SEVEN_HUNDRED_THIRTEENTH_5_OVERRIDE_SLIPS.tsv", overrides)

    summary = {
        "status": "PASS", "families": len(family_rows), "events": len(rows),
        "marked_events": marked, "plain_events": plain,
        "locus_first_marked": first_marked, "locus_first_plain": first_plain,
        "nonfirst_marked": nonfirst_marked, "nonfirst_plain": nonfirst_plain,
        "boundary_prior_correct": first_marked + nonfirst_plain,
        "boundary_prior_errors": first_plain + nonfirst_marked,
        "override_slips": len(overrides), "semantic_splits": 0,
        "decision": "FOUR_SAME_OWNER_DOUBLETS_SHARE_A_LOCUS_BOUNDARY_CARRIER_PRIOR_WITH_FIVE_OVERRIDES",
    }
    (HERE / "SEVEN_HUNDRED_THIRTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
