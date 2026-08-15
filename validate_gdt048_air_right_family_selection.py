#!/usr/bin/env python3
"""Independent reconstruction for GDT048."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
RESULT = ROOT / "gdt048_result.json"
OUT = ROOT / "gdt048_validation.json"
SUFFIXES = ("aiin", "air", "ain", "ar", "al")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def register(row):
    if row["section"] == "H" and row["currier"] == "A": return "HA"
    if row["section"] == "H" and row["currier"] == "B": return "HB"
    if row["section"] == "S" and row["currier"] == "B": return "SB"
    if row["currier"] == "B": return "OB"
    return "OUT"


def split_host(host):
    for suffix in SUFFIXES:
        if host.endswith(suffix) and len(host) > len(suffix):
            return host[:-len(suffix)], suffix
    return None


def table(rows, scope):
    c = Counter()
    for row in rows:
        if not scope(row): continue
        c[(row["side"], row["suffix"] == "air")] += 1
    return [c[("TARGET", True)], c[("TARGET", False)], c[("CONTROL", True)], c[("CONTROL", False)]]


def approx(a, b, tol=1e-12):
    return abs(a - b) <= tol


checks = []
def check(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


def main():
    result = json.loads(RESULT.read_text())
    rows = []
    for source in read(SOURCE):
        if source["locus"].startswith("f84r"): continue
        rr = register(source)
        if rr not in {"HA", "HB", "SB", "OB"}: continue
        if source["dy_closure"] != "0" or source["residual_host"].endswith("m"): continue
        if source["stripped_prefix"] not in {"NONE", "q"}: continue
        split = split_host(source["residual_host"])
        if not split: continue
        base, suffix = split
        rows.append({"locus": source["locus"], "folio": source["physical_folio"], "base": base, "suffix": suffix,
                     "side": "TARGET" if rr in {"HB", "SB"} else "CONTROL"})
    check("eligible_count", len(rows) == result["eligible_groups"])
    check("f84_absent", not any(x["locus"].startswith("f84r") for x in rows))
    for name, scope in (("ok", lambda x: x["base"] == "ok"), ("nonok", lambda x: x["base"] != "ok"), ("overall", lambda x: True)):
        values = table(rows, scope)
        stored = result[f"{name}_table"]
        check(f"{name}_table", values == [stored["target_air"], stored["target_other"], stored["control_air"], stored["control_other"]])
    ok = result["ok_table"]; non = result["nonok_table"]
    lor = math.log((ok["target_air"] * ok["control_other"]) / (ok["target_other"] * ok["control_air"]))
    lnr = math.log((non["target_air"] * non["control_other"]) / (non["target_other"] * non["control_air"]))
    se = math.sqrt(sum(1 / x for x in [ok["target_air"], ok["target_other"], ok["control_air"], ok["control_other"], non["target_air"], non["target_other"], non["control_air"], non["control_other"]]))
    z = (lor - lnr) / se
    check("interaction_reconstructed", approx(z, result["ok_vs_nonok_interaction"]["z"]))
    folios = {x["folio"] for x in rows if x["side"] == "TARGET" and x["suffix"] == "air"}
    check("target_air_folios", len(folios) == result["target_air_folios"])
    bases = {x["base"] for x in rows if x["side"] == "TARGET" and x["suffix"] == "air"}
    check("target_air_bases", len(bases) == result["target_air_bases"])
    lofo = []
    for folio in sorted(folios):
        a, b, c, d = table([x for x in rows if x["folio"] != folio], lambda x: True)
        lofo.append(math.log2(((a + .5) / (a + b + 1)) / ((c + .5) / (c + d + 1))))
    check("lofo_min", approx(min(lofo), result["lofo_min_log2_rate_ratio"]))
    for name, digest in result["inputs"].items(): check(f"input_hash:{name}", sha(ROOT / name) == digest)
    for name, digest in result["outputs"].items(): check(f"output_hash:{name}", sha(ROOT / name) == digest)
    for name, digest in result["documents"].items(): check(f"document_hash:{name}", sha(ROOT / name) == digest)
    for name, digest in result["implementation"].items(): check(f"implementation_hash:{name}", sha(ROOT / name) == digest)
    check("decision", result["status"] == "AIR_IS_BS_ENRICHED_RIGHT_FAMILY_NOT_OK_SPECIFIC")
    check("claim_ceiling", "no morpheme" in result["claim_ceiling"] and "meaning" in result["claim_ceiling"])
    check("f84_contract", not any(result["f84r"].values()))
    status = "PASS_INDEPENDENT_RECONSTRUCTION" if all(x["pass"] for x in checks) else "FAIL"
    payload = {"schema": "GDT048_VALIDATION_V1", "status": status, "checks_passed": sum(x["pass"] for x in checks), "checks_total": len(checks), "checks": checks, "result_sha256": sha(RESULT)}
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "checks": f'{payload["checks_passed"]}/{payload["checks_total"]}'}, sort_keys=True))
    raise SystemExit(0 if status.startswith("PASS") else 1)


if __name__ == "__main__":
    main()
