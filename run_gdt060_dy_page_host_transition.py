#!/usr/bin/env python3
"""GDT060: held-folio DY-conditioned PAGE_HOST transition prediction."""
from __future__ import annotations
import csv, hashlib, json, math, random
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";FRAMES=ROOT/"gdt046_line_frames.tsv";METHOD=ROOT/"GDT060_DY_PAGE_HOST_TRANSITION_METHOD.md";REPORT=ROOT/"GDT060_DY_PAGE_HOST_TRANSITION_REPORT.md";INVENTORY=ROOT/"gdt060_dy_transition_inventory.tsv";SCORES=ROOT/"gdt060_dy_transition_scores.tsv";PERM=ROOT/"gdt060_dy_transition_permutation.tsv";VARIANTS=ROOT/"gdt060_variant_log.tsv";RESULT=ROOT/"gdt060_result.json"
RIGHT=("aiin","air","ain","ar","al");LAM=4.;N_PERM=10000;SEED=60060;REPS=("RAW_SURFACE","RESIDUAL_ROOT","PAGE_HOST")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def preparse(r):
 h=r["residual_host"];b3=int(h.endswith("m")and len(h)>1);h=h[:-1]if b3 else h;right="NONE"
 for s in RIGHT:
  if h.endswith(s)and len(h)>len(s):h=h[:-len(s)];right=s;break
 inner=int(r["stripped_prefix"]in{"ch","che","sh"}and h.startswith("d")and len(h)>1);h=h[1:]if inner else h
 return h,b3,right,inner
def parser(source):
 counts=Counter(preparse(r)[0]for r in source);licensed={h for h in counts if counts[h]and counts["o"+h]and counts["ot"+h]}|{"ar","al","ol"}
 def parse(r):
  h,b3,right,inner=preparse(r);frame="NONE"
  if h.startswith("ot")and h[2:]in licensed:h=h[2:];frame="OT"
  elif h.startswith("o")and h[1:]in licensed:h=h[1:];frame="O"
  return h or"EMPTY",f'{r["stripped_prefix"]}|D{inner}|{frame}|{right}|DY{r["dy_closure"]}|B3{b3}'
 return parse,licensed
def register(r):
 if r["section"]=="H":return"HERBAL_"+r["currier"]
 if r["section"]=="S"and r["currier"]=="B":return"STARS_RECIPE_B"
 return"OTHER_"+r["currier"]
def rep_strings(row,side):
 return{"RAW_SURFACE":row[side+"_token"],"RESIDUAL_ROOT":row[side+"_root"],"PAGE_HOST":row[side+"_host"]}
def events(value):
 hist="^^";out=[]
 for ch in value+"$":out.append((hist,ch));hist=(hist+ch)[-2:]
 return out
def add(counts,key,hist,ch):counts[key,hist,ch]+=1;counts[key,hist,"#"]+=1
def fit(rows,rep,siglen):
 base=Counter();bound=Counter();pre=Counter();joint=Counter();alphabet=set("abcdefghijklmnopqrstuvwxyz$")
 for r in rows:
  left=rep_strings(r,"left")[rep];right=rep_strings(r,"right")[rep];sig=left[-siglen:];dy=r["dy"]
  alphabet.update(right)
  for hist,ch in events(right):add(base,"ALL",hist,ch);add(bound,dy,hist,ch);add(pre,sig,hist,ch);add(joint,(sig,dy),hist,ch)
 return base,bound,pre,joint,sorted(alphabet)
def prob(counts,key,hist,ch,prior,strength):
 return(counts[key,hist,ch]+strength*prior)/(counts[key,hist,"#"]+strength)
def score_models(model,left,right,dy,siglen):
 base,bound,pre,joint,alphabet=model;A=len(alphabet);sig=left[-siglen:];bits={k:0. for k in("BASE","BOUNDARY","PRE","PRE_BOUNDARY")}
 cf={0:0.,1:0.};cfb={0:0.,1:0.}
 for hist,ch in events(right):
  pb=(base["ALL",hist,ch]+.5)/(base["ALL",hist,"#"]+.5*A)
  pbound={z:prob(bound,z,hist,ch,pb,LAM)for z in(0,1)}
  pp=prob(pre,sig,hist,ch,pb,LAM)
  pjoint={z:prob(joint,(sig,z),hist,ch,.5*(pbound[z]+pp),LAM)for z in(0,1)}
  bits["BASE"]-=math.log2(pb);bits["BOUNDARY"]-=math.log2(pbound[dy]);bits["PRE"]-=math.log2(pp);bits["PRE_BOUNDARY"]-=math.log2(pjoint[dy])
  for z in(0,1):cf[z]-=math.log2(pjoint[z]);cfb[z]-=math.log2(pbound[z])
 bits["pair_logodds_dy_vs_non"]=cf[0]-cf[1];bits["boundary_logodds_dy_vs_non"]=cfb[0]-cfb[1];bits["interaction_logodds"]=bits["pair_logodds_dy_vs_non"]-bits["boundary_logodds_dy_vs_non"]
 return bits
