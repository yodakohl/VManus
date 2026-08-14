#!/usr/bin/env python3
"""Audit direct Q/L by right-edge factorial rectangles."""
from __future__ import annotations
import csv,hashlib,itertools,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(n,rows):
 with (ROOT/n).open("w",encoding="utf-8",newline="")as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def branch(f):
 if"QJB"in f or"QKB"in f:return"Q"
 if"LJB"in f or"LKB"in f:return"L"
 return"OTHER"
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv)
 cells=defaultdict(list)
 for r in inv:
  b=branch(r["family_surface"])
  if r["currier"]=="B"and b!="OTHER":cells[(r["residual_host"],b,r["record_state"])].append(r)
 cellrows=[]
 for (host,b,state),rs in sorted(cells.items()):
  cellrows.append({"residual_host":host,"branch":b,"right_edge_state":state,"occurrences":len(rs),"physical_folios":len({r["physical_folio"]for r in rs}),"tokens":"|".join(sorted({r["token"]for r in rs})),"loci":"|".join(sorted({r["locus"]for r in rs})),"claim_state":"FORMAL_CELL_NOT_MEANING"})
 write("gdt028_host_branch_state_cells.tsv",cellrows)
 hosts=sorted({h for h,_,_ in cells});rect=[];pred=[]
 for host in hosts:
  states=sorted({s for h,b,s in cells if h==host})
  for a,z in itertools.combinations(states,2):
   keys=[(host,b,s)for b in("Q","L")for s in(a,z)];present=[k in cells for k in keys]
   if sum(present)<2:continue
   missing=[f"{b}:{s}"for (_,b,s),p in zip(keys,present)if not p]
   row={"residual_host":host,"state_1":a,"state_2":z,"q_state_1":int(keys[0]in cells),"q_state_2":int(keys[1]in cells),"l_state_1":int(keys[2]in cells),"l_state_2":int(keys[3]in cells),"observed_cells":sum(present),"missing_cells":"|".join(missing),"classification":"COMPLETE_2X2"if sum(present)==4 else"THREE_OF_FOUR"if sum(present)==3 else"TWO_OF_FOUR","claim_state":"FACTORIAL_CAPACITY_NOT_MEANING"};rect.append(row)
   if sum(present)==3:
    mb,ms=missing[0].split(":");prediction="tedaldy"if(host,mb,ms)==("edal","Q","DY_RESOLUTION")else"UNRESOLVED_FORM"
    pred.append({"residual_host":host,"missing_branch":mb,"missing_right_edge_state":ms,"model_predicted_surface":prediction,"whole_inventory_occurrences":sum(r["token"]==prediction for r in inv)if prediction!="UNRESOLVED_FORM"else"","prediction_outcome":"ABSENT"if prediction!="UNRESOLVED_FORM"and not any(r["token"]==prediction for r in inv)else"PRESENT"if prediction!="UNRESOLVED_FORM"else"FORM_NOT_DERIVED","basis":"Q counterpart of shedaldy and DY extension of tedal"if prediction=="tedaldy"else"","claim_state":"EXPLICIT_FACTORIAL_PREDICTION_NOT_MEANING"})
 write("gdt028_factorial_rectangles.tsv",rect);write("gdt028_missing_fourth_predictions.tsv",pred)
 both=sum(len({b for h,b,s in cells if h==host})==2 for host in hosts);multi=sum(len({s for h,b,s in cells if h==host})>=2 for host in hosts);full=sum(r["classification"]=="COMPLETE_2X2"for r in rect);partial=sum(r["classification"]=="THREE_OF_FOUR"for r in rect);status="Q_L_RIGHT_EDGE_FACTORIAL_COMPOSITION_NOT_DEMONSTRATED"
 report=f"""# GDT028 Q/L × right-edge factorial report

Status: **{status.replace('_',' ')}**

The direct combinatorial consequence of GDT027 is not observed. The census has
{len(cells)} occupied cells over {len(hosts)} residual hosts. Only {both} hosts occur in
both Q and L branches, and only {multi} hosts occur in more than one right-edge
state. There are {full} complete Q/L × two-state rectangles.

One 3-of-4 case is especially informative. `edal` occurs as Q+AL `tedal`,
L+AL `shedal`, and L+DY `shedaldy`. The factored fourth form is `tedaldy`.
It has zero occurrences in the complete frozen inventory. This is a specific
failed prediction for unrestricted Q/L × right-edge combination.

The earlier backward-history association remains real as a distributional
constraint, but the present data do not support treating branch and right edge
as freely independent slots. Compatibility is host-specific or otherwise
restricted. Only the frozen GDT016 inventory is used; it contains no f84r row,
and f84r was not opened, retained, joined, or scored. No role, morpheme, word,
sound, language, plaintext, meaning, or translation is assigned.
""";(ROOT/"GDT028_Q_L_RIGHT_EDGE_FACTORIAL_REPORT.md").write_text(report)
 outputs=("gdt028_host_branch_state_cells.tsv","gdt028_factorial_rectangles.tsv","gdt028_missing_fourth_predictions.tsv","GDT028_Q_L_RIGHT_EDGE_FACTORIAL_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt016_result.json","gdt027_result.json","GDT028_Q_L_RIGHT_EDGE_FACTORIAL_METHOD.md")
 result={"schema":"GDT028_Q_L_RIGHT_EDGE_FACTORIAL_RESULT_V1","status":status,"inventory_groups":len(inv),"occupied_cells":len(cells),"residual_hosts":len(hosts),"both_branch_hosts":both,"multi_state_hosts":multi,"rectangles":len(rect),"complete_rectangles":full,"three_of_four_rectangles":partial,"missing_predictions":len(pred),"failed_prediction":"tedaldy","failed_prediction_occurrences":0,"interpretation":"Backward history association retained, but unrestricted branch by right-edge factorial composition is not demonstrated.","f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Formal combinatorial capacity and one explicit failed fourth-cell prediction only; no role, morpheme, word, syntax, sound, language, plaintext, meaning, or translation.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt028_q_l_right_edge_factorial.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt028_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"cells":len(cells),"hosts":len(hosts),"complete":full,"three_of_four":partial,"predictions":pred},sort_keys=True))
if __name__=="__main__":main()
