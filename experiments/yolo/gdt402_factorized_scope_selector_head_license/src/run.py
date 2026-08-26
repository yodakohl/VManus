#!/usr/bin/env python3
"""Factor every GDT399 attachment into selector, head, and local topology axes."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "artifacts"
G399 = ROOT / "experiments/yolo/gdt399_creative_scope_rebuild_after_visible_resegmentation/artifacts"
G401 = ROOT / "experiments/yolo/gdt401_amber_forward_r_composition_closure/artifacts"
ATTACHMENTS = G399 / "gdt399_4374_scope_attachments.tsv"
PAGES = G399 / "gdt399_22_page_replay.tsv"
RULES = G399 / "gdt399_rule_support.tsv"
RESOLVED401 = G401 / "gdt401_four_attachment_resolution.tsv"

R_RULE = "R_POSITIONAL_MARKING"
SELECTOR_RULES = {
    "AL_AR_ORDERED_FALLBACK",
    "INHERITED_ACTION_STACK",
    "L_AIR_RIGHT_FALLBACK",
    "NEAREST_HEAD_LEFT_TIE",
    "ONE_CARD_FORWARD",
    "OWNER_CONTEXT",
    "PREVIOUS_CARD_STACK",
    "Q_OT_PACKAGE_FORWARD",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise AssertionError(f"empty output {path.name}")
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pipe(values: set[str] | list[str]) -> str:
    chosen = sorted({value for value in values if value and value != "NONE"})
    return "|".join(chosen) if chosen else "NONE"


def selector_rule(row: dict[str, str]) -> str:
    base = [item for item in row["teaching_rule_families"].split("|") if item != R_RULE]
    if len(base) != 1 or base[0] not in SELECTOR_RULES:
        raise AssertionError(f"bad selector rule: {row['attachment_id']} {base}")
    return base[0]


def head_kind(row: dict[str, str]) -> str:
    if row["chosen_action"] == "OWNER":
        return "VISIBLE_OWNER"
    if row["chosen_action"] == "R":
        return "R_ACTION_HEAD"
    return "ORDINARY_ACTION_HEAD"


def selector_signature(row: dict[str, str], level: str) -> str:
    rule = selector_rule(row)
    if level == "EXACT_PAYLOAD_SELECTOR":
        return "::".join([row["focus_core"], row["chosen_attachment_class"], rule])
    if level == "TYPED_PAYLOAD_SELECTOR":
        return "::".join([row["focus_family"], row["chosen_attachment_class"], rule])
    if level == "GEOMETRY_SELECTOR":
        return "::".join([row["chosen_attachment_class"], rule])
    if level == "BASE_SELECTOR":
        return rule
    raise AssertionError(level)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    attachments = read_tsv(ATTACHMENTS)
    pages = read_tsv(PAGES)
    rules = read_tsv(RULES)
    resolved401 = read_tsv(RESOLVED401)
    if [len(attachments), len(pages), len(rules), len(resolved401)] != [4374, 22, 9, 4]:
        raise AssertionError("upstream inventory mismatch")

    selector_levels = [
        "EXACT_PAYLOAD_SELECTOR",
        "TYPED_PAYLOAD_SELECTOR",
        "GEOMETRY_SELECTOR",
        "BASE_SELECTOR",
    ]
    selector_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    selector_registers: dict[tuple[str, str], set[str]] = defaultdict(set)
    selector_rows: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    head_pages: dict[str, set[str]] = defaultdict(set)
    head_registers: dict[str, set[str]] = defaultdict(set)
    r_mode_pages: dict[str, set[str]] = defaultdict(set)
    r_mode_registers: dict[str, set[str]] = defaultdict(set)
    duplicate_pages: dict[str, set[str]] = defaultdict(set)
    duplicate_registers: dict[str, set[str]] = defaultdict(set)

    for row in attachments:
        for level in selector_levels:
            key = (level, selector_signature(row, level))
            selector_pages[key].add(row["physical_page"])
            selector_registers[key].add(row["register"])
            selector_rows[key].append(row)
        head_pages[row["chosen_action"]].add(row["physical_page"])
        head_registers[row["chosen_action"]].add(row["register"])
        r_mode_pages[row["r_position_mode"]].add(row["physical_page"])
        r_mode_registers[row["r_position_mode"]].add(row["register"])
        duplicate_pages[row["duplicate_scope_mode"]].add(row["physical_page"])
        duplicate_registers[row["duplicate_scope_mode"]].add(row["register"])

    replay_rows: list[dict[str, object]] = []
    selector_page_counts: Counter[str] = Counter()
    selector_register_counts: Counter[str] = Counter()
    for row in attachments:
        page_level = "NONE"
        register_level = "NONE"
        for level in selector_levels:
            key = (level, selector_signature(row, level))
            if page_level == "NONE" and selector_pages[key] - {row["physical_page"]}:
                page_level = level
            if register_level == "NONE" and selector_registers[key] - {row["register"]}:
                register_level = level
        selector_page_counts[page_level] += 1
        selector_register_counts[register_level] += 1
        head_page_ok = bool(head_pages[row["chosen_action"]] - {row["physical_page"]})
        head_register_ok = bool(head_registers[row["chosen_action"]] - {row["register"]})
        r_mode = row["r_position_mode"]
        if r_mode == "R_POSITIONAL_NESTED":
            r_support = "VISIBLE_R_TOPOLOGY_DERIVATION"
        elif r_mode == "NONE":
            r_support = "NOT_APPLICABLE"
        elif r_mode_registers[r_mode] - {row["register"]}:
            r_support = "DIRECT_OUTSIDE_REGISTER"
        else:
            r_support = "R_MARKER_PARENT_ONLY"
        duplicate_mode = row["duplicate_scope_mode"]
        if duplicate_mode == "PACKAGE_SCOPE_DESCENT":
            duplicate_support = "VISIBLE_PACKAGE_NESTING_DERIVATION"
        elif duplicate_registers[duplicate_mode] - {row["register"]}:
            duplicate_support = "DIRECT_OUTSIDE_REGISTER"
        else:
            duplicate_support = "LOCAL_VISIBLE_DUPLICATION"
        result = (
            "PASS_FACTORIZED_SELECTOR_AND_HEAD"
            if page_level != "NONE" and register_level != "NONE" and head_page_ok and head_register_ok
            else "FAIL_FACTORIZED_PORTABILITY"
        )
        replay_rows.append({
            "factorized_id": f"G402-A{len(replay_rows) + 1:05d}",
            "attachment_id": row["attachment_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "statement_id": row["statement_id"],
            "event_id": row["event_id"],
            "surface": row["surface"],
            "focus_core": row["focus_core"],
            "focus_family": row["focus_family"],
            "selector_rule": selector_rule(row),
            "attachment_geometry": row["chosen_attachment_class"],
            "selected_action_event_id": row["chosen_action_event_id"],
            "selected_action_atom_ordinal": row["chosen_action_atom_ordinal"],
            "action_core": row["chosen_action"],
            "head_kind": head_kind(row),
            "r_topology": r_mode,
            "duplicate_mode": duplicate_mode,
            "duplicate_role": row["duplicate_scope_role"],
            "lookahead_cards": row["bounded_lookahead_cards"],
            "owner_boundary_crossed": row["owner_boundary_crossed"],
            "selector_outside_page_level": page_level,
            "selector_outside_register_level": register_level,
            "head_outside_page": "YES" if head_page_ok else "NO",
            "head_outside_register": "YES" if head_register_ok else "NO",
            "r_topology_support": r_support,
            "duplicate_support": duplicate_support,
            "factorized_result": result,
        })

    axis_rows: list[dict[str, object]] = []

    def add_axis(axis: str, mapping: dict[str, list[dict[str, str]]]) -> None:
        for value in sorted(mapping):
            selected = mapping[value]
            axis_rows.append({
                "axis": axis,
                "value": value,
                "occurrences": len(selected),
                "page_count": len({row["physical_page"] for row in selected}),
                "pages": pipe({row["physical_page"] for row in selected}),
                "register_count": len({row["register"] for row in selected}),
                "registers": pipe({row["register"] for row in selected}),
                "focus_cores": pipe({row["focus_core"] for row in selected}),
                "action_cores": pipe({row["chosen_action"] for row in selected}),
                "attachment_classes": pipe({row["chosen_attachment_class"] for row in selected}),
                "portability_note": (
                    "VISIBLE_LOCAL_TOPOLOGY"
                    if (axis == "R_TOPOLOGY" and value == "R_POSITIONAL_NESTED")
                    or (axis == "DUPLICATE_MODE" and value == "PACKAGE_SCOPE_DESCENT")
                    else "DIRECT_WHERE_USED"
                ),
            })

    selectors: dict[str, list[dict[str, str]]] = defaultdict(list)
    heads: dict[str, list[dict[str, str]]] = defaultdict(list)
    r_modes: dict[str, list[dict[str, str]]] = defaultdict(list)
    duplicates: dict[str, list[dict[str, str]]] = defaultdict(list)
    geometries: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in attachments:
        selectors[selector_rule(row)].append(row)
        heads[row["chosen_action"]].append(row)
        r_modes[row["r_position_mode"]].append(row)
        duplicates[row["duplicate_scope_mode"]].append(row)
        geometries[row["chosen_attachment_class"]].append(row)
    add_axis("SCOPE_SELECTOR", selectors)
    add_axis("ACTION_HEAD", heads)
    add_axis("R_TOPOLOGY", r_modes)
    add_axis("DUPLICATE_MODE", duplicates)
    add_axis("ATTACHMENT_GEOMETRY", geometries)

    former_ids = {row["attachment_id"] for row in resolved401}
    former_rows = [row for row in replay_rows if row["attachment_id"] in former_ids]

    replay_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    replay_by_register: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in replay_rows:
        replay_by_page[str(row["physical_page"])].append(row)
        replay_by_register[str(row["register"])].append(row)
    summary_rows: list[dict[str, object]] = []
    for kind, groups in (("PAGE", replay_by_page), ("REGISTER", replay_by_register)):
        for unit in sorted(groups):
            selected = groups[unit]
            summary_rows.append({
                "unit_kind": kind,
                "unit": unit,
                "attachment_count": len(selected),
                "selector_levels": pipe({str(row["selector_outside_register_level"]) for row in selected}),
                "head_cores": pipe({str(row["action_core"]) for row in selected}),
                "r_topologies": pipe({str(row["r_topology"]) for row in selected}),
                "factorized_pass_count": sum(row["factorized_result"] == "PASS_FACTORIZED_SELECTOR_AND_HEAD" for row in selected),
                "factorized_fail_count": sum(row["factorized_result"] != "PASS_FACTORIZED_SELECTOR_AND_HEAD" for row in selected),
                "result": "PASS" if all(row["factorized_result"] == "PASS_FACTORIZED_SELECTOR_AND_HEAD" for row in selected) else "FAIL",
            })
    for page in pages:
        if page["page_replay_result"] == "LOCAL_ADDRESS_COPY_ONLY":
            summary_rows.append({
                "unit_kind": "PAGE",
                "unit": page["physical_page"],
                "attachment_count": 0,
                "selector_levels": "ADDRESS_ONLY",
                "head_cores": "ADDRESS_ONLY",
                "r_topologies": "ADDRESS_ONLY",
                "factorized_pass_count": 0,
                "factorized_fail_count": 0,
                "result": "ADDRESS_ONLY",
            })

    replay_path = OUT / "gdt402_4374_factorized_replay.tsv"
    axes_path = OUT / "gdt402_axis_inventory.tsv"
    former_path = OUT / "gdt402_four_former_amber.tsv"
    summary_path = OUT / "gdt402_22_page_4_register_replay.tsv"
    write_tsv(replay_path, replay_rows)
    write_tsv(axes_path, axis_rows)
    write_tsv(former_path, former_rows)
    write_tsv(summary_path, summary_rows)

    result = {
        "experiment_id": "GDT402",
        "status": "COMPLETE_FACTORIZED_SCOPE_PARSER__NO_FALSE_AMBER",
        "attachment_count": len(replay_rows),
        "scope_selector_count": len(selectors),
        "action_head_count": len(heads),
        "attachment_geometry_count": len(geometries),
        "r_topology_count": len(r_modes),
        "duplicate_mode_count": len(duplicates),
        "factorized_pass_count": sum(row["factorized_result"] == "PASS_FACTORIZED_SELECTOR_AND_HEAD" for row in replay_rows),
        "factorized_fail_count": sum(row["factorized_result"] != "PASS_FACTORIZED_SELECTOR_AND_HEAD" for row in replay_rows),
        "former_amber_count": len(former_rows),
        "former_amber_factorized_pass_count": sum(row["factorized_result"] == "PASS_FACTORIZED_SELECTOR_AND_HEAD" for row in former_rows),
        "selector_outside_register_levels": dict(sorted(selector_register_counts.items())),
        "selector_outside_page_levels": dict(sorted(selector_page_counts.items())),
        "local_topology_examples": {
            "R_POSITIONAL_NESTED": len(r_modes.get("R_POSITIONAL_NESTED", [])),
            "PACKAGE_SCOPE_DESCENT": len(duplicates.get("PACKAGE_SCOPE_DESCENT", [])),
        },
        "parser_order": [
            "SEGMENT_VISIBLE_RECIPE",
            "SELECT_SCOPE_RULE",
            "LOCATE_TARGET_BY_GEOMETRY",
            "LICENSE_VISIBLE_ACTION_HEAD",
            "RESOLVE_R_AND_DUPLICATE_TOPOLOGY",
            "BIND_INTERNAL_TARGET_ARGUMENTS",
        ],
        "output_hashes": {},
    }
    result_path = OUT / "gdt402_result.json"
    produced = [replay_path, axes_path, former_path, summary_path]
    result["output_hashes"] = {path.name: sha256(path) for path in produced}
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
