#!/usr/bin/env python3
from __future__ import annotations

import csv, hashlib, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import GuardedTSV,canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry';ART=EXP/'artifacts'
TARGET=ROOT/'experiments/yolo/gdt367_joint_cell_visual_acquisition/artifacts/gdt367_target_manifest.tsv';OBS=ART/'gdt368_visual_observations.tsv';FORMAL=ROOT/'gdt002_exploratory_visual_formal_join.tsv';FREEZE=ART/'gdt368_scan_freeze.json'
PANEL=ART/'gdt368_formal_panel.tsv';FEATURES=ART/'gdt368_feature_manifest.tsv';ATLAS=ART/'gdt368_candidate_atlas.tsv';NULL=ART/'gdt368_null_results.tsv';COUNTER=ART/'gdt368_counterexamples.tsv';RESULT=ART/'gdt368_result.json'
WORLDS=4096;SEED=int(hashlib.sha256(b'GDT368_QUANTITATIVE_COMPONENT_GEOMETRY_V1').hexdigest()[:16],16)

def read(p):
 with p.open(newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows,fields=None):
 names=fields or list(rows[0]);
 with p.open('w',newline='') as h:w=csv.DictWriter(h,names,delimiter='\t',lineterminator='\n',extrasaction='ignore');w.writeheader();w.writerows(rows)
def features(r):
 groups=r['group_family_expression'].split('|') if r['group_family_expression'] else []
 out=set()
 for g in groups:
  for c in set(g):out.add('FAMILY_COMPONENT:'+c)
  for n in (2,3):
   for i in range(max(0,len(g)-n+1)):out.add(f'FAMILY_{n}GRAM:'+g[i:i+n])
 if groups:
  for n in (1,2,3):
   if len(groups[0])>=n:out.add(f'FIRST_GROUP_PREFIX_{n}:'+groups[0][:n])
   if len(groups[-1])>=n:out.add(f'LAST_GROUP_SUFFIX_{n}:'+groups[-1][-n:])
  out.add('EXACT_FAMILY_EXPRESSION:'+'|'.join(groups))
 s=int(r['symbol_count'])
 for n in (3,4,5):
  if s<=n:out.add(f'SYMBOL_COUNT_LE_{n}')
 for n in (6,8,10):
  if s>=n:out.add(f'SYMBOL_COUNT_GE_{n}')
 g=len(groups)
 if g>=2:out.add('GROUP_COUNT_GE_2')
 if g>=3:out.add('GROUP_COUNT_GE_3')
 if r.get('strict_zero_alternative')=='0':out.add('READING_ALTERNATIVE_PRESENT')
 if r.get('internal_drawing_interruption')=='1':out.add('INTERNAL_BOUNDARY:DRAWING_INTERRUPTION')
 return out
def cmi(x,y,arrays):
 n=len(y);total=0.0
 for a in sorted(set(arrays)):
  idx=[i for i,z in enumerate(arrays) if z==a];na=len(idx);cx=Counter(x[i] for i in idx);cy=Counter(y[i] for i in idx);cxy=Counter((x[i],y[i]) for i in idx)
  for (xx,yy),v in cxy.items():total+=(v/n)*math.log2(v*na/(cx[xx]*cy[yy]))
 return total
def cramers_v(x,y):
 n=len(y);xs=sorted(set(x));ys=sorted(set(y));cx=Counter(x);cy=Counter(y);cxy=Counter(zip(x,y));chi=0.0
 for xx in xs:
  for yy in ys:
   e=cx[xx]*cy[yy]/n
   if e:chi+=(cxy[(xx,yy)]-e)**2/e
 d=min(len(xs)-1,len(ys)-1)
 return math.sqrt(chi/(n*d)) if d>0 else 0.0
def lofo_gain(x,y,folios):
 classes=sorted(set(y));details=[];total=0.0;positive=0
 for held in sorted(set(folios)):
  tr=[i for i,f in enumerate(folios) if f!=held];te=[i for i,f in enumerate(folios) if f==held];bc=Counter(y[i] for i in tr);xc=Counter((x[i],y[i]) for i in tr);xn=Counter(x[i] for i in tr);g=0.0
  for i in te:
   p0=(bc[y[i]]+.5)/(len(tr)+.5*len(classes));p1=(xc[(x[i],y[i])]+.5)/(xn[x[i]]+.5*len(classes));g+=math.log2(p1/p0)
  total+=g;positive+=g>0;details.append(f'{held}:{g:.6f}')
 return total,positive,';'.join(details)
