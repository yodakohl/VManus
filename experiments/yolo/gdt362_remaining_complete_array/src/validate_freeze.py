#!/usr/bin/env python3
from __future__ import annotations
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import sha256_file  # noqa:E402
BASE=ROOT/"experiments/yolo/gdt362_remaining_complete_array"
def main():
 d=json.loads((BASE/"artifacts/gdt362_freeze.json").read_text())
 with (BASE/"artifacts/gdt362_selection.tsv").open(encoding="utf-8",newline="") as f: rows=list(csv.DictReader(f,delimiter="\t"))
 c=[]
 c += [len(rows)==9,[r["locus"] for r in rows]==[f"f101v2.{i}" for i in range(10,19)]]
 c += [all(r["physical_folio"]=="f101" for r in rows),all(r["visual_state"]=="SEALED_PENDING_DIRECT_REVIEW" for r in rows)]
 c += [all(not r["page"].startswith("f84") for r in rows),d["selection"]["canvas_id"]=="1006250"]
 c += [d["prediction"]["predicate"]=="FIRST_GROUP_PREFIX_2:AQ",d["access"]["target_image_reviewed"] is False,d["access"]["f84_accessed"] is False]
 for rel,h in d["inputs"].items(): c.append(sha256_file(ROOT/rel)==h)
 for rel,h in d["outputs"].items(): c.append(sha256_file(ROOT/rel)==h)
 if not all(c): raise SystemExit("FAIL")
 print(f"PASS {sum(c)}/{len(c)}")
if __name__=="__main__":main()
