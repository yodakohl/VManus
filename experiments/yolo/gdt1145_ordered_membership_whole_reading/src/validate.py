#!/usr/bin/env python3
"""Independent released-author accounting, without a semantic executor.

Reads only the guarded F83_P1 projection plus bound receipt/profile files.
Writes only artifacts/VALIDATION.json; never calls or replaces root run.py.
"""
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
PINS = {
 'METHOD.md':'e75f304337a08c8862f9c61e7b23ba8fb28a5a72884f3f3cec7fa53fa9832c38',
 'src/SOURCE.json':'530eaa9ff7c8d19c09f92da2875422e92d522e09a287181048f2b6206c7837ac',
 'artifacts/VALIDATION_PLAN.md':'3adf07a6b4587358893edb91df95653d5a8389dc2b72dfbbc9d63a66254a8ce7',
 'artifacts/CORE.json':'6f20ab9aaadebb0be15cd3ecc98526f6861c49a244a7da9007b43600cf8bc6e1',
 'artifacts/AUTHOR_ACCOUNT.json':'8cb3c84c3adfcd5930fc681cc2ad30a56001c00720746513c4869ae68e16a946',
 'artifacts/AUTHOR_READING.md':'c2de28aae3f61a7f27732c420fa62db688d10f500e16e26db4b7b93d26bd5aa4',
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(s):
    return json.loads((EXP/s).read_text())

def safe(base,s):
    p=Path(s)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('Unsafe receipt path')
    return base/p

def main():
    checks=[]
    def check(name,passed,evidence=None):
        checks.append({'name':name,'pass':bool(passed),'evidence':evidence})
    source=load('src/SOURCE.json'); lock=load('src/PREREG_LOCK.json')
    core=load('artifacts/CORE.json'); cf=load('artifacts/CORE_FREEZE.json')
    intake=load('artifacts/TARGET_INTAKE.json'); freeze=load('artifacts/AUTHOR_FREEZE.json')
    account=load('artifacts/AUTHOR_ACCOUNT.json')
    watched={s:sha(EXP/s) for s in set(PINS)|set(freeze['hashes'])}
    sourcepath=safe(ROOT,source['source']); sourcehash=sha(sourcepath)
    check('preplan_and_final_pins',all(watched[s]==h for s,h in PINS.items()),PINS)
    check('source_byte_pin',sourcehash==source['sha256'])
    check('registration_lock_pins',all(sha(safe(EXP,s))==h for s,h in lock['hashes'].items()))
    check('all_author_freeze_pins',all(watched[s]==h for s,h in freeze['hashes'].items()))
    check('core_freeze_and_intake_pins',sha(safe(EXP,cf['core_path']))==cf['core_sha256'] and sha(EXP/'artifacts/CORE_FREEZE.json')==intake['core_freeze_sha256'])
    stamp=lambda s:datetime.fromisoformat(s.replace('Z','+00:00'))
    check('documented_freeze_before_extraction_and_author_final',stamp(lock['utc'])<stamp(cf['frozen_utc'])<stamp(intake['utc'])<stamp(freeze['frozen_utc']),
          'Documented chronology only; no independent secrecy/publication-clock certification.')
    check('nonlexical_core_empty_initial_roster',core['lexical_values']==[] and core['glyph_or_whole_form_meanings']==[] and core['initial_state']['active_order']==[] and not core['target_opened_before_freeze'] and not cf['target_body_opened_before_freeze'])
    columns=['page','panel_id','record_id','locus','zl3b_line']
    argv=['./vmanus-exp','query-tsv',source['source'],'--selector','record_id','--allow','F83_P1','--columns',','.join(columns)]
    check('registered_scope_and_exact_guard_command',source['selector']=='record_id' and source['allow']==['F83_P1'] and source['columns']==columns and intake['command']==' '.join(argv))
    guarded=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=30)
    raw=(EXP/'artifacts/TARGET.tsv').read_bytes()
    check('guarded_extraction_exact_target_bytes',guarded.returncode==0 and guarded.stdout==raw)
    check('guarded_stderr_exact_receipt',guarded.stderr==(EXP/'artifacts/TARGET_GUARD.stderr.txt').read_bytes())
    check('target_and_author_source_references',sha(EXP/'artifacts/TARGET.tsv')==intake['sha256']==account['target']['sha256'] and sha(safe(ROOT,account['target']['path']))==account['target']['sha256'] and account['core']['sha256']==cf['core_sha256'] and sha(safe(ROOT,account['core']['path']))==account['core']['sha256'])
    reader=csv.DictReader(io.StringIO(raw.decode()),delimiter='\t'); lines=list(reader)
    check('five_fields_eight_exact_scoped_lines',reader.fieldnames==columns and len(lines)==8 and {r['page'] for r in lines}=={'f83r'} and {r['panel_id'] for r in lines}=={'F83_UPPER_SPRAY'} and {r['record_id'] for r in lines}=={'F83_P1'} and [r['locus'] for r in lines]==[f'f83r.{i}' for i in range(1,9)])
    expected=[(r['locus']+':'+str(i),'ZL3b',w) for r in lines for i,w in enumerate(r['zl3b_line'].split(' '),1)]
    rows=account['accounting']['rows']; actual=[(r['at'],r['edition'],r['word']) for r in rows]
    check('72_all_literal_words_positions_order_exact',len(expected)==72 and all(w for at,ed,w in expected) and actual==expected)
    check('72_unique_positions',len({r['at'] for r in rows})==72)
    md=(EXP/'artifacts/AUTHOR_READING.md').read_text()
    check('all_eight_exact_raw_lines_retained_in_prose',all(r['locus']+'  '+r['zl3b_line'] in md for r in lines))
    values={v['id']:v for v in account['lexical_values']}; form_values={v['form']:v['id'] for v in values.values()}
    check('three_unique_explicit_costed_values_rules',len(values)==len(form_values)==3 and len(account['rules'])==3 and all(v['cost'] and v['status'] and v['profile'] for v in values.values()))
    check('all_assignments_reference_defined_matching_forms',all(r['value_id']==form_values.get(r['word']) for r in rows))
    byform=defaultdict(list)
    for r in rows: byform[r['word']].append(r)
    check('every_repeated_form_same_declared_rule_status',all(len({(r['value_id'],r['rule'],r['status']) for r in rs})==1 for rs in byform.values()))
    unknown=[r for r in rows if r['value_id'] is None]; proposed=[r for r in rows if r['value_id'] is not None]
    check('64_explicit_unknowns_8_explicit_unbound_values',len(unknown)==64 and len(proposed)==8 and all(r['status']=='unknown_unassigned' and r['rule'] is None and r['binding'] for r in unknown) and all(r['status']=='proposed_value_unbound' and r['rule'] and r['binding'] for r in proposed))
    counts=Counter(r['word'] for r in rows); untypes=len({r['word'] for r in unknown})
    check('all_author_counts_exact',account['accounting']['groups']==account['accounting']['word_occurrences']==len(rows)==72 and account['accounting']['assigned_candidate_occurrences']==len(proposed)==8 and account['accounting']['unassigned_occurrences']==len(unknown)==64 and account['accounting']['unassigned_types']==untypes==51 and account['accounting']['target_type_counts']==dict(sorted(counts.items())) and all(v['target_occurrences']==counts[v['form']] for v in values.values()),{'lines':8,'groups':len(rows),'types':len(counts),'assigned':len(proposed),'unknown':len(unknown),'unknown_types':untypes})
    check('qekaiin_distinct_and_adjacent_selectors_not_deduplicated',byform['qekaiin'][0]['value_id'] is None and [(r['at'],r['word']) for r in rows if r['at'] in ['f83r.7:9','f83r.7:10']]==[('f83r.7:9','qoteedy'),('f83r.7:10','qoteedy')])
    profiles=load('artifacts/ROOT_PROFILE_CHECK.json')['profiles']
    ep=safe(ROOT,'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/EE_WORD_PROFILES.json')
    ee=json.loads(ep.read_text()); profilemap={p['form']:p for p in profiles+ee['profiles']}
    profile_checks=[]
    for p in account['profile_observations']:
        profile_checks.append(p['ZL3b_target_occurrences']==counts[p['form']])
        for key,v in p.items():
            if key.endswith('_profile') and isinstance(v,dict):
                ed=key.removesuffix('_profile'); actualprofile=profilemap[p['form']]['editions'][ed]
                profile_checks.append(all(actualprofile[k]==n for k,n in v.items()))
    check('descriptive_profile_observations_exact_separate_readers',all(profile_checks),{'supplemental_ee_profiles_sha256':sha(ep),'scope':'Cached exposed selectors; no new corpus read or semantic inference.'})
    check('honest_no_executed_chain_or_confirmation',account['status']=='PARTIAL_ACCOUNT_NO_EXECUTED_MEMBERSHIP_CHAIN' and freeze['accounting']['complete_chain'] is False and freeze['accounting']['confirmed_meanings']==0 and freeze['accounting']['significance_claim'] is False and account['replay']=='No replay code: no live complete chain exists.')
    rootresult=load('artifacts/RESULT.json')
    first_selector=next(i for i,r in enumerate(rows) if r['word']=='qoteedy')
    result_positions=[{k:r[k] for k in ['at','word','rule','status']} for r in proposed]
    check('root_result_consistent_with_authored_rows_and_unrun_limits',
          rootresult['decision']=='PARTIAL_ACCOUNT' and rootresult['secondary_status']=='NO_EXECUTED_WRITTEN_MEMBERSHIP_CHAIN'
          and rootresult['lines']==len(lines) and rootresult['groups']==len(rows)
          and rootresult['provisional_whole_form_values']==len(values) and rootresult['uniform_proposed_rules']==len(account['rules'])
          and rootresult['proposed_value_occurrences']==len(proposed) and rootresult['unknown_occurrences']==len(unknown)
          and rootresult['proposed_form_counts']=={v['form']:counts[v['form']] for v in values.values()}
          and rootresult['all_proposed_positions']==result_positions and rootresult['first_selector']==rows[first_selector]['at']
          and rootresult['proposed_introduction_tokens_before_first_selector']==sum(r['word']=='qokaiin' for r in rows[:first_selector])
          and rootresult['whole_record_execution']=='NOT_AVAILABLE'
          and rootresult['current_order_vs_original_slot']=='NOT_EVALUABLE_NO_WRITTEN_CHAIN'
          and rootresult['removal_withheld_intervention']=='NOT_EXECUTED_NO_BOUND_REMOVAL_OR_DUTY'
          and rootresult['confirmed_words']==rootresult['independent_meaning_confirmation_capacity']==0
          and rootresult['author_account_sha256']==sha(EXP/'artifacts/AUTHOR_ACCOUNT.json'),
          {'root_result_sha256':sha(EXP/'artifacts/RESULT.json'),'token_count_is_not_executed_roster':True})
    check('all_watched_scientific_bytes_unchanged',watched=={s:sha(EXP/s) for s in watched} and sha(sourcepath)==sourcehash)
    result={'experiment':'GDT1145','validator_sha256':sha(Path(__file__)),'plan_sha256':PINS['artifacts/VALIDATION_PLAN.md'],'accounting_pass':all(c['pass'] for c in checks),'checks':checks,
      'source_accounting':{'lines':len(lines),'groups':len(rows),'exact_forms':len(counts),'provisional_whole_values':len(values),'provisional_value_occurrences':len(proposed),'unknown_occurrences':len(unknown),'unknown_types':untypes,'declared_uniform_rules':len(account['rules'])},
      'review':{'author_outcome':'PARTIAL_ACCOUNT_NO_EXECUTED_MEMBERSHIP_CHAIN','written_chain':'NOT_DERIVED','word_meanings_validated':0,'execution':'No semantic executor, parsed target event chain, returned-value consumer or target rival/intervention run exists. CORE trace and differing recipients are contract examples only.','reference_truth':'value_id/form bindings and repeated rule labels mechanically checked. Descriptive operation labels correspond to R1-R3 prose by manual inspection; no callable/typed rule references or execution certified.','dependency_gaps':['Only one proposed introduction before first selector atf83r.2:7; unknown prefix not assigned missing introductions.','Removal atf83r.6:3 has no identified member argument. Later qokaiin is a fresh introduction under the declared rule; olchedy also intervenes.','No written count/duty and selector-to-duty binding derived.','All64unknown groups remain open; no event order/no-op/boundary/reference donation permitted.'],'author_prose_precision':'Generic rank-two selection requires at least two current members, not three. Three-member introduction is a separate full-trace obligation. The author wording cannot establish a manuscript count contradiction.','rivals':'CURRENT_ORDER versus ORIGINAL_SLOT/removal-withholding are unrun on the target. Generic entity register/ordered recipe instances remain semantically possible; no preference inferred.','costs':'Three costed whole-form C0 values and three uniform textual rules; identities, argument attachment, event order and duty construction remain missing/unpriced dependencies.'},
      'unverified':['Native visual truth, English meanings, historical/source identification and global manuscript claims.','Actual time of target opening/secrecy: receipts establish only documented freeze/intake chronology.','Additional raw-source fields or separator/uncertainty annotations not supplied by the W91 projection. Raw supplied line whitespace is retained exactly.','Complete old legacy tree baseline: source bytepin checked; validator writes only its JSON and does not modify legacy files.'],
      'scientific_pass':False,'confirmed_meanings':0,'independent_confirmation':0,'significance':False,'reserves':'CLOSED'}
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'accounting_pass':result['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],'groups':len(rows),'assigned_unbound':len(proposed),'unknown':len(unknown),'written_chain':'NOT_DERIVED'}))
    return 0 if result['accounting_pass'] else 1

if __name__=='__main__':
    raise SystemExit(main())
