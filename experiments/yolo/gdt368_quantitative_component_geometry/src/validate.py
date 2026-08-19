#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,math,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import GuardedTSV,canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry';ART=EXP/'artifacts';ROOT_TARGET=ROOT/'experiments/yolo/gdt367_joint_cell_visual_acquisition/artifacts/gdt367_target_manifest.tsv';SOURCE=ROOT/'gdt002_exploratory_visual_formal_join.tsv';W=4096;SEED=int(hashlib.sha256(b'GDT368_QUANTITATIVE_COMPONENT_GEOMETRY_V1').hexdigest()[:16],16)
def read(p):
 with p.open(newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def fs(r):
 gs=r['group_family_expression'].split('|') if r['group_family_expression'] else [];o=set()
 for g in gs:
  for c in set(g):o.add('FAMILY_COMPONENT:'+c)
  for n in (2,3):
   for i in range(max(0,len(g)-n+1)):o.add(f'FAMILY_{n}GRAM:'+g[i:i+n])
 if gs:
  for n in (1,2,3):
   if len(gs[0])>=n:o.add(f'FIRST_GROUP_PREFIX_{n}:'+gs[0][:n])
   if len(gs[-1])>=n:o.add(f'LAST_GROUP_SUFFIX_{n}:'+gs[-1][-n:])
  o.add('EXACT_FAMILY_EXPRESSION:'+'|'.join(gs))
 s=int(r['symbol_count'])
 for n in (3,4,5):
  if s<=n:o.add(f'SYMBOL_COUNT_LE_{n}')
 for n in (6,8,10):
  if s>=n:o.add(f'SYMBOL_COUNT_GE_{n}')
 if len(gs)>=2:o.add('GROUP_COUNT_GE_2')
 if len(gs)>=3:o.add('GROUP_COUNT_GE_3')
 if r['strict_zero_alternative']=='0':o.add('READING_ALTERNATIVE_PRESENT')
 if r['internal_drawing_interruption']=='1':o.add('INTERNAL_BOUNDARY:DRAWING_INTERRUPTION')
 return o
def cmi(x,y,a):
 n=len(y);z=0.0
 for q in sorted(set(a)):
  ii=[i for i,v in enumerate(a) if v==q];nn=len(ii);cx=Counter(x[i] for i in ii);cy=Counter(y[i] for i in ii);c=Counter((x[i],y[i]) for i in ii)
  for (xx,yy),v in c.items():z+=(v/n)*math.log2(v*nn/(cx[xx]*cy[yy]))
 return z
def lofo(x,y,f):
 classes=sorted(set(y));tot=0;details=[]
 for held in sorted(set(f)):
  tr=[i for i,v in enumerate(f) if v!=held];te=[i for i,v in enumerate(f) if v==held];bc=Counter(y[i] for i in tr);xc=Counter((x[i],y[i]) for i in tr);xn=Counter(x[i] for i in tr);g=0
  for i in te:g+=math.log2(((xc[(x[i],y[i])]+.5)/(xn[x[i]]+.5*len(classes)))/((bc[y[i]]+.5)/(len(tr)+.5*len(classes))))
  tot+=g;details.append(f'{held}:{g:.6f}')
 return tot,';'.join(details)
def main():
 targets={r['locus']:r for r in read(ROOT_TARGET)};obs={r['gdt367_target_id']:r for r in read(ART/'gdt368_visual_observations.tsv')};panel=read(ART/'gdt368_formal_panel.tsv');features=read(ART/'gdt368_feature_manifest.tsv');atlas=read(ART/'gdt368_candidate_atlas.tsv');result=json.loads((ART/'gdt368_result.json').read_text())
 guard=GuardedTSV(SOURCE,selector_column='page',forbidden_prefixes=('f84',),forbidden_action='skip');src={r['locus']:r for r in guard if r['channel']=='CONTACT_GAP'};pr={r['locus']:r for r in panel}
 raw=defaultdict(set)
 for i,l in enumerate(sorted(targets)):
  for q in fs(src[l]):raw[q].add(i)
 eligible={q:frozenset(ii) for q,ii in raw.items() if len(ii)>=4 and 27-len(ii)>=4 and len({targets[sorted(targets)[i]]['physical_folio'] for i in ii})>=2 and len({targets[sorted(targets)[i]]['physical_folio'] for i in range(27) if i not in ii})>=2};masks=defaultdict(list)
 for q,m in eligible.items():masks[m].append(q)
 ordered=[]
 for m,aliases in sorted(masks.items(),key=lambda z:(len(z[0]),sorted(z[1])[0],sorted(z[0]))):ordered.append((sorted(aliases)[0],m))
 arrays=[pr[l]['array_id'] for l in sorted(targets)];folios=[pr[l]['physical_folio'] for l in sorted(targets)];endpoints=['MAJOR_BODY_COUNT','TERMINAL_ARM_COUNT','DOMINANT_HUE'];ys={e:[obs[targets[l]['gdt367_target_id']][e.lower()] for l in sorted(targets)] for e in endpoints};observed={e:[cmi([int(i in m) for i in range(27)],ys[e],arrays) for _,m in ordered] for e in endpoints};rng=np.random.default_rng(SEED);nulls={}
 groups=defaultdict(list)
 for i,a in enumerate(arrays):groups[a].append(i)
 for e in endpoints:
  y=ys[e];n=np.zeros((len(ordered),W))
  for w in range(W):
   yp=y.copy()
   for ii in groups.values():
    vals=[yp[i] for i in ii];rng.shuffle(vals)
    for i,v in zip(ii,vals):yp[i]=v
   for j,(_,m) in enumerate(ordered):n[j,w]=cmi([int(i in m) for i in range(27)],yp,arrays)
  nulls[e]=n
 maxall=np.maximum.reduce([np.max(nulls[e],axis=0) for e in endpoints]);j=next(i for i,(q,m) in enumerate(ordered) if q=='FAMILY_3GRAM:ACA');m=ordered[j][1];x=[int(i in m) for i in range(27)];y=ys['TERMINAL_ARM_COUNT'];oc=observed['TERMINAL_ARM_COUNT'][j];lp=(1+int(np.sum(nulls['TERMINAL_ARM_COUNT'][j]>=oc-1e-15)))/(W+1);mp=(1+int(np.sum(maxall>=oc-1e-15)))/(W+1);gain,details=lofo(x,y,folios);top=atlas[0]
 body=dict(result);digest=body.pop('content_hash');checks=[guard.stats.lines_seen==guard.stats.selected==80 and guard.stats.skipped_forbidden==0,len(src)==len(targets)==len(panel)==27,set(src)==set(targets)==set(pr),all(not r['page'].startswith('f84') for r in panel),all(pr[l]['group_family_expression']==src[l]['group_family_expression'] for l in src),len(raw)==174,len(ordered)==27,len(features)==27,len(atlas)==81,result['family_edition_stable_loci']==27,abs(oc-2/3)<1e-12,abs(float(top['conditional_mi_bits_per_row'])-oc)<1e-12,abs(float(top['local_p'])-lp)<1e-12,abs(float(top['maxT_p'])-mp)<1e-12,abs(float(top['lofo_gain_bits'])-gain)<1e-12,top['held_folio_details']==details,top['formal_feature']=='FAMILY_3GRAM:ACA',top['endpoint']=='TERMINAL_ARM_COUNT',top['array_direction_details']=='F100R_L2:0.500000;F89R2_L4:2.000000;F99V_L1:-1.000000;F99V_L2:1.000000',top['same_direction_mobile_arrays']=='3' and top['opposite_direction_mobile_arrays']=='1',top['label']=='UNSTABLE',result['interesting_exploratory_count']==0,result['status']=='ADJUSTED_ASSOCIATION_DIRECTIONALLY_UNSTABLE',not result['f84_accessed'],all(sha256_file(ROOT/k)==v for k,v in result['inputs'].items()),all(sha256_file(ROOT/k)==v for k,v in result['outputs'].items()),all(sha256_file(ROOT/k)==v for k,v in result['implementation'].items()),hashlib.sha256(canonical_json_bytes(body)).hexdigest()==digest]
 assert all(checks);p={'schema':'GDT368_VALIDATION_V1','status':'PASS','checks_passed':sum(checks),'checks_total':len(checks),'result_sha256':sha256_file(ART/'gdt368_result.json'),'independent_null_replay':True,'scope':'SOURCE_JOIN_FEATURE_LIBRARY_TOP_SCORE_LOFO_4096_WORLD_MAXT_DIRECTION_HASHES_AND_F84_GUARD'};(ART/'gdt368_validation.json').write_bytes(canonical_json_bytes(p));print(f'PASS {sum(checks)}/{len(checks)}')
if __name__=='__main__':main()
