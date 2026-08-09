#!/usr/bin/env python3
"""Compose the frozen favored family graph into a neutral path atlas."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
TRANSITIONS = RESULTS / "source_native_transition_atlas.tsv"
TRANSITION_VALIDATION = RESULTS / "source_native_transition_atlas_validation.json"
SPEC = BASE / "SOURCE_NATIVE_CONSTRUCTION_PATH_ATLAS_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_construction_path_atlas.tsv"
OUT_JSON = RESULTS / "source_native_construction_path_atlas.json"
OUT_REPORT = RESULTS / "source_native_construction_path_atlas_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    TRANSITIONS: "f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",
    TRANSITION_VALIDATION: "209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",
    SPEC: "c29b5d6354b30087dfd28f73698a4fea8864008812c712691dc58355c626cfbc",
}
EXPECTED_FAVORED = frozenset(("DA", "AQ", "QK", "KJ", "PK", "LJ"))
POSITIONS = ("WHOLE", "OPENING", "CLOSING", "INTERNAL")
FIELDS = (
    "path",
    "symbols",
    "edges",
    "occurrences",
    "distinct_groups",
    "distinct_loci",
    "physical_folios",
    "currier_A_groups",
    "currier_B_groups",
    "whole_occurrences",
    "opening_occurrences",
    "closing_occurrences",
    "internal_occurrences",
    "maximal_occurrences",
    "maximal_distinct_groups",
    "maximal_physical_folios",
    "section_group_counts_json",
    "support_label",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError("invalid page")
    return match.group(1)


def graph_paths(edges: frozenset[str]) -> tuple[str, ...]:
    successors = defaultdict(list)
    incoming = Counter()
    for pair in sorted(edges):
        successors[pair[0]].append(pair[1])
        incoming[pair[1]] += 1
    output = set()

    def walk(path: str) -> None:
        for successor in successors[path[-1]]:
            extended = path + successor
            output.add(extended)
            walk(extended)

    for node in sorted(successors):
        walk(node)
    return tuple(sorted(output, key=lambda value: (len(value), value)))


def maximal_runs(surface: str, favored: frozenset[str]):
    flags = [surface[index : index + 2] in favored for index in range(len(surface) - 1)]
    index = 0
    while index < len(flags):
        if not flags[index]:
            index += 1
            continue
        end = index
        while end + 1 < len(flags) and flags[end + 1]:
            end += 1
        yield index, end + 2, surface[index : end + 2]
        index = end + 1


def role(start: int, end: int, length: int) -> str:
    if start == 0 and end == length:
        return "WHOLE"
    if start == 0:
        return "OPENING"
    if end == length:
        return "CLOSING"
    return "INTERNAL"


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(TRANSITION_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_576_PAIR_HELD_FOLIO_RECONSTRUCTION":
        raise SystemExit("transition validation")
    with TRANSITIONS.open(encoding="utf-8", newline="") as handle:
        transition_rows = list(csv.DictReader(handle, delimiter="\t"))
    favored = frozenset(row["pair_id"] for row in transition_rows if row["structural_label"] == "FAVORED_ADJACENCY")
    disfavored = frozenset(row["pair_id"] for row in transition_rows if row["structural_label"] == "DISFAVORED_ADJACENCY")
    if len(transition_rows) != 576 or favored != EXPECTED_FAVORED or len(disfavored) != 52 or favored & disfavored:
        raise SystemExit("transition inventory")
    paths = graph_paths(favored)
    if len(paths) != 13:
        raise SystemExit("path inventory")
    path_set = frozenset(paths)
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        all_rows = list(csv.DictReader(handle, delimiter="\t"))
    rows = [row for row in all_rows if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE"]
    if len(all_rows) != 26184 or len(rows) != 21899 or len({row["consensus_group_id"] for row in rows}) != 21899:
        raise SystemExit("source identity")
    occurrences = {path: [] for path in paths}
    maximal = {path: [] for path in paths}
    transition_counts = Counter()
    run_lengths = Counter()
    symbols_covered = 0
    groups_with_favored = 0
    groups_with_disfavored = 0
    whole_path_groups = 0
    maximal_run_count = 0
    total_symbols = 0
    total_transitions = 0
    for row in rows:
        surface = row["family_surface"]
        if len(surface) != int(row["symbol_count"]) or not surface:
            raise SystemExit("surface geometry")
        length = len(surface)
        total_symbols += length
        total_transitions += max(0, length - 1)
        covered = set()
        pair_labels = []
        for index in range(length - 1):
            pair = surface[index : index + 2]
            label = "FAVORED" if pair in favored else ("DISFAVORED" if pair in disfavored else "UNRESOLVED")
            transition_counts[label] += 1
            pair_labels.append(label)
            if label == "FAVORED":
                covered.update((index, index + 1))
        symbols_covered += len(covered)
        groups_with_favored += bool(covered)
        groups_with_disfavored += "DISFAVORED" in pair_labels
        whole_path_groups += length >= 2 and all(label == "FAVORED" for label in pair_labels)
        for start in range(length - 1):
            for end in range(start + 2, min(length, start + 5) + 1):
                path = surface[start:end]
                if path in path_set:
                    occurrences[path].append((row, role(start, end, length)))
        for start, end, path in maximal_runs(surface, favored):
            if path not in path_set:
                raise SystemExit("invalid maximal path")
            maximal[path].append((row, role(start, end, length)))
            maximal_run_count += 1
            run_lengths[len(path)] += 1
    if total_symbols != 89212 or total_transitions != 67313:
        raise SystemExit("source totals")
    output_rows = []
    for path in paths:
        values = occurrences[path]
        maximal_values = maximal[path]
        groups = {row["consensus_group_id"] for row, _ in values}
        loci = {row["locus"] for row, _ in values}
        folios = {physical_folio(row["page"]) for row, _ in values}
        currier_groups = {
            value: len({row["consensus_group_id"] for row, _ in values if row["currier"] == value})
            for value in ("A", "B")
        }
        sections = {
            section: len({row["consensus_group_id"] for row, _ in values if row["section"] == section})
            for section in sorted({row["section"] for row, _ in values})
        }
        positions = Counter(position for _, position in values)
        support = "WIDESPREAD_BOTH_REGISTERS" if len(loci) >= 20 and len(folios) >= 20 and min(currier_groups.values()) >= 10 else "LIMITED_DESCRIPTIVE_PATH"
        output_rows.append(
            {
                "path": path,
                "symbols": len(path),
                "edges": len(path) - 1,
                "occurrences": len(values),
                "distinct_groups": len(groups),
                "distinct_loci": len(loci),
                "physical_folios": len(folios),
                "currier_A_groups": currier_groups["A"],
                "currier_B_groups": currier_groups["B"],
                "whole_occurrences": positions["WHOLE"],
                "opening_occurrences": positions["OPENING"],
                "closing_occurrences": positions["CLOSING"],
                "internal_occurrences": positions["INTERNAL"],
                "maximal_occurrences": len(maximal_values),
                "maximal_distinct_groups": len({row["consensus_group_id"] for row, _ in maximal_values}),
                "maximal_physical_folios": len({physical_folio(row["page"]) for row, _ in maximal_values}),
                "section_group_counts_json": json.dumps(sections, separators=(",", ":"), sort_keys=True),
                "support_label": support,
            }
        )
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    result = {
        "experiment": "SOURCE_NATIVE_CONSTRUCTION_PATH_ATLAS",
        "status": "PASS_NEUTRAL_13_PATH_CONSTRUCTION_ATLAS",
        "inputs": {path.name: sha(path) for path in (*FROZEN, BUILDER)},
        "source_groups": len(rows),
        "source_symbols": total_symbols,
        "source_transitions": total_transitions,
        "favored_edges": sorted(favored),
        "disfavored_edges": len(disfavored),
        "graph_paths": len(paths),
        "favored_transition_occurrences": transition_counts["FAVORED"],
        "disfavored_transition_occurrences": transition_counts["DISFAVORED"],
        "unresolved_transition_occurrences": transition_counts["UNRESOLVED"],
        "symbols_participating_in_favored_edge": symbols_covered,
        "groups_with_favored_edge": groups_with_favored,
        "groups_with_disfavored_edge": groups_with_disfavored,
        "whole_favored_path_groups": whole_path_groups,
        "maximal_favored_runs": maximal_run_count,
        "maximal_run_symbol_length_counts": {str(key): run_lengths[key] for key in sorted(run_lengths)},
        "widespread_paths": [row["path"] for row in output_rows if row["support_label"] == "WIDESPREAD_BOTH_REGISTERS"],
        "tsv_sha256": sha(OUT_TSV),
        "event_loci_stored": 0,
        "member_codes_accessed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Neutral composition of the already-confirmed source-family adjacency graph only; no direction, wordhood, morpheme, syntax name, sound, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    longest = [row for row in output_rows if len(row["path"]) == max(map(len, paths))][0]
    OUT_REPORT.write_text(
        f"""# Source-native construction-path atlas

Status: **{result['status']}**

The fixed six-edge graph yields **13** possible contiguous paths. Across
**{len(rows):,}** strict confirmed-prose groups, **{transition_counts['FAVORED']:,}**
of **{total_transitions:,}** physical adjacencies are favored, involving
**{symbols_covered:,}** symbol positions in **{groups_with_favored:,}** groups.
There are **{maximal_run_count:,}** maximal favored runs and
**{whole_path_groups:,}** complete groups whose every edge follows the graph.

The longest path `{longest['path']}` occurs **{longest['occurrences']:,}** times
across **{longest['physical_folios']}** folios; its exclusive positions are
whole/opening/closing/internal = **{longest['whole_occurrences']} /
{longest['opening_occurrences']} / {longest['closing_occurrences']} /
{longest['internal_occurrences']}**. Widespread path labels are purely neutral
coverage descriptions.

This atlas composes an already-confirmed structural dependency. It supplies no
reading direction, wordhood, morpheme, syntax name, sound, language, cipher,
meaning, plaintext, or translation.
"""
    )
    print(json.dumps({"status": result["status"], "groups": len(rows), "paths": len(paths), "whole_path_groups": whole_path_groups}, sort_keys=True))


if __name__ == "__main__":
    main()
