#!/usr/bin/env python3
"""Independent nonimporting validation of GDT028."""
from __future__ import annotations
import csv,hashlib,itertools,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt028_result.json";VAL=ROOT/"gdt028_validation.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def branch(f):
 if"QJB"in f or"QKB"in f:return"Q"
 if"LJB"in f or"LKB"in f:return"L"
 return"OTHER"
def main():
 checks=[];result=json.loads(RES.read_text());body=dict(result);digest=body.pop("result_content_sha256");checks +=[("schema",result["schema"]=="GDT028_Q_L_RIGHT_EDGE_FACTORIAL_RESULT_V1"),("content_hash",digest==csha(body)),("status",result["status"]=="Q_L_RIGHT_EDGE_FACTORIAL_COMPOSITION_NOT_DEMONSTRATED")]
 for section in("inputs","implementation","outputs"):
  for name,digest in result[section].items():checks.append((f"hash:{section}:{name}",sha(ROOT/name)==digest))
 inv=read("gdt016_group_state_inventory.tsv");checks +=[("inventory",len(inv)==result["inventory_groups"]==15592),("f84r_absent",not any(r["locus"].startswith("f84r")for r in inv))]
 cells=defaultdict(list)
 for row in inv:
  b=branch(row["family_surface"])
  if row["currier"]=="B"and b!="OTHER":cells[(row["residual_host"],b,row["record_state"])].append(row)
 expected_cells=[]
 for (host,b,state),rows in sorted(cells.items()):expected_cells.append({"residual_host":host,"branch":b,"right_edge_state":state,"occurrences":str(len(rows)),"physical_folios":str(len({r["physical_folio"]for r in rows})),"tokens":"|".join(sorted({r["token"]for r in rows})),"loci":"|".join(sorted({r["locus"]for r in rows})),"claim_state":"FORMAL_CELL_NOT_MEANING"})
 stored_cells=read("gdt028_host_branch_state_cells.tsv");checks.append(("cell_inventory_exact",stored_cells==expected_cells))
 hosts=sorted({h for h,_,_ in cells});expected_rect=[];expected_pred=[]
 for host in hosts:
  states=sorted({s for h,b,s in cells if h==host})
  for first,second in itertools.combinations(states,2):
   keys=[(host,b,s)for b in("Q","L")for s in(first,second)];present=[key in cells for key in keys]
   if sum(present)<2:continue
   missing=[f"{b}:{s}"for (_,b,s),yes in zip(keys,present)if not yes]
   expected_rect.append({"residual_host":host,"state_1":first,"state_2":second,"q_state_1":str(int(keys[0]in cells)),"q_state_2":str(int(keys[1]in cells)),"l_state_1":str(int(keys[2]in cells)),"l_state_2":str(int(keys[3]in cells)),"observed_cells":str(sum(present)),"missing_cells":"|".join(missing),"classification":"COMPLETE_2X2"if sum(present)==4 else"THREE_OF_FOUR"if sum(present)==3 else"TWO_OF_FOUR","claim_state":"FACTORIAL_CAPACITY_NOT_MEANING"})
   if sum(present)==3:
    mb,ms=missing[0].split(":");surface="tedaldy"if(host,mb,ms)==("edal","Q","DY_RESOLUTION")else"UNRESOLVED_FORM";count=sum(r["token"]==surface for r in inv)if surface!="UNRESOLVED_FORM"else""
    expected_pred.append({"residual_host":host,"missing_branch":mb,"missing_right_edge_state":ms,"model_predicted_surface":surface,"whole_inventory_occurrences":str(count),"prediction_outcome":"ABSENT"if surface!="UNRESOLVED_FORM"and count==0 else"PRESENT"if surface!="UNRESOLVED_FORM"else"FORM_NOT_DERIVED","basis":"Q counterpart of shedaldy and DY extension of tedal"if surface=="tedaldy"else"","claim_state":"EXPLICIT_FACTORIAL_PREDICTION_NOT_MEANING"})
 rect=read("gdt028_factorial_rectangles.tsv");pred=read("gdt028_missing_fourth_predictions.tsv");checks +=[("rectangles_exact",rect==expected_rect),("predictions_exact",pred==expected_pred)]
 both=sum(len({b for h,b,s in cells if h==host})==2 for host in hosts);multi=sum(len({s for h,b,s in cells if h==host})>=2 for host in hosts);complete=sum(r["classification"]=="COMPLETE_2X2"for r in rect);partial=sum(r["classification"]=="THREE_OF_FOUR"for r in rect)
 checks +=[("summary",result["occupied_cells"]==len(cells)==210 and result["residual_hosts"]==len(hosts)==198 and result["both_branch_hosts"]==both==8 and result["multi_state_hosts"]==multi==4 and result["rectangles"]==len(rect)==4 and result["complete_rectangles"]==complete==0 and result["three_of_four_rectangles"]==partial==1),("failed_cell",result["failed_prediction"]=="tedaldy"and result["failed_prediction_occurrences"]==0),("flags",result["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False})]
 report=" ".join((ROOT/"GDT028_Q_L_RIGHT_EDGE_FACTORIAL_REPORT.md").read_text().lower().split());ledger=(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text();checks +=[("claims",all(x in report for x in("zero occurrences","specific failed prediction","do not support treating branch and right edge as freely independent slots","f84r was not opened","no role"))),("ledger",ledger.count("GDT028_CKPT001")==1)]
 failures=[n for n,ok in checks if not ok];validation={"schema":"GDT028_Q_L_RIGHT_EDGE_FACTORIAL_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction of all host-branch-state cells, all eligible rectangles, the explicit missing tedaldy prediction, hashes, f84r exclusion, ledger, and claims."};VAL.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps(validation,sort_keys=True));
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
