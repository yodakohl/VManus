#!/usr/bin/env python3
"""GDT1133 independent released-account validator; no author writes."""
import ast, collections, copy, csv, gzip, hashlib, io, json, pathlib, subprocess, sys
sys.dont_write_bytecode=True
D=pathlib.Path(__file__).resolve().parents[1]
ROOT=D.parents[2]
EXPECTED_SHA='fbae55398a9a53c12af9a329a0ea46daec3cb4efb4b7529187f5b21f12cb1c6f'
MD_SHA='5737024ed1bacb5035a42f2266ce61eeb68b92b8c915e56e8009cb551418becd'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def local(s):
 p=pathlib.Path(s)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe relative file pin')
 v=D/p
 if not v.resolve().is_relative_to(D.resolve()):raise ValueError('Pin outside experiment')
 return v
checks=[]
def check(name,condition,detail=None):
 x={'check':name,'status':'PASS' if condition else 'FAIL'}
 if detail is not None:x['detail']=detail
 checks.append(x)
def replay_author():
 # Execute the released materializer in memory; omit only its two final I/O expressions.
 path=D/'src/AUTHOR_MATERIALIZE.py';tree=ast.parse(path.read_text())
 removed=[]
 for n in tree.body:
  if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call):
   f=n.value.func
   if isinstance(f,ast.Attribute) and f.attr=='write_text' or isinstance(f,ast.Name) and f.id=='print':removed.append(n)
 check('replay_only_final_write_and_print_omitted',len(removed)==2)
 tree.body=[n for n in tree.body if n not in removed]
 ctx={'__file__':str(path),'__name__':'independent_replay'}
 exec(compile(tree,str(path),'exec'),ctx)
 return ctx

