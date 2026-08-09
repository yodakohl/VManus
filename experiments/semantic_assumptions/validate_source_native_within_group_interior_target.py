#!/usr/bin/env python3
"""Production-free validation of the endpoint-free interior target."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"

import csv,hashlib,json,math,re
from collections import Counter
from copy import deepcopy
from pathlib import Path
import validate_source_native_within_group_interior_preflight as clean


BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results"
PANEL_PATH=RESULTS/"source_native_within_group_interior_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_within_group_interior_capacity_validation.json"
PREFLIGHT_VALIDATION=RESULTS/"source_native_within_group_interior_preflight_validation.json";CLEAN_VALIDATOR=BASE/"validate_source_native_within_group_interior_preflight.py"
TARGET_SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json"
SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_TARGET_SPEC.md";RUNNER=BASE/"run_source_native_within_group_interior_target.py"
TARGET_RESULT=RESULTS/"source_native_within_group_interior_target.json";TARGET_REPORT=RESULTS/"source_native_within_group_interior_target_report.md"
OUT=RESULTS/"source_native_within_group_interior_target_validation.json";REPORT=RESULTS/"source_native_within_group_interior_target_validation_report.md"
FROZEN={
 PANEL_PATH:"0b6202641045ed11fd1ae4870353b4bec17adcc658c9687fd766f35bfbfe51ad",CAPACITY_VALIDATION:"1513617bafcc3c4143af7be129251cf9dd7e7aa5cfa429c414c55eaa8fe923f8",
 PREFLIGHT_VALIDATION:"654aeca00226b198e1f198b922aa999251e1fe5886f44ceb4205a445c9050a9f",CLEAN_VALIDATOR:"4fa4c3e6a935f1e8ab86144eb096e5126bb64e3fc6665e4db92422866fa8597f",
 TARGET_SOURCE:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
 SPEC:"fa665d4659aa3aab776da34b970bf2aa03b5bd1d0368c11fc86e5ccc8acde670",RUNNER:"294f0bdd8ed7323ce2770ad1c7008a053448eba519bf5b79b55414c8c8304be0",
 TARGET_RESULT:"330d40c9fbfc7337c8afdc9d305e3e3767a8be117d87e3cc6e727c889a90efab",TARGET_REPORT:"d4474628606df2679a23f228f543380b7ae0930166fcf4ccf68b7c7d0705633d",
}
ALPHABET=tuple("ABCDEFGHJKLMNPQRSTUVWXYZ");INDEX={value:index for index,value in enumerate(ALPHABET)}
SOURCE_FIELDS=("consensus_group_id","locus","page","section","currier","hand","code","kind","grammar_scope","strict_zero_alternative","consensus_group_index","consensus_group_count","start_symbol_1based","end_symbol_1based","symbol_count","family_surface","zl_sta_codes","it_sta_codes","rf_sta_codes","left_boundary_profile","right_boundary_profile")


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def split_for(folio):
 value=int.from_bytes(hashlib.sha256(f"SNWG001|{folio}".encode()).digest()[:8],"little")%5
 return "TEST" if value==0 else ("CAL" if value==1 else "TRAIN")
def numeric_max(a,b):
 if isinstance(a,dict):return math.inf if set(a)!=set(b) else max((numeric_max(a[k],b[k]) for k in a),default=0.)
 if isinstance(a,list):return math.inf if len(a)!=len(b) else max((numeric_max(x,y) for x,y in zip(a,b)),default=0.)
 if isinstance(a,(int,float)) and not isinstance(a,bool):return abs(float(a)-float(b))
 return 0. if a==b else math.inf
def aggregate(result):return {**result,"INTERIOR_POSITION_PASS":clean.passes(result)}


def eligible_ids(rows):
 return {r['consensus_group_id'] for r in rows if r['strict_zero_alternative']=='1' and r['grammar_scope']=='CONFIRMED_PROSE' and re.match(r'f\d+',r['page']) and int(r['symbol_count'])>=3}
def join(panel,rows):
 if len(rows)!=26184:raise ValueError("source count")
 by={r['consensus_group_id']:r for r in rows}
 if len(by)!=len(rows):raise ValueError("duplicate source")
 panel_ids={r['unit_id'] for r in panel.rows}
 if eligible_ids(rows)!=panel_ids or len(panel_ids)!=19203:raise ValueError("eligible set")
 sequences=[];counts=Counter()
 for masked in panel.rows:
  source=by.get(masked['unit_id']);match=re.match(r'f\d+',source['page']) if source else None
  if source is None or match is None or source['strict_zero_alternative']!='1' or source['grammar_scope']!='CONFIRMED_PROSE':raise ValueError("scope")
  surface=source['family_surface'];interior=surface[1:-1]
  if len(surface)!=int(masked['original_symbol_count']) or len(interior)!=int(masked['interior_symbol_count']) or int(source['symbol_count'])!=len(surface):raise ValueError("length")
  if not interior or any(x not in INDEX for x in interior):raise ValueError("symbol")
  exact={'locus':source['locus'],'page':source['page'],'physical_folio':match.group(),'section':source['section'],'currier':source['currier'],'hand':source['hand'],'kind':source['kind'],'original_symbol_count':str(len(surface)),'interior_symbol_count':str(len(interior)),'split':split_for(match.group())}
  if any(masked[k]!=v for k,v in exact.items()):raise ValueError("metadata")
  sequences.append(tuple(INDEX[x] for x in interior));counts.update(interior)
 return sequences,counts
def expected_report(stored):
 f=stored['forward'];r=stored['reversed'];target=stored['gates']['INTERIOR_POSITION_TARGET_PASS']
 return f"""# Endpoint-free source-group interior-position target

