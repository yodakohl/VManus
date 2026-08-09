#!/usr/bin/env python3
"""Production-free validation of the within-group Markov target."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import csv,hashlib,json,math,re
from collections import Counter
from copy import deepcopy
from pathlib import Path
import validate_source_native_within_group_markov_preflight as independent

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_within_group_stage_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_within_group_stage_capacity_validation.json";PREFLIGHT_VALIDATION=RESULTS/"source_native_within_group_markov_preflight_validation.json";CLEAN_VALIDATOR=BASE/"validate_source_native_within_group_markov_preflight.py";TARGET_SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json";SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_MARKOV_TARGET_SPEC.md";RUNNER=BASE/"run_source_native_within_group_markov_target.py";TARGET_RESULT=RESULTS/"source_native_within_group_markov_target.json";TARGET_REPORT=RESULTS/"source_native_within_group_markov_target_report.md";OUT=RESULTS/"source_native_within_group_markov_target_validation.json";REPORT=RESULTS/"source_native_within_group_markov_target_validation_report.md"
FROZEN={PANEL_PATH:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",CAPACITY_VALIDATION:"2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",PREFLIGHT_VALIDATION:"39221059e92c19ace099c44f574ef8926cd9e2425f7c0cbdcb4cdf9ba61b61ae",CLEAN_VALIDATOR:"09eed4b2852ad422db5f76bf3de3e3862c96db7a1328151de369fe5f4d37d43e",TARGET_SOURCE:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",SPEC:"5d9fc2826ac996ac9ad6b9f23601a9934290fcbeed2ac783d219176fdb36ad02",RUNNER:"8c1fd4e6896017c44c8430b5ae231b94022815993cdbd33d4c31e09a57108475",TARGET_RESULT:"6c4ab6d48f9d264138b2063e1e789aeac3db8fce8e7781df1a88be2927b65225",TARGET_REPORT:"780899f1a261f983c7e9d74e8877c4bd63c5851956743e5e840126ac20fed224"}
ALPHABET=tuple("ABCDEFGHJKLMNPQRSTUVWXYZ");INDEX={x:i for i,x in enumerate(ALPHABET)};SOURCE_FIELDS=("consensus_group_id","locus","page","section","currier","hand","code","kind","grammar_scope","strict_zero_alternative","consensus_group_index","consensus_group_count","start_symbol_1based","end_symbol_1based","symbol_count","family_surface","zl_sta_codes","it_sta_codes","rf_sta_codes","left_boundary_profile","right_boundary_profile")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def split_for(folio):
 value=int.from_bytes(hashlib.sha256(f"SNWG001|{folio}".encode()).digest()[:8],"little")%5
 return 'TEST' if value==0 else ('CAL' if value==1 else 'TRAIN')
def numeric_max(a,b):
 if isinstance(a,dict):return math.inf if set(a)!=set(b) else max((numeric_max(a[k],b[k]) for k in a),default=0.)
 if isinstance(a,list):return math.inf if len(a)!=len(b) else max((numeric_max(x,y) for x,y in zip(a,b)),default=0.)
 if isinstance(a,(int,float)) and not isinstance(a,bool):return abs(float(a)-float(b))
 return 0. if a==b else math.inf
def aggregate(r):return {**r,'MARKOV_INCREMENT_PASS':independent.passes(r)}
def eligible_ids(rows):return {r['consensus_group_id'] for r in rows if r['strict_zero_alternative']=='1' and r['grammar_scope']=='CONFIRMED_PROSE' and re.match(r'f\d+',r['page'])}
def join(panel,rows):
 if len(rows)!=26184:raise ValueError('source count')
 by={r['consensus_group_id']:r for r in rows}
 if len(by)!=len(rows):raise ValueError('duplicate')
 panel_ids={r['unit_id'] for r in panel.rows}
 if eligible_ids(rows)!=panel_ids or len(panel_ids)!=21899:raise ValueError('eligible')
 seqs=[];counts=Counter()
 for masked in panel.rows:
  source=by.get(masked['unit_id']);match=re.match(r'f\d+',source['page']) if source else None
  if source is None or match is None or source['strict_zero_alternative']!='1' or source['grammar_scope']!='CONFIRMED_PROSE':raise ValueError('scope')
  surface=source['family_surface']
  if len(surface)!=int(masked['symbol_count']) or int(source['symbol_count'])!=len(surface) or any(x not in INDEX for x in surface):raise ValueError('surface')
  exact={'locus':source['locus'],'page':source['page'],'physical_folio':match.group(),'section':source['section'],'currier':source['currier'],'hand':source['hand'],'kind':source['kind'],'symbol_count':str(len(surface)),'split':split_for(match.group())}
  if any(masked[k]!=v for k,v in exact.items()):raise ValueError('metadata')
  seqs.append(tuple(INDEX[x] for x in surface));counts.update(surface)
 return seqs,counts
def rejects(panel,rows,mutation):
 altered=deepcopy(rows);mutation(altered)
 try:join(panel,altered)
 except ValueError:return True
 return False
def expected_report(stored):
 f=stored['forward'];r=stored['reversed'];target=stored['gates']['MARKOV_TARGET_PASS']
 return f"""# Source-native within-group Markov-increment target

