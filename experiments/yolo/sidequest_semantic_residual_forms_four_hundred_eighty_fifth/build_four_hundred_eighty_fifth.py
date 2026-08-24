#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P477 = ROOT / "experiments/yolo/sidequest_semantic_sentence_templates_four_hundred_seventy_seventh"
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P483 = ROOT / "experiments/yolo/sidequest_semantic_form_classes_four_hundred_eighty_third"
P484 = ROOT / "experiments/yolo/sidequest_semantic_hierarchical_manual_four_hundred_eighty_fourth"


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


def choose_occurrences(candidates: list[tuple[int, int, dict[str, str]]]) -> list[tuple[int, int, dict[str, str]]]:
    """Maximum covered events by non-overlapping motif occurrences."""
    ordered = sorted(candidates, key=lambda x: (x[1], x[0], x[2]["template_id"], x[2]["occurrence_id"]))
    n = len(ordered)
    score = [0] * (n + 1)
    predecessor: list[int] = []
    for index, item in enumerate(ordered):
        prior = index - 1
        while prior >= 0 and ordered[prior][1] >= item[0]:
            prior -= 1
        predecessor.append(prior + 1)
        width = item[1] - item[0] + 1
        score[index + 1] = max(score[index], score[prior + 1] + width)
    selected = []
    index = n
    while index:
        item = ordered[index - 1]
        prior = predecessor[index - 1]
        width = item[1] - item[0] + 1
        if score[prior] + width > score[index - 1]:
            selected.append(item)
            index = prior
        else:
            index -= 1
    return sorted(selected)


