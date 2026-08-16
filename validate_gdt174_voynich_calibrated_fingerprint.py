#!/usr/bin/env python3
"""Independent, non-importing reconstruction of the GDT174 fingerprint."""
from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
DESIGN=R/"gdt174_design.json";HPR2=R/"gdt062_right_family_inventory.tsv";FRAMES=R/"gdt046_line_frames.tsv"
OLD_PARSES=R/"gdt172_blind_parses.json.gz";B2_PARSES=R/"gdt173_blind_parses.json.gz";OLD_DIAG=R/"gdt172_blind_diagnostics.tsv";B2_DIAG=R/"gdt173_blind_diagnostics.tsv"
FINGERPRINT=R/"gdt173_three_system_fingerprint.tsv";RECOVERY=R/"gdt173_three_system_recovery.tsv";TABLE=R/"gdt174_side_by_side.tsv";PLACEMENT=R/"gdt174_axis_placement.tsv";OPERATIONS=R/"gdt174_voynich_operations.tsv";COUNTER=R/"gdt174_counterexamples.tsv";REPORT=R/"GDT174_VOYNICH_CALIBRATED_FINGERPRINT_REPORT.md";RESULT=R/"gdt174_result.json";PRODUCER=R/"run_gdt174_voynich_calibrated_fingerprint.py";OUT=R/"gdt174_validation.json"
SYSTEMS=("LEXICAL_A","HUMAN_GROWN_B2","FACTORIAL_B");WORLD={"LEXICAL_A":"CONTROL_P","HUMAN_GROWN_B2":"CONTROL_R","FACTORIAL_B":"CONTROL_Q"};ALPHA=16.;BETA=8.

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with p.open(newline="",encoding="utf8") as h:return list(csv.DictReader(h,delimiter="\t"))
def load(p):
 with gzip.open(p,"rt",encoding="utf8") as h:return json.load(h)["rows"]
def seed(s):return int(hashlib.sha256(s.encode()).hexdigest()[:16],16)
def number(locus):
 m=re.search(r"\.(\d+)$",locus);assert m;return int(m.group(1))

def panel():
 frames={};rf=0
 with FRAMES.open(newline="",encoding="utf8") as h:
  for x in csv.DictReader(h,delimiter="\t"):
   if x["page"].startswith("f84") or x["locus"].startswith("f84"):rf+=1;continue
   frames[x["locus"]]=x
 by=defaultdict(list);rh=0
 with HPR2.open(newline="",encoding="utf8") as h:
  for x in csv.DictReader(h,delimiter="\t"):
   if x["page"].startswith("f84") or x["locus"].startswith("f84"):rh+=1;continue
   if x["locus"] in frames:by[x["locus"]].append(x)
 assert set(by)==set(frames)
 assert all(len(v)==int(v[0]["group_count"]) and sorted(int(x["group_index"]) for x in v)==list(range(1,int(v[0]["group_count"])+1)) for v in by.values())
 pages=defaultdict(list);folios=defaultdict(list)
 for locus,x in frames.items():pages[x["page"]].append(locus);folios[x["physical_folio"]].append(locus)
 ends=set()
 for values in pages.values():
  values.sort(key=number);ends.add(values[-1])
  for a,b in zip(values,values[1:]):
   if int(frames[b]["paragraph_start"]):ends.add(a)
 lord={}
 for values in folios.values():
  values.sort(key=lambda x:(frames[x]["page"],number(x)))
  for i,locus in enumerate(values):lord[locus]=i
 ford={name:i for i,name in enumerate(sorted(folios))};rows=[]
 for locus in sorted(by,key=lambda x:(frames[x]["page"],number(x))):
  f=frames[locus]
  for x in sorted(by[locus],key=lambda y:int(y["group_index"])):
   local=("D1" if x["inner_d"]=="1" else "D0")+"|"+x["local_frame"]
   if x["inner_d"]=="0" and x["local_frame"]=="NONE":local="NONE"
   ro="NONE"
   if x["dy_closure"]=="1" or x["b3"]=="1":ro="DY"+x["dy_closure"]+"|B3"+x["b3"]
   rows.append({"surface_group":x["token"],"inferred_host":x["page_host"],"outer_left":x["wrapper"],"local_left":local,"right_inner":x["right_family"],"right_outer":ro,"register":x["register"],"hand":x["hand"],"folio_id":x["physical_folio"],"layout_folio_ordinal":ford[x["physical_folio"]],"physical_line_id":locus,"line_ordinal_on_folio":lord[locus],"group_index":int(x["group_index"]),"group_count":int(x["group_count"]),"paragraph_start":int(f["paragraph_start"]),"paragraph_end":int(locus in ends),"right_separator":"LINE_END" if x["group_index"]==x["group_count"] else "SOURCE_GROUP_BOUNDARY","page":x["page"],"locus":locus})
 assert not any(x["page"].startswith("f84") or x["locus"].startswith("f84") for x in rows)
 return rows,{"groups":len(rows),"lines":len(by),"pages":len(pages),"folios":len(folios),"f84_hpr2_rows_rejected":rh,"f84_frame_rows_rejected":rf}

