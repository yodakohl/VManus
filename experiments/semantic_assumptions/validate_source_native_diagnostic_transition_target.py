#!/usr/bin/env python3
"""Production-free validation of diagnostic transition transfer."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import csv,hashlib,json,math,re
from collections import Counter
from copy import deepcopy
from pathlib import Path
import validate_source_native_diagnostic_transition_preflight as independent

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_diagnostic_transition_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_diagnostic_transition_capacity_validation.json";FAMILY_VALIDATION=RESULTS/"source_native_transition_atlas_validation.json";PREFLIGHT_VALIDATION=RESULTS/"source_native_diagnostic_transition_preflight_validation.json";CLEAN_VALIDATOR=BASE/"validate_source_native_diagnostic_transition_preflight.py";SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json";SPEC=BASE/"SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_TARGET_SPEC.md";RUNNER=BASE/"run_source_native_diagnostic_transition_target.py";TARGET=RESULTS/"source_native_diagnostic_transition_target.json";TARGET_REPORT=RESULTS/"source_native_diagnostic_transition_target_report.md";OUT=RESULTS/"source_native_diagnostic_transition_target_validation.json";REPORT=RESULTS/"source_native_diagnostic_transition_target_validation_report.md"
FROZEN={PANEL_PATH:"7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02",CAPACITY_VALIDATION:"0a1257ffd8e1b88a3f94fade1381516c95f2cbdf9eeba3d0dc41a64ca5b23033",FAMILY_VALIDATION:"209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",PREFLIGHT_VALIDATION:"3fba190832b0147d7ae23b8af54fa3c53d671a526bbf62e2dce09bc5b4c73736",CLEAN_VALIDATOR:"76a5567cc7cb57b12a46afb18ee75b7ebdfc31d3b216ae19025c46c94e39134c",SOURCE:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",SPEC:"ea5faf6bdc627c6a76ac6e0f332f7926c9a67d39b4d9e5201835e8734a0724b7",RUNNER:"77db6561cd899c4ff10123b81851cc955ae38e9a816749f29b4184b4f7629194",TARGET:"f01ca643dda1030b6fb7d43efa04c87a81e111e2c43a38c669f1380a67d34182",TARGET_REPORT:"1fc93678b409dd87c465cb384927a166b0d42a0bbed3519d62a18119df39bef0"};ALPHABET=tuple("ABCDEFGHJKLMNPQRSTUVWXYZ");INDEX={value:index for index,value in enumerate(ALPHABET)};SOURCE_FIELDS=("consensus_group_id","locus","page","section","currier","hand","code","kind","grammar_scope","strict_zero_alternative","consensus_group_index","consensus_group_count","start_symbol_1based","end_symbol_1based","symbol_count","family_surface","zl_sta_codes","it_sta_codes","rf_sta_codes","left_boundary_profile","right_boundary_profile")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def folio(page):
 match=re.fullmatch(r'(f\d+)[rv]\d*',page)
 if match is None:raise ValueError('page')
 return match.group(1)
def eligible(rows):return {row['consensus_group_id'] for row in rows if row['strict_zero_alternative']=='1' and row['grammar_scope']=='DIAGNOSTIC_NONPROSE' and re.fullmatch(r'f\d+[rv]\d*',row['page'])}
def join(panel,rows):
 if len(rows)!=26184:raise ValueError('source rows')
 by_id={row['consensus_group_id']:row for row in rows}
 if len(by_id)!=26184 or eligible(rows)!={row['unit_id'] for row in panel.rows}:raise ValueError('identity')
 sequences=[];counts=Counter()
 for masked in panel.rows:
  row=by_id[masked['unit_id']];surface=row['family_surface']
  if len(surface)!=int(masked['symbol_count']) or int(row['symbol_count'])!=len(surface) or any(value not in INDEX for value in surface):raise ValueError('surface')
  exact={'locus':row['locus'],'page':row['page'],'physical_folio':folio(row['page']),'section':row['section'],'currier':row['currier'],'kind':row['kind'],'symbol_count':str(len(surface))}
  if row['strict_zero_alternative']!='1' or row['grammar_scope']!='DIAGNOSTIC_NONPROSE' or any(masked[key]!=value for key,value in exact.items()):raise ValueError('metadata')
  sequences.append(tuple(INDEX[value] for value in surface));counts.update(surface)
 return sequences,counts
def numeric_max(left,right):
 if isinstance(left,dict):return math.inf if set(left)!=set(right) else max((numeric_max(left[key],right[key]) for key in left),default=0.)
 if isinstance(left,list):return math.inf if len(left)!=len(right) else max((numeric_max(a,b) for a,b in zip(left,right)),default=0.)
 if isinstance(left,(int,float)) and not isinstance(left,bool):return abs(float(left)-float(right))
 return 0. if left==right else math.inf
def rejects(panel,rows,mutation):
 altered=deepcopy(rows);mutation(altered)
 try:join(panel,altered)
 except (ValueError,KeyError):return True
 return False
def expected_report(stored):
 section=stored['evaluation']['SECTION_KIND_LENGTH'];held=stored['evaluation']['FOLIO_KIND_LENGTH'];target=stored['evaluation']['DIAGNOSTIC_TRANSFER_PASS']
 return f"""# Prose-graph transfer to diagnostic groups