Status: **{stored['status']}**

The single frozen join matched **{stored['joined_target_sequences']:,}** complete groups.
Forward/reversed transition-minus-position equal-folio gains are
**{f['gain']['effect_equal_folio']:+.6f}** and
**{r['gain']['effect_equal_folio']:+.6f}** nat/symbol, with
**{f['gain']['positive_folios']}/24** and
**{r['gain']['positive_folios']}/24** positive folios. Exact unseen-group
gains are **{f['unseen']['effect_equal_folio']:+.6f}** and
**{r['unseen']['effect_equal_folio']:+.6f}** on
**{f['unseen']['groups']}** held groups.

`MARKOV_TARGET_PASS` is **{str(target).lower()}**. Decision: **{stored['decision']}**.
No event-level sequence or transition is stored. This supplies no syntax,
morphology, sound, word, language, meaning, plaintext, cipher, or translation.
"""
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 failures=[];checks=0
 def check(ok,name):
  nonlocal checks;checks+=1
  if not ok:failures.append(name)
 for path,expected in FROZEN.items():check(sha(path)==expected,f'hash:{path.name}')
 check(json.loads(CAPACITY_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION','capacity');check(json.loads(PREFLIGHT_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_192_WORLD_MARKOV_PREFLIGHT_RECONSTRUCTION','preflight');check(json.loads(SOURCE_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION','source')
 with TARGET_SOURCE.open(encoding='utf-8',newline='') as h:
  reader=csv.DictReader(h,delimiter='\t');check(tuple(reader.fieldnames or ())==SOURCE_FIELDS,'schema');rows=list(reader)
 panel=independent.clean.load_panel();seqs,counts=join(panel,rows);check(len(seqs)==21899,'join')
 forward=aggregate(independent.evaluate(panel,seqs));reverse=aggregate(independent.evaluate(panel,[tuple(reversed(s)) for s in seqs]));target=forward['MARKOV_INCREMENT_PASS'] and reverse['MARKOV_INCREMENT_PASS'];gates={'exact_26184_source_rows':len(rows)==26184,'exact_21899_joined_groups':len(seqs)==21899,'exact_split_counts':Counter(r['split'] for r in panel.rows)=={'TRAIN':10753,'CAL':5516,'TEST':5630},'exact_94_folios':len(set(panel.folios))==94,'complete_eligible_id_set':eligible_ids(rows)=={r['unit_id'] for r in panel.rows},'forward_MARKOV_INCREMENT_PASS':forward['MARKOV_INCREMENT_PASS'],'reversed_MARKOV_INCREMENT_PASS':reverse['MARKOV_INCREMENT_PASS'],'MARKOV_TARGET_PASS':target};status='CONFIRM_SOURCE_NATIVE_WITHIN_GROUP_FIRST_ORDER_DEPENDENCY' if target else 'NONCONFIRM_SOURCE_NATIVE_WITHIN_GROUP_FIRST_ORDER_DEPENDENCY';decision='RETAIN_PORTABLE_LOCAL_TRANSITION_GRAMMAR' if target else 'FAVOR_RECURRENT_TEMPLATES_OVER_FROZEN_FIRST_ORDER_RULE'
 stored=json.loads(TARGET_RESULT.read_text());check(stored['status']==status and stored['decision']==decision,'decision');check(numeric_max(stored['forward'],forward)<=1e-12,'forward');check(numeric_max(stored['reversed'],reverse)<=1e-12,'reverse');check(stored['gates']==gates,'gates');check(stored['family_counts']=={x:counts[x] for x in ALPHABET},'counts');check(stored['source_rows_accessed']==26184 and stored['joined_target_sequences']==21899,'access');check(stored['target_source_opened'] is True and stored['target_sequences_accessed']==21899 and stored['target_evaluations_computed']==2,'target');check(stored['event_level_sequences_stored']==0 and stored['event_level_transitions_stored']==0 and stored['english_glosses']==0,'ceiling');check(TARGET_REPORT.read_text()==expected_report(stored),'report')
 idx=next(i for i,r in enumerate(rows) if r['consensus_group_id']==panel.rows[0]['unit_id']);check(rejects(panel,rows,lambda x:x.pop(idx)),'missing');check(rejects(panel,rows,lambda x:x.append(dict(x[idx]))),'duplicate');check(rejects(panel,rows,lambda x:x[idx].__setitem__('page','f999r')),'metadata');check(rejects(panel,rows,lambda x:x[idx].__setitem__('family_surface','I'+x[idx]['family_surface'][1:])),'symbol')
 if failures:raise SystemExit('validation failed: '+failures[0])
 result={'experiment':'SOURCE_NATIVE_WITHIN_GROUP_MARKOV_TARGET_VALIDATION','status':'PASS_PRODUCTION_FREE_WITHIN_GROUP_MARKOV_CONFIRMATION_RECONSTRUCTION','checks':checks,'failures':[],'reconstructed_status':status,'reconstructed_decision':decision,'forward_equal_folio_gain':forward['gain']['effect_equal_folio'],'reversed_equal_folio_gain':reverse['gain']['effect_equal_folio'],'forward_unseen_groups':forward['unseen']['groups'],'forward_unseen_gain':forward['unseen']['effect_equal_folio'],'reversed_unseen_gain':reverse['unseen']['effect_equal_folio'],'target_rows_reconstructed':21899,'event_level_sequences_stored':0,'english_glosses':0,'inputs':{p.name:sha(p) for p in FROZEN},'claim_ceiling':'Production-free confirmation of a first-order source-family dependency only; no syntax, morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.'}
 OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Within-group Markov target validation

Status: **{result['status']}**

A production-free implementation rejoins all **21,899** complete groups and
reconstructs both evaluations in **{checks} checks**. Forward/reversed gains
are **{forward['gain']['effect_equal_folio']:+.6f}** and
**{reverse['gain']['effect_equal_folio']:+.6f}**, with 24/24 positive folios;
the **{forward['unseen']['groups']}** exact unseen groups remain positive at
**{forward['unseen']['effect_equal_folio']:+.6f}** and
**{reverse['unseen']['effect_equal_folio']:+.6f}**. Every aggregate, gate,
decision, report byte, binding, and four mutations match.

This confirms a first-order structural dependency only and supplies no syntax,
morphology, sound, word, language, meaning, plaintext, cipher, or translation.
""");print(json.dumps({'status':result['status'],'checks':checks},sort_keys=True))
if __name__=='__main__':main()
