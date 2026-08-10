#!/usr/bin/env python3
"""Aggregate-only CCT002 marginal-null capacity audit."""
from __future__ import annotations
import csv,hashlib,json,math,os,re,tempfile
from collections import Counter,defaultdict
from pathlib import Path
B=Path(__file__).resolve().parent;R=B/"results";SELF=Path(__file__).resolve();SPEC=B/"CCT002_MARGINAL_MERGER_CAPACITY_SPEC.md";PANEL=R/"cho_che_canonical_transfer_masked_panel.tsv";SOURCE=R/"source_separator_transcription.tsv";STOP=R/"cho_che_canonical_transfer_target_validation.json";OUT=R/"cct002_marginal_merger_capacity.json";REPORT=R/"cct002_marginal_merger_capacity.md";SITE=re.compile(r"(ch|sh)([oe])")
EXPECTED={PANEL:"8287193a0fcea0e9e7219153fee3d58b830bc60c5a37ee358dfa8abd18e8bf1a",SOURCE:"4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",STOP:"bf154c1668bb60a830202c80e155d74180c3375210acbb5270ab846b94a8ff38"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def install(j,m):
 if OUT.exists() or REPORT.exists():raise FileExistsError
 with tempfile.TemporaryDirectory(prefix="cct002c_",dir=R) as d:
  a,b=Path(d)/"j",Path(d)/"m";a.write_bytes(j);b.write_bytes(m);os.link(a,OUT)
  try:os.link(b,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def derive():
 masked=list(csv.DictReader(PANEL.open(),delimiter="\t"));src={x["source_group_id"]:x for x in csv.DictReader(SOURCE.open(),delimiter="\t")}
 if len(masked)!=2223 or len(src)!=115470:raise RuntimeError("source geometry")
 events=[]
 for x in masked:
  y=src[x["source_group_id"]];s=y["clean_ascii_fragments"];q=list(SITE.finditer(s))
  if len(q)!=1 or q[0].group(1)!=x["site_prefix"]:raise RuntimeError("site")
  i=q[0].end()-1;events.append((s[:i]+"X"+s[i+1:],s[i],s,len(s),q[0].group(1),i,x["physical_folio"],x["edition"]))
 return events
def main():
 for p,h in EXPECTED.items():
  if sha(p)!=h:raise SystemExit("hash "+p.name)
 stop=json.loads(STOP.read_text())
 if stop["decision"]!="STOP_INSUFFICIENT_CANONICAL_COLLISION_CAPACITY" or stop["score"]["capacity"]["collision_pairs"]!=35:raise SystemExit("stop binding")
 events=derive();members=defaultdict(dict);freq=Counter(x[2] for x in events)
 for c,r,t,n,p,i,_,_ in events:
  old=members[c].setdefault(r,t)
  if old!=t:raise RuntimeError("member")
 pairs=[]
 for c,m in members.items():
  if set(m)=={"o","e"}:
   o,e=m["o"],m["e"];sample=next(x for x in events if x[2]==o);pairs.append((o,e,(sample[3],sample[4],sample[5])))
 shells=defaultdict(list)
 for o,e,s in pairs:shells[s].append((o,e))
 movable=sum(len(v) for v in shells.values() if len(v)>=2);log_orbit=sum(math.lgamma(len(v)+1) for v in shells.values());pairtypes={x for p in pairs for x in p[:2]};pe=[x for x in events if x[2] in pairtypes]
 # Any additive member-only score is algebraically constant.  Check it on
 # actual log frequencies under the identity and reversed e-member orders.
 identity=sum(math.log1p(freq[o])+math.log1p(freq[e]) for o,e,_ in pairs);reversed_total=0.0
 for shell in sorted(shells,key=repr):
  v=sorted(shells[shell]);es=list(reversed([e for _,e in v]));reversed_total+=sum(math.log1p(freq[o])+math.log1p(freq[e]) for (o,_),e in zip(v,es))
 marginal_delta=abs(identity-reversed_total)
 hist=dict(sorted(Counter(len(v) for v in shells.values()).items()))
 gates={"cct001_exact_35_pairs":len(pairs)==35,"cct001_exact_586_events":len(pe)==586,"at_least_24_pairs":len(pairs)>=24,"at_least_16_movable_pairs":movable>=16,"at_least_8192_joint_bijections":log_orbit>=math.log(8192),"all_eight_leaves":{x[6] for x in pe}=={"f39","f55","f68","f73","f87","f89","f90","f96"},"all_three_readings":{x[7] for x in pe}=={"ZL3b","IT2a","RF1b"},"additive_marginals_invariant":marginal_delta<=1e-12,"no_scores_computed":True,"english_glosses_zero":True};passed=all(gates.values());status="PASS_CCT002_MARGINAL_NULL_CAPACITY" if passed else "STOP_CCT002_MARGINAL_NULL_CAPACITY";decision="AUTHORIZE_CCT002_SYNTHETIC_CALIBRATION_ONLY" if passed else "CLOSE_CCT002_UNSCORED"
 result={"experiment":"CCT002_MARGINAL_MERGER_CAPACITY","status":status,"decision":decision,"inputs":{p.name:sha(p) for p in (*EXPECTED,SPEC,SELF)},"target_rows":len(events),"collision_pairs":len(pairs),"collision_events":len(pe),"movable_pairs":movable,"shell_count":len(shells),"nontrivial_shell_count":sum(len(v)>=2 for v in shells.values()),"shell_size_histogram":{str(k):v for k,v in hist.items()},"log_joint_bijections":log_orbit,"at_least_8192_joint_bijections":log_orbit>=math.log(8192),"additive_marginal_max_abs_delta":marginal_delta,"gates":gates,"raw_types_emitted":0,"canonical_templates_emitted":0,"state_scores_computed":0,"merger_scores_computed":0,"english_glosses":0,"claim_ceiling":"Capacity only for a marginal-preserving synthetic null calibration; no canonical form word sound meaning plaintext or translation."};report=f"# CCT002 marginal-preserving merger capacity\n\nStatus: **{status}**\n\nThe aggregate audit retains **{len(pairs)}** collision pairs and **{movable}** movable pairs in **{len(shells)}** exact length/prefix/site shells; **{sum(len(v)>=2 for v in shells.values())}** shells are nontrivial. The joint log-orbit is **{log_orbit:.6f}** and additive member-frequency delta is **{marginal_delta:.3g}**. No association or merger score was computed. Decision: **{decision}**.\n";install((json.dumps(result,indent=2,sort_keys=True)+"\n").encode(),report.encode());print(json.dumps({"status":status,"decision":decision,"pairs":len(pairs),"movable":movable,"shells":len(shells),"nontrivial":sum(len(v)>=2 for v in shells.values()),"log_orbit":log_orbit,"gates":gates},sort_keys=True))
 if not passed:raise SystemExit(2)
if __name__=="__main__":main()
