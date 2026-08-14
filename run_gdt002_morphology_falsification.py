#!/usr/bin/env python3
"""Falsification-first inventory for fixed candidate Voynich modules."""
import csv,hashlib,itertools,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;S=R/'experiments/semantic_assumptions/results'
MODULES=('ar','ol','dal','dar','sy','te','tee','dy');EDS=('ZL3b','IT2a','RF1b')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def guarded(p,locus_col):
 out=[]
 with p.open(encoding='utf-8') as f:
  head=f.readline().rstrip('\n').split('\t');i=head.index(locus_col)
  for line in f:
   cells=line.rstrip('\n').split('\t');locus=cells[i]
   if locus.startswith('f84r'):continue
   out.append(dict(zip(head,cells)))
 return out
def write_tsv(p,rows):
 with p.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def folio(page):
 m=re.match(r'(f\d+)',page);return m.group(1) if m else page
def layout(kind):return {'P':'RUNNING_TEXT','L':'LABEL','C':'CIRCULAR','R':'RADIAL'}.get(kind,'OTHER')
sep=guarded(S/'source_separator_transcription.tsv','locus');meta={x['source_group_id']:x for x in sep}
align=guarded(S/'source_sta_group_alignment.tsv','locus');annrows=guarded(S/'existing_human_exact_locus_annotations.tsv','locus');ann={x['locus']:x for x in annrows}
groups=defaultdict(dict);types=defaultdict(lambda:defaultdict(list));byline=defaultdict(list)
for x in align:
 m=meta[x['source_group_id']];surface=x['nearest_basic_eva_primary'].lower();rec={**x,**{k:m[k] for k in ('page','section','currier','hand','code','kind','grammar_scope','paragraph_start','paragraph_end','ivtff_group_raw','clean_ascii_fragments','legacy_mapping_status')}};rec['surface']=surface
 key=(x['locus'],int(x['source_group_index']));groups[key][x['edition']]=rec;types[x['edition']][surface].append(rec);byline[x['edition'],x['locus']].append(rec)
for z in byline.values():z.sort(key=lambda x:int(x['source_group_index']))
inventory=[]
for (locus,gi),edmap in sorted(groups.items()):
 first=next(iter(edmap.values()));surfaces={e:edmap[e]['surface'] for e in EDS if e in edmap};counts={edmap[e]['source_group_count'] for e in edmap};a=ann.get(locus,{})
 agreement='ALL_THREE_EXACT' if len(edmap)==3 and len(set(surfaces.values()))==1 and len(counts)==1 else 'AVAILABLE_EXACT' if len(set(surfaces.values()))==1 and len(counts)==1 else 'READING_OR_TOPOLOGY_DISAGREEMENT'
 for mod in MODULES:
  matching=[e for e,s in surfaces.items() if mod in s]
  if not matching:continue
  states=[];segments=[];positions=[]
  for e in EDS:
   if e not in surfaces:continue
   s=surfaces[e];pos=[i for i in range(len(s)) if s.startswith(mod,i)]
   if not pos:states.append(f'{e}:ABSENT');continue
   state='FREE' if s==mod else 'PREFIX' if s.startswith(mod) else 'SUFFIX' if s.endswith(mod) else 'INTERNAL';states.append(f'{e}:{state}');positions.append(f'{e}:'+','.join(map(str,pos)))
   i=pos[0];segments.append(f'{e}:{s[:i] or "∅"}+'+'['+mod.upper()+']+'+f'{s[i+len(mod):] or "∅"}')
  inventory.append({'module':mod.upper(),'locus':locus,'page':first['page'],'physical_folio':folio(first['page']),'source_group_index':gi,'source_group_count_by_reading':';'.join(f'{e}:{edmap[e]["source_group_count"]}' for e in EDS if e in edmap),'ZL3b_token':surfaces.get('ZL3b',''),'IT2a_token':surfaces.get('IT2a',''),'RF1b_token':surfaces.get('RF1b',''),'match_state_by_reading':';'.join(states),'match_positions_zero_based':';'.join(positions),'proposed_segmentation_by_reading':';'.join(segments),'reading_agreement':agreement,'layout_role':layout(first['kind']),'kind':first['kind'],'section':first['section'],'currier':first['currier'],'hand':first['hand'],'grammar_scope':first['grammar_scope'],'left_separator_by_reading':';'.join(f'{e}:{edmap[e]["left_separator"]}' for e in EDS if e in edmap),'right_separator_by_reading':';'.join(f'{e}:{edmap[e]["right_separator"]}' for e in EDS if e in edmap),'annotation_provenance':'EXISTING_HUMAN_ANNOTATION' if a else 'NONE','object_tags':a.get('object_tags',''),'relation_tags':';'.join(filter(None,(a.get('local_relation_tags',''),a.get('unit_relation_tags','')))),'annotation_certainty':a.get('certainty',''),'raw_source_description':' || '.join(filter(None,(a.get('unit_description',''),a.get('local_comment','')))),'claim_state':'FORMAL_MODULE_OCCURRENCE_NOT_MORPHEME'})
