#!/usr/bin/env python3
"""Independent literal replay of frozen IDEA583 whole packet; no parser/executor."""
from pathlib import Path
import csv,json,hashlib,re,collections,sys
ROOT=Path(__file__).resolve().parents[3]
DOS=ROOT/'research_registry/proposals/laufenberg_f85r2_20260926'
NATIVE=ROOT/'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv'
DRAFT=DOS/'DEFAULT_CONTEXT_WHOLE_DRAFT.json'; CONTRACT=DOS/'DEFAULT_CONTEXT_AUTHOR_CONTRACT.json'; REPORT=DOS/'DEFAULT_CONTEXT_WHOLE_REPORT.md'
OUT=DOS/'DEFAULT_CONTEXT_WHOLE_REPLAY_B.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def tsv(p):
 with p.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f,delimiter='\t'))
def check(n,bad):
 checks[n]=not bool(bad)
 if bad: errors[n]=bad[:15] if isinstance(bad,list) else [bad]
checks={};errors={}
src=tsv(NATIVE); d=json.loads(DRAFT.read_text()); c=json.loads(CONTRACT.read_text()); a=d['all_occurrences']
source_cols=list(src[0]); sm={r['source_group_id']:r for r in src}; am={r['source_group_id']:r for r in a}
check('473_rows',len(src)!=473 or len(a)!=473)
check('unique_ids',len(sm)!=473 or len(am)!=473)
check('id_set',set(sm)^set(am))
mis=[]
for sid,r in sm.items():
 q=am.get(sid)
 if q is None or any(q.get(k)!=r[k] for k in source_cols):mis.append(sid)
check('all_12_native_fields_match',mis)
check('first_contract_hash_and_bytes',not d['first_contract_unchanged'] or d['first_contract_hashes'].get('json')!=sha(CONTRACT))
# Lexical binding conservation: 66 exact old values and 7 newly counted, no unregistered additions.
oldlex=c['lexicon']; newlex=d['lexicon']; le=[]
for form,entry in oldlex.items():
 if newlex.get(form)!=entry:le.append(form)
check('66_frozen_bindings_unchanged',le or len(oldlex)!=66)
check('new_bindings_exactly_seven',set(d['new_whole_bindings'])!={'sain','opchdy','qotor','sheedy','shodaiin','olfar','ary'} or len(d['new_whole_bindings'])!=7)
check('lexicon_union_exact',set(newlex)!=(set(oldlex)|set(d['new_whole_bindings'])))
# Every lexicon value must match every exact whole form, and the all-reader row inventory must bind exactly once.
row_errors=[]
for row in a:
 entry=newlex.get(row['ivtff_group_raw'])
 expected=entry
 got=row.get('whole_binding')
 if expected!=got:row_errors.append({'id':row['source_group_id'],'expected':expected,'got':got})
check('row_bindings_match_frozen_lexicon',row_errors)
# Every family occurrence exactly matches underlying literal target rows and frozen family value.
pairs=[('dar','odar'),('tedy','otedy'),('tchedy','otchedy'),('chedy','ochedy'),('che@152;y','oche@152;y')]
expected_family=[]
for row in src:
 raw=row['ivtff_group_raw']
 if any(raw in pair for pair in pairs): expected_family.append(row['source_group_id'])
family=d['all_41_family_obligations']; fammap={r['source_group_id']:r for r in family}
check('41_family_ids_exact',len(family)!=41 or {r['source_group_id'] for r in family}!=set(expected_family))
check('family_row_raw_exact', [r['source_group_id'] for r in family if r['source_group_id'] not in sm or fammap[r['source_group_id']]['ivtff_group_raw']!=sm[r['source_group_id']]['ivtff_group_raw']])
fam_bind=[]
for row in family:
 actual=am.get(row['source_group_id'],{}).get('whole_binding')
 if row.get('whole_binding')!=actual:fam_bind.append(row['source_group_id'])
check('family_values_match_all_occurrences',fam_bind)
# Recompute status/counts and unique-form totals.
sc=collections.Counter((r['edition'],r['derivation_status']) for r in a)
reported=d['counts']['by_reader_and_status']; scerr=[]
for ed,obj in reported.items():
 for status,n in obj.items():
  if sc[(ed,status)]!=n:scerr.append((ed,status,n,sc[(ed,status)]))
for ed in ('ZL3b','IT2a','RF1b'):
 if sum(v for (e,_),v in sc.items() if e==ed)!={'ZL3b':156,'IT2a':157,'RF1b':160}[ed]:scerr.append((ed,'total'))
check('reader_status_counts',scerr)
check('ZL_type_counts',len({r['ivtff_group_raw'] for r in src if r['edition']=='ZL3b'})!=115 or len(d['unknown_ZL_types'])!=44)
# Reconstruct all derivation spans from numeric source IDs and verify each listed token string.
by_locus={}
for r in src:
 if r['edition']=='ZL3b':by_locus.setdefault(r['locus'],[]).append(r)
