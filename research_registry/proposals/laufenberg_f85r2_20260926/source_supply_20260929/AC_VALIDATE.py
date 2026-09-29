#!/usr/bin/env python3
"""Integrity checks of an existing packet and bounded no-card report only."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
checks = []


def check(name, value):
    checks.append({"name": name, "pass": bool(value)})


receipt = json.loads((BASE / "AC_INPUTS.json").read_text())
for item in receipt["inputs"]:
    check("source hash " + item["path"], hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"])
source = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv"
check("byte-identical owned473-group projection", source.read_bytes() == (BASE / "AC_COMPLETE_GROUPS.tsv").read_bytes())
with (BASE / "AC_COMPLETE_GROUPS.tsv").open(newline="") as f:
    rows = list(csv.DictReader(f, delimiter="\t"))
check("473 groups", len(rows) == 473)
check("all24 loci", len({r["locus"] for r in rows}) == 24)
check("all72 reader/locus units", len({(r["edition"], r["locus"]) for r in rows}) == 72)
check("no other target selector", all(r["locus"].startswith("f85r2.") for r in rows))
check("all reader totals", Counter(r["edition"] for r in rows) == {"ZL3b": 156, "IT2a": 157, "RF1b": 160})
check("whole four-block plus outside partitions", Counter(r["block"] for r in rows) == {"N": 57, "E": 81, "S": 78, "W": 108, "OUTSIDE": 149})
for reader in ("ZL3b", "IT2a", "RF1b"):
    for locus, exact in (("f85r2.4", "dair sheo oraiin chol daiin"), ("f85r2.23", "ol lcheol chol ol sheoly")):
        rr = [r for r in rows if r["edition"] == reader and r["locus"] == locus]
        check("exact retained whole line " + reader + " " + locus, " ".join(r["ivtff_group_raw"] for r in rr) == exact)
comparison = json.loads((BASE / "AC_CANDIDATE_COMPARISON.json").read_text())
check("no-card no-selection status", comparison["status"] == "NO_NEW_CARD_NO_SELECTION_EXISTING_RAW_RETAINED")
check("no registry mutation", receipt["registry_mutations"] == 0)
result = {"status": "PASS" if all(x["pass"] for x in checks) else "FAIL", "kind": "DOCUMENT_INTEGRITY_ONLY_NO_SEMANTIC_TEST", "check_count": len(checks), "checks": checks}
(BASE / "AC_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ("status", "kind", "check_count")}))
raise SystemExit(0 if result["status"] == "PASS" else 1)
