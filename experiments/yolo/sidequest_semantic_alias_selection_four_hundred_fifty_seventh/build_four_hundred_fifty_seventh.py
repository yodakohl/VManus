#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_combined_prose_manual_four_hundred_fifty_sixth/FOUR_HUNDRED_FIFTY_SIXTH_381_EVENT_COMBINED_EDITION.tsv"
CARDS = ROOT / "experiments/yolo/sidequest_semantic_combined_prose_manual_four_hundred_fifty_sixth/FOUR_HUNDRED_FIFTY_SIXTH_173_CARD_COMBINED_DICTIONARY.tsv"
ALIASES = ROOT / "experiments/yolo/sidequest_semantic_combined_prose_manual_four_hundred_fifty_sixth/FOUR_HUNDRED_FIFTY_SIXTH_VALUE_ALIAS_FAMILIES.tsv"

IDS = {
    "ANSATZ_SHORT": "87411f84689b4f93a303", "ANSATZ_EXPANDED": "07913ef9b1fb773cd325",
    "AFTER_EXPANDED": "4de12cf322dfb76ded1e", "AFTER_SHORT": "601b77449028deed39de",
    "FILL_H1": "a6939862e33ece5a0483", "FILL_B1": "a7af89ab31ce5e247395",
    "WARM_DEFAULT": "2c1a5fd92b9e3c762242", "WARM_B2": "f0db6d30cd34f4cb2a4d",
    "MOVE_DEFAULT": "6f7ff8287eddf4da9fdb", "MOVE_BEFORE_TARGET": "5e8441397e7c0faf042b",
    "PORTION_FIRST": "403c1592f918c8f23b88", "PORTION_REPEAT": "d929a14ec45749b2e805",
    "CONTINUE_INSIDE": "dcda95c81a5460feb191", "CONTINUE_RESUME": "d665560c8ff80799a82c",
    "NEXT_H3": "a48efd6c4491a046ba78", "NEXT_DEFAULT": "faf321940aed922846a9",
    "CLOSE_EXPANDED": "259b2b3b0bf859882e2c", "CLOSE_SHORT": "d225b7a7b95da7aee437",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    cards = read(CARDS)
    alias_rows = read(ALIASES)
    alias_values = {row["small_value_de"] for row in alias_rows}
    cards_by_value: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        cards_by_value[row["small_value_de"]].append(row)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
        by_field[row["field_id"]].append(row)

    rule_rows = [
        {"value_de": "Ansatz umsetzen; Schluss", "selection_layer": "LOCAL_CONTEXT", "rule": "QOKCHDY at statement start; expanded OKCHEDY after prior action", "events": 5},
        {"value_de": "danach umsetzen; Schluss", "selection_layer": "RECORD_RENDERER", "rule": "short OTCHDY in B5; expanded OTCHEDY in B3", "events": 3},
        {"value_de": "dies kurz fuellen", "selection_layer": "RECORD_RENDERER", "rule": "ETYD in H1; YTEY in B1", "events": 2},
        {"value_de": "dies länger wärmen", "selection_layer": "RECORD_RENDERER", "rule": "CHKEEY in B2; CHEEKY in H4 and B4", "events": 3},
        {"value_de": "dies umsetzen", "selection_layer": "LOCAL_CONTEXT", "rule": "CHEDCHY immediately before AN DIE STELLE SETZEN; otherwise CHDY/CHEDY", "events": 12},
        {"value_de": "eine Portion davon zuführen", "selection_layer": "LOCAL_CONTEXT", "rule": "YKAN when immediately repeating the same portion instruction; otherwise YKAIN", "events": 2},
        {"value_de": "fortsetzen", "selection_layer": "STATEMENT_POSITION", "rule": "DCHOL/SCHOL for Herbal statement-entry resumption; normal OL card inside statement", "events": 21},
        {"value_de": "nächster Posten", "selection_layer": "RECORD_RENDERER", "rule": "QOTCHY in H3; OTCHEY in H5 and B4", "events": 3},
        {"value_de": "umsetzen; Schluss", "selection_layer": "LOCAL_CONTEXT", "rule": "short DCHDY only after KURZ FORTSETZEN; otherwise expanded DCHEDY", "events": 5},
    ]
    write("FOUR_HUNDRED_FIFTY_SEVENTH_NINE_ALIAS_RULES.tsv", rule_rows)

    def predict(row: dict[str, str], statement_pos: int, previous: dict[str, str] | None, following: dict[str, str] | None) -> tuple[str, str, str]:
        value = row["small_value_de"]
        if value not in alias_values:
            candidates = cards_by_value[value]
            if len(candidates) != 1:
                raise ValueError((value, len(candidates)))
            return candidates[0]["joint_tuple_id"], "UNIQUE_VALUE", "only exact card with this small value"
        if value == "Ansatz umsetzen; Schluss":
            return (IDS["ANSATZ_SHORT"] if statement_pos == 1 else IDS["ANSATZ_EXPANDED"], "LOCAL_CONTEXT", "statement start selects short card")
        if value == "danach umsetzen; Schluss":
            return (IDS["AFTER_SHORT"] if row["record_unit_id"] == "B5" else IDS["AFTER_EXPANDED"], "RECORD_RENDERER", "B5 uses contracted renderer")
        if value == "dies kurz fuellen":
            return (IDS["FILL_H1"] if row["record_unit_id"] == "H1" else IDS["FILL_B1"], "RECORD_RENDERER", "H1 and B1 order the same atoms differently")
        if value == "dies länger wärmen":
            return (IDS["WARM_B2"] if row["record_unit_id"] == "B2" else IDS["WARM_DEFAULT"], "RECORD_RENDERER", "B2 uses CHK-EE order")
        if value == "dies umsetzen":
            return (IDS["MOVE_BEFORE_TARGET"] if following and following["small_value_de"] == "an die Stelle setzen" else IDS["MOVE_DEFAULT"], "LOCAL_CONTEXT", "target-setting follower selects expanded current-item form")
        if value == "eine Portion davon zuführen":
            return (IDS["PORTION_REPEAT"] if previous and previous["small_value_de"] == value else IDS["PORTION_FIRST"], "LOCAL_CONTEXT", "second immediately repeated portion contracts")
        if value == "fortsetzen":
            return (IDS["CONTINUE_RESUME"] if row["register"] == "HERBAL" and statement_pos == 1 else IDS["CONTINUE_INSIDE"], "STATEMENT_POSITION", "Herbal statement entry uses resumption card")
        if value == "nächster Posten":
            return (IDS["NEXT_H3"] if row["record_unit_id"] == "H3" else IDS["NEXT_DEFAULT"], "RECORD_RENDERER", "H3 uses QOTCHY renderer")
        if value == "umsetzen; Schluss":
            return (IDS["CLOSE_SHORT"] if previous and previous["small_value_de"] == "kurz fortsetzen" else IDS["CLOSE_EXPANDED"], "LOCAL_CONTEXT", "short continuation licenses short close card")
        raise ValueError(value)

    output_events = []
    alias_audit = []
    for row in events:
        statement = by_statement[row["statement_id"]]
        statement_pos = statement.index(row) + 1
        previous = statement[statement_pos - 2] if statement_pos > 1 else None
        following = statement[statement_pos] if statement_pos < len(statement) else None
        prediction, layer, reason = predict(row, statement_pos, previous, following)
        out = dict(row)
        out.update({
            "statement_position": statement_pos, "field_position": by_field[row["field_id"]].index(row) + 1,
            "previous_value_de": previous["small_value_de"] if previous else "STATEMENT_START",
            "next_value_de": following["small_value_de"] if following else "STATEMENT_END",
            "selection_layer": layer, "selection_reason": reason,
            "predicted_joint_tuple_id": prediction,
            "exact_card_recovered": "YES" if prediction == row["joint_tuple_id"] else "NO",
        })
        output_events.append(out)
        if row["small_value_de"] in alias_values:
            alias_audit.append({
                "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "statement_id": row["statement_id"],
                "statement_position": statement_pos, "surface": row["surface"], "small_value_de": row["small_value_de"],
                "previous_value_de": out["previous_value_de"], "next_value_de": out["next_value_de"],
                "selection_layer": layer, "selection_reason": reason,
                "expected_joint_tuple_id": row["joint_tuple_id"], "predicted_joint_tuple_id": prediction,
                "recovered": out["exact_card_recovered"],
            })
    write("FOUR_HUNDRED_FIFTY_SEVENTH_381_EVENT_REVERSE_SELECTION.tsv", output_events)
    write("FOUR_HUNDRED_FIFTY_SEVENTH_56_ALIAS_OCCURRENCE_AUDIT.tsv", alias_audit)

    updated_cards = []
    for row in cards:
        out = dict(row)
        if row["small_value_de"] in alias_values:
            rule = next(item for item in rule_rows if item["value_de"] == row["small_value_de"])
            out["exact_selection_layer"] = rule["selection_layer"]
            out["exact_selection_rule"] = rule["rule"]
        else:
            out["exact_selection_layer"] = "UNIQUE_VALUE"
            out["exact_selection_rule"] = "write the only card carrying this value"
        updated_cards.append(out)
    write("FOUR_HUNDRED_FIFTY_SEVENTH_173_CARD_DICTIONARY_WITH_SELECTION.tsv", updated_cards)

    summary = {
        "status": "PASS", "events": len(output_events), "alias_families": len(rule_rows), "alias_events": len(alias_audit),
        "unique_value_events": sum(row["selection_layer"] == "UNIQUE_VALUE" for row in output_events),
        "local_context_events": sum(row["selection_layer"] == "LOCAL_CONTEXT" for row in output_events),
        "statement_position_events": sum(row["selection_layer"] == "STATEMENT_POSITION" for row in output_events),
        "record_renderer_events": sum(row["selection_layer"] == "RECORD_RENDERER" for row in output_events),
        "exact_cards_recovered": sum(row["exact_card_recovered"] == "YES" for row in output_events),
    }
    (HERE / "FOUR_HUNDRED_FIFTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