def direction(x,y,arrays,endpoint):
 if endpoint in {'MAJOR_BODY_COUNT','TERMINAL_ARM_COUNT'}:
  order={'MAJOR_BODY_COUNT':{'ONE':1,'TWO':2,'THREE_PLUS':3},'TERMINAL_ARM_COUNT':{'ZERO_ONE':0,'TWO_THREE':1,'FOUR_PLUS':2}}[endpoint]
  idx=[i for i,v in enumerate(y) if v in order];a=[order[y[i]] for i in idx if x[i]];b=[order[y[i]] for i in idx if not x[i]];d=(sum(a)/len(a) if a else 0)-(sum(b)/len(b) if b else 0);sgn=1 if d>=0 else -1;same=0;opp=0;parts=[]
  for ar in sorted(set(arrays)):
   ii=[i for i,z in enumerate(arrays) if z==ar and y[i] in order]
   p=[order[y[i]] for i in ii if x[i]];q=[order[y[i]] for i in ii if not x[i]]
   if not p or not q:continue
   z=sum(p)/len(p)-sum(q)/len(q);same+=z*sgn>0;opp+=z*sgn<0;parts.append(f'{ar}:{z:.6f}')
  return 'ORDERED_LEVEL',d,same,opp,';'.join(parts)
 states=sorted(set(y));best=None
 for s in states:
  a=[x[i] for i in range(len(x)) if y[i]==s];b=[x[i] for i in range(len(x)) if y[i]!=s];d=(sum(a)/len(a) if a else 0)-(sum(b)/len(b) if b else 0)
  cand=(abs(d),s,d)
  if best is None or cand>best:best=cand
 _,state,d=best;sgn=1 if d>=0 else -1;same=0;opp=0;parts=[]
 for a in sorted(set(arrays)):
  idx=[i for i,z in enumerate(arrays) if z==a]
  if len(set(x[i] for i in idx))<2 or len(set(y[i] for i in idx))<2:continue
  p=[x[i] for i in idx if y[i]==state];q=[x[i] for i in idx if y[i]!=state]
  if not p or not q:continue
  z=sum(p)/len(p)-sum(q)/len(q);same+=z*sgn>0;opp+=z*sgn<0;parts.append(f'{a}:{z:.6f}')
 return state,d,same,opp,';'.join(parts)

