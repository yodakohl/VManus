#!/usr/bin/env python3
"""Clean-room reconstruction of the source-native construction-path atlas."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
TRANSITIONS = RESULTS / "source_native_transition_atlas.tsv"
TRANSITION_VALIDATION = RESULTS / "source_native_transition_atlas_validation.json"
SPEC = BASE / "SOURCE_NATIVE_CONSTRUCTION_PATH_ATLAS_SPEC.md"
BUILDER = BASE / "build_source_native_construction_path_atlas.py"
TSV = RESULTS / "source_native_construction_path_atlas.tsv"
PRODUCTION = RESULTS / "source_native_construction_path_atlas.json"
PRODUCTION_REPORT = RESULTS / "source_native_construction_path_atlas_report.md"
OUT = RESULTS / "source_native_construction_path_atlas_validation.json"
REPORT = RESULTS / "source_native_construction_path_atlas_validation_report.md"
FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    TRANSITIONS: "f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",
    TRANSITION_VALIDATION: "209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",
    SPEC: "c29b5d6354b30087dfd28f73698a4fea8864008812c712691dc58355c626cfbc",
    BUILDER: "ef326a0f84b5b4b9a24e3a623a53580b71e91b17da3e1c55a74198f47c0adb66",
    TSV: "8e37e2b082fec4f27712ef77b4370b7cc90bcc7f72ab9fa27d99e8b16601f665",
    PRODUCTION: "22a5575582b6a45f6b469ea648dfc1a111c581c32c975c45a6edb89df21995ca",
    PRODUCTION_REPORT: "4afc397de9174f84dca452ce6769a2d3f3b2f0a77eca732b65a2c4204a442b20",
}
FAVORED = frozenset(("DA", "AQ", "QK", "KJ", "PK", "LJ"))
PATHS = ("AQ", "DA", "KJ", "LJ", "PK", "QK", "AQK", "DAQ", "PKJ", "QKJ", "AQKJ", "DAQK", "DAQKJ")
PATH_SET = frozenset(PATHS)
FIELDS = (
    "path", "symbols", "edges", "occurrences", "distinct_groups",
    "distinct_loci", "physical_folios", "currier_A_groups",
    "currier_B_groups", "whole_occurrences", "opening_occurrences",
    "closing_occurrences", "internal_occurrences", "maximal_occurrences",
    "maximal_distinct_groups", "maximal_physical_folios",
    "section_group_counts_json", "support_label",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError("page")
    return match.group(1)


def position(start: int, end: int, length: int) -> str:
    if start == 0 and end == length:
        return "WHOLE"
    if start == 0:
        return "OPENING"
    if end == length:
        return "CLOSING"
    return "INTERNAL"


def rebuild(source_rows, disfavored):
    selected = [row for row in source_rows if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE"]
    if len(source_rows) != 26184 or len(selected) != 21899 or len({row["consensus_group_id"] for row in selected}) != 21899:
        raise ValueError("identity")
    occurrences = {path: [] for path in PATHS}
    maximal = {path: [] for path in PATHS}
    transition_counts = Counter()
    run_lengths = Counter()
    total_symbols = total_transitions = participating = with_favored = with_disfavored = whole = run_count = 0
    for row in selected:
        surface = row["family_surface"]
        if not surface or len(surface) != int(row["symbol_count"]):
            raise ValueError("surface")
        length = len(surface)
        total_symbols += length
        total_transitions += max(0, length - 1)
        flags = []
        covered = set()
        for index in range(length - 1):
            pair = surface[index:index + 2]
            label = "FAVORED" if pair in FAVORED else ("DISFAVORED" if pair in disfavored else "UNRESOLVED")
            transition_counts[label] += 1
            flags.append(label == "FAVORED")
            if label == "FAVORED":
                covered.update((index, index + 1))
        participating += len(covered)
        with_favored += bool(covered)
        with_disfavored += any(surface[index:index + 2] in disfavored for index in range(length - 1))
        whole += length >= 2 and all(flags)
        for start in range(length - 1):
            for end in range(start + 2, min(length, start + 5) + 1):
                path = surface[start:end]
                if path in PATH_SET:
                    occurrences[path].append((row, position(start, end, length)))
        index = 0
        while index < len(flags):
            if not flags[index]:
                index += 1
                continue
            end_edge = index
            while end_edge + 1 < len(flags) and flags[end_edge + 1]:
                end_edge += 1
            end = end_edge + 2
            path = surface[index:end]
            if path not in PATH_SET:
                raise ValueError("maximal path")
            maximal[path].append((row, position(index, end, length)))
            run_lengths[len(path)] += 1
            run_count += 1
            index = end_edge + 1
    output = []
    for path in PATHS:
        values = occurrences[path]
        maxima = maximal[path]
        groups = {row["consensus_group_id"] for row, _ in values}
        loci = {row["locus"] for row, _ in values}
        folios = {folio(row["page"]) for row, _ in values}
        currier = {value: len({row["consensus_group_id"] for row, _ in values if row["currier"] == value}) for value in ("A", "B")}
        section_counts = {value: len({row["consensus_group_id"] for row, _ in values if row["section"] == value}) for value in sorted({row["section"] for row, _ in values})}
        positions = Counter(value for _, value in values)
        support = "WIDESPREAD_BOTH_REGISTERS" if len(loci) >= 20 and len(folios) >= 20 and min(currier.values()) >= 10 else "LIMITED_DESCRIPTIVE_PATH"
        output.append({
            "path": path,
            "symbols": len(path),
            "edges": len(path) - 1,
            "occurrences": len(values),
            "distinct_groups": len(groups),
            "distinct_loci": len(loci),
            "physical_folios": len(folios),
            "currier_A_groups": currier["A"],
            "currier_B_groups": currier["B"],
            "whole_occurrences": positions["WHOLE"],
            "opening_occurrences": positions["OPENING"],
            "closing_occurrences": positions["CLOSING"],
            "internal_occurrences": positions["INTERNAL"],
            "maximal_occurrences": len(maxima),
            "maximal_distinct_groups": len({row["consensus_group_id"] for row, _ in maxima}),
            "maximal_physical_folios": len({folio(row["page"]) for row, _ in maxima}),
            "section_group_counts_json": json.dumps(section_counts, separators=(",", ":"), sort_keys=True),
            "support_label": support,
        })
    summary = {
        "source_groups": len(selected),
        "source_symbols": total_symbols,
        "source_transitions": total_transitions,
        "favored_transition_occurrences": transition_counts["FAVORED"],
        "disfavored_transition_occurrences": transition_counts["DISFAVORED"],
        "unresolved_transition_occurrences": transition_counts["UNRESOLVED"],
        "symbols_participating_in_favored_edge": participating,
        "groups_with_favored_edge": with_favored,
        "groups_with_disfavored_edge": with_disfavored,
        "whole_favored_path_groups": whole,
        "maximal_favored_runs": run_count,
        "maximal_run_symbol_length_counts": {str(key): run_lengths[key] for key in sorted(run_lengths)},
        "widespread_paths": [row["path"] for row in output if row["support_label"] == "WIDESPREAD_BOTH_REGISTERS"],
    }
    return output, summary


def tsv_text(rows) -> str:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue()


def report_text(summary, rows) -> str:
    longest = next(row for row in rows if row["path"] == "DAQKJ")
    return f"""# Source-native construction-path atlas

