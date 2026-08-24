#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P519 = ROOT / "experiments/yolo/sidequest_semantic_owner_initialization_five_hundred_nineteenth"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71/V71_R3_OWNER_LEDGER.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read_tsv(P519 / "FIVE_HUNDRED_NINETEENTH_381_OWNER_AWARE_MASTER_LOG.tsv")
    transitions = read_tsv(P519 / "FIVE_HUNDRED_NINETEENTH_21_OWNER_TRANSITIONS.tsv")
    owner_ledger = read_tsv(V71)
    ledger_by_event: dict[str, dict[str, str]] = {}
    for row in owner_ledger:
        if row["source_level"] != "PROSE_FIELD":
            continue
        for member in row["member_ids"].split("|"):
            ledger_by_event[f"E{int(member):03d}"] = row

    cue_for_event = {
        "E189": "NEW_DISCONNECTED_DEVICE",
        "E198": "VISIBLE_REGION_GAP",
        "E203": "ENTER_LARGE_SHARED_POOL",
        "E212": "ENTER_POOL_EDGE_STATION_SET",
        "E239": "NEXT_SEPARATE_MARGIN_VESSEL",
        "E248": "NEXT_SEPARATE_MARGIN_VESSEL",
        "E264": "VISIBLE_REGION_GAP",
        "E291": "ENTER_VISIBLE_LINKED_PAIR",
        "E338": "ENTER_LEFT_OPEN_FRINGE_STATION",
        "E356": "ENTER_RIGHT_S_RUN_MULTIPORT_STATION",
    }
    internal = [row for row in transitions if row["master_decision"] == "YES"]
    cue_rows: list[dict[str, str]] = []
    for row in internal:
        ledger = ledger_by_event[row["event_id"]]
        status = ledger["ownership_status"]
        cue_rows.append(
            {
                "cue_no": str(len(cue_rows) + 1),
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "record": row["record"],
                "page": row["page"],
                "locus": row["locus"],
                "visual_trigger_class": cue_for_event[row["event_id"]],
                "visible_geometric_basis": ledger["visible_geometric_basis"],
                "owner_code_after_threshold": row["owner_code"],
                "ownership_status": status,
                "automatic_action": (
                    "RESET_TO_VISIBLE_LOCAL_OWNER"
                    if status == "DIRECT_VISIBLE"
                    else "RESET_TO_LOCAL_OWNER_SLOT_AND_COPY_EXEMPLAR_BINDING"
                ),
                "free_master_choice": "NO",
                "instruction_de": (
                    "An der neuen sichtbaren Station den lokalen Besitzer automatisch laden."
                    if status == "DIRECT_VISIBLE"
                    else "An der sichtbaren Lücke die alte Vererbung beenden; lokale Bindung aus dem Seitenexemplar übernehmen."
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTIETH_TEN_VISIBLE_OWNER_THRESHOLDS.tsv", cue_rows)

    cue_by_event = {row["event_id"]: row for row in cue_rows}
    output: list[dict[str, str]] = []
    decisions: list[dict[str, str]] = []
    for row in source:
        cue = cue_by_event.get(row["event_id"])
        owner_rule = row["owner_handling_mode"]
        if cue:
            owner_rule = cue["automatic_action"]
        reasons: list[str] = []
        if row["block_start_decision"] == "YES":
            reasons.append("ENTER_ALLOGRAPH_BLOCK")
            decisions.append(
                {
                    "decision_no": "",
                    "event_id": row["event_id"],
                    "statement_id": row["statement_id"],
                    "record": row["record"],
                    "page": row["page"],
                    "decision_type": "ENTER_ALLOGRAPH_BLOCK",
                    "selected_value": row["allograph_block_id"],
                }
            )
        output.append(
            {
                **row,
                "visual_owner_threshold": cue["visual_trigger_class"] if cue else "NONE",
                "owner_threshold_rule": owner_rule,
                "free_owner_choice": "NO",
                "threshold_conscious_decision_count": str(len(reasons)),
                "threshold_conscious_reasons": "|".join(reasons) if reasons else "NONE",
                "threshold_master_mode": "CONSCIOUS_LOCAL_CHOICE" if reasons else "AUTOMATIC_FLOW",
            }
        )
    for number, row in enumerate(decisions, 1):
        row["decision_no"] = str(number)
    write_tsv("FIVE_HUNDRED_TWENTIETH_381_THRESHOLD_MASTER_LOG.tsv", output)
    write_tsv("FIVE_HUNDRED_TWENTIETH_FIFTY_CONSCIOUS_DECISIONS.tsv", decisions)

    grammar_rows = [
        {
            "rule_no": "1",
            "condition": "FIRST_EVENT_OF_RECORD",
            "action": "LOAD_VISIBLE_RECORD_OWNER",
            "master_choice": "NO",
            "teaching_de": "Am Recordanfang den sichtbaren Hauptbesitzer laden.",
        },
        {
            "rule_no": "2",
            "condition": "NEW_DISCONNECTED_VISIBLE_STATION_OR_REGION",
            "action": "RESET_TO_VISIBLE_LOCAL_OWNER",
            "master_choice": "NO",
            "teaching_de": "Beginnt eine getrennte Station, endet die alte Besitzervererbung.",
        },
        {
            "rule_no": "3",
            "condition": "VISIBLE_GAP_WITH_AMBIGUOUS_TARGET",
            "action": "RESET_AND_COPY_LOCAL_EXEMPLAR_BINDING",
            "master_choice": "NO",
            "teaching_de": "Bei einer Bildlücke nicht raten: zurücksetzen und die lokale Exemplarbindung kopieren.",
        },
        {
            "rule_no": "4",
            "condition": "NO_THRESHOLD",
            "action": "INHERIT_CURRENT_OWNER",
            "master_choice": "NO",
            "teaching_de": "Ohne neue sichtbare Schwelle den laufenden Besitzer behalten.",
        },
    ]
    write_tsv("FIVE_HUNDRED_TWENTIETH_FOUR_OWNER_THRESHOLD_RULES.tsv", grammar_rows)

    summary = {
        "status": "PASS",
        "events": len(output),
        "visible_internal_thresholds": len(cue_rows),
        "direct_visible_thresholds": sum(row["ownership_status"] == "DIRECT_VISIBLE" for row in cue_rows),
        "ambiguous_gap_thresholds": sum(row["ownership_status"] == "UNRESOLVED" for row in cue_rows),
        "free_owner_choices": 0,
        "remaining_decision_instances": len(decisions),
        "remaining_conscious_events": sum(row["threshold_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in output),
        "automatic_events": sum(row["threshold_master_mode"] == "AUTOMATIC_FLOW" for row in output),
        "cue_classes": dict(Counter(row["visual_trigger_class"] for row in cue_rows)),
    }
    (HERE / "FIVE_HUNDRED_TWENTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
