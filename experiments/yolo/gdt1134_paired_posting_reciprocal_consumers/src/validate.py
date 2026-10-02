#!/usr/bin/env python3
"""Independent GDT1134 literal/replay/flow checks. Author files are read-only."""
import collections,csv,hashlib,importlib.util,io,json,pathlib,re,subprocess,sys
from copy import deepcopy
sys.dont_write_bytecode=True
D=pathlib.Path(__file__).resolve().parents[1];ROOT=D.parents[2]
EXPECT_SHA='006007f772d4e8acf3738ffcbe191cf8c4ac68a5793532458c396b9c4e40108b'
PLAN_SHA='27fefdabd63438f3260c4d43f5855eed33b8b665c16934178195e4be1ec75419'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def local(p):
 q=pathlib.Path(p)
 if q.is_absolute() or '..' in q.parts:raise ValueError('Unsafe artifact pin')
 return D/q
checks=[]
def check(name,passed,detail=None):
 v={'check':name,'status':'PASS' if passed else 'FAIL'}
 if detail is not None:v['detail']=detail
 checks.append(v)
def load_module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 release=read(D/'artifacts/FINAL_RELEASE.json')
 if not release['independent_review_authorized']:raise ValueError('Root final release required')
 expected=read(D/'artifacts/VALIDATOR_EXPECTATIONS.json');source=read(D/'src/SOURCE.json');core=read(D/'src/CORE.json');ext=read(D/'src/EXTENSIONS.json');account=read(D/'artifacts/AUTHOR_ACCOUNT.json')
 initial=read(D/'artifacts/INITIAL_FREEZE_RECEIPT.json');extension=read(D/'artifacts/EXTENSION_FREEZE_RECEIPT.json');final=read(D/'artifacts/FINAL_FREEZE_RECEIPT.json')
 check('blinded_expectation_bytes',sha(D/'artifacts/VALIDATOR_EXPECTATIONS.json')==EXPECT_SHA and sha(D/'artifacts/VALIDATOR_EXPECTATIONS.md')==PLAN_SHA)
 check('contract_and_all_eight_registered_input_pins',all(sha(local(p))==h for p,h in expected['contract_pins'].items()) and all(sha(ROOT/p)==h for p,h in expected['registered_input_pins'].items()))
 check('root_release_final_receipt_and_all_five_author_pins',sha(D/'artifacts/FINAL_FREEZE_RECEIPT.json')==release['final_receipt_sha256'] and final['files']==release['verified_files'] and all(sha(local(p))==h for p,h in final['files'].items()))
 check('initial_extension_final_freeze_bytes_identity',all(sha(local(p))==h for receipt in [initial,extension] for p,h in receipt['files'].items()) and initial['freeze_utc']==core['freeze_utc']<extension['freeze_utc']<final['freeze_utc'] and not extension['first_completed_derivation_performed'])
 check('source_core_extension_account_identity',sha(D/'src/SOURCE.json')==release['source_sha256']==final['source_sha256']==ext['source_sha256']==account['source_sha256'] and sha(D/'src/CORE.json')==ext['core_sha256']==account['core_sha256'] and sha(D/'src/EXTENSIONS.json')==account['extensions_sha256'])
 command=source['command'];check('guarded_selector_only_three_owned_loci',command.count('--allow')==3 and [command[i+1] for i,x in enumerate(command) if x=='--allow']==['f105v.5','f105v.6','f105v.7'] and command[command.index('--selector')+1]=='locus')
 query=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=True);rows=list(csv.DictReader(io.StringIO(query.stdout),delimiter='\t'))
 check('all90_source_native_rows_11fields_guarded_conservation',rows==source['native_rows'] and len(rows)==90 and len(source['native_columns'])==11 and len({r['source_group_id'] for r in rows})==90)
 for edition in ('IT2a','ZL3b','RF1b'):
  native=[r for r in rows if r['edition']==edition];a=account['accounts'][edition]
  check(edition+'_all30_native_fields_and_boundaries',len(native)==len(a['rows'])==30 and [{k:r[k] for k in source['native_columns']} for r in a['rows']]==native and [sum(r['locus']==l for r in native) for l in ('f105v.5','f105v.6','f105v.7')]==[10,13,7])
 formal=load_module(ROOT/'experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py','gdt1134_frozen_formal')
 merge_rows=list(csv.DictReader((ROOT/source['fixed_merge_path']).open(),delimiter='\t'));merges=[(r['left'],r['right'],r['merged'],int(r['train_occurrences'])) for r in merge_rows]
 fixed={};formal_ok=account['fixed_source_lines']==source['lines'] and [int(r['rank']) for r in merge_rows]==list(range(1,65))
 for line in source['lines']:
  pending=[];reconstructed=[]
  for n in [r for r in rows if r['edition']==line['edition'] and r['locus']==line['locus']]:
   pending.append(n)
   if n['right_separator']=='UNCERTAIN_SMALL_SPACE':continue
   units=list(formal.apply_bpe(formal.collapse(''.join(r['ivtff_group_raw'] for r in pending)),merges)) if all(re.fullmatch('[a-z]+',r['ivtff_group_raw']) for r in pending) else None
   reconstructed.append({'source_ids':[r['source_group_id'] for r in pending],'raw_groups':[r['ivtff_group_raw'] for r in pending],'fixed_units':units,'native_rows':pending});pending=[]
  formal_ok &= not pending and reconstructed==line['chunks']
  for c in line['chunks']:
   for sid in c['source_ids']:fixed[sid]=c['fixed_units']
 check('unchanged605_64merges_all_hardchunks_and_units',formal_ok and all(r['fixed_units']==fixed[r['source_group_id']] for a in account['accounts'].values() for r in a['rows']))
 dictionary={d['raw_form']:d for d in ext['dictionary']}
 occurrence_ok=len(dictionary)==len(ext['dictionary'])
 for raw,d in dictionary.items():
  occurrence_ok &= d['occurrences']==[r['source_group_id'] for r in rows if r['ivtff_group_raw']==raw]
  occurrence_ok &= all(fixed[sid]==d['fixed_representation'] for sid in d['occurrences'])
 check('exact_whole_occurrences_and_frozen_representations',occurrence_ok)
 aliases=collections.defaultdict(list)
 for d in ext['dictionary']:aliases[d['rule']].append(d['raw_form'])
 actual_aliases={rule:set(words) for rule,words in aliases.items() if len(words)>1}
 check('same_rule_aliases_declared_and_priced',actual_aliases=={a['rule']:set(a['words']) for a in ext['aliases']} and all(a['extra_alias_cost']>=1 for a in ext['aliases']))
 costs={'core_primitives':len(core['primitives']),'opaque_constants':len(core['constants']),'whole_entries':len(ext['dictionary']),'whole_assignment_cost':sum(d['cost']['whole_assignment'] for d in ext['dictionary']),'primitive_component_cost':sum(d['cost']['primitive_components'] for d in ext['dictionary']),'formal_residual_cost':sum(d['cost']['fixed_unit_whole_residual_cost'] for d in ext['dictionary']),'extra_syntax_rules':len(ext['extra_grammar_rules']),'reference_default_cost':sum(x['cost'] for x in ext['reference_defaults']),'alias_cost':sum(x['extra_alias_cost'] for x in ext['aliases']),'background_entries':len(ext['background_world_inputs'])}
 check('account_cost_inventory_exact_frozen_extensions',account['cost_inventory']==ext and ext['additional_primitive_families']==0 and len(core['primitives'])==12 and len(core['constants'])==ext['constants_introduction_cost']==7 and len(ext['dictionary'])==28)
 helper=load_module(D/'src/author_helper.py','gdt1134_released_helper')
 evaluate=lambda edition='IT2a',world=None,change=None:helper.evaluate([r for r in rows if r['edition']==edition],fixed,dictionary,deepcopy(world) if world is not None else helper.world(),deepcopy(change))
 check('all_three_deterministic_account_replays_exact',all(evaluate(edition)==a for edition,a in account['accounts'].items()))
 first_barriers={};whole_contribution={}
 for edition,a in account['accounts'].items():
  bad=next((r for r in a['rows'] if r['errors']),None);first_barriers[edition]=bad['source_group_id'] if bad else None
  after=False;honest=True
  for r in a['rows']:
   if after:honest &= r['status'] in ('UNEXECUTED_AFTER_BARRIER','UNKNOWN_UNEXECUTED') and not r['arguments'] and not r['returns']
   if r['errors']:after=True
  check(edition+'_first_barrier_and_exact_unexecuted_tail',a['first_barrier']==first_barriers[edition] and honest)
  live={r['source_group_id'] for r in a['rows'] if any(a['objects'][oid]['type']=='Proposition' for oid in r['returns'])};edges={(ar['from_return_source_id'],r['source_group_id']) for r in a['rows'] for ar in r['arguments'] if ar['from_return_source_id']!=r['source_group_id']}
  def closure(terminals,graph):
   reached=set(terminals)
   while True:
    before=len(reached);reached|={s for s,t in graph if t in reached}
    if len(reached)==before:return reached
  reached=closure(live,edges);dead=[r['source_group_id'] for r in a['rows'] if r['status']=='ACCOUNTED' and r['source_group_id'] not in reached]
  removed_edge={e for e in edges if e!=('IT2a|f105v.6|G003','IT2a|f105v.7|G002')};without=closure(live,removed_edge)
  whole_contribution[edition]={'terminal_assertion_sources':sorted(live),'transitively_dead_operational_groups':dead,'dead_without_extra_lkaiin_certificate_dependency':[r['source_group_id'] for r in a['rows'] if r['status']=='ACCOUNTED' and r['source_group_id'] not in without]}
 check('IT_actual_graph_all30_contribute_to_real_terminal_assertions',not whole_contribution['IT2a']['transitively_dead_operational_groups'])
 it=account['accounts']['IT2a'];marks=[o for o in it['objects'].values() if o['type']=='JournalMark'];counters=[o for o in it['objects'].values() if o['type']=='CounterResult'];read_objects=[o for o in it['objects'].values() if o['type']=='MarkRead']
 check('two_distinct_marks_same_frozen_function_owners_T',len(marks)==2 and len({m['id'] for m in marks})==2 and {m['value']['owner'] for m in marks}=={'A','B'} and all(m['value']['transaction']=='T' for m in marks) and dictionary['daiin']['rule']=='MARK')
 check('two_COUNTER_same_function_actual_right_role_mark_bindings',len(counters)==2 and dictionary['dar']['rule']=='COUNTER_PREFIX' and all(c['value']['source_role']!=c['value']['returned_role'] and c['value']['transaction']=='T' and c['actual_object_links']['origin_mark'] in {m['id'] for m in marks} for c in counters) and {c['value']['source_role'] for c in counters}=={'A','B'})
 check('both_late_reads_use_actual_counterreturn_owner_mark_and_T',len(read_objects)==2 and all(r['value']['counter_result_id'] in {c['id'] for c in counters} and r['value']['mark_id'] in {m['id'] for m in marks} and r['value']['transaction']=='T' and next(c for c in counters if c['id']==r['value']['counter_result_id'])['value']['returned_role']==r['value']['owner'] for r in read_objects))
 fixture_specs=[('FALSE_FIRST_MARK',{'false_mark':1}),('FALSE_LAST_MARK',{'false_mark':2}),('REMOVE_FIRST_MARK',{'remove_mark':1}),('REMOVE_LAST_MARK',{'remove_mark':2}),('UNRELATED_SAME_VALUE_SELECTOR',{'unrelated_selector':True}),('PARTIAL_SELECTOR_SWAP',{'swap_first_selector':True}),('WRONG_RETURNED_OWNER',{'wrong_counter':1,'wrong_kind':'owner'}),('WRONG_RETURNED_TRANSACTION',{'wrong_counter':1,'wrong_kind':'transaction'}),('COMMON_DONE_FALSE_FIRST',{'status_representation':'shared_DONE','false_mark':1}),('COMMON_SCALAR',{'status_representation':'shared_SCALAR'})]
 actual_fixtures=[];outputs={}
 for name,change in fixture_specs:
  out=evaluate(change=change);outputs[name]=out
  actual_fixtures.append({'name':name,'engineering_or_declared_counterfactual_only':True,'status':out['status'],'first_barrier':out['first_barrier'],'read_values':out['read_values'],'terminal':out['terminal'],'failed_row':next((r for r in out['rows'] if r['errors']),None),'entry_count':out['final_entry_count']})
 for ordinal in (0,1):
  w=helper.world();deleted=w['entries'].pop(ordinal);out=evaluate(world=w);name='DELETE_ACTUAL_LEDGER_ENTRY_'+str(ordinal+1);outputs[name]=out
  actual_fixtures.append({'name':name,'question':'Declarative certificate-dependency failure; no physical posting event was performed.','deleted_background_record':deleted,'status':out['status'],'first_barrier':out['first_barrier'],'failed_row':next(r for r in out['rows'] if r['errors']),'entry_count':out['final_entry_count'],'ledger_entry_invented':False})
 swapped=evaluate(world=helper.world(('B','A')));outputs['GLOBAL_ROLE_LABEL_RENAMING']=swapped
 actual_fixtures.append({'name':'GLOBAL_ROLE_LABEL_RENAMING','status':swapped['status'],'read_values':swapped['read_values'],'terminal':swapped['terminal'],'interpretation':'All role identities, entries and labels renamed consistently; no cardinal orientation selected.'})
 check('all13_actual_intervention_outcomes_replayed_exact',actual_fixtures==account['counterfactuals'])
 vals=lambda name:[r['recorded_completed'] for r in outputs[name]['read_values']]
 check('both_mark_changes_reach_late_read_only_dependent_side_changes',vals('FALSE_FIRST_MARK')==[True,False] and vals('FALSE_LAST_MARK')==[False,True] and all(outputs[n]['read_values'][i]['mark_id']==it['read_values'][i]['mark_id'] for n in ('FALSE_FIRST_MARK','FALSE_LAST_MARK') for i in (0,1)))
 check('early_wrong_counter_owner_T_probes_honestly_stop_before_READ',all(outputs[n]['first_barrier']=='IT2a|f105v.6|G009' and not outputs[n]['read_values'] for n in ('WRONG_RETURNED_OWNER','WRONG_RETURNED_TRANSACTION')))
 check('declarative_entry_deletion_never_creates_entries',all(outputs['DELETE_ACTUAL_LEDGER_ENTRY_'+str(i)]['final_entry_count']==1 and outputs['DELETE_ACTUAL_LEDGER_ENTRY_'+str(i)]['no_ledger_entries_created'] and not outputs['DELETE_ACTUAL_LEDGER_ENTRY_'+str(i)]['read_values'] for i in (1,2)) and not account['physical_ledger_posting_performed'])
 check('strict_DONE_loses_mixed_side_status_and_scalar_interface_missing',vals('COMMON_DONE_FALSE_FIRST')==[False,False] and vals('COMMON_SCALAR')==['V','V'] and outputs['COMMON_SCALAR']['first_barrier']=='IT2a|f105v.7|G002' and any('MISSING_SCALAR_TO_COMPLETION_FUNCTION' in r['errors'] for r in outputs['COMMON_SCALAR']['rows']))
 # Observe the released evaluator's actual local objects, without altering its bytes or code.
 lines=(D/'src/author_helper.py').read_text().splitlines();read_line=next(i for i,s in enumerate(lines,1) if 'counter_obj = arg(row, need("projected_counter"))' in s);mark_line=next(i for i,s in enumerate(lines,1) if 'field = arg(row, need("field"))' in s)
 read_sids=[r['source_group_id'] for r in it['rows'] if dictionary[r['ivtff_group_raw']]['rule']=='READ_RETURNED_MARK'];probes=[]
 def instrumented(site,line,mutate):
  changed=[]
  def tracer(frame,event,arg):
   if event=='line' and frame.f_code is helper.evaluate.__code__ and frame.f_lineno==line and frame.f_locals.get('row',{}).get('source_group_id')==site and not changed:
    mutate(frame.f_locals);changed.append(site)
   return tracer
  prior=sys.gettrace();sys.settrace(tracer)
  try:out=evaluate()
  finally:sys.settrace(prior)
  return out,changed
 for index,sid in enumerate(read_sids):
  def swap_return(locals):
   ctx=locals['ctx'];obj=ctx['projected_counter'][0];f=ctx['frame'][0];obj['returned_role']=next(r for r in f['roles'] if r is not obj['returned_role']);obj['value']['returned_role']=obj['returned_role']['value']['label']
  out,changed=instrumented(sid,read_line,swap_return)
  observable=bool(changed) and out['read_values'][index]['owner']!=it['read_values'][index]['owner'] and out['read_values'][index]['mark_id']!=it['read_values'][index]['mark_id'] and out['read_values'][1-index]==it['read_values'][1-index]
  check('late_READ_'+str(index+1)+'_actually_uses_changed_returned_account',observable)
  probes.append({'name':'CHANGE_RETURNED_ROLE_AT_LATE_READ_'+str(index+1),'site':sid,'first_barrier':out['first_barrier'],'read_values':out['read_values'],'mutation_reached':bool(changed)})
  def wrong_T(locals):
   obj=locals['ctx']['projected_counter'][0];obj['transaction']={'id':'unrelated-T2','value':{'transaction':'T2'}};obj['value']['transaction']='T2'
  out,changed=instrumented(sid,read_line,wrong_T)
  check('late_READ_'+str(index+1)+'_actually_checks_returned_T',bool(changed) and out['first_barrier']==sid and any('READ_COUNTER_TRANSACTION_MISMATCH' in r['errors'] for r in out['rows']))
  probes.append({'name':'CHANGE_RETURNED_T_AT_LATE_READ_'+str(index+1),'site':sid,'first_barrier':out['first_barrier'],'read_values':out['read_values'],'mutation_reached':bool(changed)})
 mark_sid=next(r['source_group_id'] for r in it['rows'] if dictionary[r['ivtff_group_raw']]['rule']=='MARK')
 stale_acceptances=[]
 for field,mutated_value in [('role','X'),('value','OTHER_VALUE'),('date','OTHER_DATE'),('ledger','OTHER_LEDGER')]:
  def stale_certificate(locals):locals['ctx']['field'][0]['certificate']['entry'][field]=mutated_value
  stale,changed=instrumented(mark_sid,mark_line,stale_certificate)
  stale_row=next(r for r in stale['rows'] if r['source_group_id']==mark_sid)
  stale_accepted=bool(changed) and stale_row['status']=='ACCOUNTED' and any(stale['objects'][oid]['type']=='JournalMark' for oid in stale_row['returns'])
  stale_acceptances.append(stale_accepted)
  probes.append({'name':'POST_RELEASE_DIAGNOSTIC_MUTATE_'+field.upper()+'_AFTER_CERTIFICATION','site':mark_sid,'mark_accepted':stale_accepted,'first_barrier':stale['first_barrier'],'entry_field_changed':field,'mutated_value':mutated_value,'terminal_truth':stale['terminal']['value']['truth'] if stale['terminal'] else None,'naturally_arose_in_baseline':False})
 check('strict_MARK_dynamic_role_value_date_ledger_revalidation_diagnostic',not any(stale_acceptances),'Post-release diagnostic only: separately injected external entry mutations after valid certification are accepted by MARK. All preregistered initial-world entry deletions pass; unchanged baseline remains consistent. This is absent dynamic metadata revalidation, not a preregistered whole-world contradiction.')
 for probe in probes:probe['post_release_diagnostic']=True
 actual_extra=next(r for r in it['rows'] if r['ivtff_group_raw']=='lkaiin');cert_arg=any(a['from_return_source_id']=='IT2a|f105v.6|G003' for a in actual_extra['arguments'])
 check('all_actual_lkaiin_certificate_dependencies_individually_frozen_and_priced',not cert_arg,'Code CHECK_READ_PAIR additionally reads latest cert_props collection. Frozen lkaiin meaning/defaults do not individually declare this edge; without it ckheey collection is dead.')
 check('frozen_extension_counter_policy_late_READ_claim_matches_actual13_cases',not any('must reach READ' in c for c in ext['counterfactuals']) or all(outputs[n]['first_barrier'] in read_sids for n in ('WRONG_RETURNED_OWNER','WRONG_RETURNED_TRANSACTION')),'EXTENSIONS says wrong Counter owner/T must reach READ; actual frozen probes stop at earlier .6G009 pair check. Honest account disclosure retained; do not invent late execution.')
 check('public_GO_metadata_literal_matches_actual_public_commit',ext['public_go_commit']==account['public_registration']['public_commit'],'Frozen EXTENSIONS public_go_commit has source-hash suffix; separate public registration is valid and disclosed.')
 check('source_and_all_frozen_author_bytes_unchanged_after_validation',sha(D/'src/SOURCE.json')==release['source_sha256'] and all(sha(local(p))==h for p,h in final['files'].items()))
 failures=[c for c in checks if c['status']=='FAIL'];limits=['Conservation/replay/argument sensitivity are technical behavior, not semantic truth or productive morphology.',
 'IT complete operational graph uses an extra code-visible latest certificate-collection dependency at lkaiin not individually priced in the frozen meaning/defaults; strict frozen completeness is not certified.',
 'Late READ tracing and post-certificate mutation are post-release diagnostics, separate from the original13 frozen intervention fixtures.',
 'Wrong returned owner/T registered fixtures stop at the earlier written counter-pair check. Separate midstream late-READ instrumentation tests actual account/T operand use without claiming those fixtures reached READ.',
 'Post-release diagnostic externally mutates role/value/date/ledger one field at a time after valid certification; MARK accepts all four. Baseline is consistent and all initial-world deletion fixtures pass. This demonstrates absent dynamic metadata revalidation, not naturally occurring mutation or a preregistered whole-world contradiction.',
 'Strict DONE loses independent mixed recorded status; scalar branch lacks a scalar-to-completion interface. Neither excludes numerical coding with separately paid role/status relations or copied reference implementation.',
 'A/B global renaming remains equivalent; equal V/D do not identify unrelated accounts or settlement.',
 'Terminal propositions and redundant assertions count as stipulated C0 content, not independent observations. Primitive atomicity and interpretation plausibility remain manual.',
 'One exposed leaf, zero confirmed meanings/independent confirmation, no physical Ledger posting, no payment/stock/settlement or reserve claim.']
 report={'experiment':'GDT1134','status':'REPLAY_AND_FLOW_PASS_WITH_PRESERVED_FROZEN_CONTRACT_LIMITS','semantic_validation':False,'strict_frozen_complete_certified':False,'checks':checks,'failed_checks':len(failures),'computed_cost_counts':costs,'first_barriers':first_barriers,'whole_contribution':whole_contribution,'thirteen_intervention_outcomes':[{k:v for k,v in f.items() if k not in ('failed_row','terminal')} for f in actual_fixtures],'independent_midstream_probes':probes,'manual_unverified_limits':limits,'expected_sha256':EXPECT_SHA,'validator_sha256':sha(pathlib.Path(__file__)),'final_receipt_sha256':sha(D/'artifacts/FINAL_FREEZE_RECEIPT.json')}
 (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
 text=['# GDT1134 independent validation','',report['status']+'. Semantic validation: false; strict frozen completeness is not certified.','',f'{len(checks)-len(failures)}/{len(checks)} checks passed; {len(failures)} preserved failures.','',
 'All90 native rows/11 columns and all fixed representations are conserved. All five final author pins, source pin and initial/extension receipts pass. All three account replays and13 intervention outputs match exactly, without author writes.','',
 'Both MARK owners and both COUNTER returns retain T and reach actual late mark reads. In separate post-release diagnostics, changing only the actual projected return at each late READ changes its mark owner/ID; changing only its T fails that READ. Single-mark changes affect only the dependent read. Registered wrong owner/T fixtures instead stop earlier at .6G009; they are not late READ evidence.','',
 'Separate post-release diagnostic role/value/date/ledger mutations after valid certification are each accepted by MARK. No such mutation arose in the unchanged baseline; all original pre-certification entry-deletion worlds pass. This is a dynamic-revalidation limit, not a preregistered whole-world contradiction.','',
 'IT operational graph has no dead whole when code-visible lkaiin certificate edge is included. That edge is not individually specified/priced in frozen meaning/defaults; removing it makes .6G003 ckheey collection dead. ZL/RF first unknown is .5G008, and every subsequent row is unexecuted.','',
 'Preserved failed checks:','']+['- '+c['check']+': '+c.get('detail','') for c in failures]+['','Manual/unverified limits:','']+['- '+x for x in limits]
 (D/'artifacts/VALIDATION_REPORT.md').write_text('\n'.join(text)+'\n')
 print(json.dumps({'status':report['status'],'checks':len(checks),'failures':[c['check'] for c in failures]}));return bool(failures)
if __name__=='__main__':raise SystemExit(main())
