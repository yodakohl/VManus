#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,itertools,json,math,sys
from collections import Counter
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt369_order_preserving_geometry_null';ART=EXP/'artifacts';G=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry/artifacts';W=4096;SEED=int(hashlib.sha256(b'GDT369_ORDER_PRESERVING_GEOMETRY_NULL_V1').hexdigest()[:16],16)
def read(p):
 with p.open(newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def cmi(x,y,a):
 n=len(y);z=0.0
 for q in sorted(set(a)):
  ii=[i for i,v in enumerate(a) if v==q];nn=len(ii);cx=Counter(x[i] for i in ii);cy=Counter(y[i] for i in ii);cc=Counter((x[i],y[i]) for i in ii)
  for (xx,yy),v in cc.items():z+=(v/n)*math.log2(v*nn/(cx[xx]*cy[yy]))
 return z
def packs(rows,e,reverse=False):
 out=[]
 for a in sorted({r['array_id'] for r in rows}):
  rr=sorted(((i,r) for i,r in enumerate(rows) if r['array_id']==a),key=lambda z:int(z[1]['ordinal']));idx=[i for i,_ in rr];y=tuple(r[e] for _,r in rr)
  if reverse:vals=sorted({y,tuple(reversed(y))})
  else:
   adj=sum(y[i]==y[i-1] for i in range(1,len(y)));vals=sorted({p for p in itertools.permutations(y) if sum(p[i]==p[i-1] for i in range(1,len(p)))==adj})
  out.append((idx,vals))
 return out
def allworld(rows,e,reverse=False):
 p=packs(rows,e,reverse)
 for c in itertools.product(*(x[1] for x in p)):
  y=['']*len(rows)
  for (idx,_),v in zip(p,c):
   for i,z in zip(idx,v):y[i]=z
  yield y
def main():
 rows=read(G/'gdt368_formal_panel.tsv');fm=read(G/'gdt368_feature_manifest.tsv');r=json.loads((ART/'gdt369_result.json').read_text());loci=[x['locus'] for x in rows];masks=[]
 for f in fm:
  s=set(f['loci_present'].split(','));masks.append((f['canonical_feature'],[int(x in s) for x in loci]))
 arrays=[x['array_id'] for x in rows];ends=['major_body_count','terminal_arm_count','dominant_hue'];observed={e:[cmi(x,[q[e] for q in rows],arrays) for _,x in masks] for e in ends};j=next(i for i,(q,x) in enumerate(masks) if q=='FAMILY_3GRAM:ACA');obs=observed['terminal_arm_count'][j];vals=[]
 for y in allworld(rows,'terminal_arm_count'):vals.append([cmi(x,y,arrays) for _,x in masks])
 local=sum(v[j]>=obs-1e-15 for v in vals);mx=sum(max(v)>=max(observed['terminal_arm_count'])-1e-15 for v in vals);rv=[]
 for y in allworld(rows,'terminal_arm_count',True):rv.append([cmi(x,y,arrays) for _,x in masks])
 rl=sum(v[j]>=obs-1e-15 for v in rv);rm=sum(max(v)>=max(observed['terminal_arm_count'])-1e-15 for v in rv);rng=np.random.default_rng(SEED);pp={e:packs(rows,e) for e in ends};g=0
 for w in range(W):
  mm=0
  for e in ends:
   y=['']*27
   for idx,q in pp[e]:
    v=q[int(rng.integers(0,len(q)))]
    for i,z in zip(idx,v):y[i]=z
   mm=max(mm,max(cmi(x,y,arrays) for _,x in masks))
  g+=mm>=obs-1e-15
 body=dict(r);d=body.pop('content_hash');checks=[len(rows)==len(masks)==27,all(not x['page'].startswith('f84') for x in rows),abs(obs-2/3)<1e-12,len(vals)==2880,local==72,mx==168,len(rv)==32,rl==rm==4,g==245,r['endpoint_orbits']=={'MAJOR_BODY_COUNT':2080,'TERMINAL_ARM_COUNT':2880,'DOMINANT_HUE':120},abs(r['adjacency_exact_local']['fixed_p']-.025)<1e-12,abs(r['adjacency_exact_endpoint_max']['p']-168/2880)<1e-12,abs(r['adjacency_sampled_global_max']['p']-246/4097)<1e-12,abs(r['reversal_exact_local']['fixed_p']-.125)<1e-12,r['status']=='GDT368_ASSOCIATION_NOT_UNUSUAL_UNDER_ORDER_MATCHED_NULL',not r['feature_or_endpoint_reselection'],not r['semantics_assigned'],not r['f84_accessed'],all(sha256_file(ROOT/k)==v for k,v in r['inputs'].items()),all(sha256_file(ROOT/k)==v for k,v in r['outputs'].items()),all(sha256_file(ROOT/k)==v for k,v in r['implementation'].items()),hashlib.sha256(canonical_json_bytes(body)).hexdigest()==d];assert all(checks);p={'schema':'GDT369_VALIDATION_V1','status':'PASS','checks_passed':sum(checks),'checks_total':len(checks),'result_sha256':sha256_file(ART/'gdt369_result.json'),'scope':'INDEPENDENT_ORDINAL_ORBITS_EXACT_ADJACENCY_REVERSAL_AND_SAMPLED_GLOBAL_REPLAY_HASHES_AND_F84'};(ART/'gdt369_validation.json').write_bytes(canonical_json_bytes(p));print(f'PASS {sum(checks)}/{len(checks)}')
if __name__=='__main__':main()
