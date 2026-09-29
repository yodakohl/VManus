#!/usr/bin/env python3
"""Full-position and manual-obligation accounting only, not a grammar oracle."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
PARENT=ROOT/'experiments/yolo/gdt1029_galen_paired_endpoint_and_reference'


def main():
    paths=[BASE/'GALEN_SCOPE_ALL_POSITIONS.tsv',BASE/'GALEN_SCOPE_OPERATIONS.tsv',
           BASE/'GALEN_SCOPE_POLICY_20260929.md',BASE/'GALEN_SCOPE_DERIVATION_DECISION_20260929.md',
           PARENT/'src/SOURCE.json',PARENT/'artifacts/ALL_POSITIONS.tsv',PARENT/'REPORT.md',
           ROOT/'experiments/yolo/gdt1028_galen_whole_preparation_and_desire/src/SOURCE.json']
    # Opaque exact comparison proves the guarded output retained the entire
    # already-admitted parent table. Only that scoped output is parsed below.
    assert (BASE/'GALEN_SCOPE_ALL_POSITIONS.tsv').read_bytes()==(PARENT/'artifacts/ALL_POSITIONS.tsv').read_bytes()
    rows=list(csv.DictReader((BASE/'GALEN_SCOPE_ALL_POSITIONS.tsv').open(),delimiter='\t'))
    assert len(rows)==95 and [int(r['position']) for r in rows]==list(range(1,96))
    assert len({r['word'] for r in rows})==67
    assert {r['locus'] for r in rows}=={f'f107v.{n}' for n in range(45,50)}|{f'f111r.{n}' for n in range(44,48)}
    assert all(not r['locus'].startswith(('f84','f116v')) for r in rows)
    assert all(r['confirmed']=='0' for r in rows)
    operations=list(csv.DictReader((BASE/'GALEN_SCOPE_OPERATIONS.tsv').open(),delimiter='\t'))
    expected=[r for r in rows if r['value'] in ('BOIL','THOROUGH_REBOIL')]
    assert len(expected)==len(operations)==8
    for r,v in zip(expected,operations):
        assert all(r[k]==v[k] for k in ['unit','local_position','word','value'])
        assert v['unresolved_obligation'] and v['independent_capacity']=='0'
    governors={'CALLED','FOR','BECAUSE','AS_JUST_SAID','HOWEVER_LONG','LONGER','REMEMBER_ABOVE_ALL'}
    selected=[r for r in rows if r['value'] in governors]
    annotations={
      ('II','21'):'EVACUATION purpose local; complete prohibition under degree-slot assumption',
      ('II','28'):'Reason relation requested; prior prohibition/polarity binding not derived',
      ('II','29'):'THIS_USE retains parent E reference; no new derivation of anaphora',
      ('II','42'):'Duration comparison requests BOIL; full loss/comparison construction open',
      ('II','46'):'EVACUATION reference present; general versus purpose-limited comparison unresolved',
      ('III','19'):'Local naming run21/22 derived conditionally; inherited food/method references',
      ('III','25'):'Purpose request present; interrupted memory/contact construction unresolved',
      ('III','26'):'Norm versus intervening softness proposition scope not selected',
      ('III','38'):'Local hypothetical operation mode; full conditional predicate scope open',
      ('III','40'):'Old transfer-plan reprise and origin/owner bindings not derived'
    }
    assert {(r['unit'],r['local_position']) for r in selected}==set(annotations)
    cols=['unit','local_position','source_id','word','value','derivation_and_gap']
    with (BASE/'GALEN_SCOPE_GOVERNORS.tsv').open('w') as f:
        writer=csv.DictWriter(f,cols,delimiter='\t',lineterminator='\n');writer.writeheader()
        for r in selected:
            writer.writerow({**{k:r[k] for k in cols[:-1]},'derivation_and_gap':annotations[r['unit'],r['local_position']]})
    report={'status':'PASS_ACCOUNTING_ONLY','positions':95,'unchanged_types':67,
            'operation_mentions':8,'governor_mentions':len(selected),
            'parent_table_byte_exact':True,'grammar_truth_or_uniqueness_validated':False,
            'complete_new_derivations':0,'confirmed_words':0,'independent_confirmation_capacity':0,
            'bindings':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (BASE/'GALEN_SCOPE_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='bindings'}))


if __name__=='__main__':
    main()
