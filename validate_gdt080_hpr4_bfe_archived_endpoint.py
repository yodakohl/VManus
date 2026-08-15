#!/usr/bin/env python3
"""Independent reconstruction for GDT080."""
from __future__ import annotations
import csv, hashlib, itertools, json
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
VIS=ROOT/"gdt002_exploratory_visual_formal_join.tsv";PAR=ROOT/"gdt059_hpr2_external_inventory.tsv";RES=ROOT/"gdt080_result.json";JOIN=ROOT/"gdt080_hpr4_bfe_join.tsv";TEST=ROOT/"gdt080_hpr4_bfe_tests.tsv";COUNTER=ROOT/"gdt080_hpr4_bfe_counterexamples.tsv";LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";OUT=ROOT/"gdt080_validation.json"
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 r=json.loads(RES.read_text());v=[x for x in read(VIS)if x["channel"]=="BFE_ENCLOSURE"and not x["locus"].startswith("f84r")];p=defaultdict(list)
 for x in read(PAR):
  if not x["locus"].startswith("f84r"):p[x["locus"]].append(x)
 z=[]
 for x in v:
  q=p.get(x["locus"],[]);assert len(q)<=1
  if q:z.append((x,q[0],int(q[0]["page_host"] in {"d","ok","yk","yt"})))
 b=[x for x in z if x[0]["visual_state"]=="INDIVIDUAL_BOUNDED"];o=[x for x in z if x[0]["visual_state"]=="OPEN_OR_COMMUNAL"]
 eff=sum(x[2]for x in b)/len(b)-sum(x[2]for x in o)/len(o);m=[x for x in z if x[0]["page"]=="f82v"];obs=sum(x[2]for x in m if x[0]["visual_state"]=="INDIVIDUAL_BOUNDED")/3-sum(x[2]for x in m if x[0]["visual_state"]=="OPEN_OR_COMMUNAL")/2
 vals=[]
 for c in itertools.combinations(range(5),3):
  s=set(c);vals.append(sum(m[i][2]for i in s)/3-sum(m[i][2]for i in range(5)if i not in s)/2)
 checks={}
 checks["inventory"]=len(v)==30 and len(z)==20 and len(b)==12 and len(o)==8
 checks["hits"]=sum(x[2]for x in z)==3 and Counter(x[1]["page_host"]for x in z if x[2])=={"ok":3}
 checks["effects"]=abs(eff-r["pooled_bounded_minus_open_effect"])<1e-12 and abs(obs-r["f82v_within_page_effect"])<1e-12 and abs(sum(x>=obs-1e-12 for x in vals)/len(vals)-r["f82v_one_sided_exact_p"])<1e-12
 checks["tables"]=len(read(JOIN))==30 and len(read(TEST))==5 and len(read(COUNTER))==30
 checks["status"]=r["status"]=="HPR4_STABLE_HOST_CLASS_ARCHIVED_BFE_DIRECTION_FAILS_AND_IS_ONE_HOST_DRIVEN"
 checks["fresh_prediction_unconsumed"]=read(ROOT/"gdt078_hpr4_predictions.tsv")[0]["status"]=="FROZEN_NOT_RUN"
 checks["historical_stop"]=json.loads((ROOT/"experiments/semantic_assumptions/results/bfe001_bio_figure_enclosure_capacity.json").read_text())["status"]=="STOP_ONE_MIXED_FOLIO_PAGE_ECOLOGY_CONFOUND"
 checks["f84_seal"]=not any(r["f84r"].values()) and not any(x["locus"].startswith("f84r")for x in read(JOIN))
 body=dict(r);claimed=body.pop("result_content_sha256");checks["content_hash"]=csha(body)==claimed
 checks["hashes"]=all(sha(ROOT/name)==d for fam in("inputs","outputs","documents","implementation")for name,d in r[fam].items())
 q=[x for x in read(LEDGER)if x["checkpoint_id"]=="GDT080_CKPT001"];checks["ledger"]=len(q)==1 and q[0]["status"]==r["status"]
 passed=all(checks.values());out={"schema":"GDT080_HPR4_BFE_ARCHIVED_ENDPOINT_VALIDATION_V1","status":"PASS_INDEPENDENT_ARCHIVED_ENDPOINT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independently reconstructs non-f84 inventory, parse eligibility, class hits, pooled and f82v exact effects, historical stop, frozen prediction, hashes, seal and ledger."};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"checks":f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