def recurrence(rows):
 c=Counter(x["inferred_host"] for x in rows);f=defaultdict(set)
 for x in rows:f[x["inferred_host"]].add(x["folio_id"])
 return {"recurrent_host_mass":sum(n for n in c.values() if n>=2)/len(rows),"cross_folio_host_mass":sum(n for k,n in c.items() if len(f[k])>=2)/len(rows)}

def discovery(rows):
 c=Counter(x["surface_group"] for x in rows);folios=defaultdict(set)
 for x in rows:folios[x["surface_group"]].add(x["folio_id"])
 vocab=set(c);stats={}
 for word in sorted(vocab):
  if len(word)<2:continue
  for n in range(1,min(3,len(word)-1)+1):
   base=word[n:]
   if base in vocab:
    z=stats.setdefault(("LEFT",word[:n]),{"hosts":set(),"folios":set(),"pairs":set(),"occ":0});z["hosts"].add(base);z["folios"].update(folios[word]|folios[base]);z["pairs"].add((base,word));z["occ"]+=c[word]
   base=word[:-n]
   if base in vocab:
    z=stats.setdefault(("RIGHT",word[-n:]),{"hosts":set(),"folios":set(),"pairs":set(),"occ":0});z["hosts"].add(base);z["folios"].update(folios[word]|folios[base]);z["pairs"].add((base,word));z["occ"]+=c[word]
 items=[]
 for (side,op),z in stats.items():items.append({"side":side,"operation":op,"operation_length":len(op),"distinct_hosts":len(z["hosts"]),"exact_pair_types":len(z["pairs"]),"physical_folios":len(z["folios"]),"transformed_occurrences":z["occ"],"eligible":len(z["hosts"])>=8 and len(z["folios"])>=5})
 items.sort(key=lambda x:(x["side"],-x["distinct_hosts"],-x["exact_pair_types"],x["operation"]));left=[x["operation"] for x in items if x["side"]=="LEFT" and x["eligible"]][:12];right=[x["operation"] for x in items if x["side"]=="RIGHT" and x["eligible"]][:12]
 return c,items,left,right

def compat(forms,left,right):
 ls={op:{h for h in forms if op+h in forms} for op in left};rs={op:{h for h in forms if h+op in forms} for op in right}
 obs=sum(bool(ls[l]&rs[r]&{h for h in forms if l+h+r in forms}) for l in left for r in right);hosts=sorted(forms);rng=random.Random(seed("GDT170_COMPAT_"+"GDT174_VOYNICH_FROZEN"));null=[]
 for _ in range(1024):
  total=0
  for l in left:
   for r in right:total+=bool(ls[l]&set(rng.sample(hosts,min(len(rs[r]),len(hosts)))))
  null.append(total)
 den=max(1,len(left)*len(right));return {"selected_left_operations":float(len(left)),"selected_right_operations":float(len(right)),"compatibility_density":obs/den,"null_density":sum(null)/len(null)/den,"compatibility_null_excess":obs/den-sum(null)/len(null)/den,"compatibility_inclusive_p":(1+sum(x>=obs for x in null))/1025}