for rows in by_locus.values():rows.sort(key=lambda r:int(r['source_group_index']))
span_errors=[]; all_span_ids=[]; status_expected={}
for item in d['manual_derivations']:
 span=item['span']
 m=re.fullmatch(r'\.(\d+) G(\d+)(?:-G(\d+)| through \.(\d+) G(\d+))',span)
 if not m:span_errors.append({'span':span,'parse':'unrecognized'});continue
 loc1=int(m.group(1));g1=int(m.group(2));loc2=int(m.group(4) or loc1);g2=int(m.group(5) or m.group(3))
 ids=[]
 for loc in range(loc1,loc2+1):
  rws=by_locus.get(f'f85r2.{loc}',[])
  low=g1 if loc==loc1 else 1; high=g2 if loc==loc2 else len(rws)
  ids.extend(f'ZL3b|f85r2.{loc}|G{i:03d}' for i in range(low,high+1))
 raw=[sm[x]['ivtff_group_raw'] for x in ids if x in sm]
 if raw!=item['tokens']:span_errors.append({'span':span,'expected':raw,'listed':item['tokens']})
 all_span_ids.extend(ids)
 for sid in ids:status_expected[sid]='LOCAL_DERIVED_WITH_UNPARSED_INTERVENING_TEXT' if span.startswith('.13 ') or span.startswith('.15 ') else 'LOCAL_DERIVED_COMPLETE_UNIT'
check('all_derivation_tokens_match_projection',span_errors)
check('spans_nonoverlap_and_correct_length',len(all_span_ids)!=len(set(all_span_ids)) or len(all_span_ids)!=82)
status_errors=[]
for row in a:
 exp=status_expected.get(row['source_group_id'])
 if exp and row['derivation_status']!=exp:status_errors.append((row['source_group_id'],exp,row['derivation_status']))
check('derived_status_matches_listed_spans',status_errors)
# Counts and payload accounting from entries.
ind=len(newlex)-sum(1 for e in newlex.values() if e.get('independent_binding') is False)
payload=sum(e.get('primitive_payload_count',0) for e in newlex.values())
check('binding_and_payload_totals',ind!=68 or payload!=78 or sum(e['primitive_payload_count'] for e in d['new_whole_bindings'].values())!=9)
check('reported_group_coverage_total',d['counts']['literal_rows']!=473 or sum(sum(v.values()) for v in reported.values())!=473)

result={'status':'PASS_LITERAL_AND_SPAN_REPLAY' if all(checks.values()) else 'FAIL_LITERAL_OR_SPAN_REPLAY',
 'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [NATIVE,CONTRACT,DRAFT,REPORT]},
 'method':'Independent exact comparison to the owned GDT1042 native_groups.tsv; exact old lexicon equality against frozen contract JSON; family IDs and values recomputed from literals; derivation spans reconstructed from numeric group IDs. No producer runner imported, no semantic executor.',
 'checks':checks,'errors':errors,
 'recomputed':{'rows':len(src),'row_ids':len(sm),'family_occurrences':len(expected_family),'derived_span_groups':len(all_span_ids),'reader_status_counts':{ed:{st:sc[(ed,st)] for e,st in sc if e==ed} for ed in ('ZL3b','IT2a','RF1b')},'old_bindings':len(oldlex),'new_bindings':len(d['new_whole_bindings']),'whole_bindings':len(newlex),'independent_entries':ind,'payload_sum':payload},
 'manual_findings':{'N2':'sain receives the same DEREF(x) twice under the no-intervening-ar binder-write scope, returns BooleanScalar and EQUALS compares that scalar to opchdy TRUE. This is a tautological identity check, not context variation or evidence.',
 'N3':'qotor(sheedy,shodaiin,olfar,ary) is a complete, typed positive proposition asserting distinct nonempty thermal-disposition profile sets for OLD and YOUNG, without ranking. It is an added profile model, not the source duty’s more direct response-under-COLD/HEAT relation; no link is made to c0/c1 or their conduct plans.',
 'O4':'The report is right that N3 is an assertion rather than only the E comparison plan, and that general case-specific adjustment plans occur. But its own limitation remains material: old/young profile values are not identified with c0/c1, and profile-of-disposition inequality is not by itself an assertion about response to external cold versus heat. So O4 is only partly addressed unless the original source duty is narrowed to thermal profile variation plus generic context-specific adjustment. No particular source-to-target link is supplied.',
 'O2':'Explicitly incomplete; same input is shown HARM at c1 and GOOD in .13 under default but no written distinct time fields or relation to YEAR.',
 'O3':'Explicitly incomplete; c0/c1 ownership does not write distinct recipients or health class.',
 'alternate_rows':'All IT/RF rows remain unparsed. Frozen c0/c1/d register and fixed argument debts are retained; they are direct-use constraints, not global impossibility. New packet does not repair them.',
 'scope':'The 72 complete ZL groups (A1 35 + N.2/N.3 10 + E 27), ten conditional local groups (.13/.15), 24 assigned-unparsed and 50 unknown-unparsed total 156. No whole page reading.'},
 'limitations':'Literal/span replay only; manual semantics are conditional on highly free authored values. No native image/source review, no confirmed meanings, no global UNSAT.'}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':result['status'],'checks':checks,'errors':errors,'recomputed':result['recomputed'],'output':str(OUT.relative_to(ROOT))},ensure_ascii=False,indent=2))
if not all(checks.values()):sys.exit(1)
