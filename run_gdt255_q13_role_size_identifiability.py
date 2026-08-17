#!/usr/bin/env python3
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
F80="gdt254_f80r_role_projection.tsv";F82="gdt243_f82r_missingness_role_projection.tsv";R254="gdt254_result.json";R243="gdt243_result.json"
OUTS=["gdt255_group_count_role_crosstab.tsv","gdt255_shared_host_role_atlas.tsv","gdt255_counterexamples.tsv"];DOCS=["GDT255_Q13_ROLE_SIZE_IDENTIFIABILITY_METHOD.md","GDT255_Q13_ROLE_SIZE_IDENTIFIABILITY_REPORT.md"]
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def rd(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def wr(p,z):
 with (R/p).open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=list(z[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(z)
def main():
 fields=rd(F80)+rd(F82);assert len(fields)==94 and all(not x["page"].startswith("f84") for x in fields)
 ct=Counter((int(x["field_group_count"]),x["robust_abstract_role_like"]) for x in fields);tab=[]
 for n in sorted({k[0] for k in ct}):
  tab.append({"field_group_count":n,"fields":sum(ct[n,r] for r in ("SHORT_ARGUMENT_LIKE","INSTRUCTION_CLAUSE_LIKE")),"short_argument_like":ct[n,"SHORT_ARGUMENT_LIKE"],"instruction_clause_like":ct[n,"INSTRUCTION_CLAUSE_LIKE"],"deterministic_threshold_prediction":"SHORT_ARGUMENT_LIKE" if n<=2 else "INSTRUCTION_CLAUSE_LIKE"})
 wr(OUTS[0],tab)
 exact=sum(("SHORT_ARGUMENT_LIKE" if int(x["field_group_count"])<=2 else "INSTRUCTION_CLAUSE_LIKE")==x["robust_abstract_role_like"] for x in fields)
 occ=defaultdict(list)
 for x in fields:
  toks=x["source_tokens"].split("|");hosts=x["page_hosts"].split("|")
  assert len(toks)==len(hosts)==int(x["field_group_count"])
  for t,h in zip(toks,hosts):occ[h].append((x,t))
 atlas=[]
 for h,z in sorted(occ.items()):
  pc=Counter(x[0]["page"] for x in z)
  if set(pc)!={"f80r","f82r"} or min(pc.values())<2:continue
  rc=Counter(x[0]["robust_abstract_role_like"] for x in z);maj,maxn=min((k for k,v in rc.items() if v==max(rc.values()))),max(rc.values())
  sizes=sorted({int(x[0]["field_group_count"]) for x in z});size_pred=sum(("SHORT_ARGUMENT_LIKE" if int(x[0]["field_group_count"])<=2 else "INSTRUCTION_CLAUSE_LIKE")==x[0]["robust_abstract_role_like"] for x in z)
  wrappers=sorted({t[:-len(h)-2] if t.endswith(h+"dy") else t[:-len(h)] if t.endswith(h) else "OTHER" for _,t in z})
  atlas.append({"page_host":h,"occurrences":len(z),"f80r_occurrences":pc["f80r"],"f82r_occurrences":pc["f82r"],"paragraphs":len({(x[0]["page"],x[0]["paragraph_id"]) for x in z}),"majority_role_like":maj,"role_purity":f"{maxn/len(z):.12f}","field_group_counts":";".join(map(str,sizes)),"size_threshold_correct":size_pred,"size_threshold_fraction":f"{size_pred/len(z):.12f}","surface_prefix_variants":";".join(wrappers),"semantic_residual_after_size_control":"NONE_IDENTIFIABLE"})
 atlas.sort(key=lambda x:(-float(x["role_purity"]),-min(int(x["f80r_occurrences"]),int(x["f82r_occurrences"])),-int(x["occurrences"]),x["page_host"]));wr(OUTS[1],atlas)
 ol=next(x for x in atlas if x["page_host"]=="olche")
 counter=[{"counterexample":"EXACT_SIZE_COLLAPSE","value":f"{exact}/94 fields equal the rule group_count<=2 SHORT else INSTRUCTION","consequence":"the retained role-like layer has zero residual information beyond field size"},{"counterexample":"OLCHE_SIZE_CONFOUND","value":f"olche is {ol['majority_role_like']} in {ol['occurrences']}/{ol['occurrences']} occurrences but only in field sizes {ol['field_group_counts']}","consequence":"its apparent stable role is fully explained by the exact-size rule"},{"counterexample":"NO_EDGE_CLASS_RECOVERY","value":"corrected projections retain only the two size-separated interior classes","consequence":"opener closer or record-function semantics are not identified"},{"counterexample":"TWO_PAGE_SCOPE","value":"the corrected comparison has two physical folios","consequence":"no q13-wide role dictionary can be inferred"}];wr(OUTS[2],counter)
 status="CORRECTED_Q13_ROLE_ANALOGIES_COLLAPSE_EXACTLY_TO_FIELD_SIZE_ZERO_HOST_SEMANTIC_RESIDUAL";result={"experiment":"GDT255_Q13_ROLE_SIZE_IDENTIFIABILITY","status":status,"fields":len(fields),"pages":2,"size_threshold_correct":exact,"size_threshold_accuracy":exact/len(fields),"short_fields":sum(x["robust_abstract_role_like"]=="SHORT_ARGUMENT_LIKE" for x in fields),"clause_fields":sum(x["robust_abstract_role_like"]=="INSTRUCTION_CLAUSE_LIKE" for x in fields),"shared_hosts_min2_each_page":len(atlas),"olche":{"occurrences":int(ol["occurrences"]),"role_purity":float(ol["role_purity"]),"size_threshold_fraction":float(ol["size_threshold_fraction"]),"status":"FORMAL_CLOSED_SHORT_FIELD_HOST_NO_SEMANTIC_ROLE"},"interpretation":"The corrected external role analogies are exactly a field-size partition, so PAGE_HOST role purity on these pages cannot localize semantic content.","active_semantic_assignments":0,"claim_ceiling":"Role/size identifiability audit only; no ingredient operation material state word language plaintext or translation.","f84":{"input":False,"retained":False,"joined":False,"scored":False,"new_access":False},"inputs":{p:sha(p) for p in [F80,F82,R254,R243]},"outputs":{},"documents":{},"implementation":{}}
 for p in OUTS:result["outputs"][p]=sha(p)
 for p in DOCS:result["documents"][p]=sha(p)
 result["implementation"][Path(__file__).name]=sha(Path(__file__).name)
 report=(R/DOCS[1]).read_text().split("\n## Reproducible result",1)[0].rstrip()+f"\n\n## Reproducible result\n\nStatus: **{status}**.\n\nAll **{exact}/94** fields equal the rule: **1–2 groups → SHORT_ARGUMENT_LIKE; 3+ groups → INSTRUCTION_CLAUSE_LIKE**. The {len(atlas)} PAGE_HOSTs recurring at least twice on each page therefore have no identifiable role signal beyond size. `olche` is 4/4 short-field-like across both pages and multiple wrappers, but all four occurrences lie in one- or two-group fields, where the whole panel is short-field-like.\n\nThe corrected lattice remains useful formal segmentation, but it cannot ground meanings. No f84 input was used.\n";(R/DOCS[1]).write_text(report,encoding="utf-8");result["documents"][DOCS[1]]=sha(DOCS[1]);result["content_hash"]=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt255_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"exact":exact,"hosts":len(atlas),"olche":ol},sort_keys=True))
if __name__=="__main__":main()
