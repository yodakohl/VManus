#!/usr/bin/env python3
"""Clean-room SNPL002 preflight validator; imports no production module."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import multiprocessing
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SPEC = BASE / "SNPL002_SOURCE_NATIVE_LOCAL_QUERY_PREFLIGHT_SPEC.md"
CORE = BASE / "snpl002_core.py"
PROD = RESULTS / "snpl002_source_native_local_query_preflight.json"
PROD_MD = RESULTS / "snpl002_source_native_local_query_preflight.md"
OUT = RESULTS / "snpl002_source_native_local_query_preflight_validation.json"
OUT_MD = RESULTS / "snpl002_source_native_local_query_preflight_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
COLUMNS = {"ZL3b": "zl_sta_codes", "IT2a": "it_sta_codes", "RF1b": "rf_sta_codes"}
LABELS = ("f89v2.6", "f102r2.21", "f102r2.22", "f102v1.17")
TARGETS = ("f48v", "f18v", "f23r", "f19r")
STRATA = (("B", "5"), ("A", "1"), ("A", "1"), ("A", "1"))
FAMILIES = {"NULL": 64, "GLOBAL_EDGE_MUTATION": 8, "ONE_LABEL": 8, "WRONG_PAIRING": 8, "ONE_READING": 8, "FAMILY_ONLY": 8}
DATA = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load() -> dict:
    labels = {}
    pages = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    members = defaultdict(set)
    with GROUPS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in LABELS:
                if row["locus"] in labels:
                    raise AssertionError("duplicate label")
                labels[row["locus"]] = {reading: tuple(row[column].split()) for reading, column in COLUMNS.items()}
                continue
            if row["page"] in TARGETS:
                continue
            if row["section"] != "H" or row["grammar_scope"] != "CONFIRMED_PROSE" or row["strict_zero_alternative"] != "1":
                continue
            stratum = (row["currier"], row["hand"])
            for reading, column in COLUMNS.items():
                group = tuple(row[column].split())
                pages[stratum][reading][row["page"]].append(group)
                for code in group:
                    members[code[0]].add(code)
    return {
        "labels": labels,
        "pages": {
            stratum: {
                reading: {page: tuple(groups) for page, groups in by_page.items()}
                for reading, by_page in by_reading.items()
            }
            for stratum, by_reading in pages.items()
        },
        "members": {family: tuple(sorted(values)) for family, values in members.items()},
    }


def motifs(sequence):
    return tuple(sorted({
        sequence[index:index + width]
        for width in (4, 5)
        for index in range(max(0, len(sequence) - width + 1))
    }, key=lambda value: (len(value), value)))


def includes(group, motif):
    return any(group[index:index + len(motif)] == motif for index in range(len(group) - len(motif) + 1))


def raw(groups, query_motifs, weights):
    total = sum(weights)
    if total <= 0:
        raise AssertionError("weight")
    return max((
        sum(weight for motif, weight in zip(query_motifs, weights) if includes(group, motif)) / total
        for group in groups
    ), default=0.0)


def score(query, candidate, references):
    query_windows = motifs(query)
    n = len(references)
    dfs = [sum(any(includes(group, motif) for group in groups) for groups in references.values()) for motif in query_windows]
    weights = [math.log((n + 1) / (df + 1)) for df in dfs]
    observed = raw(candidate, query_windows, weights)
    null = [raw(groups, query_windows, weights) for groups in references.values()]
    rank = (sum(value < observed for value in null) + 0.5 * sum(value == observed for value in null) + 0.5) / (n + 1)
    return rank


def assignment(matrix):
    perms = list(itertools.permutations(range(4)))
    values = [sum(matrix[label][page] for label, page in enumerate(perm)) for perm in perms]
    diagonal = values[0]
    count = sum(value >= diagonal - 1e-15 for value in values)
    wrong = values[1:]
    return {
        "diagonal": diagonal,
        "best_wrong": max(wrong),
        "margin": diagonal - max(wrong),
        "exceed_or_tie": count,
        "p": count / 24,
        "unique_top": count == 1,
        "scores_sha256": hashlib.sha256(b"".join(float(value).hex().encode() + b"\n" for value in values)).hexdigest(),
    }


def select(world):
    def pick(seed, values, count):
        return sorted(values, key=lambda value: hashlib.sha256(f"{seed}|{value}".encode()).digest())[:count]
    b = pick(f"SNPL002|B|{world}", sorted(DATA["pages"][("B", "5")]["ZL3b"]), 1)
    a = pick(f"SNPL002|A|{world}", sorted(DATA["pages"][("A", "1")]["ZL3b"]), 3)
    return tuple(b + a)


def alternate(code):
    options = [value for value in DATA["members"].get(code[0], ()) if value != code]
    return options[0] if options else code


def edge(sequence):
    result = list(sequence)
    for index in list(range(len(result))) + list(range(len(result) - 1, -1, -1)):
        replacement = alternate(result[index])
        if replacement != result[index]:
            result[index] = replacement
            return tuple(result)
    raise AssertionError("edge")


def injected(family, world):
    answer = {reading: {} for reading in READINGS}
    if family == "NULL":
        return answer
    if family == "GLOBAL_EDGE_MUTATION":
        for reading in READINGS:
            for index, locus in enumerate(LABELS):
                answer[reading][index] = edge(DATA["labels"][locus][reading])
    elif family == "ONE_LABEL":
        index = world % 4
        for reading in READINGS:
            answer[reading][index] = edge(DATA["labels"][LABELS[index]][reading])
    elif family == "WRONG_PAIRING":
        for reading in READINGS:
            for index in range(4):
                answer[reading][index] = edge(DATA["labels"][LABELS[(index - 1) % 4]][reading])
    elif family == "ONE_READING":
        reading = READINGS[world % 3]
        for index, locus in enumerate(LABELS):
            answer[reading][index] = edge(DATA["labels"][locus][reading])
    elif family == "FAMILY_ONLY":
        for reading in READINGS:
            for index, locus in enumerate(LABELS):
                answer[reading][index] = tuple(alternate(code) for code in DATA["labels"][locus][reading])
    return answer


def world(task):
    family, index = task
    chosen = select(index)
    insert = injected(family, index)
    matrices = {}
    for reading in READINGS:
        matrix = [[0.0] * 4 for _ in range(4)]
        for page_index, (page, stratum) in enumerate(zip(chosen, STRATA)):
            candidate = DATA["pages"][stratum][reading][page]
            if page_index in insert[reading]:
                candidate = candidate + (insert[reading][page_index],)
            excluded = {name for name, candidate_stratum in zip(chosen, STRATA) if candidate_stratum == stratum}
            references = {name: groups for name, groups in DATA["pages"][stratum][reading].items() if name not in excluded}
            for label_index, locus in enumerate(LABELS):
                matrix[label_index][page_index] = score(DATA["labels"][locus][reading], candidate, references)
        matrices[reading] = matrix
    pooled = [[sum(matrices[reading][i][j] for reading in READINGS) / 3 for j in range(4)] for i in range(4)]
    matrices["POOLED"] = pooled
    assignments = {reading: assignment(matrix) for reading, matrix in matrices.items()}
    gates = {
        "pooled_unique_top": assignments["POOLED"]["unique_top"],
        "every_reading_unique_top": all(assignments[reading]["unique_top"] for reading in READINGS),
        "three_explicit_true_labels_unique_page_best": all(pooled[i][i] > max(pooled[k][i] for k in range(4) if k != i) + 1e-15 for i in (1, 2, 3)),
        "three_explicit_true_midranks_at_least_075": all(pooled[i][i] >= 0.75 for i in (1, 2, 3)),
        "ambiguous_f89_true_midrank_at_least_050": pooled[0][0] >= 0.50,
    }
    return family, index, {
        "family": family,
        "world": index,
        "selected_pages": list(chosen),
        "matrix": matrices,
        "matrix_sha256": hashlib.sha256(b"".join(float(value).hex().encode() + b"\n" for row in pooled for value in row)).hexdigest(),
        "assignments": assignments,
        "gates": gates,
        "passes": all(gates.values()),
    }


def main() -> None:
    global DATA
    if OUT.exists() or OUT_MD.exists():
        raise RuntimeError("validation output exists")
    prod = json.loads(PROD.read_text())
    checks = 0

    def check(condition, label):
        nonlocal checks
        if not condition:
            raise AssertionError(label)
        checks += 1

    check(prod["frozen_files"]["spec_sha256"] == sha(SPEC), "spec hash")
    check(prod["frozen_files"]["core_sha256"] == sha(CORE), "core hash")
    check(prod["frozen_files"]["groups_sha256"] == sha(GROUPS), "group hash")
    check(prod["world_counts"] == FAMILIES, "world counts")
    check(prod["target_pages"] == list(TARGETS), "targets")
    check(prod["target_rows_accessed"] is False and prod["target_scores_computed"] is False, "isolation")
    DATA = load()
    check(set(DATA["labels"]) == set(LABELS), "labels")
    check(len(DATA["pages"][("A", "1")]["ZL3b"]) == 92, "A pages")
    check(len(DATA["pages"][("B", "5")]["ZL3b"]) == 5, "B pages")
    for target in TARGETS:
        check(all(target not in DATA["pages"][stratum][reading] for stratum in DATA["pages"] for reading in READINGS), "target absent")

    tasks = [(family, index) for family, count in FAMILIES.items() for index in range(count)]
    workers = min(32, os.cpu_count() or 1, len(tasks))
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as executor:
        reconstructed = list(executor.map(world, tasks, chunksize=1))
    pass_counts = defaultdict(int)
    for family, index, record in reconstructed:
        stored = prod["records"][family][index]
        check(record == stored, f"world {family} {index}")
        pass_counts[family] += int(record["passes"])
    check(dict(pass_counts) == prod["pass_counts"], "pass counts")
    expected = {"NULL": 0, "GLOBAL_EDGE_MUTATION": 8, "ONE_LABEL": 0, "WRONG_PAIRING": 0, "ONE_READING": 0, "FAMILY_ONLY": 0}
    check(prod["pass_counts"] == expected, "expected decisions")
    check(prod["decision"] == "GO_FREEZE_SNPL002_TARGET", "decision")
    check(prod["gates"]["target_scores_computed"] is False, "no target score")
    check(prod["gates"]["ocr_or_automated_vision_used"] is False, "no vision")
    check("No target Herbal row" in PROD_MD.read_text(), "report isolation")
    check("no plant name" in prod["claim_ceiling"], "claim ceiling")

    validation = {
        "status": "PASS_CLEAN_ROOM_104_WORLD_SNPL002_PREFLIGHT_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "workers": workers,
        "worlds_reconstructed": len(tasks),
        "pass_counts": dict(pass_counts),
        "production_sha256": sha(PROD),
        "production_report_sha256": sha(PROD_MD),
        "validator_sha256_before_output": sha(Path(__file__)),
        "target_rows_accessed": False,
        "target_scores_computed": False,
        "decision": prod["decision"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# SNPL002 independent validation\n\n"
        f"PASS: **{checks}** checks reconstruct all **{len(tasks)}** worlds with "
        "NULL 0/64, GLOBAL_EDGE_MUTATION 8/8, and zero passes in all four "
        "adversarial families. Frozen hashes, selections, 4x4 matrices, 24-way "
        "assignments, gates, target isolation, and the claim ceiling agree.\n\n"
        "This validates only the target-blind scorer preflight. It supplies no "
        "plant name, word meaning, sound, language, cipher, plaintext, or translation.\n"
    )


if __name__ == "__main__":
    main()