write_tsv(R/'gdt002_morphology_occurrences.tsv',inventory)

# Minimal/near-minimal transformation pairs, consolidated across alternate readings.
pairs=defaultdict(lambda:{'editions':set(),'left':defaultdict(list),'right':defaultdict(list),'same_loci':set(),'same_pages':set()})
def addpair(rule,a,b,e,seg):
 if a==b or a not in types[e] or b not in types[e]:return
 key=(rule,a,b,seg);z=pairs[key];z['editions'].add(e);z['left'][e]+=types[e][a];z['right'][e]+=types[e][b]
 la={x['locus'] for x in types[e][a]};lb={x['locus'] for x in types[e][b]};z['same_loci']|=la&lb;z['same_pages']|={x['page'] for x in types[e][a]}&{x['page'] for x in types[e][b]}
for e in EDS:
 ts=set(types[e])
 for base in ts:
  addpair('Q_OUTER_INSERTION',base,'q'+base,e,f'q+{base}')
  if base.startswith('d') and 's'+base[1:] in ts:addpair('D_S_LEFT_CONTRAST',base,'s'+base[1:],e,f'd/s+{base[1:]}')
  if base.startswith('o') and 'ot'+base[1:] in ts:addpair('O_OT_LEFT_CONTRAST',base,'ot'+base[1:],e,f'o/ot+{base[1:]}')
  for i in range(len(base)-1):
   if base.startswith('te',i):addpair('TE_TEE_CONTRAST',base,base[:i]+'tee'+base[i+2:],e,base[:i]+'+te/tee+'+base[i+2:])
  for s1,s2 in itertools.combinations(('', 'dal','dar','sy','dy'),2):
   if s1 and not base.endswith(s1):continue
   stem=base[:-len(s1)] if s1 else base
   if len(stem)>=2:addpair('RIGHT_MODULE_CONTRAST',base,stem+s2,e,f'{stem}+{s1 or "∅"}/{s2 or "∅"}')
pairrows=[]
for (rule,a,b,seg),z in pairs.items():
 def loc(side):return sorted({x['locus'] for e in z['editions'] for x in z[side][e]})
 def fols(side):return sorted({folio(x['page']) for e in z['editions'] for x in z[side][e]})
 la,lb=loc('left'),loc('right');fa,fb=fols('left'),fols('right');score=100*len(z['editions'])+20*len(z['same_loci'])+5*min(len(fa),len(fb))+min(len(la),len(lb))
 pairrows.append({'pair_rule':rule,'left_form':a,'right_form':b,'proposed_segmentation':seg,'editions_present':';'.join(sorted(z['editions'])),'alternate_readings_not_replications':1,'left_physical_folios':len(fa),'right_physical_folios':len(fb),'left_loci_count':len(la),'right_loci_count':len(lb),'same_locus_count':len(z['same_loci']),'same_page_count':len(z['same_pages']),'representative_left_loci':';'.join(la[:8]),'representative_right_loci':';'.join(lb[:8]),'ranking_score':score,'evidence_ceiling':'FORMAL_MINIMAL_PAIR_NO_MEANING'})
