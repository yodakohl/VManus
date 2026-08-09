#!/usr/bin/env python3
"""Production-free validation of the exact-position transition target."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import csv,hashlib,json,math,re
from collections import Counter
from copy import deepcopy
from pathlib import Path
import validate_source_native_within_group_exact_position_markov_preflight as independent

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_within_group_stage_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_within_group_stage_capacity_validation.json";PREFLIGHT_VALIDATION=RESULTS/"source_native_within_group_exact_position_markov_preflight_validation.json";CLEAN_VALIDATOR=BASE/"validate_source_native_within_group_exact_position_markov_preflight.py";TARGET_SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json";SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_TARGET_SPEC.md";RUNNER=BASE/"run_source_native_within_group_exact_position_markov_target.py";TARGET_RESULT=RESULTS/"source_native_within_group_exact_position_markov_target.json";TARGET_REPORT=RESULTS/"source_native_within_group_exact_position_markov_target_report.md";OUT=RESULTS/"source_native_within_group_exact_position_markov_target_validation.json";REPORT=RESULTS/"source_native_within_group_exact_position_markov_target_validation_report.md"
FROZEN={PANEL_PATH:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",CAPACITY_VALIDATION:"2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",PREFLIGHT_VALIDATION:"6926383302f914eeb958e22ee1410b2c0369312492625a04e9a54243e15585c6",CLEAN_VALIDATOR:"53603e375458f04625fe013681c5cd7676a94f2538a01172555eb70c460ac6a2",TARGET_SOURCE:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",SPEC:"81336cfaba5cd1d2221783d01ea3a63edc8d7e0489177902ea3174501ed32671",RUNNER:"c8c4534dc12ced579f3d409e62b922df66599976a4213cb3c7da2eb433f770e5",TARGET_RESULT:"5c59e783919dc35046ad8f941f4ad28e4f272d3e062773a783a6f048c3d8ec33",TARGET_REPORT:"1afa9190203b41634346aa9e9a020b7875e7aacacf2268d621f90a624767c313"}
ALPHABET=tuple("ABCDEFGHJKLMNPQRSTUVWXYZ");INDEX={symbol:index for index,symbol in enumerate(ALPHABET)};SOURCE_FIELDS=("consensus_group_id","locus","page","section","currier","hand","code","kind","grammar_scope","strict_zero_alternative","consensus_group_index","consensus_group_count","start_symbol_1based","end_symbol_1based","symbol_count","family_surface","zl_sta_codes","it_sta_codes","rf_sta_codes","left_boundary_profile","right_boundary_profile")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def split_for(folio):
 value=int.from_bytes(hashlib.sha256(f"SNWG001|{folio}".encode()).digest()[:8],"little")%5
 return 'TEST' if value==0 else ('CAL' if value==1 else 'TRAIN')
def numeric_max(left,right):
 if isinstance(left,dict):return math.inf if set(left)!=set(right) else max((numeric_max(left[key],right[key]) for key in left),default=0.)
 if isinstance(left,list):return math.inf if len(left)!=len(right) else max((numeric_max(a,b) for a,b in zip(left,right)),default=0.)
 if isinstance(left,(int,float)) and not isinstance(left,bool):return abs(float(left)-float(right))
 return 0. if left==right else math.inf
def aggregate(result):return {**result,'EXACT_POSITION_MARKOV_PASS':independent.passes(result)}
def eligible_ids(rows):return {row['consensus_group_id'] for row in rows if row['strict_zero_alternative']=='1' and row['grammar_scope']=='CONFIRMED_PROSE' and re.match(r'f\d+',row['page'])}
def join(panel,rows):
 if len(rows)!=26184:raise ValueError('source count')
 by_id={row['consensus_group_id']:row for row in rows}
 if len(by_id)!=len(rows):raise ValueError('duplicate')
 panel_ids={row['unit_id'] for row in panel.rows}
 if eligible_ids(rows)!=panel_ids or len(panel_ids)!=21899:raise ValueError('eligible')
 sequences=[];counts=Counter()
 for masked in panel.rows:
  source=by_id.get(masked['unit_id']);match=re.match(r'f\d+',source['page']) if source else None
  if source is None or match is None or source['strict_zero_alternative']!='1' or source['grammar_scope']!='CONFIRMED_PROSE':raise ValueError('scope')
  surface=source['family_surface']
  if len(surface)!=int(masked['symbol_count']) or int(source['symbol_count'])!=len(surface) or any(symbol not in INDEX for symbol in surface):raise ValueError('surface')
  exact={'locus':source['locus'],'page':source['page'],'physical_folio':match.group(),'section':source['section'],'currier':source['currier'],'hand':source['hand'],'kind':source['kind'],'symbol_count':str(len(surface)),'split':split_for(match.group())}
  if any(masked[key]!=value for key,value in exact.items()):raise ValueError('metadata')
  sequences.append(tuple(INDEX[symbol] for symbol in surface));counts.update(surface)
 return sequences,counts
def rejects(panel,rows,mutation):
 altered=deepcopy(rows);mutation(altered)
 try:join(panel,altered)
 except ValueError:return True
 return False
def expected_report(stored):
 forward=stored['forward'];reverse=stored['reversed'];target=stored['gates']['EXACT_POSITION_MARKOV_TARGET_PASS']
 return f"""# Exact-position-controlled transition target

