#!/usr/bin/env python3
"""GDT048: determine whether OKAIR is an OK-specific or right-family effect."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
METHOD = ROOT / "GDT048_AIR_RIGHT_FAMILY_SELECTION_METHOD.md"
REPORT = ROOT / "GDT048_AIR_RIGHT_FAMILY_SELECTION_REPORT.md"
BY_BASE = ROOT / "gdt048_air_selection_by_base.tsv"
OCC = ROOT / "gdt048_air_occurrences.tsv"
RESULT = ROOT / "gdt048_result.json"
SUFFIXES = ("aiin", "air", "ain", "ar", "al")
TARGET = {"HB", "SB"}
CONTROL = {"HA", "OB"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def register(row):
    if row["section"] == "H" and row["currier"] == "A":
        return "HA"
    if row["section"] == "H" and row["currier"] == "B":
        return "HB"
    if row["section"] == "S" and row["currier"] == "B":
        return "SB"
    if row["currier"] == "B":
        return "OB"
    return "OUT"


def split_host(host):
    for suffix in SUFFIXES:
        if host.endswith(suffix) and len(host) > len(suffix):
            return host[: -len(suffix)], suffix
    return None


def fisher_two_sided(a, b, c, d):
    row = a + b
    col = a + c
    total = a + b + c + d
    low = max(0, row - (total - col))
    high = min(row, col)

    def prob(x):
        return math.comb(col, x) * math.comb(total - col, row - x) / math.comb(total, row)

    observed = prob(a)
    return sum(prob(x) for x in range(low, high + 1) if prob(x) <= observed + 1e-15)


def exact_stratified(rows, base):
    # Conditional distribution of total target AIR count given margins in each
    # outer-wrapper stratum. Convolve the two hypergeometric distributions.
    distribution = {0: 1.0}
    observed = 0
    strata = []
    for wrapper in ("NONE", "q"):
        z = [x for x in rows if x["base"] == base and x["wrapper"] == wrapper]
        nt = sum(x["side"] == "TARGET" for x in z)
        nc = len(z) - nt
        na = sum(x["suffix"] == "air" for x in z)
        obs = sum(x["side"] == "TARGET" and x["suffix"] == "air" for x in z)
        observed += obs
        strata.append({"wrapper": wrapper, "target_n": nt, "control_n": nc, "air_n": na, "observed_target_air": obs})
        next_dist = defaultdict(float)
        lo = max(0, na - nc)
        hi = min(nt, na)
        for old, oldp in distribution.items():
            for x in range(lo, hi + 1):
                p = math.comb(nt, x) * math.comb(nc, na - x) / math.comb(nt + nc, na)
                next_dist[old + x] += oldp * p
        distribution = dict(next_dist)
    p_obs = distribution[observed]
    p_two = sum(p for p in distribution.values() if p <= p_obs + 1e-15)
    return observed, p_two, strata


def table(rows, predicate):
    z = [x for x in rows if predicate(x)]
    a = sum(x["side"] == "TARGET" and x["suffix"] == "air" for x in z)
    b = sum(x["side"] == "TARGET" and x["suffix"] != "air" for x in z)
    c = sum(x["side"] == "CONTROL" and x["suffix"] == "air" for x in z)
    d = sum(x["side"] == "CONTROL" and x["suffix"] != "air" for x in z)
    odds = (a * d) / (b * c) if b and c else None
    return {"target_air": a, "target_other": b, "control_air": c, "control_other": d,
            "odds_ratio": odds, "fisher_p": fisher_two_sided(a, b, c, d)}


def log_odds_interaction(ok, nonok):
    values = [ok[k] for k in ("target_air", "target_other", "control_air", "control_other")]
    other = [nonok[k] for k in ("target_air", "target_other", "control_air", "control_other")]
    assert all(x > 0 for x in values + other)
    log_ok = math.log(ok["odds_ratio"])
    log_other = math.log(nonok["odds_ratio"])
    se = math.sqrt(sum(1 / x for x in values + other))
    z = (log_ok - log_other) / se
    p = math.erfc(abs(z) / math.sqrt(2))
    return {"log_odds_ratio_difference": log_ok - log_other, "z": z, "two_sided_p": p}


def main():
    rows = []
    for row in read(SOURCE):
        if row["locus"].startswith("f84r"):
            continue
        rr = register(row)
        if rr not in TARGET | CONTROL:
            continue
        if row["dy_closure"] != "0" or row["residual_host"].endswith("m"):
            continue
        if row["stripped_prefix"] not in {"NONE", "q"}:
            continue
        parsed = split_host(row["residual_host"])
        if not parsed:
            continue
        base, suffix = parsed
        rows.append({
            "locus": row["locus"], "physical_folio": row["physical_folio"],
            "register": rr, "side": "TARGET" if rr in TARGET else "CONTROL",
            "token": row["token"], "wrapper": row["stripped_prefix"],
            "residual_host": row["residual_host"], "base": base, "suffix": suffix,
        })
    assert not any(x["locus"].startswith("f84r") for x in rows)

    ok = table(rows, lambda x: x["base"] == "ok")
    nonok = table(rows, lambda x: x["base"] != "ok")
    overall = table(rows, lambda x: True)
    observed_stratified, stratified_p, strata = exact_stratified(rows, "ok")
    interaction = log_odds_interaction(ok, nonok)

    base_rows = []
    for base in sorted({x["base"] for x in rows}):
        z = [x for x in rows if x["base"] == base]
        t = table(rows, lambda x, b=base: x["base"] == b)
        target_air_folios = len({x["physical_folio"] for x in z if x["side"] == "TARGET" and x["suffix"] == "air"})
        base_rows.append({
            "base": base, **{k: t[k] for k in ("target_air", "target_other", "control_air", "control_other")},
            "total": len(z), "target_air_folios": target_air_folios,
            "odds_ratio": "INF" if t["odds_ratio"] is None else f'{t["odds_ratio"]:.9f}',
            "fisher_p": f'{t["fisher_p"]:.12g}',
        })
    base_rows.sort(key=lambda x: (-x["target_air"], -x["target_air_folios"], -x["total"], x["base"]))
    write(BY_BASE, base_rows, list(base_rows[0]))

    air_rows = [x for x in rows if x["suffix"] == "air"]
    air_rows.sort(key=lambda x: (x["side"], x["register"], x["physical_folio"], x["locus"], x["token"]))
    write(OCC, air_rows, list(air_rows[0]))

    target_air_folios = sorted({x["physical_folio"] for x in rows if x["side"] == "TARGET" and x["suffix"] == "air"})
    lofo = []
    for folio in target_air_folios:
        z = [x for x in rows if x["physical_folio"] != folio]
        t = table(z, lambda x: True)
        target_rate = (t["target_air"] + 0.5) / (t["target_air"] + t["target_other"] + 1)
        control_rate = (t["control_air"] + 0.5) / (t["control_air"] + t["control_other"] + 1)
        lofo.append({"physical_folio": folio, "log2_rate_ratio": math.log2(target_rate / control_rate)})

    recurrent_bases = [x for x in base_rows if x["target_air"] > 0]
    decision = "AIR_IS_BS_ENRICHED_RIGHT_FAMILY_NOT_OK_SPECIFIC"
    assert ok["fisher_p"] < 0.05 and nonok["fisher_p"] < 0.05
    assert interaction["two_sided_p"] > 0.05
    assert min(x["log2_rate_ratio"] for x in lofo) > 0

    report = f"""# GDT048 — AIR right-family selection