pair_rule_totals=Counter(x['pair_rule'] for x in pairrows)
pairrows.sort(key=lambda x:(-int(x['ranking_score']),x['pair_rule'],x['left_form'],x['right_form']));pairrows=pairrows[:500];write_tsv(R/'gdt002_morphology_minimal_pairs.tsv',pairrows)

# Source-manual split/join analogues.
split=defaultdict(lambda:{'editions':set(),'split_loci':set(),'joined_loci':set(),'seps':set()})
for e in EDS:
 for (_,locus),seq in byline.items():
  if _!=e:continue
  for a,b in zip(seq,seq[1:]):
   joined=a['surface']+b['surface']
   if joined not in types[e] or sum(m in joined for m in MODULES)<2:continue
   k=(a['surface'],b['surface'],joined);z=split[k];z['editions'].add(e);z['split_loci'].add(locus);z['joined_loci']|={x['locus'] for x in types[e][joined]};z['seps'].add(a['right_separator'])
splitrows=[{'left_free_group':a,'right_free_group':b,'joined_form':j,'candidate_segmentation':a+' | '+b+' ↔ '+j,'editions_present':';'.join(sorted(z['editions'])),'split_loci_count':len(z['split_loci']),'joined_loci_count':len(z['joined_loci']),'separator_states':';'.join(sorted(z['seps'])),'representative_split_loci':';'.join(sorted(z['split_loci'])[:10]),'representative_joined_loci':';'.join(sorted(z['joined_loci'])[:10]),'claim_state':'MANUAL_GROUP_SPLIT_JOIN_ANALOGY_NOT_MORPHEME'} for (a,b,j),z in split.items()]
splitrows.sort(key=lambda x:(-len(x['editions_present'].split(';')),-int(x['split_loci_count']),x['joined_form']));write_tsv(R/'gdt002_morphology_split_join.tsv',splitrows or [{'left_free_group':'NONE','right_free_group':'NONE','joined_form':'NONE','candidate_segmentation':'NONE','editions_present':'NONE','split_loci_count':0,'joined_loci_count':0,'separator_states':'NONE','representative_split_loci':'NONE','representative_joined_loci':'NONE','claim_state':'NO_ROWS'}])

# Physical-group summaries and label/prose density use exact all-reading surfaces only.
stable=[]
for key,em in groups.items():
 if len(em)==3 and len({x['surface'] for x in em.values()})==1 and len({x['source_group_count'] for x in em.values()})==1:stable.append(next(iter(em.values())))
density={}
for role in ('LABEL','RUNNING_TEXT'):
 rr=[x for x in stable if layout(x['kind'])==role];chars=sum(len(x['surface']) for x in rr);hits=sum(sum(x['surface'].count(m) for m in MODULES) for x in rr);multi=sum(sum(m in x['surface'] for m in MODULES)>=2 for x in rr);free=sum(x['surface'] in MODULES for x in rr)
 density[role]={'groups':len(rr),'symbols':chars,'candidate_hits':hits,'hits_per_100_symbols':100*hits/chars,'multi_module_groups':multi,'multi_module_rate':multi/len(rr),'standalone_candidate_groups':free,'standalone_rate':free/len(rr)}
density_sensitivity={}
for name,mods in {'EXCLUDE_NESTED_TE_TEE':('ar','ol','dal','dar','sy','dy'),'RIGHT_EDGE_CANDIDATES_ONLY':('dal','dar','sy','dy')}.items():
 density_sensitivity[name]={}
 for role in ('LABEL','RUNNING_TEXT'):
  rr=[x for x in stable if layout(x['kind'])==role];chars=sum(len(x['surface']) for x in rr);hits=sum(sum(x['surface'].count(m) for m in mods) for x in rr);multi=sum(sum(m in x['surface'] for m in mods)>=2 for x in rr)
  density_sensitivity[name][role]={'candidate_hits':hits,'hits_per_100_symbols':100*hits/chars,'multi_module_groups':multi,'multi_module_rate':multi/len(rr)}

