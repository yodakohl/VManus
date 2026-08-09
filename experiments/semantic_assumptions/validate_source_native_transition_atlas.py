#!/usr/bin/env python3
"""Independent reconstruction of the held-folio transition atlas."""

from __future__ import annotations
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from copy import deepcopy
from pathlib import Path
import numpy as np

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_within_group_stage_masked.tsv";GROUPS=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json";TARGET=RESULTS/"source_native_within_group_exact_position_markov_target.json";TARGET_VALIDATION=RESULTS/"source_native_within_group_exact_position_markov_target_validation.json";RULES=BASE.parent.parent/"transcription"/"sources"/"sta"/"STA-Eva_def.bit";SPEC=BASE/"SOURCE_NATIVE_TRANSITION_ATLAS_SPEC.md";BUILDER=BASE/"build_source_native_transition_atlas.py";ATLAS=RESULTS/"source_native_transition_atlas.tsv";PRODUCTION=RESULTS/"source_native_transition_atlas.json";PRODUCTION_REPORT=RESULTS/"source_native_transition_atlas_report.md";OUT=RESULTS/"source_native_transition_atlas_validation.json";REPORT=RESULTS/"source_native_transition_atlas_validation_report.md"
FROZEN={PANEL_PATH:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",GROUPS:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",TARGET:"5c59e783919dc35046ad8f941f4ad28e4f272d3e062773a783a6f048c3d8ec33",TARGET_VALIDATION:"9f621e977e0640f9f2104e6b0133c898a2802f7ae063ce396e6cb746b6f96282",RULES:"7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",SPEC:"06c9145eb362ae42be5e47f0ab87c2da3f6553e12a9b133d6bb985e8a43f70f2",BUILDER:"a74ffc096daf3f47bf204c1381bcc758a3cc76b85851089ef226d045f914d3fd",ATLAS:"f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",PRODUCTION:"c8450cb4585fc1c766b278d9cfbef75e2d25260a9c792aaeffd7210f3c6c77fd",PRODUCTION_REPORT:"49f357d45f3218fbf32ea4d6480c46d53ccf7bd79686c2fd4a2d714a57d1e46d"}
ALPHABET=tuple("ABCDEFGHJKLMNPQRSTUVWXYZ");INDEX={value:index for index,value in enumerate(ALPHABET)};PANEL_FIELDS=("unit_id","locus","page","physical_folio","section","currier","hand","kind","symbol_count","split");SOURCE_FIELDS=("consensus_group_id","locus","page","section","currier","hand","code","kind","grammar_scope","strict_zero_alternative","consensus_group_index","consensus_group_count","start_symbol_1based","end_symbol_1based","symbol_count","family_surface","zl_sta_codes","it_sta_codes","rf_sta_codes","left_boundary_profile","right_boundary_profile")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def members():
 result=defaultdict(list)
 for raw in RULES.read_text().splitlines():
  line=raw.strip();parts=line.split(None,1)
  if line and not line.startswith('#') and len(parts)==2 and re.fullmatch(r'[A-Z][0-9A-Za-z]',parts[0]):result[parts[0][0]].append(f'{parts[0]}={parts[1].strip()}')
 if set(result)!=set(ALPHABET):raise ValueError('members')
 return dict(result)
def read_inputs():
 with PANEL_PATH.open(encoding='utf-8',newline='') as handle:
  reader=csv.DictReader(handle,delimiter='\t')
  if tuple(reader.fieldnames or ())!=PANEL_FIELDS:raise ValueError('panel schema')
  panel=list(reader)
 with GROUPS.open(encoding='utf-8',newline='') as handle:
  reader=csv.DictReader(handle,delimiter='\t')
  if tuple(reader.fieldnames or ())!=SOURCE_FIELDS:raise ValueError('source schema')
  groups=list(reader)
 return panel,groups
def join(panel,groups):
 if len(panel)!=21899 or len(groups)!=26184 or len({row['unit_id'] for row in panel})!=21899:raise ValueError('cardinality')
 source={row['consensus_group_id']:row for row in groups}
 if len(source)!=len(groups):raise ValueError('duplicate source')
 eligible={row['consensus_group_id'] for row in groups if row['strict_zero_alternative']=='1' and row['grammar_scope']=='CONFIRMED_PROSE' and re.fullmatch(r'f\d+[rv]\d*',row['page'])}
 if eligible!={row['unit_id'] for row in panel}:raise ValueError('eligible')
 sequences=[]
 for masked in panel:
  row=source[masked['unit_id']];surface=row['family_surface']
  if len(surface)!=int(masked['symbol_count']) or int(row['symbol_count'])!=len(surface) or any(value not in INDEX for value in surface):raise ValueError('surface')
  if any(masked[key]!=row[key] for key in ('locus','page','section','currier','hand','kind')):raise ValueError('metadata')
  sequences.append(tuple(INDEX[value] for value in surface))
 return sequences