def cosine(a,b):
 dot=sum(v*b.get(k,0.) for k,v in a.items());na=math.sqrt(sum(v*v for v in a.values()));nb=math.sqrt(sum(v*v for v in b.values()));return dot/(na*nb) if na and nb else 0.
def short_sub(rows):
 freq=Counter(x["inferred_host"] for x in rows);hosts=sorted(freq);buckets=defaultdict(list)
 for h in hosts:
  if len(h) in (2,3):
   for i in range(len(h)):buckets[len(h),i,h[:i]+"_"+h[i+1:]].append(h)
 edges=set()
 for vals in buckets.values():edges.update(itertools.combinations(sorted(set(vals)),2))
 same=defaultdict(Counter);external=defaultdict(Counter);lines=defaultdict(list)
 for x in rows:same[x["inferred_host"]]["|".join(str(x[k]) for k in ("outer_left","local_left","right_inner","right_outer"))]+=1;lines[x["physical_line_id"]].append(x)
 for line in lines.values():
  line.sort(key=lambda x:x["group_index"])
  for i,x in enumerate(line):
   for j in range(max(0,i-2),min(len(line),i+3)):
    if i!=j:external[x["inferred_host"]][line[j]["inferred_host"]]+=1
 def score(profiles):
  classes=defaultdict(list)
  for a,b in edges:
   dif=[i for i in range(len(a)) if a[i]!=b[i]]
   if len(dif)!=1:continue
   i=dif[0];d=Counter(profiles[b]);d.subtract(profiles[a]);scale=sum(abs(v) for v in d.values())
   if scale:d=Counter({k:v/scale for k,v in d.items() if v})
   classes[len(a),i,a[i],b[i]].append(d)
  vals=[]
  for group in classes.values():
   if len(group)>=3:vals.extend(cosine(a,b) for a,b in itertools.combinations(group,2))
  return sum(vals)/len(vals) if vals else 0.
 return sum(n for h,n in freq.items() if len(h) in (2,3))/len(rows),score(same),score(external)

def held(rows,endpoint):
 lines=defaultdict(list)
 for x in rows:lines[x["physical_line_id"]].append(x)
 events=[]
 for line in lines.values():
  line.sort(key=lambda x:x["group_index"])
  for i,x in enumerate(line):
   if endpoint=="NEXT_HOST":
    if i+1<len(line):events.append((x,line[i+1]["inferred_host"],1.))
   else:
    other=Counter(y["inferred_host"] for j,y in enumerate(line) if i!=j);n=sum(other.values())
    for target,count in other.items():events.append((x,target,count/n))
 vocab={t for _,t,_ in events};gt=Counter();gn=0.;nt=Counter();nn=Counter();ht=Counter();hn=Counter();ft=defaultdict(Counter);fn=Counter();fnt=defaultdict(Counter);fnn=defaultdict(Counter);fht=defaultdict(Counter);fhn=defaultdict(Counter)
 for x,t,w in events:
  fold=x["layout_folio_ordinal"];nk=(x["group_index"],x["line_ordinal_on_folio"]%3,x["group_count"]);h=x["inferred_host"];gt[t]+=w;gn+=w;nt[nk,t]+=w;nn[nk]+=w;ht[h,t]+=w;hn[h]+=w;ft[fold][t]+=w;fn[fold]+=w;fnt[fold][nk,t]+=w;fnn[fold][nk]+=w;fht[fold][h,t]+=w;fhn[fold][h]+=w
 gains=Counter()
 for x,t,w in events:
  fold=x["layout_folio_ordinal"];nk=(x["group_index"],x["line_ordinal_on_folio"]%3,x["group_count"]);h=x["inferred_host"];q=(gt[t]-ft[fold][t]+.5)/(gn-fn[fold]+.5*len(vocab));base=(nt[nk,t]-fnt[fold][nk,t]+ALPHA*q)/(nn[nk]-fnn[fold][nk]+ALPHA);hp=(ht[h,t]-fht[fold][h,t]+BETA*base)/(hn[h]-fhn[fold][h]+BETA);gains[fold]+=w*math.log2(hp/base)
 return sum(gains.values())

