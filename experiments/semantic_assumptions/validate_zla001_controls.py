#!/usr/bin/env python3
"""Nonimporting reconstruction of all ZLA001 synthetic controls."""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
R = BASE / "results"
PANEL = R / "zodiac_label_cycle_capacity.tsv"
STORED = R / "zla001_controls.json"
ATTEMPT1 = R / "zla001_controls_attempt1.json"
OUT = R / "zla001_controls_validation.json"
OUT_MD = R / "zla001_controls_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
VIEWS = ("FAMILY_ONLY", "BOUNDARY_AWARE")
KINDS = ("DISTRIBUTED", "NULL", "ONE_FOLIO", "READING_DISAGREEMENT", "EXACT_ONLY", "LENGTH_ONLY", "DISTANCE_TWO")
N = 65_536
TOL = 1e-15


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ahash(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes(order="C")).hexdigest()


def geometry() -> tuple[list[dict[str, object]], list[str], list[str]]:
    with PANEL.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["ring_id"]].append(row)
    rings = []
    for ring_id in sorted(grouped):
        values = sorted(grouped[ring_id], key=lambda row: int(row["grove_ordinal"]))
        rings.append({
            "id": ring_id, "page": values[0]["page"], "folio": values[0]["physical_folio"],
            "loci": tuple(row["current_locus"] for row in values),
        })
    pages = sorted({str(ring["page"]) for ring in rings})
    folios = sorted({str(ring["folio"]) for ring in rings})
    if len(rings) != 21 or sum(len(ring["loci"]) for ring in rings) != 235 or len(pages) != 11 or len(folios) != 4:
        raise AssertionError("geometry")
    return rings, pages, folios


