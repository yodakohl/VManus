#!/usr/bin/env python3
"""Build a deterministic line-level interpreter from confirmed structures.

This is an export/audit, not a semantic search.  It composes the already
confirmed visible-word roles, five exact mandatory D/E -> q edges, and
isolated REL_I/FREE_L/FREE_R detached completions into one expression per
prose line.  The former L_SERIAL and REL_TO_FREE edges are deliberately
excluded after their corrected position-zone audits. Maximal adjacent active
edges form one component, plain spans are explicit, FREE_A closure and
paragraph opening are retained, and cached geometry adds only previously
confirmed soft-break and right-restart markers. Qualified
bare-d/s/t initial-carrier states from v0.41 are retained separately from the
BOUND_D selector, and continuation d/s carriers expose their qualified
first-core-role selection with every counterexample retained. Stable root
substitution classes are displayed as value neighborhoods without merging
their literal roots. Existing token semantics are read from v0.49, including
the distributed root-content poles and the qualified exact che-to-value
content direction with its H/S/T cross-ecology upgrade plus cross-ecology
roles on exact E-to-q endpoints; none is converted into a lexical gloss.
"""

from __future__ import annotations

import csv
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence

from common import RESULTS, core
from run_internal_utterance_grammar import WordNode, line_nodes
from run_typology_neutral_structure import SOURCES, canonical_units, prose_rows
from run_confirmed_operator_factorial_inventory import collapse_signature, role
from run_detached_suffix_collapsed_order import boundary_candidates, select_edges
from run_selector_q_hard_boundary import TARGET_PAIRS
import voynich_paradigm_decoder as paradigm


BASE = Path(__file__).resolve().parents[2]
LAYOUT = BASE / "transcription/zl3b_layout_aware_reading_units.tsv"
TRANSLATION = RESULTS / "complete_first_translation_v049.tsv"
CLASS_FILE = RESULTS / "root_substitution_classes.tsv"
OUTPUT_TSV = RESULTS / "abstract_line_interpreter_zl.tsv"
OUTPUT_TEXT = RESULTS / "abstract_line_interpreter_zl.txt"
OUTPUT_JSON = RESULTS / "abstract_line_interpreter_results.json"
OUTPUT_REPORT = RESULTS / "abstract_line_interpreter_report.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def root_classes() -> dict[str, str]:
    output: dict[str, str] = {}
    for row in read_tsv(CLASS_FILE):
        for root in row["roots"].split(","):
            output[root] = row["class"]
    return output


ROOT_CLASS = root_classes()
DEPLETED_BOUNDARIES = {
    ("BARE", "Q_BARE"),
    ("BARE", "Q_BOUND_E"),
    ("BOUND_D", "BARE"),
    ("REL_I", "Q_BARE"),
    ("FREE_A", "BARE"),
}
INITIAL_BARE_CARRIERS = {"d", "s", "t"}
CORE_ROLE_TENDENCY = {
    "BARE": "S",
    "BOUND_D": "D",
    "BOUND_E": "D",
    "FREE_R": "D",
    "REL_I": "S",
}
PRE_ATLAS_BASELINE = {
    "ZL3b": {"lines_with_active_edge": 1477, "active_edges": 2183, "plain_star": 2325},
    "IT2a": {"lines_with_active_edge": 1489, "active_edges": 2193, "plain_star": 2313},
    "RF1b": {"lines_with_active_edge": 1276, "active_edges": 1737, "plain_star": 2529},
}


def layout_index() -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in read_tsv(LAYOUT):
        output[row["locus"]] = {
            "soft": {int(value) for value in row["soft_break_positions"].split(",") if value},
            "high": {int(value) for value in row["high_break_positions"].split(",") if value},
            "restart": {int(value) for value in row["right_restart_positions"].split(",") if value},
        }
    return output


