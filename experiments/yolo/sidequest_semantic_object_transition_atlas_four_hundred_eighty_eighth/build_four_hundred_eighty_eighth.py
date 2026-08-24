#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P485 = ROOT / "experiments/yolo/sidequest_semantic_residual_forms_four_hundred_eighty_fifth"

TRANSITIONS = {
    "ACTIVE_CARRIED": "laufenden Arbeitsposten beibehalten",
    "BATCH_ACTIVATED": "neuen Ansatz zum laufenden Posten machen",
    "PORTION_CREATED": "eine Portion abteilen und aktivieren",
    "FRACTION_CREATED": "eine Fraktion entnehmen und aktivieren",
    "ADDITION_ACTIVATED": "einen Zusatz zum laufenden Posten machen",
    "COLLECTION_CREATED": "einen Empfangsbestand bilden",
    "FLOW_ACTIVATED": "einen Flüssigkeitslauf aktivieren",
    "RESULT_CREATED": "einen Ergebnisbestand aktivieren",
    "NEXT_ITEM_ACTIVATED": "zum nächsten Arbeitsposten wechseln",
    "TARGET_ONLY": "nur die Zielstelle setzen; Stoff bleibt unverändert",
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


def collapse(values: list[str]) -> str:
    out = []
    for value in values:
        if not out or out[-1] != value:
            out.append(value)
    return ">".join(out)


def main() -> None:
    deck = read(P485 / "FOUR_HUNDRED_EIGHTY_FIFTH_59_ITEM_LOCAL_DECK.tsv")
    decompositions = {row["statement_id"]: row for row in read(P485 / "FOUR_HUNDRED_EIGHTY_FIFTH_65_LOCAL_FORM_DECOMPOSITIONS.tsv")}
    mini = {row["residual_form_id"]: row for row in read(P485 / "FOUR_HUNDRED_EIGHTY_FIFTH_THREE_RESIDUAL_MINI_FORMS.tsv")}
    events = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv")
    event_map = {row["event_id"]: row for row in events}
    statement_events: dict[str, list[str]] = defaultdict(list)
    for row in events:
        statement_events[row["statement_id"]].append(row["event_id"])

    def item_event_ids(row: dict[str, str]) -> list[str]:
        item = row["local_item_id"]
        statement_id = row["statement_ids"]
        if item.startswith("R"):
            return mini[item]["event_ids"].split("|")
        if item.startswith("W:"):
            return statement_events[statement_id]
        return decompositions[statement_id]["residual_event_ids"].split("|")

    transition_counts = Counter(row["state_transition"] for row in events)
    transition_rows = []
    for transition, meaning in TRANSITIONS.items():
        transition_rows.append({
            "transition_id": transition,
            "short_workshop_rule_de": meaning,
            "all_prose_events": transition_counts[transition],
            "changes_active_object": "NO" if transition in {"ACTIVE_CARRIED", "TARGET_ONLY"} else "YES",
        })
    write("FOUR_HUNDRED_EIGHTY_EIGHTH_TEN_OBJECT_TRANSITIONS.tsv", transition_rows)

    atlas = []
    signature_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in deck:
        ids = item_event_ids(row)
        selected = [event_map[event_id] for event_id in ids]
        transition_chain = collapse([event["state_transition"] for event in selected])
        phase_chain = collapse([event["action_phase"] for event in selected])
        rich_chain = collapse([
            f"{event['action_phase']}:{event['state_transition']}:{event['closes_step']}:{event['quantity_kind']}:{event['direction_roles']}"
            for event in selected
        ])
        created = [event["state_transition"] for event in selected if event["state_transition"] not in {"ACTIVE_CARRIED", "TARGET_ONLY"}]
        item = {
            "local_item_id": row["local_item_id"],
            "kind": row["kind"],
            "statement_ids": row["statement_ids"],
            "events": len(selected),
            "event_ids": "|".join(ids),
            "phase_chain": phase_chain,
            "object_transition_chain": transition_chain,
            "object_changes": "|".join(created) or "NONE",
            "source_object_de": selected[0]["active_before_de"],
            "result_object_de": selected[-1]["active_after_de"],
            "owner_codes": "|".join(dict.fromkeys(event["owner_code"] for event in selected)),
            "meaningful_merge_signature": rich_chain,
            "teaching_text_de": row["teaching_text_de"],
        }
        atlas.append(item)
        signature_groups[rich_chain].append(item)
    write("FOUR_HUNDRED_EIGHTY_EIGHTH_59_LOCAL_ITEM_OBJECT_ATLAS.tsv", atlas)

    merge_rows = []
    for signature, rows in sorted(signature_groups.items()):
        if len(rows) < 2:
            continue
        meanings = {row["teaching_text_de"] for row in rows}
        merge_rows.append({
            "candidate_group": f"C{len(merge_rows) + 1:02d}",
            "items": len(rows),
            "local_item_ids": "|".join(str(row["local_item_id"]) for row in rows),
            "shared_object_action_signature": signature,
            "same_concrete_action": "YES" if len(meanings) == 1 else "NO",
            "decision": "MERGE" if len(meanings) == 1 else "KEEP_SEPARATE_ACTIONS",
            "reason_de": "gleiche konkrete Restkarte" if len(meanings) == 1 else "gleicher Objektzustand, aber andere konkrete Handlung oder Gradierung",
        })
    write("FOUR_HUNDRED_EIGHTY_EIGHTH_THREE_ABSTRACT_MERGE_CANDIDATES.tsv", merge_rows)

    long_rows = []
    for row in sorted((row for row in atlas if row["kind"] == "KEEP_WHOLE_LOCAL_FORM"), key=lambda item: (-int(item["events"]), item["local_item_id"])):
        long_rows.append({
            "priority": len(long_rows) + 1,
            "local_item_id": row["local_item_id"],
            "statement_id": row["statement_ids"],
            "events": row["events"],
            "phase_chain": row["phase_chain"],
            "object_transition_chain": row["object_transition_chain"],
            "source_object_de": row["source_object_de"],
            "result_object_de": row["result_object_de"],
            "next_question_de": "Welche konkrete Werkstattprozedur erklärt diese ganze Folge mit einem kurzen gelernten Makronamen?",
        })
    write("FOUR_HUNDRED_EIGHTY_EIGHTH_TEN_LONG_NOMENCLATOR_PRIORITIES.tsv", long_rows)

    chain_counts = Counter(row["object_transition_chain"] for row in atlas)
    chain_rows = []
    for chain, count in sorted(chain_counts.items(), key=lambda item: (-item[1], item[0])):
        chain_rows.append({
            "chain_id": f"T{len(chain_rows) + 1:02d}",
            "object_transition_chain": chain,
            "local_items": count,
            "item_ids": "|".join(row["local_item_id"] for row in atlas if row["object_transition_chain"] == chain),
        })
    write("FOUR_HUNDRED_EIGHTY_EIGHTH_26_OBJECT_TRANSITION_CHAINS.tsv", chain_rows)

    summary = {
        "status": "PASS",
        "object_transition_types": len(transition_rows),
        "local_items": len(atlas),
        "active_carried_only_items": sum(row["object_transition_chain"] == "ACTIVE_CARRIED" for row in atlas),
        "items_with_object_change": sum(row["object_changes"] != "NONE" for row in atlas),
        "transition_chains": len(chain_rows),
        "abstract_repeated_signatures": len(merge_rows),
        "safe_new_merges": sum(row["decision"] == "MERGE" for row in merge_rows),
        "long_whole_forms": len(long_rows),
        "largest_whole_form_events": int(long_rows[0]["events"]),
    }
    (HERE / "FOUR_HUNDRED_EIGHTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
