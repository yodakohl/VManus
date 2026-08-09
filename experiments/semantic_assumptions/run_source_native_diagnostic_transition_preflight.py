#!/usr/bin/env python3
"""Run the target-free diagnostic transition-transfer calibration."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import hashlib,json,math,multiprocessing as mp
from pathlib import Path
from source_native_diagnostic_transition_core import evaluate,load_panel,synthetic_sequences

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_diagnostic_transition_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_diagnostic_transition_capacity_validation.json";FAMILY_ATLAS=RESULTS/"source_native_transition_atlas.tsv";FAMILY_VALIDATION=RESULTS/"source_native_transition_atlas_validation.json";CORE=BASE/"source_native_diagnostic_transition_core.py";SPEC=BASE/"SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_PREFLIGHT_SPEC.md";RUNNER=Path(__file__).resolve();TARGET_OUT=RESULTS/"source_native_diagnostic_transition_target.json";TARGET_REPORT=RESULTS/"source_native_diagnostic_transition_target_report.md";OUT=RESULTS/"source_native_diagnostic_transition_preflight.json";REPORT=RESULTS/"source_native_diagnostic_transition_preflight_report.md"
FROZEN={PANEL_PATH:"7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02",CAPACITY_VALIDATION:"0a1257ffd8e1b88a3f94fade1381516c95f2cbdf9eeba3d0dc41a64ca5b23033",FAMILY_ATLAS:"f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",FAMILY_VALIDATION:"209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",CORE:"4494da0ec8969b44c5636c419fb55b3485d4ddad98c3406c6f0cf09a3595a211",SPEC:"1af65aeb3c2c0bccc5c9f3157e2a4587f6cd0deb3948bc3bf24d3fd15955cd25"};TASKS=([('POSITION_ONLY',world) for world in range(64)]+[('GRAPH',100+world) for world in range(8)]+[('ONE_SECTION',200+world) for world in range(8)]+[('ONE_FOLIO',300+world) for world in range(8)]+[('POSITION_CHAIN',400+world) for world in range(8)]);PANEL=None
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def worker(payload):
 mode,world=payload;return {'mode':mode,'world':world,**evaluate(PANEL,synthetic_sequences(PANEL,world,mode),2048,.02)}
def finite(value):
 if isinstance(value,dict):return all(finite(item) for item in value.values())
 if isinstance(value,list):return all(finite(item) for item in value)
 return not isinstance(value,float) or math.isfinite(value)
def main():
 global PANEL
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 if TARGET_OUT.exists() or TARGET_REPORT.exists():raise SystemExit('target exists')
 for path,expected in FROZEN.items():
  if sha(path)!=expected:raise SystemExit(f'frozen mismatch: {path.name}')
 capacity=json.loads(CAPACITY_VALIDATION.read_text());family=json.loads(FAMILY_VALIDATION.read_text())
 if capacity['status']!='PASS_INDEPENDENT_TARGET_MASKED_DIAGNOSTIC_CAPACITY_RECONSTRUCTION' or capacity['target_family_sequences_output']!=0 or family['status']!='PASS_INDEPENDENT_576_PAIR_HELD_FOLIO_RECONSTRUCTION':raise SystemExit('authorization failure')
 PANEL=load_panel(PANEL_PATH)
 with mp.get_context('fork').Pool(32) as pool:records=pool.map(worker,TASKS)
 records.sort(key=lambda row:TASKS.index((row['mode'],row['world'])));counts={mode:{'worlds':sum(candidate==mode for candidate,_ in TASKS),'passes':sum(row['DIAGNOSTIC_TRANSFER_PASS'] for row in records if row['mode']==mode)} for mode in ('POSITION_ONLY','GRAPH','ONE_SECTION','ONE_FOLIO','POSITION_CHAIN')}
 large={}
 for mode,world in (('POSITION_ONLY',0),('GRAPH',100)):large[mode]={'mode':mode,'world':world,**evaluate(PANEL,synthetic_sequences(PANEL,world,mode),8192,.01)}
 reference=synthetic_sequences(PANEL,100,'GRAPH');mutations={}
 for name,altered in (('missing_sequence',reference[:-1]),('length_mismatch',[tuple()]+reference[1:]),('invalid_symbol',[(-1,)+reference[0][1:]]+reference[1:])):
  try:evaluate(PANEL,altered,128,.02)
  except ValueError:mutations[name]=True
  else:mutations[name]=False
 bad_rows=[dict(row) for row in PANEL.rows];bad_rows[0]['unit_id']=bad_rows[1]['unit_id'];bad_panel=type(PANEL)(bad_rows,PANEL.lengths,PANEL.folios,PANEL.folio_index)
 try:evaluate(bad_panel,reference,128,.02)
 except ValueError:mutations['duplicate_unit_id']=True
 else:mutations['duplicate_unit_id']=False
 pattern=counts['POSITION_ONLY']['passes']<=1 and counts['GRAPH']['passes']>=7 and all(counts[mode]['passes']==0 for mode in ('ONE_SECTION','ONE_FOLIO','POSITION_CHAIN'))
 gates={'expected_synthetic_pattern':pattern,'target_size_null_rejects':not large['POSITION_ONLY']['DIAGNOSTIC_TRANSFER_PASS'],'target_size_graph_passes':large['GRAPH']['DIAGNOSTIC_TRANSFER_PASS'],'target_size_decisions_match_calibration':large['POSITION_ONLY']['DIAGNOSTIC_TRANSFER_PASS']==next(row['DIAGNOSTIC_TRANSFER_PASS'] for row in records if row['mode']=='POSITION_ONLY' and row['world']==0) and large['GRAPH']['DIAGNOSTIC_TRANSFER_PASS']==next(row['DIAGNOSTIC_TRANSFER_PASS'] for row in records if row['mode']=='GRAPH' and row['world']==100),'finite_summaries':all(finite(row) for row in records) and finite(large),'mutation_guards':all(mutations.values()),'exact_capacity':len(PANEL.rows)==1382 and len(PANEL.folios)==26 and int(sum(max(0,int(length)-1) for length in PANEL.lengths))==4857,'target_absent':not TARGET_OUT.exists() and not TARGET_REPORT.exists()};passed=all(gates.values());status='PASS_TARGET_FREE_DIAGNOSTIC_TRANSITION_PREFLIGHT' if passed else 'STOP_DIAGNOSTIC_TRANSITION_PREFLIGHT';decision='GO_INDEPENDENTLY_VALIDATE_DIAGNOSTIC_TRANSITION_PREFLIGHT' if passed else 'STOP_BEFORE_DIAGNOSTIC_TRANSITION_TARGET'
 result={'experiment':'SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_PREFLIGHT','status':status,'decision':decision,'inputs':{path.name:sha(path) for path in (*FROZEN,RUNNER)},'workers':32,'calibration_assignments':2048,'target_size_assignments':8192,'records':records,'counts':counts,'target_size_checks':large,'mutations':mutations,'gates':gates,'target_source_opened':False,'target_family_sequences_accessed':0,'target_scores_computed':0,'target_outputs_absent':not TARGET_OUT.exists() and not TARGET_REPORT.exists(),'english_glosses':0,'claim_ceiling':'Target-free calibration of fixed prose-graph transfer into masked diagnostic geometry only; no wordhood, ownership, label meaning, picture identity, sound, language, cipher, plaintext, or translation follows.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Diagnostic transition-transfer preflight

Status: **{status}**

The 2,048-assignment grid yields **{counts['POSITION_ONLY']['passes']}/64**
position-only false passes, **{counts['GRAPH']['passes']}/8** global graph
passes, and **{counts['ONE_SECTION']['passes']}/8** one-section,
**{counts['ONE_FOLIO']['passes']}/8** one-folio, and
**{counts['POSITION_CHAIN']['passes']}/8** position-chain passes. The null and
graph decisions remain unchanged at the target-size 8,192 assignments. All
remaining gates are **{'passing' if passed else 'not all passing'}**.

Zero diagnostic family sequences or target scores were opened. Decision:
**{decision}**. No wordhood, ownership, label meaning, picture identity, sound,
language, cipher, plaintext, or translation follows.
""");print(json.dumps({'status':status,'counts':counts,'gates':gates,'decision':decision},sort_keys=True))
if __name__=='__main__':main()