def translation_index() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    line_tags: dict[str, list[str]] = {}
    token_tags: dict[str, list[str]] = defaultdict(list)
    for row in read_tsv(TRANSLATION):
        for line_tag in row["line_semantic_translation"].split(" || "):
            if line_tag and line_tag != "[LEXICAL CONTENT UNTRANSLATED]":
                line_tags.setdefault(row["locus"], []).append(line_tag)
        tag = row["token_semantic_translation"]
        if tag and tag != "[LEXICAL CONTENT UNTRANSLATED]":
            token_tags[row["locus"]].append(tag)
    return line_tags, token_tags


def unit_expression(root: str, role: str) -> str:
    value = f"{ROOT_CLASS[root]}[{root}]" if root in ROOT_CLASS else root
    return f"{value}:{role}"


def word_expression(node: WordNode) -> str:
    return "{" + "+".join(
        unit_expression(root, role) for root, role in zip(node.roots, node.roles)
    ) + "}"


def compress_plain(parts: Sequence[str]) -> list[str]:
    output: list[str] = []
    plain_count = 0
    for part in parts:
        if part == "PLAIN":
            plain_count += 1
            continue
        if plain_count:
            output.append("PLAIN" if plain_count == 1 else "PLAIN*")
            plain_count = 0
        output.append(part)
    if plain_count:
        output.append("PLAIN" if plain_count == 1 else "PLAIN*")
    return output


def edge_component_expression(labels: Sequence[str], nodes: Sequence[WordNode]) -> str:
    words = ",".join(word_expression(node) for node in nodes)
    if len(labels) == 1:
        name = {
            "D_SELECT_Q_EXACT": "D_STATE_TO_EXACT_Q_DEPENDENT",
            "E_SELECT_Q_EXACT": "E_STATE_TO_EXACT_Q_DEPENDENT",
            "DETACHED_SUFFIX_REL_I": "DETACHED_REL_I_COMPLETION",
            "DETACHED_SUFFIX_FREE_L": "DETACHED_FREE_L_COMPLETION",
            "DETACHED_SUFFIX_FREE_R": "DETACHED_FREE_R_COMPLETION",
        }[labels[0]]
        return f"{name}({words})"
    return f"CONSTRUCTION_CHAIN[{' > '.join(labels)}]({words})"


def active_construction_label(
    left: WordNode, right: WordNode, suffix_role: str | None = None,
) -> str:
    if suffix_role:
        return f"DETACHED_SUFFIX_{suffix_role}"
    pair = (left.last_role, right.first_role)
    if pair in TARGET_PAIRS:
        return "D_SELECT_Q_EXACT" if pair[0] == "BOUND_D" else "E_SELECT_Q_EXACT"
    return ""


def initial_carrier(
    surface: str | None, opening: bool, paragraph_context_known: bool,
) -> dict[str, Any]:
    empty = {
        "carrier": "",
        "state": "",
        "actual_context": "",
        "aligned": 0,
        "expression": "",
        "frame": "",
        "first_core_role": "",
        "core_role_tendency": "",
        "core_role_alignment": "",
    }
    if not surface:
        return empty
    units = core.segment(surface)
    if len(units) <= 1:
        return empty
    signature = paradigm.strict_parse(units[0])
    carrier = signature[0]
    if (
        carrier not in INITIAL_BARE_CARRIERS
        or signature != (carrier, False, "NONE", "NONE", "NONE", "NONE")
    ):
        return empty
    actual = (
        "PARAGRAPH_OPEN" if opening else "CONTINUATION_LINE"
    ) if paragraph_context_known else "PARAGRAPH_CONTEXT_UNAVAILABLE"
    if carrier == "t":
        state = "PARAGRAPH_OPENING_ASSOCIATED"
        frame = "T_OPEN_CARRIER"
        aligned = opening if paragraph_context_known else False
    else:
        state = "CONTINUATION_LINE_ENTRY_ASSOCIATED"
        frame = f"{carrier.upper()}_CONT_CARRIER"
        aligned = (not opening) if paragraph_context_known else False
    first_core_role = role(collapse_signature(paradigm.strict_parse(units[1]), q=False))
    role_tendency = ""
    role_alignment = ""
    if carrier in {"d", "s"}:
        if not paragraph_context_known:
            role_tendency = "CONTEXT_UNAVAILABLE"
            role_alignment = "CONTEXT_UNAVAILABLE"
        elif opening:
            role_tendency = "OUT_OF_SCOPE_PARAGRAPH_OPEN"
            role_alignment = "OUT_OF_SCOPE"
        else:
            role_tendency = CORE_ROLE_TENDENCY.get(first_core_role, "UNMAPPED")
            role_alignment = (
                "UNMAPPED" if role_tendency == "UNMAPPED" else
                "ALIGNED" if carrier.upper() == role_tendency else
                "COUNTEREXAMPLE"
            )
    hierarchy = (
        f";FIRST_CORE_ROLE={first_core_role};ROLE_TENDENCY={role_tendency};"
        f"ROLE_ALIGNMENT={role_alignment}"
        if carrier in {"d", "s"} else ""
    )
    return {
        "carrier": carrier,
        "state": state,
        "actual_context": actual,
        "aligned": int(aligned),
        "expression": (
            f"INITIAL_BARE_{carrier.upper()}_CARRIER[STATE={state};"
            f"ACTUAL={actual}{hierarchy};LEX=?]"
        ),
        "frame": frame,
        "first_core_role": first_core_role,
        "core_role_tendency": role_tendency,
        "core_role_alignment": role_alignment,
    }


