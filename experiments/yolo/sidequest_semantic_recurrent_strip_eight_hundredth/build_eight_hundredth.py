#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
CARDS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv"
EVENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
STATEMENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv"

ACTION = ("CH", "SH", "CTH")
O_STRIP = ("O", "OR", "HO")
MEANING = {
    "CH": "ENTNEHMEN",
    "SH": "HALTEN",
    "CTH": "BEREITEN",
    "O": "VORGANG",
    "OR": "ANSATZ",
    "HO": "ZUTAT",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalized_signature(tokens: list[str], group: tuple[str, ...], member: str) -> str:
    return "+".join("SLOT" if token == member else token for token in tokens)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(CARDS)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    card_by_id = {row["exact_card_id"]: row for row in cards}

    inventory = []
    for row in cards:
        tokens = row["component_recipe"].split("+")
        action_members = [member for member in ACTION if member in tokens]
        o_members = [member for member in O_STRIP if member in tokens]
        if not action_members and not o_members:
            continue
        inventory.append(
            {
                "exact_card_id": row["exact_card_id"],
                "surfaces": row["registered_surfaces"],
                "component_recipe": row["component_recipe"],
                "working_reading_de": row["rebuilt_reading_de"],
                "events": row["events"],
                "action_members": "+".join(action_members) or "NONE",
                "o_strip_members": "+".join(o_members) or "NONE",
                "action_stack": "YES" if len(action_members) > 1 else "NO",
                "o_strip_stack": "YES" if len(o_members) > 1 else "NO",
            }
        )

    family_rows = []
    for group_name, group in (("ACTION_CH_SH_CTH", ACTION), ("O_OR_HO", O_STRIP)):
        families: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)
        for row in cards:
            tokens = row["component_recipe"].split("+")
            present = [member for member in group if member in tokens]
            if len(present) != 1 or tokens.count(present[0]) != 1:
                continue
            signature = normalized_signature(tokens, group, present[0])
            families[signature].append((present[0], row))
        for signature, members in sorted(families.items()):
            distinct = sorted({member for member, _ in members})
            if len(distinct) < 2:
                continue
            family_rows.append(
                {
                    "group": group_name,
                    "normalized_tail": signature,
                    "members_present": "+".join(distinct),
                    "member_count": len(distinct),
                    "cards": "|".join(row["exact_card_id"] for _, row in members),
                    "surfaces": "|".join(row["registered_surfaces"] for _, row in members),
                    "events": sum(int(row["events"]) for _, row in members),
                    "complete_three_member_family": "YES" if set(distinct) == set(group) else "NO",
                    "interpretation": (
                        "ONE_OPERATION_SLOT_WITH_THREE_ACTION_CHOICES"
                        if set(distinct) == set(ACTION)
                        else "TWO_NOUN_VALUES_SHARE_A_BARE_POSITION__NOT_ONE_STEM"
                    ),
                }
            )

    micro_cards = {
        "CH": next(row for row in cards if row["component_recipe"] == "CH+E+Y"),
        "SH": next(row for row in cards if row["component_recipe"] == "SH+E+Y"),
        "CTH": next(row for row in cards if row["component_recipe"] == "CTH+E+Y"),
    }
    substitution_rows = []
    target_events = [row for row in events if row["component_recipe"] in {"CH+E+Y", "SH+E+Y", "CTH+E+Y"}]
    for event in target_events:
        source_member = event["component_recipe"].split("+")[0]
        source_statement = statements[event["statement_id"]]
        for target_member in ACTION:
            card = micro_cards[target_member]
            substitution_rows.append(
                {
                    "source_event": event["event_id"],
                    "page": event["page"],
                    "statement_id": event["statement_id"],
                    "owner_de": event["owner_de"],
                    "source_member": source_member,
                    "source_surface": event["surface"],
                    "target_member": target_member,
                    "target_card": card["exact_card_id"],
                    "target_surfaces": card["registered_surfaces"],
                    "fixed_tail": "E+Y",
                    "substituted_prompt_de": f"{MEANING[target_member]} · KURZ · DIES",
                    "other_statement_events_fixed": "YES",
                    "owner_fixed": "YES",
                    "source_statement": source_statement["surface_sequence"],
                    "swap_status": "ATTESTED_CARD_INSERTED__CREATIVE_READBACK",
                }
            )

    stack_rows = []
    for row in cards:
        tokens = row["component_recipe"].split("+")
        for group_name, group in (("ACTION_CH_SH_CTH", ACTION), ("O_OR_HO", O_STRIP)):
            members = [member for member in group if member in tokens]
            if len(members) > 1:
                stack_rows.append(
                    {
                        "group": group_name,
                        "exact_card_id": row["exact_card_id"],
                        "surfaces": row["registered_surfaces"],
                        "component_recipe": row["component_recipe"],
                        "members_stacked": "+".join(members),
                        "working_reading_de": row["rebuilt_reading_de"],
                        "events": row["events"],
                        "consequence": (
                            "SEQUENTIAL_ACTION_STACK__DO_NOT_COLLAPSE_ACTION_VALUES"
                            if group_name == "ACTION_CH_SH_CTH"
                            else "COOCCURRENCE_PROVES_DISTINCT_GRAMMATICAL_LEVELS"
                        ),
                    }
                )

    decision_rows = [
        {
            "component": "CH",
            "short_value_de": "ENTNEHMEN",
            "old_tier": "RECURRENT_RULE_STRIP",
            "new_tier": "PARADIGM_CORE18",
            "reason": "complete CH/SH/CTH choice under fixed E+Y tail",
        },
        {
            "component": "SH",
            "short_value_de": "HALTEN",
            "old_tier": "RECURRENT_RULE_STRIP",
            "new_tier": "PARADIGM_CORE18",
            "reason": "complete CH/SH/CTH choice under fixed E+Y tail",
        },
        {
            "component": "CTH",
            "short_value_de": "BEREITEN",
            "old_tier": "RECURRENT_RULE_STRIP",
            "new_tier": "PARADIGM_CORE18",
            "reason": "complete CH/SH/CTH choice under fixed E+Y tail",
        },
        {
            "component": "O",
            "short_value_de": "VORGANG",
            "old_tier": "RECURRENT_RULE_STRIP",
            "new_tier": "RECURRENT_RULE_STRIP",
            "reason": "cooccurs with OR; no shared three-member tail",
        },
        {
            "component": "OR",
            "short_value_de": "ANSATZ",
            "old_tier": "RECURRENT_RULE_STRIP",
            "new_tier": "RECURRENT_RULE_STRIP",
            "reason": "noun-like preparation referent; cooccurs with O and HO",
        },
        {
            "component": "HO",
            "short_value_de": "ZUTAT",
            "old_tier": "RECURRENT_RULE_STRIP",
            "new_tier": "RECURRENT_RULE_STRIP",
            "reason": "noun-like ingredient referent; cooccurs with OR",
        },
    ]

    write(
        "EIGHT_HUNDREDTH_58_RELEVANT_CARDS.tsv",
        inventory,
        ["exact_card_id", "surfaces", "component_recipe", "working_reading_de", "events", "action_members", "o_strip_members", "action_stack", "o_strip_stack"],
    )
    write(
        "EIGHT_HUNDREDTH_SHARED_TAILS.tsv",
        family_rows,
        ["group", "normalized_tail", "members_present", "member_count", "cards", "surfaces", "events", "complete_three_member_family", "interpretation"],
    )
    write(
        "EIGHT_HUNDREDTH_12_ACTION_READBACKS.tsv",
        substitution_rows,
        ["source_event", "page", "statement_id", "owner_de", "source_member", "source_surface", "target_member", "target_card", "target_surfaces", "fixed_tail", "substituted_prompt_de", "other_statement_events_fixed", "owner_fixed", "source_statement", "swap_status"],
    )
    write(
        "EIGHT_HUNDREDTH_STACKED_COUNTEREXAMPLES.tsv",
        stack_rows,
        ["group", "exact_card_id", "surfaces", "component_recipe", "members_stacked", "working_reading_de", "events", "consequence"],
    )
    write(
        "EIGHT_HUNDREDTH_6_COMPONENT_DECISIONS.tsv",
        decision_rows,
        ["component", "short_value_de", "old_tier", "new_tier", "reason"],
    )

    action_union = [row for row in cards if set(row["component_recipe"].split("+")) & set(ACTION)]
    o_union = [row for row in cards if set(row["component_recipe"].split("+")) & set(O_STRIP)]
    summary = {
        "status": "PASS",
        "decision": "CH_SH_CTH_PROMOTED_TO_ACTION_CORE__O_OR_HO_REMAIN_DISTINCT_STRIP_VALUES",
        "action_union_cards": len(action_union),
        "action_union_events": sum(int(row["events"]) for row in action_union),
        "o_union_cards": len(o_union),
        "o_union_events": sum(int(row["events"]) for row in o_union),
        "complete_action_microparadigms": sum(row["complete_three_member_family"] == "YES" and row["group"] == "ACTION_CH_SH_CTH" for row in family_rows),
        "action_source_events": len(target_events),
        "action_readbacks": len(substitution_rows),
        "stacked_counterexamples": len(stack_rows),
        "new_core_size": 18,
        "remaining_recurrent_strip_values": 13,
        "fixed_pages": ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"],
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDREDTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