# Page-conditioned explicit visual contrasts; unmentioned roles are never negatives.
axes={'APPARATUS_VS_FIGURE':lambda a:'POS' if 'WATER_OR_APPARATUS' in a['object_tags'] and 'FIGURE' not in a['object_tags'] else 'NEG' if 'FIGURE' in a['object_tags'] and 'WATER_OR_APPARATUS' not in a['object_tags'] else None,'UPPER_VS_LOWER':lambda a:'POS' if re.search(r'\b(upper|above|top)\b',(a['unit_description']+' '+a['local_comment']).lower()) else 'NEG' if re.search(r'\b(lower|below|bottom)\b',(a['unit_description']+' '+a['local_comment']).lower()) else None,'LEFT_VS_RIGHT':lambda a:'POS' if re.search(r'\b(left|west)\b',(a['unit_description']+' '+a['local_comment']).lower()) else 'NEG' if re.search(r'\b(right|east)\b',(a['unit_description']+' '+a['local_comment']).lower()) else None,'INSIDE_VS_OUTSIDE':lambda a:'POS' if re.search(r'\b(inside|within|enclosed)\b',(a['unit_description']+' '+a['local_comment']).lower()) else 'NEG' if re.search(r'\b(outside|external)\b',(a['unit_description']+' '+a['local_comment']).lower()) else None,'FLOW_DUCT_VS_FIGURE':lambda a:'POS' if re.search(r'\b(flow|tube|duct|channel|waterfall|spray)\b',(a['unit_description']+' '+a['local_comment']).lower()) else 'NEG' if re.search(r'\b(nymph|human figure|female figure)\b',(a['unit_description']+' '+a['local_comment']).lower()) else None}
locus_presence={}
for locus in {x['locus'] for x in annrows}:
 em={e:[r for (l,i),m in groups.items() if l==locus for ee,r in m.items() if ee==e] for e in EDS};locus_presence[locus]={}
 for mod in MODULES:
  vals=[any(mod in x['surface'] for x in em[e]) for e in EDS if em[e]];locus_presence[locus][mod]=vals[0] if vals and len(set(vals))==1 else None
def hyper_tail(strata,obs):
 dist={0:1}
 for n,k,m in strata:
  den=math.comb(n,k);local={x:math.comb(m,x)*math.comb(n-m,k-x)/den for x in range(max(0,k-(n-m)),min(k,m)+1)};nd=defaultdict(float)
  for a,p in dist.items():
   for b,q in local.items():nd[a+b]+=p*q
  dist=nd
 return sum(p for x,p in dist.items() if x>=obs-1e-12)
visual=[]
for axis,fn in axes.items():
 for mod in MODULES:
  rr=[]
  for a in annrows:
   if len(a['normalized_code'])<2 or a['normalized_code'][1]!='L':continue
   state=fn(a);pres=locus_presence.get(a['locus'],{}).get(mod)
   if state and pres is not None:rr.append((a['page'],state,int(pres),a['locus']))
  pos=[x for x in rr if x[1]=='POS'];neg=[x for x in rr if x[1]=='NEG'];pages=defaultdict(list)
  for x in rr:pages[x[0]].append(x)
  strata=[];obs=0;inform=0
  for p,z in pages.items():
   n=len(z);k=sum(x[1]=='POS' for x in z);m=sum(x[2] for x in z)
   if k and k<n and m and m<n:strata.append((n,k,m));obs+=sum(x[1]=='POS' and x[2] for x in z);inform+=1
  effect=(sum(x[2] for x in pos)/len(pos)-sum(x[2] for x in neg)/len(neg)) if pos and neg else 0
  visual.append({'module':mod.upper(),'visual_contrast':axis,'positive_n':len(pos),'negative_n':len(neg),'positive_with_module':sum(x[2] for x in pos),'negative_with_module':sum(x[2] for x in neg),'effect':effect,'informative_pages':inform,'page_conditioned_one_sided_p':hyper_tail(strata,obs) if strata else 1.0,'reading_stable_rows':len(rr),'representative_positive_loci':';'.join(x[3] for x in pos if x[2])[:500],'representative_negative_loci':';'.join(x[3] for x in neg if x[2])[:500],'confound':'HUMAN_DESCRIPTION_AXIS; ABSENCE_UNKNOWN; PAGE_CONDITIONED; PROXIMITY_NOT_OWNERSHIP'})