def main() -> None:
    local = read(P483 / "FOUR_HUNDRED_EIGHTY_THIRD_65_LOCAL_FORMS.tsv")
    events = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv")
    occurrences = read(P477 / "FOUR_HUNDRED_SEVENTY_SEVENTH_MOTIF_OCCURRENCES.tsv")
    old_manual = read(P484 / "FOUR_HUNDRED_EIGHTY_FOURTH_283_ITEM_HIERARCHICAL_MANUAL.tsv")
    old_ledger = read(P484 / "FOUR_HUNDRED_EIGHTY_FOURTH_776_FORWARD_RECONSTRUCTION.tsv")
    local_ids = [row["statement_id"] for row in local]
    local_set = set(local_ids)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    event_position: dict[str, dict[str, int]] = defaultdict(dict)
    for event in events:
        event_position[event["statement_id"]][event["event_id"]] = len(by_statement[event["statement_id"]])
        by_statement[event["statement_id"]].append(event)
    candidates: dict[str, list[tuple[int, int, dict[str, str]]]] = defaultdict(list)
    for occurrence in occurrences:
        statement_id = occurrence["statement_id"]
        if statement_id not in local_set:
            continue
        positions = [event_position[statement_id][event_id] for event_id in occurrence["event_ids"].split("|")]
        candidates[statement_id].append((min(positions), max(positions), occurrence))

    selected_by_statement = {statement_id: choose_occurrences(candidates[statement_id]) for statement_id in local_ids}
    selected_rows = []
    residual_by_statement: dict[str, list[list[dict[str, str]]]] = {}
    for statement_id in local_ids:
        covered = set()
        for start, end, occurrence in selected_by_statement[statement_id]:
            covered.update(range(start, end + 1))
            selected_rows.append({
                "selection_order": len(selected_rows) + 1,
                "statement_id": statement_id,
                "occurrence_id": occurrence["occurrence_id"],
                "template_id": occurrence["template_id"],
                "event_ids": occurrence["event_ids"],
                "events": end - start + 1,
                "actual_span_de": occurrence["actual_span_de"],
            })
        spans: list[list[dict[str, str]]] = []
        current: list[dict[str, str]] = []
        for index, event in enumerate(by_statement[statement_id]):
            if index in covered:
                if current:
                    spans.append(current)
                    current = []
            else:
                current.append(event)
        if current:
            spans.append(current)
        residual_by_statement[statement_id] = spans
    write("FOUR_HUNDRED_EIGHTY_FIFTH_43_OPTIMAL_MOTIF_OCCURRENCES.tsv", selected_rows)

    one_span_patterns = Counter()
    for spans in residual_by_statement.values():
        if len(spans) == 1:
            one_span_patterns[">".join(event["component_parse"] for event in spans[0])] += 1
    mini_patterns = {pattern for pattern, count in one_span_patterns.items() if count >= 2}
    mini_ids = {pattern: f"R{index + 1:02d}" for index, pattern in enumerate(sorted(mini_patterns))}

    mini_rows = []
    for pattern in sorted(mini_patterns):
        occurrences_for_pattern = []
        for statement_id, spans in residual_by_statement.items():
            if len(spans) == 1 and ">".join(event["component_parse"] for event in spans[0]) == pattern:
                occurrences_for_pattern.append((statement_id, spans[0]))
        sample = occurrences_for_pattern[0][1]
        mini_rows.append({
            "residual_form_id": mini_ids[pattern],
            "component_pattern": pattern,
            "short_rule_de": "; ".join(event["pass481_event_de"] for event in sample),
            "statements": len(occurrences_for_pattern),
            "statement_ids": "|".join(statement_id for statement_id, _ in occurrences_for_pattern),
            "event_ids": "|".join(event["event_id"] for _, span in occurrences_for_pattern for event in span),
        })
    write("FOUR_HUNDRED_EIGHTY_FIFTH_THREE_RESIDUAL_MINI_FORMS.tsv", mini_rows)

    decomposition_rows = []
    local_deck = []
    residual_rows = []
    strategy_by_statement = {}
    for source in local:
        statement_id = source["statement_id"]
        statement_events = by_statement[statement_id]
        selected = selected_by_statement[statement_id]
        spans = residual_by_statement[statement_id]
        covered_count = sum(end - start + 1 for start, end, _ in selected)
        if not spans:
            strategy = "MOTIFS_ONLY"
            deck_item = "NONE"
        elif len(spans) > 1:
            strategy = "KEEP_WHOLE_LOCAL_FORM"
            deck_item = f"W:{statement_id}"
            local_deck.append({"local_item_id": deck_item, "kind": strategy, "component_or_statement_pattern": source["phase_chain"], "events_to_memorize": len(statement_events), "statement_ids": statement_id, "teaching_text_de": source["complete_expansion_de"]})
        else:
            pattern = ">".join(event["component_parse"] for event in spans[0])
            if pattern in mini_ids:
                strategy = "SHARED_RESIDUAL_MINI_FORM"
                deck_item = mini_ids[pattern]
            else:
                strategy = "ONE_LOCAL_RESIDUAL"
                deck_item = f"X:{statement_id}"
                local_deck.append({"local_item_id": deck_item, "kind": strategy, "component_or_statement_pattern": pattern, "events_to_memorize": len(spans[0]), "statement_ids": statement_id, "teaching_text_de": "; ".join(event["pass481_event_de"] for event in spans[0])})
        strategy_by_statement[statement_id] = (strategy, deck_item)
        decomposition_rows.append({
            "statement_id": statement_id,
            "register": source["register"],
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "statement_events": len(statement_events),
            "selected_motifs": "|".join(item[2]["template_id"] for item in selected) or "NONE",
            "motif_events": covered_count,
            "residual_events": len(statement_events) - covered_count,
            "residual_spans": len(spans),
            "residual_event_ids": "||".join("|".join(event["event_id"] for event in span) for span in spans) or "NONE",
            "strategy": strategy,
            "local_deck_item": deck_item,
            "complete_expansion_de": source["complete_expansion_de"],
        })
        for span_index, span in enumerate(spans, 1):
            pattern = ">".join(event["component_parse"] for event in span)
            residual_rows.append({
                "residual_span_order": len(residual_rows) + 1,
                "statement_id": statement_id,
                "span_in_statement": span_index,
                "events": len(span),
                "event_ids": "|".join(event["event_id"] for event in span),
                "component_pattern": pattern,
                "phase_pattern": ">".join(event["action_phase"] for event in span),
                "reading_de": "; ".join(event["pass481_event_de"] for event in span),
                "shared_mini_form": mini_ids.get(pattern, "NONE") if len(spans) == 1 else "NOT_APPLIED_TO_MULTI_SPAN_STATEMENT",
            })
    for mini in mini_rows:
        local_deck.append({"local_item_id": mini["residual_form_id"], "kind": "SHARED_RESIDUAL_MINI_FORM", "component_or_statement_pattern": mini["component_pattern"], "events_to_memorize": 1, "statement_ids": mini["statement_ids"], "teaching_text_de": mini["short_rule_de"]})
    local_deck.sort(key=lambda row: row["local_item_id"])
    write("FOUR_HUNDRED_EIGHTY_FIFTH_65_LOCAL_FORM_DECOMPOSITIONS.tsv", decomposition_rows)
    write("FOUR_HUNDRED_EIGHTY_FIFTH_75_RESIDUAL_SPANS.tsv", residual_rows)
    write("FOUR_HUNDRED_EIGHTY_FIFTH_59_ITEM_LOCAL_DECK.tsv", local_deck)

    revised_manual = [row for row in old_manual if row["layer"] != "L6_LOCAL_STATEMENT_FORM"]
    insertion = []
    for row in local_deck:
        insertion.append({
            "manual_order": 0,
            "layer": "L6_REDUCED_LOCAL_DECK",
            "item_id": row["local_item_id"],
            "teaching_value_or_rule_de": row["teaching_text_de"],
            "scope": "PROSE",
            "support_or_instances": row["statement_ids"],
            "source_artifact": "PASS485_OPTIMAL_MOTIF_RESIDUAL_DECK",
        })
    revised_manual = [row for row in revised_manual if row["layer"] < "L6"] + insertion + [row for row in revised_manual if row["layer"] > "L6"]
    for index, row in enumerate(revised_manual, 1):
        row["manual_order"] = index
    write("FOUR_HUNDRED_EIGHTY_FIFTH_277_ITEM_REVISED_MANUAL.tsv", revised_manual)

    revised_ledger = []
    for row in old_ledger:
        new = dict(row)
        statement_id = row["statement_or_locus"]
        if row["domain"] == "PROSE" and statement_id in strategy_by_statement:
            strategy, item = strategy_by_statement[statement_id]
            new["semantic_layer"] = strategy
            new["syntax_item"] = item
        revised_ledger.append(new)
    write("FOUR_HUNDRED_EIGHTY_FIFTH_776_REDUCED_MANUAL_RECONSTRUCTION.tsv", revised_ledger)

    counts = Counter(row["strategy"] for row in decomposition_rows)
    summary = {
        "status": "PASS",
        "local_statements": len(local),
        "original_local_items": 65,
        "original_local_event_atoms": sum(len(by_statement[statement_id]) for statement_id in local_ids),
        "optimal_motif_occurrences": len(selected_rows),
        "motif_covered_events": sum(int(row["events"]) for row in selected_rows),
        "residual_spans": len(residual_rows),
        "residual_events": sum(int(row["events"]) for row in residual_rows),
        "residual_mini_forms": len(mini_rows),
        "revised_local_items": len(local_deck),
        "revised_local_event_atoms": sum(int(row["events_to_memorize"]) for row in local_deck),
        "motifs_only_statements": counts["MOTIFS_ONLY"],
        "one_local_residual_statements": counts["ONE_LOCAL_RESIDUAL"],
        "shared_mini_form_statements": counts["SHARED_RESIDUAL_MINI_FORM"],
        "whole_local_form_statements": counts["KEEP_WHOLE_LOCAL_FORM"],
        "manual_items": len(revised_manual),
        "groups": len(revised_ledger),
    }
    (HERE / "FOUR_HUNDRED_EIGHTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