def parse_line(
    row: Any, geometry: dict[str, Any] | None = None,
    paragraph_context_known: bool = True,
) -> dict[str, Any]:
    nodes = line_nodes(row)
    raw_positions = [
        index for index, word in enumerate(row.words, 1) if canonical_units(word)
    ]
    if len(raw_positions) != len(nodes):
        raise RuntimeError(f"node/raw position mismatch at {row.locus}")
    role_pairs = [(left.last_role, right.first_role) for left, right in zip(nodes, nodes[1:])]
    suffix_candidates = boundary_candidates(row.words, "CORE_ISOLATED")
    suffix_edges = select_edges(suffix_candidates, "CORE_ISOLATED")
    labels = []
    for node_index, (left, right) in enumerate(zip(nodes, nodes[1:])):
        raw_left = raw_positions[node_index] - 1
        raw_right = raw_positions[node_index + 1] - 1
        if raw_right != raw_left + 1:
            labels.append("NONE")
            continue
        labels.append(active_construction_label(
            left,
            right,
            suffix_candidates[raw_left] if raw_left in suffix_edges else None,
        ) or "NONE")
    parts: list[str] = []
    frame_parts: list[str] = []
    assigned: list[int] = []
    index = 0
    while index < len(nodes):
        if index < len(labels) and labels[index] != "NONE":
            start = index
            end_gap = index
            while end_gap + 1 < len(labels) and labels[end_gap + 1] != "NONE":
                end_gap += 1
            component_labels = labels[start:end_gap + 1]
            component_nodes = nodes[start:end_gap + 2]
            parts.append(edge_component_expression(component_labels, component_nodes))
            if len(component_labels) == 1:
                frame_parts.append({
                    "D_SELECT_Q_EXACT": "D",
                    "E_SELECT_Q_EXACT": "E",
                    "DETACHED_SUFFIX_REL_I": "SI",
                    "DETACHED_SUFFIX_FREE_L": "SL",
                    "DETACHED_SUFFIX_FREE_R": "SR",
                }[component_labels[0]])
            else:
                frame_parts.append("CHAIN(" + ">".join(label[0] for label in component_labels) + ")")
            assigned.extend(range(start, end_gap + 2))
            index = end_gap + 2
        else:
            parts.append(f"PLAIN({word_expression(nodes[index])})")
            frame_parts.append("PLAIN")
            assigned.append(index)
            index += 1
    if assigned != list(range(len(nodes))):
        raise RuntimeError(f"non-deterministic component assignment at {row.locus}: {assigned}")

    geometry = geometry or {"soft": set(), "high": set(), "restart": set()}
    layout_markers = []
    for position in sorted(geometry["soft"]):
        strength = "HIGH" if position in geometry["high"] else "MEDIUM"
        restart = ";RIGHT_RESTART" if position in geometry["restart"] else ""
        layout_markers.append(f"AFTER_W{position}:{strength}_SOFT_BREAK{restart}")
    opening = bool(row.paragraph_start)
    carrier = initial_carrier(
        row.words[0] if row.words else None,
        opening,
        paragraph_context_known,
    )
    closing = bool(nodes and nodes[-1].last_role in {"FREE_A", "Q_FREE_A"})
    depleted_hits = [
        f"W{index + 1}:{left}>{right}:W{index + 2}"
        for index, (left, right) in enumerate(role_pairs)
        if (left, right) in DEPLETED_BOUNDARIES
    ]
    coarse = compress_plain(frame_parts)
    grammar_frame = "|".join(coarse + (["CLOSE"] if closing else []))
    document_frame = "|".join(
        ([carrier["frame"]] if carrier["frame"] else [])
        + (["OPEN"] if opening else [])
        + [grammar_frame]
    )
    expression = " ; ".join(
        ([carrier["expression"]] if carrier["expression"] else [])
        + (["PARAGRAPH_OPEN"] if opening else [])
        + parts
        + (["FREE_A_CLOSE"] if closing else [])
        + (["LAYOUT{" + ",".join(layout_markers) + "}"] if layout_markers else [])
    )
    return {
        "page": row.page,
        "locus": row.locus,
        "section": row.section,
        "language": row.language,
        "hand": row.hand,
        "surface": " ".join(row.words),
        "word_count": len(nodes),
        "active_edges": sum(label != "NONE" for label in labels),
        "edge_signature": ">".join(label[0] if label != "NONE" else "_" for label in labels),
        "active_constructions": ";".join(label for label in labels if label != "NONE"),
        "depleted_boundary_hits": len(depleted_hits),
        "depleted_boundary_signature": ";".join(depleted_hits),
        "grammar_frame": grammar_frame,
        "document_frame": document_frame,
        "abstract_expression": expression,
        "initial_bare_carrier": carrier["carrier"],
        "initial_carrier_state": carrier["state"],
        "initial_carrier_actual_context": carrier["actual_context"],
        "initial_carrier_context_aligned": carrier["aligned"],
        "initial_carrier_first_core_role": carrier["first_core_role"],
        "initial_carrier_core_role_tendency": carrier["core_role_tendency"],
        "initial_carrier_core_role_alignment": carrier["core_role_alignment"],
        "paragraph_context_known": int(paragraph_context_known),
        "paragraph_open": int(opening),
        "free_a_close": int(closing),
        "soft_breaks": len(geometry["soft"]),
        "right_restarts": len(geometry["restart"]),
    }