visual.sort(key=lambda x:(float(x['page_conditioned_one_sided_p']),-abs(float(x['effect'])),x['module'],x['visual_contrast']));write_tsv(R/'gdt002_morphology_visual_associations.tsv',visual)

# Module/productivity summary and ranked falsification decisions.
summary={};pair_by_rule=Counter(x['pair_rule'] for x in pairrows)
for mod in MODULES:
 rr=[x for x in inventory if x['module']==mod.upper()];host=set();free=set();bound=set();prefix=suffix=internal=0;folios=set();sections=set()
 for x in rr:
  folios.add(x['physical_folio']);sections.add(x['section'])
  for e in EDS:
   s=x[e+'_token'];
   if not s or mod not in s:continue
   host.add(s)
   if s==mod:free.add((x['locus'],x['source_group_index']))
   else:
    bound.add((x['locus'],x['source_group_index']));prefix+=int(s.startswith(mod));suffix+=int(s.endswith(mod));internal+=int(not s.startswith(mod) and not s.endswith(mod))
 summary[mod]={'physical_rows':len(rr),'free_physical':len(free),'bound_physical':len(bound),'host_types':len(host),'physical_folios':len(folios),'sections':len(sections),'prefix_reading_hits':prefix,'suffix_reading_hits':suffix,'internal_reading_hits':internal}
rankrows=[]
def rank(candidate,rank,evidence,counter):rankrows.append({'candidate':candidate,'rank':rank,'supporting_evidence':evidence,'falsifying_or_limiting_evidence':counter,'semantic_status':'UNASSIGNED'})
for mod in MODULES:
 z=summary[mod];slot=(z['suffix_reading_hits']/(z['prefix_reading_hits']+z['suffix_reading_hits']+z['internal_reading_hits'])) if mod in {'dal','dar','sy','dy'} and (z['prefix_reading_hits']+z['suffix_reading_hits']+z['internal_reading_hits']) else None
 rk='STRONG' if z['free_physical']>=20 and z['host_types']>=100 and (slot is None or slot>=.6) else 'PROVISIONAL' if z['host_types']>=50 and z['free_physical']>=3 and (slot is None or slot>=.35) else 'WEAK' if z['host_types']>=10 else 'FAILED'
 rank(mod.upper()+'_REUSABLE_FORMAL_UNIT',rk,f"free={z['free_physical']}; bound={z['bound_physical']}; host_types={z['host_types']}; folios={z['physical_folios']}; sections={z['sections']}",f"prefix/suffix/internal reading-hits={z['prefix_reading_hits']}/{z['suffix_reading_hits']}/{z['internal_reading_hits']}"+(f'; right-slot concentration={slot:.3f}' if slot is not None else ''))
for op,rule in [('D_S_LEFT','D_S_LEFT_CONTRAST'),('Q_OUTER','Q_OUTER_INSERTION'),('O_OT_LEFT','O_OT_LEFT_CONTRAST'),('TE_TEE','TE_TEE_CONTRAST')]:
 n=pair_by_rule[rule];rk='PROVISIONAL' if n>=10 else 'WEAK' if n else 'FAILED';rank(op+'_FORMAL_CONTRAST',rk,f'{n} retained strongest pair types under {rule}', 'No semantic visual contrast is established; pairs are type-selected and editions are alternate readings.')
rank('FOUR_SLOT_SEMANTIC_TEMPLATE','FAILED','Reusable pieces and formal pairs exist.','Existing whole-manuscript morphology MDL lost to the source winner by 100562.898 bits; no candidate has a stable page-controlled visual role and slot boundaries remain ambiguous/overlapping.')
write_tsv(R/'gdt002_morphology_rankings.tsv',rankrows)

