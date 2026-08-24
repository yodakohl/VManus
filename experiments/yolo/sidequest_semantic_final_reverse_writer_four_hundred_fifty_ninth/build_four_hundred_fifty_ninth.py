#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_whole_card_reduction_four_hundred_fifty_eighth/FOUR_HUNDRED_FIFTY_EIGHTH_381_EVENT_REVISED_EDITION.tsv"
CARDS = ROOT / "experiments/yolo/sidequest_semantic_whole_card_reduction_four_hundred_fifty_eighth/FOUR_HUNDRED_FIFTY_EIGHTH_173_CARD_REVISED_DICTIONARY.tsv"
ALIASES = ROOT / "experiments/yolo/sidequest_semantic_whole_card_reduction_four_hundred_fifty_eighth/FOUR_HUNDRED_FIFTY_EIGHTH_ELEVEN_ALIAS_FAMILIES.tsv"

ID = {
    "ANSATZ_SHORT": "87411f84689b4f93a303", "ANSATZ_LONG": "07913ef9b1fb773cd325",
    "AFTER_LONG": "4de12cf322dfb76ded1e", "AFTER_SHORT": "601b77449028deed39de",
    "FILL_H1": "a6939862e33ece5a0483", "FILL_B1": "a7af89ab31ce5e247395",
    "SUPPLY_H5": "b74e9e65637b7c8538dd", "SUPPLY_B6": "43eb9aa12959b4d5cdc9",
    "WARM_DEFAULT": "2c1a5fd92b9e3c762242", "WARM_B2": "f0db6d30cd34f4cb2a4d",
    "MOVE_DEFAULT": "6f7ff8287eddf4da9fdb", "MOVE_TARGET": "5e8441397e7c0faf042b",
    "PORTION_FIRST": "403c1592f918c8f23b88", "PORTION_REPEAT": "d929a14ec45749b2e805",
    "CONTINUE_INSIDE": "dcda95c81a5460feb191", "CONTINUE_RESUME": "d665560c8ff80799a82c",
    "NEXT_H3": "a48efd6c4491a046ba78", "NEXT_DEFAULT": "faf321940aed922846a9",
    "CLOSE_LONG": "259b2b3b0bf859882e2c", "CLOSE_SHORT": "d225b7a7b95da7aee437",
    "LEAD_B1": "0f18de177ed7c878bf95", "LEAD_B5": "8c97dfde96fbc78e3355",
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
    alias_values = {row["small_value_de"] for row in read(ALIASES)}
    by_value: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cards:
        by_value[row["small_value_de"]].append(row)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    rules = [
        ("Ansatz umsetzen; Schluss", "LOCAL_CONTEXT", "short QOKCHDY at statement entry; expanded OKCHEDY after prior action", 5),
        ("danach umsetzen; Schluss", "RECORD_RENDERER", "short OTCHDY in B5; expanded OTCHEDY in B3", 3),
        ("dies kurz fuellen", "RECORD_RENDERER", "ETYD in H1; YTEY in B1", 2),
        ("dies kurz zuführen", "RECORD_RENDERER", "KCHEY in H5; QEKY in B6", 2),
        ("dies länger wärmen", "RECORD_RENDERER", "CHKEEY in B2; CHEEKY in H4 and B4", 3),
        ("dies umsetzen", "LOCAL_CONTEXT", "CHEDCHY before target-setting; otherwise CHDY/CHEDY", 12),
        ("eine Portion davon zuführen", "LOCAL_CONTEXT", "contract to YKAN on immediate repetition; otherwise YKAIN", 2),
        ("fortsetzen", "STATEMENT_POSITION", "DCHOL/SCHOL for Herbal statement-entry resumption; ordinary OL inside", 21),
        ("nächster Posten", "RECORD_RENDERER", "QOTCHY in H3; OTCHEY in H5 and B4", 3),
        ("umsetzen; Schluss", "LOCAL_CONTEXT", "short DCHDY after KURZ FORTSETZEN; otherwise expanded DCHEDY", 5),
        ("weiterfuehren", "RECORD_RENDERER", "DL in B1; LOL in B5", 3),
    ]
    rule_rows = [{"value_de": value, "selection_layer": layer, "rule": rule, "events": count} for value, layer, rule, count in rules]
    write("FOUR_HUNDRED_FIFTY_NINTH_ELEVEN_EXACT_SELECTION_RULES.tsv", rule_rows)

    def predict(row: dict[str, str], pos: int, prev: dict[str, str] | None, nxt: dict[str, str] | None) -> tuple[str, str, str]:
        value = row["small_value_de"]
        if value not in alias_values:
            candidate = by_value[value]
            if len(candidate) != 1:
                raise ValueError((value, len(candidate)))
            return candidate[0]["joint_tuple_id"], "UNIQUE_VALUE", "only card with value"
        if value == "Ansatz umsetzen; Schluss":
            return (ID["ANSATZ_SHORT"] if pos == 1 else ID["ANSATZ_LONG"], "LOCAL_CONTEXT", "statement entry")
        if value == "danach umsetzen; Schluss":
            return (ID["AFTER_SHORT"] if row["record_unit_id"] == "B5" else ID["AFTER_LONG"], "RECORD_RENDERER", "B5 contraction")
        if value == "dies kurz fuellen":
            return (ID["FILL_H1"] if row["record_unit_id"] == "H1" else ID["FILL_B1"], "RECORD_RENDERER", "H1/B1 atom order")
        if value == "dies kurz zuführen":
            return (ID["SUPPLY_B6"] if row["record_unit_id"] == "B6" else ID["SUPPLY_H5"], "RECORD_RENDERER", "H5/B6 atom order")
        if value == "dies länger wärmen":
            return (ID["WARM_B2"] if row["record_unit_id"] == "B2" else ID["WARM_DEFAULT"], "RECORD_RENDERER", "B2 CHK-EE order")
        if value == "dies umsetzen":
            return (ID["MOVE_TARGET"] if nxt and nxt["small_value_de"] == "an die Stelle setzen" else ID["MOVE_DEFAULT"], "LOCAL_CONTEXT", "target follower")
        if value == "eine Portion davon zuführen":
            return (ID["PORTION_REPEAT"] if prev and prev["small_value_de"] == value else ID["PORTION_FIRST"], "LOCAL_CONTEXT", "immediate repetition")
        if value == "fortsetzen":
            return (ID["CONTINUE_RESUME"] if row["register"] == "HERBAL" and pos == 1 else ID["CONTINUE_INSIDE"], "STATEMENT_POSITION", "entry resumption")
        if value == "nächster Posten":
            return (ID["NEXT_H3"] if row["record_unit_id"] == "H3" else ID["NEXT_DEFAULT"], "RECORD_RENDERER", "H3 allograph")
        if value == "umsetzen; Schluss":
            return (ID["CLOSE_SHORT"] if prev and prev["small_value_de"] == "kurz fortsetzen" else ID["CLOSE_LONG"], "LOCAL_CONTEXT", "short predecessor")
        if value == "weiterfuehren":
            return (ID["LEAD_B5"] if row["record_unit_id"] == "B5" else ID["LEAD_B1"], "RECORD_RENDERER", "B5 L+OL allograph")
        raise ValueError(value)

    outputs = []
    alias_audit = []
    for row in events:
        statement = by_statement[row["statement_id"]]
        pos = statement.index(row) + 1
        prev = statement[pos - 2] if pos > 1 else None
        nxt = statement[pos] if pos < len(statement) else None
        expected, layer, reason = predict(row, pos, prev, nxt)
        out = dict(row)
        out.update({
            "statement_position": pos, "previous_value_de": prev["small_value_de"] if prev else "STATEMENT_START",
            "next_value_de": nxt["small_value_de"] if nxt else "STATEMENT_END", "selection_layer": layer,
            "selection_reason": reason, "predicted_joint_tuple_id": expected,
            "exact_card_recovered": "YES" if expected == row["joint_tuple_id"] else "NO",
        })
        outputs.append(out)
        if row["small_value_de"] in alias_values:
            alias_audit.append({
                "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "statement_id": row["statement_id"],
                "statement_position": pos, "surface": row["surface"], "small_value_de": row["small_value_de"],
                "previous_value_de": out["previous_value_de"], "next_value_de": out["next_value_de"],
                "selection_layer": layer, "expected_joint_tuple_id": row["joint_tuple_id"],
                "predicted_joint_tuple_id": expected, "recovered": out["exact_card_recovered"],
            })
    write("FOUR_HUNDRED_FIFTY_NINTH_381_EVENT_FINAL_REVERSE_WRITER.tsv", outputs)
    write("FOUR_HUNDRED_FIFTY_NINTH_61_ALIAS_OCCURRENCE_AUDIT.tsv", alias_audit)

    card_outputs = []
    rule_by_value = {row["value_de"]: row for row in rule_rows}
    for row in cards:
        out = dict(row)
        if row["small_value_de"] in rule_by_value:
            out["exact_selection_layer"] = rule_by_value[row["small_value_de"]]["selection_layer"]
            out["exact_selection_rule"] = rule_by_value[row["small_value_de"]]["rule"]
        else:
            out["exact_selection_layer"] = "UNIQUE_VALUE"
            out["exact_selection_rule"] = "write only card with this value"
        card_outputs.append(out)
    write("FOUR_HUNDRED_FIFTY_NINTH_173_CARD_FINAL_DICTIONARY.tsv", card_outputs)

    summary = {
        "status": "PASS", "events": len(outputs), "cards": len(card_outputs), "alias_families": len(rule_rows),
        "alias_events": len(alias_audit), "unique_value_events": sum(row["selection_layer"] == "UNIQUE_VALUE" for row in outputs),
        "local_context_events": sum(row["selection_layer"] == "LOCAL_CONTEXT" for row in outputs),
        "statement_position_events": sum(row["selection_layer"] == "STATEMENT_POSITION" for row in outputs),
        "record_renderer_events": sum(row["selection_layer"] == "RECORD_RENDERER" for row in outputs),
        "exact_cards_recovered": sum(row["exact_card_recovered"] == "YES" for row in outputs),
    }
    (HERE / "FOUR_HUNDRED_FIFTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