def main():
 freeze=json.loads(FREEZE.read_text());assert not freeze['formal_access_before_freeze'] and freeze['worlds']==WORLDS
 targets={r['locus']:r for r in read(TARGET)};obs={r['gdt367_target_id']:r for r in read(OBS)}
 guarded=GuardedTSV(FORMAL,selector_column='page',forbidden_prefixes=('f84',),forbidden_action='skip');all_formal=list(guarded);assert guarded.stats.skipped_forbidden==0
 formal={r['locus']:r for r in all_formal if r['channel']=='CONTACT_GAP'};assert len(formal)==27 and set(formal)==set(targets)
 endpoints=['MAJOR_BODY_COUNT','TERMINAL_ARM_COUNT','DOMINANT_HUE'];rows=[]
 for locus in sorted(targets):
  t=targets[locus];o=obs[t['gdt367_target_id']];f=formal[locus];row={'gdt367_target_id':t['gdt367_target_id'],'page':t['page'],'physical_folio':t['physical_folio'],'locus':locus,'array_id':t['array_id'],'ordinal':t['ordinal'],'contact_gap_state':t['contact_gap_state'],'major_body_count':o['major_body_count'],'terminal_arm_count':o['terminal_arm_count'],'dominant_hue':o['dominant_hue'],'family_expression':f['family_expression'],'group_family_expression':f['group_family_expression'],'symbol_count':f['symbol_count'],'group_count':f['group_count'],'boundary_expression':f['boundary_expression'],'internal_drawing_interruption':f['internal_drawing_interruption'],'strict_zero_alternative':f['strict_zero_alternative'],'alternative_sites':f['alternative_sites'],'family_edition_stable':f['family_edition_stable'],'member_edition_stable':f['member_edition_stable']};assert not row['page'].startswith('f84');rows.append(row)
 write(PANEL,rows)
 feat_loci=defaultdict(set)
 for i,r in enumerate(rows):
  for f in features(r):feat_loci[f].add(i)
 eligible={}
 for f,idx in feat_loci.items():
  if len(idx)<4 or len(rows)-len(idx)<4:continue
  yes={rows[i]['physical_folio'] for i in idx};no={rows[i]['physical_folio'] for i in range(len(rows)) if i not in idx}
  if len(yes)>=2 and len(no)>=2:eligible[f]=frozenset(idx)
 bymask=defaultdict(list)
 for f,m in eligible.items():bymask[m].append(f)
 manifest=[];masks=[]
 for m,aliases in sorted(bymask.items(),key=lambda z:(len(z[0]),sorted(z[1])[0],sorted(z[0]))):
  aliases=sorted(aliases);canon=aliases[0];fid=hashlib.sha256(','.join(str(x) for x in sorted(m)).encode()).hexdigest()[:16];masks.append((fid,canon,aliases,m));manifest.append({'feature_id':fid,'canonical_feature':canon,'aliases':'|'.join(aliases),'support':len(m),'absence':len(rows)-len(m),'folios_present':','.join(sorted({rows[i]['physical_folio'] for i in m})),'folios_absent':','.join(sorted({rows[i]['physical_folio'] for i in range(len(rows)) if i not in m})),'loci_present':','.join(rows[i]['locus'] for i in sorted(m))})
 write(FEATURES,manifest)
 arrays=[r['array_id'] for r in rows];folios=[r['physical_folio'] for r in rows];rng=np.random.default_rng(SEED);atlas=[];null_rows=[];null_by_endpoint={};obs_by_endpoint={}
 for endpoint in endpoints:
  key=endpoint.lower();y=[r[key] for r in rows];obs_cmi=[]
  for fid,canon,aliases,m in masks:obs_cmi.append(cmi([int(i in m) for i in range(len(rows))],y,arrays))
  obs_by_endpoint[endpoint]=obs_cmi;null=np.zeros((len(masks),WORLDS))
  groups=defaultdict(list)
  for i,a in enumerate(arrays):groups[a].append(i)
  for w in range(WORLDS):
   yp=y.copy()
   for idx in groups.values():
    vals=[yp[i] for i in idx];rng.shuffle(vals)
    for i,v in zip(idx,vals):yp[i]=v
   for j,(_,_,_,m) in enumerate(masks):null[j,w]=cmi([int(i in m) for i in range(len(rows))],yp,arrays)
  null_by_endpoint[endpoint]=null
  null_rows.append({'endpoint':endpoint,'worlds':WORLDS,'observed_max_cmi':f'{max(obs_cmi):.12f}','null_mean_max_within_endpoint':f'{np.max(null,axis=0).mean():.12f}','array_mobile_rows':sum(len(v) for v in groups.values() if len({y[i] for i in v})>1)})
 max_all=np.maximum.reduce([np.max(null_by_endpoint[e],axis=0) for e in endpoints]);selector=math.log2(3*len(masks)*2)
 for endpoint in endpoints:
  key=endpoint.lower();y=[r[key] for r in rows];secure=[i for i,v in enumerate(y) if v!='UNCERTAIN']
  for j,(fid,canon,aliases,m) in enumerate(masks):
   x=[int(i in m) for i in range(len(rows))];oc=obs_by_endpoint[endpoint][j];local=(1+int(np.sum(null_by_endpoint[endpoint][j]>=oc-1e-15)))/(WORLDS+1);maxp=(1+int(np.sum(max_all>=oc-1e-15)))/(WORLDS+1);gain,pos,details=lofo_gain(x,y,folios);state,effect,same,opp,array_details=direction(x,y,arrays,endpoint);sx=[x[i] for i in secure];sy=[y[i] for i in secure];sa=[arrays[i] for i in secure];secure_cmi=cmi(sx,sy,sa) if secure else 0.0
   if maxp<=.20 and gain>0 and pos>=2 and same>=2 and opp==0:label='INTERESTING_EXPLORATORY'
   elif (local<=.10 and same<2) or (endpoint=='DOMINANT_HUE' and same<2):label='LIKELY_PAGE_CONFOUND'
   elif opp>0 or gain<0 and local<=.10:label='UNSTABLE'
   elif local<=.10 or gain>0:label='WEAK'
   else:label='NO_SIGNAL'
   atlas.append({'candidate_id':hashlib.sha256((endpoint+'|'+fid).encode()).hexdigest()[:16],'endpoint':endpoint,'feature_id':fid,'formal_feature':canon,'aliases':'|'.join(aliases),'support':len(m),'state_counts_feature_present':json.dumps(dict(sorted(Counter(y[i] for i in m).items())),separators=(',',':')),'state_counts_feature_absent':json.dumps(dict(sorted(Counter(y[i] for i in range(len(rows)) if i not in m).items())),separators=(',',':')),'conditional_mi_bits_per_row':f'{oc:.12f}','secure_only_cmi_bits_per_row':f'{secure_cmi:.12f}','cramers_v':f'{cramers_v(x,y):.12f}','local_p':f'{local:.12f}','maxT_p':f'{maxp:.12f}','lofo_gain_bits':f'{gain:.12f}','selector_cost_bits':f'{selector:.12f}','selector_paid_gain_bits':f'{gain-selector:.12f}','positive_held_folios':pos,'held_folio_details':details,'contrast_state':state,'pooled_direction_effect':f'{effect:.12f}','same_direction_mobile_arrays':same,'opposite_direction_mobile_arrays':opp,'array_direction_details':array_details,'family_level_edition_stability':f"{sum(r['family_edition_stable']=='1' for r in rows)}/27",'label':label})
 atlas.sort(key=lambda r:(float(r['maxT_p']),-float(r['conditional_mi_bits_per_row']),-float(r['lofo_gain_bits']),r['endpoint'],r['formal_feature']))
 write(ATLAS,atlas);write(NULL,null_rows)
 counter=[]
 for r in atlas[:20]:
  if int(r['opposite_direction_mobile_arrays']) or float(r['lofo_gain_bits'])<0 or r['label']=='LIKELY_PAGE_CONFOUND':counter.append({'candidate_id':r['candidate_id'],'endpoint':r['endpoint'],'formal_feature':r['formal_feature'],'counterexample_type':'ARRAY_DIRECTION_OR_HELD_TRANSFER','detail':f"opposite_arrays={r['opposite_direction_mobile_arrays']};lofo_gain_bits={r['lofo_gain_bits']};array_details={r['array_direction_details']};label={r['label']}"})
 if not counter:counter=[{'candidate_id':'NONE','endpoint':'ALL','formal_feature':'NONE','counterexample_type':'NO_TOP20_COUNTEREXAMPLE_ROW','detail':'No top-20 row met the fixed counterexample export rule.'}]
 write(COUNTER,counter)
 top=atlas[0];interesting=sum(r['label']=='INTERESTING_EXPLORATORY' for r in atlas);status='POSTSELECTED_QUANTITATIVE_GEOMETRY_LEAD' if interesting else ('ADJUSTED_ASSOCIATION_DIRECTIONALLY_UNSTABLE' if float(top['maxT_p'])<=.05 else 'NO_ADJUSTED_QUANTITATIVE_GEOMETRY_SIGNAL')
 p={'schema':'GDT368_RESULT_V1','status':status,'panel_rows':len(rows),'physical_folios':len(set(folios)),'arrays':len(set(arrays)),'formal_feature_raw_count':len(feat_loci),'formal_unique_mask_count':len(masks),'candidate_rows':len(atlas),'interesting_exploratory_count':interesting,'top_candidate':top,'null_worlds':WORLDS,'max_search':'THREE_ENDPOINTS_X_ALL_UNIQUE_STATE_BLIND_MASKS','formal_source_guard_stats':guarded.stats.__dict__,'family_edition_stable_loci':sum(r['family_edition_stable']=='1' for r in rows),'post_image_selection':True,'historical_contact_gap_results_changed':False,'f84_accessed':False,'inputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (TARGET,OBS,FORMAL,FREEZE,EXP/'FORMAL_SCAN.md',EXP/'DIRECTION_CLARIFICATION.md')},'outputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (PANEL,FEATURES,ATLAS,NULL,COUNTER)},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'claim_ceiling':'ANONYMOUS_POSTSELECTED_VISIBLE_GEOMETRY_SOURCE_FAMILY_ASSOCIATION_ONLY'};p['content_hash']=hashlib.sha256(canonical_json_bytes(p)).hexdigest();RESULT.write_bytes(canonical_json_bytes(p))
if __name__=='__main__':main()
