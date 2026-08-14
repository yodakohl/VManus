#!/usr/bin/env python3
"""Independent held-folio reconstruction of GDT018."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT/"gdt018_result.json"
VALIDATION = ROOT/"gdt018_validation.json"
ALPHA = .5


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode()).hexdigest()


def read(name):
    with (ROOT/name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def context(event, model):
    if model == "POSITION":
        return (event["position_bin"],)
    if model == "POSITION_PLUS_DY":
        return (event["position_bin"], event["previous_dy"])
    if model == "POSITION_PLUS_PREVIOUS_STATE":
        return (event["position_bin"], event["previous_state"])
    return (event["previous_state"],)


def score(training, testing, model, alphabet_size):
    counts = defaultdict(Counter)
    totals = Counter()
    for event in training:
        key = context(event, model)
        counts[key][event["next_state"]] += 1
        totals[key] += 1
    bits = 0.0
    for event in testing:
        key = context(event, model)
        bits -= math.log2((counts[key][event["next_state"]]+ALPHA)
                          /(totals[key]+ALPHA*alphabet_size))
    return bits


def js(left, right):
    keys = set(left)|set(right)
    nl = sum(left.values())
    nr = sum(right.values())
    value = 0.0
    for key in keys:
        p = left[key]/nl
        q = right[key]/nr
        midpoint = (p+q)/2
        if p:
            value += .5*p*math.log2(p/midpoint)
        if q:
            value += .5*q*math.log2(q/midpoint)
    return value


def close(a, b, tolerance=7e-10):
    return abs(float(a)-float(b)) <= tolerance


def main():
    checks = []
    result = json.loads(RESULT.read_text())
    copy = dict(result)
    digest = copy.pop("result_content_sha256")
    checks += [("schema", result["schema"] == "GDT018_DY_BOUNDARY_FUNCTION_RESULT_V1"),
               ("content", digest == csha(copy))]
    for part in ("inputs", "implementation", "outputs"):
        for name, expected in result[part].items():
            checks.append((part+":"+name, sha(ROOT/name) == expected))
    inventory = read("gdt016_group_state_inventory.tsv")
    checks += [("input_count", len(inventory) == result["groups"] == 15592),
               ("hard_f84_guard", not any(row["locus"].startswith("f84r") for row in inventory))]
    grouped = defaultdict(list)
    for row in inventory:
        grouped[row["locus"]].append(row)
    lines = []
    events = []
    starts = Counter()
    post = Counter()
    internal = Counter()
    for locus, line in sorted(grouped.items()):
        line.sort(key=lambda row:int(row["group_index"]))
        lines.append(line)
        starts[line[0]["record_state"]] += 1
        for index in range(1, len(line)):
            current = line[index]
            previous = line[index-1]
            position = ((int(current["group_index"])-1)/(int(current["group_count"])-1)
                        if int(current["group_count"]) > 1 else .5)
            event = {"physical_folio":current["physical_folio"],
                     "position_bin":min(3,int(position*4)),
                     "previous_state":previous["record_state"],
                     "previous_dy":int(previous["record_state"]=="DY_RESOLUTION"),
                     "next_state":current["record_state"]}
            events.append(event)
            (post if event["previous_dy"] else internal)[event["next_state"]] += 1
    alphabet = sorted({row["record_state"] for row in inventory})
    folios = sorted({row["physical_folio"] for row in inventory})
    checks += [("lines", len(lines)==result["lines"]==2471),
               ("folios", len(folios)==result["physical_folios"]==94),
               ("boundaries", len(events)==result["internal_boundaries"]==13121),
               ("post_dy", sum(post.values())==result["post_dy_boundaries"]==2344)]
    models = ("POSITION", "POSITION_PLUS_DY", "POSITION_PLUS_PREVIOUS_STATE", "PREVIOUS_STATE")
    totals = Counter()
    positive_dy = positive_reset = 0
    reset_total = 0.0
    stored_folds = {row["held_folio"]:row for row in read("gdt018_heldout_boundary_models.tsv")}
    for held in folios:
        training = [event for event in events if event["physical_folio"] != held]
        testing = [event for event in events if event["physical_folio"] == held]
        scores = {model:score(training, testing, model, len(alphabet)) for model in models}
        for model, value in scores.items():
            totals[model] += value
        gain = scores["POSITION"]-scores["POSITION_PLUS_DY"]
        positive_dy += gain>0
        training_lines = [line for line in lines if line[0]["physical_folio"] != held]
        start_counts = Counter(line[0]["record_state"] for line in training_lines)
        internal_counts = Counter()
        for line in training_lines:
            for index in range(1,len(line)):
                if line[index-1]["record_state"]!="DY_RESOLUTION":
                    internal_counts[line[index]["record_state"]]+=1
        ns=sum(start_counts.values());ni=sum(internal_counts.values());llr=0.0;npost=0
        for event in testing:
            if event["previous_dy"]:
                value=event["next_state"]
                llr+=math.log2((start_counts[value]+ALPHA)/(ns+ALPHA*len(alphabet)))-math.log2((internal_counts[value]+ALPHA)/(ni+ALPHA*len(alphabet)))
                npost+=1
        reset_total+=llr;positive_reset+=llr>0
        stored=stored_folds[held]
        checks.append(("fold:"+held,
            int(stored["held_internal_boundaries"])==len(testing)
            and int(stored["held_post_dy_boundaries"])==npost
            and close(stored["position_bits"],scores["POSITION"])
            and close(stored["position_plus_dy_bits"],scores["POSITION_PLUS_DY"])
            and close(stored["position_plus_previous_state_bits"],scores["POSITION_PLUS_PREVIOUS_STATE"])
            and close(stored["previous_state_bits"],scores["PREVIOUS_STATE"])
            and close(stored["post_dy_start_vs_internal_log2_likelihood"],llr)))
    dy_gain=totals["POSITION"]-totals["POSITION_PLUS_DY"]
    full_gain=totals["POSITION"]-totals["POSITION_PLUS_PREVIOUS_STATE"]
    extra=(8-4)*(len(alphabet)-1)
    bic=extra/2*math.log2(len(events))
    checks += [("model_bits", all(close(totals[name],result["model_bits"][name]) for name in models)),
               ("dy_gain",close(dy_gain,result["dy_gain_vs_position"])),
               ("gain_fraction",close(dy_gain/full_gain,result["dy_fraction_of_full_previous_state_gain"])),
               ("positive_dy_folds",positive_dy==result["positive_dy_gain_folios"]==80),
               ("bic",extra==result["bic_extra_parameters"]==56 and close(bic,result["bic_penalty_bits"]) and close(dy_gain-bic,result["bic_net_gain_bits"])),
               ("reset",close(reset_total,result["post_dy_start_vs_internal_log2_likelihood"]) and positive_reset==result["positive_local_reset_folios"]==25),
               ("js",close(js(post,starts),result["js_post_dy_vs_start"]) and close(js(internal,starts),result["js_non_dy_internal_vs_start"]))]
    stored_profiles={row["state"]:row for row in read("gdt018_next_state_profiles.tsv")}
    checks.append(("profiles",all(int(stored_profiles[state]["line_start_count"])==starts[state]
                                  and int(stored_profiles[state]["post_dy_count"])==post[state]
                                  and int(stored_profiles[state]["non_dy_internal_count"])==internal[state]
                                  for state in alphabet)))
    checks += [("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT018_CKPT001")==1),
               ("f84_flags",result["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False})]
    report=(ROOT/"GDT018_DY_BOUNDARY_FUNCTION_REPORT.md").read_text().lower()
    checks.append(("claims",all(value in report for value in ("not a miniature line reset","internal resolution","no morpheme","f84r was absent"))))
    failures=[name for name,ok in checks if not ok]
    validation={"schema":"GDT018_DY_BOUNDARY_FUNCTION_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction from the frozen f84r-free GDT016 inventory of 94 held-folio model comparisons, local-reset likelihood ratios, profiles, JS distances, penalties, hashes, ledger, and claims."}
    VALIDATION.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n")
    print(json.dumps(validation,sort_keys=True))
    if failures:raise SystemExit(1)


if __name__=="__main__":main()
