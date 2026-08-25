#!/usr/bin/env python3
"""Adjudicate the 63 Pass-1022 R-head-or-tail alternatives."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "sidequest_semantic_argument_scope_stack_one_thousand_twenty_second"
AMBIGUITIES = SOURCE / "SCOPE_STACK_AMBIGUITIES.tsv"
ATTACHMENTS = SOURCE / "SCOPE_STACK_ATTACHMENTS.tsv"
EVENTS = SOURCE / "PASS1022_3888_EVENT_SCOPE_BINDINGS.tsv"
OUT_TSV = HERE / "R_HEAD_TAIL_63_ADJUDICATION.tsv"
OUT_COUNTS = HERE / "R_HEAD_TAIL_COUNTS.json"

ACTIONS = {"OK", "CH", "SH", "K", "S", "T", "CHD", "R", "P"}
COMPLEMENTS = {"Y", "AIIN", "AIN", "OR", "AL", "AR", "AIR", "L"}
ACTION_VALUES = {
    "OK": "SETZEN",
    "CH": "NEHMEN",
    "SH": "HALTEN",
    "K": "GEBEN",
    "S": "WÄHLEN",
    "T": "EINSTELLEN",
    "CHD": "UMSETZEN",
    "R": "MARKIEREN",
    "P": "EINSETZEN",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_r_card(
    event: dict[str, str], related: list[tuple[dict[str, str], dict[str, str]]]
) -> tuple[str, str, str, str]:
    tokens = event["component_recipe"].split("+")
    r_index = tokens.index("R")
    actions_left = [token for token in tokens[:r_index] if token in ACTIONS]
    right = tokens[r_index + 1 :]
    next_action_offset = next(
        (index for index, token in enumerate(right) if token in ACTIONS), len(right)
    )
    local_right = right[:next_action_offset]
    local_complements = [token for token in local_right if token in COMPLEMENTS]

    if actions_left and local_complements:
        outer = actions_left[-1]
        rationale = (
            f"{outer}={ACTION_VALUES[outer]} steht links im selben Paket; "
            f"{'+'.join(local_complements)} steht rechts von R vor jeder neuen Handlung. "
            "R ist deshalb der innere Kopf MARKIEREN."
        )
        return "NESTED", "R2_NESTED_LOCAL", "INNER_R_WITH_RIGHT_COMPLEMENT", rationale

    if actions_left:
        outer = actions_left[-1]
        rationale = (
            f"{outer}={ACTION_VALUES[outer]} steht bereits links im selben Paket; "
            "rechts von R folgt darin kein eigenes Argument. R markiert den äußeren Kopf, "
            "statt einen neuen offenen Kopf zu beginnen."
        )
        return "TAIL", "R3_TAIL_AFTER_ACTION", "CARD_FINAL_R_AFTER_ACTION", rationale

    if "OL" in local_right and not local_complements:
        outer = event["active_head_before_de"]
        rationale = (
            f"R hat kein eigenes Argument; OL führt ausdrücklich den offenen Kopf {outer} "
            "fort. R bleibt dessen Markierungsschwanz."
        )
        return "TAIL", "R4_TAIL_BEFORE_OL", "R_PLUS_OL_CONTINUES_OUTER", rationale

    if local_complements:
        rationale = (
            "R ist der erste Handlungskopf des Pakets und erhält rechts vor jeder neuen "
            f"Handlung { '+'.join(local_complements) }; es eröffnet MARKIEREN."
        )
        return "HEAD", "R1_HEAD_WITH_LOCAL_RIGHT", "FIRST_ACTION_R_WITH_COMPLEMENT", rationale

    if "L" in tokens[:r_index]:
        rationale = (
            "L öffnet den Rahmen nach rechts; R ist der erste Handlungskopf darin und "
            "erhält den unmittelbar folgenden Zusatz."
        )
        return "HEAD", "R1_HEAD_IN_RIGHT_FRAME", "RIGHT_FRAME_TO_R", rationale

    r_card = int(event["card_ordinal_in_statement"])
    has_immediate_right_focus = any(
        int(attachment["card_ordinal_in_statement"]) == r_card + 1
        for _, attachment in related
    )
    if tokens == ["R"] and has_immediate_right_focus:
        rationale = (
            "R steht als eigene Karte und die nächste Karte beginnt sofort mit seinem "
            "Zusatz; damit eröffnet R den Kopf MARKIEREN."
        )
        return "HEAD", "R1_HEAD_STANDALONE", "STANDALONE_R_BEFORE_ARGUMENT", rationale

    return (
        "UNRESOLVED",
        "R5_NO_POSITION_CUE",
        "NO_DECISIVE_POSITION_CUE",
        "Weder ein lokales R-Argument noch ein eindeutiger äußerer Handlungskopf ist sichtbar.",
    )


def main() -> None:
    ambiguity_rows = [
        row
        for row in read_tsv(AMBIGUITIES)
        if row["ambiguity_class"] == "R_HEAD_OR_TAIL"
    ]
    attachments = {row["attachment_id"]: row for row in read_tsv(ATTACHMENTS)}
    events = read_tsv(EVENTS)
    event_by_id = {row["event_id"]: row for row in events}
    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        statement_events[event["statement_id"]].append(event)

    related_by_r: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for ambiguity in ambiguity_rows:
        attachment = attachments[ambiguity["attachment_id"]]
        related_by_r[attachment["chosen_action_event_id"]].append((ambiguity, attachment))

    decisions = {
        event_id: classify_r_card(event_by_id[event_id], related)
        for event_id, related in related_by_r.items()
    }

    fields = [
        "ambiguity_id",
        "attachment_id",
        "physical_page",
        "statement_id",
        "r_event_id",
        "r_card_ordinal",
        "r_locus",
        "r_surface",
        "r_component_recipe",
        "r_active_head_before_de",
        "previous_card_recipe",
        "next_card_recipe",
        "neighbourhood_de",
        "package_pattern",
        "r_decision",
        "rule_id",
        "focus_event_id",
        "focus_card_ordinal",
        "focus_surface",
        "focus_component_recipe",
        "focus_core",
        "focus_value_de",
        "focus_distance_cards",
        "selected_attachment",
        "rejected_attachment",
        "changed_from_pass1022_default",
        "rationale_de",
    ]

    output: list[dict[str, str]] = []
    for ambiguity in ambiguity_rows:
        attachment = attachments[ambiguity["attachment_id"]]
        r_event_id = attachment["chosen_action_event_id"]
        r_event = event_by_id[r_event_id]
        focus_event = event_by_id[ambiguity["event_id"]]
        statement = statement_events[r_event["statement_id"]]
        position = statement.index(r_event)
        previous_recipe = statement[position - 1]["component_recipe"] if position else "STATEMENT_START"
        next_recipe = (
            statement[position + 1]["component_recipe"]
            if position + 1 < len(statement)
            else "STATEMENT_END"
        )
        decision, rule_id, package_pattern, rationale = decisions[r_event_id]
        if decision in {"HEAD", "NESTED"}:
            selected = ambiguity["chosen_attachment"]
            rejected = ambiguity["alternative_attachment"]
            changed = "NO"
        elif decision == "TAIL":
            selected = ambiguity["alternative_attachment"]
            rejected = ambiguity["chosen_attachment"]
            changed = "YES"
        else:
            selected = "UNRESOLVED"
            rejected = "UNRESOLVED"
            changed = "NO"
        r_card = int(r_event["card_ordinal_in_statement"])
        focus_card = int(focus_event["card_ordinal_in_statement"])
        output.append(
            {
                "ambiguity_id": ambiguity["ambiguity_id"],
                "attachment_id": ambiguity["attachment_id"],
                "physical_page": ambiguity["physical_page"],
                "statement_id": ambiguity["statement_id"],
                "r_event_id": r_event_id,
                "r_card_ordinal": r_event["card_ordinal_in_statement"],
                "r_locus": r_event["locus"],
                "r_surface": r_event["surface"],
                "r_component_recipe": r_event["component_recipe"],
                "r_active_head_before_de": r_event["active_head_before_de"],
                "previous_card_recipe": previous_recipe,
                "next_card_recipe": next_recipe,
                "neighbourhood_de": f"{previous_recipe} | [{r_event['component_recipe']}] | {next_recipe}",
                "package_pattern": package_pattern,
                "r_decision": decision,
                "rule_id": rule_id,
                "focus_event_id": ambiguity["event_id"],
                "focus_card_ordinal": focus_event["card_ordinal_in_statement"],
                "focus_surface": ambiguity["surface_card"],
                "focus_component_recipe": ambiguity["component_recipe"],
                "focus_core": ambiguity["focus_core"],
                "focus_value_de": ambiguity["focus_value_de"],
                "focus_distance_cards": str(focus_card - r_card),
                "selected_attachment": selected,
                "rejected_attachment": rejected,
                "changed_from_pass1022_default": changed,
                "rationale_de": rationale,
            }
        )

    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    card_counts = Counter(decision[0] for decision in decisions.values())
    row_counts = Counter(row["r_decision"] for row in output)
    rule_card_counts = Counter(decision[1] for decision in decisions.values())
    counts = {
        "result": "COMPLETE_R_HEAD_TAIL_POSITION_RULE",
        "root_value": "R=MARKIEREN",
        "r_head_or_tail_alternative_rows": len(output),
        "distinct_r_cards": len(decisions),
        "distinct_statements": len({row["statement_id"] for row in output}),
        "card_decisions": dict(sorted(card_counts.items())),
        "row_decisions": dict(sorted(row_counts.items())),
        "rule_card_counts": dict(sorted(rule_card_counts.items())),
        "rows_changed_from_pass1022_default": sum(
            row["changed_from_pass1022_default"] == "YES" for row in output
        ),
        "unresolved_rows": row_counts.get("UNRESOLVED", 0),
        "unresolved_cards": card_counts.get("UNRESOLVED", 0),
        "source_hashes": {
            AMBIGUITIES.name: sha256(AMBIGUITIES),
            ATTACHMENTS.name: sha256(ATTACHMENTS),
            EVENTS.name: sha256(EVENTS),
        },
    }
    assert len(output) == 63
    assert len(decisions) == 42
    assert counts["unresolved_rows"] == 0
    OUT_COUNTS.write_text(json.dumps(counts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