def edition_parses(path: Path) -> dict[str, dict[str, Any]]:
    context_known = path != SOURCES["RF1b"]
    return {
        row.locus: parse_line(row, paragraph_context_known=context_known)
        for row in prose_rows(path)
    }


def agreement(parses: dict[str, dict[str, dict[str, Any]]], field: str) -> dict[str, Any]:
    editions = list(parses)
    common = sorted(set.intersection(*(set(parses[edition]) for edition in editions)))
    pair_rows = {}
    for left_index, left in enumerate(editions):
        for right in editions[left_index + 1:]:
            same = sum(parses[left][locus][field] == parses[right][locus][field] for locus in common)
            pair_rows[f"{left}~{right}"] = {"same": same, "total": len(common), "rate": same / max(len(common), 1)}
    triple = sum(len({parses[edition][locus][field] for edition in editions}) == 1 for locus in common)
    return {
        "common_loci": len(common),
        "all_three_same": triple,
        "all_three_rate": triple / max(len(common), 1),
        "pairs": pair_rows,
    }


def top_frames(parses: dict[str, dict[str, dict[str, Any]]], limit: int = 30) -> list[dict[str, Any]]:
    counts = {
        edition: Counter(row["grammar_frame"] for row in rows.values())
        for edition, rows in parses.items()
    }
    return [
        {"frame": frame, **{edition: counts[edition][frame] for edition in parses}}
        for frame, _count in counts["ZL3b"].most_common(limit)
    ]


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# Deterministic abstract line interpreter",
        "",
        "**ABSTRACT_LINE_INTERPRETER_BUILT**",
        "",
        "Every prose line is rendered as a lossless-order abstract expression over confirmed position-local roles and constructions. Roots remain literal; a substitution-class label is displayed only as a neighborhood wrapper, never as a merge or gloss. L_SERIAL and REL_TO_FREE are excluded after their corrected position-zone failures; the five exact hard D/E->q edges, isolated detached suffixes, qualified bare-d/s/t initial-carrier states, the v0.41 d/s first-core-role hierarchy, v0.45 bathing record/subregister/drawing-context tags, v0.46 root-content poles, the v0.47 qualified exact che-to-value content direction, its v0.48 H/S/T cross-ecology upgrade, and v0.49 cross-ecology content roles on exact E-to-q endpoints are included.",
        "",
        "| edition | lines | lines with active edge | active edges | distinct coarse frames |",
        "|---|---:|---:|---:|---:|",
    ]
    for edition, row in payload["editions"].items():
        lines.append(f"| {edition} | {row['lines']} | {row['lines_with_active_edge']} | {row['active_edges']} | {row['distinct_frames']} |")
    lines += [
        "",
        "Active construction counts: " + "; ".join(
            f"{edition}=" + ",".join(f"{name}:{count}" for name, count in row["construction_counts"].items())
            for edition, row in payload["editions"].items()
        ) + ".",
        "",
        "Initial bare-carrier counts: " + "; ".join(
            f"{edition}=" + ",".join(
                f"{name}:{count}" for name, count in row["initial_carrier_counts"].items()
            )
            for edition, row in payload["editions"].items()
        ) + ". Bare d is distinct from BOUND_D; every carrier lexeme remains unknown.",
        "D/S continuation core-role alignment counts: " + "; ".join(
            f"{edition}=" + ",".join(
                f"{name}:{count}" for name, count in row["initial_core_role_alignment_counts"].items()
            )
            for edition, row in payload["editions"].items()
        ) + ". ALIGNED/COUNTEREXAMPLE/UNMAPPED are probabilistic formal states, not translated words.",
        "",
        "Observed instances of the confirmed depleted BARE->q boundaries are retained as explicit counterexamples in the TSV, not converted into active edges: " + "; ".join(
            f"{edition}:{row['depleted_boundary_hits']}" for edition, row in payload["editions"].items()
        ) + ".",
        "",
        f"All-three exact coarse-frame agreement: {payload['frame_agreement']['all_three_same']}/{payload['frame_agreement']['common_loci']} ({payload['frame_agreement']['all_three_rate']:.1%}). Exact edge-sequence agreement: {payload['edge_agreement']['all_three_same']}/{payload['edge_agreement']['common_loci']} ({payload['edge_agreement']['all_three_rate']:.1%}).",
        "",
        "## Most frequent ZL coarse frames",
        "",
        "| frame | ZL | IT | RF |",
        "|---|---:|---:|---:|",
    ]
    for row in payload["top_frames"][:20]:
        lines.append(f"| `{row['frame']}` | {row['ZL3b']} | {row['IT2a']} | {row['RF1b']} |")
    lines += [
        "",
        "This export organizes what is already known; it does not convert structural roles into European S/V/O labels or English words. Its practical purpose is to choose the next semantic target at the recurring expression-frame level.",
        "",
        f"ZL expression rows: `{OUTPUT_TSV.name}`. Runtime: {payload['elapsed_seconds']:.3f} seconds.",
    ]
    OUTPUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    started = time.perf_counter()
    geometry = layout_index()
    line_tags, token_tags = translation_index()
    parses = {edition: edition_parses(path) for edition, path in SOURCES.items()}

    zl_rows = []
    for row in prose_rows(SOURCES["ZL3b"]):
        parsed = parse_line(row, geometry.get(row.locus))
        semantic_line_values = sorted(set(value for value in line_tags.get(row.locus, []) if value))
        parsed["existing_line_semantics"] = " || ".join(semantic_line_values)
        parsed["existing_token_semantics"] = " || ".join(token_tags.get(row.locus, []))
        zl_rows.append(parsed)
    if len(zl_rows) != len(parses["ZL3b"]):
        raise RuntimeError("ZL parse count mismatch")
    with OUTPUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(zl_rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(zl_rows)
    OUTPUT_TEXT.write_text(
        "\n".join(f"<{row['locus']}> {row['abstract_expression']}" for row in zl_rows) + "\n",
        encoding="utf-8",
    )

    edition_summary = {}
    for edition, rows in parses.items():
        construction_counts = Counter(
            label
            for row in rows.values()
            for label in row["active_constructions"].split(";")
            if label
        )
        edition_summary[edition] = {
            "lines": len(rows),
            "lines_with_active_edge": sum(row["active_edges"] > 0 for row in rows.values()),
            "active_edges": sum(row["active_edges"] for row in rows.values()),
            "distinct_frames": len({row["grammar_frame"] for row in rows.values()}),
            "ambiguous_or_unassigned_lines": 0,
            "construction_counts": dict(construction_counts),
            "depleted_boundary_hits": sum(row["depleted_boundary_hits"] for row in rows.values()),
            "plain_star": sum(row["grammar_frame"] == "PLAIN*" for row in rows.values()),
            "initial_carrier_counts": dict(Counter(
                row["initial_bare_carrier"] for row in rows.values()
                if row["initial_bare_carrier"]
            )),
            "initial_carrier_context_aligned": sum(
                row["initial_carrier_context_aligned"] for row in rows.values()
            ),
            "initial_core_role_alignment_counts": dict(Counter(
                row["initial_carrier_core_role_alignment"] for row in rows.values()
                if row["initial_carrier_core_role_alignment"]
            )),
        }
    payload = {
        "status": "ABSTRACT_LINE_INTERPRETER_BUILT",
        "scope": "deterministic composition of already confirmed structures; no new lexical gloss",
        "translation_source": TRANSLATION.name,
        "active_rules": [
            "BOUND_D>Q_BARE", "BOUND_D>Q_BOUND_D", "BOUND_D>Q_REL_I",
            "BOUND_E>Q_BARE", "BOUND_E>Q_BOUND_E",
            "DETACHED_SUFFIX_REL_I", "DETACHED_SUFFIX_FREE_L", "DETACHED_SUFFIX_FREE_R",
            "INITIAL_BARE_T_PARAGRAPH_OPEN_ASSOC", "INITIAL_BARE_D/S_CONTINUATION_ASSOC",
            "INITIAL_BARE_D/S_FIRST_CORE_ROLE_SELECTION",
        ],
        "excluded_rules": [
            "L_SERIAL (position-zone audit failure)",
            "REL_TO_FREE (fails after detached-suffix correction)",
        ],
        "depleted_constraints": [
            "BARE>Q_BARE", "BARE>Q_BOUND_E", "BOUND_D>BARE",
            "REL_I>Q_BARE", "FREE_A>BARE",
        ],
        "pre_atlas_baseline": PRE_ATLAS_BASELINE,
        "editions": edition_summary,
        "frame_agreement": agreement(parses, "grammar_frame"),
        "edge_agreement": agreement(parses, "edge_signature"),
        "top_frames": top_frames(parses),
        "zl_rows_exported": len(zl_rows),
        "zl_lines_with_existing_token_semantics": sum(bool(row["existing_token_semantics"]) for row in zl_rows),
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_report(payload)
    print(json.dumps({
        "status": payload["status"],
        "editions": edition_summary,
        "frame_agreement": payload["frame_agreement"],
        "edge_agreement": payload["edge_agreement"],
        "top_frames": payload["top_frames"][:12],
        "elapsed_seconds": payload["elapsed_seconds"],
        "output": str(OUTPUT_TSV.resolve()),
    }, indent=2))


if __name__ == "__main__":
    main()
