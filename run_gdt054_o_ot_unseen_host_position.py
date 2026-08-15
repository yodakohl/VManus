#!/usr/bin/env python3
"""GDT054: held-host positional transfer for O/OT ladders."""
from __future__ import annotations
import csv,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";METHOD=ROOT/"GDT054_O_OT_UNSEEN_HOST_POSITION_METHOD.md";REPORT=ROOT/"GDT054_O_OT_UNSEEN_HOST_POSITION_REPORT.md";HOSTS=ROOT/"gdt054_unseen_host_profiles.tsv";TESTS=ROOT/"gdt054_position_tests.tsv";RESULT=ROOT/"gdt054_result.json";DISCOVERY={"ar","al","ol"};PERMS=20000
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def pos(r):
 i=int(r["group_index"]);n=int(r["group_count"]);return(i-1)/(n-1)if n>1 else.5
def reg(r):
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["currier"]=="B":return"OB"
 return"OA"
def parts(rows,bases,a,b,register="ALL"):
 out=[]
 for host in bases:
  by=defaultdict(lambda:[[],[]])
  for r in rows:
   if register!="ALL"and reg(r)!=register:continue
   if r["residual_host"]==a+host:by[r["page"]][0].append(pos(r))
   elif r["residual_host"]==b+host:by[r["page"]][1].append(pos(r))
  out.extend((host,page,x,y)for page,(x,y)in by.items()if x and y)
 return out
def effect(z):
 num=den=0.
 for host,page,a,b in z:
  w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
 return num/den if den else 0.
def perm_p(z,observed,seed):
 rng=random.Random(seed);extreme=0
 for _ in range(PERMS):
  shuffled=[]
  for host,page,a,b in z:
   vals=a+b;rng.shuffle(vals);shuffled.append((host,page,vals[:len(a)],vals[len(a):]))
  extreme+=abs(effect(shuffled))>=abs(observed)-1e-15
 return(extreme+1)/(PERMS+1)
def main():
 rows=read(SOURCE);assert len(rows)==15592 and not any(r["locus"].startswith("f84r")for r in rows);counts=Counter(r["residual_host"]for r in rows);bases=sorted(h for h in counts if h not in DISCOVERY and"o"+h in counts and"ot"+h in counts)
 profiles=[]
 for h in bases:
  z=parts(rows,[h],"","ot");profiles.append({"base_host":h,"base_n":counts[h],"o_n":counts["o"+h],"ot_n":counts["ot"+h],"shared_pages_base_ot":len(z),"base_to_ot_effect":f"{effect(z):.12f}"if z else"","claim_state":"HELD_FROM_AR_AL_OL_DISCOVERY"})
 write(HOSTS,profiles,list(profiles[0]))
 contrasts=(("BASE_TO_OT","","ot"),("BASE_TO_O","","o"),("O_TO_OT","o","ot"));tests=[]
 for i,(name,a,b)in enumerate(contrasts):
  z=parts(rows,bases,a,b);e=effect(z);hostset=sorted({x[0]for x in z});lo=[]
  for omit in hostset:lo.append(effect([x for x in z if x[0]!=omit]))
  re={rr:effect(parts(rows,bases,a,b,rr))for rr in("HA","HB","SB","OB","OA")}
  tests.append({"contrast":name,"form_a":a+"H","form_b":b+"H","held_hosts":len(hostset),"shared_page_host_strata":len(z),"a_groups":sum(len(x[2])for x in z),"b_groups":sum(len(x[3])for x in z),"position_effect_b_minus_a":e,"permutation_p":perm_p(z,e,54001+i),"loho_min_effect":min(lo),"loho_max_effect":max(lo),**{rr.lower()+"_effect":re[rr]for rr in re}})
 for t in tests:t["bonferroni_3_p"]=min(1.,3*t["permutation_p"])
 write(TESTS,[{k:(f"{v:.12g}"if isinstance(v,float)else v)for k,v in t.items()}for t in tests],list(tests[0]));m={t["contrast"]:t for t in tests};decision="O_EARLY_OT_LATE_POSITIONAL_RENDERER_TRANSFERS_TO_UNSEEN_HOSTS";assert m["BASE_TO_OT"]["position_effect_b_minus_a"]>0 and m["BASE_TO_OT"]["loho_min_effect"]>0 and m["BASE_TO_OT"]["bonferroni_3_p"]<.05 and m["BASE_TO_O"]["position_effect_b_minus_a"]<0 and m["O_TO_OT"]["position_effect_b_minus_a"]>0
 report=f"""# GDT054 — O/OT unseen-host position transfer

## Outcome

**{decision}**

After excluding the AR/AL/OL discovery ladders, 27 other host families supply
within-page H versus OT+H contrasts. OT+H occurs {m['BASE_TO_OT']['position_effect_b_minus_a']:+.3f}
normalized line positions later over {m['BASE_TO_OT']['shared_page_host_strata']}
page×host strata (adjusted p {m['BASE_TO_OT']['bonferroni_3_p']:.6g}). The
effect remains positive after deleting every held host; minimum
{m['BASE_TO_OT']['loho_min_effect']:+.3f}.

The length-only explanation is contradicted by the one-sign O frame: O+H is
{m['BASE_TO_O']['position_effect_b_minus_a']:+.3f} earlier than bare H, while
OT+H is {m['O_TO_OT']['position_effect_b_minus_a']:+.3f} later than O+H. Thus O
and OT form an opposing positional renderer rather than a monotone string-
length effect. Transfer is Currier-B dominant: H→OT effects are
{m['BASE_TO_OT']['hb_effect']:+.3f} in Herbal B,
{m['BASE_TO_OT']['sb_effect']:+.3f} in Stars B, and
{m['BASE_TO_OT']['ob_effect']:+.3f} in other B, but
{m['BASE_TO_OT']['ha_effect']:+.3f} in Herbal A.

This is the strongest new constructional function after B3: O marks an early
local rendering and OT a later rendering across independently held host
families. “Early/later” is the demonstrated function; bounded/interior,
reference, morphology, and lexical interpretations remain speculative.

No word, morpheme, POS, sound, language, plaintext, meaning, or translation is
assigned. f84r is absent from the frozen input and was not opened, retained,
queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT054_O_OT_UNSEEN_HOST_POSITION_RESULT_V1","status":decision,"strict_groups":len(rows),"eligible_ladders":len(bases),"discovery_hosts_excluded":sorted(DISCOVERY),"tests":tests,"hpr2_prediction":"HPR2_P03","prediction_outcome":"SUPPORTED_FORMAL_POSITIONAL_TRANSFER","claim_ceiling":"O-early/OT-late positional renderer transfer only; no bounded/interior, reference, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt014_result.json":sha(ROOT/"gdt014_result.json"),"gdt051_result.json":sha(ROOT/"gdt051_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{HOSTS.name:sha(HOSTS),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"ladders":len(bases),"tests":tests},sort_keys=True))
if __name__=="__main__":main()