def closure(rows):
 ends=[x for x in rows if x["paragraph_end"] and x["right_separator"]=="LINE_END"];marks=[x for x in rows if x["right_outer"]!="NONE" or x["right_inner"]!="NONE"]
 return len([x for x in marks if x in ends])/max(1,len(marks)),sum(x["right_outer"]!="NONE" or x["right_inner"]!="NONE" for x in ends)/max(1,len(ends))
def signature(rows,panel):
 acc=defaultdict(Counter)
 for x in rows:
  h=x["inferred_host"]
  if h not in panel:continue
  acc[h]["N"]+=1;acc[h]["P"+str(x["group_index"])]+=1;acc[h]["L"+str(x["line_ordinal_on_folio"]%3)]+=1;acc[h]["LEFT"]+=x["outer_left"]!="NONE" or x["local_left"]!="NONE";acc[h]["RIGHT"]+=x["right_outer"]!="NONE" or x["right_inner"]!="NONE"
 out=[]
 for h in panel:
  n=acc[h]["N"];v=[math.log1p(n)]+[acc[h]["P"+str(i)]/max(1,n) for i in range(1,7)]+[acc[h]["L"+str(i)]/max(1,n) for i in range(3)]+[acc[h]["LEFT"]/max(1,n),acc[h]["RIGHT"]/max(1,n)];out.append(v)
 a=np.asarray(out,float);sd=a.std(axis=0);sd[sd<1e-12]=1;return (a-a.mean(axis=0))/sd
def greedy(a,b):
 an=np.linalg.norm(a,axis=1);bn=np.linalg.norm(b,axis=1);sim=a@b.T/np.maximum(1e-12,an[:,None]*bn[None,:]);cand=sorted(((float(sim[i,j]),i,j) for i in range(len(a)) for j in range(len(b))),reverse=True);ui=set();uj=set();vals=[]
 for v,i,j in cand:
  if i not in ui and j not in uj:ui.add(i);uj.add(j);vals.append(v)
  if len(vals)==min(len(a),len(b)):break
 return sum(vals)/len(vals)
def alignment(rows):
 regs=sorted({x["register"] for x in rows});vals=[]
 for i,a in enumerate(regs):
  for b in regs[i+1:]:
   ar=[x for x in rows if x["register"]==a];br=[x for x in rows if x["register"]==b];ap=[x for x,_ in Counter(x["inferred_host"] for x in ar).most_common(100)];bp=[x for x,_ in Counter(x["inferred_host"] for x in br).most_common(100)];vals.append(greedy(signature(ar,ap),signature(br,bp)))
 return sum(vals)/len(vals)