def main():
 release=read(D/'artifacts/FINAL_RELEASE.json')
 if not release.get('review_authorized'):raise ValueError('Root final release required')
 expected=read(D/'artifacts/VALIDATOR_EXPECTATIONS.json');source=read(D/'src/SOURCE.json');account=read(D/'artifacts/AUTHOR_ACCOUNT.json')
 core=read(D/'src/CORE.json');ext=read(D/'src/EXTENSIONS.json');initial=read(D/'artifacts/AUTHOR_INITIAL_FREEZE_RECEIPT.json');final=read(D/'artifacts/AUTHOR_FINAL_FREEZE_RECEIPT.json')
 check('independent_expectation_bytes',sha(D/'artifacts/VALIDATOR_EXPECTATIONS.json')==EXPECTED_SHA and sha(D/'artifacts/VALIDATOR_EXPECTATIONS.md')==MD_SHA)
 check('all_frozen_contract_bytes',all(sha(local(p))==h for p,h in expected['contract_pins'].items()))
 check('all_registered_input_bytes',all(sha(ROOT/p['path'])==p['sha256'] for p in expected['registered_input_pins']))
 check('final_receipt_and_all_author_pins',sha(D/'artifacts/AUTHOR_FINAL_FREEZE_RECEIPT.json')==release['author_final_receipt_sha256'] and all(sha(local(p))==h for p,h in final['files'].items()))
 check('initial_core_extension_source_identity',all(sha(local(p))==h for p,h in initial['files'].items()) and initial['source_sha256']==final['source_sha256']==sha(D/'src/SOURCE.json')==core['source_sha256'] and ext['core_sha256']==sha(D/'src/CORE.json'))
 check('inventory_freeze_before_materialized_account',core['frozen_utc']<=initial['frozen_utc']<final['frozen_utc'] and account['generated_at_inventory_freeze_utc']==ext['frozen_utc'] and ext['no_complete_derivation_claimed_before_freeze'])
 carriers=read_compressed(ROOT/source['source_path'])
 check('source_exact_three_retained_f19r_readers',source['readers']==[r for r in carriers if r['page']=='f19r'] and {r['edition'] for r in source['readers']}=={'IT2a','ZL3b','RF1b'} and source['allow']==['f19r'] and not source['new_access'])
 del carriers
 columns=','.join(source['caption_native_rows'][0])
 query=subprocess.run([str(ROOT/'vmanus-exp'),'query-tsv','--selector','locus','--allow','f102v1.17','--columns',columns,source['caption_source_path']],cwd=ROOT,capture_output=True,text=True,check=True)
 native_caption=list(csv.DictReader(io.StringIO(query.stdout),delimiter='\t'))
 check('guarded_literal_C2_three_caption_rows',native_caption==source['caption_native_rows'] and sha(ROOT/source['caption_source_path'])==source['caption_source_sha256'] and all(r['ivtff_group_raw']==('losalody' if r['edition']=='RF1b' else 'loralody') for r in native_caption))
 native_body=[v for r in source['readers'] for l in r['lines'] for c in l['chunks'] for v in c['source_rows']]
 native=native_body+native_caption;actual={r['native']['source_group_id']:r['native'] for r in account['native_groups']}
 check('all233_native_rows_all_fields_no_duplicates',len(native)==len(account['native_groups'])==len(actual)==233 and all(actual[v['source_group_id']]==v for v in native))
 srcchunks=[c for r in source['readers'] for l in sorted(r['lines'],key=lambda l:int(l['locus'].split('.')[-1])) for c in l['chunks']]
 check('all227_hardchunks_final_units_and_native_spans_exact',len(srcchunks)==len(account['chunks'])==227 and all(c==a['native_chunk'] and c['units']==a['fixed_units'] and a['license_id']==' + '.join(c['raw_groups']) for c,a in zip(srcchunks,account['chunks'])))
 check('source_and_inventory_pins_in_account',account['source_sha256']==sha(D/'src/SOURCE.json') and account['core_sha256']==sha(D/'src/CORE.json') and account['extensions_sha256']==sha(D/'src/EXTENSIONS.json'))
 counts={'primitive_families':len(core['families']),'unit_function_assignments':len(core['unit_functions']),'opaque_constants':len(core['opaque_constants']),'finite_whole_hardchunk_licenses':len(ext['licenses']),'body_al_final_unit_sites':sum((c['units'] or []).count('al') for c in srcchunks)}
 check('declared_core_extension_counts_from_actual_definitions',counts==ext['counts'] and all(account['costs'][k]==v for k,v in counts.items()) and len(core['body_extra_atomic_definition_predicates'])==account['costs']['explicit_qol_atomic_predicates']==2)
 check('licenses_match_fixed_units_and_frozen_unit_functions',all(ext['licenses'][' + '.join(c['raw_groups'])]['fixed_final_units']==c['units'] and (ext['licenses'][' + '.join(c['raw_groups'])]['operations'] is None or ext['licenses'][' + '.join(c['raw_groups'])]['operations']==[core['unit_functions'][u] for u in c['units']]) for c in srcchunks))
 check('four_caption_functions_not_changed',core['fixed_caption_units']==['l','or','al','ody'] and core['fixed_caption_functions']=={'l':'CAPTION_SOURCE','or':'FROM_SOURCE','al':'DECOCTION_KIND','ody':'APPELLATION'} and core['unit_functions']['os']!='FROM_SOURCE')
 captions=[r for r in account['native_groups'] if r['is_caption']];caption_ok=True
 for r in captions:
  if r['native']['edition']=='RF1b':caption_ok &= r['status']=='PARTIAL_MISSING_INPUT' and r['first_barrier']['unit']=='os';continue
  vals=[s['returns'][0] for s in r['substeps']]
  caption_ok &= [v['type'] for v in vals]==['SourceKindRef','FromSourceSpec','MaterialKindSpec','Appellation']
  caption_ok &= vals[0]['kind']=='K19' and vals[1]['source_kind']=='K19' and vals[2]['kind']=='S19' and vals[2]['form']=='DECOCTION' and vals[2]['physical_instance'] is None and vals[3]['denotation']=='S19' and vals[3]['source_kind']=='K19' and vals[3]['form']=='DECOCTION'
 check('actual_nominal_caption_return_contracts_and_RF_barrier',caption_ok)
 barrier_ok=True;summary=[]
 for reader in source['readers']:
  edition=reader['edition'];rows=[r for r in account['native_groups'] if r['native']['edition']==edition and not r['is_caption']]
  chunks=[c for c in account['chunks'] if c['edition']==edition];barrier_seen=False
  for c in chunks:
   if barrier_seen:barrier_ok &= not c['substeps'] and c['status'] in ('UNKNOWN','BLOCKED_UNKNOWN_CONTINUITY','BLOCKED_AFTER_FIRST_TYPED_BARRIER') and {k:v for k,v in c['state_before'].items() if k!='unknown_ids'}=={k:v for k,v in c['state_after'].items() if k!='unknown_ids'}
   if c['status']!='ACCOUNTED_C0':barrier_seen=True
  reported=next(s for s in account['summary'] if s['reader']==edition);bad=next((r for r in rows if r['status']!='ACCOUNTED_C0'),None)
  check(edition+'_summary_actual_scope_and_first_barrier',reported['native_body_groups']==len(rows) and reported['accounted_native_groups']==sum(r['status']=='ACCOUNTED_C0' for r in rows) and reported['full_body_operational']==(bad is None) and (reported['first_barrier'] is None if bad is None else reported['first_barrier']['source_id']==bad['native']['source_group_id']))
  summary.append(reported)
 check('unknown_barriers_stop_all_later_execution_no_default_carry',barrier_ok)
 gaps=account['strict_whole_contribution_gaps']
 check('strict_PARTIAL_and_three_dead_wholes_retained',account['status'].startswith('PARTIAL') and len(gaps)==3 and all(not s['strict_complete'] for s in summary) and all(g['source_id'] in {r['native']['source_group_id'] for r in account['native_groups'] if r.get('strict_contribution_gap')} for g in gaps))
 ctx=replay_author();check('deterministic_entire_account_replay_without_writing_author',ctx['result']==account)
 # The existing operate API exposes actual state operands; replay actual source order only.
 operations=[(c['ids'],i,u) for r in source['readers'] if r['edition']=='IT2a' for l in sorted(r['lines'],key=lambda l:int(l['locus'].split('.')[-1])) for c in l['chunks'] for i,u in enumerate(c['units'])]
 probe_reports=[]
 def run_probe(name,hook=None,skip=None,ret_hook=None):
  st=ctx['init']('IT2a');oldret=ctx['ret'];events=[];failure=None
  if ret_hook:
   def modified_ret(step,value):
    value=oldret(step,value);ret_hook(step,value);return value
   ctx['ret']=modified_ret
  try:
   for n,(sid,index,u) in enumerate(operations):
    if skip and skip(sid,u):events.append({'source_ids':sid,'unit':u,'status':'DELETED_BY_INTERVENTION'});continue
    if hook:hook(st,sid,u)
    try:
     step=ctx['operate'](st,sid,u,index);events.append({'source_ids':sid,'unit':u,'status':'EXECUTED'})
    except ValueError as error:
     failure={'source_ids':sid,'unit':u,'reason':str(error),'actual_remaining_plan':[{'source_ids':s,'unit':v} for s,i,v in operations[n+1:]]};break
  finally:ctx['ret']=oldret
  report={'name':name,'first_failure':failure,'physical_liquid_exists':st['d'] is not None,'executed_operations':len(events),'state':ctx['compact'](ctx['state'](st))};probe_reports.append(report);return report
 baseline=run_probe('BASELINE');check('existing_operate_API_baseline_reaches_written_drink',baseline['first_failure'] is None and baseline['state']['drink'] is not None)
 or_sid=['IT2a|f19r.10|G002'];ody_sid=['IT2a|f19r.11|G002']
 def mutate_or(step,value):
  if step['source_ids']==or_sid and step['unit']=='or':value['source_kind']='K2'
 orprobe=run_probe('ALTER_ONLY_RETURNED_OR_SOURCE_FIELD',ret_hook=mutate_or)
 check('actual_returned_OR_field_read_at_later_raw_group',orprobe['first_failure'] is not None and orprobe['first_failure']['source_ids']!=or_sid and orprobe['first_failure']['reason']=='PREPARATION_SOURCE_MISMATCH')
 def mutate_ody(step,value):
  if step['source_ids']==ody_sid and step['unit']=='ody':value['form']='RAW_JUICE'
 odyprobe=run_probe('ALTER_ONLY_RETURNED_ODY_FORM_FIELD',ret_hook=mutate_ody)
 check('actual_returned_ODY_field_read_at_later_raw_group',odyprobe['first_failure'] is not None and odyprobe['first_failure']['source_ids']!=ody_sid and odyprobe['first_failure']['reason']=='APPELLATION_NOT_THIS_ACTUAL_LIQUID')
 firstboil=next(sid for sid,i,u in operations if core['unit_functions'][u]=='BOIL_CURRENT_MIXTURE')
 for name,skip in [('DELETE_FIRST_PREPARATION',lambda sid,u:sid==firstboil and core['unit_functions'][u]=='BOIL_CURRENT_MIXTURE'),('DELETE_ALL_PERFORMED_PREPARATIONS',lambda sid,u:core['unit_functions'][u]=='BOIL_CURRENT_MIXTURE')]:
  pr=run_probe(name,skip=skip);check(name+'_does_not_invent_physical_d',pr['first_failure'] is not None and not pr['physical_liquid_exists'])
 def output_swap(st,sid,u):
  if core['unit_functions'][u]=='EXPANDED_CAPTION_DEFINITION':st['use_selected']=copy.deepcopy(st['p'])
 pr=run_probe('SUBSTITUTE_SELECTED_PHYSICAL_OUTPUT_P_AT_WRITTEN_DEFINITION',hook=output_swap)
 check('selected_solid_fails_actual_written_liquid_definition',pr['first_failure'] is not None and pr['first_failure']['reason']=='WRITTEN_OUTPUT_SELECTION_NOT_LIQUID_D')
 definition_index=next(n for n,(sid,i,u) in enumerate(operations) if core['unit_functions'][u]=='EXPANDED_CAPTION_DEFINITION')
 last_selection=next((sid,u) for sid,i,u in reversed(operations[:definition_index]) if core['unit_functions'][u]=='SELECT_LIQUID_FOR_USE')
 def changed_selection_return(step,value):
  if (step['source_ids'],step['unit'])==last_selection and value['type']=='MaterialReference':value.update(physical_id='p',phase='SOLID_PHASE',form='BOILED_SOLID')
 selected_probe=run_probe('CHANGE_ACTUAL_LAST_USE_SELECTION_RETURN_TO_SOLID_P',ret_hook=changed_selection_return)
 check('actual_selection_return_substitution_reaches_liquid_consumer_gate',selected_probe['first_failure'] is not None and selected_probe['first_failure']['reason']=='WRITTEN_OUTPUT_SELECTION_NOT_LIQUID_D')
 def changed_input_source_return(step,value):
  if value['type']=='BotanicalInput':value['source_kind']='K2'
 input_probe=run_probe('CHANGE_ACTUAL_BOTANICAL_INPUT_PRODUCER_SOURCE_TO_K2',ret_hook=changed_input_source_return)
 check('actual_source_producer_change_detected_at_first_written_source_assertion',input_probe['first_failure'] is not None and input_probe['first_failure']['reason']=='CONTRADICTED_BODY_INPUT_SOURCE')
 def source_swap(st,sid,u):
  if core['unit_functions'][u]=='EXPANDED_CAPTION_DEFINITION':st['d']['source_kind']='K2'
 pr=run_probe('SUBSTITUTE_PHYSICAL_OUTPUT_SOURCE_K2_AT_WRITTEN_DEFINITION',hook=source_swap)
 check('changed_source_fails_actual_written_provenance_definition',pr['first_failure'] is not None and pr['first_failure']['reason']=='EXPANDED_DEFINITION_SOURCE_FORM_MISMATCH')
 def denotation_flip(st,sid,u):
  if core['unit_functions'][u]=='EXPANDED_CAPTION_DEFINITION':st['caption_appellation']=copy.deepcopy(st['caption_appellation']);st['caption_appellation']['denotation']='K19'
 pr=run_probe('STRICT_CAPTION_DENOTATION_FLIP_AT_ACTUAL_WRITTEN_REFERENCE',hook=denotation_flip)
 check('strict_flip_actual_reference_exists_and_fixed_definition_rejects',pr['first_failure'] is not None and pr['first_failure']['reason']=='CAPTION_DENOTATION_NOT_MATERIAL_KIND')
 check('two_distinct_consumed_nonseed_functions_reported_only_IT',next(s for s in summary if s['reader']=='IT2a')['nonseed_consumed_caption_functions']==['ody','or'] and all(not s['required_two_functions_reached'] for s in summary if s['reader']!='IT2a'))
 # Directly challenge the claimed common-input/preparation predicate at its first actual site.
 st=ctx['init']('IT2a'); provenance_report=None
 for sid,index,u in operations:
  if core['unit_functions'][u]=='ASSERT_OUTPUT_PROVENANCE':
   st['p']=copy.deepcopy(st['p']);st['p']['source_kind']='K2';st['p']['origin_input']['id']='DIFFERENT_INPUT';st['p']['preparation']['id']='DIFFERENT_PREPARATION'
   try:
    step=ctx['operate'](st,sid,u,index);failure=None
   except ValueError as error:failure=str(error);step=None
   provenance_report={'name':'MISMATCH_SOLID_PROVENANCE_AT_ACTUAL_COMMON_PROVENANCE_ASSERTION','source_ids':sid,'unit':u,'first_failure':{'source_ids':sid,'unit':u,'reason':failure} if failure else None,'mismatched_fields':['p.source_kind','p.origin_input.id','p.preparation.id'],'accepted':failure is None,'returned_predicates':[v['predicate'] for v in step['returns'] if v['type']=='WorldPredicate'] if step else []}
   break
  ctx['operate'](st,sid,u,index)
 probe_reports.append(provenance_report)
 check('strict_common_input_preparation_provenance_predicate_checks_mismatch',provenance_report is not None and not provenance_report['accepted'], 'Frozen ASSERT_OUTPUT_PROVENANCE claims common e/w; actual predicate only checks distinct physical IDs and solid/liquid phases, so the mutated input/source/preparation is accepted.')
 check('all_author_source_freeze_bytes_unchanged_after_replay_probes',all(sha(local(p))==h for p,h in final['files'].items()) and sha(D/'src/SOURCE.json')==final['source_sha256'])
 failures=[c for c in checks if c['status']=='FAIL']
 limits=['Technical preservation/replay and conditional value-flow checks do not prove semantic truth or productive morphology.',
 'Nested-ID consumer metadata overcounts possible field readership; direct OR and ODY return-field probes independently show actual reads at later written groups.',
 'IT76 is operational; three entirely unused reference wholes prevent strict whole completion. RF3/76 and ZL18/78 stop at native unknowns; no state crosses them.',
 'Actual source-producer K2 intervention fails immediately at .1G001 source assertion; separate local physical-output sourceK2 intervention reaches .11G002 definition. The last actual use-selection returned MaterialReference was also independently changed to solid p and failed at definition.',
 'Countercases are independent conditional API interventions at actual sites; narrative author consequences were not themselves executed branches.',
 'Deleting first versus all preparations was checked separately; both stop at actual first missing-liquid view before any later boil can occur.',
 'ASSERT_OUTPUT_PROVENANCE accepts a changed solid source/input/preparation: its actual truth test checks only distinct IDs and phase. Baseline co-provenance construction is consistent, but this claimed identity predicate is not enforced.',
 'Expanded qol compound has two paid primitive predicates; alias atomicity, interpretation plausibility, provenance assertion strength and linguistic justification remain manual.',
 'Wider plant-name plus preparation/definition and one-pair lexical whole rivals remain untested/equivalent, even though the strict fixed flip rejects.',
 'No independent confirmation, medical efficacy, selected meaning or reserve opening.']
 report={'experiment':'GDT1133','status':'TECHNICAL_ACCOUNTING_PASS_WITH_PROVENANCE_PREDICATE_FAILURE' if len(failures)==1 and failures[0]['check']=='strict_common_input_preparation_provenance_predicate_checks_mismatch' else 'FAIL_TECHNICAL_CHECKS' if failures else 'PASS_TECHNICAL_CHECKS_STRICT_ACCOUNT_REMAINS_PARTIAL','semantic_validation':False,'checks':checks,'failed_checks':len(failures),'scope_counts':{'native_rows':len(native),'body_rows':len(native_body),'body_hardchunks':len(srcchunks),'caption_rows':3},'summary':summary,'cost_counts':counts,'conditional_API_probes':probe_reports,'manual_unverified_limits':limits,'expectations_sha256':EXPECTED_SHA,'author_final_receipt_sha256':sha(D/'artifacts/AUTHOR_FINAL_FREEZE_RECEIPT.json'),'validator_sha256':sha(pathlib.Path(__file__))}
 (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 md=['# GDT1133 independent validation','',report['status']+'. Semantic validation: false.','',f'{len(checks)-len(failures)}/{len(checks)} technical checks passed.','',
 'All233 native rows,230 body positions and227 fixed hardchunks are conserved. Initial/final inventory and author pins pass. Released materializer was replayed in memory with only final file-write/print omitted; frozen author artifacts were not rewritten.','',
 'OR .10G002 returned source_kind was changed alone through the existing return API: later .11G001 preparation rejects the mismatch. ODY .11G002 returned form was changed alone: .11G003 Col rejects the actual appellation. These test actual returned fields rather than recursive consumer metadata.','',
 'IT76/76 is operational, with three wholly unused reference expressions; strict account remains PARTIAL. RF3/76 stops at .1G004 d@222; and its caption at os. ZL18/78 stops at .2G010 @241;. All later unknown-dependent groups execute no steps.','',
 'Unknown-ID bookkeeping may grow at additional UNKNOWN groups; all semantic operands remain fixed and no later steps execute. The strict common-provenance predicate challenge fails: changed p input/source/preparation is accepted.','',
 'Actual intervention first failures:','']
 md += ['- '+p['name']+': '+('none' if p['first_failure'] is None else ','.join(p['first_failure']['source_ids'])+' / '+p['first_failure']['unit']+' / '+p['first_failure']['reason']) for p in probe_reports]
 md += ['','Manual/unverified limits:','']+['- '+x for x in limits]
 if failures:md += ['','Failed checks:','']+['- '+x['check'] for x in failures]
 (D/'artifacts/VALIDATOR_REPORT.md').write_text('\n'.join(md)+'\n')
 print(json.dumps({'status':report['status'],'checks':len(checks),'failures':[c['check'] for c in failures]}));return bool(failures)
def read_compressed(p):return json.loads(gzip.decompress(p.read_bytes()))
if __name__=='__main__':raise SystemExit(main())