Status: **PASS_NEUTRAL_13_PATH_CONSTRUCTION_ATLAS**

The fixed six-edge graph yields **13** possible contiguous paths. Across
**{summary['source_groups']:,}** strict confirmed-prose groups, **{summary['favored_transition_occurrences']:,}**
of **{summary['source_transitions']:,}** physical adjacencies are favored, involving
**{summary['symbols_participating_in_favored_edge']:,}** symbol positions in **{summary['groups_with_favored_edge']:,}** groups.
There are **{summary['maximal_favored_runs']:,}** maximal favored runs and
**{summary['whole_favored_path_groups']:,}** complete groups whose every edge follows the graph.

The longest path `DAQKJ` occurs **{longest['occurrences']:,}** times
across **{longest['physical_folios']}** folios; its exclusive positions are
whole/opening/closing/internal = **{longest['whole_occurrences']} /
{longest['opening_occurrences']} / {longest['closing_occurrences']} /
{longest['internal_occurrences']}**. Widespread path labels are purely neutral
coverage descriptions.

This atlas composes an already-confirmed structural dependency. It supplies no
reading direction, wordhood, morpheme, syntax name, sound, language, cipher,
meaning, plaintext, or translation.
"""


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures = []
    checks = 0

    def check(condition, name):
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, f"hash:{path.name}")
    with TRANSITIONS.open(encoding="utf-8", newline="") as handle:
        transitions = list(csv.DictReader(handle, delimiter="\t"))
    favored = frozenset(row["pair_id"] for row in transitions if row["structural_label"] == "FAVORED_ADJACENCY")
    disfavored = frozenset(row["pair_id"] for row in transitions if row["structural_label"] == "DISFAVORED_ADJACENCY")
    check(len(transitions) == 576 and favored == FAVORED and len(disfavored) == 52, "transition-inventory")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    rows, summary = rebuild(source_rows, disfavored)
    check(len(rows) == 13 and {row["path"] for row in rows} == PATH_SET, "path-inventory")
    check(tsv_text(rows) == TSV.read_text(), "tsv-bytes")
    stored = json.loads(PRODUCTION.read_text())
    for key, value in summary.items():
        check(stored[key] == value, f"summary:{key}")
    check(stored["favored_edges"] == sorted(FAVORED) and stored["disfavored_edges"] == 52 and stored["graph_paths"] == 13, "graph")
    check(stored["tsv_sha256"] == sha(TSV), "tsv-binding")
    check(stored["event_loci_stored"] == 0 and stored["member_codes_accessed"] == 0 and stored["english_glosses"] == 0, "claim-ceiling")
    check(PRODUCTION_REPORT.read_text() == report_text(summary, rows), "report-bytes")
    by_path = {row["path"]: row for row in rows}
    check(by_path["DAQKJ"]["occurrences"] == 99 and by_path["DAQKJ"]["opening_occurrences"] == 99 and sum(by_path["DAQKJ"][f"{value}_occurrences"] for value in ("whole", "closing", "internal")) == 0, "long-chain-opening")
    check(by_path["DAQK"]["occurrences"] == 959 and by_path["DAQK"]["opening_occurrences"] == 958, "four-chain-opening")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_CONSTRUCTION_PATH_ATLAS_VALIDATION",
        "status": "PASS_INDEPENDENT_13_PATH_CONSTRUCTION_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "source_groups": 21899,
        "paths": 13,
        "longest_path": "DAQKJ",
        "longest_path_occurrences": 99,
        "longest_path_opening_occurrences": 99,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "english_glosses": 0,
        "claim_ceiling": "Independent reconstruction of a neutral path composition only; no direction, wordhood, morpheme, syntax name, sound, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Construction-path atlas validation

Status: **{result['status']}**

A clean-room implementation reconstructs all **21,899** source groups, the
fixed six favored and 52 disfavored edges, all **13** graph paths, every
aggregate row, exact TSV/report bytes, and bindings in **{checks}** checks.
The longest `DAQKJ` path occurs 99 times on 35 folios and all 99 are group
openings; `DAQK` is opening in 958/959 occurrences.

These are neutral structural paths, not words, sounds, meanings, or a
translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
