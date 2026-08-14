#!/usr/bin/env python3
"""Targeted, exposed-data transfer of the two frozen CKPT009 layout predicates."""
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
def write_tsv(p,rows):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def write_json(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def folio(page):return page.split('r')[0].split('v')[0]
def selected(p,wanted):
 rows=[]
 with p.open(newline='',encoding='utf-8') as f:
  header=next(csv.reader(f,delimiter='\t'));li=header.index('locus')
  for raw in f:
   q=raw.split('\t',li+1)
   if len(q)<=li or q[li] not in wanted:continue
   rows.append(dict(zip(header,next(csv.reader([raw],delimiter='\t')))))
 return rows
def kt(k,n):return -(math.lgamma(k+.5)+math.lgamma(n-k+.5)-math.lgamma(n+1)-2*math.lgamma(.5))*math.log2(math.e)

prior=json.loads((R/'gdt002_exploratory_discovery_results.json').read_text())
atlas=read(R/'gdt002_exploratory_candidate_atlas.tsv')
fixed={x['formal_feature']:x for x in atlas if x['channel'] in {'F82_TOP_VS_BOTTOM_ROW','F82_APPARATUS_VS_FIGURE'} and x['formal_feature'] in {'FAMILY_PREFIX_3:AQA','FAMILY_3GRAM:ACA'}}
assert set(fixed)=={'FAMILY_PREFIX_3:AQA','FAMILY_3GRAM:ACA'}

cross=read(S/'existing_human_current_locus_crosswalk.tsv')
f75={}
for x in cross:
 if x['source_page']=='f75v' and x['source_unit']=='l1' and x['primary_eligible']=='1':
  i=int(x['source_item']);f75[i]=x
assert sorted(f75)==list(range(1,21))
f67=[]
for x in cross:
 if x['source_page']=='f67r2' and x['source_unit'] in {'l','x'} and x['primary_eligible']=='1':
  key=(x['source_unit'],int(x['source_item']))
  if key not in {(z['source_unit'],int(z['source_item'])) for z in f67}:f67.append(x)
assert Counter(x['source_unit'] for x in f67)=={'l':7,'x':12}

ann=read(S/'existing_human_exact_locus_annotations.tsv')
apparatus_candidates=[]
for x in ann:
 if x['page']=='f84r' or x['certainty']!='UNHEDGED':continue
 tags=set(x['object_tags'].split(';'))
 if 'WATER_OR_APPARATUS' in tags and 'FIGURE' not in tags:state='APPARATUS_POSITION'
 elif 'FIGURE' in tags and 'WATER_OR_APPARATUS' not in tags:state='FIGURE_POSITION'
 else:continue
 apparatus_candidates.append((state,x))

wanted={x['current_locus'] for x in f75.values()}|{x['current_locus'] for x in f67}|{x[1]['locus'] for x in apparatus_candidates}
assert not any(x.startswith('f84r.') for x in wanted)
cons={x['locus']:x for x in selected(S/'source_sta_family_consensus_loci.tsv',wanted)}
groups=defaultdict(list)
for x in selected(S/'source_sta_family_consensus_groups.tsv',wanted):groups[x['locus']].append(x)
align=defaultdict(lambda:defaultdict(list))
for x in selected(S/'source_sta_group_alignment.tsv',wanted):align[x['locus']][x['edition']].append(x)
for xs in groups.values():xs.sort(key=lambda x:int(x['consensus_group_index']))
for e in align.values():
 for xs in e.values():xs.sort(key=lambda x:int(x['source_group_index']))
def formal(loc):
 c=cons.get(loc,{});gs=groups.get(loc,[]);fam='|'.join(x['family_surface'] for x in gs) or c.get('family_sequence','')
 ed={e:'|'.join(x['primary_sta_families'] for x in align.get(loc,{}).get(e,[])) for e in ED}
 return {'family_expression':fam,'family_prefix_AQA':str(int(fam.startswith('AQA'))) if fam else '','family_contains_ACA':str(int(any('ACA' in g for g in fam.split('|')))) if fam else '','formal_coverage':str(int(bool(fam))),'strict_zero_alternative':c.get('strict_zero_alternative',''),'kind':c.get('kind',''),'family_edition_stable':str(int(bool(ed['ZL3b']) and len(set(ed.values()))==1)),**{f'{e}_family_expression':ed[e] for e in ED}}

rows=[]
def add(channel,state,page,loc,group,ordinal,pair,source,exposure):
 rows.append({'channel':channel,'visual_state':state,'page':page,'physical_folio':folio(page),'locus':loc,'visual_group':group,'ordinal':ordinal,'pair_id':pair,'provenance':'EXISTING_HUMAN_ANNOTATION','annotation_source':source,'prior_exposure':exposure,**formal(loc)})
for i,x in sorted(f75.items()):add('AQA_POSITIONAL_TRANSFER','TOP' if i%2 else 'BOTTOM','f75v',x['current_locus'],'F75V_TEN_PAIRED_STACKS',i,(i+1)//2,'existing_human_current_locus_crosswalk.tsv','F67_TAIL_ECHO_F75V_TRANSFER;NOT_FRESH')
for x in sorted(f67,key=lambda z:(z['source_unit'],int(z['source_item']))):add('AQA_POSITIONAL_TRANSFER','UPPER_ISOLATED' if x['source_unit']=='l' else 'LOWER_MOON_ADJACENT','f67r2',x['current_locus'],'F67R2_UPPER_LOWER_REGISTERS',x['source_item'],x['source_item'],'existing_human_current_locus_crosswalk.tsv','RTA001;RBR001;TAIL_ECHO;NOT_FRESH')
for state,x in apparatus_candidates:
 f=formal(x['locus'])
 if f['kind']=='L' and f['formal_coverage']=='1':add('ACA_APPARATUS_TRANSFER',state,x['page'],x['locus'],x['unit'],x['old_locus'],'','existing_human_exact_locus_annotations.tsv','EXISTING_EXACT_ANNOTATION;MULTIPLE_PRIOR_ROUTES')
rows.sort(key=lambda x:(x['channel'],x['page'],int(x['locus'].rsplit('.',1)[1]),x['locus']))
write_tsv(R/'gdt002_targeted_transfer_join.tsv',rows)

def effect(xs,feature,positive):
 a=[int(x[feature]) for x in xs if x['visual_state']==positive];b=[int(x[feature]) for x in xs if x['visual_state']!=positive]
 return sum(a)/len(a)-sum(b)/len(b),len(a),len(b),sum(a),sum(b)
def exact_page_permutation(xs,feature,positive):
 pages=sorted({x['page'] for x in xs});blocks=[];obs=[]
 for p in pages:
  q=[x for x in xs if x['page']==p];k=sum(x['visual_state']==positive for x in q);m=[int(x[feature]) for x in q]
  if k and k<len(q):
   blocks.append((p,m,k));obs.append(sum(m[i] for i,x in enumerate(q) if x['visual_state']==positive)/k-sum(m[i] for i,x in enumerate(q) if x['visual_state']!=positive)/(len(q)-k))
 target=sum(obs)/len(obs);worlds=tail=0
 for choices in itertools.product(*(list(itertools.combinations(range(len(m)),k)) for _,m,k in blocks)):
  vals=[]
  for (_,m,k),chosen in zip(blocks,choices):
   z=set(chosen);vals.append(sum(m[i] for i in z)/k-sum(m[i] for i in range(len(m)) if i not in z)/(len(m)-k))
  worlds+=1;tail+=sum(vals)/len(vals)>=target-1e-12
 return {'effect':target,'worlds':worlds,'one_sided_exact_p':tail/worlds,'tail':tail,'per_page_effects':dict(zip((x[0] for x in blocks),obs))}
def paired_swap(xs,feature,positive):
 pairs=defaultdict(list)
 for x in xs:pairs[x['pair_id']].append(x)
 assert all(len(q)==2 and {x['visual_state'] for x in q}=={positive,'BOTTOM'} for q in pairs.values())
 obs=effect(xs,feature,positive)[0];tail=worlds=0
 for flips in itertools.product((0,1),repeat=len(pairs)):
  a=[];b=[]
  for flip,q in zip(flips,pairs.values()):
   vals=[int(x[feature]) for x in q];a.append(vals[flip]);b.append(vals[1-flip])
  worlds+=1;tail+=(sum(a)/len(a)-sum(b)/len(b)>=obs-1e-12)
 return {'worlds':worlds,'one_sided_exact_p':tail/worlds,'tail':tail}

aqa=[x for x in rows if x['channel']=='AQA_POSITIONAL_TRANSFER' and x['formal_coverage']=='1']
aqa_pages={}
for p,pos in [('f75v','TOP'),('f67r2','UPPER_ISOLATED')]:
 q=[x for x in aqa if x['page']==p];e,n1,n0,k1,k0=effect(q,'family_prefix_AQA',pos);aqa_pages[p]={'positive_state':pos,'n_positive':n1,'n_other':n0,'AQA_positive':k1,'AQA_other':k0,'effect':e}
 if p=='f75v':aqa_pages[p].update(paired_swap(q,'family_prefix_AQA',pos))
 else:
  z=exact_page_permutation(q,'family_prefix_AQA',pos);aqa_pages[p].update({k:z[k] for k in ('worlds','one_sided_exact_p','tail')})
 # Each exposed page is scored separately; there is no claim of fresh replication.

aca=[x for x in rows if x['channel']=='ACA_APPARATUS_TRANSFER']
informative=[x for x in aca if x['page'] in {'f77r','f82r'}]
aca_exact=exact_page_permutation(informative,'family_contains_ACA','APPARATUS_POSITION')
aca_pages={}
for p in sorted({x['page'] for x in aca}):
 q=[x for x in aca if x['page']==p];states=Counter(x['visual_state'] for x in q)
 if len(states)==2:
  e,n1,n0,k1,k0=effect(q,'family_contains_ACA','APPARATUS_POSITION')
  # Recompute the source code correctly by visual-state null versus feature split.
  null=kt(n1,n1+n0);alt=0.0
  for v in (0,1):
   z=[int(x['visual_state']=='APPARATUS_POSITION') for x in q if int(x['family_contains_ACA'])==v]
   if z:alt+=kt(sum(z),len(z))
  orbit=exact_page_permutation(q,'family_contains_ACA','APPARATUS_POSITION')
  aca_pages[p]={'apparatus_n':n1,'figure_n':n0,'ACA_apparatus':k1,'ACA_figure':k0,'effect':e,'exact_worlds':orbit['worlds'],'one_sided_exact_p':orbit['one_sided_exact_p'],'raw_mdl_gain_bits':null-alt}
overall_null=overall_alt=0.0
for p in ('f77r','f82r'):
 q=[x for x in informative if x['page']==p];y=[int(x['visual_state']=='APPARATUS_POSITION') for x in q];overall_null+=kt(sum(y),len(y))
 for v in (0,1):
  z=[int(x['visual_state']=='APPARATUS_POSITION') for x in q if int(x['family_contains_ACA'])==v]
  if z:overall_alt+=kt(sum(z),len(z))
aca_exact['raw_mdl_gain_bits']=overall_null-overall_alt;aca_exact['two_candidate_selector_paid_mdl_gain_bits']=aca_exact['raw_mdl_gain_bits']-1

result={'artifact':'GDT002_TARGETED_EXPOSED_TRANSFER_V1','status':'AQA_NO_TRANSFER_ACA_DIRECTION_REPEATS_BUT_TRANSFER_ONLY_WEAK','mode':'TARGETED_EXPLORATORY_NOT_VALIDATION','fixed_candidates':{'AQA':{'source_candidate_id':fixed['FAMILY_PREFIX_3:AQA']['candidate_id'],'source_channel':'F82_TOP_VS_BOTTOM_ROW','rule':'FAMILY_PREFIX_3:AQA'},'ACA':{'source_candidate_id':fixed['FAMILY_3GRAM:ACA']['candidate_id'],'source_channel':'F82_APPARATUS_VS_FIGURE','rule':'FAMILY_3GRAM:ACA'}},'counts':{'join_rows':len(rows),'AQA_rows':sum(x['channel']=='AQA_POSITIONAL_TRANSFER' for x in rows),'AQA_formal_rows':len(aqa),'ACA_rows':len(aca),'ACA_informative_rows':len(informative)},'AQA':{'pages':aqa_pages,'decision':'NO_TRANSFER_ON_EXPOSED_F75V_OR_F67R2_LAYOUTS'},'ACA':{'pages':aca_pages,'pooled_f77r_f82r':aca_exact,'decision':'INTERESTING_EXPLORATORY_DIRECTION_ONLY_NOT_VALIDATED','interpretive_ceiling':'The independent f77r page has the same direction but p=.6 and negative page-only MDL; the pooled signal is driven by the f82r discovery page.'},'holdout':{'page':'f84r','formal_payload_opened':False,'formal_payload_joined':False,'used_in_search':False,'commitment_sha256':sha(R/'gdt002_f84r_holdout_projection_commitment.json')},'exposure':'f75v/f67r2 and f77/f82 have prior route exposure; this is targeted reuse, not fresh confirmation.','inputs':{str(p.relative_to(R)):sha(p) for p in [R/'gdt002_exploratory_discovery_results.json',R/'gdt002_exploratory_candidate_atlas.tsv',R/'GDT002_YOLO_LEDGER.tsv',S/'existing_human_current_locus_crosswalk.tsv',S/'existing_human_exact_locus_annotations.tsv',S/'source_sta_family_consensus_loci.tsv',S/'source_sta_family_consensus_groups.tsv',S/'source_sta_group_alignment.tsv',R/'experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv',R/'gdt002_f84r_holdout_projection_commitment.json',R/'run_gdt002_targeted_transfer.py']},'documents':{},'outputs':{},'claim_ceiling':'Formal association transfer diagnostics only. Semantic roles remain UNASSIGNED; no word, POS, sound, language, plaintext, meaning, or translation is established.'}
for name in ['GDT002_METHOD.md','GDT002_CURRENT_SUMMARY.md','GDT002_TARGETED_TRANSFER_REPORT.md']:result['documents'][name]=sha(R/name)
result['outputs']['gdt002_targeted_transfer_join.tsv']=sha(R/'gdt002_targeted_transfer_join.tsv')
write_json(R/'gdt002_targeted_transfer_results.json',result)
print(result['status'],result['counts']);print(result['AQA']);print(result['ACA'])
