#!/usr/bin/env python3
"""Separate narrow input/table/state checks, never meaning validation."""
import csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
s=json.loads((E/'src/SPEC.json').read_text());d={}
for k,b in s['inputs'].items():
 raw=(ROOT/b['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==b['sha256'];d[k]=json.loads(raw)
a=d['author'];t=d['target'];r=json.loads((E/'artifacts/RESULT.json').read_text());trace=json.loads((E/'artifacts/ENTRY_TRACE.json').read_text())
with (E/'artifacts/ALL_POSITIONS.tsv').open() as f: rows=list(csv.DictReader(f,delimiter='\t'))
assert len(rows)==len(a['positions'])==129
rawrows=[(c['context'],x) for c in t['contexts'] for x in c['groups']]
for x,y,(ctx,z) in zip(rows,a['positions'],rawrows):
 assert x['raw_id']==y['raw_id']==z['source_group_id'] and x['raw_surface']==y['raw_surface']==z['ivtff_group_raw']
 assert json.loads(x['segmentation'])==y['segmentation'] and ''.join(y['segmentation'])==y['raw_surface']
 assert x['status']==y['status'];assert json.loads(x['computed_or_UNBOUND_patient'])==y['computed_or_UNBOUND_patient']
assert len(trace)==22
for ctx,n,mat in [('f85r1.1-6',3,'M1'),('f80v.30-37',8,'M2')]:
 for policy in ['TOPIC','CURRENT']:
  seq=[x for x in trace if x['context']==ctx and x['policy']==policy];assert len(seq)==n
  expected=mat if ctx.startswith('f85') or policy=='TOPIC' else 'P5';assert seq[-1]['operand']==expected
  assert seq[0]['state']['topic']==seq[0]['state']['current']==mat
  if ctx.startswith('f85'):assert seq[1]['state']['owner']=='C1'
  else:
   assert seq[4]['state']['entities']['P5']['parent']=='M2' and seq[4]['state']['current']=='P5'
   assert seq[4]['state']['topic']=='M2'
  for x in seq:assert x['operand'] in x['state']['entities'] and x['state']['entities'][x['operand']]['sort']=='Material'
assert r['early_worked_groups']==11 and r['remaining_unbound_groups']==118 and r['whole_complete_contexts']==0
for late in r['late_conditional']:
 assert late['actual_manuscript_state_bound'] is False
 if late['policy']=='TOPIC':assert [x['parent'] for x in late['parts']]==['X','X'] and late['bare_kain_patient_by_D3']=='X' and late['sequential_trace_mismatch'] is True
 else:assert [x['parent'] for x in late['parts']]==['X','A'] and late['bare_kain_patient_by_D3']=='B' and late['sequential_trace_mismatch'] is False
v=dict(status='PASS',scope='Bound four inputs,129 raw/table rows,22 declared early state projections and two conditional late consequences',generic_grammar_derivation=False,manuscript_meaning=False,confirmed_words=0)
(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