Status: **{stored['status']}**

The single frozen join matched **{stored['joined_target_sequences']:,}** complete groups and scored
**{forward['test_symbols']:,}** noninitial held transitions. Forward/reversed
transition-minus-exact-position equal-folio gains are
**{forward['gain']['effect_equal_folio']:+.6f}** and
**{reverse['gain']['effect_equal_folio']:+.6f}** nat/transition-symbol, with
**{forward['gain']['positive_folios']}/24** and
**{reverse['gain']['positive_folios']}/24** positive folios. Exact unseen-group
gains are **{forward['unseen']['effect_equal_folio']:+.6f}** and
**{reverse['unseen']['effect_equal_folio']:+.6f}** on
**{forward['unseen']['groups']}** held groups.

`EXACT_POSITION_MARKOV_TARGET_PASS` is **{str(target).lower()}**. Decision:
**{stored['decision']}**. No event-level sequence, transition, or position is stored.
This supplies no syntax, morphology, sound, word, language, meaning, plaintext,
cipher, or translation.
"""
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 failures=[];checks=0
 def check(condition,name):
  nonlocal checks;checks+=1
  if not condition:failures.append(name)
 for path,expected in FROZEN.items():check(sha(path)==expected,f'hash:{path.name}')
 check(json.loads(CAPACITY_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION','capacity');check(json.loads(PREFLIGHT_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_192_WORLD_EXACT_POSITION_MARKOV_RECONSTRUCTION','preflight');check(json.loads(SOURCE_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION','source')
 with TARGET_SOURCE.open(encoding='utf-8',newline='') as handle:
  reader=csv.DictReader(handle,delimiter='\t');check(tuple(reader.fieldnames or ())==SOURCE_FIELDS,'schema');rows=list(reader)
 panel=independent.clean.load_panel();sequences,counts=join(panel,rows);check(len(sequences)==21899,'join')
 forward=aggregate(independent.evaluate(panel,sequences));reverse=aggregate(independent.evaluate(panel,[tuple(reversed(sequence)) for sequence in sequences]));target=forward['EXACT_POSITION_MARKOV_PASS'] and reverse['EXACT_POSITION_MARKOV_PASS']
 gates={'exact_26184_source_rows':len(rows)==26184,'exact_21899_joined_groups':len(sequences)==21899,'exact_5521_scored_test_groups':forward['test_groups']==5521 and reverse['test_groups']==5521,'exact_17435_test_transition_symbols':forward['test_symbols']==17435 and reverse['test_symbols']==17435,'exact_split_counts':Counter(row['split'] for row in panel.rows)=={'TRAIN':10753,'CAL':5516,'TEST':5630},'exact_94_folios':len(set(panel.folios))==94,'complete_eligible_id_set':eligible_ids(rows)=={row['unit_id'] for row in panel.rows},'forward_EXACT_POSITION_MARKOV_PASS':forward['EXACT_POSITION_MARKOV_PASS'],'reversed_EXACT_POSITION_MARKOV_PASS':reverse['EXACT_POSITION_MARKOV_PASS'],'EXACT_POSITION_MARKOV_TARGET_PASS':target}
 status='CONFIRM_EXACT_POSITION_CONTROLLED_FIRST_ORDER_DEPENDENCY' if target else 'NONCONFIRM_EXACT_POSITION_CONTROLLED_FIRST_ORDER_DEPENDENCY';decision='RETAIN_POSITION_INDEPENDENT_LOCAL_TRANSITION_GRAMMAR' if target else 'DOWNGRADE_COARSE_MARKOV_TO_POSITION_CONFOUND';stored=json.loads(TARGET_RESULT.read_text())
 expected_inputs={path.name:sha(path) for path in (PANEL_PATH,CAPACITY_VALIDATION,BASE/"source_native_within_group_exact_position_markov_core.py",BASE/"SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_SPEC.md",RESULTS/"source_native_within_group_exact_position_markov_preflight.json",PREFLIGHT_VALIDATION,SOURCE_VALIDATION,SPEC,TARGET_SOURCE,RUNNER)}
 check(stored['inputs']==expected_inputs,'input bindings');check(stored['status']==status and stored['decision']==decision,'decision');check(numeric_max(stored['forward'],forward)<=1e-12,'forward');check(numeric_max(stored['reversed'],reverse)<=1e-12,'reverse');check(stored['gates']==gates,'gates');check(stored['family_counts']=={symbol:counts[symbol] for symbol in ALPHABET},'counts');check(stored['source_rows_accessed']==26184 and stored['joined_target_sequences']==21899 and stored['scored_test_groups']==5521 and stored['scored_test_transition_symbols']==17435,'access');check(stored['target_source_opened'] is True and stored['target_sequences_accessed']==21899 and stored['target_evaluations_computed']==2,'target');check(stored['event_level_sequences_stored']==0 and stored['event_level_transitions_stored']==0 and stored['event_level_positions_stored']==0 and stored['english_glosses']==0,'ceiling');check(TARGET_REPORT.read_text()==expected_report(stored),'report')
 index=next(i for i,row in enumerate(rows) if row['consensus_group_id']==panel.rows[0]['unit_id']);check(rejects(panel,rows,lambda values:values.pop(index)),'missing');check(rejects(panel,rows,lambda values:values.append(dict(values[index]))),'duplicate');check(rejects(panel,rows,lambda values:values[index].__setitem__('page','f999r')),'metadata');check(rejects(panel,rows,lambda values:values[index].__setitem__('family_surface','I'+values[index]['family_surface'][1:])),'symbol')
 if failures:raise SystemExit('validation failed: '+failures[0])
 result={'experiment':'SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_TARGET_VALIDATION','status':'PASS_PRODUCTION_FREE_EXACT_POSITION_MARKOV_CONFIRMATION_RECONSTRUCTION','checks':checks,'failures':[],'reconstructed_status':status,'reconstructed_decision':decision,'forward_equal_folio_gain':forward['gain']['effect_equal_folio'],'reversed_equal_folio_gain':reverse['gain']['effect_equal_folio'],'unseen_groups':forward['unseen']['groups'],'forward_unseen_gain':forward['unseen']['effect_equal_folio'],'reversed_unseen_gain':reverse['unseen']['effect_equal_folio'],'target_rows_reconstructed':21899,'scored_test_transition_symbols':17435,'event_level_sequences_stored':0,'english_glosses':0,'inputs':{path.name:sha(path) for path in FROZEN},'claim_ceiling':'Production-free confirmation of an exact-position-controlled first-order source-family dependency only; no syntax, morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.'}
 OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Exact-position transition target validation

Status: **{result['status']}**

A production-free implementation rejoins all **21,899** complete groups and
reconstructs both evaluations in **{checks} checks**. Forward/reversed held
gains are **{forward['gain']['effect_equal_folio']:+.6f}** and
**{reverse['gain']['effect_equal_folio']:+.6f}** nat/transition-symbol, with
24/24 positive folios. The **{forward['unseen']['groups']}** exact unseen groups
remain positive at **{forward['unseen']['effect_equal_folio']:+.6f}** and
**{reverse['unseen']['effect_equal_folio']:+.6f}**. Every aggregate, gate,
decision, report byte, binding, and four join mutations matches.

This confirms a first-order structural dependency beyond exact ordinal
position only. It supplies no syntax, morphology, sound, word, language,
meaning, plaintext, cipher, or translation.
""");print(json.dumps({'status':result['status'],'checks':checks},sort_keys=True))
if __name__=='__main__':main()