## Outcome

**{decision}**

`OKAIR` is a real distributional lead, but the evidence does not isolate the
whole host. Within base `OK`, AIR occurs {ok['target_air']} times in Herbal-B
plus Stars/Recipe B versus {ok['control_air']} in Herbal-A plus other-B; the
matched non-AIR counts are {ok['target_other']} and {ok['control_other']}.
The exact odds ratio is {ok['odds_ratio']:.3f} (two-sided Fisher
`p={ok['fisher_p']:.6g}`). The result remains under exact `q`/bare-wrapper
stratification (`p={stratified_p:.6g}`).

But AIR is also enriched away from `OK`: {nonok['target_air']}/{nonok['target_air'] + nonok['target_other']}
target groups versus {nonok['control_air']}/{nonok['control_air'] + nonok['control_other']}
controls, odds ratio {nonok['odds_ratio']:.3f}, `p={nonok['fisher_p']:.6g}`.
The OK-specific log-odds interaction is not distinguishable from that broader
effect (`z={interaction['z']:.3f}`, `p={interaction['two_sided_p']:.3f}`). AIR
appears on {len(recurrent_bases)} distinct target bases, and the overall AIR
enrichment stays positive after deleting every target folio (minimum log2 rate
ratio {min(x['log2_rate_ratio'] for x in lofo):+.3f}).

The better theory is therefore a reusable right-family selection: Currier-B's
Herbal-B and Stars/Recipe registers select AIR more often than the matched
right edges AIN/AIIN/AR/AL. `OKAIR` is one especially clean instance, not yet
an independently privileged content stem. This advances the formal grammar
but does not identify AIR as a linguistic suffix or give it a function or
meaning.

No exact `OKAIR` occurrence is present in the human label atlas, and GDT047's
visual grounding failure remains. f84r was skipped before host parsing and was
not opened, retained, queried, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")

    result = {
        "schema": "GDT048_AIR_RIGHT_FAMILY_SELECTION_RESULT_V1",
        "status": decision,
        "eligible_groups": len(rows),
        "right_family": list(SUFFIXES),
        "ok_table": ok,
        "nonok_table": nonok,
        "overall_table": overall,
        "ok_wrapper_stratified": {"observed_target_air": observed_stratified, "two_sided_p": stratified_p, "strata": strata},
        "ok_vs_nonok_interaction": interaction,
        "target_air_bases": len(recurrent_bases),
        "target_air_folios": len(target_air_folios),
        "lofo_min_log2_rate_ratio": min(x["log2_rate_ratio"] for x in lofo),
        "lofo": lofo,
        "claim_ceiling": "Reusable source-formal right-family selection only; no morpheme, function, word, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False},
        "inputs": {SOURCE.name: sha(SOURCE), "gdt047_result.json": sha(ROOT / "gdt047_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {BY_BASE.name: sha(BY_BASE), OCC.name: sha(OCC)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": decision, "groups": len(rows), "ok": ok, "nonok": nonok, "interaction_p": interaction["two_sided_p"]}, sort_keys=True))


if __name__ == "__main__":
    main()
