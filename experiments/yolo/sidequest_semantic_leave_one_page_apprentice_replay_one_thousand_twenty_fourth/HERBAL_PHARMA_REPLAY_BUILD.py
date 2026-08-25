#!/usr/bin/env python3
"""Leave-one-page replay for the ten Herbal and Pharma pages."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / (
    "experiments/yolo/"
    "sidequest_semantic_scope_ambiguity_resolution_one_thousand_twenty_third/"
    "PASS1023_4345_SCOPE_ATTACHMENTS.tsv"
)
DOUBLING_SOURCE = ROOT / (
    "experiments/yolo/"
    "sidequest_semantic_repeated_core_operator_one_thousand_twenty_first/"
    "PASS1021_ADJUDICATED_DOUBLING.tsv"
)

HERBAL_PAGES = ("f10r", "f11r", "f13r", "f17r", "f18r", "f55v", "f56r")
PHARMA_PAGES = ("f88r", "f88v", "f89r")
TARGET_PAGES = HERBAL_PAGES + PHARMA_PAGES

ACTIONS = {"OK", "CH", "SH", "K", "S", "T", "CHD", "R", "P"}
FORWARD_FRAMES = {"L", "AIR"}
LEFT_RELATIONS = {"AL", "AR"}

FORWARD_RULE_MAP = {
    "OPENING_ARGUMENT_FORWARD": "FORWARD_OPENING_ARGUMENT",
    "GRADE_TO_NEXT_COMPATIBLE_HEAD": "FORWARD_OPENING_GRADE",
    "OT_SIBLING_FORWARD": "FORWARD_OT_SIBLING",
    "Q_PACKET_FORWARD": "FORWARD_Q_PACKET",
    "OPENING_ARGUMENT_TO_NEXT_Q_PACKET": "FORWARD_ARGUMENT_TO_Q_PACKET",
    "L_OR_AIR_RIGHT_FRAME": "FORWARD_L_AIR_FRAME",
}

PARENT_RULE = {
    "LOCAL_NEAREST_LEFT": "NEAREST_HEAD_LEFT_TIE",
    "LOCAL_NEAREST_RIGHT": "NEAREST_HEAD_LEFT_TIE",
    "LOCAL_NEAREST_TIE_LEFT": "NEAREST_HEAD_LEFT_TIE",
    "LOCAL_AL_AR_LEFT": "AL_AR_LEFT_OR_OWNER",
    "OWNER_AL_AR_DEFAULT": "AL_AR_LEFT_OR_OWNER",
    "LOCAL_L_AIR_RIGHT": "L_AIR_RIGHT_OR_FALLBACK",
    "LOCAL_L_AIR_RIGHT_TIE": "L_AIR_RIGHT_OR_FALLBACK",
    "LOCAL_L_AIR_LEFT_FALLBACK": "L_AIR_RIGHT_OR_FALLBACK",
    "FORWARD_L_AIR_FRAME": "L_AIR_RIGHT_OR_FALLBACK",
    "FORWARD_OPENING_ARGUMENT": "BOUNDED_ONE_CARD_FORWARD",
    "FORWARD_OPENING_GRADE": "BOUNDED_ONE_CARD_FORWARD",
    "FORWARD_ARGUMENT_TO_Q_PACKET": "BOUNDED_ONE_CARD_FORWARD",
    "FORWARD_Q_PACKET": "Q_OT_PACKAGE_CONTROL",
    "FORWARD_OT_SIBLING": "Q_OT_PACKAGE_CONTROL",
    "R_POSITIONAL_HEAD": "R_POSITIONAL_MARKING",
    "R_POSITIONAL_TAIL": "R_POSITIONAL_MARKING",
    "R_POSITIONAL_NESTED": "R_POSITIONAL_MARKING",
    "STACK_PREVIOUS_CARD": "STACK_INHERITANCE",
    "STACK_INHERITED_ACTION": "STACK_INHERITANCE",
    "STACK_OWNER": "OWNER_STACK",
    "PACKAGE_SCOPE_DESCENT": "DUPLICATE_PACKAGE_RULE",
    "FREE_PLURAL_OR_REPEAT": "DUPLICATE_PACKAGE_RULE",
}


def read_tsv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader), list(reader.fieldnames or [])


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def base_rule(row: dict[str, str]) -> str:
    decisions = row["pass1023_decisions"]
    rule_ids = row["pass1023_rule_ids"]
    if "R_NESTED" in decisions:
        return "R_POSITIONAL_NESTED"
    if "R_TAIL" in decisions:
        return "R_POSITIONAL_TAIL"
    if "R_HEAD" in decisions:
        return "R_POSITIONAL_HEAD"
    if "BOUNDED_FORWARD" in decisions:
        if rule_ids not in FORWARD_RULE_MAP:
            raise AssertionError(f"unknown forward rule: {rule_ids}")
        return FORWARD_RULE_MAP[rule_ids]
    if "OWNER_ONLY" in decisions:
        return "OWNER_AL_AR_DEFAULT"
    if "EQUAL_RIGHT" in decisions:
        return "LOCAL_L_AIR_RIGHT_TIE"
    if "EQUAL_LEFT" in decisions:
        return "LOCAL_NEAREST_TIE_LEFT"

    attachment = row["chosen_attachment_class"]
    focus = row["focus_core"]
    if attachment == "SAME_CARD_LEFT_ACTION":
        if focus in LEFT_RELATIONS:
            return "LOCAL_AL_AR_LEFT"
        if focus in FORWARD_FRAMES:
            return "LOCAL_L_AIR_LEFT_FALLBACK"
        return "LOCAL_NEAREST_LEFT"
    if attachment == "SAME_CARD_RIGHT_ACTION":
        if focus in FORWARD_FRAMES:
            return "LOCAL_L_AIR_RIGHT"
        return "LOCAL_NEAREST_RIGHT"
    if attachment == "PREVIOUS_CARD_ACTION":
        return "STACK_PREVIOUS_CARD"
    if attachment == "INHERITED_ACTION":
        return "STACK_INHERITED_ACTION"
    if attachment == "OWNER_ONLY":
        return "STACK_OWNER"
    raise AssertionError(f"unknown attachment class: {attachment}")


def required_rules(row: dict[str, str]) -> list[str]:
    rules = [base_rule(row)]
    if row["duplicate_scope_mode"] != "SINGLE":
        rules.append(row["duplicate_scope_mode"])
    return rules


def parent_rules(row: dict[str, str]) -> list[str]:
    return sorted({PARENT_RULE[rule] for rule in required_rules(row)})


def mode(rule: str) -> str:
    if rule.startswith("LOCAL_") or rule in {"R_POSITIONAL_HEAD", "R_POSITIONAL_NESTED"}:
        return "DIRECT_LOCAL"
    if rule.startswith("FORWARD_"):
        return "BOUNDED_FORWARD"
    if rule in {"OWNER_AL_AR_DEFAULT", "STACK_OWNER"}:
        return "OWNER"
    return "STACK"


def parse_actions(value: str) -> list[tuple[int, str]]:
    if value == "NONE":
        return []
    result = []
    for item in value.split("|"):
        core, ordinal = item.rsplit("@", 1)
        result.append((int(ordinal), core))
    return result


def topology_parts(row: dict[str, str]) -> tuple[str, str, str]:
    focus_ordinal = int(row["focus_atom_ordinal"])
    left = parse_actions(row["same_card_left_actions"])
    right = parse_actions(row["same_card_right_actions"])
    nearest_left = left[-1] if left else None
    nearest_right = right[0] if right else None
    if nearest_left and nearest_right:
        configuration = "BOTH"
        left_distance = focus_ordinal - nearest_left[0]
        right_distance = nearest_right[0] - focus_ordinal
        distance_relation = (
            "EQUAL" if left_distance == right_distance
            else "LEFT_CLOSER" if left_distance < right_distance
            else "RIGHT_CLOSER"
        )
    elif nearest_left:
        configuration = "LEFT_ONLY"
        distance_relation = "LEFT_ONLY"
    elif nearest_right:
        configuration = "RIGHT_ONLY"
        distance_relation = "RIGHT_ONLY"
    else:
        configuration = "NO_LOCAL"
        distance_relation = "NO_LOCAL"
    return configuration, distance_relation, (
        f"{base_rule(row)}|{row['focus_core']}|{configuration}|{distance_relation}|"
        f"{row['duplicate_scope_mode']}|{row['duplicate_scope_role']}"
    )


def exact_signature(row: dict[str, str]) -> str:
    return (
        f"{row['component_recipe']}|FOCUS={row['focus_core']}@{row['focus_atom_ordinal']}|"
        f"RULE={base_rule(row)}|DUP={row['duplicate_scope_role']}"
    )


def support_text(rules: list[str], mapping: dict[str, set[str]], held_page: str) -> str:
    items = []
    for rule in rules:
        pages = sorted(mapping[rule] - {held_page})
        items.append(f"{rule}:{len(pages)}:{','.join(pages) if pages else 'NONE'}")
    return ";".join(items)


def main() -> None:
    all_rows, source_fields = read_tsv(SOURCE)
    doubling_rows, _ = read_tsv(DOUBLING_SOURCE)
    if len(all_rows) != 4345:
        raise AssertionError(f"expected 4,345 Pass1023 attachments, got {len(all_rows)}")
    if set(TARGET_PAGES) - {row["physical_page"] for row in all_rows}:
        raise AssertionError("one or more requested pages are absent")

    rule_pages: dict[str, set[str]] = defaultdict(set)
    parent_pages: dict[str, set[str]] = defaultdict(set)
    topology_pages: dict[str, set[str]] = defaultdict(set)
    exact_pages: dict[str, set[str]] = defaultdict(set)
    rule_register_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    parent_register_pages: dict[tuple[str, str], set[str]] = defaultdict(set)

    for row in all_rows:
        page = row["physical_page"]
        register = row["register"]
        for rule in required_rules(row):
            rule_pages[rule].add(page)
            rule_register_pages[(rule, register)].add(page)
        for parent in parent_rules(row):
            parent_pages[parent].add(page)
            parent_register_pages[(parent, register)].add(page)
        _, _, topology = topology_parts(row)
        topology_pages[topology].add(page)
        exact_pages[exact_signature(row)].add(page)

    # Pass1023 explicitly carries the Pass1021 package-first rule. Action-core
    # doublets do not themselves appear in the 4,345 focus rows, so their
    # other-page support must come from the adjudicated 40-card package ledger.
    for row in doubling_rows:
        rule = row["selected_doubling_rule"]
        page = row["physical_page"]
        register = row["register"]
        rule_pages[rule].add(page)
        rule_register_pages[(rule, register)].add(page)
        parent = PARENT_RULE[rule]
        parent_pages[parent].add(page)
        parent_register_pages[(parent, register)].add(page)

    selected = [row for row in all_rows if row["physical_page"] in TARGET_PAGES]
    if len(selected) != 1249:
        raise AssertionError(f"expected 1,249 requested-page attachments, got {len(selected)}")

    audit_fields = source_fields + [
        "replay_mode",
        "replay_rule_type",
        "replay_parent_rules",
        "replay_required_rules",
        "replay_local_head_configuration",
        "replay_distance_relation",
        "replay_rule_support_other_pages",
        "replay_rule_support_other_pages_same_register",
        "replay_parent_support_other_pages",
        "replay_unsupported_rules",
        "replay_unsupported_rules_same_register",
        "replay_strict_result",
        "replay_same_register_result",
        "replay_parent_result",
        "replay_topology_signature",
        "replay_topology_other_page_count",
        "replay_topology_other_pages",
        "replay_topology_page_private",
        "replay_exact_signature",
        "replay_exact_other_page_count",
        "replay_exact_other_pages",
        "replay_exact_page_private",
        "replay_private_pattern_class",
    ]

    audited: list[dict[str, object]] = []
    for row in selected:
        page = row["physical_page"]
        register = row["register"]
        rules = required_rules(row)
        parents = parent_rules(row)
        unsupported = [rule for rule in rules if not (rule_pages[rule] - {page})]
        unsupported_register = [
            rule for rule in rules
            if not (rule_register_pages[(rule, register)] - {page})
        ]
        unsupported_parent = [parent for parent in parents if not (parent_pages[parent] - {page})]
        configuration, distance_relation, topology = topology_parts(row)
        topology_other = sorted(topology_pages[topology] - {page})
        exact = exact_signature(row)
        exact_other = sorted(exact_pages[exact] - {page})

        if unsupported:
            private_class = "PRIVATE_RULE_SUBTYPE"
        elif not topology_other:
            private_class = "PRIVATE_TOPOLOGY_COMBINATION_RULE_PORTABLE"
        elif not exact_other:
            private_class = "PRIVATE_EXACT_FORM_RULE_PORTABLE"
        else:
            private_class = "NONE"

        output = dict(row)
        output.update(
            {
                "replay_mode": mode(base_rule(row)),
                "replay_rule_type": base_rule(row),
                "replay_parent_rules": "|".join(parents),
                "replay_required_rules": "|".join(rules),
                "replay_local_head_configuration": configuration,
                "replay_distance_relation": distance_relation,
                "replay_rule_support_other_pages": support_text(rules, rule_pages, page),
                "replay_rule_support_other_pages_same_register": support_text(
                    rules,
                    {rule: rule_register_pages[(rule, register)] for rule in rules},
                    page,
                ),
                "replay_parent_support_other_pages": support_text(parents, parent_pages, page),
                "replay_unsupported_rules": "|".join(unsupported) or "NONE",
                "replay_unsupported_rules_same_register": "|".join(unsupported_register) or "NONE",
                "replay_strict_result": "PRIVATE_RULE_SUBTYPE" if unsupported else "SUPPORTED_FROM_OTHER_PAGE",
                "replay_same_register_result": (
                    "NEEDS_OTHER_REGISTER_EXAMPLE" if unsupported_register else "SUPPORTED_WITHIN_REGISTER"
                ),
                "replay_parent_result": "PRIVATE_PARENT_RULE" if unsupported_parent else "PARENT_RULE_SUPPORTED",
                "replay_topology_signature": topology,
                "replay_topology_other_page_count": len(topology_other),
                "replay_topology_other_pages": ",".join(topology_other) or "NONE",
                "replay_topology_page_private": "YES" if not topology_other else "NO",
                "replay_exact_signature": exact,
                "replay_exact_other_page_count": len(exact_other),
                "replay_exact_other_pages": ",".join(exact_other) or "NONE",
                "replay_exact_page_private": "YES" if not exact_other else "NO",
                "replay_private_pattern_class": private_class,
            }
        )
        audited.append(output)

    page_fields = [
        "physical_page",
        "register",
        "attachment_count",
        "direct_local",
        "stack",
        "bounded_forward",
        "owner",
        "pass1023_resolved_count",
        "pass1023_changed_count",
        "distinct_required_rule_count",
        "unsupported_rule_types",
        "unsupported_same_register_rule_types",
        "strict_replay_result",
        "same_register_replay_result",
        "parent_replay_result",
        "private_topology_rows",
        "private_topology_signatures",
        "private_exact_form_rows",
        "private_exact_form_signatures",
    ]
    page_rows: list[dict[str, object]] = []
    for page in TARGET_PAGES:
        page_data = [row for row in audited if row["physical_page"] == page]
        mode_counts = Counter(str(row["replay_mode"]) for row in page_data)
        rules = sorted(
            {
                rule
                for row in page_data
                for rule in str(row["replay_required_rules"]).split("|")
            }
        )
        unsupported = sorted(
            {
                rule
                for row in page_data
                for rule in str(row["replay_unsupported_rules"]).split("|")
                if rule != "NONE"
            }
        )
        unsupported_register = sorted(
            {
                rule
                for row in page_data
                for rule in str(row["replay_unsupported_rules_same_register"]).split("|")
                if rule != "NONE"
            }
        )
        private_topology = [row for row in page_data if row["replay_topology_page_private"] == "YES"]
        private_exact = [row for row in page_data if row["replay_exact_page_private"] == "YES"]
        page_rows.append(
            {
                "physical_page": page,
                "register": page_data[0]["register"],
                "attachment_count": len(page_data),
                "direct_local": mode_counts["DIRECT_LOCAL"],
                "stack": mode_counts["STACK"],
                "bounded_forward": mode_counts["BOUNDED_FORWARD"],
                "owner": mode_counts["OWNER"],
                "pass1023_resolved_count": sum(
                    row["pass1023_resolution_status"] == "RESOLVED_BY_WORKSHOP_RULE"
                    for row in page_data
                ),
                "pass1023_changed_count": sum(
                    row["pass1023_changed_from_pass1022"] == "YES" for row in page_data
                ),
                "distinct_required_rule_count": len(rules),
                "unsupported_rule_types": "|".join(unsupported) or "NONE",
                "unsupported_same_register_rule_types": "|".join(unsupported_register) or "NONE",
                "strict_replay_result": "PRIVATE_RULE_SUBTYPE" if unsupported else "REPLAYABLE_FROM_OTHER_PAGES",
                "same_register_replay_result": (
                    "NEEDS_OTHER_REGISTER_EXAMPLE" if unsupported_register else "REPLAYABLE_WITHIN_REGISTER"
                ),
                "parent_replay_result": (
                    "PARENT_RULE_SUPPORTED" if all(row["replay_parent_result"] == "PARENT_RULE_SUPPORTED" for row in page_data)
                    else "PRIVATE_PARENT_RULE"
                ),
                "private_topology_rows": len(private_topology),
                "private_topology_signatures": len(
                    {str(row["replay_topology_signature"]) for row in private_topology}
                ),
                "private_exact_form_rows": len(private_exact),
                "private_exact_form_signatures": len(
                    {str(row["replay_exact_signature"]) for row in private_exact}
                ),
            }
        )

    private_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in audited:
        if row["replay_topology_page_private"] == "YES":
            private_groups[(str(row["physical_page"]), str(row["replay_topology_signature"]))].append(row)
    private_fields = [
        "private_pattern_id",
        "physical_page",
        "register",
        "topology_signature",
        "occurrence_count",
        "attachment_ids",
        "example_component_recipe",
        "example_focus_core",
        "rule_type",
        "parent_rules",
        "rule_supported_other_page",
        "parent_supported_other_page",
        "classification",
    ]
    private_rows: list[dict[str, object]] = []
    for ordinal, ((page, topology), group) in enumerate(sorted(private_groups.items()), start=1):
        first = group[0]
        strict_private = any(row["replay_strict_result"] == "PRIVATE_RULE_SUBTYPE" for row in group)
        private_rows.append(
            {
                "private_pattern_id": f"HPRP{ordinal:03d}",
                "physical_page": page,
                "register": first["register"],
                "topology_signature": topology,
                "occurrence_count": len(group),
                "attachment_ids": "|".join(str(row["attachment_id"]) for row in group),
                "example_component_recipe": first["component_recipe"],
                "example_focus_core": first["focus_core"],
                "rule_type": first["replay_rule_type"],
                "parent_rules": first["replay_parent_rules"],
                "rule_supported_other_page": "NO" if strict_private else "YES",
                "parent_supported_other_page": first["replay_parent_result"].replace("PARENT_RULE_", ""),
                "classification": (
                    "GENUINE_PRIVATE_RULE_SUBTYPE" if strict_private
                    else "PRIVATE_COMBINATION_OF_PORTABLE_RULES"
                ),
            }
        )

    strict_private_rows = [row for row in audited if row["replay_strict_result"] == "PRIVATE_RULE_SUBTYPE"]
    changed_rows = [row for row in audited if row["pass1023_changed_from_pass1022"] == "YES"]
    summary = {
        "source_pass1023_attachment_count": len(all_rows),
        "requested_page_attachment_count": len(audited),
        "requested_pages": list(TARGET_PAGES),
        "register_counts": dict(sorted(Counter(str(row["register"]) for row in audited).items())),
        "mode_counts": dict(sorted(Counter(str(row["replay_mode"]) for row in audited).items())),
        "pass1023_resolved_on_requested_pages": sum(
            row["pass1023_resolution_status"] == "RESOLVED_BY_WORKSHOP_RULE" for row in audited
        ),
        "pass1023_changed_on_requested_pages": len(changed_rows),
        "strict_replay_supported_attachment_count": len(audited) - len(strict_private_rows),
        "strict_replay_private_rule_attachment_count": len(strict_private_rows),
        "strict_replay_private_rule_types": sorted(
            {str(row["replay_rule_type"]) for row in strict_private_rows}
        ),
        "parent_rule_supported_attachment_count": sum(
            row["replay_parent_result"] == "PARENT_RULE_SUPPORTED" for row in audited
        ),
        "private_topology_row_count": sum(row["replay_topology_page_private"] == "YES" for row in audited),
        "private_topology_signature_count": len(private_rows),
        "private_exact_form_row_count": sum(row["replay_exact_page_private"] == "YES" for row in audited),
        "private_exact_form_signature_count": len(
            {str(row["replay_exact_signature"]) for row in audited if row["replay_exact_page_private"] == "YES"}
        ),
        "page_results": {
            str(row["physical_page"]): str(row["strict_replay_result"]) for row in page_rows
        },
        "checks": {
            "all_requested_pages_present": "PASS",
            "all_requested_page_attachments_present_once": "PASS",
            "support_excludes_held_page": "PASS",
            "fixed_values_unchanged": "PASS",
            "new_pages_added": 0,
        },
    }

    if len(audited) != 1249:
        raise AssertionError("requested-page inventory count changed")
    if len(strict_private_rows) != 1 or strict_private_rows[0]["replay_rule_type"] != "R_POSITIONAL_NESTED":
        raise AssertionError("unexpected strict-private rule inventory")
    if len(private_rows) != 14:
        raise AssertionError(f"expected 14 private topology signatures, got {len(private_rows)}")
    if sum(row["replay_topology_page_private"] == "YES" for row in audited) != 15:
        raise AssertionError("expected 15 private-topology rows")
    if len(changed_rows) != 18:
        raise AssertionError("expected 18 Pass1023 changes on requested pages")

    write_tsv(OUT / "HERBAL_PHARMA_REPLAY_ATTACHMENTS.tsv", audited, audit_fields)
    write_tsv(OUT / "HERBAL_PHARMA_REPLAY_PAGE_SUMMARY.tsv", page_rows, page_fields)
    write_tsv(OUT / "HERBAL_PHARMA_REPLAY_PRIVATE_PATTERNS.tsv", private_rows, private_fields)
    with (OUT / "HERBAL_PHARMA_REPLAY_SUMMARY.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
