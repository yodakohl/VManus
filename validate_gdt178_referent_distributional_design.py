#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
d=json.loads(Path("gdt178_design.json").read_text());c=list(csv.DictReader(open("gdt169_external_referent_candidates.tsv"),delimiter="\t"));s=list(csv.DictReader(open("gdt062_right_family_inventory.tsv"),delimiter="\t"));checks=[d["status"]=="FROZEN_BEFORE_FULL_ATLAS_DISTRIBUTIONAL_SCORING",len(c)==40,all(not x["source_page"].startswith("f84") and not x["target_page"].startswith("f84") for x in c),all(not x["page"].startswith("f84r") for x in s),d["representations"]==["HOST_EXACT","HOST_CHAR2","HOST_CHAR3","RAW_CHAR3","HOST_LENGTH"],all(sha(p)==h for p,h in d["inputs"].items()),not d["f84r_accessed"]]
clean=dict(d);e=clean.pop("content_hash");checks.append(hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(",",":")).encode()).hexdigest()==e)
v={"experiment":d["experiment"],"status":"PASS" if all(checks) else "FAIL","checks_passed":sum(checks),"checks_total":len(checks),"design_sha256":sha("gdt178_design.json")};Path("gdt178_design_validation.json").write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(v["status"],f"{v['checks_passed']}/{v['checks_total']}")
if not all(checks):raise SystemExit(1)
