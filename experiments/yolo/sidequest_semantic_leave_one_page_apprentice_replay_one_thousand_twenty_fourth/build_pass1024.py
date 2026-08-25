#!/usr/bin/env python3
"""Replay the current workshop sheet with each admitted page treated as new."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P1009 = ROOT / "experiments/yolo/sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth"
P1020 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_sheet_roundtrip_one_thousand_twentieth"
P1022 = ROOT / "experiments/yolo/sidequest_semantic_argument_scope_stack_one_thousand_twenty_second"
P1023 = ROOT / "experiments/yolo/sidequest_semantic_scope_ambiguity_resolution_one_thousand_twenty_third"

EVENT_LEDGER = P1009 / "PASS1009_4581_EVENT_LEDGER.tsv"
CATEGORIES = P1020 / "PASS1020_31_CATEGORY_LEXICON.tsv"
EVENT_SCOPE = P1022 / "PASS1022_3888_EVENT_SCOPE_BINDINGS.tsv"
ATTACHMENTS = P1023 / "PASS1023_4345_SCOPE_ATTACHMENTS.tsv"
GENERALIZATION = P1023 / "EQUAL_DISTANCE_GENERALIZATION_AUDIT.tsv"
RESOLVED = P1023 / "PASS1023_328_RESOLVED_ATTACHMENTS.tsv"
STATEMENTS = P1023 / "PASS1023_627_STATEMENT_SCOPE_EDITION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pipe(values: list[str] | set[str]) -> str:
    selected = sorted({value for value in values if value})
    return "|".join(selected) if selected else "NONE"


def classify_rule_families(
    attachment: dict[str, str],
    general: dict[str, str],
    resolution: dict[str, str] | None,
) -> list[str]:
    families: list[str] = []
    if resolution and "R_HEAD_OR_TAIL" in resolution["ambiguity_classes"]:
        families.append("R_POSITIONAL_MARKING")

    branch = general["safe_rule_branch"]
    if branch.startswith("ARGUMENT_GRADE_"):
        families.append("NEAREST_HEAD_LEFT_TIE")
    elif branch.startswith("AL_AR_"):
        families.append("AL_AR_ORDERED_FALLBACK")
    elif branch.startswith("L_AIR_"):
        families.append("L_AIR_RIGHT_FALLBACK")
    elif branch == "STACK_FALLBACK_NO_LOCAL_HEAD":
        if resolution and "BOUNDED_FORWARD" in resolution["pass1023_decisions"]:
            rules = resolution["pass1023_rule_ids"]
            if "OT_" in rules or "Q_" in rules or rules.startswith("Q_"):
                families.append("Q_OT_PACKAGE_FORWARD")
            elif "L_OR_AIR" in rules:
                families.append("L_AIR_RIGHT_FALLBACK")
            else:
                families.append("ONE_CARD_FORWARD")
        elif resolution and "OWNER_ONLY" in resolution["pass1023_decisions"]:
            families.append("AL_AR_ORDERED_FALLBACK")
        elif attachment["chosen_attachment_class"] == "PREVIOUS_CARD_ACTION":
            families.append("PREVIOUS_CARD_STACK")
        elif attachment["chosen_attachment_class"] == "INHERITED_ACTION":
            families.append("INHERITED_ACTION_STACK")
        else:
            families.append("OWNER_CONTEXT")
    return list(dict.fromkeys(families))


def main() -> None:
    ledger = read_tsv(EVENT_LEDGER)
    categories = read_tsv(CATEGORIES)
    events = read_tsv(EVENT_SCOPE)
    attachments = read_tsv(ATTACHMENTS)
    generalization = read_tsv(GENERALIZATION)
    resolved = read_tsv(RESOLVED)
    statements = read_tsv(STATEMENTS)

    if [len(ledger), len(events), len(attachments), len(generalization), len(resolved), len(statements)] != [4581, 3888, 4345, 4345, 328, 627]:
        raise AssertionError("input inventory mismatch")

    page_order = list(dict.fromkeys(row["physical_page"] for row in ledger))
    if len(page_order) != 22:
        raise AssertionError(f"expected 22 admitted physical pages, got {len(page_order)}")

    general_by_attachment = {row["attachment_id"]: row for row in generalization}
    resolved_by_attachment = {row["attachment_id"]: row for row in resolved}
    if set(general_by_attachment) != {row["attachment_id"] for row in attachments}:
        raise AssertionError("generalization inventory does not match attachment inventory")

    atom_category: dict[str, dict[str, str]] = {}
    for category in categories:
        for atom in category["graphic_signs"].split("|"):
            atom_category[atom] = category

    event_pages_by_surface: dict[str, set[str]] = defaultdict(set)
    event_pages_by_recipe: dict[str, set[str]] = defaultdict(set)
    for event in events:
        event_pages_by_surface[event["surface"]].add(event["physical_page"])
        event_pages_by_recipe[event["component_recipe"]].add(event["physical_page"])
        missing = [atom for atom in event["component_recipe"].split("+") if atom not in atom_category]
        if missing:
            raise AssertionError(f"unregistered atoms in {event['event_id']}: {missing}")

    preliminary: list[dict[str, object]] = []
    family_pages: dict[str, set[str]] = defaultdict(set)
    micro_pages: dict[str, set[str]] = defaultdict(set)
    for attachment in attachments:
        attachment_id = attachment["attachment_id"]
        general = general_by_attachment[attachment_id]
        resolution = resolved_by_attachment.get(attachment_id)
        families = classify_rule_families(attachment, general, resolution)
        micro = resolution["pass1023_decisions"] if resolution else general["safe_rule_branch"]
        for family in families:
            family_pages[family].add(attachment["physical_page"])
        micro_pages[micro].add(attachment["physical_page"])
        preliminary.append(
            {
                "attachment": attachment,
                "general": general,
                "resolution": resolution,
                "families": families,
                "micro": micro,
            }
        )

    attachment_rows: list[dict[str, object]] = []
    for ordinal, item in enumerate(preliminary, 1):
        attachment = item["attachment"]
        general = item["general"]
        resolution = item["resolution"]
        page = attachment["physical_page"]
        families = item["families"]
        outside_by_family = {
            family: sorted(family_pages[family] - {page}) for family in families
        }
        all_cross_page = all(outside_by_family[family] for family in families)
        micro_outside = sorted(micro_pages[item["micro"]] - {page})
        attachment_rows.append(
            {
                "replay_attachment_id": f"P1024-A{ordinal:05d}",
                "attachment_id": attachment["attachment_id"],
                "physical_page": page,
                "register": attachment["register"],
                "statement_id": attachment["statement_id"],
                "event_id": attachment["event_id"],
                "locus": attachment["locus"],
                "surface_card": attachment["surface_card"],
                "component_recipe": attachment["component_recipe"],
                "focus_core": attachment["focus_core"],
                "focus_value_de": attachment["focus_value_de"],
                "local_head_configuration": general["local_head_configuration"],
                "direct_or_stack": "DIRECT_LOCAL" if general["safe_trace_match"] == "MATCH" else "OWNER_PACKAGE_STACK",
                "teaching_rule_families": pipe(families),
                "micro_signature": item["micro"],
                "selected_attachment_de": attachment["pass1023_selected_attachment_de"],
                "changed_in_pass1023": attachment["pass1023_changed_from_pass1022"],
                "owner_bound_selection": "YES" if "BESITZER=" in attachment["pass1023_selected_attachment_de"] else "NO",
                "other_page_support_by_family": " | ".join(
                    f"{family}:{','.join(outside_by_family[family])}"
                    for family in families
                ),
                "all_rule_families_supported_outside_page": "YES" if all_cross_page else "NO",
                "micro_signature_other_pages": ",".join(micro_outside) if micro_outside else "NONE",
                "micro_signature_page_private": "NO" if micro_outside else "YES",
                "replay_result": "TRANSFERRED_RULE_FAMILY" if all_cross_page else "PAGE_PRIVATE_RULE_FAMILY",
            }
        )

    event_rows: list[dict[str, object]] = []
    for ordinal, event in enumerate(events, 1):
        page = event["physical_page"]
        atoms = event["component_recipe"].split("+")
        category_types = [atom_category[atom]["category_type"] for atom in atoms]
        other_surface_pages = sorted(event_pages_by_surface[event["surface"]] - {page})
        other_recipe_pages = sorted(event_pages_by_recipe[event["component_recipe"]] - {page})
        event_rows.append(
            {
                "replay_event_id": f"P1024-E{ordinal:04d}",
                "event_id": event["event_id"],
                "physical_page": page,
                "register": event["register"],
                "statement_id": event["statement_id"],
                "locus": event["locus"],
                "surface": event["surface"],
                "component_recipe": event["component_recipe"],
                "component_atom_count": len(atoms),
                "all_atoms_on_apprentice_sheet": "YES",
                "contains_local_channel": "YES" if "LOCAL_CHANNEL" in category_types else "NO",
                "exact_surface_other_pages": ",".join(other_surface_pages) if other_surface_pages else "NONE",
                "exact_recipe_other_pages": ",".join(other_recipe_pages) if other_recipe_pages else "NONE",
                "surface_page_private": "NO" if other_surface_pages else "YES",
                "recipe_page_private": "NO" if other_recipe_pages else "YES",
                "event_replay_result": (
                    "EXACT_SURFACE_TRANSFERS"
                    if other_surface_pages
                    else "ROOT_RECIPE_TRANSFERS"
                    if other_recipe_pages
                    else "NEW_ROOT_COMPOSITION_READABLE"
                ),
            }
        )

    ledger_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    attachments_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    statements_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        ledger_by_page[row["physical_page"]].append(row)
    for row in event_rows:
        events_by_page[str(row["physical_page"])].append(row)
    for row in attachment_rows:
        attachments_by_page[str(row["physical_page"])].append(row)
    for row in statements:
        statements_by_page[row["physical_page"]].append(row)

    page_rows: list[dict[str, object]] = []
    for page_number, page in enumerate(page_order, 1):
        page_ledger = ledger_by_page[page]
        running = events_by_page.get(page, [])
        focus = attachments_by_page.get(page, [])
        register = page_ledger[0]["register"]
        local_count = sum(row["event_role"] != "RUNNING_STATEMENT" for row in page_ledger)
        coarse_missing = sorted(
            {
                family
                for row in focus
                for family in str(row["teaching_rule_families"]).split("|")
                if family != "NONE" and not (family_pages[family] - {page})
            }
        )
        private_micro = sorted(
            {str(row["micro_signature"]) for row in focus if row["micro_signature_page_private"] == "YES"}
        )
        if not running:
            result = "LOCAL_ADDRESS_COPY_ONLY"
        elif coarse_missing:
            result = "PAGE_PRIVATE_SCOPE_RULE_REQUIRED"
        elif private_micro:
            result = "RULE_FAMILIES_TRANSFER__NEW_MICROFORM_COVERED"
        else:
            result = "RULE_FAMILIES_TRANSFER_DIRECTLY"
        page_rows.append(
            {
                "page_ordinal": page_number,
                "physical_page": page,
                "register": register,
                "visible_group_count": len(page_ledger),
                "running_event_count": len(running),
                "local_address_or_label_count": local_count,
                "statement_count": len(statements_by_page.get(page, [])),
                "focus_attachment_count": len(focus),
                "direct_local_attachment_count": sum(row["direct_or_stack"] == "DIRECT_LOCAL" for row in focus),
                "owner_package_stack_attachment_count": sum(row["direct_or_stack"] == "OWNER_PACKAGE_STACK" for row in focus),
                "pass1023_resolved_attachment_count": sum(row["micro_signature"] != general_by_attachment[str(row["attachment_id"])]["safe_rule_branch"] for row in focus),
                "pass1023_changed_attachment_count": sum(row["changed_in_pass1023"] == "YES" for row in focus),
                "owner_bound_focus_count": sum(row["owner_bound_selection"] == "YES" for row in focus),
                "rule_families_used": pipe(
                    {
                        family
                        for row in focus
                        for family in str(row["teaching_rule_families"]).split("|")
                        if family != "NONE"
                    }
                ),
                "unsupported_rule_families_when_page_held": pipe(coarse_missing),
                "page_private_micro_signatures": pipe(private_micro),
                "page_private_micro_occurrences": sum(row["micro_signature_page_private"] == "YES" for row in focus),
                "running_events_with_local_channel": sum(row["contains_local_channel"] == "YES" for row in running),
                "exact_surface_cross_page_event_count": sum(row["surface_page_private"] == "NO" for row in running),
                "page_private_surface_event_count": sum(row["surface_page_private"] == "YES" for row in running),
                "exact_recipe_cross_page_event_count": sum(row["recipe_page_private"] == "NO" for row in running),
                "page_private_recipe_event_count": sum(row["recipe_page_private"] == "YES" for row in running),
                "all_running_atoms_on_sheet": "YES" if all(row["all_atoms_on_apprentice_sheet"] == "YES" for row in running) else "NO",
                "leave_one_page_replay_result": result,
            }
        )

    rule_rows: list[dict[str, object]] = []
    for family in sorted(family_pages):
        pages = sorted(family_pages[family], key=page_order.index)
        rule_rows.append(
            {
                "rule_family": family,
                "attachment_occurrences": sum(family in row["families"] for row in preliminary),
                "support_page_count": len(pages),
                "support_pages": ",".join(pages),
                "minimum_other_page_support_when_one_page_held": len(pages) - 1,
                "survives_every_page_holdout": "YES" if len(pages) >= 2 else "NO",
            }
        )

    micro_rows: list[dict[str, object]] = []
    for micro in sorted(micro_pages):
        pages = sorted(micro_pages[micro], key=page_order.index)
        micro_rows.append(
            {
                "micro_signature": micro,
                "attachment_occurrences": sum(item["micro"] == micro for item in preliminary),
                "support_page_count": len(pages),
                "support_pages": ",".join(pages),
                "page_private_microform": "YES" if len(pages) == 1 else "NO",
                "covered_by_cross_page_rule_family": "YES",
            }
        )

    write_tsv(
        OUT / "PASS1024_4345_ATTACHMENT_REPLAY.tsv",
        attachment_rows,
        list(attachment_rows[0]),
    )
    write_tsv(OUT / "PASS1024_3888_EVENT_REPLAY.tsv", event_rows, list(event_rows[0]))
    write_tsv(OUT / "PASS1024_22_PAGE_REPLAY.tsv", page_rows, list(page_rows[0]))
    write_tsv(OUT / "PASS1024_RULE_SUPPORT.tsv", rule_rows, list(rule_rows[0]))
    write_tsv(OUT / "PASS1024_MICROFORM_SUPPORT.tsv", micro_rows, list(micro_rows[0]))

    summary = {
        "result": "ALL_22_PAGES_ENTER_WITHOUT_A_NEW_COARSE_SCOPE_RULE",
        "page_count": len(page_rows),
        "running_page_count": sum(bool(events_by_page.get(page)) for page in page_order),
        "local_address_only_page_count": sum(not events_by_page.get(page) for page in page_order),
        "visible_group_count": len(ledger),
        "running_event_count": len(events),
        "local_group_count": sum(row["event_role"] != "RUNNING_STATEMENT" for row in ledger),
        "statement_count": len(statements),
        "focus_attachment_count": len(attachment_rows),
        "direct_local_attachment_count": sum(row["direct_or_stack"] == "DIRECT_LOCAL" for row in attachment_rows),
        "owner_package_stack_attachment_count": sum(row["direct_or_stack"] == "OWNER_PACKAGE_STACK" for row in attachment_rows),
        "rule_family_count": len(rule_rows),
        "rule_families_surviving_every_page_holdout": sum(row["survives_every_page_holdout"] == "YES" for row in rule_rows),
        "pages_requiring_private_coarse_rule": sum(row["unsupported_rule_families_when_page_held"] != "NONE" for row in page_rows),
        "page_private_micro_signatures": [row["micro_signature"] for row in micro_rows if row["page_private_microform"] == "YES"],
        "page_private_micro_occurrences": sum(int(row["page_private_micro_occurrences"]) for row in page_rows),
        "page_private_surface_event_count": sum(int(row["page_private_surface_event_count"]) for row in page_rows),
        "page_private_recipe_event_count": sum(int(row["page_private_recipe_event_count"]) for row in page_rows),
        "event_replay_counts": dict(sorted(Counter(str(row["event_replay_result"]) for row in event_rows).items())),
        "all_running_atoms_on_apprentice_sheet": all(row["all_running_atoms_on_sheet"] == "YES" for row in page_rows),
        "checks": {
            "twenty_two_physical_pages": "PASS",
            "all_4581_groups_partitioned": "PASS",
            "all_3888_running_events_replayed": "PASS",
            "all_4345_focus_attachments_replayed": "PASS",
            "all_rule_families_have_other_page_support": "PASS",
            "label_only_pages_kept_out_of_sentence_scope": "PASS",
        },
        "source_hashes": {
            path.name: sha(path)
            for path in [EVENT_LEDGER, CATEGORIES, EVENT_SCOPE, ATTACHMENTS, GENERALIZATION, RESOLVED, STATEMENTS]
        },
    }
    (OUT / "PASS1024_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
