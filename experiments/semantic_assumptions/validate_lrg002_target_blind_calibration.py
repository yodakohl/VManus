#!/usr/bin/env python3
"""Nonimporting reconstruction of every LRG002 synthetic calibration world."""

from __future__ import annotations

import os
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import csv
import hashlib
import json
import math
import multiprocessing as mp
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent; RES = HERE / "results"
CAPACITY = RES / "lrg002_prose_slot_capacity.tsv"
PRODUCTION = RES / "lrg002_target_blind_calibration.json"
PRODUCTION_REPORT = RES / "lrg002_target_blind_calibration_report.md"
OUT = RES / "lrg002_target_blind_calibration_validation.json"
OUT_REPORT = RES / "lrg002_target_blind_calibration_validation_report.md"
ASSIGNMENTS = 8192; SEED = 22022026
POSITIVE = ("DISTRIBUTED_FIRST_FULL", "DISTRIBUTED_LAST_FULL", "DISTRIBUTED_EDGE_FULL", "DISTRIBUTED_FIRST_HALF", "DISTRIBUTED_LAST_HALF")
NEGATIVE = ("ONE_FOLIO", "ONE_SECTION", "ONE_PARITY", "FOLIO_RANDOM_DIRECTION", "SECTION_OPPOSITION", "PARITY_OPPOSITION", "PAGE_ONLY", "LENGTH_ONLY", "SEGMENT_ONLY")
G = None; C = None


def digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def array_digest(value: np.ndarray) -> str: return hashlib.sha256(np.ascontiguousarray(value).tobytes(order="C")).hexdigest()


def geometry() -> dict[str, object]:
    with CAPACITY.open(encoding="utf-8", newline="") as handle: rows = list(csv.DictReader(handle, delimiter="\t"))
    output = {key: np.asarray([row[key] for row in rows]) for key in ("consensus_group_id", "segment_id", "page", "physical_folio", "section", "segment_position", "folio_parity")}
    output["length"] = np.asarray([int(row["symbol_count"]) for row in rows], dtype=np.int16)
    output["primary"] = np.asarray([row["primary_slot_eligible"] == "1" for row in rows])
    groups = defaultdict(list)
    for index, row in enumerate(rows):
        if output["primary"][index]: groups[row["segment_id"]].append(index)
    output["segment_rows"] = tuple(np.asarray(sorted(group, key=lambda index: int(rows[index]["segment_group_index"])), dtype=np.int32) for _, group in sorted(groups.items()))
    output["folio_names"] = tuple(sorted(set(output["physical_folio"]), key=lambda item: int(item[1:])))
    lookup = {name: index for index, name in enumerate(output["folio_names"])}
    output["segment_folio"] = np.asarray([lookup[str(output["physical_folio"][indices[0]])] for indices in output["segment_rows"]], dtype=np.int16)
    if len(rows) != 5824 or output["primary"].sum() != 5769 or len(output["segment_rows"]) != 705 or len(output["folio_names"]) != 16: raise RuntimeError("geometry")
    return output


def ranks(scores: np.ndarray) -> np.ndarray:
    result = np.zeros(len(scores), dtype=np.float64); cells = defaultdict(list)
    for index, (page, length) in enumerate(zip(G["page"], G["length"], strict=True)): cells[(str(page), int(length))].append(index)
    for members in cells.values():
        indices = np.asarray(members, dtype=np.int64); values = scores[indices]
        if len(indices) == 1: continue
        order = np.argsort(values, kind="mergesort"); ordered = values[order]; local = np.empty(len(indices)); start = 0
        while start < len(indices):
            stop = start + 1
            while stop < len(indices) and ordered[stop] == ordered[start]: stop += 1
            local[order[start:stop]] = (start + stop - 1) / 2.0; start = stop
        result[indices] = (local + 1.0) / (len(indices) + 1.0) - 0.5
    return result


def make_rotations(name: str) -> np.ndarray:
    rng = np.random.default_rng(SEED + (0 if name == "INDEPENDENT_SEGMENT" else 1))
    lengths = np.asarray([len(indices) for indices in G["segment_rows"]], dtype=np.uint16)
    if name == "INDEPENDENT_SEGMENT": return np.floor(rng.random((ASSIGNMENTS, len(lengths))) * lengths[None, :]).astype(np.uint16)
    clocks = rng.integers(0, 2**31 - 1, size=(ASSIGNMENTS, len(G["folio_names"])), dtype=np.int64)
    result = np.empty((ASSIGNMENTS, len(lengths)), dtype=np.uint16)
    for index, length in enumerate(lengths): result[:, index] = clocks[:, G["segment_folio"][index]] % int(length)
    return result


