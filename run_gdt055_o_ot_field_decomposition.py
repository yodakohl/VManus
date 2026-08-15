#!/usr/bin/env python3
"""GDT055: locate O/OT positional effects between versus within DY fields."""
from __future__ import annotations
import csv,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";METHOD=ROOT/"GDT055_O_OT_FIELD_DECOMPOSITION_METHOD.md";REPORT=ROOT/"GDT055_O_OT_FIELD_DECOMPOSITION_REPORT.md";OCC=ROOT/"gdt055_complete_line_o_ot_contexts.tsv";TESTS=ROOT/"gdt055_field_decomposition_tests.tsv";RESULT=ROOT/"gdt055_result.json";DISCOVERY={"ar","al","ol"};FEATURES=("normalized_field_index","normalized_within_field_position","field_start","after_dy");PERMS=10000
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def inventory(source):
 by=defaultdict(list)
 for r in source:by[r["locus"]].append(r)
 out=[]
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)!=n or {int(r["group_index"])for r in line}!=set(range(1,n+1)):continue
  fields=[];cur=[]
  for i,r in enumerate(line):
   cur.append((i,r))
   if r["record_state"]=="DY_RESOLUTION":fields.append(cur);cur=[]
  if cur:fields.append(cur)
  for fi,field in enumerate(fields):
   for j,(i,r)in enumerate(field):out.append({"locus":locus,"page":r["page"],"physical_folio":r["physical_folio"],"register":r["section"]+"|"+r["currier"],"group_index":i+1,"group_count":n,"token":r["token"],"residual_host":r["residual_host"],"field_index":fi+1,"field_count":len(fields),"position_in_field":j+1,"field_length":len(field),"normalized_field_index":fi/(len(fields)-1)if len(fields)>1 else.5,"normalized_within_field_position":j/(len(field)-1)if len(field)>1 else.5,"field_start":int(j==0),"after_dy":int(i>0 and line[i-1]["record_state"]=="DY_RESOLUTION")})
 return out
def parts(rows,bases,a,b,feature):
 out=[]
 for host in bases:
  by=defaultdict(lambda:[[],[]])
  for r in rows:
   if r["residual_host"]==a+host:by[r["page"]][0].append(float(r[feature]))
   elif r["residual_host"]==b+host:by[r["page"]][1].append(float(r[feature]))
  out.extend((host,page,x,y)for page,(x,y)in by.items()if x and y)
 return out
def effect(z):
 num=den=0.
 for host,page,a,b in z:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
 return num/den if den else 0.
def perm(z,obs,seed):
 rng=random.Random(seed);ext=0
 for _ in range(PERMS):
  q=[]
  for h,p,a,b in z:v=a+b;rng.shuffle(v);q.append((h,p,v[:len(a)],v[len(a):]))
  ext+=abs(effect(q))>=abs(obs)-1e-15
 return(ext+1)/(PERMS+1)
def main():
 source=read(SOURCE);assert len(source)==15592 and not any(r["locus"].startswith("f84r")for r in source);rows=inventory(source);assert len(rows)==8774;counts=Counter(r["residual_host"]for r in source);bases=sorted(h for h in counts if h not in DISCOVERY and"o"+h in counts and"ot"+h in counts)
 relevant=[r for r in rows if any(r["residual_host"]in{h,"o"+h,"ot"+h}for h in bases)];write(OCC,[{k:(f"{v:.12g}"if isinstance(v,float)else v)for k,v in r.items()}for r in relevant],list(relevant[0]))
 contrasts=(("BASE_TO_OT","","ot"),("BASE_TO_O","","o"),("O_TO_OT","o","ot"));tests=[]
 for ci,(name,a,b)in enumerate(contrasts):
  for fi,feature in enumerate(FEATURES):
   z=parts(rows,bases,a,b,feature);e=effect(z);hosts=sorted({x[0]for x in z});lo=[effect([x for x in z if x[0]!=h])for h in hosts]
   tests.append({"contrast":name,"feature":feature,"held_hosts":len(hosts),"shared_page_host_strata":len(z),"a_groups":sum(len(x[2])for x in z),"b_groups":sum(len(x[3])for x in z),"effect_b_minus_a":e,"permutation_p":perm(z,e,55000+ci*10+fi),"loho_min_effect":min(lo),"loho_max_effect":max(lo)})
 for t in tests:t["bonferroni_12_p"]=min(1.,12*t["permutation_p"])
 write(TESTS,[{k:(f"{v:.12g}"if isinstance(v,float)else v)for k,v in t.items()}for t in tests],list(tests[0]));get=lambda c,f:next(t for t in tests if t["contrast"]==c and t["feature"]==f);bf=get("BASE_TO_OT","normalized_field_index");bw=get("BASE_TO_OT","normalized_within_field_position");ba=get("BASE_TO_OT","after_dy");oe=get("BASE_TO_O","normalized_within_field_position");decision="OT_IS_LATER_FIELD_POST_DY_RENDERER_O_IS_EARLY_INTRAFIELD_RENDERER";assert bf["effect_b_minus_a"]>0 and bf["bonferroni_12_p"]<.05 and bf["loho_min_effect"]>0 and abs(bw["effect_b_minus_a"])<.03 and ba["effect_b_minus_a"]>0 and oe["effect_b_minus_a"]<0
 report=f"""# GDT055 — O/OT field decomposition

## Outcome

**{decision}**

On 8,774 complete-line groups, the held-host OT shift is primarily between
fields. OT+H lies {bf['effect_b_minus_a']:+.3f} normalized field indices later
than H across {bf['shared_page_host_strata']} page×host strata (12-test
adjusted p {bf['bonferroni_12_p']:.6g}; leave-one-host minimum
{bf['loho_min_effect']:+.3f}). Its within-field shift is only
{bw['effect_b_minus_a']:+.3f}.

OT also has an immediate-after-DY excess of {ba['effect_b_minus_a']:+.3f}.
By contrast O+H moves {oe['effect_b_minus_a']:+.3f} earlier inside its field.
The O/OT opposition therefore decomposes into an early intrafield O renderer
and a later-field/post-checkpoint OT renderer. This is stronger and more
specific than the earlier “local frame” wording.

The demonstrated function is relative record placement. It does not establish
that OT means later, after, inside, bounded, or continuation in any language;
those remain analogies. No word, morpheme, POS, sound, language, plaintext,
meaning, or translation is assigned. f84r is absent from the input and was not
opened, retained, queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT055_O_OT_FIELD_DECOMPOSITION_RESULT_V1","status":decision,"complete_groups":len(rows),"eligible_ladders":len(bases),"tests":tests,"claim_ceiling":"Transferable formal placement: O early/intrafield and OT later-field/post-DY; no lexical later/after/inside/bounded meaning, word, morpheme, POS, sound, language, plaintext, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt054_result.json":sha(ROOT/"gdt054_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"groups":len(rows),"field":bf,"within":bw,"after_dy":ba,"o_within":oe},sort_keys=True))
if __name__=="__main__":main()
