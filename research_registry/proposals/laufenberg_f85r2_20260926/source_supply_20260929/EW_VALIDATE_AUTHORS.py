#!/usr/bin/env python3
"""Reproduce author accounting and the observed failures, not word meanings."""
import argparse
import csv
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path

BASE = Path('research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929')

def read(name):
    return json.loads((BASE / name).read_text())

def digest(name):
    return hashlib.sha256((BASE / name).read_bytes()).hexdigest()

def reproduce():
    rows = list(csv.DictReader((BASE / 'EV_ACTUAL_CONTEXT.tsv').open(), delimiter='\t'))
    expected = [(r['locus'], i, t) for r in rows[:4] for i, t in enumerate(r['eva_clean'].split(), 1)]
    assert len(expected) == 28
    assert [r['locus'] for r in rows] == ['f68r1.1','f68r1.2','f68r1.3','f68r1.4','f68r1.26']
    r, v, old = read('EW_POSITION_AUTHOR.json'), read('EW_VISIBILITY_AUTHOR.json'), read('EV_PARAGRAPH_AUTHOR.json')
    assert expected == [(x['locus'], x['group_index'], x['raw_group']) for x in r['positions']]
    assert all(''.join(x['parse']) == x['raw_group'] for x in r['positions'])
    declarations = r['shared_four_atoms'] | r['new_local_units']
    assert all(part in declarations for x in r['positions'] for part in x['parse'])
    actual_parts = Counter(part for x in r['positions'] for part in x['parse'])
    assert len(declarations) == r['costs']['total_unit_values'] == 29
    assert len(r['grammar']) == 12 and len(r['clauses']) == 6
    old_parses = {x['token']:x['parse'] for x in old['whole_group_accounting'] if 'parse' in x}
    assert old_parses == r['retained_seven_exact_form_parses']
    assert all(x['parse'] == old_parses[x['raw_group']] for x in r['positions'] if x['raw_group'] in old_parses)
    assert v['whole28_accounting'] == old['whole_group_accounting']
    assert v['retained_atoms'] == old['whole_context_application']['exact_construction']['semantic_atoms']
    assert v['input_sha256'] == digest('EV_ACTUAL_CONTEXT.tsv')
    assert v['source_events_sha256_unchanged'] == digest('EV_SOURCE_EVENTS.json')
    claimed, concatenated = 'qokeeedy', ''.join(['qo','k','ee','dy'])
    assert concatenated == 'qokeedy' and concatenated != claimed
    daram = next(x for x in r['positions'] if x['raw_group'] == 'daram')
    c5 = next(x for x in r['clauses'] if x['id'] == 'C5')
    assert 'END(I)=END(I_down_after_up)' in daram['formula_contribution']
    assert 'I_down_after_up' not in c5['formula']
    critic = read('EW_POSITION_CRITIC.json')
    assert critic['source_integrity']['author_sha256'] == digest('EW_POSITION_AUTHOR.json')
    vruntime = (datetime.fromisoformat(v['frozen_utc']) - datetime.fromisoformat(v['started_utc'])).total_seconds()
    rruntime = (datetime.fromisoformat(r['frozen_utc']) - datetime.fromisoformat(r['started_utc'])).total_seconds()
    return {
        'status':'OBSERVED_AUTHOR_ACCOUNTING_AND_FAILURES_REPRODUCED_ONLY',
        'input_sha256':digest('EV_ACTUAL_CONTEXT.tsv'),
        'source_sha256':digest('EV_SOURCE_EVENTS.json'),
        'R_author_sha256':digest('EW_POSITION_AUTHOR.json'),
        'V_author_sha256':digest('EW_VISIBILITY_AUTHOR.json'),
        'critic_sha256':digest('EW_POSITION_CRITIC.json'),
        'R_exact_positions':28, 'R_exact_parses':28,
        'R_declared_units':29, 'R_part_use_counts':dict(sorted(actual_parts.items())),
        'R_rule_inventory':12, 'R_clause_inventory':6,
        'V_original_partial_preserved':True,
        'V_full_draft_literal_failure':{'target':claimed,'parts':['qo','k','ee','dy'],'result':concatenated},
        'R_C5_contribution_reconciliation':'FAIL: detailed daram END equality absent from bundled C5 under R5',
        'R_cycle_derivation':'UNBOUND interface; no unconditional UNSAT',
        'V_elapsed_seconds':vruntime,'V_budget_seconds':480,'V_overrun_seconds':max(0,vruntime-480),
        'R_elapsed_seconds':rruntime,'R_budget_seconds':480,
        'meaning_validation':False,'confirmed_words':0,'independent_confirmation_leaves':0,
        'scope':'Existing five-locus EV artifact only; no new manuscript acquisition',
    }

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=reproduce();serialized=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    destination=BASE/'EW_ACCOUNTING_VALIDATION.json'
    if args.write: destination.write_text(serialized)
    else: assert destination.read_text()==serialized
    print(json.dumps({k:result[k] for k in ['status','R_exact_positions','R_declared_units','V_full_draft_literal_failure','R_C5_contribution_reconciliation','V_overrun_seconds','meaning_validation']}))

if __name__=='__main__': main()