def coefficients(shifts: np.ndarray) -> np.ndarray:
    row_count = len(G["consensus_group_id"]); folio_count = len(G["folio_names"])
    left = np.zeros((ASSIGNMENTS, row_count)); right = np.zeros((ASSIGNMENTS, row_count)); assignment_rows = np.arange(ASSIGNMENTS)
    for folio_index in range(folio_count):
        segment_indices = np.flatnonzero(G["segment_folio"] == folio_index); segment_count = len(segment_indices)
        primary = np.concatenate([G["segment_rows"][index] for index in segment_indices]); core_count = len(primary) - 2 * segment_count
        base = -1.0 / (folio_count * core_count); left[:, primary] = base; right[:, primary] = base
        for segment_index in segment_indices:
            positions = G["segment_rows"][segment_index]; shift = shifts[:, segment_index].astype(np.int64)
            first = positions[shift]; last = positions[(shift - 1) % len(positions)]
            left[assignment_rows, first] += 1.0 / (folio_count * segment_count) - base; left[assignment_rows, last] -= base
            right[assignment_rows, last] += 1.0 / (folio_count * segment_count) - base; right[assignment_rows, first] -= base
    return np.concatenate((left, right), axis=0)


def cos(left: np.ndarray, right: np.ndarray) -> float:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right)); return float(left @ right / denominator) if denominator > 1e-15 else -1.0


def summary(values: np.ndarray) -> dict[str, object]:
    vectors = {}
    for folio in G["folio_names"]:
        current = G["primary"] & (G["physical_folio"] == folio)
        means = {position: float(values[current & (G["segment_position"] == position)].mean()) for position in ("FIRST", "LAST", "CORE")}
        vectors[folio] = np.asarray((means["FIRST"] - means["CORE"], means["LAST"] - means["CORE"]))
    matrix = np.stack([vectors[folio] for folio in G["folio_names"]]); overall = matrix.mean(axis=0); norm = float(np.linalg.norm(overall)); direction = overall / norm if norm > 1e-15 else np.zeros(2)
    folio_projection = matrix @ direction; sections = {}; parities = {}
    for section in ("B", "P"):
        mask = np.asarray([str(G["section"][np.flatnonzero(G["physical_folio"] == folio)[0]]) == section for folio in G["folio_names"]]); sections[section] = matrix[mask].mean(axis=0)
    for parity in ("ODD", "EVEN"):
        mask = np.asarray([str(G["folio_parity"][np.flatnonzero(G["physical_folio"] == folio)[0]]) == parity for folio in G["folio_names"]]); parities[parity] = matrix[mask].mean(axis=0)
    deletion = np.asarray([(matrix.sum(axis=0) - matrix[index]) / (len(matrix) - 1) @ direction for index in range(len(matrix))]); denominator = float(np.abs(folio_projection).sum())
    sp = {key: float(vector @ direction) for key, vector in sections.items()}; pp = {key: float(vector @ direction) for key, vector in parities.items()}; sm = max(sp.values()); pm = max(pp.values())
    return {
        "overall_vector": [float(value) for value in overall], "norm": norm,
        "folio_vectors": {folio: [float(value) for value in vectors[folio]] for folio in G["folio_names"]},
        "folio_projections": {folio: float(value) for folio, value in zip(G["folio_names"], folio_projection, strict=True)},
        "positive_folios": int(np.count_nonzero(folio_projection > 0)), "minimum_deletion_projection": float(deletion.min()),
        "maximum_absolute_folio_concentration": float(np.abs(folio_projection).max() / denominator) if denominator else math.inf,
        "section_vectors": {key: [float(value) for value in vector] for key, vector in sections.items()}, "section_projections": sp,
        "section_balance_ratio": min(sp.values()) / sm if sm > 0 else -math.inf, "section_cosine": cos(sections["B"], sections["P"]),
        "parity_vectors": {key: [float(value) for value in vector] for key, vector in parities.items()}, "parity_projections": pp,
        "parity_balance_ratio": min(pp.values()) / pm if pm > 0 else -math.inf, "parity_cosine": cos(parities["ODD"], parities["EVEN"]),
    }


