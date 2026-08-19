#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,itertools,json,math,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt369_order_preserving_geometry_null';ART=EXP/'artifacts';G=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry/artifacts';PANEL=G/'gdt368_formal_panel.tsv';FEATURES=G/'gdt368_feature_manifest.tsv';ATLAS=G/'gdt368_candidate_atlas.tsv';FREEZE=ART/'gdt369_freeze.json';OUT=ART/'gdt369_null_results.tsv';RESULT=ART/'gdt369_result.json';SEED=int(hashlib.sha256(b'GDT369_ORDER_PRESERVING_GEOMETRY_NULL_V1').hexdigest()[:16],16);W=4096
def read(p):
 with p.open(newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,r):
 with p.open('w',newline='') as h:w=csv.DictWriter(h,list(r[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(r)
def cmi(x,y,a):
 n=len(y);z=0.0
 for q in sorted(set(a)):
  ii=[i for i,v in enumerate(a) if v==q];nn=len(ii);cx=Counter(x[i] for i in ii);cy=Counter(y[i] for i in ii);cc=Counter((x[i],y[i]) for i in ii)
  for (xx,yy),v in cc.items():z+=(v/n)*math.log2(v*nn/(cx[xx]*cy[yy]))
 return z
def allowed(rows,endpoint,array):
 rr=sorted(((i,r) for i,r in enumerate(rows) if r['array_id']==array),key=lambda z:int(z[1]['ordinal']));idx=[i for i,_ in rr];y=[r[endpoint] for _,r in rr];adj=sum(y[i]==y[i-1] for i in range(1,len(y)));vals=sorted({p for p in itertools.permutations(y) if sum(p[i]==p[i-1] for i in range(1,len(p)))==adj});return idx,vals
def reversal(rows,endpoint,array):
 idx=[i for i,r in sorted(enumerate(rows),key=lambda z:(z[1]['array_id'],int(z[1]['ordinal']))) if r['array_id']==array];y=tuple(rows[i][endpoint] for i in idx);return idx,sorted({y,tuple(reversed(y))})
def worlds(rows,endpoint,kind):
 arrays=sorted({r['array_id'] for r in rows});packs=[(allowed if kind=='adjacency' else reversal)(rows,endpoint,a) for a in arrays]
 for combo in itertools.product(*(p[1] for p in packs)):
  y=['']*len(rows)
  for (idx,_),vals in zip(packs,combo):
   for i,v in zip(idx,vals):y[i]=v
  yield y
def main():
 freeze=json.loads(FREEZE.read_text());rows=read(PANEL);fm=read(FEATURES);atlas=read(ATLAS);assert len(rows)==27 and len(fm)==27 and len(atlas)==81
 loci=[r['locus'] for r in rows];masks=[]
 for f in fm:
  s=set(f['loci_present'].split(','));masks.append((f['canonical_feature'],[int(l in s) for l in loci]))
 arrays=[r['array_id'] for r in rows];endpoints=['major_body_count','terminal_arm_count','dominant_hue'];observed={e:[cmi(x,[r[e] for r in rows],arrays) for _,x in masks] for e in endpoints};j=next(i for i,(q,x) in enumerate(masks) if q=='FAMILY_3GRAM:ACA');obs=observed['terminal_arm_count'][j];exact={};rev={};out=[]
 for e in endpoints:
  n=0;local=0;maxt=0;revs=[]
  for y in worlds(rows,e,'adjacency'):
   vals=[cmi(x,y,arrays) for _,x in masks];n+=1;maxt+=max(vals)>=max(observed[e])-1e-15
   if e=='terminal_arm_count':local+=vals[j]>=obs-1e-15
  exact[e]={'orbit':n,'endpoint_max_tail':maxt,'endpoint_max_p':maxt/n,'fixed_tail':local,'fixed_p':local/n if e=='terminal_arm_count' else None}
  rn=0;rl=0;rm=0
  for y in worlds(rows,e,'reversal'):
   vals=[cmi(x,y,arrays) for _,x in masks];rn+=1;rm+=max(vals)>=max(observed[e])-1e-15
   if e=='terminal_arm_count':rl+=vals[j]>=obs-1e-15
  rev[e]={'orbit':rn,'endpoint_max_tail':rm,'endpoint_max_p':rm/rn,'fixed_tail':rl,'fixed_p':rl/rn if e=='terminal_arm_count' else None}
  out.append({'endpoint':e.upper(),'adjacency_orbit':n,'observed_endpoint_max_cmi':f'{max(observed[e]):.12f}','adjacency_endpoint_max_tail':maxt,'adjacency_endpoint_max_p':f'{maxt/n:.12f}','reversal_orbit':rn,'reversal_endpoint_max_tail':rm,'reversal_endpoint_max_p':f'{rm/rn:.12f}'})
 rng=np.random.default_rng(SEED);sample_max=[]
 packs={e:[allowed(rows,e,a) for a in sorted({r['array_id'] for r in rows})] for e in endpoints}
 for w in range(W):
  mx=0.0
  for e in endpoints:
   y=['']*len(rows)
   for idx,vals in packs[e]:
    q=vals[int(rng.integers(0,len(vals)))]
    for i,v in zip(idx,q):y[i]=v
   mx=max(mx,max(cmi(x,y,arrays) for _,x in masks))
  sample_max.append(mx)
 global_tail=sum(v>=obs-1e-15 for v in sample_max);global_p=(global_tail+1)/(W+1);write(OUT,out)
 status='ORDER_MATCHED_ASSOCIATION_PERSISTS_BUT_DIRECTION_UNSTABLE' if global_p<=.05 else 'GDT368_ASSOCIATION_NOT_UNUSUAL_UNDER_ORDER_MATCHED_NULL'
 p={'schema':'GDT369_RESULT_V1','status':status,'fixed_candidate':{'endpoint':'TERMINAL_ARM_COUNT','formal_feature':'FAMILY_3GRAM:ACA','observed_cmi_bits_per_row':obs,'gdt368_direction_status':'UNSTABLE'},'adjacency_exact_local':exact['terminal_arm_count'],'adjacency_exact_endpoint_max':{'orbit':exact['terminal_arm_count']['orbit'],'tail':exact['terminal_arm_count']['endpoint_max_tail'],'p':exact['terminal_arm_count']['endpoint_max_p']},'adjacency_sampled_global_max':{'worlds':W,'tail':global_tail,'p':global_p},'reversal_exact_local':rev['terminal_arm_count'],'reversal_exact_endpoint_max':{'orbit':rev['terminal_arm_count']['orbit'],'tail':rev['terminal_arm_count']['endpoint_max_tail'],'p':rev['terminal_arm_count']['endpoint_max_p']},'endpoint_orbits':{e.upper():exact[e]['orbit'] for e in endpoints},'feature_or_endpoint_reselection':False,'semantics_assigned':False,'f84_accessed':False,'inputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (PANEL,FEATURES,ATLAS,FREEZE,EXP/'METHOD.md',EXP/'CORRECTION.md')},'outputs':{str(OUT.relative_to(ROOT)):sha256_file(OUT)},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'claim_ceiling':'ORDER_ROBUSTNESS_DIAGNOSTIC_OF_FIXED_DIRECTIONALLY_UNSTABLE_GDT368_ASSOCIATION'};p['content_hash']=hashlib.sha256(canonical_json_bytes(p)).hexdigest();RESULT.write_bytes(canonical_json_bytes(p))
if __name__=='__main__':main()
