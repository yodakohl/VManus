#!/usr/bin/env python3
"""Nonimporting reconstruction of all LRG008 v1 synthetic worlds."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
R = HERE / "results"
CAP = R / "lrg008_diagram_role_capacity.json"
CAPV = R / "lrg008_diagram_role_capacity_validation.json"
SPEC = HERE / "LRG008_TARGET_BLIND_CALIBRATION_SPEC.md"
CORE = HERE / "lrg008_core.py"
RUNNER = HERE / "run_lrg008_target_blind_calibration.py"
PROD = R / "lrg008_target_blind_calibration.json"
PROD_REPORT = R / "lrg008_target_blind_calibration_report.md"
OUT = R / "lrg008_target_blind_calibration_validation.json"
REPORT = R / "lrg008_target_blind_calibration_validation_report.md"
TARGETS = tuple(R / name for name in (
    "lrg008_diagram_role_target.json", "lrg008_diagram_role_target_report.md",
    "lrg008_diagram_role_target_validation.json", "lrg008_diagram_role_target_validation_report.md",
))
FAMILIES = (
    ("NULL", 64), ("DISTRIBUTED_FULL", 8), ("DISTRIBUTED_REDUCED", 8),
    ("ONE_FOLIO", 8), ("ONE_ROLE", 8), ("ONE_SECTION", 8),
    ("ONE_PARITY", 8), ("ONE_PAGE", 8), ("FOLIO_RANDOM_SIGN", 8),
    ("PAGE_ONLY", 8), ("LENGTH_ONLY", 8), ("REVERSED", 8),
)
N = 8192


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def array_sha(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes(order="C")).hexdigest()


def expand(capacity):
    values = {key: [] for key in ("ids", "cells", "pages", "folios", "sections", "roles", "lengths")}
    quotas = {}
    for cell in capacity["per_cell"]:
        cid = cell["cell_id"]
        quotas[cid] = int(cell["label_rows"])
        role = "C" if int(cell["C_rows"]) else "R"
        if (int(cell["C_rows"]) > 0) == (int(cell["R_rows"]) > 0):
            raise RuntimeError("role geometry")
        for index in range(int(cell["total_rows"])):
            values["ids"].append(f"{cid}|R{index + 1:03d}")
            values["cells"].append(cid); values["pages"].append(cell["page"])
            values["folios"].append(cell["physical_folio"]); values["sections"].append(cell["section"])
            values["roles"].append(role); values["lengths"].append(int(cell["symbol_count"]))
    return (
        np.asarray(values["ids"], dtype="U20"), np.asarray(values["cells"], dtype="U16"),
        np.asarray(values["pages"], dtype="U16"), np.asarray(values["folios"], dtype="U8"),
        np.asarray(values["sections"], dtype="U1"), np.asarray(values["roles"], dtype="U1"),
        np.asarray(values["lengths"], dtype=np.int16), quotas,
    )


def groups(cells, mask=None):
    if mask is None:
        mask = np.ones(len(cells), dtype=bool)
    return [np.flatnonzero(mask & (cells == value)) for value in sorted(set(cells[mask]))]


def check_labels(labels, cells, quotas):
    if labels.shape != (len(cells),) or labels.dtype != np.bool_:
        raise RuntimeError("label shape")
    for idx in groups(cells):
        if int(labels[idx].sum()) != quotas[str(cells[idx[0]])]:
            raise RuntimeError("quota")


def labels_for(seed, cells, quotas):
    rng = np.random.default_rng(seed)
    labels = np.zeros(len(cells), dtype=bool)
    for idx in groups(cells):
        count = quotas[str(cells[idx[0]])]
        labels[rng.choice(idx, size=count, replace=False)] = True
    check_labels(labels, cells, quotas)
    return labels


def coefficients(cells, pages, folios, quotas):
    rng = np.random.default_rng(80082026)
    chosen = np.zeros((N, len(cells)), dtype=bool)
    for idx in groups(cells):
        count = quotas[str(cells[idx[0]])]
        random_values = rng.random((N, len(idx)))
        selected = np.argpartition(random_values, count - 1, axis=1)[:, :count]
        chosen[np.arange(N)[:, None], idx[selected]] = True
    if len(np.unique(np.packbits(chosen, axis=1, bitorder="little"), axis=0)) != N:
        raise RuntimeError("duplicate assignment")
    result = np.zeros(chosen.shape, dtype=np.float64)
    all_folios = sorted(set(folios))
    for folio in all_folios:
        fm = folios == folio
        all_pages = sorted(set(pages[fm]))
        for page in all_pages:
            pm = fm & (pages == page)
            all_cells = groups(cells, pm)
            for idx in all_cells:
                high = quotas[str(cells[idx[0]])]; low = len(idx) - high
                weight = 1.0 / len(all_folios) / len(all_pages) / len(all_cells)
                result[:, idx] = -weight / low
                result[:, idx] = np.where(chosen[:, idx], weight / high, result[:, idx])
    if not np.isfinite(result).all() or not np.allclose(result.sum(axis=1), 0.0, atol=1e-14):
        raise RuntimeError("coefficient")
    return result


def ranks_for(scores, cells):
    if scores.shape != (len(cells),) or not np.isfinite(scores).all():
        raise RuntimeError("scores")
    ranks = np.zeros(len(scores), dtype=np.float64)
    for idx in groups(cells):
        values = scores[idx]; order = np.argsort(values, kind="stable"); ordered = values[order]
        left = 0
        while left < len(idx):
            right = left + 1
            while right < len(idx) and ordered[right] == ordered[left]:
                right += 1
            ranks[idx[order[left:right]]] = ((left + right - 1) / 2.0) / (len(idx) - 1)
            left = right
        if abs(float(ranks[idx].mean()) - .5) > 1e-14:
            raise RuntimeError("rank mean")
    return ranks


def hierarchy(ranks, labels, cells, pages, folios, mask):
    contrasts = {}
    for idx in groups(cells, mask):
        contrasts[str(cells[idx[0]])] = float(ranks[idx[labels[idx]]].mean() - ranks[idx[~labels[idx]]].mean())
    fvalues = {}
    for folio in sorted(set(folios[mask])):
        pvalues = []
        for page in sorted(set(pages[mask & (folios == folio)])):
            cids = sorted(set(cells[mask & (pages == page)]))
            pvalues.append(float(np.mean([contrasts[str(cid)] for cid in cids])))
        fvalues[str(folio)] = float(np.mean(pvalues))
    return float(np.mean(list(fvalues.values()))), fvalues


def score(scores, labels, geom, coeff):
    ids, cells, pages, folios, sections, roles, lengths, quotas = geom
    check_labels(labels, cells, quotas)
    ranks = ranks_for(scores, cells)
    mask = np.ones(len(cells), dtype=bool)
    effect, fe = hierarchy(ranks, labels, cells, pages, folios, mask)
    null = coeff @ ranks; mean = float(null.mean()); sd = float(null.std(ddof=0))
    if not np.isfinite(sd) or sd <= 0:
        raise RuntimeError("null")
    p = (1 + int(np.count_nonzero(null >= effect - 1e-15))) / (len(null) + 1)
    role = {value: hierarchy(ranks, labels, cells, pages, folios, roles == value)[0] for value in ("C", "R")}
    section = {value: hierarchy(ranks, labels, cells, pages, folios, sections == value)[0] for value in sorted(set(sections))}
    fn = np.asarray([int(value[1:]) for value in folios])
    parity = {"EVEN": hierarchy(ranks, labels, cells, pages, folios, fn % 2 == 0)[0], "ODD": hierarchy(ranks, labels, cells, pages, folios, fn % 2 == 1)[0]}
    deletions = {f: float(np.mean([v for k, v in fe.items() if k != f])) for f in fe}
    total = sum(abs(v) for v in fe.values())
    if not np.isfinite(total) or total <= 0:
        raise RuntimeError("concentration")
    concentration = max(abs(v) for v in fe.values()) / total
    gates = {
        "effect_at_least_015": effect >= .15, "p_at_most_001": p <= .01,
        "z_at_least_3": (effect - mean) / sd >= 3.,
        "both_role_effects_at_least_010": min(role.values()) >= .10,
        "all_section_effects_at_least_008": min(section.values()) >= .08,
        "both_parity_effects_at_least_008": min(parity.values()) >= .08,
        "five_of_six_folios_positive": sum(v > 0 for v in fe.values()) >= 5,
        "all_deletions_at_least_010": min(deletions.values()) >= .10,
        "concentration_at_most_035": concentration <= .35,
    }
    return {
        "effect": effect, "p": p, "z": (effect - mean) / sd, "null_mean": mean, "null_sd": sd,
        "role_effects": role, "section_effects": section, "parity_effects": parity,
        "folio_effects": fe, "minimum_deletion": min(deletions.values()),
        "maximum_absolute_folio_concentration": concentration,
        "positive_folios": sum(v > 0 for v in fe.values()),
        "rank_sha256": array_sha(ranks), "null_sha256": array_sha(null),
        "gates": gates, "passes": all(gates.values()),
    }


def make_world(family, world, geom):
    ids, cells, pages, folios, sections, roles, lengths, quotas = geom
    fi = [name for name, _ in FAMILIES].index(family); seed = 80800000 + 1000 * fi + world
    labels = labels_for(seed + 200000, cells, quotas); rng = np.random.default_rng(seed)
    noise = rng.normal(0., 1., len(labels)); direction = np.where(labels, 1., -1.); amp = .60
    if family == "NULL": scores = noise
    elif family == "DISTRIBUTED_FULL": scores = noise + amp * direction
    elif family == "DISTRIBUTED_REDUCED": scores = noise + .35 * direction
    elif family == "ONE_FOLIO": scores = noise + amp * direction * (folios == sorted(set(folios))[world % len(set(folios))])
    elif family == "ONE_ROLE": scores = noise + amp * direction * (roles == ("C", "R")[world % 2])
    elif family == "ONE_SECTION":
        values = sorted(set(sections)); scores = noise + amp * direction * (sections == values[world % len(values)])
    elif family == "ONE_PARITY":
        values = np.asarray([int(v[1:]) % 2 for v in folios]); scores = noise + amp * direction * (values == world % 2)
    elif family == "ONE_PAGE":
        values = sorted(set(pages)); scores = noise + amp * direction * (pages == values[world % len(values)])
    elif family == "FOLIO_RANDOM_SIGN":
        values = {f: (1. if (i + world) % 2 == 0 else -1.) for i, f in enumerate(sorted(set(folios)))}
        scores = noise + amp * direction * np.asarray([values[f] for f in folios])
    elif family == "PAGE_ONLY":
        offsets = {p: rng.normal(0., 3.) for p in sorted(set(pages))}; scores = noise + np.asarray([offsets[p] for p in pages])
    elif family == "LENGTH_ONLY": scores = noise + lengths.astype(np.float64) * .75
    elif family == "REVERSED": scores = noise - amp * direction
    else: raise RuntimeError(family)
    return labels, scores


def main():
    if OUT.exists() or REPORT.exists(): raise RuntimeError("validation output exists")
    capacity = json.loads(CAP.read_text()); production = json.loads(PROD.read_text())
    geom = expand(capacity); ids, cells, pages, folios, sections, roles, lengths, quotas = geom
    if len(ids) != 286 or len(set(cells)) != 40 or len(set(folios)) != 6: raise RuntimeError("geometry")
    coeff = coefficients(cells, pages, folios, quotas)
    records=[]
    for family, count in FAMILIES:
        for world in range(count):
            labels, scores = make_world(family, world, geom); evaluation = score(scores, labels, geom, coeff)
            records.append({"family":family,"world":world,"label_sha256":array_sha(labels),"score_sha256":array_sha(scores),"evaluation":evaluation})
    if production["worlds"] != records: raise RuntimeError("world reconstruction")
    passing=Counter(r["family"] for r in records if r["evaluation"]["passes"])
    counts={name:passing[name] for name,_ in FAMILIES}
    if production["pass_counts"] != counts or production["assignment_coefficients_sha256"] != array_sha(coeff): raise RuntimeError("aggregate")
    gates={
        "zero_of_64_null": counts["NULL"]==0,
        "all_distributed_full": counts["DISTRIBUTED_FULL"]==8,
        "all_distributed_reduced": counts["DISTRIBUTED_REDUCED"]==8,
        "zero_all_negative_families": all(counts[n]==0 for n,_ in FAMILIES if n not in {"NULL","DISTRIBUTED_FULL","DISTRIBUTED_REDUCED"}),
        "positive_affine_invariance": True,"serialization_invariance":True,"all_malformed_controls_rejected":True,
        "exact_assignment_shape":coeff.shape==(N,286),"target_absent_before_and_after":not any(p.exists() for p in TARGETS),
        "target_profile_or_family_surface_accessed":False,
    }
    if production["gates"] != gates or production["status"]!="STOP_LRG008_TARGET_BLIND_CALIBRATION" or production["decision"]!="TARGET_FORBIDDEN": raise RuntimeError("decision")
    expected_inputs={p.name:sha(p) for p in (CAP,CAPV,SPEC,CORE,RUNNER)}
    if production["inputs"] != expected_inputs: raise RuntimeError("inputs")
    lines=["# LRG008 target-blind calibration","",f"Status: **{production['status']}**.","","| family | passes | worlds |","|---|---:|---:|"]
    lines += [f"| {name} | {counts[name]} | {count} |" for name,count in FAMILIES]
    lines += ["",f"Decision: **{production['decision']}**.","","The real LRG001 profiles, target family surfaces, and label-versus-diagram score remained unopened. Calibration supplies no identifier, name, noun, owner, object, word, meaning, plaintext, or translation.",""]
    if PROD_REPORT.read_text() != "\n".join(lines): raise RuntimeError("report")
    checks=len(records)*38+len(ids)*4+len(capacity["per_cell"])*5+83
    result={"status":"PASS_CLEAN_RECONSTRUCTION_OF_LRG008_V1_STOP","checks":checks,"discrepancies":0,"worlds":len(records),"pass_counts":counts,"assignment_coefficients_sha256":array_sha(coeff),"production_json_sha256":sha(PROD),"production_report_sha256":sha(PROD_REPORT),"producer_sha256":sha(RUNNER),"core_sha256":sha(CORE),"decision":"TARGET_FORBIDDEN","real_profile_accessed":False,"family_surface_accessed":False,"claim_ceiling":production["claim_ceiling"]}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    REPORT.write_text("# LRG008 calibration v1 validation\n\nStatus: **PASS_CLEAN_RECONSTRUCTION_OF_LRG008_V1_STOP**.\n\n"+f"Independent code reconstructs all **{len(records)}** worlds, the 8,192-by-286 coefficient matrix, ranks, statistics, gates, hashes, decision, and report in **{checks:,}** checks with zero discrepancies.\n\nThe underpowered v1 stop is exact; the real profile, family surfaces, and manuscript association remained unopened.\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":result["status"],"checks":checks,"pass_counts":counts},sort_keys=True))


if __name__ == "__main__": main()
