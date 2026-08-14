#!/usr/bin/env python3
"""Exploratory GDT002 visual/formal atlas; never retains, joins, or scores f84 formal rows."""
from __future__ import annotations
import csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
S=R/'experiments/semantic_assumptions/results'
ED=('ZL3b','IT2a','RF1b')

def read(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def write_tsv(p,rows):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def folio(page):return page.split('r')[0].split('v')[0]
def read_selected_loci(p,wanted):
 """Parse full formal records only for the preselected nonholdout loci."""
 rows=[]
 with p.open(newline='',encoding='utf-8') as f:
  header=next(csv.reader(f,delimiter='\t'));li=header.index('locus')
  for raw in f:
   prefix=raw.split('\t',li+1)
   if len(prefix)<=li or prefix[li] not in wanted:continue
   values=next(csv.reader([raw],delimiter='\t'));rows.append(dict(zip(header,values)))
 return rows

oldsel=read(R/'gdt002_contact_gap_selection.tsv');oldobs={x['target_id']:x for x in read(R/'gdt002_contact_gap_observations.tsv')};oldloc={x['target_id']:x for x in read(R/'gdt002_contact_gap_localizations.tsv')}
repsel=read(R/'gdt002_contact_gap_replication_selection.tsv');repobs={x['target_id']:x for x in read(R/'gdt002_contact_gap_replication_observations.tsv')};reploc={x['target_id']:x for x in read(R/'gdt002_contact_gap_replication_localizations.tsv')}
visual=read(R/'gdt002_visual_inventory.tsv')
bfe=json.loads((S/'bfe001_bio_figure_enclosure_capacity.json').read_text())
wanted={x['locus'] for x in oldsel if x['physical_folio']=='f89'}|{x['locus'] for x in repsel}
wanted|={x['local_text_loci'] for x in visual if x['folio'] in {'f80r','f82r'} and x['local_text_loci']}
wanted|={x['current_locus'] for x in bfe['observations'] if x['page']!='f84r'}
assert wanted and not any(x.startswith('f84r.') for x in wanted)

cons={x['locus']:x for x in read_selected_loci(S/'source_sta_family_consensus_loci.tsv',wanted)}
groups=defaultdict(list)
for x in read_selected_loci(S/'source_sta_family_consensus_groups.tsv',wanted):groups[x['locus']].append(x)
align=defaultdict(lambda:defaultdict(list))
for x in read_selected_loci(S/'source_sta_group_alignment.tsv',wanted):align[x['locus']][x['edition']].append(x)
for x in groups.values():x.sort(key=lambda z:int(z['consensus_group_index']))
for byed in align.values():
 for x in byed.values():x.sort(key=lambda z:int(z['source_group_index']))

def formal(locus):
 c=cons.get(locus,{}); gs=groups.get(locus,[]); by=align.get(locus,{})
 edfam={e:'|'.join(x['primary_sta_families'] for x in by.get(e,[])) for e in ED}
 edmem={e:'|'.join(x['primary_sta_codes'] for x in by.get(e,[])) for e in ED}
 fam='|'.join(x['family_surface'] for x in gs) or c.get('family_sequence','')
 return {'section':c.get('section',''),'currier':c.get('currier',''),'hand':c.get('hand',''),'code':c.get('code',''),'kind':c.get('kind',''),'grammar_scope':c.get('grammar_scope',''),'family_expression':fam,'symbol_count':c.get('symbol_count',''),'group_count':str(len(gs) or max((len(by.get(e,[])) for e in ED),default=0)),'group_family_expression':'|'.join(x['family_surface'] for x in gs),'boundary_expression':'||'.join(f"{x['left_boundary_profile']}->{x['right_boundary_profile']}" for x in gs),'internal_drawing_interruption':str(int(any('DRAWING_INTERRUPTION' in x['left_boundary_profile'] or 'DRAWING_INTERRUPTION' in x['right_boundary_profile'] for x in gs))),'strict_zero_alternative':c.get('strict_zero_alternative',''),'alternative_sites':c.get('alternative_sites',''),'family_edition_stable':str(int(bool(edfam[ED[0]]) and len(set(edfam.values()))==1)),'member_edition_stable':str(int(bool(edmem[ED[0]]) and len(set(edmem.values()))==1)),**{f'{e}_family_expression':edfam[e] for e in ED},**{f'{e}_member_expression':edmem[e] for e in ED}}

joined=[]
def add(channel,state,r,prov,source,confidence='',visual_detail=''):
 assert r['page']!='f84r' and not r['locus'].startswith('f84r.')
 joined.append({'channel':channel,'visual_state':state,'observation_provenance':prov,'observation_source':source,'review_confidence':confidence,'visual_detail':visual_detail,'target_id':r.get('target_id',''),'inherited_from_target_id':r.get('inherited_from_target_id',''),'page':r['page'],'physical_folio':r.get('physical_folio') or folio(r['page']),'locus':r['locus'],'array_id':r.get('array_id') or r.get('repetition_group',''),'ordinal':r.get('ordinal_in_complete_unit') or r.get('ordinal') or r.get('ordinal_in_group',''),**formal(r['locus'])})
for r in oldsel:
 if r['physical_folio']=='f89':
  o=oldobs[r['target_id']];add('CONTACT_GAP',o['review_state'],r,o['provenance'],'INITIAL_SINGLE_CROP_REVIEW',o['review_confidence'],'complete original f89 array')
for r in repsel:
 o=repobs[r['target_id']];add('CONTACT_GAP',o['consensus_state'],r,o['provenance'],o['consensus_source'],'',r['call_source'])

for v in visual:
 if v['folio'] in {'f80r','f82r'} and v['local_text_loci']:
  r={'page':v['folio'],'locus':v['local_text_loci'],'repetition_group':v['repetition_group'],'ordinal_in_group':v['ordinal_in_group']}
  state='APPARATUS_POSITION' if v['unit_type']=='APPARATUS_ASSOCIATED_TEXT_POSITION' else 'FIGURE_POSITION'
  add('HUMAN_LAYOUT',state,r,v['provenance'],v['annotation_source'],v['confidence'],f"{v['repetition_group']}|x={v['x_order']}|y={v['y_order']}|owner={v['ownership_evidence']}")

for o in bfe['observations']:
 if o['page']=='f84r':continue
 r={'page':o['page'],'locus':o['current_locus'],'repetition_group':o['page'],'ordinal_in_group':o['current_locus'].rsplit('.',1)[-1]}
 add('BFE_ENCLOSURE',o['state'],r,'PRIOR_AI_DIRECT_VISUAL_OBSERVATION','bfe001_bio_figure_enclosure_capacity.json','','existing bounded/open call')
joined.sort(key=lambda x:(x['channel'],x['page'],int(x['locus'].rsplit('.',1)[1]),x['locus']))
write_tsv(R/'gdt002_exploratory_visual_formal_join.tsv',joined)

def masks_for(rows):
 n=len(rows); features=[]
 def put(name,level,mask,note=''):
  s=sum(mask)
  if 2<=s<=n-2:features.append({'name':name,'level':level,'mask':tuple(map(int,mask)),'note':note})
 def putcat(name,level,values,note=''):
  if len(set(values))>=2:features.append({'name':name,'level':level,'mask':tuple(values),'note':note})
 fam=[x['family_expression'] for x in rows]
 parts=[x.split('|') if x else [] for x in fam]
 for k in (1,2,3):
  for p in sorted({x[0][:k] for x in parts if x and len(x[0])>=k}):put(f'FAMILY_PREFIX_{k}:{p}','FAMILY_COMPONENT',[bool(x) and x[0].startswith(p) for x in parts])
  for p in sorted({x[-1][-k:] for x in parts if x and len(x[-1])>=k}):put(f'FAMILY_SUFFIX_{k}:{p}','FAMILY_COMPONENT',[bool(x) and x[-1].endswith(p) for x in parts])
 for k in (1,2,3):
  vals=sorted({g[i:i+k] for xs in parts for g in xs for i in range(max(0,len(g)-k+1))})
  for p in vals:put(f'FAMILY_{k}GRAM:{p}','FAMILY_COMPONENT',[any(p in g for g in xs) for xs in parts])
 for p in sorted(set(fam)):
  if p:put(f'EXACT_FAMILY:{p}','EXACT_FAMILY',[x==p for x in fam])
 lengths=[int(x['symbol_count'] or 0) for x in rows]
 putcat('TOTAL_SYMBOL_COUNT','NUMERIC_CONSTRUCTION',lengths,'Numeric source-native family-symbol count.')
 for q in sorted(set(lengths)):put(f'SYMBOL_COUNT_GE:{q}','CONSTRUCTION',[x>=q for x in lengths])
 put('MULTI_GROUP','CONSTRUCTION',[int(x['group_count'] or 0)>1 for x in rows],'Directly coupled to drawing interruption in this panel.')
 put('INTERNAL_DRAWING_INTERRUPTION','BOUNDARY',[x['internal_drawing_interruption']=='1' for x in rows],'Potential visual/transcription tautology.')
 put('ALTERNATIVE_BEARING','UNCERTAINTY',[x['strict_zero_alternative']=='0' for x in rows])
 for e in ED:
  toks=[x[f'{e}_member_expression'].replace('|',' ').split() for x in rows]
  for t in sorted({z for xs in toks for z in xs}):put(f'MEMBER_TOKEN_{e}:{t}','MEMBER_CODE',[t in xs for xs in toks],f'primary edition={e}')
 # Collapse identical masks while retaining aliases.
 out={}
 for f in features:
  key=f['mask']
  if key in out:out[key]['aliases'].append(f['name']);out[key]['editions'].add(f['note'].split('=')[-1] if f['level']=='MEMBER_CODE' else 'CONSENSUS')
  else:out[key]={**f,'aliases':[f['name']],'editions':{f['note'].split('=')[-1] if f['level']=='MEMBER_CODE' else 'CONSENSUS'}}
 return list(out.values())

def mi(mask,y,strata):
 n=len(y);total=0.0
 for s in sorted(set(strata)):
  ix=[i for i,z in enumerate(strata) if z==s];ns=len(ix);cx=Counter((mask[i],y[i]) for i in ix);mx=Counter(mask[i] for i in ix);my=Counter(y[i] for i in ix)
  for (a,b),v in cx.items():total+=(v/n)*math.log2(v*ns/(mx[a]*my[b]))
 return total
def signed(mask,y,strata):
 vals=[]
 for s in sorted(set(strata)):
  a=[mask[i] for i,z in enumerate(strata) if z==s and y[i]==1];b=[mask[i] for i,z in enumerate(strata) if z==s and y[i]==0]
  if a and b:vals.append(sum(a)/len(a)-sum(b)/len(b))
 return sum(vals)/len(vals) if vals else 0.0,len(vals)
def kt(k,n):return -(math.lgamma(k+.5)+math.lgamma(n-k+.5)-math.lgamma(n+1)-math.lgamma(.5)*2)*math.log2(math.e)
def mdl(mask,y,strata):
 null=alt=0.0
 for s in sorted(set(strata)):
  ix=[i for i,z in enumerate(strata) if z==s];yy=[y[i] for i in ix];null+=kt(sum(yy),len(yy))
  for x in sorted(set(mask[i] for i in ix)):
   zz=[y[i] for i in ix if mask[i]==x]
   if zz:alt+=kt(sum(zz),len(zz))
 return null-alt
def worlds(y,strata):
 fixed=list(y);blocks=[]
 for s in sorted(set(strata)):
  ix=[i for i,z in enumerate(strata) if z==s];k=sum(y[i] for i in ix)
  blocks.append((ix,list(itertools.combinations(ix,k))))
 for combo in itertools.product(*(b[1] for b in blocks)):
  yy=[0]*len(y)
  for chosen in combo:
   for i in chosen:yy[i]=1
  yield yy
def cyclic_worlds(y,strata):
 blocks=[]
 for s in sorted(set(strata)):
  ix=[i for i,z in enumerate(strata) if z==s];vals=[y[i] for i in ix]
  rotations=[]
  for k in range(len(vals)):
   q=tuple(vals[k:]+vals[:k])
   if q not in rotations:rotations.append(q)
  blocks.append((ix,rotations))
 for combo in itertools.product(*(b[1] for b in blocks)):
  yy=[0]*len(y)
  for (ix,_),vals in zip(blocks,combo):
   for i,v in zip(ix,vals):yy[i]=v
  yield yy
def jacc(a,b):
 u=sum(x or y for x,y in zip(a,b));return sum(x and y for x,y in zip(a,b))/u if u else 1.0
def family_feature_present(name,expression):
 parts=expression.split('|') if expression else []
 if name.startswith('FAMILY_PREFIX_'):
  token=name.split(':',1)[1];return int(bool(parts) and parts[0].startswith(token))
 if name.startswith('FAMILY_SUFFIX_'):
  token=name.split(':',1)[1];return int(bool(parts) and parts[-1].endswith(token))
 if 'GRAM:' in name:
  token=name.split('GRAM:',1)[1];return int(any(token in group for group in parts))
 if name.startswith('EXACT_FAMILY:'):return int(expression==name.split(':',1)[1])
 raise ValueError(name)

def analyze(channel,rows,pos,neg,stratum_key):
 source=[x for x in rows if x['family_expression']]
 hard_ix=[i for i,x in enumerate(source) if x['visual_state'] in {pos,neg}];hard=[source[i] for i in hard_ix]
 y=[int(x['visual_state']==pos) for x in hard];strata=[x[stratum_key] for x in hard];features=masks_for(source)
 for f in features:f['full_mask']=f['mask'];f['mask']=tuple(f['mask'][i] for i in hard_ix)
 # Compact depth-2 worlds from the strongest 20 primitives, selected transparently in-sample.
 prelim=sorted([f for f in features if set(f['mask'])<={0,1}],key=lambda f:max(abs(signed(f['mask'],y,strata)[0]),mi(f['mask'],y,strata)),reverse=True)[:20]
 known={f['mask'] for f in features}
 for a,b in itertools.combinations(prelim,2):
  for op in ('AND','OR'):
   m=tuple((x and z) if op=='AND' else (x or z) for x,z in zip(a['mask'],b['mask']))
   if m not in known and 2<=sum(m)<=len(m)-2:
    fm=tuple((x and z) if op=='AND' else (x or z) for x,z in zip(a['full_mask'],b['full_mask']))
    known.add(m);features.append({'name':f"({a['name']})_{op}_({b['name']})",'level':'JOINT_DEPTH2','mask':m,'full_mask':fm,'note':'Postselected depth-2 exploratory combination.','aliases':[],'editions':{'CONSENSUS'}})
 ws=list(worlds(y,strata));cyclic=list(cyclic_worlds(y,strata));obs_signed=[abs(signed(f['mask'],y,strata)[0]) for f in features];obs_mi=[mi(f['mask'],y,strata) for f in features]
 matched_strata=[f"{x[stratum_key]}|L{x['symbol_count']}|G{x['group_count']}" for x in hard]
 matched=list(worlds(y,matched_strata)) if channel=='CONTACT_GAP' else []
 uncertainty=[i for i,x in enumerate(source) if x['visual_state'] not in {pos,neg}]
 sensitivity={}
 if channel=='CONTACT_GAP' and len(uncertainty)==1:
  for label,val in (('AS_CONTACT',1),('AS_CLEAR_GAP',0)):
   yy=[int(x['visual_state']==pos) if x['visual_state'] in {pos,neg} else val for x in source];ss=[x[stratum_key] for x in source]
   sensitivity[label]=(yy,ss,list(worlds(yy,ss)))
 null_s=[];null_m=[];per=[]
 for yy in ws:
  ss=[abs(signed(f['mask'],yy,strata)[0]) for f in features];mm=[mi(f['mask'],yy,strata) for f in features];null_s.append(max(ss,default=0));null_m.append(max(mm,default=0));per.append((ss,mm))
 out=[];folios=sorted({x['physical_folio'] for x in hard});arrays=sorted(set(strata));selector=math.log2(max(1,len(features)))
 for j,f in enumerate(features):
  m=f['mask'];s,info=signed(m,y,strata);cmi=obs_mi[j];ps=sum(z[0][j]>=abs(s)-1e-12 for z in per)/len(ws);pm=sum(z[1][j]>=cmi-1e-12 for z in per)/len(ws);pms=sum(z>=abs(s)-1e-12 for z in null_s)/len(ws);pmm=sum(z>=cmi-1e-12 for z in null_m)/len(ws)
  pcy=sum(abs(signed(m,yy,strata)[0])>=abs(s)-1e-12 for yy in cyclic)/len(cyclic)
  pmatched=(sum(abs(signed(m,yy,matched_strata)[0])>=abs(signed(m,y,matched_strata)[0])-1e-12 for yy in matched)/len(matched)) if matched else 1.0
  binary=set(m)<={0,1};tab=Counter((m[i],y[i]) for i in range(len(y)));nc=sum(y);ng=len(y)-nc
  if binary:
   pc=sum(m[i] for i in range(len(y)) if y[i]);pg=sum(m[i] for i in range(len(y)) if not y[i]);effect=pc/nc-pg/ng;summary=f'present={sum(m)}'
  else:
   pv=[m[i] for i in range(len(y)) if y[i]];gv=[m[i] for i in range(len(y)) if not y[i]];pc=sum(pv)/len(pv);pg=sum(gv)/len(gv);effect=pc-pg;summary=f"categories={','.join(map(str,sorted(set(m))))}"
  lo=[]
  for fo in folios:
   ix=[i for i,x in enumerate(hard) if x['physical_folio']!=fo];v,k=signed(tuple(m[i] for i in ix),[y[i] for i in ix],[strata[i] for i in ix]);lo.append(f'{fo}:{v:.6f}:{k}')
  loa=[]
  for aa in arrays:
   ix=[i for i,z in enumerate(strata) if z!=aa];v,k=signed(tuple(m[i] for i in ix),[y[i] for i in ix],[strata[i] for i in ix]);loa.append(f'{aa}:{v:.6f}:{k}')
  contrib=[]
  for a in arrays:
   ix=[i for i,z in enumerate(strata) if z==a];v,k=signed(tuple(m[i] for i in ix),[y[i] for i in ix],[a]*len(ix));contrib.append(f'{a}:{v:.6f}:{k}')
  # Edition masks for primitive member features only. Postselected joint rules
  # are not assigned fictitious cross-edition stability.
  em=[]
  if f['level']=='MEMBER_CODE':
   token=f['name'].split(':',1)[-1]
   for e in ED:em.append(tuple(int(token in x[f'{e}_member_expression'].replace('|',' ').split()) for x in hard))
  elif f['level'] in {'FAMILY_COMPONENT','EXACT_FAMILY'}:
   for e in ED:em.append(tuple(family_feature_present(f['name'],x[f'{e}_family_expression']) for x in hard))
  elif f['level']=='JOINT_DEPTH2':em=[]
  else:em=[m,m,m]
  edir=[signed(x,y,strata)[0] for x in em];ej=min((jacc(em[a],em[b]) for a in range(len(em)) for b in range(a+1,len(em))),default='')
  edition_consistent=bool(edir) and all(v==0 or (v>0)==(s>0) for v in edir)
  coupling=f['name'] in {'MULTI_GROUP','INTERNAL_DRAWING_INTERRUPTION'}
  positive_folios=len({hard[i]['physical_folio'] for i in range(len(hard)) if y[i] and (m[i] if binary else True)})
  if coupling or (channel!='CONTACT_GAP' and (info<2 or positive_folios<2)):label='LIKELY_PAGE_CONFOUND'
  elif ps<=.05 and pms<=.50 and positive_folios>=2 and edition_consistent:label='INTERESTING_EXPLORATORY'
  elif cmi>=.15 and (ps>.10 or not all(float(z.split(':')[1])==0 or (float(z.split(':')[1])>0)==(s>0) for z in lo)):label='UNSTABLE'
  elif ps<=.25 or pm<=.10:label='WEAK'
  else:label='NO_SIGNAL'
  conf=[]
  if info<2:conf.append('ONE_INFORMATIVE_ARRAY')
  if positive_folios<2:conf.append('ONE_POSITIVE_FOLIO')
  if coupling:conf.append('DIRECT_VISUAL_TRANSCRIPTION_COUPLING')
  if f['level']=='JOINT_DEPTH2':conf.extend(['POSTSELECTED_COMBINATION','EDITION_ROBUSTNESS_NOT_EVALUATED'])
  if binary and pc==0:conf.append('ZERO_POSITIVE_SUPPORT')
  if binary and pg==0:conf.append('ZERO_NEGATIVE_SUPPORT')
  if f['name']=='TOTAL_SYMBOL_COUNT':conf.append('FEATURE_IS_LENGTH')
  elif any(int(x['symbol_count'])>=6 for i,x in enumerate(hard) if m[i]) and all(int(x['symbol_count'])>=6 for i,x in enumerate(hard) if m[i] and y[i]):conf.append('POSSIBLE_LENGTH_CONFOUND')
  sens=[]
  for q,(yy,ss,qworlds) in sensitivity.items():
   sm=f['full_mask'];se,si=signed(sm,yy,ss);sp=sum(abs(signed(sm,z,ss)[0])>=abs(se)-1e-12 for z in qworlds)/len(qworlds);sens.append(f'{q}:effect={se:.6f},p={sp:.6f},worlds={len(qworlds)}')
  candidate_key='|'.join((channel,f['name'],str(m)))
  out.append({'channel':channel,'candidate_id':hashlib.sha256(candidate_key.encode()).hexdigest()[:12],'visual_feature':f'{pos}_VS_{neg}','formal_feature':f['name'],'feature_level':f['level'],'aliases':';'.join(f.get('aliases',[])),'label':label,'n_hard':len(y),'contact_or_positive_n':nc,'gap_or_negative_n':ng,'feature_positive':sum(m) if binary else '','positive_with_feature':pc,'negative_with_feature':pg,'effect_p_feature_given_positive_minus_negative':effect,'feature_value_summary':summary,'within_array_signed_effect':s,'informative_arrays':info,'conditional_mutual_information_bits_per_row':cmi,'raw_mdl_gain_bits':mdl(m,y,strata),'selector_paid_mdl_gain_bits':mdl(m,y,strata)-selector,'exact_permutation_worlds':len(ws),'exact_signed_p':ps,'exact_cmi_p':pm,'conditional_library_max_signed_p':pms,'conditional_library_max_cmi_p':pmm,'cyclic_rotation_worlds':len(cyclic),'cyclic_rotation_p':pcy,'length_group_matched_worlds':len(matched),'length_group_matched_signed_p':pmatched,'per_array_contributions':';'.join(contrib),'leave_one_array_effects':';'.join(loa),'leave_one_folio_effects':';'.join(lo),'survives_leave_one_array_direction':int(all(float(z.split(':')[1])==0 or (float(z.split(':')[1])>0)==(s>0) for z in loa)),'survives_leave_one_folio_direction':int(all(float(z.split(':')[1])==0 or (float(z.split(':')[1])>0)==(s>0) for z in lo)),'edition_min_mask_jaccard':ej,'edition_signed_effects':';'.join(f'{e}:{v:.6f}' for e,v in zip(ED,edir)) if edir else 'NOT_EVALUATED_POSTSELECTED_JOINT','uncertainty_dependence':';'.join(sens) or 'NO_UNCERTAIN_ROWS','obvious_confounds':';'.join(conf) or 'NONE','notes':f['note']})
 out.sort(key=lambda x:({'INTERESTING_EXPLORATORY':0,'WEAK':1,'UNSTABLE':2,'LIKELY_PAGE_CONFOUND':3,'NO_SIGNAL':4}[x['label']],x['conditional_library_max_signed_p'],x['exact_signed_p'],-abs(x['within_array_signed_effect']),x['formal_feature']))
 return out,hard

contact=[x for x in joined if x['channel']=='CONTACT_GAP']
atlas,hard=analyze('CONTACT_GAP',contact,'CONTACT','CLEAR_GAP','array_id')

bferows=[x for x in joined if x['channel']=='BFE_ENCLOSURE']
bfe_atlas,_=analyze('BFE_ENCLOSURE',bferows,'INDIVIDUAL_BOUNDED','OPEN_OR_COMMUNAL','page')

# Human layout channels are deliberately separate from CONTACT and section metadata.
human=[x for x in joined if x['channel']=='HUMAN_LAYOUT']
def subanalysis(name,rr,statefn,pos,neg,stratum):
 z=[]
 for x in rr:
  q=dict(x);q['visual_state']=statefn(x);z.append(q)
 return analyze(name,z,pos,neg,stratum)[0]
f80=[x for x in human if x['array_id']=='F80_TOP_TEXT_POSITIONS' and x['family_expression']]
human_a=subanalysis('F80_INTEGER_VS_HALFSTEP',f80,lambda x:'HALF_STEP' if '.5' in x['visual_detail'] else 'INTEGER','HALF_STEP','INTEGER','array_id')
f82=[x for x in human if x['array_id'] in {'F82_BOTTOM_REGION_TOP_ROW','F82_BOTTOM_REGION_BOTTOM_ROW'} and x['family_expression']]
human_b=subanalysis('F82_TOP_VS_BOTTOM_ROW',f82,lambda x:'TOP' if x['array_id'].endswith('TOP_ROW') else 'BOTTOM','TOP','BOTTOM','page')
f82all=[x for x in human if x['page']=='f82r' and x['family_expression']]
human_c=analyze('F82_APPARATUS_VS_FIGURE',f82all,'APPARATUS_POSITION','FIGURE_POSITION','page')[0]
all_atlas=sorted(atlas+bfe_atlas+human_a+human_b+human_c,key=lambda z:(z['channel'],{'INTERESTING_EXPLORATORY':0,'WEAK':1,'UNSTABLE':2,'LIKELY_PAGE_CONFOUND':3,'NO_SIGNAL':4}[z['label']],z['exact_signed_p'],z['formal_feature']))
for i,x in enumerate(all_atlas,1):x['atlas_row']=i
write_tsv(R/'gdt002_exploratory_candidate_atlas.tsv',all_atlas)

top=atlas[:25]
result={'artifact':'GDT002_EXPLORATORY_VISUAL_FORMAL_ASSOCIATIONS_V1','status':'EXPLORATORY_SEARCH_COMPLETE_NO_FROZEN_SEMANTIC_ROLE','mode':'PERMISSIVE_POSTSELECTED_DISCOVERY','counts':{'joined_rows':len(joined),'contact_unique_loci':len(contact),'contact_hard':len(hard),'contact_states':dict(Counter(x['visual_state'] for x in contact)),'contact_arrays':len({x['array_id'] for x in contact}),'contact_folios':len({x['physical_folio'] for x in contact}),'human_layout_loci':len(human),'bfe_nonholdout_loci':len(bferows),'candidate_atlas_rows':len(all_atlas),'contact_candidate_masks':len(atlas)},'controls':{'primary':'EXACT_WITHIN_ARRAY_CONTACT_COUNT_PERMUTATION','contact_primary_worlds':atlas[0]['exact_permutation_worlds'] if atlas else 0,'uncertain':'retained as missing; CONTACT and CLEAR_GAP assignments are sensitivity states, not replications','nuisance':'array/page/folio/ordinal/reviewer provenance reported; section/Currier/hand/code/kind invariant within CONTACT channel','matched_length_group_count':'only three assignments exist after exact matching, so recorded as low-capacity sensitivity rather than a discovery veto','editions':'ZL3b/IT2a/RF1b are alternate readings; primitive member masks compared, never counted as samples; joint-member edition robustness is not evaluated','postselection':'primitive library plus depth-2 AND/OR combinations; conditional-library maxima hold the observed-selected joint library fixed and are ranking diagnostics, not a full rerun of selection or confirmation control'},'strongest_contact_candidates':top,'historical_gate_statuses_preserved':['STOP_CAPACITY_GATE_FAILED_NO_FORMAL_COMPARISON','STOP_CENSUS_UNCERTAIN_EDITORIAL_UNIT_BOUNDARY_NO_REVIEW_NO_FORMAL_COMPARISON','STOP_VISUAL_GATE_FAILED_NO_FORMAL_COMPARISON'],'holdout':{'page':'f84r','formal_payload_opened':False,'formal_payload_joined':False,'used_in_search':False,'commitment_sha256':sha(R/'gdt002_f84r_holdout_projection_commitment.json')},'inputs':{str(p.relative_to(R)):sha(p) for p in [R/'gdt002_contact_gap_selection.tsv',R/'gdt002_contact_gap_observations.tsv',R/'gdt002_contact_gap_localizations.tsv',R/'gdt002_contact_gap_replication_selection.tsv',R/'gdt002_contact_gap_replication_observations.tsv',R/'gdt002_contact_gap_replication_localizations.tsv',R/'gdt002_contact_gap_result.json',R/'gdt002_contact_gap_result_validation.json',R/'gdt002_contact_gap_extension_result.json',R/'gdt002_contact_gap_extension_result_validation.json',R/'gdt002_contact_gap_replication_result.json',R/'gdt002_contact_gap_replication_result_validation.json',R/'gdt002_contact_gap_replication_reviewer_b.tsv',R/'gdt002_contact_gap_replication_reviewer_c.tsv',R/'gdt002_contact_gap_replication_reviewer_provenance.tsv',R/'gdt002_visual_inventory.tsv',S/'bfe001_bio_figure_enclosure_capacity.json',S/'source_sta_family_consensus_loci.tsv',S/'source_sta_family_consensus_groups.tsv',S/'source_sta_group_alignment.tsv',R/'gdt002_f84r_holdout_projection_commitment.json',R/'run_gdt002_exploratory_associations.py']},'documents_and_hypotheses':{n:sha(R/n) for n in ['YOLO_MODE.md','GDT002_METHOD.md','GDT002_CURRENT_SUMMARY.md','GDT002_EXPLORATORY_DISCOVERY_REPORT.md','gdt002_exploratory_joint_hypotheses.json']},'outputs':{},'claim_ceiling':'Ranked postselected visual/formal correlations only. No semantic role, lexeme, POS, sound, language, plaintext, meaning, or translation is established.'}
result['outputs']={n:sha(R/n) for n in ['gdt002_exploratory_visual_formal_join.tsv','gdt002_exploratory_candidate_atlas.tsv']}
write_json(R/'gdt002_exploratory_discovery_results.json',result)
print(result['status'],result['counts']);print([(x['formal_feature'],x['label'],x['exact_signed_p'],x['conditional_library_max_signed_p']) for x in top[:10]])
