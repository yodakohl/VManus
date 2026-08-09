#!/usr/bin/env python3
"""Independent reconstruction of the favored-shell member refinement."""

from __future__ import annotations
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from copy import deepcopy
from pathlib import Path

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL=RESULTS/"source_native_within_group_stage_masked.tsv";GROUPS=RESULTS/"source_sta_family_consensus_groups.tsv";FAMILY_ATLAS=RESULTS/"source_native_transition_atlas.tsv";FAMILY_VALIDATION=RESULTS/"source_native_transition_atlas_validation.json";RULES=BASE.parent.parent/"transcription"/"sources"/"sta"/"STA-Eva_def.bit";SPEC=BASE/"SOURCE_NATIVE_FAVORED_MEMBER_TRANSITION_SPEC.md";BUILDER=BASE/"build_source_native_favored_member_transition_atlas.py";ATLAS=RESULTS/"source_native_favored_member_transition_atlas.tsv";PRODUCTION=RESULTS/"source_native_favored_member_transition_atlas.json";PRODUCTION_REPORT=RESULTS/"source_native_favored_member_transition_atlas_report.md";OUT=RESULTS/"source_native_favored_member_transition_atlas_validation.json";REPORT=RESULTS/"source_native_favored_member_transition_atlas_validation_report.md"
FROZEN={PANEL:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",GROUPS:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",FAMILY_ATLAS:"f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",FAMILY_VALIDATION:"209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",RULES:"7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",SPEC:"8a996243bd31a69608494877115c68ea55dc3e804f44c2671d2e395ebb7c1481",BUILDER:"15550cca419515eb6b9403ef4263affefd2dcab5519c15d7381b3051bcb7537a",ATLAS:"776c94330f3caddb5175b6ac221e4baa82cfbc76b5304706d4a6540cfaab59ce",PRODUCTION:"3bfca64544e0971cc974cf267516edf2d8aaab2db22d2a19528afad16093cd85",PRODUCTION_REPORT:"234243940a1605426e6c1dc488dcad321cc207f5eaf5852f6b8bfd8de19b73c5"};SHELLS=("AQ","DA","KJ","LJ","PK","QK");CAPACITY={"AQ":(6567,6361,94,1695,4666),"DA":(3535,3519,93,677,2842),"KJ":(2570,2565,92,450,2115),"LJ":(1282,1151,81,175,976),"PK":(547,534,78,119,415),"QK":(2834,2746,94,815,1931)}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def inventory():
 codes=defaultdict(list);examples={}
 for raw in RULES.read_text().splitlines():
  line=raw.strip();parts=line.split(None,1)
  if line and not line.startswith('#') and len(parts)==2 and re.fullmatch(r'[A-Z][0-9A-Za-z]',parts[0]):codes[parts[0][0]].append(parts[0]);examples[parts[0]]=parts[1].strip()
 return dict(codes),examples
def folio(page):
 match=re.fullmatch(r'(f\d+)[rv]\d*',page)
 if match is None:raise ValueError('page')
 return match.group(1)
def events_from(groups,codes):
 selected=[row for row in groups if row['strict_zero_alternative']=='1' and row['grammar_scope']=='CONFIRMED_PROSE' and re.fullmatch(r'f\d+[rv]\d*',row['page'])]
 if len(selected)!=21899:raise ValueError('scope')
 all_counts=Counter();exact_counts=Counter();folios=defaultdict(set);curriers=Counter();events=[]
 for row in selected:
  family=row['family_surface'];views=[row[field].split() for field in ('zl_sta_codes','it_sta_codes','rf_sta_codes')]
  if any(len(view)!=len(family) for view in views):raise ValueError('geometry')
  for position in range(1,len(family)):
   shell=family[position-1:position+1]
   if shell not in SHELLS:continue
   all_counts[shell]+=1
   if not all(views[0][slot]==views[1][slot]==views[2][slot] for slot in (position-1,position)):continue
   left,right=views[0][position-1],views[0][position]
   if left not in codes[shell[0]] or right not in codes[shell[1]]:raise ValueError('family')
   held=folio(row['page']);exact_counts[shell]+=1;folios[shell].add(held);curriers[shell,row['currier']]+=1;events.append((shell,held,row['currier'],len(family),position,left,right))
 observed={shell:(all_counts[shell],exact_counts[shell],len(folios[shell]),curriers[shell,'A'],curriers[shell,'B']) for shell in SHELLS}
 if observed!=CAPACITY or len(events)!=16876:raise ValueError('capacity')
 return events