def main():
 checks=[]
 def ck(v,n):assert v,n;checks.append(n)
 d=json.loads(DESIGN.read_text());res=json.loads(RESULT.read_text());rows,census=panel();table=read(TABLE);places=read(PLACEMENT);ops=read(OPERATIONS);counters=read(COUNTER)
 ck(d["status"]=="FROZEN_BEFORE_VOYNICH_FINGERPRINT_SCORING","design_status");ck(res["controls_frozen_exactly_as_published"] and not res["build_b3"],"controls_frozen_no_b3");ck(census==res["census"] and census["groups"]==8448 and census["lines"]==1143 and census["folios"]==91,"census")
 c,items,left,right=discovery(rows);v={**recurrence(rows),**compat(set(c),left,right)};short,same,external=short_sub(rows);v.update({"short_host_mass":short,"same_group_substitution_cosine":same,"external_substitution_cosine":external,"next_host_gain_bits":held(rows,"NEXT_HOST"),"whole_line_gain_bits":held(rows,"WHOLE_LINE")});prec,rec=closure(rows);v.update({"right_marked_record_end_precision":prec,"record_end_right_mark_recall":rec,"register_alignment_mean":alignment(rows)})
 for k,value in v.items():ck(abs(float(res["voynich"][k])-float(value))<1e-11,"voynich_"+k)
 checks=list(dict.fromkeys(checks));selected={(x["side"],x["operation"]):x for x in ops};ck(len(left)==len(right)==12 and len(selected)==24,"operation_counts");ck([x["operation"] for x in ops if x["side"]=="LEFT"]==left and [x["operation"] for x in ops if x["side"]=="RIGHT"]==right,"operation_identity")
 ck(len(table)==18 and len(places)==18 and len(counters)==8,"output_rows");ck(all(x["voynich"]=="NA_NO_ORACLE" for x in table if x["axis"]=="HOST_RECOVERY"),"no_oracle")
 tmap={(x["axis"],x["metric"]):x for x in table};ck(tmap["LEFT_RIGHT_COMPATIBILITY","compatibility_density"]["placement"]=="FACTORIAL_B_LIKE" and tmap["LEFT_RIGHT_COMPATIBILITY","null_excess"]["placement"]=="B2_LIKE","compatibility_placements");ck(tmap["NEXT_HOST","held_gain_bits"]["placement"]=="OUTSIDE_SYNTHETIC_RANGE" and tmap["WHOLE_LINE","held_gain_bits"]["placement"]=="FACTORIAL_B_LIKE_DIRECTION","context_placements");ck(all(x["placement"]=="UNRESOLVED_NOT_DIRECTLY_COMPARABLE" for x in table if x["axis"] in {"HOST_RECOVERY","CLOSURE","REGISTER_ALIGNMENT"}),"unresolved_axes")
 ck(res["direct_outside_metrics"]==["HOST_RECURRENCE_PROXY|recurrent_host_mass","HOST_RECURRENCE_PROXY|cross_folio_host_mass","LEFT_RIGHT_COMPATIBILITY|null_density","SHORT_HOST_STRUCTURE|length_2_3_mass","EXTERNAL_SUBSTITUTION|mean_delta_cosine"],"direct_outside");ck(res["direction_outside_metrics"]==["NEXT_HOST|held_gain_bits"],"direction_outside")
 ck(all(sha(R/k)==v for k,v in res["inputs"].items()) and all(sha(R/k)==v for k,v in res["outputs"].items()),"artifact_hashes");ck(sha(REPORT)==res["documents"][REPORT.name] and sha(PRODUCER)==res["implementation"][PRODUCER.name],"document_implementation_hashes");stored=res.pop("result_content_sha256");ck(csha(res)==stored,"result_content_hash");ck(res["chronology"]=={"design_commit":"0414725","scored_after_public_design_freeze":True},"chronology");ck(not res["f84r_access"] and res["f84_rows_retained"]==0 and not any(x["page"].startswith("f84") for x in rows),"f84_seal");ck(res["no_composite"] and res["no_threshold_tuning"],"no_composite_tuning");ck(res["synthetic_control_level"]=="GDT173_REPORT_PRIMARY_SURFACE_ONLY","surface_control_level")
 checks=list(dict.fromkeys(checks));out={"schema":"GDT174_VOYNICH_CALIBRATED_FINGERPRINT_VALIDATION_V1","status":"PASS_INDEPENDENT_AXIS_FINGERPRINT_RECONSTRUCTION","checks_passed":len(checks),"checks_failed":0,"checks":checks,"eligible_groups":len(rows),"eligible_lines":census["lines"],"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"f84r_access":False};out["validation_content_sha256"]=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")
if __name__=="__main__":main()
