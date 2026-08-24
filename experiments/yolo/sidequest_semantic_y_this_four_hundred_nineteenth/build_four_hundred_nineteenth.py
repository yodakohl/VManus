#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
YPAR = ROOT / "experiments/yolo/sidequest_semantic_component_completion/Y_CHY_PARADIGM.tsv"
BASE_Y_ID = "b921a237be883a820352"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    ypar = read(YPAR)
    selected = [row for row in ypar if row["decision"].startswith("SELECTED")]
    by_statement: dict[str, list[dict[str, str]]] = {}
    for row in events:
        by_statement.setdefault(row["statement_id"], []).append(row)

    naked = []
    for row in events:
        if row["joint_tuple_id"] != BASE_Y_ID:
            continue
        sequence = by_statement[row["statement_id"]]
        index = [item["event_id"] for item in sequence].index(row["event_id"])
        prev = sequence[index - 1]["concrete_word_reading_de"] if index else "Aussagebeginn"
        nxt = sequence[index + 1]["concrete_word_reading_de"] if index + 1 < len(sequence) else "Aussageende"
        if row["event_id"] == "E170":
            behavior = "INHERITS_JUST_ADDED_PORTION"
            expansion = "diese Portion"
        elif row["event_id"] in {"E020", "E021", "E023"}:
            behavior = "ENUMERATES_ANONYMOUS_SPLIT_ITEMS"
            expansion = "dieser eine / dieser andere Posten"
        else:
            behavior = "INHERITS_OR_RECALLS_LOCAL_ITEM"
            expansion = "dies / dieser Posten"
        naked.append({
            "event_id": row["event_id"], "record": row["record_unit_id"], "statement_id": row["statement_id"],
            "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "preceding_value_de": prev, "following_value_de": nxt,
            "portable_value_de": "dies", "local_expansion_de": expansion, "referent_behavior": behavior,
        })
    write("FOUR_HUNDRED_NINETEENTH_EIGHTEEN_NAKED_Y.tsv", naked)

    families = Counter(row["candidate_family"] for row in selected)
    wrapper_values = {
        "BASE_Y_CARD": "dies",
        "OK_Y": "dies ansetzen",
        "OK_CHY": "dies ansetzen",
        "OK_E_Y": "dies kurz ansetzen",
        "OK_EE_Y": "dies länger ansetzen",
        "OT_EE_Y": "dies als Folge länger halten",
        "CHD_CHED_Y": "dies bearbeiten oder umsetzen",
        "CHED_CHY": "dies zuführen oder umsetzen",
        "OK_AL_Y": "dies an die Stelle setzen",
        "OK_OK_CHY": "dies erneut ansetzen",
        "OK_Y_LDDY": "dies befestigen; Schluss",
        "LCH_Y": "dies abziehen",
    }
    wrapper_rows = [
        {"candidate_family": family, "events": count, "y_contribution_de": "dies", "composed_value_de": wrapper_values[family]}
        for family, count in sorted(families.items())
    ]
    write("FOUR_HUNDRED_NINETEENTH_TWELVE_Y_WRAPPER_FAMILIES.tsv", wrapper_rows)

    b2_ids = ["E169", "E170", "E171"]
    b2_values = ["eine Portion zugeben", "dies", "länger ansetzen; Schluss"]
    by_id = {row["event_id"]: row for row in events}
    b2 = []
    for order, (event_id, value) in enumerate(zip(b2_ids, b2_values), start=1):
        row = by_id[event_id]
        b2.append({"order": order, "event_id": event_id, "surface": row["surface_display"], "small_value_de": value, "active_referent_after": "ADDED_PORTION"})
    write("FOUR_HUNDRED_NINETEENTH_B2_THREE_CARD_CELL.tsv", b2)

    models = [
        {"candidate": "WASSER", "cross_section_fit": 1, "wrapper_fit": 2, "split_pair_fit": 1, "score": 4, "decision": "REJECT"},
        {"candidate": "POSTEN", "cross_section_fit": 4, "wrapper_fit": 4, "split_pair_fit": 4, "score": 12, "decision": "KEEP_AS_EXPANSION"},
        {"candidate": "DIES", "cross_section_fit": 4, "wrapper_fit": 4, "split_pair_fit": 4, "score": 12, "decision": "SELECT_SHORTEST"},
        {"candidate": "AKTIV", "cross_section_fit": 3, "wrapper_fit": 2, "split_pair_fit": 2, "score": 7, "decision": "REJECT_PROPERTY_NOT_REFERENT"},
    ]
    write("FOUR_HUNDRED_NINETEENTH_FOUR_Y_MODELS.tsv", models)

    summary = {
        "status": "PASS", "naked_y_events": len(naked), "productive_y_chy_events": len(selected),
        "productive_wrapper_families": len(wrapper_rows), "b2_events": len(b2),
        "decision": "Y_CHY_DEICTIC_THIS_OR_CURRENT_ITEM", "small_value_de": "DIES",
    }
    (HERE / "FOUR_HUNDRED_NINETEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