Status: **{stored['status']}**

The one-time join matched **1,382** strict diagnostic groups with **4,857**
noninitial positions on **26** folios. Under `SECTION_KIND_LENGTH`, favored
edges are **{section['observed_favored']}** versus null mean
**{section['null_mean_favored']:.3f}** (p=**{section['favored_upper_p']:.6f}**)
and disfavored edges are **{section['observed_disfavored']}** versus
**{section['null_mean_disfavored']:.3f}** (p=**{section['disfavored_lower_p']:.6f}**).
Under `FOLIO_KIND_LENGTH`, the corresponding counts/means are
**{held['observed_favored']} / {held['null_mean_favored']:.3f}** and
**{held['observed_disfavored']} / {held['null_mean_disfavored']:.3f}**, with
p=**{held['favored_upper_p']:.6f} / {held['disfavored_lower_p']:.6f}**.

`DIAGNOSTIC_TRANSFER_PASS` is **{str(target).lower()}**. Decision:
**{stored['decision']}**. No event sequence, pair, position, member code, or English
gloss is stored. This supplies no wordhood, ownership, label meaning, picture
identity, sound, language, cipher, plaintext, or translation.
"""
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 failures=[];checks=0
 def check(condition,name):
  nonlocal checks;checks+=1
  if not condition:failures.append(name)
 for path,expected in FROZEN.items():check(sha(path)==expected,f'hash:{path.name}')
 check(json.loads(CAPACITY_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_TARGET_MASKED_DIAGNOSTIC_CAPACITY_RECONSTRUCTION','capacity');check(json.loads(FAMILY_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_576_PAIR_HELD_FOLIO_RECONSTRUCTION','atlas');check(json.loads(PREFLIGHT_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_96_WORLD_DUAL_ENSEMBLE_RECONSTRUCTION','preflight');check(json.loads(SOURCE_VALIDATION.read_text())['status']=='PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION','source')
 with SOURCE.open(encoding='utf-8',newline='') as handle:reader=csv.DictReader(handle,delimiter='\t');check(tuple(reader.fieldnames or ())==SOURCE_FIELDS,'schema');rows=list(reader)
 panel=independent.load_panel();sequences,counts=join(panel,rows);evaluation=independent.evaluate(panel,sequences,8192,.01);target=evaluation['DIAGNOSTIC_TRANSFER_PASS'];gates={'exact_26184_source_rows':len(rows)==26184,'exact_1382_joined_groups':len(sequences)==1382,'exact_4857_noninitial_positions':sum(max(0,len(sequence)-1) for sequence in sequences)==4857,'exact_26_folios':len(panel.folios)==26,'complete_eligible_id_set':eligible(rows)=={row['unit_id'] for row in panel.rows},'SECTION_KIND_LENGTH_TRANSFER_PASS':evaluation['SECTION_KIND_LENGTH']['TRANSFER_PASS'],'FOLIO_KIND_LENGTH_TRANSFER_PASS':evaluation['FOLIO_KIND_LENGTH']['TRANSFER_PASS'],'DIAGNOSTIC_TRANSFER_PASS':target};status='CONFIRM_PROSE_GRAPH_TRANSFER_TO_DIAGNOSTIC_TEXT' if target else 'NONCONFIRM_PROSE_GRAPH_TRANSFER_TO_DIAGNOSTIC_TEXT';decision='RETAIN_SHARED_PROSE_DIAGNOSTIC_FAMILY_GRAMMAR' if target else 'RETAIN_PROSE_LOCAL_TRANSITION_GRAMMAR_ONLY';stored=json.loads(TARGET.read_text());check(stored['status']==status and stored['decision']==decision,'decision');check(numeric_max(stored['evaluation'],evaluation)==0,'evaluation');check(stored['gates']==gates,'gates');check(stored['family_counts']=={value:counts[value] for value in ALPHABET},'counts');check(stored['source_rows_accessed']==26184 and stored['joined_target_sequences']==1382 and stored['noninitial_positions']==4857 and stored['physical_folios']==26,'access');check(stored['target_source_opened'] is True and stored['target_family_sequences_accessed']==1382 and stored['target_evaluations_computed']==1 and stored['member_codes_accessed']==0,'target');check(stored['event_level_sequences_stored']==0 and stored['event_level_pairs_stored']==0 and stored['event_level_positions_stored']==0 and stored['english_glosses']==0,'ceiling');check(TARGET_REPORT.read_text()==expected_report(stored),'report')
 index=next(i for i,row in enumerate(rows) if row['consensus_group_id']==panel.rows[0]['unit_id']);check(rejects(panel,rows,lambda values:values.pop(index)),'missing');check(rejects(panel,rows,lambda values:values.append(dict(values[index]))),'duplicate');check(rejects(panel,rows,lambda values:values[index].__setitem__('page','f999r')),'metadata');check(rejects(panel,rows,lambda values:values[index].__setitem__('family_surface','I'+values[index]['family_surface'][1:])),'symbol')
 if failures:raise SystemExit('validation failed: '+failures[0])
 failed=[name for name,value in gates.items() if not value];result={'experiment':'SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_TARGET_VALIDATION','status':'PASS_PRODUCTION_FREE_DIAGNOSTIC_NONCONFIRMATION_RECONSTRUCTION','checks':checks,'failures':[],'reconstructed_status':status,'reconstructed_decision':decision,'failed_gates':failed,'section_favored_p':evaluation['SECTION_KIND_LENGTH']['favored_upper_p'],'section_disfavored_p':evaluation['SECTION_KIND_LENGTH']['disfavored_lower_p'],'folio_favored_p':evaluation['FOLIO_KIND_LENGTH']['favored_upper_p'],'folio_disfavored_p':evaluation['FOLIO_KIND_LENGTH']['disfavored_lower_p'],'target_rows_reconstructed':1382,'event_level_sequences_stored':0,'english_glosses':0,'inputs':{path.name:sha(path) for path in FROZEN},'claim_ceiling':'Production-free reconstruction of the frozen diagnostic transfer nonconfirmation only; no wordhood, ownership, label meaning, sound, language, cipher, plaintext, or translation follows.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Diagnostic transition target validation

Status: **{result['status']}**

A production-free implementation rejoins all **1,382** diagnostic groups and
reconstructs both 8,192-assignment ensembles, every orbit digest, score, gate,
decision, report byte, binding, and four mutations in **{checks}** checks. Both
favored and disfavored tails reach p=1/8192 in both nulls, but favored folio
concentration is **{evaluation['SECTION_KIND_LENGTH']['favored_max_abs_contribution_fraction']:.6f}**
and **{evaluation['FOLIO_KIND_LENGTH']['favored_max_abs_contribution_fraction']:.6f}**,
above the frozen .25 cap, so the registered result remains a nonconfirmation.

This supplies no wordhood, ownership, label meaning, picture identity, sound,
language, cipher, plaintext, or translation.
""");print(json.dumps({'status':result['status'],'checks':checks,'failed_gates':failed},sort_keys=True))
if __name__=='__main__':main()
