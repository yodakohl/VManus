#!/usr/bin/env python3
"""Independent receipt/account checks. No semantic engine or author mutation.

Only VALIDATION.json is written. VALIDATION.md records separate manual review.
"""
import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
PINS = {
    'METHOD.md': 'f80ac11c49d66cb055ef61d1391402d4066216bf0306d1f49e36a617dda2d861',
    'src/SOURCE.json': '0ea56ea589521e0b1b57f56f63df43fa9cd3f2dab6255a51986c097dbd53f137',
    'artifacts/VALIDATION_PLAN.md': '0f7ee777fe6fe58be56e2e7c56a15c14841056574ca738e6e8086d4bbef6c236',
    'CORE.json': '2b1efddd83da54d801c61e0249a373f392480f1f842edd7ce18ed46ca86a43f3',
    'CORE.md': '34a46dae74da8e7dd2e886dfb523222d1a56eb7f09dbeee9166cefe08d65c672',
    'AUTHOR_READING.md': '69f1fff4e129a95b89090f20d70bfb86212e542acf1c184a92da43f83ef551df',
    'artifacts/AUTHOR_ACCOUNT.json': '9ec0b0890d16eb2617a7657a53025cec0b8d4ad7c97ea87ae9ac90059acc9e3d',
    'artifacts/AUTHOR_RECEIPT.json': '6c9540f00658bb23bac972b35010722f16855e993face00feee441b9fd267e6d',
    'src/author_check.py': 'b5170149add7642dfc60c58ca56f3e85eca20fffd8ac373d90dea6587029afc9',
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(s):
    return json.loads((EXP / s).read_text())

def bound(s):
    p = Path(s)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('unsafe receipt path')
    return ROOT / p

def main():
    checks = []
    def check(name, value, evidence=None):
        checks.append({'name': name, 'pass': bool(value), 'evidence': evidence})
    before = {s:sha(EXP/s) for s in PINS}
    check('registered_and_final_byte_pins', before == PINS, before)
    source, a, core = load('src/SOURCE.json'), load('artifacts/AUTHOR_ACCOUNT.json'), load('CORE.json')
    receipt, reg, freeze = load('artifacts/AUTHOR_RECEIPT.json'), load('artifacts/REGISTRATION_RECEIPT.json'), load('artifacts/CORE_FREEZE_RECEIPT.json')
    sourcepins = {r['path']:sha(bound(r['path'])) == r['sha256'] for r in source['sources']}
    check('all_seven_bound_source_pins', all(sourcepins.values()), sourcepins)
    check('final_receipt_pins', all(sha(bound(r['path']))==r['sha256'] for r in receipt['files']))
    check('core_freeze_pins', all(sha(bound(s))==h for s,h in freeze['core_hashes'].items()))
    check('registration_receipt_pins', all(reg[k]==PINS[p] for k,p in [('method_sha256','METHOD.md'),('source_sha256','src/SOURCE.json'),('validation_plan_sha256','artifacts/VALIDATION_PLAN.md')]))
    stamp = lambda s:datetime.fromisoformat(s.replace('Z','+00:00'))
    check('documented_stage_chronology', stamp(reg['utc']) < stamp(freeze['author_freeze_utc']) < stamp(freeze['root_recorded_utc']) < stamp(a['authored_utc']) < stamp(receipt['final_author_freeze_utc']), 'Documented clocks; no independent secrecy or public commit-time certification.')
    check('account_source_core_references', sha(bound(a['source_native_path']))==a['source_native_sha256'] and a['core_sha256']==PINS['CORE.json'] and a['core_md_sha256']==PINS['CORE.md'])
    with bound(a['source_native_path']).open(newline='') as f:
        native=list(csv.DictReader(f,delimiter='\t'))
    rows=a['primary_account']; primary=[r for r in native if r['edition']=='ZL3b' and r['block']!='OUTSIDE']
    check('473_all_fields_global_order_exact', len(native)==473 and native==a['conserved_native_rows'], {'rows':len(native),'fields':list(native[0])})
    check('473_unique_ids', len({r['source_group_id'] for r in a['conserved_native_rows']})==473)
    check('108_primary_all_fields_order_exact', len(rows)==108 and primary==[r['native'] for r in rows])
    blocks=Counter(r['block'] for r in primary); editions=Counter(r['edition'] for r in native if r['block']!='OUTSIDE')
    check('native_reader_block_counts', dict(blocks)=={'N':19,'E':27,'S':26,'W':36} and dict(editions)=={'ZL3b':108,'IT2a':107,'RF1b':109}, {'blocks':dict(blocks),'editions':dict(editions)})
    check('149_outside_retained_without_primary_gloss', sum(r['block']=='OUTSIDE' for r in native)==149 and all(r['native']['block']!='OUTSIDE' for r in rows))
    check('primary_required_fields_nonempty', all(r[k] for r in rows for k in ['analysis','stable_denotation','grammatical_attachment','contribution','clause_anchor','epistemic_status','syntax_status']))
    repeats=defaultdict(list)
    for r in rows: repeats[r['native']['ivtff_group_raw']].append(r)
    check('exact_repeats_same_analysis_sense', all(all(r['analysis']==rs[0]['analysis'] and r['stable_denotation']==rs[0]['stable_denotation'] for r in rs) for rs in repeats.values()), {f:len(rs) for f,rs in repeats.items() if len(rs)>1})
    e=a['extensions']; primitives={**core['lexicon'],**e['primitive_entries']}; new={r['form']:r['parts'] for r in e['ordered_component_licenses']}; licenses={**core['ordered_component_licenses'],**new}
    check('no_extension_replaces_core', not set(core['lexicon']) & set(e['primitive_entries']) and not set(core['ordered_component_licenses']) & set(new))
    check('18_exact_assemblies_defined_parts', len(licenses)==18 and all(''.join(parts)==f and all(p in primitives for p in parts) for f,parts in licenses.items()))
    check('assigned_analyses_licensed', all(r['analysis']==licenses.get(r['native']['ivtff_group_raw']) or r['analysis']==[r['native']['ivtff_group_raw']] and r['native']['ivtff_group_raw'] in primitives for r in rows if r['semantic_status']!='UNKNOWN_WORD'))
    occ=lambda f:[r['native']['source_group_id'] for r in rows if r['native']['ivtff_group_raw']==f]
    check('new_whole_occurrences_exact', all(v['whole_occurrences']==occ(f) for f,v in e['primitive_entries'].items()))
    check('new_licensed_occurrences_exact', all(r['occurrences']==occ(r['form']) for r in e['ordered_component_licenses']))
    byid={r['native']['source_group_id']:r for r in rows}
    check('core_context_raw_clauses_retained', all([byid[i]['native']['ivtff_group_raw'] for i in c['native_ids']]==c['raw'] and c['clause'] in a['connected_readings'][byid[c['native_ids'][0]]['native']['block']] for c in core['complete_contexts']))
    md=(EXP/'AUTHOR_READING.md').read_text()
    check('four_prose_readings_exact_in_md', set(a['connected_readings'])==set('NESW') and all(p in md for p in a['connected_readings'].values()))
    check('all_108_ids_raw_attachments_in_md', all(r['native']['source_group_id'].replace('|','\\|') in md and r['native']['ivtff_group_raw'] in md and r['grammatical_attachment'] in md for r in rows))
    unknown=[r for r in rows if r['semantic_status']=='UNKNOWN_WORD']
    check('44_unknowns_literal_in_block_prose', all('[UNKNOWN:'+r['native']['ivtff_group_raw']+']' in a['connected_readings'][r['native']['block']] for r in unknown))
    check('unknown_inventory_exact_positions_counts', a['unknown_inventory']==[
        {'form':f,'count':len(rs),'native_ids':[r['native']['source_group_id'] for r in rs]}
        for f,rs in sorted(repeats.items()) if rs[0]['semantic_status']=='UNKNOWN_WORD'])
    priors=load('artifacts/WORD_PRIORS.json')
    check('word_prior_exact_primary_form_scope', priors['profile_count']==85 and
          {p['form'] for p in priors['profiles']}==set(repeats) and priors['source_receipt']['inputs']['selector_count']==179,
          'Cached selector incidence, not physical folio count; frozen MD header count/leaves is imprecise.')
    counts={'all_native_rows':len(native),'primary_positions':len(rows),'primary_type_count':len(repeats),'semantic_unknown_positions':len(unknown),'semantic_unknown_types':len({r['native']['ivtff_group_raw'] for r in unknown}),'structural_positions':sum(r['semantic_status']=='STRUCTURAL_MARK' for r in rows),'core_scope_unresolved_positions':sum(r['semantic_status']=='UNRESOLVED_CORE_SCOPE' for r in rows),'known_sense_positions':sum(r['semantic_status']=='DEFINED_C0_WORD' for r in rows),'syntax_unresolved_positions':sum(r['syntax_status'].startswith('UNRESOLVED') for r in rows),'core_primitive_entries':len(core['lexicon']),'new_primitive_entries':len(e['primitive_entries']),'core_ordered_licenses':len(core['ordered_component_licenses']),'new_ordered_licenses':len(new),'core_rule_cards':len(core['rules']),'new_rule_cards':len(e['ordinary_constructions'])}
    check('all_account_receipt_counts_exact', counts==a['counts']==receipt['counts'], counts)
    used=Counter(p for r in rows if isinstance(r['analysis'],list) for p in r['analysis'])
    check('all_32_primitives_used_in_assigned_analysis', set(used)==set(primitives), dict(used))
    limits=a['result_limits']
    check('honest_partial_zero_confirmation', a['candidate_label']==receipt['candidate_label']=='PARTIAL_SCOPED_C0' and limits['confirmed_words']==0 and not limits['confirmed_source'] and limits['independent_confirmation_capacity']==0 and limits['meaning_preference']=='NONE' and limits['reserves']=='CLOSED')
    supplemental=subprocess.run([sys.executable,str(EXP/'src/author_check.py')],cwd=ROOT,capture_output=True,text=True,timeout=30)
    check('read_only_author_checker', supplemental.returncode==0,supplemental.stdout.strip())
    check('all_pinned_scientific_bytes_unchanged', before=={s:sha(EXP/s) for s in PINS})
    result={'experiment':'GDT1140','validator_sha256':sha(Path(__file__)),'frozen_plan_sha256':PINS['artifacts/VALIDATION_PLAN.md'],'accounting_pass':all(c['pass'] for c in checks),'checks':checks,'counts':counts,
      'per_block':{b:{'positions':blocks[b],'semantic_statuses':dict(Counter(r['semantic_status'] for r in rows if r['native']['block']==b)),'syntax_unresolved':sum(r['syntax_status'].startswith('UNRESOLVED') for r in rows if r['native']['block']==b)} for b in 'NESW'},
      'manual_adjudication':{'candidate':'PARTIAL_SCOPED_C0','complete_reading':False,'fixed_core_contradiction_established':False,'scope_discrepancy':a['scope_discrepancy'],'assigned_words_with_unresolved_syntax':sum(r['semantic_status']=='DEFINED_C0_WORD' and r['syntax_status'].startswith('UNRESOLVED') for r in rows),'symbolic_reuse':'Exact common d/qo HOLD compositions and or/ol actor-reference applications are authored explicitly. No runtime semantic computation claimed.','prose_review':'All108 attachments, full core/account/prose/code and complete owned Carmina read. No established prose/table contradiction;68 unresolved syntax positions prevent whole reading.','costs':'32 primitives,18 finite licenses,16 grammar cards; alias/default/boundary/reference assumptions disclosed. Not measured MDL/search freedom.','rival':'Physiological capacity/general condition record and lexical renaming remain indistinguishable.'},
      'unverified':['English meanings, native visual truth, source identity and complete grammatical coherence.','Semantic runtime/replay/interventions: not applicable; no semantic API or manual-account generator.','Independent public commit time or author secrecy: documented chronology only.','Full numerical freedom cost of each clause/reference/scope choice.','Full old1137/1138/1139 tree baseline: no registered whole-tree pins in this contract; this validator edits none. Bound884/998 reports checked.'],
      'claim_ceiling':{'confirmed_words':0,'meaning_preference':'NONE','independent_confirmation':0,'reserves':'CLOSED'}}
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'accounting_pass':result['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],'candidate':'PARTIAL_SCOPED_C0','counts':counts},sort_keys=True))
    return 0 if result['accounting_pass'] else 1

if __name__=='__main__':
    raise SystemExit(main())