def orbit(rings: list[dict[str, object]]) -> tuple[np.ndarray, dict[str, int | str]]:
    options = [tuple(range(2, len(ring["loci"]) // 2 + 1)) for ring in rings]
    radices = [len(value) for value in options]
    total = math.prod(radices)
    domain = b"ZLA001|NONADJACENT_DISTANCE_ORBIT|v1"
    start = int.from_bytes(hashlib.sha256(domain + b"|start").digest(), "big") % total
    step = int.from_bytes(hashlib.sha256(domain + b"|step").digest(), "big") % total or 1
    while math.gcd(step, total) != 1:
        step += 1
    result = np.empty((N, len(rings)), dtype="<u2")
    for world in range(N):
        value = (start + world * step) % total
        for column in range(len(rings) - 1, -1, -1):
            digit = value % radices[column]
            value //= radices[column]
            result[world, column] = options[column][digit]
    if len({row.tobytes() for row in result}) != N:
        raise AssertionError("orbit duplicates")
    return result, {"complete_space": total, "start": start, "step": step, "sha256": ahash(result)}


def edit(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    if len(a) < len(b):
        a, b = b, a
    old = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        new = [i]
        for j, y in enumerate(b, 1):
            new.append(min(new[-1] + 1, old[j] + 1, old[j - 1] + (x != y)))
        old = new
    return old[-1]


def ps(a: tuple[str, ...], b: tuple[str, ...]) -> float:
    m = max(len(a), len(b))
    value = (1.0 - edit(a, b) / m) - min(len(a), len(b)) / m
    if value > TOL or not math.isfinite(value):
        raise AssertionError("pair")
    return min(value, 0.0)


def plant(ring: dict[str, object], seed: int, step: int) -> list[tuple[str, ...]]:
    size = len(ring["loci"])
    unseen = set(range(size)); cycles = []
    while unseen:
        start = min(unseen); cycle = []; value = start
        while value in unseen:
            unseen.remove(value); cycle.append(value); value = (value + step) % size
        cycles.append(cycle)
    output = [None] * size
    for ci, cycle in enumerate(cycles):
        width = min(6, max(2, len(cycle) - 1))
        tokens = [f"E{seed}:{ring['id']}:{ci}:{i}" for i in range(len(cycle))]
        for local, position in enumerate(cycle):
            output[position] = tuple(tokens[(local + offset) % len(tokens)] for offset in range(width))
    return [tuple(value) for value in output]


def random_seq(ring: dict[str, object], seed: int, reading: str) -> list[tuple[str, ...]]:
    rng = random.Random(f"ZLA001|{seed}|{reading}|{ring['id']}")
    alphabet = [f"A{i}" for i in range(12)]
    output = []
    for position in range(len(ring["loci"])):
        length = 4 + rng.randrange(4)
        output.append(tuple(rng.choice(alphabet) for _ in range(length - 1)) + (f"N{position}",))
    return output


def exact_seq(ring: dict[str, object], seed: int) -> list[tuple[str, ...]]:
    rng = random.Random(f"ZLA001|EXACT|{seed}|{ring['id']}")
    bases = [tuple(f"X{pair}:{rng.randrange(7)}:{i}" for i in range(5)) for pair in range((len(ring["loci"]) + 1) // 2)]
    return [bases[i // 2] for i in range(len(ring["loci"]))]


def length_seq(ring: dict[str, object], seed: int) -> list[tuple[str, ...]]:
    lengths = [3 + ((i + seed % 3) // 2) % 5 for i in range(len(ring["loci"]))]
    return [tuple("L" for _ in range(length)) for length in lengths]


def boundary(values: list[tuple[str, ...]]) -> list[tuple[str, ...]]:
    return [value[:max(1, len(value)//2)] + ("|",) + value[max(1, len(value)//2):] for value in values]


def world(rings: list[dict[str, object]], folios: list[str], kind: str, seed: int) -> dict:
    output = {reading: {view: [] for view in VIEWS} for reading in READINGS}
    signal = folios[seed % len(folios)]
    for reading in READINGS:
        for ring in rings:
            selected = kind
            if kind == "ONE_FOLIO": selected = "DISTRIBUTED" if ring["folio"] == signal else "NULL"
            if kind == "READING_DISAGREEMENT": selected = "DISTRIBUTED" if reading != "RF1b" else "DISTANCE_TWO"
            if selected == "DISTRIBUTED": values = plant(ring, seed, 1)
            elif selected == "DISTANCE_TWO": values = plant(ring, seed, 2)
            elif selected == "NULL": values = random_seq(ring, seed, reading)
            elif selected == "EXACT_ONLY": values = exact_seq(ring, seed)
            elif selected == "LENGTH_ONLY": values = length_seq(ring, seed)
            else: raise AssertionError(selected)
            output[reading]["FAMILY_ONLY"].append(values)
            output[reading]["BOUNDARY_AWARE"].append(boundary(values))
    return output


def ring_table(values: list[tuple[str, ...]], boundaries: list[tuple[str, ...]], size: int, noexact: bool) -> dict[int, float]:
    result = {}
    for distance in range(1, size // 2 + 1):
        scores = []
        for i in range(size):
            j = (i + distance) % size
            if noexact and boundaries[i] == boundaries[j]: continue
            scores.append(ps(values[i], values[j]))
        result[distance] = float(np.mean(scores)) if len(scores) >= 3 else float("nan")
    return result


def aggregate(matrix: np.ndarray, rings: list[dict[str, object]], pages: list[str], folios: list[str]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    page_scores = {}
    for page in pages:
        cols = [i for i, ring in enumerate(rings) if ring["page"] == page]
        with np.errstate(invalid="ignore"): page_scores[page] = np.nanmean(matrix[:, cols], axis=1)
    fs = {}
    for folio in folios:
        pgs = [page for page in pages if any(ring["page"] == page and ring["folio"] == folio for ring in rings)]
        with np.errstate(invalid="ignore"): fs[folio] = np.nanmean(np.stack([page_scores[p] for p in pgs]), axis=0)
    with np.errstate(invalid="ignore"): total = np.nanmean(np.stack([fs[f] for f in folios]), axis=0)
    return total, fs


def score_view(rings, pages, folios, assignments, sequences, reading, view, noexact):
    columns = []; eligible = []
    for c, ring in enumerate(rings):
        table = ring_table(sequences[reading][view][c], sequences[reading]["BOUNDARY_AWARE"][c], len(ring["loci"]), noexact)
        values = np.empty(N + 1); values[0] = table[1]
        for d in range(2, len(ring["loci"]) // 2 + 1): values[1:][assignments[:, c] == d] = table[d]
        columns.append(values)
        if math.isfinite(values[0]): eligible.append(ring["id"])
    total, fs = aggregate(np.stack(columns, axis=1), rings, pages, folios)
    return total, fs, eligible


def summary(scores):
    effects = {}; zobs = {}; znull = {}
    for reading in READINGS:
        values = scores[reading]
        if not np.isfinite(values).all(): raise AssertionError("nonfinite aggregate")
        mean = float(np.mean(values[1:])); sd = float(np.std(values[1:], ddof=0))
        if not sd > 0: raise AssertionError("zero null SD")
        effects[reading] = float(values[0] - mean); zobs[reading] = float((values[0]-mean)/sd); znull[reading] = (values[1:]-mean)/sd
    joint = min(zobs.values()); null = np.min(np.stack([znull[r] for r in READINGS]), axis=0)
    exceed = int(np.count_nonzero(null >= joint - TOL))
    return {"effect_by_reading": effects, "minimum_effect": min(effects.values()), "z_by_reading": zobs, "joint_z": joint,
            "exceedances": exceed, "p_plus_one": (1+exceed)/(N+1), "null_joint_sha256": ahash(null.astype("<f8")),
            "score_sha256_by_reading": {r: ahash(scores[r].astype("<f8")) for r in READINGS}}


def evaluate(rings, pages, folios, assignments, sequences):
    if assignments.shape != (N, len(rings)) or len({row.tobytes() for row in assignments}) != N: raise AssertionError("assignment matrix contract")
    for c, ring in enumerate(rings):
        if not set(np.unique(assignments[:, c])) <= set(range(2, len(ring["loci"])//2+1)): raise AssertionError("illegal ring distance")
    full = {v:{} for v in VIEWS}; noex = {v:{} for v in VIEWS}; fscore = {v:{} for v in VIEWS}; coverage = {r:{} for r in READINGS}
    for reading in READINGS:
        for view in VIEWS:
            if len(sequences[reading][view]) != len(rings): raise AssertionError("sequence ring count")
            for ring, vals in zip(rings, sequences[reading][view]):
                if len(vals) != len(ring["loci"]) or any(not v for v in vals): raise AssertionError("sequence slot contract")
            full[view][reading], fscore[view][reading], _ = score_view(rings,pages,folios,assignments,sequences,reading,view,False)
            noex[view][reading], _, eligible = score_view(rings,pages,folios,assignments,sequences,reading,view,True)
            coverage[reading][view] = eligible
    comp = {r:(full[VIEWS[0]][r]+full[VIEWS[1]][r])/2 for r in READINGS}
    nex = {r:(noex[VIEWS[0]][r]+noex[VIEWS[1]][r])/2 for r in READINGS}
    primary = summary(comp); noexact = summary(nex); components = {v:summary(full[v]) for v in VIEWS}
    fe={}; support={}; concentration={}; deletion={f:{} for f in folios}
    for reading in READINGS:
        fe[reading]={}
        for folio in folios:
            values=(fscore[VIEWS[0]][reading][folio]+fscore[VIEWS[1]][reading][folio])/2
            fe[reading][folio]=float(values[0]-np.mean(values[1:]))
        support[reading]=sum(x>0 for x in fe[reading].values()); denom=sum(abs(x) for x in fe[reading].values())
        concentration[reading]=max(abs(x) for x in fe[reading].values())/denom if denom else 1.0
        for deleted in folios: deletion[deleted][reading]=float(np.mean([fe[reading][f] for f in folios if f!=deleted]))
    counts={r:min(len(coverage[r][v]) for v in VIEWS) for r in READINGS}
    fcounts={r:len({ring["folio"] for ring in rings if ring["id"] in set(coverage[r][VIEWS[0]]) and ring["id"] in set(coverage[r][VIEWS[1]])}) for r in READINGS}
    gates={"joint_p_at_most_001":primary["p_plus_one"]<=.01,"minimum_effect_at_least_0015":primary["minimum_effect"]>=.015,
           "both_components_at_least_0010":all(components[v]["minimum_effect"]>=.01 for v in VIEWS),
           "noexact_coverage_at_least_18_rings_all_four_folios":min(counts.values())>=18 and min(fcounts.values())==4,
           "noexact_effect_at_least_0010_and_p_at_most_005":noexact["minimum_effect"]>=.01 and noexact["p_plus_one"]<=.05,
           "at_least_three_positive_folios_every_reading":min(support.values())>=3,
           "every_folio_deletion_positive_every_reading":all(x>0 for d in deletion.values() for x in d.values()),
           "maximum_folio_concentration_at_most_060":max(concentration.values())<=.60}
    return {"primary":primary,"components":components,"noexact":noexact,"noexact_ring_counts":counts,"noexact_folio_counts":fcounts,
            "folio_effects":fe,"positive_folio_counts":support,"folio_concentration":concentration,"deletion_effects":deletion,"gates":gates,"confirmed":all(gates.values())}


def safe(rings,pages,folios,assignments,sequences):
    try: return {"status":"SCORED","confirmed":bool((value:=evaluate(rings,pages,folios,assignments,sequences))["confirmed"]),"result":value}
    except AssertionError as error: return {"status":"REJECTED_NUMERIC_OR_CONTRACT","confirmed":False,"error":str(error)}


def compare(a, b, path="") -> int:
    checks=1
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a)!=set(b): raise AssertionError(f"keys {path}")
        return checks+sum(compare(a[k],b[k],f"{path}.{k}") for k in a)
    if isinstance(a, list) and isinstance(b, list):
        if len(a)!=len(b): raise AssertionError(f"length {path}")
        return checks+sum(compare(x,y,f"{path}[{i}]") for i,(x,y) in enumerate(zip(a,b)))
    if isinstance(a,(int,float)) and isinstance(b,(int,float)) and not isinstance(a,bool) and not isinstance(b,bool):
        if not math.isclose(float(a),float(b),rel_tol=0,abs_tol=1e-15): raise AssertionError(f"number {path}: {a} {b}")
    elif a!=b: raise AssertionError(f"value {path}: {a!r} {b!r}")
    return checks


def compact(value):
    if value["status"]!="SCORED": return value
    r=value["result"]
    return {"status":"SCORED","confirmed":value["confirmed"],"primary":r["primary"],"components":r["components"],"noexact":r["noexact"],
            "noexact_ring_counts":r["noexact_ring_counts"],"noexact_folio_counts":r["noexact_folio_counts"],"positive_folio_counts":r["positive_folio_counts"],
            "folio_concentration":r["folio_concentration"],"deletion_effects":r["deletion_effects"],"gates":r["gates"]}


def main():
    if OUT.exists() or OUT_MD.exists(): raise SystemExit("refusing overwrite")
    stored=json.loads(STORED.read_text()); attempt=json.loads(ATTEMPT1.read_text())
    rings,pages,folios=geometry(); assignments,meta=orbit(rings); checks=0; pass_counts={}
    if stored["orbit"]!=meta: raise AssertionError("orbit metadata"); checks+=1
    for kind in KINDS:
        passing=0
        for seed in range(8):
            actual=safe(rings,pages,folios,assignments,world(rings,folios,kind,seed)); expected=dict(stored["records"][kind][seed]); expected.pop("world"); expected.pop("result_sha256",None)
            checks+=compare(compact(actual),expected,f"{kind}.{seed}"); passing+=bool(actual["confirmed"])
        pass_counts[kind]=passing
    if pass_counts!=stored["pass_counts"]: raise AssertionError("pass counts")
    checks+=1
    if attempt["pass_counts"]!={"DISTANCE_TWO":0,"DISTRIBUTED":8,"EXACT_ONLY":0,"LENGTH_ONLY":0,"NULL":0,"ONE_FOLIO":0,"READING_DISAGREEMENT":2}: raise AssertionError("attempt1")
    checks+=1
    mutation={}
    base=world(rings,folios,"DISTRIBUTED",0)
    duplicate=assignments.copy(); duplicate[1]=duplicate[0]; mutation["duplicate_assignment_rejected"]=safe(rings,pages,folios,duplicate,base)["status"]!="SCORED"
    illegal=assignments.copy(); illegal[0,0]=1; mutation["adjacent_null_distance_rejected"]=safe(rings,pages,folios,illegal,base)["status"]!="SCORED"
    missing=copy.deepcopy(base); missing["ZL3b"]["FAMILY_ONLY"][0].pop(); mutation["missing_slot_rejected"]=safe(rings,pages,folios,assignments,missing)["status"]!="SCORED"
    empty=copy.deepcopy(base); empty["ZL3b"]["FAMILY_ONLY"][0][0]=tuple(); mutation["empty_sequence_rejected"]=safe(rings,pages,folios,assignments,empty)["status"]!="SCORED"
    again,againmeta=orbit(rings); mutation["deterministic_assignment_serialization"]=meta==againmeta and np.array_equal(assignments,again)
    if mutation!=stored["mutation_checks"]: raise AssertionError("mutations")
    checks+=len(mutation)
    if not all(stored["gates"].values()) or stored["status"]!="PASS": raise AssertionError("top gates")
    checks+=2
    result={"experiment":"ZLA001_CONTROL_VALIDATION","status":"PASS","checks":checks,"inputs":{p.name:sha(p) for p in (PANEL,STORED,ATTEMPT1,Path(__file__))},
            "reconstructed":{"worlds":56,"pass_counts":pass_counts,"orbit":meta},"mutations":mutation,
            "claim_ceiling":"Synthetic calibration reconstruction only; no manuscript adjacency effect, serial code, number, degree, word, meaning, plaintext, or translation."}
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    OUT_MD.write_text(f"# ZLA001 control validation\n\nStatus: **PASS** ({checks} checks). A nonimporting implementation reconstructed all 56 complete 65,536-distance worlds, the corrected 8/8 distributed and 0/8 negative pass profile, the failed attempt-1 2/8 disagreement diagnosis, the exact orbit, and every malformed-input control. No manuscript STA sequence was opened.\n")
    print(json.dumps({"status":"PASS","checks":checks,"pass_counts":pass_counts,"orbit_sha256":meta["sha256"]},sort_keys=True))


if __name__=="__main__": main()
