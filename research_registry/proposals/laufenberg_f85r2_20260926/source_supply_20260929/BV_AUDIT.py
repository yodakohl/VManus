#!/usr/bin/env python3
"""Replay existing pure transforms on four exposed forms; no fitting or decoding."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
FORMS = ('qotchs', 'qotol', 'qotchy', 'qotain')
INPUTS = (
 'run_gdt012_core_semantic_atlas.py',
 'run_gdt062_right_family_register_renderer.py',
 'experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py',
 'experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv',
 'experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/SURFACE_PREDICTION_CENSUS.tsv',
 'experiments/yolo/gdt751_q_base_carrier_shell_audit/artifacts/Q_BASE_51_PAIR_DECK.tsv',
)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name, path):
 spec = importlib.util.spec_from_file_location(name, ROOT / path)
 mod = importlib.util.module_from_spec(spec)
 spec.loader.exec_module(mod)
 return mod
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'experiments/yolo/gdt605_multisymbol_unit_alphabet/src'))
a = load('bv_old_012', INPUTS[0]); b = load('bv_old_062', INPUTS[1]); c = load('bv_old_605', INPUTS[2])
with (ROOT/INPUTS[3]).open(newline='') as f:
 merges = list(csv.DictReader(f, delimiter='\t'))
assert [int(r['rank']) for r in merges] == list(range(1,65))
rules = [(r['left'],r['right'],r['merged'],int(r['train_occurrences'])) for r in merges]
rows=[]
for form in FORMS:
 wrapper, residual, dy = a.strip_layers(form)
 host, b3, right, inner = b.preparse({'residual_host':residual,'stripped_prefix':wrapper})
 collapsed=c.collapse(form); units=list(c.apply_bpe(collapsed,rules))
 assert ''.join(units)==collapsed
 rows.append(dict(surface=form,wrapper=wrapper,residual_host=residual,dy_closure=dy,
                  page_host_before_local_frame=host,b3=b3,right_family=right,inner_d=inner,
                  local_frame='NOT_FROZEN_FOR_NEW_INPUT',collapsed=collapsed,bpe_units=units))
queries=[]
for path,selector,columns in [
 (INPUTS[5],'prefix_surface','pair_id,prefix_surface,base_surface,prefix_canonical_axes,base_canonical_axes,quality_stage_exactly_preserved,preparation_relation,prefix_reader_exact_occurrences,base_reader_exact_occurrences,confirmed_lexeme,component_export_credit'),
 (INPUTS[4],'target_surface','target_surface,position_evidence_units,pages,minimum_whole_edit_distance,serial_consensus_axes,dimension_conflicts,serial_status,role_decision,automatic_working_default_de,target_axes_before_counts,evidence_loci,confirmed_lexeme,component_export_credit')]:
 cmd=['./vmanus-exp','query-tsv',path,'--selector',selector]
 for form in FORMS: cmd+=['--allow',form]
 cmd+=['--columns',columns]
 res=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
 queries.append(dict(command=cmd,stdout=res.stdout,stderr=res.stderr))
result=dict(schema='bv-existing-grammar-audit-v1',forms=list(FORMS),formal_replays=rows,
 inputs={p:digest(ROOT/p) for p in INPUTS},queries=queries,
 decision='FORMAL_FAMILY_ONLY_NO_COMMON_MEANING_EXPORT_BT_UNSELECTED',
 confirmed_words=0,independent_meaning_confirmation_capacity=0,
 reserves_opened=False,images_opened=False,new_decoder=False)
(BASE/'BV_RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
with (BASE/'BV_FORMAL_TABLE.tsv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader()
 for row in rows:w.writerow({**row,'bpe_units':' | '.join(row['bpe_units'])})
print(json.dumps(rows,indent=2))
