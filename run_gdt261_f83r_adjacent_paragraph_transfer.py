#!/usr/bin/env python3
"""Run the exposed f83r display-layer sensitivity to GDT260."""
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
REL="gdt238_relation_inventory.tsv";MORPH="gdt002_morphology_occurrences.tsv";EXPOSE="gdt201_f83r_zone_predictions.tsv";FRAME="gdt046_line_frames.tsv";LINES="gdt020_line_phase_parses.tsv";ACCESS="gdt257_result.json"
OUTS=["gdt261_f83r_transfer.tsv","gdt261_counterexamples.tsv"];DOCS=["GDT261_F83R_ADJACENT_PARAGRAPH_TRANSFER_METHOD.md","GDT261_F83R_ADJACENT_PARAGRAPH_TRANSFER_REPORT.md"]
def read(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows):
 with (R/p).open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def tail(m,k):
 den=math.comb(25,m);return sum(math.comb(3,j)*math.comb(22,m-j) for j in range(k,min(3,m)+1) if 0<=m-j<=22)/den if m else 1
def main():
 rel=[x for x in read(REL) if x["locus"]=="f83r.46"];assert len(rel)==1 and rel[0]["relation_class"]=="ATTACHMENT" and rel[0]["certainty"]=="HEDGED"
 mm=[x for x in read(MORPH) if x["locus"]=="f83r.46" and x["module"]=="OL"];assert len(mm)==1 and mm[0]["ZL3b_token"]==mm[0]["IT2a_token"]==mm[0]["RF1b_token"]=="olsaiin" and mm[0]["reading_agreement"]=="ALL_THREE_EXACT"
 ex=[x for x in read(EXPOSE) if x["locus"]=="f83r.46"];assert len(ex)==1 and ex[0]["formal_exposure"]=="FORMAL_VALUES_PREVIOUSLY_EXPOSED"
 fr=[x for x in read(FRAME) if x["page"]=="f83r"];assert all(not x["page"].startswith("f84r") for x in fr);starts={x["locus"] for x in fr if x["paragraph_start"]=="1"};assert {"f83r.47","f83r.52"}<=starts
 frame_loci={x["locus"] for x in fr};ls=[x for x in read(LINES) if x["page"]=="f83r" and x["locus"] in frame_loci];assert len(ls)==25 and all(not x["page"].startswith("f84r") for x in ls);target={"f83r.47","f83r.48","f83r.49"}
 rows=[]
 for name,t in [("LEFT_MODULE","ol"),("RIGHT_REMAINDER","saiin"),("FULL_LABEL","olsaiin")]:
  hit=defaultdict(list);exact=set()
  for x in ls:
   for tok in [q.strip() for q in x["tokens"].split("|")]:
    for i in range(len(tok)-len(t)+1):
     d=sum(a!=b for a,b in zip(t,tok[i:i+len(t)]))
     if d<=1:hit[x["locus"]].append(f"{tok}@{i+1}:d{d}")
     if d==0:exact.add(x["locus"])
  k=len(target&set(hit));m=len(hit);p=tail(m,k)
  rows.append({"representation":name,"target_surface":t,"page_prose_lines":25,"target_paragraph_lines":3,"all_hit_lines":m,"target_hit_lines":k,"target_hit_loci":";".join(sorted(target&set(hit),key=lambda z:int(z.split('.')[1]))),"exact_hit_lines":len(exact),"local_hypergeom_p":f"{p:.12f}","three_representation_bonferroni_p":f"{min(1,3*p):.12f}","transfer_state":"NO_SPECIFIC_ADJACENT_PARAGRAPH_ENRICHMENT","semantic_value":"UNASSIGNED"})
 write(OUTS[0],rows);assert [(x["all_hit_lines"],x["target_hit_lines"]) for x in rows]==[(24,3),(12,0),(0,0)]
 counter=[
  {"counterexample":"LEFT_MODULE_UBIQUITOUS","value":"ol hits 24/25 page lines and 3/3 target lines; p=.88","consequence":"target hits provide no adjacent-paragraph specificity"},
  {"counterexample":"RIGHT_REMAINDER_ABSENT","value":"saiin hits 12 page lines but 0/3 target lines","consequence":"the less generic label remainder does not transfer"},
  {"counterexample":"FULL_LABEL_ABSENT","value":"olsaiin has zero one-edit prose hit-lines","consequence":"no whole-label paragraph bridge"},
  {"counterexample":"HEDGED_ATTACHMENT","value":"human comment says the label may be attached to the tube endpoint","consequence":"source-bound relation is weaker than f82r.10"},
  {"counterexample":"PREEXPOSED_AND_ENDPOINT_SHIFTED","value":"label/prose were exposed and endpoint is raw display rather than STA members","consequence":"falsifying sensitivity only, not prospective replication"},]
 write(OUTS[1],counter);a=json.loads((R/ACCESS).read_text());assert a["access"]["pristine_access_seal"] is False
 result={"experiment":"GDT261_F83R_ADJACENT_PARAGRAPH_TRANSFER","status":"F83R_EXPOSED_ADJACENT_PARAGRAPH_SENSITIVITY_FAILS_GDT260_COMPONENT_TRANSFER","target":"f83r.46_to_f83r.47_49","formal_exposure":"PREVIOUSLY_EXPOSED","endpoint":"SOURCE_DISPLAY_WITHIN_TOKEN_HAMMING_LE1","left_module":"24_PAGE_3_TARGET_P_0.88","right_remainder":"12_PAGE_0_TARGET","full_label":"0_PAGE_0_TARGET","active_semantic_assignments":0,"interpretation":"The independent-folio exposed display sensitivity does not support a general attached-label component neighborhood in the adjacent paragraph, leaving GDT260 page-local and provisional.","claim_ceiling":"Exposed display-layer transfer sensitivity only; no object component reference function word language plaintext meaning or translation.","f84r":{"prior_transient_parse_disclosed":True,"new_access":False,"used":False,"scored":False,"further_access_authorized":False},"inputs":{x:sha(x) for x in [REL,MORPH,EXPOSE,FRAME,LINES,ACCESS]},"outputs":{},"documents":{},"implementation":{Path(__file__).name:sha(Path(__file__).name)}}
 for x in OUTS:result["outputs"][x]=sha(x)
 for x in DOCS:result["documents"][x]=sha(x)
 result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt261_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"rows":rows},sort_keys=True))
if __name__=="__main__":main()