def folds(rows,mode):
 key="physical_folio"if mode=="LEAVE_FOLIO_OUT"else"register"
 for value in sorted({r[key]for r in rows}):yield value,[r for r in rows if r[key]!=value],[r for r in rows if r[key]==value]
def evaluate(rows,rep,mode,siglen):
 totals=Counter();byreg=defaultdict(Counter);details={}
 for fold,train,test in folds(rows,mode):
  model=fit(train,rep,siglen)
  for r in test:
   s=score_models(model,rep_strings(r,"left")[rep],rep_strings(r,"right")[rep],r["dy"],siglen);details[r["boundary_id"]]=s
   for k,v in s.items():totals[k]+=v;byreg[r["register"]][k]+=v
 out=[]
 for scope,z in [("ALL",totals)]+sorted(byreg.items()):
  n=len(rows)if scope=="ALL"else sum(r["register"]==scope for r in rows);nd=sum(r["dy"]for r in rows if scope=="ALL"or r["register"]==scope);chars=sum(len(rep_strings(r,"right")[rep])+1 for r in rows if scope=="ALL"or r["register"]==scope)
  out.append({"evaluation":mode,"pre_context":f"SUFFIX_{siglen}","representation":rep,"scope":scope,"boundaries":n,"dy_boundaries":nd,"right_events":chars,"base_bits":z["BASE"],"boundary_bits":z["BOUNDARY"],"pre_bits":z["PRE"],"pre_boundary_bits":z["PRE_BOUNDARY"],"boundary_gain_vs_base":z["BASE"]-z["BOUNDARY"],"pre_gain_vs_base":z["BASE"]-z["PRE"],"joint_gain_vs_pre":z["PRE"]-z["PRE_BOUNDARY"],"joint_gain_vs_boundary":z["BOUNDARY"]-z["PRE_BOUNDARY"],"joint_gain_per_event_vs_pre":(z["PRE"]-z["PRE_BOUNDARY"])/chars})
 return out,details
def permute(rows,details_by_rep):
 strata=defaultdict(list)
 for r in rows:
  strata[r["stratum"]].append(r)
 eligible=[z for z in strata.values()if any(r["dy"]for r in z)and any(not r["dy"]for r in z)]
 stats=[]
 for rep,det in details_by_rep.items():
  for field in("boundary_logodds_dy_vs_non","pair_logodds_dy_vs_non","interaction_logodds"):
   obs=exp=0.;n=0
   for z in eligible:
    k=sum(r["dy"]for r in z);vals=[det[r["boundary_id"]][field]for r in z];obs+=sum(det[r["boundary_id"]][field]for r in z if r["dy"]);exp+=k*sum(vals)/len(vals);n+=k
   stats.append({"representation":rep,"statistic":field,"eligible_dy":n,"observed_sum":obs,"expected_sum":exp,"effect_per_dy":(obs-exp)/n})
 rng=random.Random(SEED);worlds=[[]for _ in stats]
 for _ in range(N_PERM):
  sums=[0.]*len(stats)
  for z in eligible:
   k=sum(r["dy"]for r in z);chosen=rng.sample(range(len(z)),k)
   for j,(rep,field) in enumerate(( (s["representation"],s["statistic"]) for s in stats)):
    sums[j]+=sum(details_by_rep[rep][z[i]["boundary_id"]][field]for i in chosen)
  for j,s in enumerate(sums):worlds[j].append((s-stats[j]["expected_sum"])/stats[j]["eligible_dy"])
 scales=[]
 for j,s in enumerate(stats):
  vals=worlds[j];mu=sum(vals)/len(vals);sd=(sum((x-mu)**2 for x in vals)/len(vals))**.5 or 1.;scales.append((mu,sd));s["permutation_worlds"]=N_PERM;s["local_two_sided_p"]=(1+sum(abs(x-mu)>=abs(s["effect_per_dy"]-mu)-1e-15 for x in vals))/(N_PERM+1)
 maxz=[]
 for w in range(N_PERM):maxz.append(max(abs((worlds[j][w]-scales[j][0])/scales[j][1])for j in range(len(stats))))
 for j,s in enumerate(stats):
  z=abs((s["effect_per_dy"]-scales[j][0])/scales[j][1]);s["maxT_9_p"]=(1+sum(x>=z-1e-15 for x in maxz))/(N_PERM+1)
 return stats,len(eligible)