# Explicit counterexamples.
def loci_for(forms):
 return sorted({x['locus'] for e in EDS for s in forms for x in types[e].get(s,[])})
counter=[{'candidate':'AROL_SEMANTIC_ROOT','counterexample_type':'CROSS_REGISTER_AND_OBJECT_DIVERSITY','loci':';'.join(loci_for({'arol','sarol'})[:40]),'tokens':'arol;sarol','evidence':'These forms occur outside flow-like annotations, including plant/pharmaceutical label contexts.','impact':'AROL cannot mean flow/water.'},{'candidate':'TE_TEE_FREE_CORE','counterexample_type':'NEAR_ABSENT_STANDALONE','loci':'MANUSCRIPT_WIDE','tokens':'te;tee','evidence':f"Standalone physical counts TE={summary['te']['free_physical']}, TEE={summary['tee']['free_physical']}; both are pervasive substrings and TE nests inside TEE.",'impact':'Reusable substring evidence does not identify an independent core.'},{'candidate':'F83R_OPPOSING_FORM','counterexample_type':'TRANSCRIPTION_DISAGREEMENT','loci':'f83r.50','tokens':'sasoldal;saroldal','evidence':'ZL3b differs from IT2a/RF1b at the proposed s+ar+ol+dal segmentation.','impact':'The complete opposing label is not all-reading stable.'},{'candidate':'F82R_DARARY','counterexample_type':'TRANSCRIPTION_DISAGREEMENT','loci':'f82r.38','tokens':'darary;daryry;jarary','evidence':'All three readings disagree at the onset/internal sequence.','impact':'It cannot anchor d+ar or a right module without marginalization.'},{'candidate':'F75V_SPOUT_NUMBERING','counterexample_type':'OWNERSHIP_NOT_ESTABLISHED','loci':'f75v paired labels','tokens':'20 labels','evidence':'Existing human annotations associate labels primarily with figures; no author-visible device assigns them as spout values.','impact':'Do not use the pairs as numbered or named spouts.'},{'candidate':'MEANINGFUL_D_S_Q_OPERATORS','counterexample_type':'REGISTER_DIVERSITY_NO_VISUAL_ROLE','loci':'MANUSCRIPT_WIDE','tokens':'d-;s-;q-','evidence':'Formal prefix pairs span many folios, sections, labels and prose; page-conditioned visual scans yield no confirmed semantic partition.','impact':'Productive form contrast is not a meaningful operator assignment.'},{'candidate':'WHOLE_SLOT_MORPHOLOGY','counterexample_type':'GLOBAL_MDL_FAILURE','loci':'WHOLE_MANUSCRIPT','tokens':'prefix+core+suffix','evidence':'GDT001 reversible morphology grammar best total was 100562.898 bits worse than the global source winner.','impact':'The targeted inventory cannot claim a better complete generator than whole-source similarity.'}]
write_tsv(R/'gdt002_morphology_counterexamples.tsv',counter)

spot={}
for loc in ('f82r.35','f82r.38','f83r.50','f83r.51'):
 spot[loc]={e:next((x['surface'] for (l,i),m in groups.items() if l==loc and e in m for x in [m[e]]),'MISSING') for e in EDS}
free_f83={}
for form in ('dar','sar','dal','sy'):
 free_f83[form]={e:sorted({x['locus'] for x in types[e].get(form,[]) if x['page']=='f83r' and x['kind']=='P'}) for e in EDS}
f82v_spot={}
for loc in ('f82v.43','f82v.45','f82v.47','f82v.48'):
 a=ann.get(loc,{})
 f82v_spot[loc]={'readings':{e:next((x['surface'] for (l,i),m in groups.items() if l==loc and e in m for x in [m[e]]),'MISSING') for e in EDS},'human_description':a.get('local_comment',''),'annotation_certainty':a.get('certainty',''),'ownership_ceiling':'POSITION_OR_PROXIMITY_ONLY'}
nonflow={}
for loc in ('f99v.8','f102v2.14'):
 a=ann.get(loc,{})
 nonflow[loc]={'readings':{e:next((x['surface'] for (l,i),m in groups.items() if l==loc and e in m for x in [m[e]]),'MISSING') for e in EDS},'object_tags':a.get('object_tags',''),'human_description':a.get('local_comment',''),'annotation_certainty':a.get('certainty','')}