def evaluate(scores: np.ndarray) -> dict[str, object]:
    value = ranks(scores); s = summary(value); pvalues = {}; null_hashes = {}
    for name in ("INDEPENDENT_SEGMENT", "COUPLED_FOLIO"):
        orbit = C[name] @ value; null = np.hypot(orbit[:ASSIGNMENTS], orbit[ASSIGNMENTS:])
        pvalues[name] = (1 + int(np.count_nonzero(null >= s["norm"]))) / (ASSIGNMENTS + 1); null_hashes[name] = array_digest(null)
    gates = {
        "both_null_p_at_most_001": all(value <= .01 for value in pvalues.values()), "norm_at_least_006": s["norm"] >= .06,
        "both_sections_project_at_least_0025": all(value >= .025 for value in s["section_projections"].values()), "both_parities_project_at_least_0025": all(value >= .025 for value in s["parity_projections"].values()),
        "section_balance_ratio_at_least_035": s["section_balance_ratio"] >= .35, "parity_balance_ratio_at_least_035": s["parity_balance_ratio"] >= .35,
        "section_cosine_at_least_025": s["section_cosine"] >= .25, "parity_cosine_at_least_025": s["parity_cosine"] >= .25,
        "positive_folio_support_at_least_12": s["positive_folios"] >= 12, "all_deletions_at_least_0015": s["minimum_deletion_projection"] >= .015,
        "concentration_at_most_025": s["maximum_absolute_folio_concentration"] <= .25,
    }
    return {"rank_sha256": array_digest(value), "summary": s, "pvalues": pvalues, "null_sha256": null_hashes, "gates": gates, "passes": all(gates.values())}


def synthetic(family: str, world: int) -> np.ndarray:
    seed = 720000 + 1000 * list(("NULL",) + POSITIVE + NEGATIVE).index(family) + world; rng = np.random.default_rng(seed); raw = rng.normal(0., 1., len(G["consensus_group_id"]))
    for page in sorted(set(G["page"])): raw[G["page"] == page] += rng.normal(0., 2.)
    raw += .25 * G["length"]; first = G["primary"] & (G["segment_position"] == "FIRST"); last = G["primary"] & (G["segment_position"] == "LAST")
    def add(mask, amount): raw[mask] += amount
    if family == "DISTRIBUTED_FIRST_FULL": add(first, 1.4)
    elif family == "DISTRIBUTED_LAST_FULL": add(last, 1.4)
    elif family == "DISTRIBUTED_EDGE_FULL": add(first | last, 1.1)
    elif family == "DISTRIBUTED_FIRST_HALF": add(first, .8)
    elif family == "DISTRIBUTED_LAST_HALF": add(last, .8)
    elif family == "ONE_FOLIO": add(first & (G["physical_folio"] == "f75"), 3.)
    elif family == "ONE_SECTION": add(first & (G["section"] == "B"), 1.4)
    elif family == "ONE_PARITY": add(first & (G["folio_parity"] == "ODD"), 1.4)
    elif family == "FOLIO_RANDOM_DIRECTION":
        patterns = ((1.8,0.),(-1.8,0.),(0.,1.8),(0.,-1.8))
        for index, folio in enumerate(G["folio_names"]):
            left,right=patterns[(index+world)%4]; add(first&(G["physical_folio"]==folio),left); add(last&(G["physical_folio"]==folio),right)
    elif family == "SECTION_OPPOSITION": add(first&(G["section"]=="B"),1.4); add(first&(G["section"]=="P"),-1.4)
    elif family == "PARITY_OPPOSITION": add(first&(G["folio_parity"]=="ODD"),1.4); add(first&(G["folio_parity"]=="EVEN"),-1.4)
    elif family == "PAGE_ONLY":
        for index,page in enumerate(sorted(set(G["page"]))): raw[G["page"]==page] += 20.*((index%5)-2)
    elif family == "LENGTH_ONLY": raw += 10.*G["length"]
    elif family == "SEGMENT_ONLY":
        for index,segment in enumerate(sorted(set(G["segment_id"]))): raw[G["segment_id"]==segment] += 4.*((index%7)-3)
    elif family != "NULL": raise RuntimeError(family)
    return raw


