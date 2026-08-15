#!/usr/bin/env python3
"""Independent integrity/capacity validation of the GDT136 freeze."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREDICTION = ROOT / "gdt136_prediction.json"
CAPACITY = ROOT / "gdt136_capacity.tsv"
TARGETS = ROOT / "gdt109_target_inventory.tsv"
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
PROSE = ROOT / "gdt016_group_state_inventory.tsv"
OUT = ROOT / "gdt136_prediction_validation.json"
PREFIXES = ("che", "ch", "sh", "t", "s", "d", "q")
RIGHT = ("aiin", "air", "ain", "ar", "al")


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def split_host(token):
    wrapper, host = "NONE", token
    for prefix in PREFIXES:
        if host.startswith(prefix) and len(host) > len(prefix): wrapper, host = prefix, host[len(prefix):]; break
    if host.endswith("dy") and len(host) > 2: host = host[:-2]
    return wrapper, host


def base_host(wrapper, host):
    if host.endswith("m") and len(host) > 1: host = host[:-1]
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix): host = host[:-len(suffix)]; break
    if wrapper in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1: host = host[1:]
    return host


checks = []
def check(name, value):
    checks.append({"check": name, "pass": bool(value)}); assert value, name


prediction = json.loads(PREDICTION.read_text())
check("status", prediction["status"] == "FROZEN_POSTHOC_CROSS_PANEL_BEFORE_DESCRIPTOR_SCORING")
prose = [row for row in read(PROSE) if not row["page"].startswith("f84")]
counts = Counter(base_host(row["stripped_prefix"], row["residual_host"]) for row in prose)
licensed = {host for host in counts if counts[host] and counts["o" + host] and counts["ot" + host]} | {"ar", "al", "ol"}

def parse(token):
    wrapper, host = split_host(token); host = base_host(wrapper, host)
    if host.startswith("ot") and host[2:] in licensed: host = host[2:]
    elif host.startswith("o") and host[1:] in licensed: host = host[1:]
    return host or "EMPTY"

host_folios = defaultdict(set); source_count = 0
for row in read(SOURCE):
    if row["page"].startswith("f84"): continue
    source_count += 1; host_folios[row["page_host"]].add(row["physical_folio"])
targets = read(TARGETS); rebuilt = []
for row in targets:
    flags1=[]; flags2=[]
    for column in ("zl3b_forms", "it2a_forms", "rf1b_forms"):
        available=[len(host_folios[parse(token)]-{row["physical_folio"]}) for token in row[column].split("|")]
        flags1.append(all(value >= 1 for value in available)); flags2.append(all(value >= 2 for value in available))
    rebuilt.append((row["locus"], row["physical_folio"], tuple(flags1), tuple(flags2)))
stored = {row["locus"]: row for row in read(CAPACITY)}
check("44_unique_targets", len(targets) == len(stored) == len({row["locus"] for row in targets}) == 44)
check("source_count", source_count == prediction["capacity"]["source_rows_after_all_f84_exclusion"] == 15364)
check("no_f84_target", not any(row["page"].startswith("f84") for row in targets))
for locus, folio, flags1, flags2 in rebuilt:
    row=stored[locus]
    check("capacity_"+locus, row["physical_folio"] == folio and tuple(int(row[x]) for x in ("zl_profileable_ge1","it_profileable_ge1","rf_profileable_ge1")) == tuple(map(int,flags1)) and int(row["profileable_editions_ge2"]) == sum(flags2) and row["descriptor_outcome_retained_or_scored"] == "0")
primary=[x for x in rebuilt if any(x[2])]; stronger=[x for x in rebuilt if any(x[3])]; all_three=[x for x in rebuilt if all(x[2])]
check("primary_capacity", len(primary)==31 and len({x[1] for x in primary})==6)
check("stronger_capacity", len(stronger)==27 and len({x[1] for x in stronger})==6)
check("all_readings_capacity", len(all_three)==15 and len({x[1] for x in all_three})==5)
check("models", prediction["primary_representation"] == "BEHAVIOR_SELF_NEIGHBOR_NOPOS" and prediction["comparators"] == ["PAGE_HOST_CHAR3", "RAW_CHAR3"])
check("hashes", all(sha(ROOT / name) == digest for name,digest in prediction["inputs"].items()) and all(sha(ROOT/name)==digest for name,digest in prediction["implementation"].items()) and all(sha(ROOT/name)==digest for name,digest in prediction["outputs"].items()))
content=dict(prediction); digest=content.pop("prediction_content_sha256"); check("content", csha(content)==digest)
validation={"schema":"GDT136_PREDICTION_VALIDATION_V1","status":"PASS_SCORE_BLIND_CAPACITY_FREEZE","checks":len(checks),"passed":sum(x["pass"] for x in checks),"prediction_sha256":sha(PREDICTION),"validator_sha256":sha(Path(__file__)),"check_rows":checks}
OUT.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps({"status":validation["status"],"checks":validation["checks"]},sort_keys=True))
