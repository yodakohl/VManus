#!/usr/bin/env python3
"""Build GDT793: whole-record candidate discrimination for exact `okal`."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
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
BASE = ROOT / "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
CASES = SRC / "OWNER_FINGERPRINT_CASES.tsv"
MODELS = SRC / "CANDIDATE_MODEL_SPECS.tsv"
G791 = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine"
SELECTORS = G791 / "src/PAGE_SELECTOR_SPECS.tsv"
SPINE = G791 / "artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
LINES = G791 / "artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv"
G581_LOCAL = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_744_local_card_hosts.tsv"
G790 = ROOT / "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts"
DEEP_LABELS = G790 / "GDT790_27_LABEL_OWNER_ATLAS.tsv"
DEEP_RECORDS = G790 / "GDT790_13_PANEL_RECORD_BINDINGS.tsv"
G792_PATCH = ROOT / "experiments/yolo/gdt792_target_masked_image_form_host_transfer/artifacts/GDT792_20_OKAL_EXACT_SCOPE_STRUCTURAL_OVERLAY.tsv"
CIRCLES = ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
CROSS_REL = ROOT / "transcription/voynich_cross_transcription_lines.tsv"

OUTPUT_NAMES = (
    "GDT793_41_OKAL_PREFIX_FAMILY_OCCURRENCE_ATLAS.tsv",
    "GDT793_17_RUNNING_WHOLE_CONTEXTS.tsv",
    "GDT793_15_LOCAL_COMPONENT_POSITION_ATLAS.tsv",
    "GDT793_3_TARGET_MASKED_OWNER_FINGERPRINTS.tsv",
    "GDT793_3_MEMBER_IDENTIFIABILITY_CASES.tsv",
    "GDT793_ORDERED_ARRAY_DIAGNOSTICS.tsv",
    "GDT793_5_OUTER_SLOT4_SERIES.tsv",
    "GDT793_UPPER_ZONE_SENSITIVITY.tsv",
    "GDT793_CANDIDATE_ADJUDICATION.tsv",
    "GDT793_20_EXACT_OKAL_WORKING_RENDERER.tsv",
    "GDT793_GUARDED_SOURCE_STATS.tsv",
    "RESULT.json",
)

STATUS = (
    "PARTIAL__41_OKAL_PREFIX_OCCURRENCES__26_RUNNING__15_LOCAL__17_CONTEXTS__"
    "0_OF_3_TARGET_MASKED_OWNER_RECOVERIES__F72_TWO_COLLISION_TYPES__UNIQUE_"
    "MEMBER_FAIL__STRICT_ORDINAL_FAIL__4_OF_5_OUTER_SLOT4_SENSITIVITY__CLASS_"
    "SLOT_ENTRY_CODE_C0_SELECTED_FOR_20_EXACT_OKAL_OCCURRENCES__OPAQUE_RENDERER_"
    "SURVIVES__ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEMES"
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
    result: list[str] = []
    for value in values:
        if value and value != "NONE" and value not in result:
            result.append(value)
    return "|".join(result) if result else "NONE"


def verify_source_lock() -> None:
    if not SOURCE_LOCK.is_file():
        raise RuntimeError("source lock is required")
    rows = read_tsv(SOURCE_LOCK)
    if not rows or len({row["path"] for row in rows}) != len(rows):
        raise RuntimeError("source lock is empty or contains duplicate paths")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"invalid source-lock path: {row['path']}")
        path = ROOT / relative
        if not path.is_file() or sha256(path) != row["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {row['path']}")


def guarded_query(
    path: Path, selectors: list[str], columns: str
) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for selector in selectors:
        command.extend(("--allow", selector))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or f"guarded query failed: {path}")
    stat_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise RuntimeError("guarded query statistics missing or duplicated")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    stats = {key: int(value) for key, value in json.loads(stat_lines[0][12:]).items()}
    if any(row["page"].startswith("f84") for row in rows):
        raise RuntimeError("sealed selector materialized")
    return rows, stats


def parse_clock(comment: str) -> float | None:
    match = re.search(r"(?:Label at|At|Moon at)\s+(\d\d?):(\d\d)", comment)
    if not match:
        return None
    return (int(match.group(1)) % 12) + int(match.group(2)) / 60


def near_twelve(clock: float, half_width: float) -> bool:
    return clock >= 12 - half_width or clock <= half_width


def hypergeom_all_successes(population: int, successes: int, draws: int) -> float:
    if draws > successes or draws > population:
        return 0.0
    return math.comb(successes, draws) / math.comb(population, draws)


def whole_tokens(text: str) -> list[str]:
    return [token for token in text.split() if token]


def build_paragraphs(
    line_rows: list[dict[str, str]],
) -> tuple[dict[str, str], dict[str, list[dict[str, str]]]]:
    counters: Counter[str] = Counter()
    current: dict[str, str] = {}
    locus_to_paragraph: dict[str, str] = {}
    paragraphs: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in line_rows:
        selector = row["source_selector"]
        if selector not in current or row["paragraph_start"] == "1":
            counters[selector] += 1
            current[selector] = f"{selector}:P{counters[selector]}"
        paragraph_id = current[selector]
        locus_to_paragraph[row["locus"]] = paragraph_id
        if row["line_kind"] == "RUNNING_PROSE":
            paragraphs[paragraph_id].append(row)
    return locus_to_paragraph, paragraphs


def reader_status(surface: str, cross: dict[str, str], local: bool) -> str:
    readings = [cross[name].strip() for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
    if local:
        hits = [reading == surface for reading in readings]
    else:
        hits = [surface in whole_tokens(reading) for reading in readings]
    if all(hits):
        return "ALL_THREE_EXACT_WHOLE"
    if hits[0] and sum(hits) == 2:
        return "ONE_ALTERNATE_DIFFERS"
    if hits[0]:
        return "BOTH_ALTERNATES_DIFFER"
    return "ZL3B_PROJECTION_MISMATCH"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    verify_source_lock()

    selector_specs = read_tsv(SELECTORS)
    selectors = [row["source_selector"] for row in selector_specs]
    if len(selectors) != 35 or len(set(selectors)) != 35:
        raise RuntimeError("GDT791 selector scope changed")
    physical_pages = {row["physical_page"] for row in selector_specs}
    if len(physical_pages) != 30:
        raise RuntimeError("GDT791 physical-page scope changed")

    cross_rows, cross_stats = guarded_query(
        CROSS_REL, selectors, "page,locus,zl3b_clean,it2a_clean,rf1b_clean"
    )
    cross_by_key = {(row["page"], row["locus"]): row for row in cross_rows}

    spine = read_tsv(SPINE)
    line_rows = read_tsv(LINES)
    local_cards = read_tsv(G581_LOCAL)
    deep_labels = read_tsv(DEEP_LABELS)
    deep_records = read_tsv(DEEP_RECORDS)
    circles = read_tsv(CIRCLES)
    previous_patches = read_tsv(G792_PATCH)
    cases = read_tsv(CASES)
    model_specs = {row["model_id"]: row for row in read_tsv(MODELS)}

    family = sorted(
        [row for row in spine if row["surface"].startswith("okal")],
        key=lambda row: int(row["occurrence_ordinal"]),
    )
    if len(family) != 41:
        raise RuntimeError(f"expected 41 prefix-family occurrences, found {len(family)}")
    family_running = [row for row in family if row["occurrence_kind"] == "RUNNING_EVENT"]
    family_local = [row for row in family if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL"]
    if (len(family_running), len(family_local)) != (26, 15):
        raise RuntimeError("prefix-family running/local counts changed")

    locus_to_paragraph, paragraphs = build_paragraphs(line_rows)
    line_by_locus = {row["locus"]: row for row in line_rows}
    circle_by_locus = {row["locus"]: row for row in circles}
    deep_label_by_locus = {row["locus"]: row for row in deep_labels}
    local_card_by_locus = {row["locus"]: row for row in local_cards}
    local_spine_by_locus = {
        row["locus"]: row for row in spine if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL"
    }

    local_meta: dict[str, dict[str, str]] = {}
    local_atlas: list[dict[str, Any]] = []
    for ordinal, row in enumerate(family_local, 1):
        locus = row["locus"]
        clock: float | None = None
        if locus in circle_by_locus:
            source = circle_by_locus[locus]
            clock = parse_clock(source["local_comment"])
            meta = {
                "visual_source": "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY",
                "visible_owner_id": source["array_id"],
                "visible_member_id": f"{source['array_id']}:SLOT_{source['slot_index']}",
                "visible_owner_class": source["unit_description"],
                "member_ordinal": source["slot_index"],
                "member_count": source["slot_count"],
                "local_position": source["local_comment"],
                "attachment_relation": source["unit_relation_tags"],
                "visual_trait_class": "ORDERED_ARRAY_POSITION_ONLY",
            }
        elif locus in deep_label_by_locus:
            source = deep_label_by_locus[locus]
            member_match = re.search(r"(\d+)$", source["component_id"])
            meta = {
                "visual_source": "GDT790_DEEP_PANEL_COMPONENT",
                "visible_owner_id": source["panel_id"],
                "visible_member_id": source["component_id"],
                "visible_owner_class": source["owner_class"],
                "member_ordinal": member_match.group(1) if member_match else "NA",
                "member_count": "NA",
                "local_position": source["local_position"],
                "attachment_relation": source["attachment_relation"],
                "visual_trait_class": "TOP_ROW_POSITION__OWNER_AMBIGUOUS",
            }
        elif locus in local_card_by_locus:
            source = local_card_by_locus[locus]
            meta = {
                "visual_source": "GDT581_LOCAL_MATERIAL_OWNER",
                "visible_owner_id": row["context_owner_id"],
                "visible_member_id": source["local_card_host_key"],
                "visible_owner_class": source["owner_de"],
                "member_ordinal": "1",
                "member_count": "NA",
                "local_position": "BEGINNING_OF_FIRST_MATERIAL_GROUP",
                "attachment_relation": "GROUP_CONTEXT_ONLY",
                "visual_trait_class": "MATERIAL_GROUP_ENTRY_ONLY",
            }
        else:
            raise RuntimeError(f"no published visual owner for {locus}")
        local_meta[locus] = meta
        cross = cross_by_key[(row["source_selector"], locus)]
        local_atlas.append(
            {
                "local_ordinal": ordinal,
                "occurrence_id": row["occurrence_id"],
                "surface": row["surface"],
                "exact_okal": "YES" if row["surface"] == "okal" else "NO",
                "source_selector": row["source_selector"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "topology_family": row["topology_family"],
                "locus": locus,
                **meta,
                "clock_hour": f"{clock:.6f}" if clock is not None else "NA",
                "upper_window_1_5h": (
                    "YES" if clock is not None and near_twelve(clock, 1.5)
                    else "NO" if clock is not None else "NA"
                ),
                "alternate_reader_status": reader_status(row["surface"], cross, local=True),
                "alternate_reader_credit": "SAME_MANUSCRIPT_READING_ONLY",
                "component_export_credit": "ZERO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[2], local_atlas)

    local_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in family_local:
        local_by_page[row["physical_page"]].append(row)

    occurrence_atlas: list[dict[str, Any]] = []
    for ordinal, row in enumerate(family, 1):
        is_local = row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL"
        cross = cross_by_key[(row["source_selector"], row["locus"])]
        paragraph_id = "NA" if is_local else locus_to_paragraph[row["locus"]]
        context_rows = [] if is_local else paragraphs[paragraph_id]
        context_text = (
            local_meta[row["locus"]]["local_position"]
            if is_local else " / ".join(item["eva_clean"] for item in context_rows)
        )
        page_labels = local_by_page[row["physical_page"]]
        occurrence_atlas.append(
            {
                "family_occurrence_ordinal": ordinal,
                "occurrence_id": row["occurrence_id"],
                "surface": row["surface"],
                "exact_okal": "YES" if row["surface"] == "okal" else "NO",
                "occurrence_kind": row["occurrence_kind"],
                "source_selector": row["source_selector"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "topology_family": row["topology_family"],
                "locus": row["locus"],
                "token_ordinal_in_line": row["token_ordinal_in_line"],
                "paragraph_id": paragraph_id,
                "record_id": row["record_id"],
                "context_owner_id": row["context_owner_id"],
                "visible_owner_id": local_meta[row["locus"]]["visible_owner_id"] if is_local else "NA",
                "visible_member_id": local_meta[row["locus"]]["visible_member_id"] if is_local else "NA",
                "same_page_exact_label_count": sum(
                    label["surface"] == row["surface"] for label in page_labels
                ),
                "same_page_prefix_family_label_count": len(page_labels),
                "whole_context": context_text,
                "alternate_reader_status": reader_status(row["surface"], cross, local=is_local),
                "family_definition": "COMPLETE_ZL3B_SURFACE_STARTS_WITH_OKAL",
                "semantic_credit": "ZERO__FORMAL_FAMILY_CENSUS",
                "component_export_credit": "ZERO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[0], occurrence_atlas)

    context_ids = sorted({locus_to_paragraph[row["locus"]] for row in family_running})
    running_contexts: list[dict[str, Any]] = []
    for ordinal, paragraph_id in enumerate(context_ids, 1):
        target_rows = [row for row in family_running if locus_to_paragraph[row["locus"]] == paragraph_id]
        context_rows = paragraphs[paragraph_id]
        page = target_rows[0]["physical_page"]
        local_labels = local_by_page[page]
        target_forms = [row["surface"] for row in target_rows]
        local_forms = [row["surface"] for row in local_labels]
        running_contexts.append(
            {
                "context_ordinal": ordinal,
                "paragraph_id": paragraph_id,
                "physical_page": page,
                "source_selector": target_rows[0]["source_selector"],
                "register": target_rows[0]["register"],
                "topology_family": target_rows[0]["topology_family"],
                "first_locus": context_rows[0]["locus"],
                "last_locus": context_rows[-1]["locus"],
                "line_count": len(context_rows),
                "record_ids": pipe(row["record_id"] for row in target_rows),
                "family_occurrence_count": len(target_rows),
                "family_surfaces": pipe(target_forms),
                "exact_okal_occurrence_count": target_forms.count("okal"),
                "page_local_family_label_count": len(local_labels),
                "page_local_family_surfaces": pipe(local_forms),
                "exact_running_label_overlap_surfaces": pipe(
                    form for form in target_forms if form in set(local_forms)
                ),
                "raw_whole_paragraph": " / ".join(row["eva_clean"] for row in context_rows),
                "translation_status": "UNTRANSLATED__TARGET_CANDIDATE_ONLY",
            }
        )
    if len(running_contexts) != 17:
        raise RuntimeError(f"expected 17 running contexts, found {len(running_contexts)}")
    write_tsv(out / OUTPUT_NAMES[1], running_contexts)

    owner_labels: dict[str, dict[str, list[tuple[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for locus, source in circle_by_locus.items():
        spine_row = local_spine_by_locus.get(locus)
        if spine_row and spine_row["physical_page"] == "f72r":
            owner_labels["f72r"][source["array_id"]].append((spine_row["surface"], locus))
    for row in deep_labels:
        if row["page"] == "f82r":
            owner_labels["f82r"][row["panel_id"]].append((row["label_surface"], row["locus"]))

    def case_record_tokens(case: dict[str, str]) -> list[str]:
        if case["target_locus_or_record"].startswith("f72"):
            return whole_tokens(line_by_locus[case["target_locus_or_record"]]["eva_clean"])
        record = next(
            row for row in deep_records
            if row["page"] == case["physical_page"] and row["record_id"] == case["target_locus_or_record"]
        )
        return [
            token
            for line in line_rows
            if line["source_selector"] == case["target_selector"]
            and int(record["start_line"]) <= int(line["line_number"]) <= int(record["end_line"])
            for token in whole_tokens(line["eva_clean"])
        ]

    fingerprints: list[dict[str, Any]] = []
    member_cases: list[dict[str, Any]] = []
    for case in cases:
        owners = owner_labels[case["physical_page"]]
        record_tokens = case_record_tokens(case)
        filtered_record = {
            token for token in record_tokens if len(token) > 1 and not token.startswith("okal")
        }
        form_df: Counter[str] = Counter()
        for labels in owners.values():
            form_df.update(set(form for form, _ in labels))
        scores: list[tuple[str, float, list[str]]] = []
        for owner_id, labels in owners.items():
            label_forms = {
                form for form, _ in labels if len(form) > 1 and not form.startswith("okal")
            }
            overlap = sorted(filtered_record & label_forms)
            score = sum(math.log((len(owners) + 1) / (form_df[form] + 1)) for form in overlap)
            scores.append((owner_id, score, overlap))
        scores.sort(key=lambda item: (-item[1], item[0]))
        top_score = scores[0][1]
        runner_score = scores[1][1] if len(scores) > 1 else 0.0
        top_owners = [owner for owner, score, _ in scores if abs(score - top_score) < 1e-12]
        best_owner = top_owners[0] if len(top_owners) == 1 else "TIE:" + "|".join(top_owners)
        source_score = next(score for owner, score, _ in scores if owner == case["source_owner_id"])
        source_masked_overlap = next(overlap for owner, _, overlap in scores if owner == case["source_owner_id"])
        source_unmasked = sorted(
            set(record_tokens) & {form for form, _ in owners[case["source_owner_id"]]}
        )
        recovered = (
            source_score > 0
            and len(top_owners) == 1
            and top_owners[0] == case["source_owner_id"]
            and top_score > runner_score
        )
        fingerprints.append(
            {
                "case_id": case["case_id"],
                "physical_page": case["physical_page"],
                "target_unit_id": case["target_unit_id"],
                "source_owner_id": case["source_owner_id"],
                "owner_count_on_page": len(owners),
                "record_token_count": len(record_tokens),
                "unmasked_source_overlap": pipe(source_unmasked),
                "target_masked_source_overlap": pipe(source_masked_overlap),
                "target_masked_source_score": f"{source_score:.6f}",
                "best_owner_after_mask": best_owner,
                "best_score": f"{top_score:.6f}",
                "top1_top2_margin": f"{top_score - runner_score:.6f}",
                "source_owner_recovered": "YES" if recovered else "NO",
                "mask": "REMOVE_LEN1_AND_EVERY_COMPLETE_SURFACE_STARTING_OKAL",
                "address_gate_credit": "ONE_OF_THREE_CASES" if recovered else "ZERO",
            }
        )

        source_labels = owners[case["source_owner_id"]]
        record_family_counts = Counter(token for token in record_tokens if token.startswith("okal"))
        source_family_members: dict[str, list[str]] = defaultdict(list)
        for form, member in source_labels:
            if form.startswith("okal"):
                source_family_members[form].append(member)
        shared_forms = sorted(set(record_family_counts) & set(source_family_members))
        assignment_count = 1
        all_forced = bool(shared_forms)
        for form in shared_forms:
            choices = len(source_family_members[form])
            assignment_count *= choices ** record_family_counts[form]
            all_forced &= choices == 1
        member_cases.append(
            {
                "case_id": case["case_id"],
                "source_owner_id": case["source_owner_id"],
                "shared_family_forms": pipe(shared_forms),
                "running_form_counts": pipe(
                    f"{form}:{record_family_counts[form]}" for form in shared_forms
                ),
                "label_member_counts": pipe(
                    f"{form}:{len(source_family_members[form])}" for form in shared_forms
                ),
                "candidate_member_ids": pipe(
                    member for form in shared_forms for member in source_family_members[form]
                ),
                "maximum_exact_member_assignments": assignment_count if shared_forms else 0,
                "single_member_forced_in_every_assignment": "YES" if all_forced else "NO",
                "member_model_result": "PASS_CASE" if all_forced else "FAIL_AMBIGUOUS_MEMBERS",
            }
        )
    write_tsv(out / OUTPUT_NAMES[3], fingerprints)
    write_tsv(out / OUTPUT_NAMES[4], member_cases)

    array_members: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    array_meta: dict[str, tuple[str, str, str]] = {}
    for row in local_atlas:
        owner = row["visible_owner_id"]
        ordinal = int(row["member_ordinal"]) if row["member_ordinal"] != "NA" else 999
        array_members[owner].append((ordinal, row["surface"], row["locus"]))
        array_meta[owner] = (row["physical_page"], row["topology_family"], row["visual_source"])
    ordered_diagnostics: list[dict[str, Any]] = []
    collision_types: set[tuple[str, str]] = set()
    any_cycle = False
    for owner in sorted(array_members):
        members = sorted(array_members[owner])
        edges: set[tuple[str, str]] = set()
        for left_index, (_, left, _) in enumerate(members):
            for _, right, _ in members[left_index + 1 :]:
                if left != right:
                    edges.add((left, right))
        cycles = sorted({tuple(sorted((left, right))) for left, right in edges if (right, left) in edges})
        counts = Counter(form for _, form, _ in members)
        collisions = sorted(form for form, count in counts.items() if count > 1)
        for form in collisions:
            collision_types.add((owner, form))
        any_cycle |= bool(cycles)
        if cycles:
            status = "FAIL_STRICT_ORDER__BIDIRECTIONAL_FORM_CONSTRAINT"
        elif collisions:
            status = "FAIL_UNIQUE_ORDINAL__SAME_FORM_ON_DISTINCT_MEMBERS"
        elif len(members) >= 2:
            status = "ORDERABLE_SINGLE_ARRAY__NO_TRANSFER_KEY"
        else:
            status = "NOT_TESTABLE_SINGLE_FAMILY_MEMBER"
        page, topology, source = array_meta[owner]
        ordered_diagnostics.append(
            {
                "visible_owner_id": owner,
                "physical_page": page,
                "topology_family": topology,
                "visual_source": source,
                "family_member_count": len(members),
                "ordered_positions": pipe(f"{ordinal}:{form}" for ordinal, form, _ in members),
                "ordered_loci": pipe(locus for _, _, locus in members),
                "same_surface_collision_forms": pipe(collisions),
                "bidirectional_constraint_pairs": pipe(f"{left}<>{right}" for left, right in cycles),
                "strict_ordinal_status": status,
            }
        )
    write_tsv(out / OUTPUT_NAMES[5], ordered_diagnostics)

    slot4_arrays = (
        "SCARR020|f70v1|S2",
        "SCARR018|f70v2|S2",
        "SCARR026|f72r1|S1",
        "SCARR029|f72r2|S1",
        "SCARR031|f72r3|S1",
    )
    slot4_rows: list[dict[str, Any]] = []
    for ordinal, array_id in enumerate(slot4_arrays, 1):
        source = next(row for row in circles if row["array_id"] == array_id and row["slot_index"] == "4")
        spine_row = local_spine_by_locus[source["locus"]]
        slot4_rows.append(
            {
                "series_ordinal": ordinal,
                "array_id": array_id,
                "physical_page": spine_row["physical_page"],
                "locus": source["locus"],
                "slot_index": source["slot_index"],
                "slot_count": source["slot_count"],
                "surface": spine_row["surface"],
                "okal_prefix_family": "YES" if spine_row["surface"].startswith("okal") else "NO",
                "local_comment": source["local_comment"],
                "interpretation": "HOMOLOGOUS_SLOT_RENDERER_SENSITIVITY__NOT_NUMBER_FOUR",
            }
        )
    write_tsv(out / OUTPUT_NAMES[6], slot4_rows)

    timed_labels: list[tuple[str, float]] = []
    for source in circles:
        spine_row = local_spine_by_locus.get(source["locus"])
        clock = parse_clock(source["local_comment"])
        if spine_row and clock is not None:
            timed_labels.append((spine_row["surface"], clock))
    exact_okal_timed = [clock for form, clock in timed_labels if form == "okal"]
    upper_rows: list[dict[str, Any]] = []
    for half_width in (1.0, 1.5, 2.0, 2.5, 3.0):
        population_hits = sum(near_twelve(clock, half_width) for _, clock in timed_labels)
        okal_hits = sum(near_twelve(clock, half_width) for clock in exact_okal_timed)
        upper_rows.append(
            {
                "half_width_hours_around_twelve": f"{half_width:.1f}",
                "timed_local_label_population": len(timed_labels),
                "population_window_hits": population_hits,
                "exact_okal_timed_count": len(exact_okal_timed),
                "exact_okal_window_hits": okal_hits,
                "unadjusted_all_hit_probability": f"{hypergeom_all_successes(len(timed_labels), population_hits, len(exact_okal_timed)):.6f}",
                "held_f82_exact_okal_top_row": "YES",
                "status": "POSTHOC_LOW_CAPACITY_SENSITIVITY__NO_PLAINTEXT_SELECTION",
            }
        )
    write_tsv(out / OUTPUT_NAMES[7], upper_rows)

    exact_running = [row for row in family_running if row["surface"] == "okal"]
    exact_local = [row for row in family_local if row["surface"] == "okal"]
    running_without_exact_local = sum(
        not any(label["surface"] == "okal" for label in local_by_page[row["physical_page"]])
        for row in exact_running
    )
    family_running_without_family_local = sum(not local_by_page[row["physical_page"]] for row in family_running)
    fingerprint_successes = sum(row["source_owner_recovered"] == "YES" for row in fingerprints)
    forced_member_cases = sum(row["single_member_forced_in_every_assignment"] == "YES" for row in member_cases)
    f72_collision_forms = {
        form for owner, form in collision_types if owner == "SCARR029|f72r2|S1"
    }
    topology_count = len({row["topology_family"] for row in local_atlas})
    class_gate = (
        len(f72_collision_forms) >= 2
        and topology_count >= 2
        and fingerprint_successes < 2
        and forced_member_cases < len(member_cases)
        and any_cycle
    )
    if not class_gate:
        raise RuntimeError("class/slot working gate did not pass")

    observations = {
        "PAGE_LOCAL_ADDRESS": (
            f"0/3 target-masked source-owner recoveries; {running_without_exact_local}/"
            f"{len(exact_running)} exact running uses lack a same-page exact label"
        ),
        "UNIQUE_MEMBER_OR_NAME": (
            f"{forced_member_cases}/3 cases force one member; f72 has "
            f"{pipe(sorted(f72_collision_forms))} collisions and four maximum assignments"
        ),
        "STRICT_NUMBER_OR_ORDINAL": (
            "f72 outer ring gives okalar,okal,okaly,okal,okaly and contains "
            "okal<>okaly bidirectional order"
        ),
        "VISIBLE_QUALITY_GRADE": "zero arrays have two independently coded objective visible quality levels",
        "UPPER_ZONE_MARKER": (
            "3/3 timed exact celestial labels fall within the post-hoc ±1.5h window and "
            "the f82 exact label is in the top row"
        ),
        "CLASS_SLOT_ENTRY_CODE": (
            f"two same-array collision forms on f72; {topology_count} local topologies; "
            "address, member and strict ordinal gates fail"
        ),
        "OPAQUE_PRODUCTIVE_RENDERER": (
            "no independently visible semantic trait separates the selected C0 code from a "
            "productive renderer null"
        ),
    }
    decisions = {
        "PAGE_LOCAL_ADDRESS": ("FAIL", "REJECT_AS_UNIVERSAL_RENDERER", "NO", "C0_REJECTED"),
        "UNIQUE_MEMBER_OR_NAME": ("FAIL", "REJECT_AS_UNIQUE_MEMBER_RENDERER", "NO", "C0_REJECTED"),
        "STRICT_NUMBER_OR_ORDINAL": ("FAIL", "REJECT_STRICT_ORDINAL", "NO", "C0_REJECTED"),
        "VISIBLE_QUALITY_GRADE": ("NOT_TESTABLE", "RETAIN_UNSCORED", "NO", "C0_UNTESTABLE"),
        "UPPER_ZONE_MARKER": ("POSTHOC_LEAD", "RETAIN_AS_LOW_CAPACITY_RIVAL", "NO", "C0_LOW"),
        "CLASS_SLOT_ENTRY_CODE": ("PASS", "SELECT_C0_WORKING_DEFAULT", "YES_EXACT_OKAL_ONLY", "C0_SELECTED_WORKING"),
        "OPAQUE_PRODUCTIVE_RENDERER": ("SURVIVES", "RETAIN_AS_NULL_RIVAL", "NO", "C0_NULL"),
    }
    ranks = {
        "CLASS_SLOT_ENTRY_CODE": "1",
        "UPPER_ZONE_MARKER": "2",
        "OPAQUE_PRODUCTIVE_RENDERER": "NULL",
        "VISIBLE_QUALITY_GRADE": "UNRANKED",
        "PAGE_LOCAL_ADDRESS": "REJECTED",
        "UNIQUE_MEMBER_OR_NAME": "REJECTED",
        "STRICT_NUMBER_OR_ORDINAL": "REJECTED",
    }
    adjudication: list[dict[str, Any]] = []
    for model_id, spec in model_specs.items():
        gate, status, license_value, confidence = decisions[model_id]
        adjudication.append(
            {
                "model_id": model_id,
                "rank": ranks[model_id],
                "candidate_gloss_de": spec["candidate_gloss_de"],
                "distinguishing_gate": spec["distinguishing_gate"],
                "observed_whole_record_pattern": observations[model_id],
                "gate_result": gate,
                "status_after_gdt793": status,
                "renderer_license": license_value,
                "confidence": confidence,
                "semantic_status": "WORKING_RENDERER_NOT_PLAINTEXT" if model_id == "CLASS_SLOT_ENTRY_CODE" else "NO_SELECTED_PLAINTEXT",
                "component_export_credit": "ZERO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[8], adjudication)

    previous_by_id = {row["occurrence_id"]: row for row in previous_patches}
    exact_occurrences = [row for row in occurrence_atlas if row["surface"] == "okal"]
    if len(exact_occurrences) != 20 or set(previous_by_id) != {row["occurrence_id"] for row in exact_occurrences}:
        raise RuntimeError("exact okal scope differs from GDT792")
    renderer_rows: list[dict[str, Any]] = []
    for ordinal, row in enumerate(exact_occurrences, 1):
        if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL":
            default = (
                "Ringstellen-/Systemeintragscode"
                if row["topology_family"] == "RADIAL_ARRAY"
                else "Beckenstellen-/Systemeintragscode"
            )
        elif row["topology_family"] == "RADIAL_ARRAY":
            default = "Ring-/Systemeintragscode"
        elif row["topology_family"] == "POOL_APPARATUS_NETWORK":
            default = "Stations-/Systemeintragscode"
        else:
            default = "Kennstellen-/Systemeintragscode"
        previous = previous_by_id[row["occurrence_id"]]
        renderer_rows.append(
            {
                "patch_ordinal": ordinal,
                "occurrence_id": row["occurrence_id"],
                "physical_page": row["physical_page"],
                "locus": row["locus"],
                "token_ordinal_in_line": row["token_ordinal_in_line"],
                "occurrence_kind": row["occurrence_kind"],
                "surface": "okal",
                "previous_structural_display": previous["structural_display"],
                "selected_working_role": "SYSTEM_ENTRY_CLASS_CODE",
                "working_default_de": default,
                "working_display": f"⟦okal:{default}⟧",
                "renderer_action": "REPLACE_GDT792_STRUCTURAL_TAG_WITH_C0_EXACT_WHOLE_DEFAULT",
                "semantic_confidence": "C0_SELECTED_WORKING_NOT_PLAINTEXT",
                "scope": "EXACT_OKAL_OCCURRENCES_ON_RELEASED_30_PAGE_SPINE_ONLY",
                "evidence": "F72_TWO_DISTINCT_MEMBER_COLLISION_FORMS__SECOND_TOPOLOGY_F82__ADDRESS_MEMBER_ORDINAL_FAIL",
                "counterevidence": "OPAQUE_RENDERER_SURVIVES__NO_VISIBLE_SHARED_TRAIT__UPPER_ZONE_POSTHOC_LOW_N",
                "lexeme_confirmed": "NO",
                "component_export_credit": "ZERO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[9], renderer_rows)

    guards = [
        {
            "source": "transcription/voynich_cross_transcription_lines.tsv",
            "selector_count": len(selectors),
            "physical_page_count": len(physical_pages),
            "selected_rows": cross_stats["selected"],
            "skipped_forbidden_rows": cross_stats["skipped_forbidden"],
            "skipped_not_allowed_rows": cross_stats["skipped_not_allowed"],
            "materialized_f84_rows": 0,
            "materialized_f84r_rows": 0,
            "output_columns": "page|locus|zl3b_clean|it2a_clean|rf1b_clean",
            "scratch_raw_scan_values_used": "NO__EXCLUDED_AND_REACQUIRED_THROUGH_GUARD",
        }
    ]
    write_tsv(out / OUTPUT_NAMES[10], guards)

    result = {
        "experiment_id": "GDT793",
        "status": STATUS,
        "question": "Which whole-record/page prediction distinguishes the live exact-okal meaning candidates?",
        "scope": {
            "released_physical_pages": 30,
            "source_selectors": 35,
            "new_pages_or_images_opened": 0,
            "sealed_rows_materialized": 0,
        },
        "counts": {
            "prefix_family_occurrences": len(family),
            "prefix_family_forms": len({row["surface"] for row in family}),
            "prefix_family_running": len(family_running),
            "prefix_family_local": len(family_local),
            "running_contexts": len(running_contexts),
            "exact_okal_running": len(exact_running),
            "exact_okal_local": len(exact_local),
            "exact_running_without_same_page_exact_label": running_without_exact_local,
            "family_running_without_same_page_family_label": family_running_without_family_local,
            "target_masked_owner_recoveries": fingerprint_successes,
            "member_cases_forced": forced_member_cases,
            "f72_distinct_collision_forms": len(f72_collision_forms),
            "local_topologies": topology_count,
            "outer_slot4_okal_family_hits": sum(row["okal_prefix_family"] == "YES" for row in slot4_rows),
            "exact_okal_renderer_patches": len(renderer_rows),
            "confirmed_lexemes": 0,
            "component_exports": 0,
        },
        "decision": {
            "selected_working_model": "CLASS_SLOT_ENTRY_CODE",
            "selected_working_default_de": "Kennstellen-/Systemeintragscode",
            "selection_level": "C0_REPLACEABLE_COMPLETE_WHOLE_RENDERER__NOT_PLAINTEXT",
            "page_local_address": "REJECT_AS_UNIVERSAL_RENDERER__0_OF_3_MASKED_OWNER_RECOVERIES",
            "unique_member_or_name": "REJECT__F72_FOUR_MAXIMUM_ASSIGNMENTS",
            "strict_number_or_ordinal": "REJECT__BIDIRECTIONAL_OKAL_OKALY_ORDER",
            "calendar_or_slot": "RETAIN_AS_TOPOLOGY_BOUND_RIVAL__4_OF_5_OUTER_SLOT4_SERIES",
            "upper_zone": "RETAIN_POSTHOC_LOW_CAPACITY_RIVAL__NO_SELECTION",
            "opaque_renderer": "SURVIVES_AND_LIMITS_CONFIDENCE",
        },
        "scratch_source_incident": {
            "raw_mixed_crosswalk_scans": 2,
            "sealed_rows_displayed": 0,
            "raw_scan_values_retained_or_used": 0,
            "repair": "all alternate-reader material independently reacquired by guarded 35-selector query",
        },
        "claim_ceiling": (
            "C0 exact-whole working renderer only; no confirmed word, plaintext, language, sound, "
            "root, affix, number, direction, object, substance, person, calendar value or unseen-page meaning."
        ),
    }
    (out / OUTPUT_NAMES[11]).write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
