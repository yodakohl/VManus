#!/usr/bin/env python3
"""Integrate entry-frame choice with the existing exact surface renderer."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P558 = ROOT / "experiments/yolo/sidequest_semantic_surface_renderer_completion_five_hundred_fifty_eighth"
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P697 = ROOT / "experiments/yolo/sidequest_semantic_renderer_manual_six_hundred_ninety_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def entry_frame(renderer_pieces: str) -> str:
    for piece in renderer_pieces.split("|"):
        if piece.startswith("PREFIX:"):
            return piece.split(":", 1)[1]
    return "BARE"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    event_cards = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    plans = read(P697 / "SIX_HUNDRED_NINETY_SEVENTH_230_RENDERER_PLANS.tsv")
    old_renderer = read(P558 / "FIVE_HUNDRED_FIFTY_EIGHTH_THREE_HUNDRED_EIGHTY_ONE_SURFACE_RENDERER_LEDGER.tsv")
    context_rules = read(P558 / "FIVE_HUNDRED_FIFTY_EIGHTH_FOUR_CONTEXT_WRAPPER_RULES.tsv")
    residuals = read(P558 / "FIVE_HUNDRED_FIFTY_EIGHTH_FIFTY_NINE_RESIDUAL_LOCAL_ASSIGNMENTS.tsv")
    plan_by_card_surface = {(row["card_no"], row["surface"]): row for row in plans}
    renderer_by_event = {row["event_id"]: row for row in old_renderer}

    event_rows = []
    for event in event_cards:
        renderer = renderer_by_event[event["event_id"]]
        plan = plan_by_card_surface[(event["card_no"], event["surface"])]
        frame = entry_frame(plan["renderer_pieces"])
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "locus": renderer["locus"],
            "locus_position": renderer["locus_position"],
            "card_no": event["card_no"],
            "component_recipe": event["component_recipe"],
            "surface": event["surface"],
            "entry_frame": frame,
            "multi_surface_card": renderer["multi_surface_card"],
            "renderer_source": renderer["wrapper_assignment_source"],
            "global_first_choice": renderer["renderer_first_choice"],
            "remove_wrapper": renderer["remove_wrapper"],
            "apply_wrapper": renderer["applied_wrapper_stamp"],
            "residual_locus_mode": renderer["residual_locus_mode"],
            "selection_instruction_de": "Globale Kartenform kopieren." if renderer["wrapper_assignment_source"] == "GLOBAL_RULE_RENDERER" else ("Kurze Nachbar-/Positionsregel anwenden." if renderer["wrapper_assignment_source"] == "AUTOMATIC_CONTEXT_RULE" else "Lokalen Locusmodus aus dem Meisterexemplar verwenden."),
        })

    profiles = []
    by_record_position: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_record_position[(str(row["record"]), str(row["locus_position"]))].append(row)
    for (record, position), rows in by_record_position.items():
        counts = Counter(str(row["entry_frame"]) for row in rows)
        profiles.append({
            "record": record,
            "page": rows[0]["page"],
            "locus_position": position,
            "events": len(rows),
            "bare": counts["BARE"], "q": counts["q"], "s": counts["s"],
            "ch": counts["ch"], "d": counts["d"], "che": counts["che"],
            "t": counts["t"], "sh": counts["sh"], "c": counts["c"], "y": counts["y"],
            "observed_priority_de": " > ".join(frame for frame, _ in counts.most_common()),
        })

    position_rows = []
    advice = {
        "FIRST": "s ist der stärkste gebundene Anfangsrahmen; q/d/bare bleiben kartenspezifische Alternativen.",
        "MIDDLE": "bare und q dominieren; ch/che/c sind häufige innere Eintrittsallographen.",
        "LAST": "bare und d dominieren; das Locusende erzwingt dennoch keinen bestimmten Rahmen.",
    }
    for position in ["FIRST", "MIDDLE", "LAST"]:
        rows = [row for row in event_rows if row["locus_position"] == position]
        counts = Counter(str(row["entry_frame"]) for row in rows)
        position_rows.append({
            "locus_position": position,
            "events": len(rows),
            "frame_counts": " ".join(f"{frame}:{count}" for frame, count in counts.most_common()),
            "most_common_frame": counts.most_common(1)[0][0],
            "working_priority_de": advice[position],
            "hard_limit_de": "Position ist eine Präferenz, kein alleiniger Oberflächenschlüssel.",
        })

    mode_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in residuals:
        mode_groups[row["residual_locus_mode"]].append(row)
    mode_rows = []
    for mode, rows in sorted(mode_groups.items()):
        mode_rows.append({
            "residual_locus_mode": mode,
            "events": len(rows),
            "pages": "|".join(dict.fromkeys(row["page"] for row in rows)),
            "records": "|".join(dict.fromkeys(renderer_by_event[row["event_id"]]["record"] for row in rows)),
            "loci": "|".join(dict.fromkeys(row["locus"] for row in rows)),
            "card_numbers": " ".join(dict.fromkeys(row["card_no"] for row in rows)),
            "surface_choices": " ".join(dict.fromkeys(row["final_surface"] for row in rows)),
            "copy_rule_de": "Diesen Modus einmal am Locusanfang aus dem Meisterexemplar laden und innerhalb des gebundenen Pakets beibehalten.",
        })

    context_rows = []
    for row in context_rules:
        context_rows.append({
            "rule_id": row["rule_id"], "card_nos": row["card_nos"],
            "component_parses": row["component_parses"],
            "trigger_previous_procedure": row["trigger_previous_procedure"],
            "locus_positions": row["locus_positions"],
            "remove_wrapper": row["remove_wrapper"], "apply_wrapper": row["apply_wrapper"],
            "output_surfaces": row["output_surfaces"], "events": row["events"],
            "reading_de": "Reiner Wrapperwechsel; Komponentenbedeutung bleibt unverändert.",
        })

    write("SIX_HUNDRED_NINETY_EIGHTH_381_ENTRY_FRAME_EVENTS.tsv", event_rows)
    write("SIX_HUNDRED_NINETY_EIGHTH_RECORD_POSITION_PROFILES.tsv", profiles)
    write("SIX_HUNDRED_NINETY_EIGHTH_3_POSITION_PRIORITIES.tsv", position_rows)
    write("SIX_HUNDRED_NINETY_EIGHTH_4_CONTEXT_RULES.tsv", context_rows)
    write("SIX_HUNDRED_NINETY_EIGHTH_34_LOCAL_MODES.tsv", mode_rows)

    summary = {
        "status": "PASS",
        "events": len(event_rows),
        "single_surface_events": sum(row["multi_surface_card"] == "NO" for row in event_rows),
        "multi_surface_events": sum(row["multi_surface_card"] == "YES" for row in event_rows),
        "renderer_sources": dict(Counter(str(row["renderer_source"]) for row in event_rows)),
        "entry_frames": dict(Counter(str(row["entry_frame"]) for row in event_rows)),
        "locus_positions": dict(Counter(str(row["locus_position"]) for row in event_rows)),
        "context_rules": len(context_rows),
        "residual_local_events": len(residuals),
        "residual_locus_modes": len(mode_rows),
        "decision": "ENTRY_POSITION_BIASES_FRAME_BUT_EXACT_CHOICE_USES_GLOBAL_CONTEXT_OR_LOCAL_MODE",
    }
    (HERE / "SIX_HUNDRED_NINETY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
