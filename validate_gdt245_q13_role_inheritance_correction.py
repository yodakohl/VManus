#!/usr/bin/env python3
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
checks = []
def ck(x): checks.append(bool(x)); assert x
def sha(p): return hashlib.sha256((R / p).read_bytes()).hexdigest()

z = json.loads((R / "gdt245_result.json").read_text())
for kind in ("inputs", "outputs", "documents", "implementation"):
    for p, h in z[kind].items(): ck(sha(p) == h)
rows = list(csv.DictReader((R / "gdt245_q13_role_artifact_status.tsv").open(), delimiter="\t"))
ck(len(rows) == 14)
ck(len({(r["source_experiment"], r["artifact_or_claim"], r["layer"]) for r in rows}) == 14)
ck(sum(r["current_state"].startswith("SUSPENDED") for r in rows) == 6)
ck(sum(r["current_state"] == "WITHDRAWN_F82R" for r in rows) == 1)
ck(sum(r["current_state"] == "RETAINED" for r in rows) == 3)
ck(any(r["source_experiment"] == "GDT229" and r["current_state"] == "ARCHIVED_HYPOTHESIS_NOT_ACTIVE_INTERLINEAR" for r in rows))
ck(any(r["source_experiment"] == "GDT236" and r["current_state"] == "RETAINED_WITH_ROLE_LAYER_REMOVED" for r in rows))
ck(all(r["permitted_use"] and r["reason"] and r["surviving_content"] for r in rows))
c82 = json.loads((R / "gdt242_result.json").read_text())
c80 = json.loads((R / "gdt244_result.json").read_text())
ck(c82["source_paragraphs"] == 3 and len(c82["historical_gdt229_record_ids"]) == 1)
ck(c80["source_paragraphs"] == 5 and len(c80["historical_records"]) == 2)
ck(z["active_semantic_assignments"] == 0)
ck(z["status"] == "Q13_ROLE_LAYER_SUSPENDED_FORMAL_COMPILER_AND_LABEL_RENDERER_RETAINED")
ck(z["f84"] == {"input": False, "joined": False, "new_access": False, "retained": False, "scored": False})
core = dict(z); got = core.pop("content_hash")
ck(hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == got)
out = {"experiment": z["experiment"], "status": "PASS", "checks_passed": len(checks), "checks_total": len(checks), "result_hash": sha("gdt245_result.json")}
(R / "gdt245_validation.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(f"PASS {len(checks)}/{len(checks)}")