def worker(task: tuple[str,int]) -> dict[str,object]:
    family,world=task; scores=synthetic(family,world); return {"family":family,"world":world,"score_sha256":array_digest(scores),"evaluation":evaluate(scores)}


def leaves(value) -> int:
    if isinstance(value, dict): return sum(leaves(item) for item in value.values())
    if isinstance(value, list): return sum(leaves(item) for item in value)
    return 1


def main() -> None:
    global G,C
    if OUT.exists() or OUT_REPORT.exists(): raise RuntimeError("validation output exists")
    production=json.loads(PRODUCTION.read_text(encoding="utf-8")); G=geometry(); shifts={name:make_rotations(name) for name in ("INDEPENDENT_SEGMENT","COUPLED_FOLIO")}; C={name:coefficients(matrix) for name,matrix in shifts.items()}
    tasks=[("NULL",world) for world in range(64)]+[(family,world) for family in POSITIVE+NEGATIVE for world in range(8)]
    with mp.get_context("fork").Pool(32) as pool: records=pool.map(worker,tasks,chunksize=1)
    if records != production["records"]: raise RuntimeError("calibration record mismatch")
    if production["rotation_digests"] != {name:array_digest(matrix) for name,matrix in shifts.items()} or production["coefficient_digests"] != {name:array_digest(matrix) for name,matrix in C.items()}: raise RuntimeError("rotation/coefficient mismatch")
    groups={family:[record for record in records if record["family"]==family] for family in ("NULL",)+POSITIVE+NEGATIVE}; counts={family:sum(record["evaluation"]["passes"] for record in current) for family,current in groups.items()}
    gates={"zero_of_64_null":counts["NULL"]==0,"all_distributed_plants_pass":all(counts[family]==8 for family in POSITIVE),"all_adversarial_controls_rejected":all(counts[family]==0 for family in NEGATIVE),"rotation_rows_unique":all(len(np.unique(matrix,axis=0))==ASSIGNMENTS for matrix in shifts.values())}
    if production["pass_counts"]!=counts or production["gates"]!=gates or production["status"]!="PASS_LRG002_TARGET_BLIND_CALIBRATION" or production["decision"]!="GO_FREEZE_SINGLE_LRG002_TARGET": raise RuntimeError("decision mismatch")
    expected_lines=["# LRG002 target-blind slot calibration","",f"Status: **{production['status']}**.","","| family | passes | worlds |","|---|---:|---:|"]+[f"| {family} | {counts[family]} | {len(groups[family])} |" for family in ("NULL",)+POSITIVE+NEGATIVE]+["",f"Decision: **{production['decision']}**.","","The real LRG001 profile and its prose-position association remained unopened. Synthetic calibration supplies no word, identifier, name, POS, meaning, plaintext, or translation.",""]
    if PRODUCTION_REPORT.read_text(encoding="utf-8")!="\n".join(expected_lines): raise RuntimeError("report mismatch")
    result={"status":"PASS_INDEPENDENT_LRG002_CALIBRATION_RECONSTRUCTION","checks":leaves(records)+39,"discrepancies":0,"worlds":len(records),"production_json_sha256":digest(PRODUCTION),"production_report_sha256":digest(PRODUCTION_REPORT),"rotation_digests":production["rotation_digests"],"decision":"GO_FREEZE_SINGLE_LRG002_TARGET","real_position_association_opened":False,"claim_ceiling":production["claim_ceiling"]}
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"; OUT.write_text(text,encoding="utf-8",newline="\n")
    OUT_REPORT.write_text("# LRG002 calibration validation\n\nStatus: **PASS_INDEPENDENT_LRG002_CALIBRATION_RECONSTRUCTION**.\n\n" f"Nonimporting code reconstructs all **{len(records)}** synthetic worlds, both 8,192-row rotation matrices, coefficient matrices, ranks, slot vectors, nulls, gates, digests, decision, and report in **{result['checks']:,}** checks with zero discrepancies.\n\nThe real profile-position association remained unopened; validation supplies no slot function, word, identifier, name, POS, meaning, plaintext, or translation.\n",encoding="utf-8",newline="\n")
    print(text,end="")


if __name__=="__main__": main()
