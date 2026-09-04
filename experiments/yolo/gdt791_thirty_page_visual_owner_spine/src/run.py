#!/usr/bin/env python3
"""Build GDT791: one lossless text/image-owner spine for the released 30 pages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
SELECTOR_SPECS = SRC / "PAGE_SELECTOR_SPECS.tsv"
TOPOLOGY_SPECS = SRC / "PAGE_TOPOLOGY_SPECS.tsv"
VISUAL_BATCH_SPECS = SRC / "VISUAL_BATCH_SPECS.tsv"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
ZL3B_REL = Path("transcription/voynich_zl3b_lines.tsv")
G515 = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts"
GROUPS = G515 / "gdt515_5866_unified_group_ledger.tsv"
RUNNING_MAP = G515 / "gdt515_5122_running_event_edition.tsv"
G581 = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts"
PROFILES = G581 / "gdt581_30_page_boundary_profiles.tsv"
EVENTS = G581 / "gdt581_5122_content_ready_event_edition.tsv"
STATEMENTS = G581 / "gdt581_793_content_ready_statement_edition.tsv"
LOCAL_CARDS = G581 / "gdt581_744_local_card_hosts.tsv"
ALIASES = G581 / "gdt581_4026_inherited_alias_edges.tsv"
FOCUS = G581 / "gdt581_5672_focus_reconciliation.tsv"
G790 = ROOT / "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts"
DEEP_LINES = G790 / "GDT790_123_IMAGE_AWARE_LINES.tsv"
DEEP_LABELS = G790 / "GDT790_28_LABEL_TOKEN_ATLAS.tsv"
DEEP_RECORDS = G790 / "GDT790_13_PANEL_RECORD_BINDINGS.tsv"
STRING_BRIDGES = G790 / "GDT790_10_EXACT_LABEL_PROSE_BRIDGES.tsv"
TARGET_FORMS = ("otedy", "okal", "otchdy", "olaiin", "darol", "darolsy")
OUTPUT_NAMES = (
    "GDT791_30_PAGE_EVIDENCE_REGISTRY.tsv",
    "GDT791_1007_LINE_OWNER_ATLAS.tsv",
    "GDT791_5866_OCCURRENCE_SPINE.tsv",
    "GDT791_240_RECORD_LOCAL_STATEMENT_FRAGMENTS.tsv",
    "GDT791_5_CROSS_RECORD_STATEMENTS.tsv",
    "GDT791_745_DEEP_ALIAS_BINDINGS.tsv",
    "GDT791_3_RAW_BOUNDARY_LINK_REPAIRS.tsv",
    "GDT791_10_EXACT_STRING_REFERENCE_EDGES.tsv",
    "GDT791_6_FORM_RUNNING_CENSUS.tsv",
    "GDT791_5_TOPOLOGY_FAMILY_SUMMARY.tsv",
    "GDT791_GUARDED_SOURCE_STATS.tsv",
    "RESULT.json",
)
STATUS = (
    "PASS__30_VISUALLY_REVIEWED_PAGES__35_SOURCE_SELECTORS__1007_LINES__5866_TOKENS__"
    "612_RUNNING_PROSE_LINES__392_LOCAL_LABEL_LINES__3_EMPTY_LINES__5122_RUNNING_EVENTS__"
    "744_LOCAL_CARDS__3_DEEP_PAGES__13_RECORDS__235_LEGACY_STATEMENTS__240_RECORD_LOCAL_"
    "FRAGMENTS__5_CROSS_RECORD_STATEMENTS__2_CROSS_RECORD_ALIASES_QUARANTINED__1_RAW_"
    "GOVERNOR_CROSSING_CLIPPED__ZERO_EFFECTIVE_HOST_CROSSINGS__ZERO_SEMANTIC_EXPORT"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    materialized = list(rows)
    fields = list(materialized[0]) if materialized else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise"
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pipe(values: Iterable[str]) -> str:
    output: list[str] = []
    for value in values:
        if value and value != "NONE" and value not in output:
            output.append(value)
    return "|".join(output) if output else "NONE"


def query_lines(selectors: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(ZL3B_REL), "--selector", "page"]
    for selector in selectors:
        command.extend(("--allow", selector))
    command.extend((
        "--columns",
        "page,locus,line_number,paragraph_start,paragraph_end,token_count,eva_clean",
        "--forbid-prefix", "f84", "--forbid-prefix", "f84r",
    ))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded line query failed")
    stat_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise RuntimeError("guard statistics missing or duplicated")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    stats = {key: int(value) for key, value in json.loads(stat_lines[0][12:]).items()}
    if any(row["page"].startswith("f84") for row in rows):
        raise RuntimeError("sealed selector materialized")
    return rows, stats


def verify_source_lock() -> None:
    if not SOURCE_LOCK.exists():
        return
    for row in read_tsv(SOURCE_LOCK):
        if sha256(ROOT / row["path"]) != row["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {row['path']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    verify_source_lock()

    selector_specs = read_tsv(SELECTOR_SPECS)
    topology_specs = read_tsv(TOPOLOGY_SPECS)
    batch_specs = read_tsv(VISUAL_BATCH_SPECS)
    selectors = [row["source_selector"] for row in selector_specs]
    selector_to_page = {row["source_selector"]: row["physical_page"] for row in selector_specs}
    page_to_selectors: dict[str, list[str]] = defaultdict(list)
    for row in selector_specs:
        page_to_selectors[row["physical_page"]].append(row["source_selector"])
    topology = {row["physical_page"]: row for row in topology_specs}
    pages = [row["physical_page"] for row in topology_specs]
    if len(selector_specs) != 35 or len(set(selectors)) != 35:
        raise RuntimeError("selector specification must contain 35 unique selectors")
    if len(topology_specs) != 30 or len(topology) != 30:
        raise RuntimeError("topology specification must contain 30 pages")
    if set(page_to_selectors) != set(topology):
        raise RuntimeError("selector and topology page sets differ")

    visual_evidence: dict[str, dict[str, str]] = {}
    for batch in batch_specs:
        rows = read_tsv(ROOT / batch["source_path"])
        observed = {row[batch["page_column"]] for row in rows}
        expected = set(batch["expected_pages"].split("|"))
        if not expected <= observed:
            raise RuntimeError(f"visual evidence missing in {batch['batch_id']}")
        for page in expected:
            if page in visual_evidence:
                raise RuntimeError(f"visual page assigned twice: {page}")
            visual_evidence[page] = batch
    if set(visual_evidence) != set(pages):
        raise RuntimeError("six visual batches do not cover the exact 30-page set")

    source_rows, guard_stats = query_lines(selectors)
    groups, running_map = read_tsv(GROUPS), read_tsv(RUNNING_MAP)
    profiles, events = read_tsv(PROFILES), read_tsv(EVENTS)
    statements, local_cards = read_tsv(STATEMENTS), read_tsv(LOCAL_CARDS)
    aliases, focus_rows = read_tsv(ALIASES), read_tsv(FOCUS)
    deep_lines, deep_labels = read_tsv(DEEP_LINES), read_tsv(DEEP_LABELS)
    deep_records, string_bridges = read_tsv(DEEP_RECORDS), read_tsv(STRING_BRIDGES)
    if len(source_rows) != 1007 or sum(int(row["token_count"]) for row in source_rows) != 5866:
        raise RuntimeError("guarded source cardinality changed")
    if (len(groups), len(running_map), len(events), len(local_cards), len(statements), len(aliases)) != (
        5866, 5122, 5122, 744, 793, 4026
    ):
        raise RuntimeError("GDT515/GDT581 source cardinality changed")
    if (len(deep_lines), len(deep_labels), len(deep_records), len(string_bridges)) != (123, 28, 13, 10):
        raise RuntimeError("GDT790 source cardinality changed")

    profile_by_page = {row["physical_page"]: row for row in profiles}
    if set(profile_by_page) != set(pages):
        raise RuntimeError("GDT581 profile set differs from released pages")
    event_by_id = {row["event_id"]: row for row in events}
    running_by_id: dict[str, dict[str, str]] = {}
    for mapped in running_map:
        candidates = (mapped["global_running_event_id"], mapped["source_event_id"])
        matches = [candidate for candidate in candidates if candidate in event_by_id]
        if len(matches) != 1:
            raise RuntimeError(f"cannot resolve GDT581 event identity for {mapped['global_running_event_id']}")
        running_by_id[matches[0]] = mapped
    if len(running_by_id) != 5122:
        raise RuntimeError("resolved running-event identity is not one-to-one")
    deep_line_by_locus = {row["locus"]: row for row in deep_lines}
    record_by_id = {row["record_id"]: row for row in deep_records}
    deep_pages = {row["page"] for row in deep_records}
    if deep_pages != {"f77r", "f82r", "f83r"}:
        raise RuntimeError("deep page set changed")

    running_groups = [row for row in groups if row["group_kind"] == "RUNNING_EVENT"]
    local_groups = [row for row in groups if row["group_kind"] == "LOCAL_ADDRESS_OR_LABEL"]
    if (len(running_groups), len(local_groups)) != (5122, 744):
        raise RuntimeError("group partition changed")
    for group, mapped in zip(running_groups, running_map, strict=True):
        candidates = (mapped["global_running_event_id"], mapped["source_event_id"])
        event = event_by_id[next(candidate for candidate in candidates if candidate in event_by_id)]
        if (group["physical_page"], group["locus"], group["surface"]) != (
            mapped["physical_page"], mapped["locus"], mapped["surface"]
        ) or event["event_id"] not in candidates or (
            group["physical_page"], group["surface"]
        ) != (event["physical_page"], event["surface"]):
            raise RuntimeError("running event alignment changed")
    for group, card in zip(local_groups, local_cards, strict=True):
        if (group["physical_page"], group["locus"], group["surface"], group["source_event_id"]) != (
            card["physical_page"], card["locus"], card["surface"], card["source_event_id"]
        ):
            raise RuntimeError("local-card alignment changed")
    running_detail = {
        group["global_group_id"]: (
            mapped,
            event_by_id[next(candidate for candidate in (
                mapped["global_running_event_id"], mapped["source_event_id"]
            ) if candidate in event_by_id)],
        )
        for group, mapped in zip(running_groups, running_map, strict=True)
    }
    local_detail = {group["global_group_id"]: card for group, card in zip(
        local_groups, local_cards, strict=True
    )}
    deep_local_groups = [row for row in local_groups if row["physical_page"] in deep_pages]
    if len(deep_local_groups) != 28:
        raise RuntimeError("deep local-card count changed")
    deep_label_by_group: dict[str, dict[str, str]] = {}
    for group, label in zip(deep_local_groups, deep_labels, strict=True):
        if (group["physical_page"], group["locus"], group["surface"]) != (
            label["page"], label["locus"], label["label_token"]
        ):
            raise RuntimeError("GDT581/GDT790 label alignment changed")
        deep_label_by_group[group["global_group_id"]] = label

    groups_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for group in groups:
        groups_by_locus[group["locus"]].append(group)
    source_by_locus = {row["locus"]: row for row in source_rows}
    if len(source_by_locus) != 1007:
        raise RuntimeError("source loci are not unique")
    for row in source_rows:
        if [g["surface"] for g in groups_by_locus.get(row["locus"], [])] != row["eva_clean"].split():
            raise RuntimeError(f"line/group replay failed at {row['locus']}")

    line_rows: list[dict[str, Any]] = []
    occurrence_rows: list[dict[str, Any]] = []
    for row in source_rows:
        selector, locus = row["page"], row["locus"]
        page = selector_to_page[selector]
        spec = topology[page]
        locus_groups = groups_by_locus.get(locus, [])
        kinds = {group["group_kind"] for group in locus_groups}
        if not locus_groups:
            line_kind = "EMPTY_TRANSCRIPTION_LINE"
        elif kinds == {"RUNNING_EVENT"}:
            line_kind = "RUNNING_PROSE"
        elif kinds == {"LOCAL_ADDRESS_OR_LABEL"}:
            line_kind = "LOCAL_LABEL_OR_MARKER"
        else:
            raise RuntimeError(f"mixed running/local line at {locus}")
        deep_line = deep_line_by_locus.get(locus)
        panels, records, components, owners = [], [], [], []
        for token_ordinal, group in enumerate(locus_groups, start=1):
            panel_id = record_id = component_id = statement_id = "NONE"
            legacy_owner = group["owner_de"]
            if group["group_kind"] == "RUNNING_EVENT":
                _, event = running_detail[group["global_group_id"]]
                occurrence_id, statement_id, legacy_owner = event["event_id"], event["statement_id"], event["owner_id"]
                if deep_line:
                    panel_id, record_id = deep_line["panel_id"], deep_line["record_id"]
                    context_scope, context_owner = "DEEP_PANEL_RECORD", record_id
                else:
                    context_scope, context_owner = "DIRECT_PAGE_CONTEXT_ONLY", spec["coarse_page_owner_id"]
            else:
                card = local_detail[group["global_group_id"]]
                occurrence_id = card["local_card_host_key"]
                label = deep_label_by_group.get(group["global_group_id"])
                if label:
                    panel_id, component_id = label["panel_id"], label["component_id"]
                    context_scope, context_owner = "DEEP_PANEL_COMPONENT_LABEL", component_id
                else:
                    context_scope = "LEGACY_LOCAL_CARD_WITH_PAGE_CONTEXT"
                    context_owner = spec["coarse_page_owner_id"]
            panels.append(panel_id); records.append(record_id); components.append(component_id); owners.append(legacy_owner)
            occurrence_rows.append({
                "occurrence_ordinal": len(occurrence_rows) + 1,
                "occurrence_id": occurrence_id,
                "occurrence_kind": group["group_kind"],
                "source_selector": selector,
                "physical_page": page,
                "register": spec["register"],
                "topology_family": spec["topology_family"],
                "locus": locus,
                "line_number": row["line_number"],
                "token_ordinal_in_line": token_ordinal,
                "surface": group["surface"],
                "legacy_statement_id": statement_id,
                "legacy_owner": legacy_owner,
                "panel_id": panel_id,
                "record_id": record_id,
                "component_id": component_id,
                "context_scope": context_scope,
                "context_owner_id": context_owner,
                "semantic_export_credit": "ZERO__STRUCTURAL_CROSSWALK_ONLY",
            })
        if not locus_groups:
            context_scope = "DIRECT_PAGE_CONTEXT_ONLY__EMPTY_TRANSCRIPTION_LINE"
        elif line_kind == "RUNNING_PROSE" and deep_line:
            context_scope = "DEEP_PANEL_RECORD"
        elif line_kind == "LOCAL_LABEL_OR_MARKER" and any(v != "NONE" for v in components):
            context_scope = "DEEP_PANEL_COMPONENT_LABEL"
        elif line_kind == "LOCAL_LABEL_OR_MARKER":
            context_scope = "LEGACY_LOCAL_CARD_WITH_PAGE_CONTEXT"
        else:
            context_scope = "DIRECT_PAGE_CONTEXT_ONLY"
        line_rows.append({
            "line_ordinal": len(line_rows) + 1,
            "source_selector": selector,
            "physical_page": page,
            "register": spec["register"],
            "topology_family": spec["topology_family"],
            "locus": locus,
            "line_number": row["line_number"],
            "paragraph_start": row["paragraph_start"],
            "paragraph_end": row["paragraph_end"],
            "line_kind": line_kind,
            "token_count": row["token_count"],
            "running_event_count": sum(g["group_kind"] == "RUNNING_EVENT" for g in locus_groups),
            "local_card_count": sum(g["group_kind"] == "LOCAL_ADDRESS_OR_LABEL" for g in locus_groups),
            "coarse_page_owner_id": spec["coarse_page_owner_id"],
            "legacy_owner_ids": pipe(owners),
            "panel_ids": pipe(panels),
            "record_ids": pipe(records),
            "component_ids": pipe(components),
            "context_scope": context_scope,
            "eva_clean": row["eva_clean"],
            "semantic_export_credit": "ZERO__STRUCTURAL_CROSSWALK_ONLY",
        })
    line_counts = Counter(row["line_kind"] for row in line_rows)
    if line_counts != Counter({"RUNNING_PROSE": 612, "LOCAL_LABEL_OR_MARKER": 392, "EMPTY_TRANSCRIPTION_LINE": 3}):
        raise RuntimeError(f"line partition changed: {line_counts}")
    if len(occurrence_rows) != 5866:
        raise RuntimeError("occurrence spine cardinality changed")

    page_rows: list[dict[str, Any]] = []
    for page in pages:
        spec, profile, batch = topology[page], profile_by_page[page], visual_evidence[page]
        page_lines = [row for row in line_rows if row["physical_page"] == page]
        page_occ = [row for row in occurrence_rows if row["physical_page"] == page]
        page_records = [row for row in deep_records if row["page"] == page]
        page_labels = [row for row in deep_labels if row["page"] == page]
        page_rows.append({
            "page_ordinal": spec["page_ordinal"], "physical_page": page,
            "source_selectors": "|".join(page_to_selectors[page]), "register": spec["register"],
            "topology_family": spec["topology_family"], "coarse_page_owner_id": spec["coarse_page_owner_id"],
            "coarse_visible_layout_de": spec["coarse_visible_layout_de"],
            "visual_batch_id": spec["visual_batch_id"], "visual_source_path": batch["source_path"],
            "visual_annotation_tier": spec["visual_annotation_tier"], "deep_panel_status": spec["deep_panel_status"],
            "raw_line_count": len(page_lines), "raw_token_count": sum(int(x["token_count"]) for x in page_lines),
            "running_prose_line_count": sum(x["line_kind"] == "RUNNING_PROSE" for x in page_lines),
            "local_label_line_count": sum(x["line_kind"] == "LOCAL_LABEL_OR_MARKER" for x in page_lines),
            "empty_line_count": sum(x["line_kind"] == "EMPTY_TRANSCRIPTION_LINE" for x in page_lines),
            "running_event_count": sum(x["occurrence_kind"] == "RUNNING_EVENT" for x in page_occ),
            "local_card_count": sum(x["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL" for x in page_occ),
            "legacy_statement_count": profile["statement_count"],
            "legacy_local_component_count": profile["local_component_count"],
            "legacy_local_name_slot_count": profile["local_name_slot_count"],
            "deep_panel_count": len({x["panel_id"] for x in page_records}), "deep_record_count": len(page_records),
            "deep_label_token_count": len(page_labels), "semantic_ceiling": spec["semantic_ceiling"],
        })

    deep_event_to_record = {
        event_id: deep_line_by_locus[mapped["locus"]]["record_id"]
        for event_id, mapped in running_by_id.items() if mapped["locus"] in deep_line_by_locus
    }
    deep_statements = [row for row in statements if row["physical_page"] in deep_pages]
    if len(deep_statements) != 235:
        raise RuntimeError("deep statement count changed")
    fragment_rows: list[dict[str, Any]] = []
    cross_statement_rows: list[dict[str, Any]] = []
    for statement in deep_statements:
        event_ids = statement["event_ids"].split("|")
        record_sequence = [deep_event_to_record[event_id] for event_id in event_ids]
        unique_records: list[str] = []
        for record_id in record_sequence:
            if record_id not in unique_records:
                unique_records.append(record_id)
        crossing = len(unique_records) > 1
        for fragment_ordinal, record_id in enumerate(unique_records, start=1):
            fragment_ids = [eid for eid, rid in zip(event_ids, record_sequence, strict=True) if rid == record_id]
            mapped = [running_by_id[eid] for eid in fragment_ids]
            record = record_by_id[record_id]
            fragment_rows.append({
                "fragment_ordinal": len(fragment_rows) + 1,
                "fragment_id": f"GDT791-F{len(fragment_rows)+1:03d}",
                "legacy_statement_id": statement["statement_id"], "physical_page": statement["physical_page"],
                "legacy_end_mode": statement["end_mode"], "legacy_statement_event_count": statement["event_count"],
                "fragment_ordinal_in_statement": fragment_ordinal, "fragment_count_in_statement": len(unique_records),
                "record_id": record_id, "panel_id": record["panel_id"], "record_kind": record["record_kind"],
                "fragment_event_count": len(fragment_ids), "first_event_id": fragment_ids[0],
                "first_locus": mapped[0]["locus"], "last_event_id": fragment_ids[-1], "last_locus": mapped[-1]["locus"],
                "event_ids": "|".join(fragment_ids),
                "surface_sequence": " ".join(event_by_id[eid]["surface"] for eid in fragment_ids),
                "record_boundary_action": "SPLIT_LEGACY_STATEMENT" if crossing else "RETAIN_STATEMENT",
                "semantic_export_credit": "ZERO__BOUNDARY_REPAIR_ONLY",
            })
        if crossing:
            edges = []
            for left, right, left_record, right_record in zip(event_ids, event_ids[1:], record_sequence, record_sequence[1:]):
                if left_record != right_record:
                    a, b = running_by_id[left], running_by_id[right]
                    edges.append(f"{left}:{a['surface']}@{a['locus']}->{right}:{b['surface']}@{b['locus']}")
            panels = [record_by_id[rid]["panel_id"] for rid in unique_records]
            cross_statement_rows.append({
                "crossing_ordinal": len(cross_statement_rows) + 1,
                "legacy_statement_id": statement["statement_id"], "physical_page": statement["physical_page"],
                "legacy_end_mode": statement["end_mode"], "record_ids": "|".join(unique_records),
                "panel_ids": "|".join(panels),
                "crossing_class": "PANEL_CROSS" if len(set(panels)) > 1 else "RECORD_CROSS_SAME_PANEL",
                "boundary_event_edges": "|".join(edges), "legacy_surface_sequence": statement["surface_sequence"],
                "selected_repair": "SPLIT_AT_GDT790_RECORD_BOUNDARY__KEEP_LEGACY_ID_AS_PROVENANCE",
            })
    if len(fragment_rows) != 240 or len(cross_statement_rows) != 5:
        raise RuntimeError("record-local statement partition changed")
    if Counter(x["crossing_class"] for x in cross_statement_rows) != Counter({"PANEL_CROSS": 4, "RECORD_CROSS_SAME_PANEL": 1}):
        raise RuntimeError("cross-statement topology changed")
    if {x["legacy_end_mode"] for x in cross_statement_rows} != {"LICENSED_DY_CLOSE"}:
        raise RuntimeError("cross-statement close mode changed")

    deep_alias_rows: list[dict[str, Any]] = []
    for alias in aliases:
        if alias["physical_page"] not in deep_pages:
            continue
        target_record = deep_event_to_record[alias["event_id"]]
        source_event_id = alias["lexical_source_event_id"]
        source_record = deep_event_to_record.get(source_event_id, "NONE")
        if source_record == "NONE":
            decision = "REPARENT_OWNER_DEFAULT_TO_LOCAL_RECORD_OWNER"
        elif source_record == target_record:
            decision = "RETAIN_SAME_RECORD_ALIAS"
        else:
            decision = "QUARANTINE_CROSS_RECORD_ALIAS"
        deep_alias_rows.append({
            "alias_ordinal": len(deep_alias_rows) + 1, "alias_id": alias["alias_id"],
            "alias_class": alias["alias_class"], "physical_page": alias["physical_page"],
            "statement_id": alias["statement_id"], "target_event_id": alias["event_id"],
            "target_surface": event_by_id[alias["event_id"]]["surface"],
            "target_locus": running_by_id[alias["event_id"]]["locus"], "target_record_id": target_record,
            "target_panel_id": record_by_id[target_record]["panel_id"], "inherited_root": alias["inherited_root"],
            "lexical_source_kind": alias["lexical_source_kind"], "source_event_id": source_event_id,
            "source_surface": event_by_id[source_event_id]["surface"] if source_event_id in event_by_id else "NONE",
            "source_locus": running_by_id[source_event_id]["locus"] if source_event_id in running_by_id else "NONE",
            "source_record_id": source_record,
            "source_panel_id": record_by_id[source_record]["panel_id"] if source_record in record_by_id else "NONE",
            "selected_boundary_action": decision,
            "new_owner_key": f"RECORD_OWNER:{target_record}" if source_record == "NONE" else "NONE",
            "semantic_export_credit": "ZERO__BOUNDARY_REPAIR_ONLY",
        })
    alias_decisions = Counter(x["selected_boundary_action"] for x in deep_alias_rows)
    if len(deep_alias_rows) != 745 or alias_decisions != Counter({
        "RETAIN_SAME_RECORD_ALIAS": 460,
        "REPARENT_OWNER_DEFAULT_TO_LOCAL_RECORD_OWNER": 283,
        "QUARANTINE_CROSS_RECORD_ALIAS": 2,
    }):
        raise RuntimeError(f"deep alias partition changed: {alias_decisions}")

    boundary_repairs: list[dict[str, Any]] = []
    for alias in deep_alias_rows:
        if alias["selected_boundary_action"] != "QUARANTINE_CROSS_RECORD_ALIAS":
            continue
        boundary_repairs.append({
            "repair_ordinal": len(boundary_repairs) + 1, "link_id": alias["alias_id"],
            "link_kind": alias["alias_class"], "physical_page": alias["physical_page"],
            "legacy_statement_id": alias["statement_id"], "source_event_id": alias["source_event_id"],
            "source_surface": alias["source_surface"], "source_locus": alias["source_locus"],
            "source_record_id": alias["source_record_id"], "target_event_id": alias["target_event_id"],
            "target_surface": alias["target_surface"], "target_locus": alias["target_locus"],
            "target_record_id": alias["target_record_id"], "root_or_focus": alias["inherited_root"],
            "effective_local_host": "NONE",
            "selected_repair": "QUARANTINE__DO_NOT_RENDER_INHERITED_ACTION_OR_OBJECT_ACROSS_RECORD",
        })
    for focus in focus_rows:
        if (
            focus["physical_page"] not in deep_pages
            or focus["event_id"] not in deep_event_to_record
            or focus["primary_governor_event_id"] not in deep_event_to_record
        ):
            continue
        target_record = deep_event_to_record[focus["event_id"]]
        source_record = deep_event_to_record[focus["primary_governor_event_id"]]
        if target_record == source_record:
            continue
        if focus["effective_grammar_host_kind"] != "CONTROL_ENVELOPE":
            raise RuntimeError("raw governor crossing lacks local effective host")
        boundary_repairs.append({
            "repair_ordinal": len(boundary_repairs) + 1, "link_id": focus["focus_host_id"],
            "link_kind": "RAW_PRIMARY_GOVERNOR", "physical_page": focus["physical_page"],
            "legacy_statement_id": focus["statement_id"], "source_event_id": focus["primary_governor_event_id"],
            "source_surface": event_by_id[focus["primary_governor_event_id"]]["surface"],
            "source_locus": running_by_id[focus["primary_governor_event_id"]]["locus"],
            "source_record_id": source_record, "target_event_id": focus["event_id"],
            "target_surface": focus["surface"], "target_locus": running_by_id[focus["event_id"]]["locus"],
            "target_record_id": target_record, "root_or_focus": focus["focus_root"],
            "effective_local_host": focus["effective_grammar_host_key"],
            "selected_repair": "CLIP_RAW_GOVERNOR_LINK__RETAIN_LOCAL_CONTROL_ENVELOPE",
        })
    if len(boundary_repairs) != 3:
        raise RuntimeError("raw cross-record link count changed")

    string_edge_rows: list[dict[str, Any]] = []
    for bridge in string_bridges:
        prose_panel = record_by_id[bridge["prose_record_id"]]["panel_id"]
        string_edge_rows.append({**bridge, "prose_panel_id": prose_panel,
            "cross_panel": "YES" if bridge["label_panel_id"] != prose_panel else "NO",
            "graph_edge_class": "EXACT_STRING_REFERENCE", "record_merge_credit": "ZERO",
            "meaning_transfer_credit": "ZERO"})
    if Counter(x["cross_panel"] for x in string_edge_rows) != Counter({"YES": 10}):
        raise RuntimeError("exact string bridge panel relation changed")
    if {x["semantic_credit"] for x in string_edge_rows} != {"ZERO__STRING_REUSE_ONLY"}:
        raise RuntimeError("string bridge semantic ceiling changed")

    form_rows: list[dict[str, Any]] = []
    for form in TARGET_FORMS:
        running = [x for x in events if x["surface"] == form]
        local = [x for x in local_cards if x["surface"] == form]
        labels = [x for x in deep_labels if x["label_token"] == form]
        if form == "otedy":
            next_use = "TARGET_MASKED_27_PAGE_RECORD_HEAD_VS_LEGACY_CONTINUATION_TEST"
        elif form == "okal":
            next_use = "TARGET_MASKED_27_PAGE_FIELD_AND_RECORD_POSITION_TEST"
        elif form in {"otchdy", "olaiin"}:
            next_use = "LOW_CAPACITY_OUTSIDE_PAGE_HOST_TRANSFER"
        else:
            next_use = "IMAGE_LOCAL_ONLY__NO_RUNNING_PROSE_TRANSFER_ROUTE"
        form_rows.append({
            "surface": form, "running_occurrence_count": len(running),
            "running_physical_page_count": len({x["physical_page"] for x in running}),
            "running_physical_pages": pipe(sorted({x["physical_page"] for x in running})),
            "statement_first_occurrence_count": sum(x["card_ordinal_in_statement"] == "1" for x in running),
            "deep_running_occurrence_count": sum(x["physical_page"] in deep_pages for x in running),
            "local_card_occurrence_count": len(local), "local_card_page_count": len({x["physical_page"] for x in local}),
            "gdt790_label_occurrence_count": len(labels),
            "gdt790_exact_string_bridge_count": sum(x["label_token"] == form for x in string_edge_rows),
            "boundary_conflict_target": "YES" if form == "otedy" else "NO",
            "selected_next_use": next_use, "portable_meaning_selected": "NO",
        })

    topology_rows: list[dict[str, Any]] = []
    for family in sorted({row["topology_family"] for row in topology_specs}):
        family_pages = [row for row in page_rows if row["topology_family"] == family]
        topology_rows.append({
            "topology_family": family, "physical_page_count": len(family_pages),
            "physical_pages": "|".join(row["physical_page"] for row in family_pages),
            "raw_line_count": sum(int(row["raw_line_count"]) for row in family_pages),
            "raw_token_count": sum(int(row["raw_token_count"]) for row in family_pages),
            "running_prose_line_count": sum(int(row["running_prose_line_count"]) for row in family_pages),
            "local_label_line_count": sum(int(row["local_label_line_count"]) for row in family_pages),
            "running_event_count": sum(int(row["running_event_count"]) for row in family_pages),
            "local_card_count": sum(int(row["local_card_count"]) for row in family_pages),
            "deep_page_count": sum(row["visual_annotation_tier"] == "DEEP_PANEL_COMPONENT" for row in family_pages),
            "semantic_ceiling": "VISIBLE_TOPOLOGY_CONTEXT_ONLY__NO_WORD_MEANING",
        })
    if len(topology_rows) != 5:
        raise RuntimeError("topology family count changed")

    guarded_rows = [{
        "source": str(ZL3B_REL), "selector_count": len(selectors), "physical_page_count": len(pages),
        "selected_rows": guard_stats.get("selected", -1),
        "skipped_forbidden_rows": guard_stats.get("skipped_forbidden", -1),
        "skipped_not_allowed_rows": guard_stats.get("skipped_not_allowed", -1),
        "materialized_f84_rows": 0, "materialized_f84r_rows": 0,
        "output_columns": "page|locus|line_number|paragraph_start|paragraph_end|token_count|eva_clean",
    }]
    result = {
        "experiment_id": "GDT791", "status": STATUS,
        "decision": "PANEL_THEN_RECORD_THEN_LEGACY_STATEMENT__LOSSLESS_30_PAGE_SPINE_SELECTED",
        "counts": {
            "physical_pages": 30, "source_selectors": 35, "visually_reviewed_page_contexts": 30,
            "deep_panel_pages": 3, "deep_panels": len({x["panel_id"] for x in deep_records}), "deep_records": 13,
            "source_lines": 1007, "source_tokens": 5866, "running_prose_lines": 612,
            "local_label_or_marker_lines": 392, "empty_transcription_lines": 3,
            "running_events": 5122, "local_cards": 744, "deep_legacy_statements": 235,
            "record_local_statement_fragments": 240, "cross_record_statements": 5,
            "cross_panel_statements": 4, "same_panel_cross_record_statements": 1,
            "deep_aliases": 745, "same_record_aliases_retained": 460,
            "owner_default_aliases_reparented": 283, "cross_record_aliases_quarantined": 2,
            "raw_primary_governor_crossings_clipped": 1, "effective_grammar_host_crossings": 0,
            "exact_string_reference_edges": 10, "exact_string_reference_semantic_credit": 0,
            "token_semantics_changed": 0, "component_exports": 0, "sealed_rows_materialized": 0,
        },
        "boundary_repair": {
            "precedence": ["PANEL", "RECORD", "LEGACY_STATEMENT"],
            "f77r_otedy": ("Remove the inherited CH action and Y object at f77r.25; retain otedy as an "
                "H0_OTHER whole-form image-reference candidate with its local OT>G<DY control envelope."),
        },
        "next": ("Target-mask otedy and okal on the three image pages, then compare their record-head, "
            "field and continuation geometry on the other 27 released pages; keep otchdy and olaiin as "
            "lower-capacity controls and darol/darolsy image-local."),
        "claim_ceiling": ("Structural and visible-owner integration only. No plaintext, Voynich lexeme, "
            "free root, object identity, substance, process direction or unseen-form meaning is selected."),
    }
    for name, rows in zip(OUTPUT_NAMES[:11], [page_rows, line_rows, occurrence_rows, fragment_rows,
        cross_statement_rows, deep_alias_rows, boundary_repairs, string_edge_rows, form_rows,
        topology_rows, guarded_rows], strict=True):
        write_tsv(out / name, rows)
    (out / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
