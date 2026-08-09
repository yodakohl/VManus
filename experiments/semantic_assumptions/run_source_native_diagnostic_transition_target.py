#!/usr/bin/env python3
"""Execute the one-time prose-graph transfer to diagnostic source groups."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import csv,hashlib,json,re,tempfile
from collections import Counter
from pathlib import Path
from source_native_diagnostic_transition_core import ALPHABET,INDEX,evaluate,load_panel

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_diagnostic_transition_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_diagnostic_transition_capacity_validation.json";FAMILY_ATLAS=RESULTS/"source_native_transition_atlas.tsv";FAMILY_VALIDATION=RESULTS/"source_native_transition_atlas_validation.json";CORE=BASE/"source_native_diagnostic_transition_core.py";PREFLIGHT_SPEC=BASE/"SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_PREFLIGHT_SPEC.md";PREFLIGHT=RESULTS/"source_native_diagnostic_transition_preflight.json";PREFLIGHT_VALIDATION=RESULTS/"source_native_diagnostic_transition_preflight_validation.json";SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json";SPEC=BASE/"SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_TARGET_SPEC.md";RUNNER=Path(__file__).resolve();OUT=RESULTS/"source_native_diagnostic_transition_target.json";REPORT=RESULTS/"source_native_diagnostic_transition_target_report.md"
SAFE_FROZEN={PANEL_PATH:"7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02",CAPACITY_VALIDATION:"0a1257ffd8e1b88a3f94fade1381516c95f2cbdf9eeba3d0dc41a64ca5b23033",FAMILY_ATLAS:"f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",FAMILY_VALIDATION:"209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",CORE:"4494da0ec8969b44c5636c419fb55b3485d4ddad98c3406c6f0cf09a3595a211",PREFLIGHT_SPEC:"1af65aeb3c2c0bccc5c9f3157e2a4587f6cd0deb3948bc3bf24d3fd15955cd25",PREFLIGHT:"5cc253813a24f3f87eca44d4c71a8f5b0d09bfc4690876b7fda6717cf28add97",PREFLIGHT_VALIDATION:"3fba190832b0147d7ae23b8af54fa3c53d671a526bbf62e2dce09bc5b4c73736",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",SPEC:"ea5faf6bdc627c6a76ac6e0f332f7926c9a67d39b4d9e5201835e8734a0724b7"};SOURCE_HASH="a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225";SOURCE_FIELDS=("consensus_group_id","locus","page","section","currier","hand","code","kind","grammar_scope","strict_zero_alternative","consensus_group_index","consensus_group_count","start_symbol_1based","end_symbol_1based","symbol_count","family_surface","zl_sta_codes","it_sta_codes","rf_sta_codes","left_boundary_profile","right_boundary_profile")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def folio(page):
 match=re.fullmatch(r'(f\d+)[rv]\d*',page)
 if match is None:raise ValueError('page')
 return match.group(1)
def install_pair(result_bytes,report_bytes):
 if OUT.exists() or REPORT.exists():raise FileExistsError('target exists')
 with tempfile.TemporaryDirectory(prefix='source_native_diagnostic_transition_',dir=RESULTS) as directory:
  staged_result=Path(directory)/'result.json';staged_report=Path(directory)/'report.md';staged_result.write_bytes(result_bytes);staged_report.write_bytes(report_bytes)
  if OUT.exists() or REPORT.exists():raise FileExistsError('target appeared')
  os.link(staged_result,OUT)
  try:os.link(staged_report,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing second diagnostic target')
 for path,expected in SAFE_FROZEN.items():
  if sha(path)!=expected:raise SystemExit(f'frozen target mismatch: {path.name}')
 if sha(SOURCE)!=SOURCE_HASH:raise SystemExit('source mismatch')
 if json.loads(CAPACITY_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_TARGET_MASKED_DIAGNOSTIC_CAPACITY_RECONSTRUCTION' or json.loads(FAMILY_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_576_PAIR_HELD_FOLIO_RECONSTRUCTION' or json.loads(SOURCE_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION':raise SystemExit('source authorization failure')
 preflight=json.loads(PREFLIGHT.read_text());validation=json.loads(PREFLIGHT_VALIDATION.read_text())
 if preflight['status']!='PASS_TARGET_FREE_DIAGNOSTIC_TRANSITION_PREFLIGHT' or not all(preflight['gates'].values()) or validation['status']!='PASS_INDEPENDENT_96_WORLD_DUAL_ENSEMBLE_RECONSTRUCTION' or not validation['target_outputs_absent']:raise SystemExit('preflight authorization failure')
 with SOURCE.open(encoding='utf-8',newline='') as handle:
  reader=csv.DictReader(handle,delimiter='\t')
  if tuple(reader.fieldnames or ())!=SOURCE_FIELDS:raise ValueError('schema')
  rows=list(reader)
 if len(rows)!=26184:raise ValueError('source rows')
 by_id={row['consensus_group_id']:row for row in rows}
 if len(by_id)!=26184:raise ValueError('duplicate source')
 panel=load_panel(PANEL_PATH);panel_ids={row['unit_id'] for row in panel.rows};eligible={row['consensus_group_id'] for row in rows if row['strict_zero_alternative']=='1' and row['grammar_scope']=='DIAGNOSTIC_NONPROSE' and re.fullmatch(r'f\d+[rv]\d*',row['page'])}
 if eligible!=panel_ids or len(eligible)!=1382:raise ValueError('eligible set')
 sequences=[];family_counts=Counter()
 for masked in panel.rows:
  source=by_id[masked['unit_id']];surface=source['family_surface']
  if len(surface)!=int(masked['symbol_count']) or int(source['symbol_count'])!=len(surface) or any(value not in INDEX for value in surface):raise ValueError('surface')
  exact={'locus':source['locus'],'page':source['page'],'physical_folio':folio(source['page']),'section':source['section'],'currier':source['currier'],'kind':source['kind'],'symbol_count':str(len(surface))}
  if source['strict_zero_alternative']!='1' or source['grammar_scope']!='DIAGNOSTIC_NONPROSE' or any(masked[key]!=value for key,value in exact.items()):raise ValueError('metadata')
  sequences.append(tuple(INDEX[value] for value in surface));family_counts.update(surface)
 evaluation=evaluate(panel,sequences,8192,.01);target=evaluation['DIAGNOSTIC_TRANSFER_PASS'];gates={'exact_26184_source_rows':len(rows)==26184,'exact_1382_joined_groups':len(sequences)==1382,'exact_4857_noninitial_positions':int(sum(max(0,len(sequence)-1) for sequence in sequences))==4857,'exact_26_folios':len(panel.folios)==26,'complete_eligible_id_set':eligible==panel_ids,'SECTION_KIND_LENGTH_TRANSFER_PASS':evaluation['SECTION_KIND_LENGTH']['TRANSFER_PASS'],'FOLIO_KIND_LENGTH_TRANSFER_PASS':evaluation['FOLIO_KIND_LENGTH']['TRANSFER_PASS'],'DIAGNOSTIC_TRANSFER_PASS':target}
 if target:status='CONFIRM_PROSE_GRAPH_TRANSFER_TO_DIAGNOSTIC_TEXT';decision='RETAIN_SHARED_PROSE_DIAGNOSTIC_FAMILY_GRAMMAR'
 else:status='NONCONFIRM_PROSE_GRAPH_TRANSFER_TO_DIAGNOSTIC_TEXT';decision='RETAIN_PROSE_LOCAL_TRANSITION_GRAMMAR_ONLY'
 result={'experiment':'SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_TARGET','status':status,'decision':decision,'inputs':{path.name:sha(path) for path in (*SAFE_FROZEN,SOURCE,RUNNER)},'source_rows_accessed':len(rows),'joined_target_sequences':len(sequences),'noninitial_positions':4857,'physical_folios':len(panel.folios),'family_counts':{value:family_counts[value] for value in ALPHABET},'evaluation':evaluation,'gates':gates,'target_source_opened':True,'target_family_sequences_accessed':len(sequences),'target_evaluations_computed':1,'event_level_sequences_stored':0,'event_level_pairs_stored':0,'event_level_positions_stored':0,'member_codes_accessed':0,'english_glosses':0,'claim_ceiling':'A pass establishes only transfer of fixed prose-derived physical family adjacency constraints into strict diagnostic text beyond exact-position marginals. It supplies no wordhood, ownership, label meaning, picture identity, sound, language, cipher, plaintext, or translation.'}
 section=evaluation['SECTION_KIND_LENGTH'];held=evaluation['FOLIO_KIND_LENGTH'];report=f"""# Prose-graph transfer to diagnostic groups

Status: **{status}**

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
**{decision}**. No event sequence, pair, position, member code, or English
gloss is stored. This supplies no wordhood, ownership, label meaning, picture
identity, sound, language, cipher, plaintext, or translation.
""";install_pair((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),report.encode());print(json.dumps({'status':status,'gates':gates,'decision':decision,'evaluation':evaluation},sort_keys=True))
if __name__=='__main__':main()
