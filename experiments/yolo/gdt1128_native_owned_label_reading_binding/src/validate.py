"""Read-only scientific-output accounting; no glyph/meaning adjudication."""
from pathlib import Path
import csv,hashlib,json
D=Path(__file__).resolve().parents[1]
M=json.loads((D/'experiment.json').read_text()); A=D/'artifacts'
checks={x['path']:hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in M['inputs']}
checks.update({x['path']:hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in M['outputs'] if x['path']!=str(A.relative_to(Path.cwd())/'VALIDATION.json')})
plan=json.loads((D/'src/CASE_PLAN.json').read_text()); result=json.loads((A/'RESULT.json').read_text()); go=json.loads((A/'TEXT_QUERY_GO.json').read_text()); receipt=json.loads((A/'TEXT_QUERY_RECEIPT.json').read_text())
checks['three_fixed_cases']=len(plan['cases'])==3
checks['both_seals']=M['sealed_data']=={'f84':'FORBIDDEN','f84r':'FORBIDDEN'}
checks['all_native_freezes_unchanged']=all(hashlib.sha256((A/n).read_bytes()).hexdigest()==v for n,v in go['frozen_hashes'].items())
checks['query_after_go']=receipt['utc']>=go['utc']
rows=list(csv.DictReader((A/'CACHED_LABELS.tsv').open(),delimiter='\t'))
expected={(x['locus'],e) for x in plan['cases'] for e in plan['readers']}
checks['all_nine_cached_reader_cases']=len(rows)==9 and {(r['locus'],r['edition']) for r in rows}==expected
checks['raw_labels_preserved']=all(r['kind']=='L' and r['grammar_scope']=='DIAGNOSTIC_NONPROSE' and r['source_group_count']=='1' for r in rows)
checks['all_table_cases_preserved']=len(result['table'])==9 and {(r['locus'],r['reader']) for r in result['table']}==expected
checks['no_exact_prose_bridge']=all(r['profile179_prose_count']==0 for r in result['table'])
checks['no_independent_or_meaning_claim']=result['confirmed_words']==0 and result['independent_semantic_confirmation_capacity']==0 and result['precache_independently_recovered_exact_wholeforms']==0
checks['scope_kept']=result['f84_f84r_f116v_or_reserves_opened'] is False and result['profile179_scope_excludes_f102r2'] is True
out={'status':'PASS' if all(checks.values()) else 'FAIL','claim_ceiling':'File identity, frozen-record integrity and complete case accounting only; not native reading, semantic validation, or scientific PASS','checks':checks}
(A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'checks':len(checks),'errors':[k for k,v in checks.items() if not v]}));assert all(checks.values())
