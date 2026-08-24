#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P522 = ROOT / "experiments/yolo/sidequest_semantic_wrapper_stamps_five_hundred_twenty_second"


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
    source = read_tsv(P522 / "FIVE_HUNDRED_TWENTY_SECOND_381_STAMP_RENDERER_LOG.tsv")
    entries = read_tsv(P522 / "FIVE_HUNDRED_TWENTY_SECOND_SIXTY_SIX_WRAPPER_INSTRUCTIONS.tsv")

    locus_members: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    statement_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        locus_members[(row["record"], row["locus"])].append(row)
        statement_members[row["statement_id"]].append(row)
    derived: dict[str, dict[str, str]] = {}
    for index, row in enumerate(source):
        locus = locus_members[(row["record"], row["locus"])]
        li = next(i for i, item in enumerate(locus) if item["event_id"] == row["event_id"])
        lpos = "ONLY" if len(locus) == 1 else "FIRST" if li == 0 else "LAST" if li == len(locus) - 1 else "MIDDLE"
        previous = source[index - 1] if index and source[index - 1]["record"] == row["record"] else None
        following = source[index + 1] if index + 1 < len(source) and source[index + 1]["record"] == row["record"] else None
        derived[row["event_id"]] = {
            "locus_position": lpos,
            "previous_procedure": previous["procedure_tokens"] if previous else "RECORD_START",
            "next_rule_surface": following["renderer_first_choice"] if following else "RECORD_END",
        }

    rule_specs = [
        {
            "rule_id": "WR01",
            "input_rule_surface": "qokain",
            "condition_field": "previous_procedure",
            "condition_value": "HOLD_STATE",
            "output_surface": "okain",
            "wrapper_stamp": "Ø",
            "teaching_de": "Nach einem Haltezustand qokain ohne q-Eingang schreiben.",
        },
        {
            "rule_id": "WR02",
            "input_rule_surface": "chor",
            "condition_field": "next_rule_surface",
            "condition_value": "chey",
            "output_surface": "or",
            "wrapper_stamp": "Ø",
            "teaching_de": "Vor chey den chor-Träger fortlassen und or schreiben.",
        },
        {
            "rule_id": "WR03",
            "input_rule_surface": "cheey",
            "condition_field": "locus_position",
            "condition_value": "MIDDLE",
            "output_surface": "shey",
            "wrapper_stamp": "sh",
            "teaching_de": "Mediales cheey mit sh-Eingang als shey schreiben.",
        },
        {
            "rule_id": "WR04",
            "input_rule_surface": "char",
            "condition_field": "locus_position",
            "condition_value": "LAST",
            "output_surface": "dar",
            "wrapper_stamp": "d",
            "teaching_de": "Locusfinales char mit d-Eingang als dar schreiben.",
        },
    ]
    rule_hits: dict[str, str] = {}
    rule_rows: list[dict[str, str]] = []
    for spec in rule_specs:
        hits = [
            row
            for row in source
            if row["renderer_first_choice"] == spec["input_rule_surface"]
            and derived[row["event_id"]][spec["condition_field"]] == spec["condition_value"]
        ]
        for row in hits:
            if row["renderer_final_surface"] != spec["output_surface"]:
                raise ValueError(f"context rule false positive {spec['rule_id']} {row['event_id']}")
            rule_hits[row["event_id"]] = spec["rule_id"]
        rule_rows.append(
            {
                **spec,
                "support_events": str(len(hits)),
                "event_ids": "|".join(row["event_id"] for row in hits),
                "false_positive_events": "0",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_THIRD_FOUR_CONTEXT_WRAPPER_RULES.tsv", rule_rows)

    residual_events: list[dict[str, str]] = []
    entry_by_event: dict[str, dict[str, str]] = {}
    for entry in entries:
        for event_id in entry["event_ids"].split("|"):
            entry_by_event[event_id] = entry
            if event_id in rule_hits:
                continue
            residual_events.append(
                {
                    "residual_no": str(len(residual_events) + 1),
                    "mode_id_old": entry["mode_id"],
                    "record": entry["record"],
                    "page": entry["page"],
                    "locus": entry["locus"],
                    "event_id": event_id,
                    "input_rule_surface": entry["input_rule_surface"],
                    "remove_wrapper": entry["remove_wrapper"],
                    "retain_tail": entry["retain_tail"],
                    "apply_wrapper_stamp": entry["apply_wrapper_stamp"],
                    "local_output_surface": entry["observed_local_surface"],
                    "reason": "NO_REPEATED_ZERO_FALSE_POSITIVE_CONTEXT_RULE",
                }
            )
    write_tsv("FIVE_HUNDRED_TWENTY_THIRD_FIFTY_NINE_RESIDUAL_ASSIGNMENTS.tsv", residual_events)

    residual_loci: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in residual_events:
        residual_loci[(row["record"], row["locus"])].append(row)
    modes: list[dict[str, str]] = []
    mode_for_locus: dict[tuple[str, str], str] = {}
    source_by_locus = {(row["record"], row["locus"]): row for row in source}
    for number, (key, rows) in enumerate(residual_loci.items(), 1):
        mode_id = f"RR{number:02d}"
        mode_for_locus[key] = mode_id
        members = locus_members[key]
        modes.append(
            {
                "residual_mode_id": mode_id,
                "record": key[0],
                "page": members[0]["page"],
                "locus": key[1],
                "load_event": members[0]["event_id"],
                "residual_assignments": str(len(rows)),
                "residual_event_ids": "|".join(row["event_id"] for row in rows),
                "instruction_de": "Nur die verbliebenen lokalen Stempelzuweisungen laden; vier Kontextregeln vorher anwenden.",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_THIRD_THIRTY_FOUR_RESIDUAL_LOCUS_TABLES.tsv", modes)

    mode_load_event = {row["load_event"]: row for row in modes}
    output: list[dict[str, str]] = []
    decisions: list[dict[str, str]] = []
    for row in source:
        event_id = row["event_id"]
        key = (row["record"], row["locus"])
        context_rule = rule_hits.get(event_id, "NONE")
        residual = event_id in {item["event_id"] for item in residual_events}
        mode_id = mode_for_locus.get(key, "NONE")
        load = event_id in mode_load_event
        if load:
            decisions.append(
                {
                    "decision_no": "",
                    "event_id": event_id,
                    "statement_id": row["statement_id"],
                    "record": row["record"],
                    "page": row["page"],
                    "locus": row["locus"],
                    "decision_type": "LOAD_RESIDUAL_LOCUS_TABLE",
                    "selected_value": mode_id,
                }
            )
        output.append(
            {
                **row,
                **derived[event_id],
                "context_wrapper_rule": context_rule,
                "residual_local_assignment": "YES" if residual else "NO",
                "residual_locus_mode": mode_id,
                "residual_mode_load_here": "YES" if load else "NO",
                "wrapper_assignment_source": (
                    "AUTOMATIC_CONTEXT_RULE"
                    if context_rule != "NONE"
                    else "RESIDUAL_LOCUS_TABLE"
                    if residual
                    else "GLOBAL_RULE_RENDERER"
                ),
                "context_master_mode": "CONSCIOUS_LOCAL_CHOICE" if load else "AUTOMATIC_FLOW",
            }
        )
    for number, row in enumerate(decisions, 1):
        row["decision_no"] = str(number)
    write_tsv("FIVE_HUNDRED_TWENTY_THIRD_381_CONTEXT_RENDERER_LOG.tsv", output)
    write_tsv("FIVE_HUNDRED_TWENTY_THIRD_THIRTY_FOUR_CONSCIOUS_DECISIONS.tsv", decisions)

    summary = {
        "status": "PASS",
        "events": len(output),
        "context_rules": len(rule_rows),
        "context_rule_events": len(rule_hits),
        "residual_assignments": len(residual_events),
        "residual_locus_tables": len(modes),
        "conscious_events": sum(row["context_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in output),
        "automatic_events": sum(row["context_master_mode"] == "AUTOMATIC_FLOW" for row in output),
        "dropped_locus_tables": 38 - len(modes),
        "rule_support": dict(Counter(rule_hits.values())),
    }
    (HERE / "FIVE_HUNDRED_TWENTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