def calculate(events,codes,reverse):
 folios=sorted({event[1] for event in events},key=lambda value:int(value[1:]));total=Counter();held=Counter();oriented=[]
 for shell,f,c,length,position,left,right in events:
  if reverse:context,current,slot,destination=right,left,length-position,shell[0]
  else:context,current,slot,destination=left,right,position,shell[1]
  total[shell,c,length,slot,current]+=1;held[f,shell,c,length,slot,current]+=1;oriented.append((shell,f,c,length,slot,left,right,context,current,destination))
 observed=Counter();expected=defaultdict(float);opps=Counter();fobserved=Counter();fexpected=defaultdict(float);fopps=Counter();cobserved=Counter();cexpected=defaultdict(float);copps=Counter()
 for shell,f,c,length,slot,left,right,context,current,destination in oriented:
  vocabulary=codes[destination];counts=[total[shell,c,length,slot,value]-held[f,shell,c,length,slot,value] for value in vocabulary];den=sum(counts)+.5*len(vocabulary);pair=(shell,left,right);observed[pair]+=1;opps[shell,context]+=1;fobserved[f,pair]+=1;fopps[f,shell,context]+=1;cobserved[c,pair]+=1;copps[c,shell,context]+=1
  for value,count in zip(vocabulary,counts):
   candidate=(shell,value,context) if reverse else (shell,context,value);probability=(count+.5)/den;expected[candidate]+=probability;fexpected[f,candidate]+=probability;cexpected[c,candidate]+=probability
 output={}
 for shell in SHELLS:
  for left in codes[shell[0]]:
   for right in codes[shell[1]]:
    pair=(shell,left,right);context=right if reverse else left;eligible=[value for value in folios if fopps[value,shell,context]>=3];residual=[fobserved[value,pair]-fexpected[value,pair] for value in eligible];positive=sum(value>0 for value in residual);negative=sum(value<0 for value in residual);number=len(eligible);record={'observed':observed[pair],'expected':expected[pair],'opportunities':opps[shell,context],'log_observed_expected':math.log((observed[pair]+.5)/(expected[pair]+.5)),'eligible_folios':number,'positive_folios':positive,'negative_folios':negative,'zero_folios':number-positive-negative,'positive_fraction':positive/number if number else 0.,'negative_fraction':negative/number if number else 0.}
    for currier in 'AB':record[f'currier_{currier}_observed']=cobserved[currier,pair];record[f'currier_{currier}_expected']=cexpected[currier,pair];record[f'currier_{currier}_opportunities']=copps[currier,shell,context];record[f'currier_{currier}_log_observed_expected']=math.log((cobserved[currier,pair]+.5)/(cexpected[currier,pair]+.5))
    output[pair]=record
 return output
