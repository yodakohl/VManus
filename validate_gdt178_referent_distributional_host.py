#!/usr/bin/env python3
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
def read(p):
    with Path(p).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def near(a,b,t=2e-7):return abs(a-b)<=t*max(1,abs(a),abs(b))
r=json.loads(Path("gdt178_result.json").read_text());pairs=read("gdt178_pair_scores.tsv");summary=read("gdt178_summary.tsv");null=read("gdt178_null.tsv");dele=read("gdt178_deletions.tsv");local=read("gdt178_local_queries.tsv");cand=read("gdt169_external_referent_candidates.tsv");source=read("gdt062_right_family_inventory.tsv");checks=[]
checks.append(("status",r["status"]=="FULL_ATLAS_DISTRIBUTIONAL_HOST_PROFILE_NOT_SUPPORTED"))
checks.append(("counts",len(cand)==40 and len(pairs)==r["scored_pairs"]==38 and len(local)==5))
checks.append(("no_f84",all(not x["source_page"].startswith("f84") and not x["target_page"].startswith("f84") for x in cand) and all(not x["page"].startswith("f84r") for x in source)))
reps=[x["representation"] for x in null];checks.append(("representations",reps==["HOST_EXACT","HOST_CHAR2","HOST_CHAR3","RAW_CHAR3","HOST_LENGTH"]))
allrow=next(x for x in summary if x["subset"]=="ALL")
checks.append(("summary",all(near(float(allrow[f"{rep.lower()}_mean_z"]),r["summary"][rep]["mean_z"]) for rep in reps)))
checks.append(("null",all(int(x["worlds"])==20000 and near(float(x["max5_p"]),r["summary"][x["representation"]]["max5_p"]) for x in null)))
checks.append(("all_negative",all(r["summary"][rep]["mean_z"]<0 for rep in reps)))
checks.append(("local",r["local_top_decile"]==sum(float(x["tail"])<=.1 for x in local)==0))
by=defaultdict(list)
for x in dele:by[x["representation"]].append(float(x["mean_z"]))
checks.append(("deletions",all(len(by[rep])==78 for rep in reps) and sum(v>0 for v in by["HOST_CHAR3"])==1))
checks.append(("hashes",all(sha(p)==h for p,h in {**r["inputs"],**r["outputs"],**r["implementation"]}.items())))
clean=dict(r);e=clean.pop("content_hash");checks.append(("content",hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(",",":")).encode()).hexdigest()==e))
checks.append(("claim",not r["f84r_accessed"] and "no plant identity" in r["claim_ceiling"]))
failed=[n for n,o in checks if not o];v={"experiment":r["experiment"],"status":"PASS" if not failed else "FAIL","checks_passed":sum(o for _,o in checks),"checks_total":len(checks),"failed":failed,"result_sha256":sha("gdt178_result.json"),"report_sha256":sha("GDT178_REFERENT_DISTRIBUTIONAL_HOST_REPORT.md"),"counterexamples_sha256":sha("gdt178_counterexamples.tsv"),"scope":"retained-pair summaries, null/deletion accounting, hashes, f84 exclusion and claim validation; scorer is not imported"};Path("gdt178_validation.json").write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(v["status"],f"{v['checks_passed']}/{v['checks_total']}",failed)
if failed:raise SystemExit(1)
