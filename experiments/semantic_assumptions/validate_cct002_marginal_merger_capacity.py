#!/usr/bin/env python3
"""Independent aggregate reconstruction of CCT002 capacity."""
from __future__ import annotations
import csv,hashlib,json,math,os,re,tempfile
from collections import Counter,defaultdict
from pathlib import Path
B=Path(__file__).resolve().parent;R=B/"results";SELF=Path(__file__).resolve();SPEC=B/"CCT002_MARGINAL_MERGER_CAPACITY_SPEC.md";BUILDER=B/"build_cct002_marginal_merger_capacity.py";PANEL=R/"cho_che_canonical_transfer_masked_panel.tsv";SOURCE=R/"source_separator_transcription.tsv";PROD=R/"cct002_marginal_merger_capacity.json";PREPORT=R/"cct002_marginal_merger_capacity.md";OUT=R/"cct002_marginal_merger_capacity_validation.json";REPORT=R/"cct002_marginal_merger_capacity_validation.md";SITE=re.compile(r"(ch|sh)([oe])")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def install(j,m):
 if OUT.exists() or REPORT.exists():raise FileExistsError
 with tempfile.TemporaryDirectory(prefix="cct002v_",dir=R) as d:
  a,b=Path(d)/"j",Path(d)/"m";a.write_bytes(j);b.write_bytes(m);os.link(a,OUT)
  try:os.link(b,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 prod=json.loads(PROD.read_text());rows=list(csv.DictReader(PANEL.open(),delimiter="\t"));src={}
 for x in csv.DictReader(SOURCE.open(),delimiter="\t"):
  if x["source_group_id"] in src:raise AssertionError("duplicate")
  src[x["source_group_id"]]=x
 groups=defaultdict(dict);freq=Counter();meta={};coverage=[]
 for x in rows:
  y=src[x["source_group_id"]];s=y["clean_ascii_fragments"];q=list(SITE.finditer(s));assert len(q)==1;i=q[0].end()-1;c=s[:i]+"X"+s[i+1:];groups[c][s[i]]=s;freq[s]+=1;meta[s]=(len(s),q[0].group(1),i);coverage.append((s,x["physical_folio"],x["edition"]))
 pairs=[]
 for c,m in groups.items():
  if set(m)=={"o","e"}:pairs.append((m["o"],m["e"],meta[m["o"]]))
 shells=defaultdict(list)
 for o,e,k in pairs:shells[k].append((o,e))
 movable=sum(len(v) for v in shells.values() if len(v)>=2);logorbit=sum(math.lgamma(len(v)+1) for v in shells.values());types={x for p in pairs for x in p[:2]};pe=[x for x in coverage if x[0] in types];base=sum(math.log1p(freq[o])+math.log1p(freq[e]) for o,e,_ in pairs);alt=0
 for k in sorted(shells,key=repr):
  v=sorted(shells[k]);es=list(reversed([e for _,e in v]));alt+=sum(math.log1p(freq[o])+math.log1p(freq[e]) for (o,_),e in zip(v,es))
 computed={"target_rows":len(rows),"collision_pairs":len(pairs),"collision_events":len(pe),"movable_pairs":movable,"shell_count":len(shells),"nontrivial_shell_count":sum(len(v)>=2 for v in shells.values()),"shell_size_histogram":{str(k):v for k,v in sorted(Counter(len(v) for v in shells.values()).items())},"log_joint_bijections":logorbit,"at_least_8192_joint_bijections":logorbit>=math.log(8192),"additive_marginal_max_abs_delta":abs(base-alt)}
 checks=0
 for k,v in computed.items():
  if isinstance(v,float):assert abs(v-prod[k])<=1e-12
  else:assert v==prod[k]
  checks+=1
 gates={"cct001_exact_35_pairs":len(pairs)==35,"cct001_exact_586_events":len(pe)==586,"at_least_24_pairs":len(pairs)>=24,"at_least_16_movable_pairs":movable>=16,"at_least_8192_joint_bijections":logorbit>=math.log(8192),"all_eight_leaves":{x[1] for x in pe}==set(("f39","f55","f68","f73","f87","f89","f90","f96")),"all_three_readings":{x[2] for x in pe}==set(("ZL3b","IT2a","RF1b")),"additive_marginals_invariant":abs(base-alt)<=1e-12,"no_scores_computed":True,"english_glosses_zero":True};assert gates==prod["gates"] and all(gates.values());checks+=len(gates)
 assert prod["status"]=="PASS_CCT002_MARGINAL_NULL_CAPACITY" and prod["decision"]=="AUTHORIZE_CCT002_SYNTHETIC_CALIBRATION_ONLY" and prod["raw_types_emitted"]==prod["canonical_templates_emitted"]==prod["state_scores_computed"]==prod["merger_scores_computed"]==0;checks+=6
 inputs={p.name:sha(p) for p in (SPEC,BUILDER,PANEL,SOURCE,PROD,PREPORT,SELF)};result={"experiment":"CCT002_MARGINAL_MERGER_CAPACITY_VALIDATION","status":"PASS_INDEPENDENT_MARGINAL_NULL_CAPACITY","checks_passed":checks,"inputs":inputs,**computed,"gates":gates,"association_scores_computed":0,"english_glosses":0,"claim_ceiling":"Capacity validation only; no canonical form word sound meaning plaintext or translation."};report=f"# CCT002 capacity validation\n\n**PASS**: {checks} checks independently reconstruct **{len(pairs)}** collision pairs, **{movable}** movable pairs, shell/orbit capacity, exact marginal invariance, gates, and decision. No association score was computed.\n";install((json.dumps(result,indent=2,sort_keys=True)+"\n").encode(),report.encode());print(json.dumps({"status":result["status"],"checks":checks,"pairs":len(pairs),"movable":movable,"log_orbit":logorbit},sort_keys=True))
if __name__=="__main__":main()