def favored(record):return record['observed']>=20 and record['expected']>=5 and record['log_observed_expected']>=math.log(2) and record['eligible_folios']>=10 and record['positive_fraction']>=.70 and all(record[f'currier_{currier}_opportunities']>=15 and record[f'currier_{currier}_expected']>=2 and record[f'currier_{currier}_log_observed_expected']>=math.log(1.2) for currier in 'AB')
def disfavored(record):return record['expected']>=15 and record['log_observed_expected']<=-math.log(2) and record['eligible_folios']>=10 and record['negative_fraction']>=.70 and all(record[f'currier_{currier}_opportunities']>=15 and record[f'currier_{currier}_expected']>=5 and record[f'currier_{currier}_log_observed_expected']<=-math.log(1.2) for currier in 'AB')
def rejects(groups,codes,mutation):
 altered=deepcopy(groups);mutation(altered)
 try:events_from(altered,codes)
 except ValueError:return True
 return False
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 failures=[];checks=0
 def check(condition,name):
  nonlocal checks;checks+=1
  if not condition:failures.append(name)
 for path,expected in FROZEN.items():check(sha(path)==expected,f'hash:{path.name}')
 with GROUPS.open(encoding='utf-8',newline='') as handle:groups=list(csv.DictReader(handle,delimiter='\t'))
 codes,examples=inventory();events=events_from(groups,codes);forward=calculate(events,codes,False);backward=calculate(events,codes,True)
 with ATLAS.open(encoding='utf-8',newline='') as handle:stored_rows=list(csv.DictReader(handle,delimiter='\t'))
 stored={row['pair_id']:row for row in stored_rows};check(len(stored_rows)==685 and len(stored)==685,'rows');labels=Counter();maximum_delta=0.;favored_ids=[];disfavored_ids=[]
 for shell in SHELLS:
  for left in codes[shell[0]]:
   for right in codes[shell[1]]:
    pair=(shell,left,right);first=forward[pair];second=backward[pair];check(first['observed']==second['observed'],f'count:{left}>{right}');label='FAVORED_MEMBER_PAIR' if favored(first) and favored(second) else ('DISFAVORED_MEMBER_PAIR' if disfavored(first) and disfavored(second) else 'UNRESOLVED');labels[label]+=1;pair_id=left+'>'+right;row=stored[pair_id];check(row['family_shell']==shell and row['left_member']==left and row['right_member']==right and row['left_official_example']==examples[left] and row['right_official_example']==examples[right] and int(row['observed_physical_count'])==first['observed'] and row['structural_label']==label,'row:'+pair_id)
    for prefix,record in (('forward',first),('reversed',second)):
     for field,value in record.items():delta=abs(float(row[prefix+'_'+field])-float(value));maximum_delta=max(maximum_delta,delta);check(delta<=1e-10,f'numeric:{pair_id}:{prefix}:{field}')
    if label=='FAVORED_MEMBER_PAIR':favored_ids.append(pair_id)
    if label=='DISFAVORED_MEMBER_PAIR':disfavored_ids.append(pair_id)
 production=json.loads(PRODUCTION.read_text());check(production['counts']=={'favored_family_shells':6,'all_shell_occurrences':17335,'exact_all_three_member_occurrences':16876,'excluded_member_disagreements':459,'official_candidate_member_pairs':685,'labels':dict(sorted(labels.items()))},'counts');check(production['strongest_favored']==[] and production['strongest_disfavored']==[] and favored_ids==[] and disfavored_ids==[],'zero selected');check(production['tsv_sha256']==sha(ATLAS),'binding');check(production['inputs']=={path.name:sha(path) for path in list(FROZEN)[:7]},'inputs');check(production['english_glosses']==0 and 'not sounds' in production['claim_ceiling'],'ceiling')
 expected_report=f"""# Exact-member refinement of favored family transitions

Status: **{production['status']}**

The six frozen family shells contain **17,335** occurrences; **16,876**
retain exact adjacent member codes in all three readings. Of **685**
official within-shell member pairs, the frozen two-orientation rules classify
**0** as favored and
**0** as disfavored. Strongest favored:
none. Strongest disfavored: none.

Every label is conditional on its already favored family shell, Currier,
complete length, exact position, held folio, and the opposite orientation. The
readings provide a confidence filter, not replications. This is a descriptive
decomposition, not hundreds of new tests, and supplies no sound, letter,
syllable, morpheme, word, syntax, language, cipher operation, meaning,
plaintext, or translation.
""";check(PRODUCTION_REPORT.read_text()==expected_report,'report');index=next(i for i,row in enumerate(groups) if row['strict_zero_alternative']=='1' and row['grammar_scope']=='CONFIRMED_PROSE');check(rejects(groups,codes,lambda rows:rows.pop(index)),'missing');check(rejects(groups,codes,lambda rows:rows.append(dict(rows[index]))),'duplicate');check(rejects(groups,codes,lambda rows:rows[index].__setitem__('zl_sta_codes','I')),'invalid');check(rejects(groups,codes,lambda rows:rows[index].__setitem__('family_surface','AQ')),'geometry')
 if failures:raise SystemExit('validation failed: '+failures[0])
 result={'experiment':'SOURCE_NATIVE_FAVORED_MEMBER_TRANSITION_VALIDATION','status':'PASS_INDEPENDENT_685_PAIR_ZERO_SELECTION_RECONSTRUCTION','checks':checks,'failures':[],'maximum_numeric_delta':maximum_delta,'all_shell_occurrences':17335,'exact_member_occurrences':16876,'candidate_pairs':685,'favored_member_pairs':0,'disfavored_member_pairs':0,'mutations':4,'english_glosses':0,'inputs':{path.name:sha(path) for path in FROZEN},'claim_ceiling':'Independent descriptive reconstruction of the zero exact-member-pair selection inside six neutral family shells; no sound, letter, syllable, morpheme, word, syntax, language, cipher, meaning, plaintext, or translation follows.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Favored-shell member-refinement validation

Status: **{result['status']}**

A production-free implementation reconstructs all **16,876** exact events and
**685** official candidate pairs, every leave-folio-out expectation, both
orientations, Currier controls, zero-pair decision, bindings, report, and four
mutations in **{checks:,}** checks. Maximum numeric discrepancy is
**{maximum_delta:.3g}**.

This validates only the absence of a pair passing the frozen exact-member
refinement. It supplies no sound, morpheme, word, syntax, language, meaning,
plaintext, cipher, or translation.
""");print(json.dumps({'status':result['status'],'checks':checks,'max_delta':maximum_delta},sort_keys=True))
if __name__=='__main__':main()