def metrics(panel,sequences,reverse):
 folios=sorted({row['physical_folio'] for row in panel},key=lambda value:int(value[1:]));findex={value:index for index,value in enumerate(folios)};cindex={'A':0,'B':1};total=Counter();held=Counter();events=[]
 for row,original in zip(panel,sequences):
  sequence=tuple(reversed(original)) if reverse else original;f=findex[row['physical_folio']];c=cindex[row['currier']];length=len(sequence)
  for position in range(1,length):
   previous,current=sequence[position-1],sequence[position];total[(c,length,position,current)]+=1;held[(f,c,length,position,current)]+=1;events.append((f,c,length,position,previous,current))
 observed=np.zeros((24,24),dtype=np.int64);expected=np.zeros((24,24));opportunities=np.zeros(24,dtype=np.int64);fobserved=np.zeros((94,24,24),dtype=np.int64);fexpected=np.zeros((94,24,24));fopportunities=np.zeros((94,24),dtype=np.int64);cobserved=np.zeros((2,24,24),dtype=np.int64);cexpected=np.zeros((2,24,24));copportunities=np.zeros((2,24),dtype=np.int64)
 for f,c,length,position,previous,current in events:
  training=np.asarray([total[(c,length,position,value)]-held[(f,c,length,position,value)] for value in range(24)],dtype=np.float64);probabilities=(training+.5)/(training.sum()+12.)
  observed[previous,current]+=1;expected[previous]+=probabilities;opportunities[previous]+=1;fobserved[f,previous,current]+=1;fexpected[f,previous]+=probabilities;fopportunities[f,previous]+=1;cobserved[c,previous,current]+=1;cexpected[c,previous]+=probabilities;copportunities[c,previous]+=1
 output={}
 for previous in range(24):
  eligible=fopportunities[:,previous]>=5
  for current in range(24):
   residual=fobserved[:,previous,current]-fexpected[:,previous,current];positive=int(((residual>0)&eligible).sum());negative=int(((residual<0)&eligible).sum());number=int(eligible.sum());record={'observed':int(observed[previous,current]),'expected':float(expected[previous,current]),'opportunities':int(opportunities[previous]),'log_observed_expected':float(math.log((observed[previous,current]+.5)/(expected[previous,current]+.5))),'eligible_folios':number,'positive_folios':positive,'negative_folios':negative,'zero_folios':number-positive-negative,'positive_fraction':positive/number if number else 0.,'negative_fraction':negative/number if number else 0.}
   for currier,c in cindex.items():record[f'currier_{currier}_observed']=int(cobserved[c,previous,current]);record[f'currier_{currier}_expected']=float(cexpected[c,previous,current]);record[f'currier_{currier}_opportunities']=int(copportunities[c,previous]);record[f'currier_{currier}_log_observed_expected']=float(math.log((cobserved[c,previous,current]+.5)/(cexpected[c,previous,current]+.5)))
   output[(previous,current)]=record
 return output,len(events)
def favored(record):return record['observed']>=30 and record['expected']>=10 and record['log_observed_expected']>=math.log(2) and record['eligible_folios']>=12 and record['positive_fraction']>=.75 and all(record[f'currier_{currier}_opportunities']>=30 and record[f'currier_{currier}_expected']>=5 and record[f'currier_{currier}_log_observed_expected']>=math.log(1.3) for currier in 'AB')
def disfavored(record):return record['expected']>=30 and record['log_observed_expected']<=-math.log(2) and record['eligible_folios']>=12 and record['negative_fraction']>=.75 and all(record[f'currier_{currier}_opportunities']>=30 and record[f'currier_{currier}_expected']>=10 and record[f'currier_{currier}_log_observed_expected']<=-math.log(1.3) for currier in 'AB')
def numeric_max(left,right):
 if isinstance(left,dict):return math.inf if set(left)!=set(right) else max((numeric_max(left[key],right[key]) for key in left),default=0.)
 if isinstance(left,list):return math.inf if len(left)!=len(right) else max((numeric_max(a,b) for a,b in zip(left,right)),default=0.)
 if isinstance(left,(int,float)) and not isinstance(left,bool):return abs(float(left)-float(right))
 return 0. if left==right else math.inf