requested_pairs={}
for a,b in (('otedy','qotedy'),('oteedy','qoteedy'),('darol','sarol')):
 requested_pairs[a+'__'+b]=next((x for x in pairrows if x['left_form']==a and x['right_form']==b),None)
requested_splits={}
for a,b,j in (('ar','ol','arol'),('dar','ol','darol')):
 requested_splits[a+'__'+b+'__'+j]=next((x for x in splitrows if x['left_free_group']==a and x['right_free_group']==b and x['joined_form']==j),None)
best_visual=visual[:15]
result={'artifact':'GDT002_MORPHOLOGY_FALSIFICATION_V1','status':'FORMAL_REUSE_SUPPORTED_SEMANTIC_SLOT_SYSTEM_NOT_SUPPORTED','surface_policy':'Manual source groups; nearest-basic-EVA is a lossy display projection from source-native STA alignment. Cleaner-created fragment boundaries are never treated as spaces. f84r is guarded before formal retention/parsing.','modules':summary,'density':density,'density_sensitivity':density_sensitivity,'split_join':{'rows':len(splitrows),'manual_separator_states':dict(Counter(x['separator_states'] for x in splitrows)),'requested_examples':requested_splits},'minimal_pairs':{'generated_pair_types':sum(pair_rule_totals.values()),'generated_rules':dict(pair_rule_totals),'retained_rows':len(pairrows),'retained_rules':dict(Counter(x['pair_rule'] for x in pairrows)),'requested_examples':requested_pairs,'otedy_qotedy_present':any(x['left_form']=='otedy' and x['right_form']=='qotedy' for x in pairrows),'oteedy_qoteedy_present':any(x['left_form']=='oteedy' and x['right_form']=='qoteedy' for x in pairrows)},'spotlight_readings':spot,'f83r_free_running_forms':free_f83,'f82v_spatial_form_spotlight':f82v_spot,'nonflow_arol_sarol_examples':nonflow,'best_visual_associations':best_visual,'prior_complete_model_control':{'gdt001_morphology_gap_vs_global_source_winner_bits':100562.89786046906,'decision':'STOP_MORPHOLOGY_GRAMMAR'},'answer':'Reusable formal pieces are supported, but the fixed candidates do not establish a semantic four-slot morphology or outperform the existing whole-source model. Whole-word similarity alone is insufficient as a description, yet the proposed slot system is not a better complete decipherment model.','holdout':{'f84r_formal_retained_or_scored':False},'inputs':{str(p.relative_to(R)):sha(p) for p in [S/'source_separator_transcription.tsv',S/'source_sta_group_alignment.tsv',S/'existing_human_exact_locus_annotations.tsv',R/'gdt001_morphology_grammar_results.json',R/'GDT002_YOLO_LEDGER.tsv',R/'run_gdt002_morphology_falsification.py']},'documents':{str(p.relative_to(R)):sha(p) for p in [R/'GDT002_MORPHOLOGY_FALSIFICATION_REPORT.md',R/'GDT002_CURRENT_SUMMARY.md',R/'GDT002_METHOD.md']},'outputs':{n:sha(R/n) for n in ['gdt002_morphology_occurrences.tsv','gdt002_morphology_minimal_pairs.tsv','gdt002_morphology_split_join.tsv','gdt002_morphology_visual_associations.tsv','gdt002_morphology_rankings.tsv','gdt002_morphology_counterexamples.tsv']},'claim_ceiling':'Formal source-group reuse, position, pair, density, and exploratory annotation association only. No candidate is a morpheme, operator meaning, lexeme, sound, language, plaintext, or translation.'}
(R/'gdt002_morphology_results.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(result['status']);print('inventory',len(inventory),'pairs',len(pairrows),'split_join',len(splitrows));print('density',density);print('spotlight',spot);print('ranks',[(x['candidate'],x['rank']) for x in rankrows])
