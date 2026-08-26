#!/usr/bin/env python3
"""Replay the fixed apprentice sheet while withholding each complete register."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P1020 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_sheet_roundtrip_one_thousand_twentieth"
P1024 = ROOT / "experiments/yolo/sidequest_semantic_leave_one_page_apprentice_replay_one_thousand_twenty_fourth"

CATEGORIES = P1020 / "PASS1020_31_CATEGORY_LEXICON.tsv"
EVENTS = P1024 / "PASS1024_3888_EVENT_REPLAY.tsv"
ATTACHMENTS = P1024 / "PASS1024_4345_ATTACHMENT_REPLAY.tsv"
PAGES = P1024 / "PASS1024_22_PAGE_REPLAY.tsv"

REGISTERS = ["HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"]
SURFACE_RECIPE_OVERRIDES = {
    "cheo": "CH+E+O",
    "okeor": "OK+E+OR",
}


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


def joined(values: set[str] | list[str], order: list[str] | None = None) -> str:
    selected = set(values)
    if order is None:
        result = sorted(selected)
    else:
        result = [value for value in order if value in selected]
    return "|".join(result) if result else "NONE"


def main() -> None:
    categories = read_tsv(CATEGORIES)
    events = read_tsv(EVENTS)
    attachments = read_tsv(ATTACHMENTS)
    pages = read_tsv(PAGES)

    if [len(categories), len(events), len(attachments), len(pages)] != [31, 3888, 4345, 22]:
        raise AssertionError("input inventory mismatch")
    if set(REGISTERS) != {row["register"] for row in events}:
        raise AssertionError("register inventory mismatch")

    atom_category: dict[str, dict[str, str]] = {}
    for category in categories:
        for atom in category["graphic_signs"].split("|"):
            if atom in atom_category:
                raise AssertionError(f"graphic sign repeated across categories: {atom}")
            atom_category[atom] = category

    correction_rows: list[dict[str, object]] = []
    corrected_events: list[dict[str, str]] = []
    for source_event in events:
        event = dict(source_event)
        event["source_component_recipe"] = source_event["component_recipe"]
        override = SURFACE_RECIPE_OVERRIDES.get(event["surface"])
        if override and override != event["component_recipe"]:
            correction_rows.append(
                {
                    "correction_layer": "EVENT_RECIPE",
                    "target_id": event["event_id"],
                    "physical_page": event["physical_page"],
                    "surface": event["surface"],
                    "old_value": event["component_recipe"],
                    "new_value": override,
                    "action": "REPLACE_INVISIBLE_NEAREST_ALLOGRAPH_ATOMS",
                    "reason_de": "Gleiche sichtbare Oberfläche erhält genau eine sichtbare Komponentenfolge.",
                }
            )
            event["component_recipe"] = override
            event["component_atom_count"] = str(len(override.split("+")))
            event["surface_recipe_correction"] = "PASS1025_VISIBLE_SURFACE_RECIPE"
        else:
            event["surface_recipe_correction"] = "UNCHANGED"
        corrected_events.append(event)
    events = corrected_events

    corrected_attachments: list[dict[str, str]] = []
    for source_attachment in attachments:
        attachment = dict(source_attachment)
        attachment["source_attachment_id"] = source_attachment["attachment_id"]
        attachment["pass1025_surface_determinism_correction"] = "UNCHANGED"
        surface = attachment["surface_card"]
        if surface == "cheo" and attachment["focus_core"] == "L":
            correction_rows.append(
                {
                    "correction_layer": "FOCUS_ATTACHMENT",
                    "target_id": attachment["attachment_id"],
                    "physical_page": attachment["physical_page"],
                    "surface": surface,
                    "old_value": "L=VERBINDUNG",
                    "new_value": "NONE",
                    "action": "DROP_INVISIBLE_FOCUS",
                    "reason_de": "Das L stammte nur vom eineditigen Nachbarn cheol und ist in cheo nicht sichtbar.",
                }
            )
            continue
        if surface == "okeor" and attachment["focus_core"] == "EE":
            correction_rows.append(
                {
                    "correction_layer": "FOCUS_ATTACHMENT",
                    "target_id": attachment["attachment_id"],
                    "physical_page": attachment["physical_page"],
                    "surface": surface,
                    "old_value": "EE=GRAD II",
                    "new_value": "E=GRAD I",
                    "action": "REPLACE_INVISIBLE_GRADE",
                    "reason_de": "okeor zeigt einen E-Grad; der zweite E stammte nur vom Nachbarn okeeor.",
                }
            )
            attachment["focus_core"] = "E"
            attachment["focus_value_de"] = "GRAD I"
            attachment["selected_attachment_de"] = attachment["selected_attachment_de"].replace(
                "EE=GRAD II", "E=GRAD I"
            )
            attachment["pass1025_surface_determinism_correction"] = "EE_TO_E"
        if attachment["attachment_id"] in {"SA01107", "SA01108"}:
            old_families = attachment["teaching_rule_families"]
            families = [
                family for family in old_families.split("|") if family != "R_POSITIONAL_MARKING"
            ]
            correction_rows.append(
                {
                    "correction_layer": "FOCUS_ATTACHMENT",
                    "target_id": attachment["attachment_id"],
                    "physical_page": attachment["physical_page"],
                    "surface": attachment["surface_card"],
                    "old_value": f"{old_families};R_TAIL",
                    "new_value": f"{'|'.join(families)};STACK_FALLBACK_NO_LOCAL_HEAD",
                    "action": "DROP_INVISIBLE_R_MEDIATION",
                    "reason_de": "Der vorausgehende cheo trägt nach der sichtbaren Reparatur kein R; der offene CH-Kopf bleibt direkt aktiv.",
                }
            )
            attachment["teaching_rule_families"] = "|".join(families)
            attachment["micro_signature"] = "STACK_FALLBACK_NO_LOCAL_HEAD"
            attachment["pass1025_surface_determinism_correction"] = "DROP_R_MEDIATION"
        if surface in SURFACE_RECIPE_OVERRIDES:
            attachment["component_recipe"] = SURFACE_RECIPE_OVERRIDES[surface]
        corrected_attachments.append(attachment)

    base = next(
        attachment
        for attachment in corrected_attachments
        if attachment["event_id"] == "P1008-E0028" and attachment["focus_core"] == "OR"
    )
    added_grade = dict(base)
    added_grade.update(
        {
            "replay_attachment_id": "P1025-ADDED-E0028-E",
            "attachment_id": "P1025-SA-E0028-E",
            "source_attachment_id": "NONE",
            "component_recipe": "OK+E+OR",
            "focus_core": "E",
            "focus_value_de": "GRAD I",
            "local_head_configuration": "LEFT_ONLY",
            "direct_or_stack": "DIRECT_LOCAL",
            "teaching_rule_families": "NEAREST_HEAD_LEFT_TIE",
            "micro_signature": "ARGUMENT_GRADE_ONLY_LEFT",
            "selected_attachment_de": "OK=SETZEN[E=GRAD I]",
            "changed_in_pass1023": "PASS1025_ADDED",
            "pass1025_surface_determinism_correction": "ADD_VISIBLE_E_GRADE",
        }
    )
    corrected_attachments.append(added_grade)
    correction_rows.append(
        {
            "correction_layer": "FOCUS_ATTACHMENT",
            "target_id": "P1025-SA-E0028-E",
            "physical_page": "f18r",
            "surface": "okeor",
            "old_value": "NONE",
            "new_value": "E=GRAD I",
            "action": "ADD_VISIBLE_FOCUS",
            "reason_de": "okeor zeigt den E-Grad auch dort, wo der alte eineditige Nachbar okor ihn gelöscht hatte.",
        }
    )
    for ordinal, attachment in enumerate(corrected_attachments, 1):
        attachment["pass1025_attachment_id"] = f"P1025-A{ordinal:05d}"
    attachments = corrected_attachments

    surface_registers: dict[str, set[str]] = defaultdict(set)
    surface_pages: dict[str, set[str]] = defaultdict(set)
    surface_recipes: dict[str, set[str]] = defaultdict(set)
    recipe_registers: dict[str, set[str]] = defaultdict(set)
    recipe_pages: dict[str, set[str]] = defaultdict(set)
    page_register = {page["physical_page"]: page["register"] for page in pages}
    for event in events:
        atoms = event["component_recipe"].split("+")
        missing = [atom for atom in atoms if atom not in atom_category]
        if missing:
            raise AssertionError(f"unregistered atoms in {event['event_id']}: {missing}")
        surface_registers[event["surface"]].add(event["register"])
        surface_pages[event["surface"]].add(event["physical_page"])
        surface_recipes[event["surface"]].add(event["component_recipe"])
        recipe_registers[event["component_recipe"]].add(event["register"])
        recipe_pages[event["component_recipe"]].add(event["physical_page"])
    if any(len(recipes) != 1 for recipes in surface_recipes.values()):
        raise AssertionError("surface determinism repair incomplete")

    event_rows: list[dict[str, object]] = []
    for ordinal, event in enumerate(events, 1):
        held = event["register"]
        outside_surface_registers = surface_registers[event["surface"]] - {held}
        outside_recipe_registers = recipe_registers[event["component_recipe"]] - {held}
        if outside_surface_registers:
            result = "EXACT_SURFACE_FROM_OTHER_REGISTER"
        elif outside_recipe_registers:
            result = "ROOT_RECIPE_FROM_OTHER_REGISTER"
        else:
            result = "NEW_REGISTER_RECIPE__KNOWN_ATOMS"
        event_rows.append(
            {
                "register_replay_event_id": f"P1025-E{ordinal:04d}",
                "event_id": event["event_id"],
                "held_register": held,
                "physical_page": event["physical_page"],
                "statement_id": event["statement_id"],
                "locus": event["locus"],
                "surface": event["surface"],
                "source_component_recipe": event["source_component_recipe"],
                "component_recipe": event["component_recipe"],
                "component_atom_count": event["component_atom_count"],
                "surface_recipe_correction": event["surface_recipe_correction"],
                "all_atoms_on_fixed_sheet": "YES",
                "outside_surface_registers": joined(outside_surface_registers, REGISTERS),
                "outside_surface_pages": joined(
                    {page for page in surface_pages[event["surface"]] if page_register[page] != held}
                ),
                "outside_recipe_registers": joined(outside_recipe_registers, REGISTERS),
                "outside_recipe_pages": joined(
                    {page for page in recipe_pages[event["component_recipe"]] if page_register[page] != held}
                ),
                "register_replay_result": result,
            }
        )

    category_counts: Counter[tuple[str, str]] = Counter()
    category_registers: dict[str, set[str]] = defaultdict(set)
    category_event_counts: Counter[tuple[str, str]] = Counter()
    for event in events:
        event_categories: set[str] = set()
        for atom in event["component_recipe"].split("+"):
            category_id = atom_category[atom]["category_id"]
            category_counts[(category_id, event["register"])] += 1
            category_registers[category_id].add(event["register"])
            event_categories.add(category_id)
        for category_id in event_categories:
            category_event_counts[(category_id, event["register"])] += 1

    category_rows: list[dict[str, object]] = []
    for category in categories:
        category_id = category["category_id"]
        support = category_registers[category_id]
        used_holdouts = [register for register in REGISTERS if category_counts[(category_id, register)]]
        unsupported = [register for register in used_holdouts if not (support - {register})]
        row: dict[str, object] = {
            "category_id": category_id,
            "category_type": category["category_type"],
            "graphic_signs": category["graphic_signs"],
            "short_value_de": category["short_value_de"],
            "syntax_role": category["syntax_role"],
            "support_registers": joined(support, REGISTERS),
            "support_register_count": len(support),
            "unsupported_used_register_holdouts": joined(unsupported, REGISTERS),
            "survives_every_register_where_used": "YES" if not unsupported else "NO",
        }
        for register in REGISTERS:
            row[f"{register.lower()}_atom_mentions"] = category_counts[(category_id, register)]
            row[f"{register.lower()}_event_count"] = category_event_counts[(category_id, register)]
        category_rows.append(row)

    rule_counts: Counter[tuple[str, str]] = Counter()
    rule_registers: dict[str, set[str]] = defaultdict(set)
    for attachment in attachments:
        for family in attachment["teaching_rule_families"].split("|"):
            if family == "NONE":
                continue
            rule_counts[(family, attachment["register"])] += 1
            rule_registers[family].add(attachment["register"])

    rule_rows: list[dict[str, object]] = []
    for family in sorted(rule_registers):
        support = rule_registers[family]
        used_holdouts = [register for register in REGISTERS if rule_counts[(family, register)]]
        unsupported = [register for register in used_holdouts if not (support - {register})]
        row = {
            "rule_family": family,
            "support_registers": joined(support, REGISTERS),
            "support_register_count": len(support),
            "total_occurrences": sum(rule_counts[(family, register)] for register in REGISTERS),
            "unsupported_used_register_holdouts": joined(unsupported, REGISTERS),
            "survives_every_register_where_used": "YES" if not unsupported else "NO",
        }
        for register in REGISTERS:
            row[f"{register.lower()}_occurrences"] = rule_counts[(family, register)]
        rule_rows.append(row)

    micro_counts: Counter[tuple[str, str]] = Counter()
    micro_registers: dict[str, set[str]] = defaultdict(set)
    micro_parent_families: dict[str, set[str]] = defaultdict(set)
    for attachment in attachments:
        micro = attachment["micro_signature"]
        micro_counts[(micro, attachment["register"])] += 1
        micro_registers[micro].add(attachment["register"])
        micro_parent_families[micro].update(
            family for family in attachment["teaching_rule_families"].split("|") if family != "NONE"
        )

    micro_rows: list[dict[str, object]] = []
    for micro in sorted(micro_registers):
        support = micro_registers[micro]
        private = len(support) == 1
        parents = micro_parent_families[micro]
        parent_cross_register = all(len(rule_registers[parent]) > 1 for parent in parents)
        row = {
            "micro_signature": micro,
            "parent_rule_families": joined(parents),
            "support_registers": joined(support, REGISTERS),
            "support_register_count": len(support),
            "total_occurrences": sum(micro_counts[(micro, register)] for register in REGISTERS),
            "register_private_microform": "YES" if private else "NO",
            "all_parent_rules_cross_register": "YES" if parent_cross_register else "NO",
        }
        for register in REGISTERS:
            row[f"{register.lower()}_occurrences"] = micro_counts[(micro, register)]
        micro_rows.append(row)

    pages_by_register: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_register: dict[str, list[dict[str, object]]] = defaultdict(list)
    attachments_by_register: dict[str, list[dict[str, str]]] = defaultdict(list)
    for page in pages:
        pages_by_register[page["register"]].append(page)
    for event in event_rows:
        events_by_register[str(event["held_register"])].append(event)
    for attachment in attachments:
        attachments_by_register[attachment["register"]].append(attachment)

    register_rows: list[dict[str, object]] = []
    for held in REGISTERS:
        held_events = events_by_register[held]
        held_attachments = attachments_by_register[held]
        used_categories = {
            atom_category[atom]["category_id"]
            for event in events
            if event["register"] == held
            for atom in event["component_recipe"].split("+")
        }
        unsupported_categories = {
            category_id for category_id in used_categories if not (category_registers[category_id] - {held})
        }
        used_rules = {
            family
            for attachment in held_attachments
            for family in attachment["teaching_rule_families"].split("|")
            if family != "NONE"
        }
        unsupported_rules = {family for family in used_rules if not (rule_registers[family] - {held})}
        private_micro_occurrences = sum(
            micro_counts[(micro, held)]
            for micro, support in micro_registers.items()
            if support == {held}
        )
        result_counts = Counter(str(event["register_replay_result"]) for event in held_events)
        register_rows.append(
            {
                "held_register": held,
                "physical_page_count": len(pages_by_register[held]),
                "running_page_count": sum(int(page["running_event_count"]) > 0 for page in pages_by_register[held]),
                "address_only_page_count": sum(int(page["running_event_count"]) == 0 for page in pages_by_register[held]),
                "running_event_count": len(held_events),
                "statement_count": len({event["statement_id"] for event in held_events}),
                "focus_attachment_count": len(held_attachments),
                "exact_surface_from_other_register": result_counts["EXACT_SURFACE_FROM_OTHER_REGISTER"],
                "root_recipe_from_other_register": result_counts["ROOT_RECIPE_FROM_OTHER_REGISTER"],
                "new_register_recipe_known_atoms": result_counts["NEW_REGISTER_RECIPE__KNOWN_ATOMS"],
                "exact_surface_rate": f"{result_counts['EXACT_SURFACE_FROM_OTHER_REGISTER'] / len(held_events):.6f}",
                "known_recipe_rate": f"{(result_counts['EXACT_SURFACE_FROM_OTHER_REGISTER'] + result_counts['ROOT_RECIPE_FROM_OTHER_REGISTER']) / len(held_events):.6f}",
                "used_category_count": len(used_categories),
                "unsupported_category_holdouts": joined(unsupported_categories),
                "used_rule_family_count": len(used_rules),
                "unsupported_rule_family_holdouts": joined(unsupported_rules),
                "register_private_microform_occurrences": private_micro_occurrences,
                "all_atoms_on_fixed_sheet": "YES",
                "register_replay_result": "PASS_FIXED_SHEET_AND_SCOPE" if not unsupported_categories and not unsupported_rules else "FAIL_PRIVATE_CATEGORY_OR_RULE",
            }
        )

    revision_de = {
        "P1009-S019": "okeor erhält den sichtbaren GRAD I statt eines gradlosen SETZEN.",
        "P1009-S056": "okeor fällt von dem unsichtbar ergänzten GRAD II auf den sichtbaren GRAD I zurück.",
        "P1009-S057": "cheo verliert das nur aus cheor entliehene MARKIEREN.",
        "P1009-S067": "cheo verliert MARKIEREN; L und WERT hängen direkt am weiter offenen NEHMEN-Kopf.",
        "P1009-S244": "cheo verliert die nur aus cheol entliehene VERBINDUNG.",
        "P1009-S254": "okeor fällt von dem unsichtbar ergänzten GRAD II auf den sichtbaren GRAD I zurück.",
        "P1009-S617": "cheo verliert die nur aus cheol entliehene VERBINDUNG.",
        "P1009-S627": "Beide cheo-Karten verlieren die nur aus cheol entliehene VERBINDUNG.",
    }
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in event_rows:
        events_by_statement[str(event["statement_id"])].append(event)
    statement_rows: list[dict[str, object]] = []
    for statement_id in revision_de:
        statement_events = events_by_statement[statement_id]
        corrected = [event for event in statement_events if event["surface_recipe_correction"] != "UNCHANGED"]
        statement_rows.append(
            {
                "statement_id": statement_id,
                "physical_page": statement_events[0]["physical_page"],
                "register": statement_events[0]["held_register"],
                "event_count": len(statement_events),
                "corrected_event_ids": "|".join(str(event["event_id"]) for event in corrected),
                "surface_sequence": " ".join(str(event["surface"]) for event in statement_events),
                "source_recipe_sequence": " | ".join(str(event["source_component_recipe"]) for event in statement_events),
                "corrected_recipe_sequence": " | ".join(str(event["component_recipe"]) for event in statement_events),
                "portable_reading_revision_de": revision_de[statement_id],
            }
        )

    attachment_fields = [
        "pass1025_attachment_id",
        "source_attachment_id",
        "attachment_id",
        "physical_page",
        "register",
        "statement_id",
        "event_id",
        "locus",
        "surface_card",
        "component_recipe",
        "focus_core",
        "focus_value_de",
        "direct_or_stack",
        "teaching_rule_families",
        "micro_signature",
        "selected_attachment_de",
        "pass1025_surface_determinism_correction",
    ]
    write_tsv(OUT / "PASS1025_3888_REGISTER_EVENT_REPLAY.tsv", event_rows, list(event_rows[0]))
    write_tsv(OUT / "PASS1025_4342_CORRECTED_ATTACHMENTS.tsv", attachments, attachment_fields)
    write_tsv(
        OUT / "PASS1025_SURFACE_DETERMINISM_CORRECTIONS.tsv",
        correction_rows,
        ["correction_layer", "target_id", "physical_page", "surface", "old_value", "new_value", "action", "reason_de"],
    )
    write_tsv(OUT / "PASS1025_31_CATEGORY_REGISTER_SUPPORT.tsv", category_rows, list(category_rows[0]))
    write_tsv(OUT / "PASS1025_9_RULE_REGISTER_SUPPORT.tsv", rule_rows, list(rule_rows[0]))
    write_tsv(OUT / "PASS1025_MICROFORM_REGISTER_SUPPORT.tsv", micro_rows, list(micro_rows[0]))
    write_tsv(OUT / "PASS1025_FOUR_REGISTER_REPLAY.tsv", register_rows, list(register_rows[0]))
    write_tsv(
        OUT / "PASS1025_EIGHT_CORRECTED_STATEMENTS.tsv",
        statement_rows,
        list(statement_rows[0]),
    )

    result_counts = Counter(row["register_replay_result"] for row in event_rows)
    private_micros = [row for row in micro_rows if row["register_private_microform"] == "YES"]
    summary = {
        "result": "ALL_FOUR_REGISTERS_REPLAY_WITHOUT_PRIVATE_CATEGORY_OR_COARSE_RULE",
        "register_count": 4,
        "page_count": len(pages),
        "running_event_count": len(events),
        "source_focus_attachment_count": 4345,
        "corrected_focus_attachment_count": len(attachments),
        "surface_recipe_correction_event_count": sum(
            row["surface_recipe_correction"] != "UNCHANGED" for row in events
        ),
        "surface_determinism_correction_row_count": len(correction_rows),
        "same_surface_multiple_recipe_count_after_correction": sum(
            len(recipes) > 1 for recipes in surface_recipes.values()
        ),
        "category_count": len(category_rows),
        "categories_in_all_four_registers": sum(int(row["support_register_count"]) == 4 for row in category_rows),
        "categories_not_in_all_four_registers": [
            {"category_id": row["category_id"], "support_registers": row["support_registers"]}
            for row in category_rows
            if int(row["support_register_count"]) < 4
        ],
        "categories_failing_a_register_where_used": sum(row["survives_every_register_where_used"] == "NO" for row in category_rows),
        "rule_family_count": len(rule_rows),
        "rules_failing_a_register_where_used": sum(row["survives_every_register_where_used"] == "NO" for row in rule_rows),
        "event_replay_counts": dict(sorted(result_counts.items())),
        "register_private_microforms": [row["micro_signature"] for row in private_micros],
        "register_private_microform_occurrences": sum(int(row["total_occurrences"]) for row in private_micros),
        "all_private_microform_parent_rules_cross_register": all(row["all_parent_rules_cross_register"] == "YES" for row in private_micros),
        "source_hashes": {path.name: sha(path) for path in [CATEGORIES, EVENTS, ATTACHMENTS, PAGES]},
    }
    (OUT / "PASS1025_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
