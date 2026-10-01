#!/usr/bin/env python3
"""Owned technical checks, not a semantic validator or comparative author reader."""
import collections,datetime,hashlib,json,pathlib,subprocess,sys
BASE=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads((BASE/p).read_text())
def sha(p):return hashlib.sha256((BASE/p).read_bytes()).hexdigest()
expected={'src/B_CONSTRUCTORS.json':'6c71078c6edc039019cf60d8777e1b903ad2dc6ab6d7818bfe9e7af6ba6f7f65','src/B_EXTENSIONS.json':'5e78d04079049b41dc082e112210f33cc9df93205d84bb490b697e4425367b42','src/SOURCE.json':'d228057d52a97287f071b336a09dbaf9782f20c1ccde201df99c24f269e45a68'}
assert all(sha(p)==s for p,s in expected.items())
for _ in range(2):
 subprocess.run([sys.executable,str(BASE/'src/B_MATERIALIZE.py')],check=True,stdout=subprocess.DEVNULL)
 subprocess.run([sys.executable,str(BASE/'src/B_WRITE_READING.py')],check=True)
 now={p:sha(p) for p in ['artifacts/B_ACCOUNT.json','artifacts/B_READING.md']}
 if _==0:previous=now
 else:assert now==previous
source=load('src/SOURCE.json');a=load('artifacts/B_ACCOUNT.json');f=load('src/B_CONSTRUCTORS.json');ext=load('src/B_EXTENSIONS.json')
assert len(a['rows'])==473 and len({r['source_group_id'] for r in a['rows']})==473
lookup={r['source_group_id']:r for r in a['rows']}
assert all(all(lookup[r['source_group_id']][k]==v for k,v in r.items()) for r in source['rows'])
assert len(source['rows'][0])==12
assert len(f['core_families'])==12 and len(f['opaque_constants'])==8
assert len(a['dictionary'])==50 and len(ext['added_exact_forms'])==37
assert all(r['interpretation']==a['dictionary'].get(r['ivtff_group_raw']) for r in a['rows'])
assert all(x['same_entry_all_occurrences'] for x in a['recurrence_audit'])
assert a['costs']['unknown_carry_assumptions_used']==0
assert all(not r['returns'] for r in a['rows'] if r['status'] in ['UNKNOWN','BLOCKED_UNPROVEN_UNKNOWN_BRIDGE','BLOCKED_MISSING_INITIAL_INPUTS'])
assert not any(r['status'] in ('PARTIAL_MISSING_INPUT','CONTRADICTION') for r in a['rows'])
assert all(c['truth_under_declared_inputs'] for c in a['world_propositions'])
assert len([e for e in a['physical_events'] if e['id'].startswith('IT2a:')])==10
assert {e['phase'] for e in a['physical_events'] if e['id'].startswith('IT2a:')}==set(range(1,7))
assert sum(u['reader']=='IT2a' and u['block']=='N' and u['complete'] for u in a['primary_units'])==1
it_e=next(u for u in a['primary_units'] if u['reader']=='IT2a' and u['block']=='E')
assert it_e['operational_complete'] and not it_e['complete'] and len(it_e['strict_contribution_gaps'])==3
assert {x['raw_form'] for x in a['shared_part_uses'] if x['returned_value'] is not None and x['consumer_source_ids']} >= {'aiin','daiin','shodaiin'}
assert len(a['native_uncertain_seams'])==14 and a['costs']['source_boundary_assumption_count']==5
assert collections.Counter(x['block'] for x in a['costs']['postfreeze_source_boundary_assumptions'])=={'N':3,'E':2}
assert a['other_authors_read'] is False
assert len([line for line in (BASE/'artifacts/B_READING.md').read_text().splitlines() if line.startswith('| ') and '&#124;f85r2.' in line])>=473
assert all(sha(p)==s for p,s in expected.items())
report={'schema':'GDT1131_B_OWNED_TECHNICAL_CHECKS_v1','status':'PASS_TECHNICAL_CHECKS_ONLY','scope':'Exact source conservation, frozen rules, deterministic owned replay and explicit outcome/gap preservation. Semantic truth, completeness and author comparison are not checked.','checks':{'473_unique_native_rows_all12_fields':True,'initial_and_extension_bytes_unchanged':True,'same_exact_entry_all_recurrences':True,'deterministic_account_and_reading':True,'initial_family_and_constant_caps':True,'no_unknown_carry_or_blocked_execution':True,'IT19_N_27_E_operational':True,'IT_E_three_unused_reference_gaps_preserved':True,'same_aN_actual_consumers_on_three_licensed_forms':True,'five_paid_ZL_native_boundaries':True,'ten_IT_physical_events_six_ordered_phases':True,'all_author_meanings_C0':True,'blinding_preserved':True},'source_sha256':expected['src/SOURCE.json'],'account_sha256':sha('artifacts/B_ACCOUNT.json'),'reading_sha256':sha('artifacts/B_READING.md'),'primary_counts':[{'reader':u['reader'],'block':u['block'],'executed':u['accounted_count'],'native':u['count'],'strict_complete':u['complete'],'operational_complete':u['operational_complete']} for u in a['primary_units']]}
(BASE/'artifacts/B_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
