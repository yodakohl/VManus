#!/usr/bin/env python3
"""Extract exact, tied minimum-cost RTA001 edge programs on the CPU."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
INVENTORY = RESULTS / "rta001_relation_graph_inventory.tsv"
ALIGNMENT = RESULTS / "source_sta_group_alignment.tsv"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
SEPARATOR = RESULTS / "source_separator_transcription.tsv"
DSL = HERE / "RTA001_OPERATOR_DSL.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
REPRESENTATIONS = ("surface", "family", "member", "root", "construction")

BASE_FIELDS = [
    "edge_id",
    "panel_id",
    "physical_folio",
    "page",
    "relation_type",
    "relation_instance",
    "source_node",
    "target_node",
    "source_locus",
    "target_locus",
    "edition",
    "representation",
    "status",
    "source_length",
    "target_length",
    "source_sequence_json",
    "target_sequence_json",
    "minimum_edit_cost",
    "optimal_alignment_count",
    "canonical_primitive_program_json",
    "canonical_dsl_program_json",
    "canonical_dsl_text",
    "abstract_atom_counts_json",
    "description_length_bits",
]

OP_PRIORITY = {"KEEP": 0, "SUBSTITUTE": 1, "DELETE": 2, "INSERT": 3}
EDIT_COST = {"KEEP": 0, "DELETE": 2, "INSERT": 2, "SUBSTITUTE": 3}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def jdump(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def edge_id(row: dict[str, str]) -> str:
    raw = "|".join((row["panel_id"], row["relation_instance"], row["source_locus"], row["target_locus"]))
    return "RTAE" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()


def intersperse(words: Iterable[list[str]]) -> list[str]:
    out: list[str] = []
    for index, word in enumerate(words):
        if index:
            out.append("WB")
        out.extend(word)
    return out


def split_plus_words(value: str) -> list[str]:
    if not value:
        return []
    return intersperse([[token for token in word.split("+") if token] for word in value.split()])


def build_sequences() -> dict[tuple[str, str, str], list[str]]:
    out: dict[tuple[str, str, str], list[str]] = {}
    interlinear = read_tsv(INTERLINEAR)
    for row in interlinear:
        edition, locus = row["edition"], row["locus"]
        surface_words = [[char for char in word] for word in row["surface"].split()]
        out[(edition, locus, "surface")] = intersperse(surface_words)
        out[(edition, locus, "root")] = split_plus_words(row["root_sequence"])
        roles = split_plus_words(row["role_sequence"])
        out[(edition, locus, "construction")] = roles

    alignment: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in read_tsv(ALIGNMENT):
        alignment[(row["edition"], row["locus"])].append(row)
    separators: dict[tuple[str, str, int], tuple[str, str]] = {}
    for row in read_tsv(SEPARATOR):
        separators[(row["edition"], row["locus"], int(row["source_group_index"]))] = (
            row["left_separator"],
            row["right_separator"],
        )
    for (edition, locus), rows in alignment.items():
        rows.sort(key=lambda x: int(x["source_group_index"]))
        family_words: list[list[str]] = []
        member_words: list[list[str]] = []
        construction = list(out.get((edition, locus, "construction"), []))
        for row in rows:
            family_words.append(list(row["primary_sta_families"]))
            member_words.append(row["primary_sta_codes"].split())
        out[(edition, locus, "family")] = intersperse(family_words)
        out[(edition, locus, "member")] = intersperse(member_words)
        if rows:
            first = separators[(edition, locus, 1)][0]
            last = separators[(edition, locus, len(rows))][1]
            out[(edition, locus, "construction")] = [f"LB:{first}"] + construction + [f"RB:{last}"]
    return out


def exact_alignment(source: list[str], target: list[str]) -> tuple[int, int, list[dict[str, object]]]:
    n, m = len(source), len(target)
    cost = [[0] * (m + 1) for _ in range(n + 1)]
    ties = [[0] * (m + 1) for _ in range(n + 1)]
    back: list[list[tuple[str, int, int] | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    ties[0][0] = 1
    for i in range(1, n + 1):
        cost[i][0] = i * EDIT_COST["DELETE"]
        ties[i][0] = 1
        back[i][0] = ("DELETE", i - 1, 0)
    for j in range(1, m + 1):
        cost[0][j] = j * EDIT_COST["INSERT"]
        ties[0][j] = 1
        back[0][j] = ("INSERT", 0, j - 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            candidates: list[tuple[int, str, int, int]] = []
            if source[i - 1] == target[j - 1]:
                candidates.append((cost[i - 1][j - 1], "KEEP", i - 1, j - 1))
            else:
                candidates.append((cost[i - 1][j - 1] + EDIT_COST["SUBSTITUTE"], "SUBSTITUTE", i - 1, j - 1))
            candidates.append((cost[i - 1][j] + EDIT_COST["DELETE"], "DELETE", i - 1, j))
            candidates.append((cost[i][j - 1] + EDIT_COST["INSERT"], "INSERT", i, j - 1))
            best = min(x[0] for x in candidates)
            optimal = [x for x in candidates if x[0] == best]
            cost[i][j] = best
            ties[i][j] = sum(ties[pi][pj] for _, _, pi, pj in optimal)
            chosen = min(optimal, key=lambda x: (OP_PRIORITY[x[1]], x[2], x[3]))
            back[i][j] = (chosen[1], chosen[2], chosen[3])
    i, j = n, m
    reversed_ops: list[dict[str, object]] = []
    while i or j:
        step = back[i][j]
        if step is None:
            raise AssertionError("missing DP predecessor")
        op, pi, pj = step
        item: dict[str, object] = {"op": op, "source_index": None, "target_index": None}
        if op in {"KEEP", "SUBSTITUTE", "DELETE"}:
            item["source_index"] = i
            item["source"] = source[i - 1]
        if op in {"KEEP", "SUBSTITUTE", "INSERT"}:
            item["target_index"] = j
            item["target"] = target[j - 1]
        reversed_ops.append(item)
        i, j = pi, pj
    return cost[n][m], ties[n][m], list(reversed(reversed_ops))


def summarize_run(ops: list[dict[str, object]]) -> tuple[list[str], list[str]]:
    consumed = [str(x["source"]) for x in ops if x["op"] in {"KEEP", "SUBSTITUTE", "DELETE"}]
    emitted = [str(x["target"]) for x in ops if x["op"] in {"KEEP", "SUBSTITUTE", "INSERT"}]
    return consumed, emitted


def macro(op: str, source: list[str] | None = None, target: list[str] | None = None, **extra: object) -> dict[str, object]:
    item: dict[str, object] = {"op": op}
    if source is not None:
        item["source"] = source
    if target is not None:
        item["target"] = target
    item.update(extra)
    return item


def canonical_dsl(source: list[str], target: list[str], primitive: list[dict[str, object]], representation: str) -> list[dict[str, object]]:
    if 2 <= len(source) <= 4 and len(source) == len(target) and source != target and sorted(source) == sorted(target):
        used = [False] * len(source)
        permutation = []
        for token in target:
            index = next(i for i, value in enumerate(source) if value == token and not used[i])
            used[index] = True
            permutation.append(index + 1)
        return [macro("REORDER_LOCAL_COMPONENTS", source, target, permutation=permutation)]

    keep_indices = [i for i, item in enumerate(primitive) if item["op"] == "KEEP"]
    first_keep = keep_indices[0] if keep_indices else len(primitive)
    last_keep = keep_indices[-1] if keep_indices else -1
    result: list[dict[str, object]] = []

    def replace_run(run: list[dict[str, object]], zone: str) -> list[dict[str, object]]:
        if not run:
            return []
        consumed, emitted = summarize_run(run)
        if zone in {"PREFIX", "SUFFIX"}:
            suffix = "PREFIX" if zone == "PREFIX" else "SUFFIX"
            if consumed and emitted:
                return [macro(f"REPLACE_{suffix}", consumed, emitted)]
            if consumed:
                return [macro(f"DROP_{suffix}", consumed, [])]
            return [macro(f"ADD_{suffix}", [], emitted)]
        out: list[dict[str, object]] = []
        for item in run:
            op = str(item["op"])
            src = [str(item["source"])] if "source" in item else []
            dst = [str(item["target"])] if "target" in item else []
            if op == "DELETE" and src == ["WB"]:
                out.append(macro("MERGE_BOUNDARY", src, []))
            elif op == "INSERT" and dst == ["WB"]:
                out.append(macro("SPLIT_BOUNDARY", [], dst))
            elif op == "SUBSTITUTE" and representation == "root":
                out.append(macro("REPLACE_ROOT_CLASS", src, dst))
            else:
                out.append(macro(op, src, dst))
        return out

    if not keep_indices:
        return replace_run(primitive, "PREFIX")
    result.extend(replace_run(primitive[:first_keep], "PREFIX"))
    cursor = first_keep
    while cursor <= last_keep:
        if primitive[cursor]["op"] == "KEEP":
            end = cursor
            kept: list[str] = []
            while end <= last_keep and primitive[end]["op"] == "KEEP":
                kept.append(str(primitive[end]["source"]))
                end += 1
            result.append(macro("KEEP_CORE", kept, kept))
            cursor = end
        else:
            end = cursor
            while end <= last_keep and primitive[end]["op"] != "KEEP":
                end += 1
            result.extend(replace_run(primitive[cursor:end], "CORE"))
            cursor = end
    result.extend(replace_run(primitive[last_keep + 1 :], "SUFFIX"))
    return result


def zone_for(index: int, count: int) -> str:
    if count <= 1:
        return "CORE"
    if index == 0:
        return "PREFIX"
    if index == count - 1:
        return "SUFFIX"
    return "CORE"


def atom_counts(program: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for index, item in enumerate(program):
        op = str(item["op"])
        zone = "BOUNDARY" if "BOUNDARY" in op else zone_for(index, len(program))
        target = [str(x) for x in item.get("target", [])]
        argument_class = "NONE" if not target else "ANY_LITERAL"
        counts[f"{op}|{zone}|{argument_class}"] += 1
    return dict(sorted(counts.items()))


def universal(n: int) -> int:
    if n < 0:
        raise ValueError(n)
    return 2 * int(math.floor(math.log2(n + 1))) + 1


def description_bits(program: list[dict[str, object]], vocabulary_size: int) -> int:
    literal = int(math.ceil(math.log2(vocabulary_size + 1)))
    total = 0
    for item in program:
        op = str(item["op"])
        source = item.get("source", [])
        target = item.get("target", [])
        total += 4
        if op in {"KEEP"}:
            continue
        if op in {"DELETE", "DROP_PREFIX", "DROP_SUFFIX", "DROP_CARRIER", "MERGE_BOUNDARY", "KEEP_CORE"}:
            total += universal(len(source))
        elif op in {"INSERT", "ADD_PREFIX", "ADD_SUFFIX", "ADD_CARRIER", "SPLIT_BOUNDARY"}:
            total += universal(len(target)) + len(target) * literal
        elif op in {"SUBSTITUTE", "REPLACE_ROOT_CLASS"}:
            total += universal(len(source)) + len(target) * literal
        elif op in {"REPLACE_PREFIX", "REPLACE_SUFFIX"}:
            total += universal(len(source)) + universal(len(target)) + len(target) * literal
        elif op == "REORDER_LOCAL_COMPONENTS":
            n = len(source)
            total += universal(n) + int(math.ceil(math.log2(math.factorial(n))))
        else:
            raise ValueError(f"unknown DSL operation {op}")
    return total


def dsl_text(program: list[dict[str, object]]) -> str:
    parts = []
    for item in program:
        args = []
        if "source" in item and item["source"]:
            args.append("src=" + ",".join(map(str, item["source"])))
        if "target" in item and item["target"]:
            args.append("dst=" + ",".join(map(str, item["target"])))
        if "permutation" in item:
            args.append("perm=" + ",".join(map(str, item["permutation"])))
        parts.append(str(item["op"]) + ("(" + ";".join(args) + ")" if args else ""))
    return " -> ".join(parts)


def generate() -> tuple[dict[str, list[dict[str, str]]], dict[str, object]]:
    inventory = read_tsv(INVENTORY)
    sequences = build_sequences()
    vocabulary: dict[str, set[str]] = {rep: set() for rep in REPRESENTATIONS}
    for (_, _, rep), sequence in sequences.items():
        vocabulary[rep].update(sequence)
    outputs: dict[str, list[dict[str, str]]] = {rep: [] for rep in REPRESENTATIONS}
    missing = defaultdict(int)
    for edge_row in inventory:
        eid = edge_id(edge_row)
        for representation in REPRESENTATIONS:
            vocab_size = len(vocabulary[representation])
            for edition in READINGS:
                source = sequences.get((edition, edge_row["source_locus"], representation))
                target = sequences.get((edition, edge_row["target_locus"], representation))
                common = {
                    "edge_id": eid,
                    "panel_id": edge_row["panel_id"],
                    "physical_folio": edge_row["physical_folio"],
                    "page": edge_row["page"],
                    "relation_type": edge_row["relation_type"],
                    "relation_instance": edge_row["relation_instance"],
                    "source_node": edge_row["source_node"],
                    "target_node": edge_row["target_node"],
                    "source_locus": edge_row["source_locus"],
                    "target_locus": edge_row["target_locus"],
                    "edition": edition,
                    "representation": representation,
                }
                if source is None or target is None:
                    missing[(representation, edition)] += 1
                    payload = {
                        **common,
                        "status": "MISSING_SOURCE_READING",
                        "source_length": "NA" if source is None else str(len(source)),
                        "target_length": "NA" if target is None else str(len(target)),
                        "source_sequence_json": "NA" if source is None else jdump(source),
                        "target_sequence_json": "NA" if target is None else jdump(target),
                        "minimum_edit_cost": "NA",
                        "optimal_alignment_count": "NA",
                        "canonical_primitive_program_json": "NA",
                        "canonical_dsl_program_json": "NA",
                        "canonical_dsl_text": "NA",
                        "abstract_atom_counts_json": "NA",
                        "description_length_bits": "NA",
                    }
                else:
                    cost, tie_count, primitive = exact_alignment(source, target)
                    program = canonical_dsl(source, target, primitive, representation)
                    payload = {
                        **common,
                        "status": "EXACT_PROGRAM",
                        "source_length": str(len(source)),
                        "target_length": str(len(target)),
                        "source_sequence_json": jdump(source),
                        "target_sequence_json": jdump(target),
                        "minimum_edit_cost": str(cost),
                        "optimal_alignment_count": str(tie_count),
                        "canonical_primitive_program_json": jdump(primitive),
                        "canonical_dsl_program_json": jdump(program),
                        "canonical_dsl_text": dsl_text(program),
                        "abstract_atom_counts_json": jdump(atom_counts(program)),
                        "description_length_bits": str(description_bits(program, vocab_size)),
                    }
                if list(payload) != BASE_FIELDS:
                    raise AssertionError((list(payload), BASE_FIELDS))
                outputs[representation].append(payload)
    for rows in outputs.values():
        rows.sort(key=lambda x: (x["edge_id"], READINGS.index(x["edition"])))
    meta = {
        "experiment": "RTA001_GRAPH_TO_TEXT_OPERATOR_INDUCTION",
        "schema_version": "RTA001_EXACT_EDGE_PROGRAMS_V1",
        "status": "EXACT_CPU_PROGRAMS_BUILT",
        "inputs": {
            "inventory_sha256": sha256(INVENTORY),
            "source_sta_group_alignment_sha256": sha256(ALIGNMENT),
            "pre_grounding_interlinear_sha256": sha256(INTERLINEAR),
            "source_separator_transcription_sha256": sha256(SEPARATOR),
            "operator_dsl_sha256": sha256(DSL),
        },
        "counts": {
            "edges": len(inventory),
            "rows_per_representation": len(inventory) * len(READINGS),
            "exact_programs_by_representation": {
                rep: sum(row["status"] == "EXACT_PROGRAM" for row in rows) for rep, rows in outputs.items()
            },
            "missing_by_representation_and_reading": {
                f"{rep}|{edition}": missing[(rep, edition)]
                for rep in REPRESENTATIONS
                for edition in READINGS
                if missing[(rep, edition)]
            },
            "vocabulary_sizes": {rep: len(vocabulary[rep]) for rep in REPRESENTATIONS},
        },
        "tie_policy": "All optimal alignment counts retained; canonical rendering uses KEEP<SUBSTITUTE<DELETE<INSERT.",
        "claim_ceiling": "These are formal edit programs only; no meaning, sound, language, cipher, plaintext, or translation is assigned.",
    }
    return outputs, meta


def render(rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=BASE_FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, meta = generate()
    hashes = {}
    for representation, rows in outputs.items():
        path = RESULTS / f"rta001_edge_programs_{representation}.tsv"
        content = render(rows)
        if args.check:
            if path.read_bytes() != content:
                raise SystemExit(f"edge program mismatch: {path}")
        else:
            path.write_bytes(content)
        hashes[path.name] = hashlib.sha256(content).hexdigest()
    meta["artifacts"] = hashes
    path = RESULTS / "rta001_edge_programs.json"
    content = (json.dumps(meta, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.check:
        if path.read_bytes() != content:
            raise SystemExit(f"edge program metadata mismatch: {path}")
    else:
        path.write_bytes(content)
    print(json.dumps(meta["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
