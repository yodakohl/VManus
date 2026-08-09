#!/usr/bin/env python3
"""Clean-room reconstruction of the cho/che scope synthetic preflight v2."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import multiprocessing as mp
from collections import defaultdict
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
MASKED = RESULTS / "cho_che_scope_masked_events.tsv"
MASKED_VALIDATION = RESULTS / "cho_che_scope_masked_universe_validation.json"
V1_SPEC = BASE / "CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_SPEC.md"
V1_RESULT = RESULTS / "cho_che_scope_synthetic_preflight.json"
V1_AUDIT = RESULTS / "cho_che_scope_rotation_v1_audit.json"
AMENDMENT = BASE / "CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_V2_AMENDMENT.md"
CORE = BASE / "cho_che_scope_core.py"
RUNNER = BASE / "run_cho_che_scope_synthetic_preflight.py"
PRODUCTION = RESULTS / "cho_che_scope_synthetic_preflight_v2.json"
PRODUCTION_REPORT = RESULTS / "cho_che_scope_synthetic_preflight_v2_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "cho_che_scope_synthetic_preflight_v2_validation.json"
REPORT = RESULTS / "cho_che_scope_synthetic_preflight_v2_validation_report.md"
TARGET_SOURCE = RESULTS / "source_sta_group_alignment.tsv"
TARGET_OUT = RESULTS / "cho_che_scope_target.json"
TARGET_REPORT = RESULTS / "cho_che_scope_target_report.md"

HASHES = {
    MASKED: "41f8b517419d2215a97db9ce245c5639f383b11c41d8c1377a245dea8e37abf3",
    MASKED_VALIDATION: "e7d37a23ca199e421946fab0c42f4547aade0a5fa27579b1e9e69518c0d376ec",
    V1_SPEC: "b2b51a91b999ae926170a76ce8ffe8f5b8a7d01f3e71200e93b26cefce900c94",
    V1_RESULT: "203ab1e60c83f43f6cb095b095c461cf7742ba30fecf6ff0cc2b79925c82331e",
    V1_AUDIT: "0b0c2c864ff5b375c0eb2530f344dd19b63a5eab69bdcac27335c8ae19ae4255",
    AMENDMENT: "36c4bd9817a9583bc786b50a952b65b3d15caacd7077ccaca481ad28cf96ffc0",
    CORE: "b77dd67d49c4e173d16bce2409c8f691e9cf7aae30b1333ee0eeffd9a98193b8",
    RUNNER: "107ddc38e1df740dcd59f4c4a04beb096c099f317b88a0ebb9eb5b0bd595fcad",
    PRODUCTION: "3748e03fb9217e7c7d389b887611407fc323a8b5526e7a369ac94f90aae5062e",
    PRODUCTION_REPORT: "284e8ed1a1e27612459a932dcd2ba982fe0f1c953b033b78036a4361e3ff1e0e",
}
READINGS = ("ZL3b", "IT2a", "RF1b")
FIELDS = (
    "event_id", "edition", "source_group_id", "physical_event_key", "locus",
    "source_group_index", "source_group_count", "collapsed_page", "panel_page",
    "physical_folio", "section", "currier", "paragraph_id", "paragraph_number",
    "line_index_side", "line_count_side", "line_fraction", "line_quartile",
    "group_index_line", "group_count_line", "group_fraction", "masked_template",
    "primary_query", "common_primary_query",
)
ASSIGNMENTS = 511
PANELS = None
CHECKS = 0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def u64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "little")


def mix(values: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore"):
        z = values.astype(np.uint64, copy=True) + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        return z ^ (z >> np.uint64(31))


def group_indices(values: list[str]):
    grouped = defaultdict(list)
    for i, value in enumerate(values):
        grouped[value].append(i)
    keys = sorted(grouped)
    return [np.asarray(grouped[key], dtype=np.int64) for key in keys], keys


def build_panels() -> dict:
    with MASKED.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise AssertionError("masked schema")
        all_rows = list(reader)
    if len(all_rows) != 30160:
        raise AssertionError("masked total")
    output = {}
    for edition in READINGS:
        rows = sorted((row for row in all_rows if row["edition"] == edition), key=lambda row: row["event_id"])
        if len({row["event_id"] for row in rows}) != len(rows):
            raise AssertionError("event IDs")
        strata = defaultdict(list)
        for i, row in enumerate(rows):
            strata[row["collapsed_page"], row["masked_template"], int(row["line_quartile"])].append(i)
        rotations = []
        for key in sorted(strata):
            indices = sorted(strata[key], key=lambda i: (int(rows[i]["line_index_side"]), int(rows[i]["group_index_line"]), rows[i]["event_id"]))
            rotations.append((np.asarray(indices, dtype=np.int64), key[0], "|".join(map(str, key))))

        query_indices = [i for i, row in enumerate(rows) if row["primary_query"] == "1"]
        same_support = []
        other_support = []
        query_paragraph = []
        query_page = []
        for qi in query_indices:
            query = rows[qi]
            candidates = strata[query["collapsed_page"], query["masked_template"], int(query["line_quartile"])]
            same = [i for i in candidates if i != qi and rows[i]["paragraph_id"] == query["paragraph_id"]]
            other = [i for i in candidates if rows[i]["paragraph_id"] != query["paragraph_id"]]
            if not same or not other:
                raise AssertionError("query support")
            same_support.append(np.asarray(same, dtype=np.int64))
            other_support.append(np.asarray(other, dtype=np.int64))
            query_paragraph.append(query["paragraph_id"])
            query_page.append(query["collapsed_page"])
        q_to_para, para_keys = group_indices(query_paragraph)
        para_pages = [query_page[group[0]] for group in q_to_para]
        para_to_page, page_keys = group_indices(para_pages)
        page_folios = [next(row["physical_folio"] for row in rows if row["collapsed_page"] == page) for page in page_keys]
        page_to_folio, local_folios = group_indices(page_folios)

        by_page_template = defaultdict(list)
        for i, row in enumerate(rows):
            by_page_template[row["collapsed_page"], row["masked_template"]].append(i)
        counts = defaultdict(lambda: [0, 0])
        candidates = []
        for (page, template), indices in sorted(by_page_template.items()):
            for offset, left in enumerate(indices):
                for right in indices[offset + 1:]:
                    distance = abs(int(rows[left]["line_index_side"]) - int(rows[right]["line_index_side"]))
                    if not 1 <= distance <= 12:
                        continue
                    key = (page, template, distance, 0)
                    same = rows[left]["paragraph_id"] == rows[right]["paragraph_id"]
                    counts[key][0 if same else 1] += 1
                    candidates.append((left, right, same, key, rows[left]["physical_folio"]))
        eligible = {key for key, value in counts.items() if value[0] and value[1]}
        pairs = sorted((pair for pair in candidates if pair[3] in eligible), key=lambda pair: (pair[3], pair[0], pair[1]))
        pair_left = np.asarray([pair[0] for pair in pairs], dtype=np.int64)
        pair_right = np.asarray([pair[1] for pair in pairs], dtype=np.int64)
        pair_same = np.asarray([pair[2] for pair in pairs], dtype=bool)
        pair_to_stratum, stratum_keys = group_indices(["|".join(map(str, pair[3])) for pair in pairs])
        stratum_pages = [key.split("|", 1)[0] for key in stratum_keys]
        stratum_to_page, pair_page_keys = group_indices(stratum_pages)
        pair_page_folios = [next(pair[4] for pair in pairs if pair[3][0] == page) for page in pair_page_keys]
        pair_page_to_folio, boundary_folios = group_indices(pair_page_folios)
        output[edition] = {
            "rows": rows, "rotations": rotations, "query_indices": query_indices,
            "same": same_support, "other": other_support,
            "q_to_para": q_to_para, "para_to_page": para_to_page,
            "page_to_folio": page_to_folio, "local_folios": local_folios,
            "pair_left": pair_left, "pair_right": pair_right, "pair_same": pair_same,
            "pair_to_stratum": pair_to_stratum, "stratum_to_page": stratum_to_page,
            "pair_page_to_folio": pair_page_to_folio, "boundary_folios": boundary_folios,
        }
    return output


def mean_groups(values, groups):
    return np.stack([values[:, group].mean(axis=1) for group in groups], axis=1)


def score(panel, labels):
    y = labels.astype(np.float64, copy=False)
    gains = np.empty((len(y), len(panel["query_indices"])), dtype=np.float64)
    for column, (qi, same, other) in enumerate(zip(panel["query_indices"], panel["same"], panel["other"])):
        ps = (y[:, same].sum(1) + 0.5) / (len(same) + 1.0)
        po = (y[:, other].sum(1) + 0.5) / (len(other) + 1.0)
        target = y[:, qi]
        gains[:, column] = target * np.log(ps / po) + (1.0 - target) * np.log((1.0 - ps) / (1.0 - po))
    local_folio = mean_groups(mean_groups(mean_groups(gains, panel["q_to_para"]), panel["para_to_page"]), panel["page_to_folio"])
    match = (labels[:, panel["pair_left"]] == labels[:, panel["pair_right"]]).astype(np.float64)
    contrasts = np.empty((len(y), len(panel["pair_to_stratum"])), dtype=np.float64)
    for column, group in enumerate(panel["pair_to_stratum"]):
        same = group[panel["pair_same"][group]]
        other = group[~panel["pair_same"][group]]
        contrasts[:, column] = match[:, same].mean(1) - match[:, other].mean(1)
    boundary_folio = mean_groups(mean_groups(contrasts, panel["stratum_to_page"]), panel["pair_page_to_folio"])
    return {"local_T": local_folio.mean(1), "local_folio": local_folio, "boundary_T": boundary_folio.mean(1), "boundary_folio": boundary_folio}


def rotations(panel, labels, assignment_ids, ensemble, seed):
    out = np.empty((len(assignment_ids), len(labels)), dtype=np.uint8)
    common = mix(assignment_ids.astype(np.uint64) ^ np.uint64(u64(seed)))
    for positions, page, stratum in panel["rotations"]:
        key = page if ensemble == "COUPLED_PAGE" else stratum
        shifts = mix(common ^ np.uint64(u64(key))) % np.uint64(len(positions))
        source = (np.arange(len(positions), dtype=np.uint64)[None, :] + np.uint64(len(positions)) - shifts[:, None]) % np.uint64(len(positions))
        out[:, positions] = labels[positions[source.astype(np.int64)]]
    return out


def summary(panel, labels, assignment_count, seed):
    observed = score(panel, labels[None, :])
    null = {ensemble: {"local": [], "boundary": []} for ensemble in ("INDEPENDENT_STRATUM", "COUPLED_PAGE")}
    for ensemble in null:
        for start in range(1, assignment_count + 1, 256):
            ids = np.arange(start, min(assignment_count + 1, start + 256), dtype=np.uint64)
            values = score(panel, rotations(panel, labels, ids, ensemble, seed))
            null[ensemble]["local"].append(values["local_T"])
            null[ensemble]["boundary"].append(values["boundary_T"])
        for target in null[ensemble]:
            null[ensemble][target] = np.concatenate(null[ensemble][target])

    def record(target):
        effect = float(observed[f"{target}_T"][0])
        folios = observed[f"{target}_folio"][0]
        deleted = (folios.sum() - folios) / (len(folios) - 1)
        return {
            "effect": effect, "positive_folios": int((folios > 0).sum()), "folios": len(folios),
            "max_abs_contribution_fraction": float(np.abs(folios).max() / np.abs(folios).sum()) if np.abs(folios).sum() else 1.0,
            "minimum_leave_one_folio_out": float(deleted.min()),
            "p_by_ensemble": {ensemble: float((1 + np.count_nonzero(null[ensemble][target] >= effect)) / (assignment_count + 1)) for ensemble in null},
        }
    return {"local": record("local"), "boundary": record("boundary")}


def synthetic(panel, world, family, amplitude, planted_folio=None):
    rows = panel["rows"]
    logits = np.empty(len(rows))
    uniforms = np.empty(len(rows))
    paragraph_sign = {}
    for i, row in enumerate(rows):
        base = -1.6 if u64(f"WORLD|{world}|PAGE|{row['collapsed_page']}") & 1 else 0.8
        base += ((u64(f"WORLD|{world}|TEMPLATE|{row['masked_template']}") % 2001) / 2000.0 - 0.5) * 0.8
        base += (float(row["line_fraction"]) - 0.5) * 0.6
        if family in {"PARAGRAPH", "ONE_FOLIO"} and (family != "ONE_FOLIO" or row["physical_folio"] == planted_folio):
            key = (row["collapsed_page"], row["masked_template"], row["paragraph_id"])
            if key not in paragraph_sign:
                paragraph_sign[key] = 1.0 if u64(f"WORLD|{world}|PARAGRAPH|{'|'.join(key)}") & 1 else -1.0
            base += amplitude * paragraph_sign[key]
        logits[i] = base
        uniforms[i] = (u64(f"WORLD|{world}|EVENT|{row['physical_event_key']}") + 0.5) / (1 << 64)
    labels = (uniforms < 1 / (1 + np.exp(-logits))).astype(np.uint8)
    if family == "SEQUENTIAL":
        for positions, page, stratum in panel["rotations"]:
            previous = labels[positions[0]]
            for position in positions[1:]:
                if (u64(f"WORLD|{world}|COPY|{rows[position]['physical_event_key']}") + 0.5) / (1 << 64) < amplitude:
                    labels[position] = previous
                previous = labels[position]
    if family not in {"NULL", "PARAGRAPH", "ONE_FOLIO", "SEQUENTIAL"}:
        raise ValueError("synthetic family")
    return labels


def lpass(s):
    z = s["ZL3b"]["local"]
    return z["effect"] >= .10 and max(z["p_by_ensemble"].values()) <= .05 and z["minimum_leave_one_folio_out"] >= .05 and z["positive_folios"] >= 21 and z["folios"] == 35 and z["max_abs_contribution_fraction"] <= .15 and all(s[e]["local"]["effect"] >= .05 and s[e]["local"]["minimum_leave_one_folio_out"] > 0 and s[e]["local"]["max_abs_contribution_fraction"] <= .18 for e in ("IT2a", "RF1b"))


def bpass(s):
    z = s["ZL3b"]["boundary"]
    return z["effect"] >= .10 and max(z["p_by_ensemble"].values()) <= .05 and z["minimum_leave_one_folio_out"] >= .05 and z["positive_folios"] >= 27 and z["folios"] == 45 and z["max_abs_contribution_fraction"] <= .15 and all(s[e]["boundary"]["effect"] >= .05 and s[e]["boundary"]["minimum_leave_one_folio_out"] > 0 and s[e]["boundary"]["max_abs_contribution_fraction"] <= .18 for e in ("IT2a", "RF1b"))


def evaluate(task):
    family, amplitude, world = task
    summaries = {}
    for edition in READINGS:
        panel = PANELS[edition]
        planted = sorted({row["physical_folio"] for row in panel["rows"]})[world % len({row["physical_folio"] for row in panel["rows"]})] if family == "ONE_FOLIO" else None
        values = summary(panel, synthetic(panel, world, family, amplitude, planted), ASSIGNMENTS, f"CHO_CHE_SCOPE_PREFLIGHT|{family}|{amplitude:.1f}|{world}")
        summaries[edition] = {"edition": edition, "assignments_per_ensemble": ASSIGNMENTS, **values}
    return {"family": family, "amplitude": amplitude, "world": world, "local_pass": lpass(summaries), "boundary_pass": bpass(summaries), "summaries": summaries}


def close(a, b, path="root"):
    global CHECKS
    CHECKS += 1
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            raise AssertionError(f"keys {path}")
        for key in a:
            close(a[key], b[key], f"{path}.{key}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise AssertionError(f"length {path}")
        for i, (left, right) in enumerate(zip(a, b)):
            close(left, right, f"{path}[{i}]")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        if abs(float(a) - float(b)) > 1e-12:
            raise AssertionError(f"numeric {path}: {a} != {b}")
    elif a != b:
        raise AssertionError(f"value {path}: {a} != {b}")


def main():
    global PANELS, CHECKS
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite v2 validation")
    for path, expected in HASHES.items():
        CHECKS += 1
        if sha(path) != expected:
            raise AssertionError(f"hash {path.name}")
    production = json.loads(PRODUCTION.read_text())
    PANELS = build_panels()
    capacities = {
        edition: {
            "events": len(PANELS[edition]["rows"]), "queries": len(PANELS[edition]["query_indices"]),
            "local_folios": len(PANELS[edition]["local_folios"]), "boundary_pairs": len(PANELS[edition]["pair_left"]),
            "boundary_strata": len(PANELS[edition]["pair_to_stratum"]), "boundary_folios": len(PANELS[edition]["boundary_folios"]),
        } for edition in READINGS
    }
    close(capacities, production["capacities"], "capacities")
    tasks = [("NULL", 1.0, w) for w in range(64)] + [("PARAGRAPH", 2.0, w) for w in range(8)] + [("PARAGRAPH", 3.5, w) for w in range(8)] + [("ONE_FOLIO", 4.0, w) for w in range(8)] + [("SEQUENTIAL", .9, w) for w in range(8)]
    with mp.get_context("fork").Pool(32) as pool:
        worlds = pool.map(evaluate, tasks)
    worlds.sort(key=lambda row: (row["family"], row["amplitude"], row["world"]))
    close(worlds, production["worlds"], "worlds")
    pick = lambda family, amp: [row for row in worlds if row["family"] == family and row["amplitude"] == amp]
    null, local, boundary, one, sequential = pick("NULL", 1.0), pick("PARAGRAPH", 2.0), pick("PARAGRAPH", 3.5), pick("ONE_FOLIO", 4.0), pick("SEQUENTIAL", .9)
    aggregates = {
        "null_worlds": 64, "null_local_passes": sum(row["local_pass"] for row in null), "null_boundary_passes": sum(row["boundary_pass"] for row in null),
        "local_power_passes": sum(row["local_pass"] for row in local), "boundary_power_passes": sum(row["boundary_pass"] for row in boundary),
        "one_folio_local_passes": sum(row["local_pass"] for row in one), "one_folio_boundary_passes": sum(row["boundary_pass"] for row in one),
        "sequential_local_passes": sum(row["local_pass"] for row in sequential), "sequential_boundary_passes": sum(row["boundary_pass"] for row in sequential),
    }
    close(aggregates, production["aggregates"], "aggregates")

    panel = PANELS["ZL3b"]
    labels = synthetic(panel, 0, "PARAGRAPH", 2.0)
    first = summary(panel, labels, 127, "CHO_CHE_SCOPE_COMPLEMENT")
    second = summary(panel, 1-labels, 127, "CHO_CHE_SCOPE_COMPLEMENT")
    differences = []
    for target in ("local", "boundary"):
        for field in ("effect", "minimum_leave_one_folio_out", "max_abs_contribution_fraction"):
            differences.append(abs(first[target][field]-second[target][field]))
        for ensemble in ("INDEPENDENT_STRATUM", "COUPLED_PAGE"):
            differences.append(abs(first[target]["p_by_ensemble"][ensemble]-second[target]["p_by_ensemble"][ensemble]))
    multiset = True
    ids = np.arange(1, 513, dtype=np.uint64)
    for ensemble in ("INDEPENDENT_STRATUM", "COUPLED_PAGE"):
        moved = rotations(panel, labels, ids, ensemble, "CHO_CHE_SCOPE_MULTISET")
        for positions, page, key in panel["rotations"]:
            multiset &= bool(np.all(moved[:, positions].sum(1) == labels[positions].sum()))
    invariants = {"complement_max_abs_difference": max(differences), "complement_invariant_within_1e_12": max(differences) <= 1e-12, "rotation_stratum_label_multisets_preserved": multiset}
    close(invariants, production["invariants"], "invariants")
    if production["status"] != "PASS_TARGET_FREE_SCOPE_PREFLIGHT_V2" or production["decision"] != "GO_FREEZE_ONE_TARGET_RUN" or not all(production["gates"].values()):
        raise AssertionError("production decision")
    if production["target_isolation"]["target_outcomes_accessed"] or production["target_isolation"]["target_scores_computed"] or TARGET_OUT.exists() or TARGET_REPORT.exists():
        raise AssertionError("target isolation")
    if not TARGET_SOURCE.exists():
        raise AssertionError("target source existence")
    expected_inputs = {path.name: sha(path) for path in (MASKED, MASKED_VALIDATION, CORE, V1_SPEC, V1_RESULT, V1_AUDIT, AMENDMENT, RUNNER)}
    close(expected_inputs, production["inputs"], "inputs")
    expected_report = f"""# `cho/che` paragraph-scope synthetic preflight v2

