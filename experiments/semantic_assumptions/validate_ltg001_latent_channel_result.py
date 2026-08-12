#!/usr/bin/env python3
"""Production-free reconstruction of the LTG001 held-folio result."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
RESULT = RESULTS / "ltg001_latent_channel_result.json"
ATLAS = RESULTS / "ltg001_latent_channel_atlas.json"
REPORT = RESULTS / "ltg001_latent_channel_result_report.md"
VALIDATION = RESULTS / "ltg001_latent_channel_result_validation.json"
PRODUCER_FILES = (
    HERE / "ltg001_latent_channel_core.py",
    HERE / "run_ltg001_latent_channel_result.py",
)
ALPHA = 0.25
GRID = (2, 3, 4, 6, 8)


def folio(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.I)
    assert match
    return match.group(1).lower()


def fold(value: str) -> int:
    raw = hashlib.sha256(("LTG001_FOLD_V1|" + value).encode()).digest()
    return int.from_bytes(raw[:4], "big") % 5


def seed(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode()).digest()[:8], "big")


def aggregate(family: np.ndarray, observation: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    joined = np.column_stack((family.astype(np.int64), observation.astype(np.int64)))
    cells, counts = np.unique(joined, axis=0, return_counts=True)
    return cells, counts.astype(np.float64)


def logsumexp(value: np.ndarray) -> np.ndarray:
    maximum = np.max(value, axis=1, keepdims=True)
    return maximum[:, 0] + np.log(np.sum(np.exp(value - maximum), axis=1))


def fit(family: np.ndarray, obs: np.ndarray, nf: int, ns: int, k: int, label: str) -> dict:
    cells, counts = aggregate(family, obs)
    cf = cells[:, 0].astype(int)
    co = cells[:, 1:].astype(int)
    best = None
    for restart in range(8):
        rng = np.random.default_rng(seed(f"{label}|K{k}|R{restart}"))
        pi = rng.gamma(1.0, 1.0, (nf, k)) + ALPHA
        pi /= pi.sum(1, keepdims=True)
        emit = rng.gamma(1.0, 1.0, (3, k, ns)) + ALPHA
        emit /= emit.sum(2, keepdims=True)
        previous = -math.inf
        for iteration in range(1, 501):
            joint = np.log(pi[cf])
            for edition in range(3):
                joint += np.log(emit[edition, :, co[:, edition]])
            norm = logsumexp(joint)
            weight = counts[:, None] * np.exp(joint - norm[:, None])
            pic = np.full((nf, k), ALPHA)
            np.add.at(pic, cf, weight)
            pi = pic / pic.sum(1, keepdims=True)
            ec = np.full((3, k, ns), ALPHA)
            for edition in range(3):
                for state in range(k):
                    np.add.at(ec[edition, state], co[:, edition], weight[:, state])
            emit = ec / ec.sum(2, keepdims=True)
            updated = np.log(pi[cf])
            for edition in range(3):
                updated += np.log(emit[edition, :, co[:, edition]])
            ll = float(np.dot(counts, logsumexp(updated)))
            if math.isfinite(previous) and abs(ll - previous) <= 1e-10 * (1.0 + abs(previous)):
                break
            previous = ll
        parameters = nf * (k - 1) + 3 * k * (ns - 1)
        candidate = {
            "k": k, "pi": pi, "emit": emit, "ll": ll,
            "bic": -2.0 * ll + parameters * math.log(float(counts.sum())),
            "iterations": iteration, "restart": restart,
        }
        if best is None or ll > best["ll"] + 1e-12 or (abs(ll - best["ll"]) <= 1e-12 and restart < best["restart"]):
            best = candidate
    assert best is not None
    return best


def fit_all(family, obs, nf, ns, label):
    fits = [fit(family, obs, nf, ns, k, label) for k in GRID]
    return min(fits, key=lambda item: (item["bic"], item["k"])), fits


def load():
    raw = []
    families = set()
    symbols = set()
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["strict_zero_alternative"] != "1":
                continue
            pf = folio(row["page"])
            codes = [row[field].split() for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
            assert all(len(values) == len(row["family_surface"]) for values in codes)
            for fam, z, i, r in zip(row["family_surface"], *codes):
                assert z[0] == i[0] == r[0] == fam
                observation = (z[1:], i[1:], r[1:])
                families.add(fam); symbols.update(observation)
                raw.append((fam, observation, pf, row["currier"] or "BLANK", (fam, z, i, r)))
    fn = tuple(sorted(families)); sn = tuple(sorted(symbols, key=lambda x: x.encode()))
    fi = {x: i for i, x in enumerate(fn)}; si = {x: i for i, x in enumerate(sn)}
    return {
        "family": np.asarray([fi[x[0]] for x in raw], dtype=np.int16),
        "obs": np.asarray([[si[y] for y in x[1]] for x in raw], dtype=np.int16),
        "folio": tuple(x[2] for x in raw), "fold": np.asarray([fold(x[2]) for x in raw], dtype=np.int8),
        "currier": tuple(x[3] for x in raw), "triplet": tuple(x[4] for x in raw),
        "fn": fn, "sn": sn,
    }


def direct(family, obs, ns):
    contexts = defaultdict(lambda: np.zeros(ns)); backoff = defaultdict(lambda: np.zeros(ns))
    for fam, values in zip(family.tolist(), obs.tolist()):
        for target, left, right in ((0, 1, 2), (1, 0, 2), (2, 0, 1)):
            contexts[(target, fam, values[left], values[right])][values[target]] += 1
            backoff[(target, fam)][values[target]] += 1
    return dict(contexts), dict(backoff)


def main() -> None:
    for path in PRODUCER_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert not any(isinstance(node, ast.ImportFrom) and node.module == "validate_ltg001_latent_channel_result" for node in ast.walk(tree))
    data = load(); nf = len(data["fn"]); ns = len(data["sn"])
    events = []
    folds = []
    for held in range(5):
        train = data["fold"] != held
        selected, candidates = fit_all(data["family"][train], data["obs"][train], nf, ns, f"LTG001_REAL_V1|FOLD{held}")
        contexts, backoff = direct(data["family"][train], data["obs"][train], ns)
        folds.append({
            "fold": held, "selected_k": selected["k"], "selected_bic": selected["bic"],
            "selected_log_likelihood": selected["ll"], "iterations": selected["iterations"],
            "restart": selected["restart"], "candidate_bic": {str(x["k"]): x["bic"] for x in candidates},
        })
        for index in np.flatnonzero(data["fold"] == held):
            values = data["obs"][index]; fam = int(data["family"][index])
            for target, left, right in ((0, 1, 2), (1, 0, 2), (2, 0, 1)):
                if values[left] == values[right]: continue
                weights = selected["pi"][fam] * selected["emit"][left, :, values[left]] * selected["emit"][right, :, values[right]]
                pc = float(np.sum(weights * selected["emit"][target, :, values[target]]) / np.sum(weights))
                key = (target, fam, int(values[left]), int(values[right])); seen = key in contexts
                counts = contexts[key] if seen else backoff[(target, fam)]
                pd = float((counts[values[target]] + ALPHA) / (counts.sum() + ALPHA * ns))
                events.append({
                    "folio": data["folio"][index], "currier": data["currier"][index],
                    "gain": math.log2(pc) - math.log2(pd), "seen": seen,
                    "dominant": data["triplet"][index] == ("B", "B1", "B1", "Ba"),
                })
    fv = defaultdict(list); cv = defaultdict(list)
    for event in events: fv[event["folio"]].append(event["gain"]); cv[event["currier"]].append(event["gain"])
    fg = {key: math.fsum(values)/len(values) for key,values in sorted(fv.items())}
    positive = sum(x > 0 for x in fg.values())
    signp = sum(math.comb(len(fg), x) for x in range(positive, len(fg)+1)) / 2**len(fg)
    def mean(pred):
        values=[x["gain"] for x in events if pred(x)]; return math.fsum(values)/len(values)
    loo = [math.fsum(v for f,v in fg.items() if f != removed)/(len(fg)-1) for removed in fg]
    summary = {
        "event_count": len(events), "folio_count": len(fg),
        "equal_folio_gain_bits": math.fsum(fg.values())/len(fg), "positive_folios": positive,
        "folio_sign_p": signp, "currier_gain_bits": {k: math.fsum(v)/len(v) for k,v in sorted(cv.items())},
        "dominant_policy_deleted_gain_bits": mean(lambda x:not x["dominant"]),
        "unseen_context_gain_bits": mean(lambda x:not x["seen"]),
        "unseen_context_events": sum(not x["seen"] for x in events),
        "minimum_leave_one_folio_gain_bits": min(loo),
    }
    summary["gates"] = {
        "gain_at_least_0_020": summary["equal_folio_gain_bits"] >= .020,
        "sign_p_at_most_0_01": signp <= .01,
        "currier_A_B_at_least_0_010": all(summary["currier_gain_bits"].get(x,-math.inf)>=.010 for x in ("A","B")),
        "dominant_policy_deleted_positive": summary["dominant_policy_deleted_gain_bits"] > 0,
        "unseen_context_positive": summary["unseen_context_gain_bits"] > 0,
        "every_leave_one_folio_positive": summary["minimum_leave_one_folio_gain_bits"] > 0,
    }
    summary["decision"] = "PASS_REUSABLE_LATENT_CHANNEL" if all(summary["gates"].values()) else "FINAL_NONCONFIRMATION"
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks = 0
    assert result["status"] == summary["decision"] == "FINAL_NONCONFIRMATION"; checks += 1
    for key in ("event_count","folio_count","positive_folios","unseen_context_events","decision"):
        assert result["summary"][key] == summary[key]; checks += 1
    for key in ("equal_folio_gain_bits","folio_sign_p","dominant_policy_deleted_gain_bits","unseen_context_gain_bits","minimum_leave_one_folio_gain_bits"):
        assert abs(result["summary"][key]-summary[key]) < 1e-12; checks += 1
    for key in summary["currier_gain_bits"]:
        assert abs(result["summary"]["currier_gain_bits"][key]-summary["currier_gain_bits"][key]) < 1e-12; checks += 1
    assert result["summary"]["gates"] == summary["gates"]; checks += 1
    assert result["fold_models"] == folds; checks += 1
    for key,value in fg.items(): assert abs(result["folio_gain_bits"][key]-value) < 1e-12; checks += 1
    selected, candidates = fit_all(data["family"], data["obs"], nf, ns, "LTG001_REAL_V1|FULL")
    assert selected["k"] == result["full_panel_model"]["selected_k"] == 6; checks += 1
    assert abs(selected["bic"]-result["full_panel_model"]["bic"]) < 1e-12; checks += 1
    assert result["outputs"][ATLAS.name] == hashlib.sha256(ATLAS.read_bytes()).hexdigest(); checks += 1
    assert REPORT.read_text(encoding="utf-8").startswith("# LTG001 latent transcription-channel result\n"); checks += 1
    validation = {"status":"PASS_INDEPENDENT_LTG001_RESULT_RECONSTRUCTION","checks":checks,"production_imported":False}
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation,sort_keys=True))


if __name__ == "__main__":
    main()
