#!/usr/bin/env python3
"""Freeze GDT271 capacity and prediction without scoring association direction."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SRC="gdt127_q20_field_inventory.tsv";SOURCE_RESULT="gdt270_result.json";OLD="gdt268_result.json";METHOD="GDT271_Q20_Q_OUTER_LAYER_TRANSFER_METHOD.md"
EDS=("ZL3b","IT2a","RF1b")
VARIANTS=[("PAGE_HOST_PAGE_OTHER_COMPILER",("page","page_host","other_compiler")),("PAGE_HOST_PAGE_OTHER_COMPILER_WITHIN_FIELD_POSITION",("page","page_host","other_compiler","within_field_position")),("PAGE_HOST_PAGE_OTHER_COMPILER_LOCAL_STRUCTURE",("page","page_host","other_compiler","local_structure"))]
def read(name):
 with (R/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()
def capacity(rows,ed):
 pages=defaultdict(set)
 for x in rows:
  if x["edition"]==ed:pages[x["page"]].add(int(x["star_ordinal"]))
 selected={}
 for p,values in pages.items():
  stars=sorted(values);k=len(stars)//2;selected[p]={v:0 for v in stars[:k]};selected[p].update({v:1 for v in stars[-k:]})
 occ=[]
 for x in rows:
  if x["edition"]!=ed:continue
  page=x["page"];star=int(x["star_ordinal"])
  if star not in selected[page]:continue
  hosts=x["page_hosts"].split("|");cells=json.loads(x["compiler_skeleton"]);assert len(hosts)==len(cells)
  for index,(host,cell) in enumerate(zip(hosts,cells)):
   wrapper,frame,right,inner,dy,b3=cell
   if wrapper not in {"q","NONE"}:continue
   pos="SINGLE" if len(hosts)==1 else "FIRST" if index==0 else "LAST" if index==len(hosts)-1 else "MIDDLE";end="DY" if int(x["ends_dy"]) else "B3" if int(x["ends_b3"]) else "OPEN"
   occ.append({"page":page,"page_host":host,"wrapper":wrapper,"stage":selected[page][star],"other_compiler":":".join(map(str,(frame,inner,right,dy,b3))),"within_field_position":pos,"local_structure":pos+":"+end})
 out={"selected_records":sum(len(v) for v in selected.values()),"q_or_bare_occurrences":len(occ),"variants":{}}
 for name,keys in VARIANTS:
  grouped=defaultdict(Counter)
  for x in occ:grouped[tuple(x[k] for k in keys)][x["wrapper"],x["stage"]]+=1
  mobile=[]
  for key,c in grouped.items():
   n=sum(c.values());q=c["q",0]+c["q",1];early=c["q",0]+c["NONE",0]
   if min(q,early)>max(0,q-(n-early)):mobile.append((key,n))
  out["variants"][name]={"all_strata":len(grouped),"movable_strata":len(mobile),"mobile_occurrences":sum(n for _,n in mobile),"mobile_hosts":len({key[1] for key,n in mobile}),"mobile_pages":len({key[0] for key,n in mobile})}
 return out
def main():
 rows=read(SRC);assert rows and all(not x["page"].startswith("f84") for x in rows);source=json.loads((R/SOURCE_RESULT).read_text());assert source["status"]=="Q13_Q_SEPARABLE_OUTER_RECORD_STAGE_RENDERER_COMPILER_MATCHED_EXPLORATORY"
 prediction={"experiment":"GDT271_Q20_Q_OUTER_LAYER_TRANSFER","freeze_status":"FROZEN_BEFORE_GDT271_CONDITIONAL_ASSOCIATION_SCORING","prediction":"q has positive EARLY allocation conditional on exact page PAGE_HOST and non-wrapper compiler tuple","primary_reading":"ZL3b","alternate_readings":["IT2a","RF1b"],"record_split":"first and last equal-sized star-ordinal halves; middle excluded","variants":[name for name,keys in VARIANTS],"primary_variant":"PAGE_HOST_PAGE_OTHER_COMPILER","primary_gate":{"conditional_score":"POSITIVE","positive_pages_min":9,"page_sign_max_three_p_max":0.05},"capacity":{ed:capacity(rows,ed) for ed in EDS},"semantic_assignments":0,"claim_ceiling":"Cross-register transfer of opaque q outer-renderer stage direction only; no word morpheme semantic operator meaning plaintext or translation.","f84r":{"new_access":False,"used":False,"scored":False},"inputs":{SRC:sha(SRC),SOURCE_RESULT:sha(SOURCE_RESULT),OLD:sha(OLD)},"documents":{METHOD:sha(METHOD)},"implementation":{Path(__file__).name:sha(Path(__file__).name)}};prediction["content_hash"]=hashlib.sha256(json.dumps(prediction,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt271_frozen_prediction.json").write_text(json.dumps(prediction,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":prediction["freeze_status"],"capacity":prediction["capacity"]},sort_keys=True))
if __name__=="__main__":main()