Status: **{stored['status']}**

The single frozen join matched **{stored['joined_target_sequences']:,}** groups and removed every
first and last family before fitting. Forward/reversed CAL selection chooses
**{f['selected_model']}** and **{r['selected_model']}**.
Held equal-folio gains are **{f['gain']['effect_equal_folio']:+.6f}** and
**{r['gain']['effect_equal_folio']:+.6f}** nat/interior-symbol,
with **{f['gain']['positive_folios']}/24** and
**{r['gain']['positive_folios']}/24** positive folios.

`INTERIOR_POSITION_TARGET_PASS` is **{str(target).lower()}**. Decision:
**{stored['decision']}**. No endpoint value or event-level interior sequence is stored.
This test supplies no prefix, root, suffix, sound, word, part of speech,
language, cipher operation, meaning, plaintext, or translation.
"""
def rejects(panel,rows,mutation):
 altered=deepcopy(rows);mutation(altered)
 try:join(panel,altered)
 except ValueError:return True
 return False


def main():
 if OUT.exists() or REPORT.exists():raise SystemExit("refusing overwrite")
 failures=[];checks=0
 def check(ok,name):
  nonlocal checks;checks+=1
  if not ok:failures.append(name)
 for path,expected in FROZEN.items():check(sha(path)==expected,f"hash:{path.name}")
 check(json.loads(CAPACITY_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_SCORE_BLIND_INTERIOR_CAPACITY_RECONSTRUCTION','capacity status');check(json.loads(PREFLIGHT_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_192_WORLD_INTERIOR_PREFLIGHT_RECONSTRUCTION','preflight status');check(json.loads(SOURCE_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION','source status')
 with TARGET_SOURCE.open(encoding='utf-8',newline='') as handle:
  reader=csv.DictReader(handle,delimiter='\t');check(tuple(reader.fieldnames or ())==SOURCE_FIELDS,'source schema');rows=list(reader)
 panel=clean.load_panel();sequences,counts=join(panel,rows);check(len(sequences)==19203 and sum(map(len,sequences))==45867,'join capacity')
 forward=aggregate(clean.evaluate(panel,sequences));reverse=aggregate(clean.evaluate(panel,[tuple(reversed(s)) for s in sequences]));target=forward['INTERIOR_POSITION_PASS'] and reverse['INTERIOR_POSITION_PASS']
 gates={'exact_26184_source_rows':len(rows)==26184,'exact_19203_joined_groups':len(sequences)==19203,'exact_45867_interior_symbols':sum(map(len,sequences))==45867,'exact_split_counts':Counter(r['split'] for r in panel.rows)=={'TRAIN':9364,'CAL':4887,'TEST':4952},'exact_94_folios':len(set(panel.folios))==94,'complete_eligible_id_set':eligible_ids(rows)=={r['unit_id'] for r in panel.rows},'forward_INTERIOR_POSITION_PASS':forward['INTERIOR_POSITION_PASS'],'reversed_INTERIOR_POSITION_PASS':reverse['INTERIOR_POSITION_PASS'],'INTERIOR_POSITION_TARGET_PASS':target}
 status='CONFIRM_ENDPOINT_FREE_WITHIN_GROUP_INTERIOR_POSITION_STRUCTURE' if target else 'NONCONFIRM_ENDPOINT_FREE_WITHIN_GROUP_INTERIOR_POSITION_STRUCTURE';decision='RETAIN_INTERIOR_POSITION_STRUCTURE_BEYOND_ENDPOINTS_AND_LENGTH' if target else 'DOWNGRADE_COMPLETE_GROUP_POSITION_RESULT_TO_ENDPOINT_DOMINATED'
 stored=json.loads(TARGET_RESULT.read_text());check(stored['status']==status and stored['decision']==decision,'decision');check(numeric_max(stored['forward'],forward)<=1e-12,'forward');check(numeric_max(stored['reversed'],reverse)<=1e-12,'reverse');check(stored['gates']==gates,'gates');check(stored['interior_family_counts']=={x:counts[x] for x in ALPHABET},'counts');check(stored['source_rows_accessed']==26184 and stored['joined_target_sequences']==19203 and stored['interior_symbols']==45867,'access');check(stored['target_source_opened'] is True and stored['target_sequences_accessed']==19203 and stored['target_evaluations_computed']==2,'target access');check(stored['endpoint_values_stored']==0 and stored['event_level_sequences_stored']==0 and stored['english_glosses']==0,'ceiling');check(TARGET_REPORT.read_text()==expected_report(stored),'report')
 idx=next(i for i,r in enumerate(rows) if r['consensus_group_id']==panel.rows[0]['unit_id']);check(rejects(panel,rows,lambda x:x.pop(idx)),'missing mutation');check(rejects(panel,rows,lambda x:x.append(dict(x[idx]))),'duplicate mutation');check(rejects(panel,rows,lambda x:x[idx].__setitem__('page','f999r')),'metadata mutation');check(rejects(panel,rows,lambda x:x[idx].__setitem__('family_surface',x[idx]['family_surface'][0]+'I'+x[idx]['family_surface'][2:])),'symbol mutation')
 if failures:raise SystemExit('validation failed: '+failures[0])
 result={'experiment':'SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_TARGET_VALIDATION','status':'PASS_PRODUCTION_FREE_ENDPOINT_FREE_INTERIOR_NONCONFIRM_RECONSTRUCTION','checks':checks,'failures':[],'reconstructed_status':status,'reconstructed_decision':decision,'selected_models':{'forward':forward['selected_model'],'reversed':reverse['selected_model']},'forward_equal_folio_gain':forward['gain']['effect_equal_folio'],'reversed_equal_folio_gain':reverse['gain']['effect_equal_folio'],'forward_unseen_groups':forward['unseen']['groups'],'reversed_unseen_groups':reverse['unseen']['groups'],'forward_unseen_gain':forward['unseen']['effect_equal_folio'],'reversed_unseen_gain':reverse['unseen']['effect_equal_folio'],'target_rows_reconstructed':19203,'endpoint_values_stored':0,'event_level_sequences_stored':0,'english_glosses':0,'inputs':{p.name:sha(p) for p in FROZEN},'claim_ceiling':'Production-free reconstruction of the endpoint-free nonconfirmation only; no morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.'}
 OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Endpoint-free interior target validation

Status: **{result['status']}**

A production-free implementation rejoins all **19,203** groups after deleting
both endpoints and reconstructs both target evaluations in **{checks} checks**.
Both directions select **FIXED_5** and have positive aggregate held gains, but
only **{forward['unseen']['groups']}** exact unseen interiors survive and their
equal-folio effects are **{forward['unseen']['effect_equal_folio']:+.6f}** and
**{reverse['unseen']['effect_equal_folio']:+.6f}**. Every aggregate, gate,
decision, report byte, binding, and four mutation guards match.

This locks the frozen nonconfirmation and supplies no morphology, sound, word,
language, meaning, plaintext, cipher, or translation.
""");print(json.dumps({'status':result['status'],'checks':checks,'unseen':forward['unseen']['groups']},sort_keys=True))


if __name__=='__main__':main()
