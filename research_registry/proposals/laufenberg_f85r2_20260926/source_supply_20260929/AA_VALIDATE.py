#!/usr/bin/env python3
"""Integrity checks for owned copied contexts and documentation, not semantics."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
checks = []


def check(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


def read(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


packet = read("AA_COMPLETE_UNITS.json")
rows = packet["records"]
with (BASE / "O_COMPLETE_UNITS.tsv").open(encoding="utf-8", newline="") as handle:
    original_o = list(csv.DictReader(handle, delimiter="\t"))
with (BASE / "Q_COMPLETE_UNITS.tsv").open(encoding="utf-8", newline="") as handle:
    original_q = [r for r in csv.DictReader(handle, delimiter="\t") if r["unit"] == "f29v.1-4"]
check("all O original rows retained", [r["original_row"] for r in rows if r["unit"] != "f29v.1-4"] == original_o)
check("all owned f29v original rows retained", [r["original_row"] for r in rows if r["unit"] == "f29v.1-4"] == original_q)
for r in rows:
    o = r["original_row"]
    words = json.loads(o["groups_json"]) if r["unit"] == "f29v.1-4" else o["raw_groups"].split()
    check("exact copied words " + r["reader"] + " " + r["locus"], r["words"] == words)
counts = Counter()
for r in rows:
    counts[(r["unit"], r["reader"])] += len(r["words"])
expected = {("f22r.4-6", "ZL3b"): 22, ("f22r.4-6", "IT2a"): 22, ("f22r.4-6", "RF1b"): 21, ("f32r.1-5", "ZL3b"): 31, ("f32r.1-5", "IT2a"): 31, ("f32r.1-5", "RF1b"): 31, ("f29v.1-4", "ZL3b"): 40, ("f29v.1-4", "IT2a"): 39, ("f29v.1-4", "RF1b"): 40}
check("all nine complete record counts", counts == expected)
check("277 total positions", sum(counts.values()) == 277)
selected = {"chor", "chol", "schor", "schol", "s"}
contacts = []
for r in rows:
    for n, word in enumerate(r["words"], 1):
        if word in selected:
            contacts.append({"unit": r["unit"], "reader": r["reader"], "locus": r["locus"], "group": str(n), "word": word, "right_group": r["words"][n] if n < len(r["words"]) else "", "whole_line": " ".join(r["words"])})
with (BASE / "AA_WRITTEN_CONTACTS.tsv").open(encoding="utf-8", newline="") as handle:
    saved = list(csv.DictReader(handle, delimiter="\t"))
check("all selected written occurrences retained", contacts == saved)
check("34 selected positions and243 unassigned", len(contacts) == 34 and sum(counts.values()) - len(contacts) == 243)
check("all seven literal free s", sum(r["word"] == "s" for r in contacts) == 7)
check("one schol is IT f29v2", [(r["reader"], r["locus"]) for r in contacts if r["word"] == "schol"] == [("IT2a", "f29v.2")])
check("six schor positions are two loci three readings", Counter(r["locus"] for r in contacts if r["word"] == "schor") == {"f22r.4": 3, "f32r.4": 3})
check("three unit scope only", set(r["unit"] for r in rows) == set(packet["units"]))
card = read("AA_01_NAMED_MATERIAL_PORTION.json")
check("explicit raw unreviewed status", card["status"] == "RAW_UNREVIEWED_NOT_SELECTED_NOT_TESTED")
check("one new782 receipt", read("AA_ADD_RECEIPT.json")["id"] == "IDEA000782")
correction = (BASE / "AA_BOUNDARY_CORRECTION.md").read_text(encoding="utf-8")
check("physical-line versus paragraph correction retained", "physical line ends" in correction and "not established missing-right-argument cases" in correction)
for receipt in read("AA_INPUTS.json")["fixed_inputs"]:
    check("source hash " + receipt["path"], hashlib.sha256((ROOT / receipt["path"]).read_bytes()).hexdigest() == receipt["sha256"])
result = {"status": "PASS" if all(c["pass"] for c in checks) else "FAIL", "kind": "DOCUMENT_INTEGRITY_ONLY_NO_SEMANTIC_TEST", "check_count": len(checks), "checks": checks}
(BASE / "AA_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "kind": result["kind"], "check_count": result["check_count"]}))
raise SystemExit(0 if result["status"] == "PASS" else 1)
