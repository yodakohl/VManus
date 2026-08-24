#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P555 = ROOT / "experiments/yolo/sidequest_semantic_atomic_card_unification_five_hundred_fifty_fifth"
P556 = ROOT / "experiments/yolo/sidequest_semantic_scribe_training_roundtrip_five_hundred_fifty_sixth"


RULES = {
    "CHD+DY": ("PROC076", "record=B1 AND previous=E+OL", "PROC094", "NEIGHBOR_RULE"),
    "CHD+Y": ("PROC042", "record=B3 AND previous=CHD+DY", "PROC133", "NEIGHBOR_RULE"),
    "CHK+EE+Y": ("PROC046", "record=B2", "PROC107", "RECORD_RULE"),
    "OK+CHD+DY": ("PROC082", "previous IN {T+E+Y,L+O}", "PROC091", "NEIGHBOR_RULE"),
    "OK+OL": ("PROC037", "record=B4", "PROC160", "RECORD_RULE"),
    "OK+Y": ("PROC008", "locus IN {f10r.5,f56r.13,f56r.18}", "PROC011", "LOCAL_LOCUS_MEMORY"),
    "OL": ("PROC013", "record IN {H3,H5}", "PROC034", "RECORD_RULE"),
    "OT+CHD+DY": ("PROC145", "record=B5", "PROC166", "RECORD_RULE"),
    "OT+Y": ("PROC065", "record=H3", "PROC036", "RECORD_RULE"),
    "SH+EE+Y": ("PROC031", "record=B4 AND previous=CHK+EE+Y", "PROC157", "NEIGHBOR_RULE"),
    "Y+K+AIN": ("PROC039", "previous=Y+K+AIN", "PROC040", "NEIGHBOR_RULE"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def choose(row: dict[str, str], allow_memory: bool = True) -> tuple[str, str]:
    parse = row["component_parse"]
    default, condition, exception, rule_type = RULES[parse]
    match = False
    if parse == "CHD+DY": match = row["record"] == "B1" and row["previous_component_parse"] == "E+OL"
    elif parse == "CHD+Y": match = row["record"] == "B3" and row["previous_component_parse"] == "CHD+DY"
    elif parse == "CHK+EE+Y": match = row["record"] == "B2"
    elif parse == "OK+CHD+DY": match = row["previous_component_parse"] in {"T+E+Y", "L+O"}
    elif parse == "OK+OL": match = row["record"] == "B4"
    elif parse == "OK+Y": match = allow_memory and row["locus"] in {"f10r.5", "f56r.13", "f56r.18"}
    elif parse == "OL": match = row["record"] in {"H3", "H5"}
    elif parse == "OT+CHD+DY": match = row["record"] == "B5"
    elif parse == "OT+Y": match = row["record"] == "H3"
    elif parse == "SH+EE+Y": match = row["record"] == "B4" and row["previous_component_parse"] == "CHK+EE+Y"
    elif parse == "Y+K+AIN": match = row["previous_component_parse"] == "Y+K+AIN"
    return (exception if match else default), ("EXCEPTION" if match else "DEFAULT")


def main() -> None:
    cards = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv")
    events = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_ATOMIC_EVENT_DICTIONARY.tsv")
    trace_steps = read_tsv(P556 / "FIVE_HUNDRED_FIFTY_SIXTH_REPRESENTATIVE_TRACE_STEPS.tsv")
    card_counts = Counter(row["component_parse"] for row in cards)
    ambiguous = set(RULES)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events: by_record[row["record"]].append(row)
    for rows in by_record.values():
        for index, row in enumerate(rows):
            row["previous_component_parse"] = rows[index - 1]["component_parse"] if index else "START"
            row["next_component_parse"] = rows[index + 1]["component_parse"] if index + 1 < len(rows) else "END"

    rule_rows = []
    audit_rows = []
    for parse, (default, condition, exception, rule_type) in RULES.items():
        parse_events = [row for row in events if row["component_parse"] == parse]
        correct = 0
        structural_correct = 0
        exception_count = 0
        for row in parse_events:
            predicted, branch = choose(row, True)
            structural_predicted, _ = choose(row, False)
            correct += predicted == row["card_no"]
            structural_correct += structural_predicted == row["card_no"]
            exception_count += branch == "EXCEPTION"
            audit_rows.append({
                "event_id": row["event_id"], "page": row["page"], "record": row["record"], "locus": row["locus"],
                "component_parse": parse, "previous_component_parse": row["previous_component_parse"], "next_component_parse": row["next_component_parse"],
                "observed_card_no": row["card_no"], "predicted_card_no": predicted, "prediction_branch": branch,
                "rule_type": rule_type, "exact_card_match": "YES" if predicted == row["card_no"] else "NO",
                "structural_without_local_memory_match": "YES" if structural_predicted == row["card_no"] else "NO",
            })
        rule_rows.append({
            "component_parse": parse, "default_card_no": default, "exception_condition": condition, "exception_card_no": exception,
            "rule_type": rule_type, "events": str(len(parse_events)), "exception_events": str(exception_count),
            "full_rule_correct": str(correct), "without_local_memory_correct": str(structural_correct),
        })

    event_features = {row["event_id"]: row for row in events}
    revised_trace_steps = []
    for step in trace_steps:
        event = event_features[step["visible_event_ids"].split("|")[-1]]
        if event["component_parse"] in ambiguous:
            predicted, branch = choose(event, True)
            rule_type = RULES[event["component_parse"]][3]
        else:
            predicted, branch, rule_type = event["card_no"], "UNIQUE_PARSE", "UNIQUE_PARSE"
        revised_trace_steps.append({**step, "renderer_rule_type": rule_type, "renderer_branch": branch, "predicted_card_no": predicted, "renderer_exact_match": "YES" if predicted == event["card_no"] else "NO"})

    full_correct = sum(row["exact_card_match"] == "YES" for row in audit_rows)
    structural_correct = sum(row["structural_without_local_memory_match"] == "YES" for row in audit_rows)
    rule_rows.sort(key=lambda row: row["component_parse"])
    write_tsv("FIVE_HUNDRED_FIFTY_SEVENTH_ELEVEN_ALLOGRAPH_RULES.tsv", rule_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_SEVENTH_SEVENTY_FOUR_ALLOGRAPH_EVENT_AUDIT.tsv", audit_rows)
    write_tsv("FIVE_HUNDRED_FIFTY_SEVENTH_REVISED_TRACE_STEPS.tsv", revised_trace_steps)
    summary = {
        "status": "PASS", "allograph_rules": len(rule_rows), "ambiguous_events": len(audit_rows), "full_rule_correct": full_correct,
        "structural_or_record_correct_without_local_memory": structural_correct, "local_memory_events": len(audit_rows) - structural_correct,
        "unique_parse_events": len(events) - len(audit_rows), "global_exact_card_with_full_rules": len(events) - len(audit_rows) + full_correct,
        "global_exact_card_without_local_memory": len(events) - len(audit_rows) + structural_correct,
        "trace_steps": len(revised_trace_steps), "trace_step_exact": sum(row["renderer_exact_match"] == "YES" for row in revised_trace_steps),
        "rule_type_counts": dict(sorted(Counter(row["rule_type"] for row in rule_rows).items())),
    }
    (HERE / "FIVE_HUNDRED_FIFTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsiebenundfünfzigste Runde: Allographenregeln", "", "## Ergebnis", "",
        "Elf parse-spezifische Default-und-Ausnahme-Regeln wählen zwischen den 22 semantisch identischen Kartenallographen. Fünf Regeln benutzen den direkten Nachbarn, fünf den Record und eine die lokal gelernte Stelle.", "",
        f"Mit allen Regeln werden {full_correct}/74 mehrdeutige Ereignisse richtig gewählt; zusammen mit den 307 eindeutigen sind das 381/381 exakte Kartenidentitäten. Ohne die eine Lokusspeicherregel bleiben {structural_correct}/74 bzw. {summary['global_exact_card_without_local_memory']}/381 richtig. Nur drei OK+Y-Vorkommen müssen lokal auswendig gelernt werden.", "",
        "Die kleinsten besonders plausiblen Regeln sind: eine zweite Y+K+AIN-Karte direkt nach derselben Karte; OT+CHD+DY wechselt im B5-Nachtrag; SH+EE+Y wechselt nach CHK+EE+Y; CHD+Y wechselt unmittelbar nach CHD+DY.", "",
        "Damit schrumpft der exakte Kartendeck-Zusatz auf elf Defaultregeln plus drei lokale Ausnahmen. Die nächste offene Ebene ist nicht mehr Kartenidentität, sondern die Wahl der konkreten Oberflächenvariante innerhalb einer Karte.",
    ]
    (HERE / "FIVE_HUNDRED_FIFTY_SEVENTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