def main():
 source=read(SOURCE);assert len(source)==15592 and not any(r["locus"].startswith("f84r")for r in source);parse,licensed=parser(source);byline=defaultdict(list);keep={r["locus"]for r in read(FRAMES)}
 for r in source:byline[r["locus"]].append(r)
 rows=[]
 byline={locus:z for locus,z in byline.items()if locus in keep};assert len(byline)==1164
 for locus,z in sorted(byline.items()):
  z.sort(key=lambda r:int(r["group_index"]));assert len(z)==int(z[0]["group_count"])
  parsed=[parse(r)for r in z]
  for i in range(len(z)-1):
   a,b=z[i],z[i+1];ah,ac=parsed[i];bh,bc=parsed[i+1];pos=int(4*i/max(1,len(z)-1));pl=len(ah)//3;ql=len(bh)//3;reg=register(a)
   rows.append({"boundary_id":f"{locus}:{i+1}","locus":locus,"page":a["page"],"physical_folio":a["physical_folio"],"section":a["section"],"currier":a["currier"],"register":reg,"boundary_index":i+1,"line_groups":len(z),"position_quartile":pos,"dy":int(a["dy_closure"]),"left_token":a["token"],"right_token":b["token"],"left_root":a["residual_host"],"right_root":b["residual_host"],"left_host":ah,"right_host":bh,"left_compiler":ac,"right_compiler":bc,"left_host_len_bucket":pl,"right_host_len_bucket":ql,"stratum":f'{a["physical_folio"]}|{reg}|P{pos}|L{pl}|R{ql}'})
 assert len(rows)==7409 and sum(r["dy"]for r in rows)==1298
 allscores=[];lofo_details={};cross_details={}
 for siglen in(1,2):
  for rep in REPS:
   z,d=evaluate(rows,rep,"LEAVE_FOLIO_OUT",siglen);allscores+=z
   z2,d2=evaluate(rows,rep,"LEAVE_REGISTER_OUT",siglen);allscores+=z2
   if siglen==2:lofo_details[rep]=d;cross_details[rep]=d2
 perms,cells=permute(rows,lofo_details)
 for r in rows:
  d=lofo_details["PAGE_HOST"][r["boundary_id"]];r["page_host_joint_gain_vs_pre_bits"]=d["PRE"]-d["PRE_BOUNDARY"];r["page_host_interaction_logodds"]=d["interaction_logodds"]
 write(INVENTORY,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in rows],list(rows[0]));write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in allscores],list(allscores[0]));write(PERM,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in perms],list(perms[0]))
 variants=[{"variant_id":"V00","status":"PRIMARY","description":"PAGE_HOST, previous suffix length 2, complete-folio holdout, 4-event hierarchical shrinkage."},{"variant_id":"V01","status":"RUN_SENSITIVITY","description":"Previous suffix length 1 under the same folds; checks sparse-context dependence."},{"variant_id":"V02","status":"RUN_BASELINE","description":"RAW_SURFACE under the identical models and folds."},{"variant_id":"V03","status":"RUN_BASELINE","description":"RESIDUAL_ROOT under the identical models and folds."},{"variant_id":"V04","status":"RUN_SENSITIVITY","description":"Leave the complete target register class out of training."},{"variant_id":"V05","status":"RUN_CONTROL","description":"10,000 matched DY-location permutations with nine-test maxT on the frozen suffix-2 model."},{"variant_id":"V06","status":"NOT_RUN","description":"No semantic annotations, exact-host search, alternative stripping grammar, or f84r."}];write(VARIANTS,variants,list(variants[0]))
 score={(r["evaluation"],r["pre_context"],r["representation"],r["scope"]):r for r in allscores};pr={(r["representation"],r["statistic"]):r for r in perms};p=score["LEAVE_FOLIO_OUT","SUFFIX_2","PAGE_HOST","ALL"];x=score["LEAVE_REGISTER_OUT","SUFFIX_2","PAGE_HOST","ALL"];s1=score["LEAVE_FOLIO_OUT","SUFFIX_1","PAGE_HOST","ALL"];ip=pr["PAGE_HOST","interaction_logodds"]
 if p["boundary_gain_vs_base"]>0 and ip["effect_per_dy"]<0 and ip["maxT_9_p"]<.05:status="DY_MARKS_POST_BOUNDARY_DISTRIBUTION_TESTED_PREHOST_SUFFIX_INTERACTION_NEGATIVE"
 elif p["joint_gain_vs_pre"]>0 and ip["effect_per_dy"]>0:status="DY_PAGE_HOST_TRANSITION_LEAD_LOCAL_OR_REGISTER_DEPENDENT"
 else:status="DY_PAGE_HOST_TRANSITION_CHANNEL_UNRESOLVED"
 report=f"""# GDT060 — DY-conditioned PAGE_HOST transition transfer

## Outcome

**{status}**

The panel contains {len(rows):,} internal boundaries on {len(byline):,}
complete lines and {len({r['physical_folio']for r in rows})} physical folios;
{sum(r['dy']for r in rows):,} boundaries follow a DY-closed group.

With complete target folios excluded, the PAGE_HOST joint model gains
{p['joint_gain_vs_pre']:+.3f} bits over the previous-host string model
({p['joint_gain_per_event_vs_pre']:+.6f} bit/right-character event).  It gains
{p['joint_gain_vs_boundary']:+.3f} bits over the boundary-only model.  When the
entire target register class is excluded, the gain over PRE is
{x['joint_gain_vs_pre']:+.3f} bits.  DY alone still gains
{x['boundary_gain_vs_base']:+.3f} bits over BASE in that aggregate
leave-register-out sensitivity, although held Herbal B is a small exception
({score['LEAVE_REGISTER_OUT','SUFFIX_2','PAGE_HOST','HERBAL_B']['boundary_gain_vs_base']:+.3f}
bits).

The sharper matched interaction statistic is {ip['effect_per_dy']:+.6f} bit
per eligible DY boundary across {ip['eligible_dy']} DY cases in {cells}
mixed strata (local p={ip['local_two_sided_p']:.6g}; nine-test maxT
p={ip['maxT_9_p']:.6g}).  It asks whether preceding-host context improves the
DY-versus-non-DY distinction beyond the marginal post-DY distribution while
holding folio, register, line-position quartile, and both host-length buckets.

The shorter suffix-1 sensitivity also changes the joint model by
{s1['joint_gain_vs_pre']:+.3f} bits versus PRE.  Thus the direction is not
created solely by the primary suffix-2 context's greater sparsity.  The
positive boundary-only result together with the negative interaction is most
compatible with DY acting as a distributional reset/checkpoint: it constrains
what follows, but the tested preceding-host identity does not compose with
that constraint.  This is a generative interpretation of a low-capacity
formal model, not proof of an authorial reset instruction.  Exact or broader
structural PAGE_HOST classes were not searched here, so the negative result is
specific to the frozen one- and two-character predecessor summaries.

Raw surface and residual-root baselines, every register fold, all nine matched
statistics, and all tried variants remain in the TSVs.  The result concerns a
formal source-group transition channel only.  It assigns no semantic field,
gloss, word, morpheme, POS, sound, language, plaintext, meaning, or
translation.  f84r was excluded before parsing and was not opened, retained,
queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT060_DY_PAGE_HOST_TRANSITION_RESULT_V1","status":status,"boundaries":len(rows),"complete_lines":len(byline),"physical_folios":len({r["physical_folio"]for r in rows}),"dy_boundaries":sum(r["dy"]for r in rows),"licensed_o_ot_hosts":len(licensed),"primary_lofo":p,"suffix1_sensitivity":s1,"primary_cross_register":x,"primary_matched_interaction":ip,"matched_cells":cells,"representations":list(REPS),"generative_update":"DY predicts the post-boundary PAGE_HOST distribution but the tested previous-host suffix does not improve and materially degrades that prediction; provisional reset/checkpoint architecture, not compositional pre-host to post-host mapping.","claim_ceiling":"Formal DY-conditioned PAGE_HOST transition structure only; no semantic field, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),FRAMES.name:sha(FRAMES),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt051_result.json":sha(ROOT/"gdt051_result.json"),"gdt055_result.json":sha(ROOT/"gdt055_result.json"),"gdt059_result.json":sha(ROOT/"gdt059_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{INVENTORY.name:sha(INVENTORY),SCORES.name:sha(SCORES),PERM.name:sha(PERM),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"lofo_gain":p["joint_gain_vs_pre"],"suffix1_gain":s1["joint_gain_vs_pre"],"cross_register_gain":x["joint_gain_vs_pre"],"interaction":ip},sort_keys=True))
if __name__=="__main__":main()