def reject_mutation(panel,groups,mutation):
 p=deepcopy(panel);g=deepcopy(groups);mutation(p,g)
 try:join(p,g)
 except (ValueError,KeyError):return True
 return False
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 failures=[];checks=0
 def check(condition,name):
  nonlocal checks;checks+=1
  if not condition:failures.append(name)
 for path,expected in FROZEN.items():check(sha(path)==expected,f'hash:{path.name}')
 panel,groups=read_inputs();sequences=join(panel,groups);forward,event_count=metrics(panel,sequences,False);backward,reverse_events=metrics(panel,sequences,True);check(event_count==67313 and reverse_events==event_count,'capacity');member_map=members()
 with ATLAS.open(encoding='utf-8',newline='') as handle:stored_rows=list(csv.DictReader(handle,delimiter='\t'))
 check(len(stored_rows)==576 and len({row['pair_id'] for row in stored_rows})==576,'rows');stored={row['pair_id']:row for row in stored_rows};rebuilt=[];maximum_delta=0.
 for left in range(24):
  for right in range(24):
   first=forward[(left,right)];second=backward[(right,left)];check(first['observed']==second['observed'],f'count:{left}:{right}');label='FAVORED_ADJACENCY' if favored(first) and favored(second) else ('DISFAVORED_ADJACENCY' if disfavored(first) and disfavored(second) else 'UNRESOLVED');pair=ALPHABET[left]+ALPHABET[right];row=stored[pair];check(row['left_family']==ALPHABET[left] and row['right_family']==ALPHABET[right] and int(row['observed_physical_count'])==first['observed'] and row['structural_label']==label,'identity:'+pair);check(row['left_member_examples']==';'.join(member_map[ALPHABET[left]][:4]) and row['right_member_examples']==';'.join(member_map[ALPHABET[right]][:4]),'examples:'+pair)
   for prefix,record in (('forward',first),('reversed',second)):
    for field,value in record.items():
     actual=float(row[f'{prefix}_{field}']);delta=abs(actual-float(value));maximum_delta=max(maximum_delta,delta);check(delta<=1e-10,f'numeric:{pair}:{prefix}:{field}')
   rebuilt.append({'pair_id':pair,'label':label,'first':first,'second':second})
 counts=Counter(row['label'] for row in rebuilt);favored_rows=sorted((row for row in rebuilt if row['label']=='FAVORED_ADJACENCY'),key=lambda row:(-min(row['first']['log_observed_expected'],row['second']['log_observed_expected']),row['pair_id']));disfavored_rows=sorted((row for row in rebuilt if row['label']=='DISFAVORED_ADJACENCY'),key=lambda row:(max(row['first']['log_observed_expected'],row['second']['log_observed_expected']),row['pair_id']))
 production=json.loads(PRODUCTION.read_text());check(production['status']=='PASS_DESCRIPTIVE_CONFIRMED_TRANSITION_DECOMPOSITION','status');check(production['counts']=={'complete_groups':21899,'physical_folios':94,'transition_events_per_orientation':67313,'family_pairs':576,'labels':dict(sorted(counts.items()))},'counts');check(production['tsv_sha256']==sha(ATLAS),'tsv binding');check(production['inputs']=={path.name:sha(path) for path in (*list(FROZEN)[:8],)},'inputs')
 check([row['pair_id'] for row in favored_rows[:16]]==[row['pair_id'] for row in production['strongest_favored']],'favored order');check([row['pair_id'] for row in disfavored_rows[:16]]==[row['pair_id'] for row in production['strongest_disfavored']],'disfavored order')
 for record,row in zip(production['strongest_favored'],favored_rows[:16]):check(numeric_max(record,{'pair_id':row['pair_id'],'observed':row['first']['observed'],'forward_log_observed_expected':row['first']['log_observed_expected'],'reversed_log_observed_expected':row['second']['log_observed_expected'],'forward_positive_fraction':row['first']['positive_fraction'],'reversed_positive_fraction':row['second']['positive_fraction'],'forward_negative_fraction':row['first']['negative_fraction'],'reversed_negative_fraction':row['second']['negative_fraction']})<=1e-10,'favored summary:'+row['pair_id'])
 for record,row in zip(production['strongest_disfavored'],disfavored_rows[:16]):check(numeric_max(record,{'pair_id':row['pair_id'],'observed':row['first']['observed'],'forward_log_observed_expected':row['first']['log_observed_expected'],'reversed_log_observed_expected':row['second']['log_observed_expected'],'forward_positive_fraction':row['first']['positive_fraction'],'reversed_positive_fraction':row['second']['positive_fraction'],'forward_negative_fraction':row['first']['negative_fraction'],'reversed_negative_fraction':row['second']['negative_fraction']})<=1e-10,'disfavored summary:'+row['pair_id'])
 favored_text=', '.join(row['pair_id'] for row in favored_rows[:12]) or 'none';disfavored_text=', '.join(row['pair_id'] for row in disfavored_rows[:12]) or 'none';expected_report=f"""# Held-folio source-family transition atlas

Status: **{production['status']}**

Across **{event_count:,}** noninitial family events on **94** physical
folios, the frozen two-orientation rules classify
**{counts['FAVORED_ADJACENCY']}** of 576 physical pairs as favored and
**{counts['DISFAVORED_ADJACENCY']}** as disfavored; the rest are
unresolved. Strongest favored pairs: {favored_text}. Strongest disfavored
pairs: {disfavored_text}.

Every label requires leave-folio-out exact-position baselines, the same sign in
both physical orientations, broad folio support, and the same direction in
Currier A and B. This is a descriptive decomposition of an already confirmed
aggregate model, not 576 new confirmatory tests. Family letters are neutral STA
classes; no sound, letter, syllable, morpheme, prefix, root, suffix, word,
syntax label, language, cipher operation, meaning, plaintext, or translation
follows.
""";check(PRODUCTION_REPORT.read_text()==expected_report,'report');check(production['english_glosses']==0 and 'not sounds' in production['claim_ceiling'],'ceiling')
 check(reject_mutation(panel,groups,lambda p,g:p.__setitem__(0,dict(p[1]))),'duplicate panel');check(reject_mutation(panel,groups,lambda p,g:g.pop(next(i for i,row in enumerate(g) if row['consensus_group_id']==p[0]['unit_id']))),'missing source');check(reject_mutation(panel,groups,lambda p,g:next(row for row in g if row['consensus_group_id']==p[0]['unit_id']).__setitem__('family_surface','I')),'invalid family');check(reject_mutation(panel,groups,lambda p,g:next(row for row in g if row['consensus_group_id']==p[0]['unit_id']).__setitem__('page','f999r')),'metadata')
 if failures:raise SystemExit('validation failed: '+failures[0])
 result={'experiment':'SOURCE_NATIVE_TRANSITION_ATLAS_VALIDATION','status':'PASS_INDEPENDENT_576_PAIR_HELD_FOLIO_RECONSTRUCTION','checks':checks,'failures':[],'maximum_numeric_delta':maximum_delta,'counts':{'transition_events':event_count,'family_pairs':576,'favored':counts['FAVORED_ADJACENCY'],'disfavored':counts['DISFAVORED_ADJACENCY'],'unresolved':counts['UNRESOLVED']},'favored_pairs':[row['pair_id'] for row in favored_rows],'strongest_disfavored_pairs':[row['pair_id'] for row in disfavored_rows[:16]],'mutations':4,'english_glosses':0,'inputs':{path.name:sha(path) for path in FROZEN},'claim_ceiling':'Independent descriptive reconstruction of neutral physical source-family adjacency constraints only; no sound, letter, syllable, morpheme, word, syntax label, language, cipher, meaning, plaintext, or translation follows.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Held-folio transition-atlas validation

Status: **{result['status']}**

A production-free dictionary implementation reconstructs all **67,313** events,
**576** family pairs, every leave-folio-out expected count, both orientations,
Currier controls, labels, official examples, summaries, bindings, report, and
four mutations in **{checks:,}** checks. Maximum numeric discrepancy is
**{maximum_delta:.3g}**. The six favored pairs are
`{', '.join(result['favored_pairs'])}`.

This validates only a neutral decomposition of the confirmed structural model;
no sound, morpheme, word, syntax label, language, meaning, plaintext, cipher,
or translation follows.
""");print(json.dumps({'status':result['status'],'checks':checks,'max_delta':maximum_delta,'favored':result['favored_pairs']},sort_keys=True))
if __name__=='__main__':main()