Status: **{production['status']}**

Using only the 30,160-row outcome-masked universe, the frozen two-ensemble
scorer produced **{aggregates['null_local_passes']}/64** local and
**{aggregates['null_boundary_passes']}/64** boundary false passes.
It recovered **{aggregates['local_power_passes']}/8** local plants
and **{aggregates['boundary_power_passes']}/8** stronger
distance-controlled boundary plants. One-folio and generic sequential controls
produced **{aggregates['one_folio_local_passes']}/8,
{aggregates['one_folio_boundary_passes']}/8** and
**{aggregates['sequential_local_passes']}/8,
{aggregates['sequential_boundary_passes']}/8** local/boundary passes.

Complement, rotation-multiset, capacity, finite-score, mutation, isolation, and
target-absence gates all passed.
The source outcome table was existence-tested only; **zero target outcomes and
zero target scores** were accessed.

{production['decision']} authorizes at most one separately frozen target run. No
authorial paragraph, sound, word, language, cipher operation, meaning,
plaintext, or translation follows from this preflight.
"""
    if PRODUCTION_REPORT.read_text() != expected_report:
        raise AssertionError("report bytes")
    CHECKS += 1
    result = {
        "experiment": "CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_V2_VALIDATION",
        "status": "PASS_INDEPENDENT_FULL_V2_PREFLIGHT_RECONSTRUCTION",
        "checks": CHECKS, "validator_sha256": sha(VALIDATOR), "production_sha256": sha(PRODUCTION),
        "worlds_reconstructed": len(worlds), "reading_summaries_reconstructed": len(worlds)*3,
        "aggregates": aggregates, "target_source_opened": False, "target_outcomes_accessed": 0, "target_scores_computed": 0,
        "target_outputs_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(), "failures": [],
        "claim_ceiling": production["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    REPORT.write_text(f"""# `cho/che` scope synthetic preflight v2 validation

Status: **{result['status']}**

A nonimporting implementation reconstructed all **96** synthetic worlds,
**288** reading summaries, both 511-assignment rotation ensembles, complete
capacity and hierarchy, the 0/64, 8/8, 8/8, 0/8, and 0/8 pass counts,
complement and 512-assignment multiset controls, exact decisions and report in
**{CHECKS:,}** checks. The manuscript outcome source was not opened and target
outputs remain absent. This validates preflight authorization only; no scope,
meaning, plaintext, or translation follows.
""")
    print(json.dumps({"status": result["status"], "checks": CHECKS, "worlds": len(worlds)}, sort_keys=True))


if __name__ == "__main__":
    main()
