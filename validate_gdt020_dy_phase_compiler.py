#!/usr/bin/env python3
"""Independent reconstruction of GDT020 phase models and parses."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt020_result.json";VAL=ROOT/"gdt020_validation.json";A=.5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def collapse(seq):
 out=[]
 for x in seq:
  if not out or out[-1]!=x:out.append(x)
 return out
def bits(events,folios,K,bins,phase):
 total=0.;fold=[]
 for held in folios:
  c=defaultdict(Counter);n=Counter()
  for e in events:
   if e["folio"]==held:continue
   p=min(bins-1,int(e["fraction"]*bins));ctx=(p,e["seen"])if phase else(p,);c[ctx][e["state"]]+=1;n[ctx]+=1
  b=0.
  for e in events:
   if e["folio"]!=held:continue
   p=min(bins-1,int(e["fraction"]*bins));ctx=(p,e["seen"])if phase else(p,);b-=math.log2((c[ctx][e["state"]]+A)/(n[ctx]+A*K))
  total+=b;fold.append(b)
 return total,fold
def close(a,b):return abs(float(a)-float(b))<8e-10
def main():
 checks=[];result=json.loads(RES.read_text());copy=dict(result);digest=copy.pop("result_content_sha256");checks+=[("schema",result["schema"]=="GDT020_DY_PHASE_COMPILER_RESULT_V1"),("content",digest==csha(copy))]
 for part in("inputs","implementation","outputs"):
  for n,d in result[part].items():checks.append((part+":"+n,sha(ROOT/n)==d))
 inv=read("gdt016_group_state_inventory.tsv");checks+=[("input_count",len(inv)==result["groups"]==15592),("f84_guard",not any(r["locus"].startswith("f84r")for r in inv))];by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 events=[];expected_lines=[];templates=Counter();template_folios=defaultdict(set);dy=internal=withdy=segments=0
 for locus,line in sorted(by.items()):
  line.sort(key=lambda r:int(r["group_index"]));seen=0;after=0;compiled=[];ss=[];tt=[];states=[];tokens=[];checkpoints=0
  for i,r in enumerate(line):
   frac=(int(r["group_index"])-1)/(int(r["group_count"])-1)if int(r["group_count"])>1 else.5;events.append({"folio":r["physical_folio"],"fraction":frac,"state":r["record_state"],"seen":seen,"after":after});states.append(r["record_state"]);tokens.append(r["token"]);ss.append(r["record_state"]);tt.append(r["token"])
   if r["record_state"]=="DY_RESOLUTION":dy+=1;checkpoints+=1;internal+=i+1<len(line);compiled.append((ss,tt,"CLOSED_WITH_DY"));ss=[];tt=[];seen=1;after=1
   else:after=0
  if ss:compiled.append((ss,tt,"OPEN_TAIL"))
  withdy+=checkpoints>0;segments+=len(compiled);expected_lines.append((locus,len(line),checkpoints,len(compiled)," | ".join(tokens)," > ".join(states)," || ".join(" > ".join(x[0])for x in compiled)))
  for i,(s,t,closure)in enumerate(compiled):
   key=("LINE_INITIAL"if i==0 else"POST_DY",closure," > ".join(collapse(s)));templates[key]+=1;template_folios[key].add(line[0]["physical_folio"])
 stored_lines=read("gdt020_line_phase_parses.tsv");stored_line_keys=[(r["locus"],int(r["group_count"]),int(r["checkpoint_count"]),int(r["phase_count"]),r["tokens"],r["states"],r["compiled_phases"])for r in stored_lines];checks+=[("line_parse_exact",stored_line_keys==expected_lines),("line_count",len(by)==result["lines"]==2471),("dy",dy==result["dy_checkpoints"]==2667),("internal",internal==result["internal_dy_checkpoints"]==2344),("withdy",withdy==result["lines_with_dy"]==1256),("segments",segments==result["compiled_phases"]==4815)]
 stored_templates={(r["segment_origin"],r["closure"],r["collapsed_state_template"]):r for r in read("gdt020_segment_templates.tsv")};eligible={k:v for k,v in templates.items()if v>=3};checks+=[("template_count",len(stored_templates)==result["recurrent_segment_templates"]==len(eligible)==190),("template_counts",all(int(stored_templates[k]["occurrences"])==v and int(stored_templates[k]["physical_folios"])==len(template_folios[k])for k,v in eligible.items())),("post_single",int(stored_templates[("POST_DY","CLOSED_WITH_DY","DY_RESOLUTION")]["occurrences"])==737)]
 alphabet=sorted({e["state"]for e in events});folios=sorted({e["folio"]for e in events});stored={r["model"]:r for r in read("gdt020_phase_models.tsv")}
 for bins in(4,8,10,16):
  base,bf=bits(events,folios,len(alphabet),bins,False);phase,pf=bits(events,folios,len(alphabet),bins,True);gain=base-phase;extra=bins*(len(alphabet)-1);pen=extra/2*math.log2(len(events));r=stored[f"POSITION_{bins}_BINS_PLUS_SEEN_DY"];checks.append(("model:"+str(bins),close(r["position_bits"],base)and close(r["position_plus_phase_bits"],phase)and close(r["raw_gain_bits"],gain)and int(r["positive_held_folios"])==sum(a>b for a,b in zip(bf,pf))and int(r["bic_extra_parameters"])==extra and close(r["bic_net_gain_bits"],gain-pen)))
 sensitivity=[e for e in events if not e["after"]];base,bf=bits(sensitivity,folios,len(alphabet),4,False);phase,pf=bits(sensitivity,folios,len(alphabet),4,True);gain=base-phase;extra=4*(len(alphabet)-1);pen=extra/2*math.log2(len(sensitivity));r=stored["POSITION_4_PLUS_SEEN_DY_EXCLUDING_IMMEDIATE"];checks.append(("sensitivity",len(sensitivity)==int(r["events"])==13248 and close(r["raw_gain_bits"],gain)and close(r["bic_net_gain_bits"],gain-pen)and int(r["positive_held_folios"])==sum(a>b for a,b in zip(bf,pf))))
 checks+=[("folios",len(folios)==result["physical_folios"]==94),("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT020_CKPT001")==1),("f84_flags",result["f84r"]=={"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False})];report=(ROOT/"GDT020_DY_PHASE_COMPILER_REPORT.md").read_text().lower();checks.append(("claims",all(x in report for x in("chains of compact closed fields","persistence evidence","no morpheme","f84r was absent"))))
 failures=[n for n,ok in checks if not ok];v={"schema":"GDT020_DY_PHASE_COMPILER_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent reconstruction from the frozen f84r-free inventory of every line phase parse, recurrent template counts, five held-folio phase models, penalties, hashes, ledger, and claims."};VAL.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps(v,sort_keys=True));
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
