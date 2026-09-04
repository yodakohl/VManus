#!/usr/bin/env python3
"""Build GDT792: target-masked complete-whole host transfer on 30 released pages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
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
BASE = ROOT / "experiments/yolo/gdt792_target_masked_image_form_host_transfer"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
FORM_SPECS = SRC / "FORM_CONTROL_SPECS.tsv"
GLOSS_SPECS = SRC / "CANDIDATE_GLOSS_SPECS.tsv"
G791 = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine"
SELECTORS = G791 / "src/PAGE_SELECTOR_SPECS.tsv"
SPINE = G791 / "artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
LINE_ATLAS = G791 / "artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv"
FRAGMENTS = G791 / "artifacts/GDT791_240_RECORD_LOCAL_STATEMENT_FRAGMENTS.tsv"
G581 = ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts"
EVENTS = G581 / "gdt581_5122_content_ready_event_edition.tsv"
STATEMENTS = G581 / "gdt581_793_content_ready_statement_edition.tsv"
LOCAL_CARDS = G581 / "gdt581_744_local_card_hosts.tsv"
G790 = ROOT / "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts"
DEEP_RECORDS = G790 / "GDT790_13_PANEL_RECORD_BINDINGS.tsv"
DEEP_LABELS = G790 / "GDT790_27_LABEL_OWNER_ATLAS.tsv"
DEEP_EDGES = G790 / "GDT790_10_EXACT_LABEL_PROSE_BRIDGES.tsv"
PRIOR_DICT = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
PRIOR_CELLS = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
ZL3B_REL = Path("transcription/voynich_zl3b_lines.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
TARGETS = ("otedy", "okal", "otchdy", "olaiin")
DEEP_PAGES = {"f77r", "f82r", "f83r"}
OUTPUT_NAMES = (
    "GDT792_58_TARGET_OCCURRENCE_HOST_ATLAS.tsv",
    "GDT792_4_TARGET_TRANSFER_SCORECARD.tsv",
    "GDT792_27_DECLARED_CONTROL_PROFILES.tsv",
    "GDT792_64_DETERMINISTIC_CONTROL_DECK.tsv",
    "GDT792_COMPLETE_WHOLE_CROSS_SCOPE_RANKING.tsv",
    "GDT792_CANDIDATE_GLOSS_ADJUDICATION.tsv",
    "GDT792_20_OKAL_EXACT_SCOPE_STRUCTURAL_OVERLAY.tsv",
    "GDT792_4_OKAL_SAME_PAGE_CROSS_OWNER_EDGES.tsv",
    "GDT792_GDT388_2_NEW_F72_EDGE_PACKET.tsv",
    "GDT792_GUARDED_SOURCE_STATS.tsv",
    "GDT792_24_TARGET_CONTROL_CONTRASTS.tsv",
    "RELATION_PACKET_INTAKE.json",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__58_TARGET_OCCURRENCES__48_RUNNING__10_LOCAL__39_OUTSIDE_RUNNING__"
    "9_HELD_RUNNING__6_OUTSIDE_LOCAL__4_HELD_LOCAL__2_PHYSICAL_ROLE_TRANSFERS__"
    "3_LOCAL_SCOPE_TRANSFERS__3_CROSS_TOPOLOGY_LABEL_TRANSFERS__4_OKAL_SAME_PAGE_"
    "CROSS_OWNER_STRING_REUSES__OKAL_CROSS_SCOPE_LABEL_PROSE_WHOLE__PREREGISTERED_"
    "RAW_GATE_PASS__SEMANTIC_GLOSS_UNDERDETERMINED__20_STRUCTURAL_OVERLAYS__15_"
    "PREDECESSOR_QUARANTINES__5_NEW_OVERLAYS__OTEDY_RIVALS_UNSELECTED__ZERO_SEMANTIC_"
    "RENDERER_PATCHES__ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEMES"
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


def rate(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.6f}" if denominator else "NA"


def guarded_query(path: Path, selectors: list[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for selector in selectors:
        command.extend(("--allow", selector))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or f"guarded query failed: {path}")
    stat_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise RuntimeError(f"guard statistics missing or duplicated: {path}")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    stats = {key: int(value) for key, value in json.loads(stat_lines[0][12:]).items()}
    if any(row["page"].startswith("f84") for row in rows):
        raise RuntimeError("sealed selector materialized")
    return rows, stats


def verify_source_lock() -> None:
    if not SOURCE_LOCK.exists():
        raise RuntimeError("source lock is required")
    rows = read_tsv(SOURCE_LOCK)
    if not rows or len({row["path"] for row in rows}) != len(rows):
        raise RuntimeError("source lock is empty or contains duplicate paths")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"invalid source-lock path: {row['path']}")
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"locked source missing: {row['path']}")
        if sha256(path) != row["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {row['path']}")


def physical_line_role(token_ordinal: int, token_count: int) -> str:
    if token_count == 1:
        return "LINE_SINGLETON"
    if token_ordinal == 1:
        return "LINE_INITIAL"
    if token_ordinal == token_count:
        return "LINE_FINAL"
    return "LINE_INTERNAL"


def is_state(event: dict[str, str] | None) -> bool:
    return bool(event and event["state_status"].startswith("STATE"))


def l1_distribution(a: Counter[str], b: Counter[str]) -> float:
    na, nb = sum(a.values()), sum(b.values())
    keys = set(a) | set(b)
    if not na or not nb:
        return 2.0
    return sum(abs(a[key] / na - b[key] / nb) for key in keys)


def dominant_role(rows: list[dict[str, Any]]) -> tuple[str, float]:
    if not rows:
        return "NOT_TESTABLE", 0.0
    counts = Counter(row["physical_line_role"] for row in rows)
    role, count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    share = count / len(rows)
    return (role, share) if share >= 0.60 else ("NO_60_PERCENT_MAJORITY", share)


def lcs_length_table(left: list[str], right: list[str]) -> list[list[int]]:
    """Return suffix LCS lengths for exact whole-token equality."""
    table = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for left_index in range(len(left) - 1, -1, -1):
        for right_index in range(len(right) - 1, -1, -1):
            if left[left_index] == right[right_index]:
                table[left_index][right_index] = 1 + table[left_index + 1][right_index + 1]
            else:
                table[left_index][right_index] = max(
                    table[left_index + 1][right_index], table[left_index][right_index + 1]
                )
    return table


def exact_lcs_token_alignment(
    reference_tokens: list[str], alternate_tokens: list[str], reference_index: int
) -> tuple[str, int | str, int]:
    """Classify one reference token across every maximum exact-token line LCS.

    A positive result is deliberately stricter than finding the nth copy of the
    same surface anywhere on the alternate line.  The reference occurrence must
    be used by every maximum LCS and must have exactly one possible alternate
    token partner.  Duplicate/optional matches remain explicit diagnostics.
    """
    if not 0 <= reference_index < len(reference_tokens):
        raise IndexError("reference token index outside line")
    suffix = lcs_length_table(reference_tokens, alternate_tokens)
    optimum = suffix[0][0]
    prefix = [[0] * (len(alternate_tokens) + 1) for _ in range(len(reference_tokens) + 1)]
    for left_index, left_token in enumerate(reference_tokens):
        for right_index, right_token in enumerate(alternate_tokens):
            if left_token == right_token:
                prefix[left_index + 1][right_index + 1] = 1 + prefix[left_index][right_index]
            else:
                prefix[left_index + 1][right_index + 1] = max(
                    prefix[left_index][right_index + 1], prefix[left_index + 1][right_index]
                )
    possible_partners = [
        right_index
        for right_index, right_token in enumerate(alternate_tokens)
        if reference_tokens[reference_index] == right_token
        and prefix[reference_index][right_index]
        + 1
        + suffix[reference_index + 1][right_index + 1]
        == optimum
    ]
    without_reference = reference_tokens[:reference_index] + reference_tokens[reference_index + 1 :]
    forced = lcs_length_table(without_reference, alternate_tokens)[0][0] < optimum
    if forced and len(possible_partners) == 1:
        return "UNIQUE_FORCED_EXACT", possible_partners[0] + 1, optimum
    if forced:
        return "FORCED_DUPLICATE_EXACT", "NA", optimum
    if possible_partners:
        return "OPTIONAL_OR_DUPLICATE_EXACT", "NA", optimum
    return "NO_EXACT_ALIGNMENT", "NA", optimum


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    verify_source_lock()

    selector_specs = read_tsv(SELECTORS)
    selectors = [row["source_selector"] for row in selector_specs]
    selector_to_page = {row["source_selector"]: row["physical_page"] for row in selector_specs}
    if len(selectors) != 35 or len(set(selectors)) != 35 or len(set(selector_to_page.values())) != 30:
        raise RuntimeError("GDT791 page/selector scope changed")
    source_rows, source_stats = guarded_query(
        ZL3B_REL, selectors,
        "page,locus,line_number,section,language,hand,paragraph_start,paragraph_end,token_count,eva_clean",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, selectors, "page,locus,zl3b_clean,it2a_clean,rf1b_clean"
    )
    spine, line_atlas, fragments = read_tsv(SPINE), read_tsv(LINE_ATLAS), read_tsv(FRAGMENTS)
    events, statements = read_tsv(EVENTS), read_tsv(STATEMENTS)
    local_cards = read_tsv(LOCAL_CARDS)
    deep_records, deep_labels, deep_edges = read_tsv(DEEP_RECORDS), read_tsv(DEEP_LABELS), read_tsv(DEEP_EDGES)
    prior_dictionary, prior_cells = read_tsv(PRIOR_DICT), read_tsv(PRIOR_CELLS)
    control_specs, gloss_specs = read_tsv(FORM_SPECS), read_tsv(GLOSS_SPECS)
    if (len(source_rows), len(cross_rows), len(spine), len(line_atlas), len(fragments), len(events), len(statements), len(local_cards)) != (
        1007, 1007, 5866, 1007, 240, 5122, 793, 744
    ):
        raise RuntimeError("fixed source cardinality changed")
    if (len(deep_records), len(deep_labels), len(deep_edges), len(control_specs)) != (13, 27, 10, 27):
        raise RuntimeError("GDT790/control source cardinality changed")
    prior_okal_rows = [row for row in prior_dictionary if row["surface"] == "okal"]
    if len(prior_okal_rows) != 1 or prior_okal_rows[0]["working_meaning_de"] != "Rohstoffklasse I im heißen Ansatz, Gradanfang":
        raise RuntimeError("canonical predecessor okal card changed")
    prior_okal_default = prior_okal_rows[0]["working_meaning_de"]
    prior_cell_by_position = {
        (row["locus"], int(row["token_ordinal"]), row["surface"]): row
        for row in prior_cells
    }

    source_by_locus = {row["locus"]: row for row in source_rows}
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    line_by_locus = {row["locus"]: row for row in line_atlas}
    event_by_id = {row["event_id"]: row for row in events}
    statement_by_id = {row["statement_id"]: row for row in statements}
    local_by_key = {row["local_card_host_key"]: row for row in local_cards}
    deep_label_by_locus = {row["locus"]: row for row in deep_labels}
    if len(source_by_locus) != 1007 or set(source_by_locus) != set(cross_by_locus) or set(source_by_locus) != set(line_by_locus):
        raise RuntimeError("guarded line loci differ")
    for locus, source in source_by_locus.items():
        if source["eva_clean"] != line_by_locus[locus]["eva_clean"] or source["eva_clean"] != cross_by_locus[locus]["zl3b_clean"]:
            raise RuntimeError(f"line replay mismatch at {locus}")

    # Source-flag paragraph runs, without promoting them to visible paragraphs on diagram pages.
    paragraph_counter: Counter[str] = Counter()
    current_paragraph: dict[str, str] = {}
    paragraph_members: dict[str, list[str]] = defaultdict(list)
    paragraph_id_by_locus: dict[str, str] = {}
    for row in source_rows:
        selector = row["page"]
        if row["paragraph_start"] == "1" or selector not in current_paragraph:
            paragraph_counter[selector] += 1
            current_paragraph[selector] = f"{selector}:P{paragraph_counter[selector]}"
        paragraph_id = current_paragraph[selector]
        paragraph_id_by_locus[row["locus"]] = paragraph_id
        paragraph_members[paragraph_id].append(row["locus"])

    running_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    deep_running_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in spine:
        if row["occurrence_kind"] == "RUNNING_EVENT":
            running_by_locus[row["locus"]].append(row)
            if row["record_id"] != "NONE":
                deep_running_by_record[row["record_id"]].append(row)
    deep_record_position: dict[str, tuple[int, int]] = {}
    for record_id, rows in deep_running_by_record.items():
        for ordinal, row in enumerate(rows, start=1):
            deep_record_position[row["occurrence_id"]] = (ordinal, len(rows))
    fragment_position: dict[str, tuple[str, int, int]] = {}
    for fragment in fragments:
        fragment_events = fragment["event_ids"].split("|")
        for ordinal, event_id in enumerate(fragment_events, start=1):
            if event_id in fragment_position:
                raise RuntimeError(f"event belongs to two record-local fragments: {event_id}")
            fragment_position[event_id] = (fragment["fragment_id"], ordinal, len(fragment_events))

    target_rows: list[dict[str, Any]] = []
    for spine_row in spine:
        surface = spine_row["surface"]
        if surface not in TARGETS:
            continue
        source = source_by_locus[spine_row["locus"]]
        cross = cross_by_locus[spine_row["locus"]]
        token_ordinal, token_count = int(spine_row["token_ordinal_in_line"]), int(source["token_count"])
        tokens = source["eva_clean"].split()
        if tokens[token_ordinal - 1] != surface:
            raise RuntimeError(f"target token replay mismatch at {spine_row['locus']}")
        it2a_tokens, rf1b_tokens = cross["it2a_clean"].split(), cross["rf1b_clean"].split()
        it2a_status, it2a_ordinal, it2a_lcs_length = exact_lcs_token_alignment(
            tokens, it2a_tokens, token_ordinal - 1
        )
        rf1b_status, rf1b_ordinal, rf1b_lcs_length = exact_lcs_token_alignment(
            tokens, rf1b_tokens, token_ordinal - 1
        )
        it2a_exact = it2a_status == "UNIQUE_FORCED_EXACT"
        rf1b_exact = rf1b_status == "UNIQUE_FORCED_EXACT"
        is_running = spine_row["occurrence_kind"] == "RUNNING_EVENT"
        parser_role = parser_ordinal = parser_count = parser_first = parser_final = parser_recipe = parser_state = "NA"
        left_state = right_state = "NA"
        state_neighbor_count: int | str = "NA"
        if is_running:
            event = event_by_id[spine_row["occurrence_id"]]
            statement = statement_by_id[event["statement_id"]]
            parser_ordinal, parser_count = int(event["card_ordinal_in_statement"]), int(statement["event_count"])
            parser_first, parser_final = ("YES" if parser_ordinal == 1 else "NO"), ("YES" if parser_ordinal == parser_count else "NO")
            if parser_count == 1:
                parser_role = "STATEMENT_SINGLETON"
            elif parser_ordinal == 1:
                parser_role = "STATEMENT_FIRST"
            elif parser_ordinal == parser_count:
                parser_role = "STATEMENT_FINAL"
            else:
                parser_role = "STATEMENT_INTERNAL"
            parser_recipe, parser_state = event["final_context_recipe"], event["state_status"]
            line_running = running_by_locus[spine_row["locus"]]
            line_index = next(i for i, item in enumerate(line_running) if item["occurrence_id"] == spine_row["occurrence_id"])
            left_event = event_by_id[line_running[line_index - 1]["occurrence_id"]] if line_index else None
            right_event = event_by_id[line_running[line_index + 1]["occurrence_id"]] if line_index + 1 < len(line_running) else None
            left_state, right_state = ("STATE" if is_state(left_event) else "NONSTATE_OR_EDGE"), ("STATE" if is_state(right_event) else "NONSTATE_OR_EDGE")
            state_neighbor_count = int(is_state(left_event)) + int(is_state(right_event))
        else:
            local = local_by_key[spine_row["occurrence_id"]]
            if (local["surface"], local["locus"]) != (surface, spine_row["locus"]):
                raise RuntimeError("local card identity mismatch")
        paragraph_id = paragraph_id_by_locus[spine_row["locus"]]
        members = paragraph_members[paragraph_id]
        deep_label = deep_label_by_locus.get(spine_row["locus"])
        record_ordinal, record_count = deep_record_position.get(spine_row["occurrence_id"], ("NA", "NA"))
        if isinstance(record_ordinal, int):
            record_role = "RECORD_FIRST" if record_ordinal == 1 else "RECORD_FINAL" if record_ordinal == record_count else "RECORD_INTERNAL"
        else:
            record_role = "NA"
        fragment_id, fragment_ordinal, fragment_count = fragment_position.get(spine_row["occurrence_id"], ("NA", "NA", "NA"))
        if isinstance(fragment_ordinal, int):
            fragment_role = "FRAGMENT_SINGLETON" if fragment_count == 1 else "FRAGMENT_FIRST" if fragment_ordinal == 1 else "FRAGMENT_FINAL" if fragment_ordinal == fragment_count else "FRAGMENT_INTERNAL"
        else:
            fragment_role = "NA"
        target_rows.append({
            "target_occurrence_ordinal": len(target_rows) + 1,
            "surface": surface, "occurrence_id": spine_row["occurrence_id"],
            "occurrence_kind": spine_row["occurrence_kind"],
            "mask_partition": "HELD_DEEP_IMAGE_PAGE" if spine_row["physical_page"] in DEEP_PAGES else "OUTSIDE_27_PAGE_TRAIN",
            "source_selector": spine_row["source_selector"], "physical_page": spine_row["physical_page"],
            "locus": spine_row["locus"], "register": spine_row["register"],
            "topology_family": spine_row["topology_family"], "section": source["section"],
            "language": source["language"] or "UNMARKED", "hand": source["hand"] or "UNMARKED",
            "token_ordinal_in_line": token_ordinal, "token_count_in_line": token_count,
            "physical_line_role": physical_line_role(token_ordinal, token_count),
            "normalized_line_position": f"{0.0 if token_count == 1 else (token_ordinal - 1) / (token_count - 1):.6f}",
            "source_flag_paragraph_run_id": paragraph_id,
            "line_ordinal_in_source_flag_run": members.index(spine_row["locus"]) + 1,
            "line_count_in_source_flag_run": len(members),
            "source_paragraph_start_line": "YES" if source["paragraph_start"] == "1" else "NO",
            "source_paragraph_end_line": "YES" if source["paragraph_end"] == "1" else "NO",
            "left_complete_whole": tokens[token_ordinal - 2] if token_ordinal > 1 else "EDGE",
            "right_complete_whole": tokens[token_ordinal] if token_ordinal < token_count else "EDGE",
            "left_state_card": left_state, "right_state_card": right_state,
            "adjacent_state_card_count": state_neighbor_count,
            "legacy_owner": spine_row["legacy_owner"], "panel_id": spine_row["panel_id"],
            "record_id": spine_row["record_id"], "record_token_ordinal": record_ordinal,
            "record_token_count": record_count, "physical_record_role": record_role,
            "record_local_fragment_id": fragment_id, "record_local_fragment_token_ordinal": fragment_ordinal,
            "record_local_fragment_token_count": fragment_count, "record_local_fragment_role": fragment_role,
            "component_id": spine_row["component_id"],
            "deep_visible_owner_class": deep_label["owner_class"] if deep_label else "NA",
            "deep_visible_attachment": deep_label["attachment_relation"] if deep_label else "NA",
            "parser_statement_role": parser_role, "parser_statement_ordinal": parser_ordinal,
            "parser_statement_event_count": parser_count, "parser_statement_first": parser_first,
            "parser_statement_final": parser_final, "parser_final_context_recipe": parser_recipe,
            "parser_state_status": parser_state,
            "it2a_line_token_count": len(it2a_tokens),
            "it2a_exact_token_lcs_length": it2a_lcs_length,
            "it2a_target_alignment_status": it2a_status,
            "it2a_aligned_token_ordinal": it2a_ordinal,
            "rf1b_line_token_count": len(rf1b_tokens),
            "rf1b_exact_token_lcs_length": rf1b_lcs_length,
            "rf1b_target_alignment_status": rf1b_status,
            "rf1b_aligned_token_ordinal": rf1b_ordinal,
            "all_three_unique_forced_exact_alignment": "YES" if it2a_exact and rf1b_exact else "NO",
            "reader_alignment_method": "ALL_MAXIMUM_SAME_LINE_EXACT_TOKEN_LCS__UNIQUE_FORCED_REFERENCE_OCCURRENCE",
            "reader_diagnostic_credit": "SAME_MANUSCRIPT_ALTERNATE_READING_ONLY",
            "primary_evidence_channel": "PHYSICAL_AND_VISIBLE_OWNER__TARGET_GLOSS_MASKED",
            "parser_channel_credit": "ZERO_INDEPENDENT_SEMANTIC_CREDIT__CIRCULARITY_CONTROL",
            "component_export_credit": "ZERO",
        })
    if len(target_rows) != 58 or Counter(row["occurrence_kind"] for row in target_rows) != Counter({"RUNNING_EVENT": 48, "LOCAL_ADDRESS_OR_LABEL": 10}):
        raise RuntimeError("target occurrence cardinality changed")
    otedy_running = [row for row in target_rows if row["surface"] == "otedy" and row["occurrence_kind"] == "RUNNING_EVENT"]
    if sum(row["all_three_unique_forced_exact_alignment"] == "YES" for row in otedy_running) != 10:
        raise RuntimeError("otedy all-reader exact count changed")

    spine_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in spine:
        spine_by_surface[row["surface"]].append(row)

    def profile(surface: str, target: str, kind: str) -> dict[str, Any]:
        rows = spine_by_surface.get(surface, [])
        running = [row for row in rows if row["occurrence_kind"] == "RUNNING_EVENT"]
        local = [row for row in rows if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL"]
        outside_running = [row for row in running if row["physical_page"] not in DEEP_PAGES]
        held_running = [row for row in running if row["physical_page"] in DEEP_PAGES]
        outside_local = [row for row in local if row["physical_page"] not in DEEP_PAGES]
        held_local = [row for row in local if row["physical_page"] in DEEP_PAGES]

        def roles(items: list[dict[str, str]]) -> Counter[str]:
            return Counter(physical_line_role(int(row["token_ordinal_in_line"]), int(source_by_locus[row["locus"]]["token_count"])) for row in items)

        singleton_local = [row for row in local if source_by_locus[row["locus"]]["token_count"] == "1"]
        outside_singleton = [row for row in outside_local if source_by_locus[row["locus"]]["token_count"] == "1"]
        held_singleton = [row for row in held_local if source_by_locus[row["locus"]]["token_count"] == "1"]
        parser_first = parser_final = parser_singleton = embedded_first = state_any = state_both = 0
        state_counts: Counter[str] = Counter()
        languages: Counter[str] = Counter()
        hands: Counter[str] = Counter()
        registers: Counter[str] = Counter()
        for row in outside_running:
            event = event_by_id[row["occurrence_id"]]
            statement = statement_by_id[event["statement_id"]]
            ordinal, total = int(event["card_ordinal_in_statement"]), int(statement["event_count"])
            parser_first += ordinal == 1
            parser_final += ordinal == total
            parser_singleton += total == 1
            embedded_first += ordinal == 1 and physical_line_role(int(row["token_ordinal_in_line"]), int(source_by_locus[row["locus"]]["token_count"])) != "LINE_INITIAL"
            line_running = running_by_locus[row["locus"]]
            line_index = next(i for i, item in enumerate(line_running) if item["occurrence_id"] == row["occurrence_id"])
            left = event_by_id[line_running[line_index - 1]["occurrence_id"]] if line_index else None
            right = event_by_id[line_running[line_index + 1]["occurrence_id"]] if line_index + 1 < len(line_running) else None
            neighbors = int(is_state(left)) + int(is_state(right))
            state_any += neighbors >= 1
            state_both += neighbors == 2
            state_counts[event["state_status"]] += 1
            source = source_by_locus[row["locus"]]
            languages[source["language"] or "UNMARKED"] += 1
            hands[source["hand"] or "UNMARKED"] += 1
            registers[row["register"]] += 1
        all_parser_final = 0
        for row in running:
            event = event_by_id[row["occurrence_id"]]
            statement = statement_by_id[event["statement_id"]]
            all_parser_final += int(event["card_ordinal_in_statement"]) == int(statement["event_count"])
        outside_roles, held_roles, all_roles = roles(outside_running), roles(held_running), roles(running)
        return {
            "target_surface": target, "comparison_surface": surface, "comparison_kind": kind,
            "surface_length": len(surface), "running_count": len(running),
            "running_page_count": len({row["physical_page"] for row in running}),
            "outside_running_count": len(outside_running),
            "outside_running_page_count": len({row["physical_page"] for row in outside_running}),
            "held_running_count": len(held_running),
            "outside_line_initial_count": outside_roles["LINE_INITIAL"],
            "outside_line_internal_count": outside_roles["LINE_INTERNAL"],
            "outside_line_final_count": outside_roles["LINE_FINAL"],
            "outside_line_internal_rate": rate(outside_roles["LINE_INTERNAL"], len(outside_running)),
            "held_line_initial_count": held_roles["LINE_INITIAL"],
            "held_line_internal_count": held_roles["LINE_INTERNAL"],
            "held_line_final_count": held_roles["LINE_FINAL"],
            "local_count": len(local), "local_page_count": len({row["physical_page"] for row in local}),
            "local_topology_count": len({row["topology_family"] for row in local}),
            "singleton_local_count": len(singleton_local),
            "singleton_local_page_count": len({row["physical_page"] for row in singleton_local}),
            "singleton_local_topology_count": len({row["topology_family"] for row in singleton_local}),
            "outside_local_count": len(outside_local),
            "outside_local_page_count": len({row["physical_page"] for row in outside_local}),
            "outside_local_topology_count": len({row["topology_family"] for row in outside_local}),
            "outside_singleton_local_count": len(outside_singleton),
            "outside_singleton_local_page_count": len({row["physical_page"] for row in outside_singleton}),
            "outside_singleton_local_topology_count": len({row["topology_family"] for row in outside_singleton}),
            "held_local_count": len(held_local), "held_singleton_local_count": len(held_singleton),
            "outside_language_distribution": pipe(f"{key}:{value}" for key, value in sorted(languages.items())),
            "outside_hand_distribution": pipe(f"{key}:{value}" for key, value in sorted(hands.items())),
            "outside_register_distribution": pipe(f"{key}:{value}" for key, value in sorted(registers.items())),
            "outside_state_status_distribution": pipe(f"{key}:{value}" for key, value in sorted(state_counts.items())),
            "outside_parser_statement_first_count": parser_first,
            "outside_parser_statement_final_count": parser_final,
            "outside_parser_singleton_count": parser_singleton,
            "outside_embedded_statement_first_count": embedded_first,
            "outside_embedded_statement_first_rate": rate(embedded_first, len(outside_running)),
            "outside_adjacent_state_any_count": state_any,
            "outside_adjacent_state_both_count": state_both,
            "outside_adjacent_state_both_rate": rate(state_both, len(outside_running)),
            "all_parser_statement_final_count": all_parser_final,
            "all_parser_statement_final_rate": rate(all_parser_final, len(running)),
            "all_physical_line_final_count": all_roles["LINE_FINAL"],
            "all_physical_line_final_rate": rate(all_roles["LINE_FINAL"], len(running)),
            "component_export_credit": "ZERO",
            "_languages": languages, "_hands": hands, "_registers": registers,
        }

    raw_profiles = {surface: profile(surface, surface, "UNIVERSAL") for surface in spine_by_surface}

    def public_profile(row: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in row.items() if not key.startswith("_")}

    declared_rows = []
    for spec in control_specs:
        declared_rows.append(public_profile(profile(spec["comparison_surface"], spec["target_surface"], spec["comparison_kind"])) | {"control_reason": spec["reason"]})
    if len(declared_rows) != 27:
        raise RuntimeError("declared control row count changed")

    # Two deterministic eight-member decks per target: language/frequency and parser-shape matched.
    deck_rows: list[dict[str, Any]] = []
    for target in TARGETS:
        target_profile = raw_profiles[target]
        tn, tp = max(1, target_profile["outside_running_count"]), max(1, target_profile["outside_running_page_count"])
        target_final_rate = int(target_profile["outside_parser_statement_final_count"]) / tn
        candidates = []
        for surface, candidate in raw_profiles.items():
            cn, cp = candidate["outside_running_count"], candidate["outside_running_page_count"]
            if surface in TARGETS or cn < 2 or cp < 1:
                continue
            distance = (
                0.75 * abs(math.log(cn / tn)) + 0.50 * abs(math.log(cp / tp))
                + l1_distribution(target_profile["_languages"], candidate["_languages"])
                + 0.50 * l1_distribution(target_profile["_hands"], candidate["_hands"])
                + 0.50 * l1_distribution(target_profile["_registers"], candidate["_registers"])
                + 0.15 * abs(len(surface) - len(target))
            )
            candidate_final_rate = int(candidate["outside_parser_statement_final_count"]) / cn
            if target_final_rate >= 0.80:
                same_parser_class = candidate_final_rate >= 0.80
                parser_class = "HIGH_STATEMENT_FINAL"
            elif target_final_rate <= 0.20:
                same_parser_class = candidate_final_rate <= 0.20
                parser_class = "LOW_STATEMENT_FINAL"
            else:
                same_parser_class = 0.20 < candidate_final_rate < 0.80
                parser_class = "MIXED_STATEMENT_POSITION"
            candidates.append((distance, surface, same_parser_class, parser_class, candidate))
        language_deck = sorted(candidates, key=lambda item: (item[0], item[1]))[:8]
        shape_deck = sorted((item for item in candidates if item[2]), key=lambda item: (item[0], item[1]))[:8]
        if len(language_deck) != 8 or len(shape_deck) != 8:
            raise RuntimeError(f"insufficient deterministic controls for {target}")
        for deck_name, selected in (("LANGUAGE_FREQUENCY", language_deck), ("PARSER_SHAPE", shape_deck)):
            for rank_ordinal, (distance, surface, _, parser_class, candidate) in enumerate(selected, start=1):
                deck_rows.append({
                    "target_surface": target, "deck": deck_name, "control_rank": rank_ordinal,
                    "control_surface": surface, "matching_distance": f"{distance:.6f}",
                    "target_outside_count": tn, "control_outside_count": candidate["outside_running_count"],
                    "target_outside_pages": tp, "control_outside_pages": candidate["outside_running_page_count"],
                    "parser_class": parser_class,
                    "control_outside_internal_rate": candidate["outside_line_internal_rate"],
                    "control_embedded_statement_first_rate": candidate["outside_embedded_statement_first_rate"],
                    "control_adjacent_state_both_rate": candidate["outside_adjacent_state_both_rate"],
                    "control_component_export_credit": "ZERO__WHOLE_ONLY_COMPARISON",
                })
    if len(deck_rows) != 64:
        raise RuntimeError("deterministic control deck cardinality changed")

    # Outside-to-deep target-mask transfer.
    score_rows: list[dict[str, Any]] = []
    target_profiles = {target: profile(target, target, "TARGET") for target in TARGETS}
    for target in TARGETS:
        rows = [row for row in target_rows if row["surface"] == target]
        outside_running = [row for row in rows if row["occurrence_kind"] == "RUNNING_EVENT" and row["mask_partition"] == "OUTSIDE_27_PAGE_TRAIN"]
        held_running = [row for row in rows if row["occurrence_kind"] == "RUNNING_EVENT" and row["mask_partition"] == "HELD_DEEP_IMAGE_PAGE"]
        outside_local = [row for row in rows if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL" and row["mask_partition"] == "OUTSIDE_27_PAGE_TRAIN"]
        held_local = [row for row in rows if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL" and row["mask_partition"] == "HELD_DEEP_IMAGE_PAGE"]
        predicted_role, train_share = dominant_role(outside_running)
        held_hits = sum(row["physical_line_role"] == predicted_role for row in held_running)
        held_share = held_hits / len(held_running) if held_running else 0.0
        physical_result = "NOT_TESTABLE" if predicted_role == "NO_60_PERCENT_MAJORITY" or not held_running else "PASS" if held_share >= 0.60 else "FAIL"
        label_result = "PASS" if outside_local and held_local else "NOT_TESTABLE"
        outside_topologies = {row["topology_family"] for row in outside_local}
        held_topologies = {row["topology_family"] for row in held_local}
        novel_topologies = held_topologies - outside_topologies
        topology_result = "PASS" if outside_local and held_local and novel_topologies else "NOT_TESTABLE"
        running = [row for row in rows if row["occurrence_kind"] == "RUNNING_EVENT"]
        parser_final = sum(row["parser_statement_final"] == "YES" for row in running)
        physical_final = sum(row["physical_line_role"] == "LINE_FINAL" for row in running)
        overall = "PASS_PHYSICAL_AND_LOCAL_SCOPE" if physical_result == label_result == "PASS" else "PARTIAL_ONE_CHANNEL" if "PASS" in {physical_result, label_result} else "NO_TRANSFER_OR_INSUFFICIENT"
        score_rows.append({
            "target_surface": target, "outside_running_count": len(outside_running), "held_running_count": len(held_running),
            "outside_majority_physical_role": predicted_role, "outside_majority_share": f"{train_share:.6f}",
            "held_role_hit_count": held_hits, "held_role_share": rate(held_hits, len(held_running)),
            "physical_role_transfer": physical_result, "outside_local_count": len(outside_local),
            "outside_local_pages": pipe(sorted({row["physical_page"] for row in outside_local})),
            "outside_local_topologies": pipe(sorted(outside_topologies)), "held_local_count": len(held_local),
            "held_local_pages": pipe(sorted({row["physical_page"] for row in held_local})),
            "held_local_topologies": pipe(sorted(held_topologies)), "local_scope_transfer": label_result,
            "novel_held_local_topologies": pipe(sorted(novel_topologies)),
            "cross_topology_label_transfer": topology_result,
            "parser_statement_final_count": parser_final, "physical_line_final_count": physical_final,
            "parser_physical_final_divergence": parser_final - physical_final,
            "overall_host_transfer": overall, "meaning_credit": "C0_ROLE_RANKING_ONLY",
            "component_export_credit": "ZERO",
        })
    if Counter(row["physical_role_transfer"] for row in score_rows) != Counter({"PASS": 2, "NOT_TESTABLE": 1, "FAIL": 1}):
        raise RuntimeError(f"unexpected physical transfers: {score_rows}")
    if Counter(row["local_scope_transfer"] for row in score_rows) != Counter({"PASS": 3, "NOT_TESTABLE": 1}):
        raise RuntimeError("unexpected local scope transfers")
    if Counter(row["cross_topology_label_transfer"] for row in score_rows) != Counter({"PASS": 3, "NOT_TESTABLE": 1}):
        raise RuntimeError("unexpected topology transfers")

    # Three explicit metrics against both deterministic decks. Only LINE_INTERNAL is
    # fully physical; the other two are retained as mixed/parser circularity controls.
    contrast_rows: list[dict[str, Any]] = []
    for target in TARGETS:
        target_profile = target_profiles[target]
        held = [row for row in target_rows if row["surface"] == target and row["occurrence_kind"] == "RUNNING_EVENT" and row["mask_partition"] == "HELD_DEEP_IMAGE_PAGE"]
        held_metrics = {
            "PHYSICAL_LINE_INTERNAL": sum(row["physical_line_role"] == "LINE_INTERNAL" for row in held) / len(held),
            "EMBEDDED_STATEMENT_FIRST": sum(row["parser_statement_first"] == "YES" and row["physical_line_role"] != "LINE_INITIAL" for row in held) / len(held),
            "BOTH_ADJACENT_STATE_CARDS": sum(row["adjacent_state_card_count"] == 2 for row in held) / len(held),
        }
        target_metrics = {
            "PHYSICAL_LINE_INTERNAL": float(target_profile["outside_line_internal_rate"]),
            "EMBEDDED_STATEMENT_FIRST": float(target_profile["outside_embedded_statement_first_rate"]),
            "BOTH_ADJACENT_STATE_CARDS": float(target_profile["outside_adjacent_state_both_rate"]),
        }
        control_fields = {
            "PHYSICAL_LINE_INTERNAL": "control_outside_internal_rate",
            "EMBEDDED_STATEMENT_FIRST": "control_embedded_statement_first_rate",
            "BOTH_ADJACENT_STATE_CARDS": "control_adjacent_state_both_rate",
        }
        channels = {
            "PHYSICAL_LINE_INTERNAL": "PRIMARY_PHYSICAL",
            "EMBEDDED_STATEMENT_FIRST": "MIXED_PHYSICAL_PLUS_PARSER",
            "BOTH_ADJACENT_STATE_CARDS": "PARSER_COUPLED_NEIGHBOR_STATE",
        }
        for metric in ("PHYSICAL_LINE_INTERNAL", "EMBEDDED_STATEMENT_FIRST", "BOTH_ADJACENT_STATE_CARDS"):
            for deck in ("LANGUAGE_FREQUENCY", "PARSER_SHAPE"):
                controls = [float(row[control_fields[metric]]) for row in deck_rows if row["target_surface"] == target and row["deck"] == deck]
                target_value = target_metrics[metric]
                contrast_rows.append({
                    "target_surface": target, "metric": metric, "evidence_channel": channels[metric],
                    "control_deck": deck, "target_outside_rate": f"{target_value:.6f}",
                    "control_min_rate": f"{min(controls):.6f}", "control_median_rate": f"{sorted(controls)[3:5][0] / 2 + sorted(controls)[3:5][1] / 2:.6f}",
                    "control_max_rate": f"{max(controls):.6f}",
                    "strictly_beaten_controls": sum(target_value > value for value in controls),
                    "tied_controls": sum(target_value == value for value in controls),
                    "higher_controls": sum(target_value < value for value in controls),
                    "seven_of_eight_control_gate": "PASS" if sum(target_value > value for value in controls) >= 7 else "FAIL",
                    "held_deep_rate": f"{held_metrics[metric]:.6f}",
                    "held_matches_or_exceeds_60_percent": "YES" if held_metrics[metric] >= 0.60 else "NO",
                    "semantic_credit": "PRIMARY_ROLE_ONLY" if channels[metric] == "PRIMARY_PHYSICAL" else "ZERO_INDEPENDENT__CIRCULARITY_DIAGNOSTIC",
                })
    if len(contrast_rows) != 24:
        raise RuntimeError("target/control contrast cardinality changed")

    # Exhaustive cross-scope rank among every complete form with 3–25 running uses.
    ranking_rows: list[dict[str, Any]] = []
    for surface in sorted(spine_by_surface):
        row = public_profile(profile(surface, surface, "UNIVERSAL_3_TO_25_RUNNING"))
        if 3 <= int(row["running_count"]) <= 25:
            ranking_rows.append(row)
    ranking_rows.sort(key=lambda row: (
        -int(row["singleton_local_page_count"]), -int(row["singleton_local_topology_count"]),
        -int(row["singleton_local_count"]), -int(row["local_page_count"]),
        -int(row["running_page_count"]), row["comparison_surface"],
    ))
    for ordinal, row in enumerate(ranking_rows, start=1):
        row["cross_scope_rank"] = ordinal
        row["target_flag"] = "YES" if row["comparison_surface"] in TARGETS else "NO"
        row["outside_train_eligible"] = "YES" if 3 <= int(row["outside_running_count"]) <= 25 else "NO"
        row["outside_train_cross_scope_rank"] = "NA"
        row["outside_train_multichar_rank"] = "NA"
    outside_train_rows = [row for row in ranking_rows if row["outside_train_eligible"] == "YES"]
    outside_train_rows.sort(key=lambda row: (
        -int(row["outside_singleton_local_page_count"]),
        -int(row["outside_singleton_local_topology_count"]),
        -int(row["outside_singleton_local_count"]),
        -int(row["outside_local_page_count"]),
        -int(row["outside_running_page_count"]), row["comparison_surface"],
    ))
    for ordinal, row in enumerate(outside_train_rows, start=1):
        row["outside_train_cross_scope_rank"] = ordinal
    outside_train_multichar = [row for row in outside_train_rows if int(row["surface_length"]) > 1]
    for ordinal, row in enumerate(outside_train_multichar, start=1):
        row["outside_train_multichar_rank"] = ordinal
    okal_rank = next(row for row in ranking_rows if row["comparison_surface"] == "okal")
    if int(okal_rank["cross_scope_rank"]) != 1 or (
        int(okal_rank["singleton_local_count"]), int(okal_rank["singleton_local_page_count"]), int(okal_rank["singleton_local_topology_count"])
    ) != (4, 3, 2):
        raise RuntimeError("okal no longer leads recurrent singleton-label rank")
    if (int(okal_rank["outside_train_cross_scope_rank"]), int(okal_rank["outside_train_multichar_rank"])) != (4, 2):
        raise RuntimeError("okal training-only rank changed")

    # Two new f72 Ring-D-label -> Ring-E-prose exact-whole edges, plus two retained f82 edges.
    f72_labels = [row for row in target_rows if row["surface"] == "okal" and row["locus"] in {"f72r2.9", "f72r2.11"}]
    f72_prose = [row for row in target_rows if row["surface"] == "okal" and row["locus"] == "f72r2.22"]
    if len(f72_labels) != 2 or len(f72_prose) != 1 or f72_prose[0]["token_ordinal_in_line"] != 19:
        raise RuntimeError("f72 okal endpoints changed")
    cross_owner_rows: list[dict[str, Any]] = []
    for label in f72_labels:
        cross_owner_rows.append({
            "edge_id": f"GDT792-X{len(cross_owner_rows)+1:02d}", "source_experiment": "GDT792_NEW",
            "physical_page": "f72r", "label_locus": label["locus"], "label_owner": label["legacy_owner"],
            "label_surface": "okal", "prose_locus": "f72r2.22", "prose_token_ordinal": 19,
            "prose_owner": f72_prose[0]["legacy_owner"], "same_page": "YES", "cross_owner": "YES",
            "edge_class": "EXACT_COMPLETE_WHOLE_CROSS_OWNER_REUSE",
            "semantic_credit": "ZERO__STRING_REUSE_AND_OWNER_SEPARATION_ONLY",
        })
    for edge in deep_edges:
        if edge["label_token"] == "okal":
            cross_owner_rows.append({
                "edge_id": f"GDT792-X{len(cross_owner_rows)+1:02d}", "source_experiment": "GDT790_RETAINED",
                "physical_page": edge["label_page"], "label_locus": edge["label_locus"],
                "label_owner": edge["label_component_id"], "label_surface": edge["label_token"],
                "prose_locus": edge["prose_locus"], "prose_token_ordinal": edge["prose_token_ordinals"],
                "prose_owner": edge["prose_record_id"], "same_page": edge["same_page"], "cross_owner": "YES",
                "edge_class": "EXACT_COMPLETE_WHOLE_CROSS_OWNER_REUSE",
                "semantic_credit": "ZERO__STRING_REUSE_AND_OWNER_SEPARATION_ONLY",
            })
    if len(cross_owner_rows) != 4 or Counter(row["source_experiment"] for row in cross_owner_rows) != Counter({"GDT792_NEW": 2, "GDT790_RETAINED": 2}):
        raise RuntimeError("four okal cross-owner edges not recovered")

    packet_rows = []
    for ordinal, edge in enumerate(cross_owner_rows[:2], start=1):
        packet_rows.append({
            "edge_id": f"G792-E{ordinal:03d}", "batch_id": "GDT792_F72_OKAL_CROSS_OWNER",
            "page": "f72r2", "physical_folio": "f72", "diagram_unit_id": "F72R_RING_D_TO_RING_E",
            "pivot_visual_id": f"LABEL:{edge['label_locus']}", "pivot_locus": edge["label_locus"],
            "target_visual_id": "PROSE:f72r2.22:19", "target_locus": "f72r2.22@19",
            "relation_type": "EXACT_COMPLETE_WHOLE_CROSS_OWNER_REUSE_CANDIDATE",
            "direction_basis": "NONE__TRANSCRIPTION_ORDER_IS_NOT_REFERENCE_DIRECTION",
            "ownership_basis": "EXISTING_RING_D_LABEL_AND_RING_E_PROSE_OWNER",
            "geometry_only_selection": "FALSE", "source_manifest_id": "GDT515_OWNER_LAYER__GDT791_VISUAL_OWNER_SPINE",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT792_RUNNER", "relation_reviewer": "GDT792_VALIDATOR",
            "relation_confidence": "EXPLORATORY_EXACT_STRING", "ambiguity_state": "SEMANTIC_RELATION_UNRESOLVED",
            "formal_access_state": "SEALED_NOT_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXACT_STRING_REFERENCE_ONLY",
        })

    okal_profile = target_profiles["okal"]
    okal_score = next(row for row in score_rows if row["target_surface"] == "okal")
    okal_physical_contrasts = [row for row in contrast_rows if row["target_surface"] == "okal" and row["metric"] == "PHYSICAL_LINE_INTERNAL"]
    okal_deck_controls = {
        deck: {row["control_surface"] for row in deck_rows if row["target_surface"] == "okal" and row["deck"] == deck}
        for deck in ("LANGUAGE_FREQUENCY", "PARSER_SHAPE")
    }
    okal_raw_conditions = {
        "outside_two_singleton_pages": int(okal_profile["outside_singleton_local_count"]) >= 2 and len(okal_score["outside_local_pages"].split("|")) >= 2,
        "held_singleton_new_topology": int(okal_profile["held_singleton_local_count"]) >= 1 and okal_score["cross_topology_label_transfer"] == "PASS",
        "running_internal_transfer": okal_score["outside_majority_physical_role"] == "LINE_INTERNAL" and okal_score["physical_role_transfer"] == "PASS",
        "physical_role_beats_seven_of_eight_in_both_decks": len(okal_physical_contrasts) == 2 and all(row["seven_of_eight_control_gate"] == "PASS" for row in okal_physical_contrasts),
        "all_30_page_cross_scope_rank_first": int(okal_rank["cross_scope_rank"]) == 1,
        "outside_and_held_cross_owner_string_reuse_present": len(cross_owner_rows) == 4,
    }
    if not all(okal_raw_conditions.values()):
        raise RuntimeError(f"preregistered okal observable conditions failed: {okal_raw_conditions}")
    okal_selection_vetoes = {
        "training_only_rank_not_first": int(okal_rank["outside_train_cross_scope_rank"]) != 1,
        "relation_edges_have_zero_semantic_credit": all(row["semantic_credit"].startswith("ZERO__") for row in cross_owner_rows),
        "candidate_glosses_not_discriminated_by_observed_predictions": True,
        "address_class_and_member_remain_observationally_equivalent": True,
    }
    if not all(okal_selection_vetoes.values()):
        raise RuntimeError(f"okal semantic veto accounting changed: {okal_selection_vetoes}")

    gloss_rows = []
    for spec in gloss_specs:
        target, rank = spec["target_surface"], int(spec["candidate_rank"])
        if target == "okal" and rank == 1:
            after = "PREREGISTERED_TRIGGER_PASS__SEMANTICALLY_UNDERDETERMINED__NOT_SELECTED"
            evidence = "4 singleton labels/3 pages/2 topologies; 15/16 prose uses line-internal (13/14 outside, 2/2 held); 4 same-page cross-owner edges"
            counter = "all-30 rank leaks held labels; edges have zero semantic credit; address, class, and addressed-member predictions tie"
        elif target == "okal" and rank == 2:
            after = "ACTIVE_UNDISCRIMINATED_C0_RIVAL__STRUCTURAL_OVERLAY_ONLY__NOT_SELECTED"
            evidence = "same exact whole is a singleton label on four loci and a line-internal running form at 15/16 loci"
            counter = "label-compatible form is established, but identifier/class plaintext is not"
        elif target == "okal" and rank == 3:
            after, evidence, counter = "ACTIVE_UNDISCRIMINATED_C0_RIVAL__NOT_SELECTED", "same complete-whole cross-scope geometry", "not distinguished from address or class; no lexical anchor"
        elif target == "okal":
            after, evidence, counter = "ACTIVE_UNDISCRIMINATED_C0_RIVAL__NOT_SELECTED", "limited compatibility", "cross-register repeated-label geometry is not distinctive for this reading"
        elif target == "otedy" and rank == 1:
            after = "BOLD_C0_STRUCTURAL_RIVAL__NOT_SELECTED"
            evidence = "18/18 parser-final but only 1/18 physical-line-final; 9 singleton and 9 attached fields"
            counter = "DY parser coupling has zero independent semantic credit; only 10/18 running wholes all-reader exact"
        elif target == "otedy" and rank == 2:
            after = "BOLD_C0_VISUAL_RIVAL__F77_SPECIFIC__NOT_SELECTED"
            evidence = "reader-stable f77 inner-port label and next visible record reuse"
            counter = "one port; zero outside local labels; Currier-B confounding"
        else:
            after, evidence, counter = "ACTIVE_C0_RIVAL__NOT_SELECTED", "complete-whole role compatibility", "insufficient independent capacity"
        gloss_rows.append({**spec, "status_after_scoring": after, "evidence": evidence,
            "counterevidence": counter, "confidence": "C0_EXPLORATORY_HYPOTHESIS",
            "preregistered_gate_result": "PASS_RAW_OBSERVABLES" if target == "okal" and rank == 1 else "NOT_APPLICABLE",
            "semantic_discrimination_result": "UNDERDETERMINED",
            "renderer_license": "NO", "semantic_credit": "ZERO",
            "lexeme_confirmed": "NO", "component_export_credit": "ZERO"})

    okal_occurrences = [row for row in target_rows if row["surface"] == "okal"]
    patch_rows = []
    for row in okal_occurrences:
        prior_cell = prior_cell_by_position.get((row["locus"], int(row["token_ordinal_in_line"]), "okal"))
        patch_rows.append({
            "patch_id": f"GDT792-P{len(patch_rows)+1:03d}", "occurrence_id": row["occurrence_id"],
            "physical_page": row["physical_page"], "locus": row["locus"],
            "token_ordinal_in_line": row["token_ordinal_in_line"], "surface": "okal",
            "occurrence_kind": row["occurrence_kind"],
            "predecessor_presence": "PRESENT_IN_GDT734_CACHE" if prior_cell else "ABSENT__NEW_30_PAGE_OVERLAY",
            "superseded_dictionary_card": prior_okal_default if prior_cell else "NONE",
            "superseded_cache_display": prior_cell["v99r7_spoken_cell_de"] if prior_cell else "NONE",
            "structural_display": "⟦okal:CROSS_SCOPE_LABEL_PROSE_WHOLE⟧",
            "structural_tag": "CROSS_SCOPE_LABEL_PROSE_WHOLE",
            "preregistered_gate_result": "RAW_OBSERVABLE_TRIGGER_PASS",
            "selected_semantic_gloss": "NONE",
            "renderer_action": "STRUCTURAL_TAG_ONLY__NO_SEMANTIC_DISPLAY",
            "prior_default_action": "QUARANTINE_IF_PRESENT__NOT_SEMANTICALLY_REFUTED",
            "semantic_confidence": "C0_UNDERDETERMINED",
            "scope": "EXACT_OCCURRENCE_ON_RELEASED_30_PAGE_SPINE_ONLY",
            "evidence": "EXACT_COMPLETE_WHOLE_CROSS_SCOPE_HOST_TRANSFER",
            "counterevidence": "NO_CONFIRMED_PLAINTEXT__ADDRESS_VS_CLASS_VS_MEMBER_UNRESOLVED",
            "lexeme_confirmed": "NO", "component_export_credit": "ZERO",
        })
    if len(patch_rows) != 20 or Counter(row["occurrence_kind"] for row in patch_rows) != Counter({"RUNNING_EVENT": 16, "LOCAL_ADDRESS_OR_LABEL": 4}):
        raise RuntimeError("okal patch cardinality changed")
    if Counter(row["predecessor_presence"] for row in patch_rows) != Counter({"PRESENT_IN_GDT734_CACHE": 15, "ABSENT__NEW_30_PAGE_OVERLAY": 5}):
        raise RuntimeError("okal predecessor/new-overlay partition changed")

    # Base rate for the same 60% rule.  This prevents a common line-internal
    # transfer from being described as semantic discrimination.
    baseline_testable = baseline_pass = baseline_internal_testable = baseline_internal_pass = 0
    for candidate in raw_profiles.values():
        if not 3 <= int(candidate["running_count"]) <= 25:
            continue
        outside_n, held_n = int(candidate["outside_running_count"]), int(candidate["held_running_count"])
        if not outside_n or not held_n:
            continue
        outside_counts = {
            "LINE_INITIAL": int(candidate["outside_line_initial_count"]),
            "LINE_INTERNAL": int(candidate["outside_line_internal_count"]),
            "LINE_FINAL": int(candidate["outside_line_final_count"]),
        }
        predicted_role, predicted_count = sorted(outside_counts.items(), key=lambda item: (-item[1], item[0]))[0]
        if predicted_count / outside_n < 0.60:
            continue
        held_hits = int(candidate[f"held_line_{predicted_role.removeprefix('LINE_').lower()}_count"])
        passed = held_hits / held_n >= 0.60
        baseline_testable += 1
        baseline_pass += int(passed)
        if predicted_role == "LINE_INTERNAL":
            baseline_internal_testable += 1
            baseline_internal_pass += int(passed)

    guarded_rows = [
        {"source": str(ZL3B_REL), "selector_count": 35, "physical_page_count": 30,
         "selected_rows": source_stats.get("selected", -1), "skipped_forbidden_rows": source_stats.get("skipped_forbidden", -1),
         "skipped_not_allowed_rows": source_stats.get("skipped_not_allowed", -1), "materialized_f84_rows": 0,
         "materialized_f84r_rows": 0,
         "output_columns": "page|locus|line_number|section|language|hand|paragraph_start|paragraph_end|token_count|eva_clean"},
        {"source": str(CROSS_REL), "selector_count": 35, "physical_page_count": 30,
         "selected_rows": cross_stats.get("selected", -1), "skipped_forbidden_rows": cross_stats.get("skipped_forbidden", -1),
         "skipped_not_allowed_rows": cross_stats.get("skipped_not_allowed", -1), "materialized_f84_rows": 0,
         "materialized_f84r_rows": 0, "output_columns": "page|locus|zl3b_clean|it2a_clean|rf1b_clean"},
    ]

    for name, rows in zip(OUTPUT_NAMES[:10], [target_rows, score_rows, declared_rows, deck_rows, ranking_rows,
        gloss_rows, patch_rows, cross_owner_rows, packet_rows, guarded_rows], strict=True):
        write_tsv(out / name, rows)
    write_tsv(out / OUTPUT_NAMES[10], contrast_rows)
    intake_completed = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(out / OUTPUT_NAMES[8])], cwd=ROOT, text=True, capture_output=True, check=False)
    if intake_completed.returncode:
        raise RuntimeError(intake_completed.stderr or intake_completed.stdout or "relation intake failed")
    relation_intake = json.loads(intake_completed.stdout)
    if relation_intake["packet_rows"] != 2 or relation_intake["eligible_edges"] != 0 or relation_intake["score_ready"]:
        raise RuntimeError(f"unexpected relation intake: {relation_intake}")
    (out / OUTPUT_NAMES[11]).write_text(json.dumps(relation_intake, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    outside_otedy_singletons = sum(row["surface"] == "otedy" and row["mask_partition"] == "OUTSIDE_27_PAGE_TRAIN" and row["parser_statement_role"] == "STATEMENT_SINGLETON" for row in target_rows)
    deep_otedy_singletons = sum(row["surface"] == "otedy" and row["mask_partition"] == "HELD_DEEP_IMAGE_PAGE" and row["record_local_fragment_role"] == "FRAGMENT_SINGLETON" for row in target_rows)
    if (outside_otedy_singletons, deep_otedy_singletons) != (7, 2):
        raise RuntimeError("GDT791-corrected otedy singleton partition changed")
    result = {
        "experiment_id": "GDT792", "status": STATUS,
        "decision": {
            "okal": "SELECT_CROSS_SCOPE_LABEL_PROSE_WHOLE_STRUCTURAL_TAG__WITHHOLD_ALL_SEMANTIC_GLOSSES",
            "otedy": "KEEP_BOUNDED_E_FIELD_AND_F77_PORT_STATUS_AS_BOLD_C0_RIVALS__DO_NOT_SELECT",
            "otchdy": "LOW_CAPACITY_CROSS_TOPOLOGY_LABEL_ROLE_ONLY",
            "olaiin": "CROSS_TOPOLOGY_LABEL_ROLE_TRANSFERS_BUT_RUNNING_PHYSICAL_ROLE_FAILS",
        },
        "counts": {
            "released_pages": 30, "outside_training_pages": 27, "held_deep_pages": 3,
            "source_selectors": 35, "source_lines": 1007, "source_tokens": 5866,
            "target_occurrences": 58, "target_running": 48, "target_local": 10,
            "outside_running": 39, "held_running": 9, "outside_local": 6, "held_local": 4,
            "physical_role_transfer_passes": 2, "physical_role_transfer_failures": 1,
            "physical_role_not_testable": 1, "local_scope_transfer_passes": 3,
            "cross_topology_label_transfer_passes": 3, "declared_profile_rows": 27,
            "deterministic_control_deck_rows": 64, "target_control_contrasts": 24,
            "new_f72_edges": 2, "retained_f82_edges": 2,
            "okal_same_page_cross_owner_edges": 4, "okal_running_occurrences": 16,
            "okal_local_occurrences": 4, "okal_exact_scope_structural_overlays": 20,
            "okal_gdt734_predecessor_quarantines": 15, "okal_new_structural_overlays": 5,
            "selected_semantic_glosses": 0, "semantic_renderer_patches": 0,
            "otedy_running_all_three_reader_unique_forced_exact_alignment": 10,
            "confirmed_lexemes": 0,
            "otedy_corrected_singleton_fields": outside_otedy_singletons + deep_otedy_singletons,
            "otedy_corrected_attached_fields": 18 - outside_otedy_singletons - deep_otedy_singletons,
            "component_exports": 0, "sealed_rows_materialized": 0,
        },
        "okal_preregistered_raw_observable_trigger": {
            "result": "PASS",
            "conditions": okal_raw_conditions,
        },
        "okal_semantic_selection": {
            "result": "WITHHELD__OBSERVATIONS_DO_NOT_DISCRIMINATE_REGISTERED_RIVALS",
            "vetoes": okal_selection_vetoes,
            "all_30_rank": int(okal_rank["cross_scope_rank"]),
            "outside_train_rank": int(okal_rank["outside_train_cross_scope_rank"]),
            "outside_train_multichar_rank": int(okal_rank["outside_train_multichar_rank"]),
        },
        "control_deck_dependence": {
            "okal_language_frequency_controls": len(okal_deck_controls["LANGUAGE_FREQUENCY"]),
            "okal_parser_shape_controls": len(okal_deck_controls["PARSER_SHAPE"]),
            "overlap": len(okal_deck_controls["LANGUAGE_FREQUENCY"] & okal_deck_controls["PARSER_SHAPE"]),
            "unique_union": len(okal_deck_controls["LANGUAGE_FREQUENCY"] | okal_deck_controls["PARSER_SHAPE"]),
            "interpretation": "Sensitivity decks, not independent confirmations.",
        },
        "physical_transfer_baseline": {
            "cohort": "complete wholes with 3-25 running occurrences and a testable outside-to-held 60-percent role",
            "testable_forms": baseline_testable,
            "passing_forms": baseline_pass,
            "predicted_line_internal_testable_forms": baseline_internal_testable,
            "predicted_line_internal_passing_forms": baseline_internal_pass,
        },
        "parser_circularity_control": {
            "otedy_running_statement_final": 18, "otedy_running_physical_line_final": 1,
            "interpretation": "Parser closure is not physical record closure and receives zero independent meaning credit.",
        },
        "relation_packet": relation_intake,
        "next": "Discriminate okal address versus class versus addressed-member at paragraph/page scale; separately test otedy bounded-field versus f77 port-status with unique-forced reader alignments.",
        "claim_ceiling": "The experiment may select occurrence-conditioned complete-whole renderer defaults and reject earlier renderer cards. It cannot confirm a lexeme, plaintext, language, sound value, free root or affix, object identity, process direction, number, substance, disease, plant, person, or unseen-page meaning.",
    }
    (out / OUTPUT_NAMES[12]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
