#!/usr/bin/env python3
"""Independent GDT1137 frozen-plan review using released APIs; no author writes.
Pins/account conservation, repeat inventories, meaningful part/return probes.
No decoder, type theorem prover, physical solver or scientific meaning PASS.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import hashlib,json,sys,types
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1]
ART=BASE/'artifacts'
PINS={
'METHOD.md':'57d23dec78afc859f039fa7a5118842b235be55080e4768678b2a85dd3659b35',
'PREREGISTRATION.md':'57d23dec78afc859f039fa7a5118842b235be55080e4768678b2a85dd3659b35',
'artifacts/NATIVE_SOURCE.json':'40fab9cdfced7433f9b250d811bdcc654b3e5c17370eeb43d156f9bc474d6b2d',
'artifacts/WORD_PRIORS.json':'7f25081cdd2178d2c8fa2a38159ab83a39f5f8789f065f8503e7b19eb50813d8',
'artifacts/VALIDATION_PLAN.md':'d193c280be97c416575fcbda12b9698e4ba4f0202753b552b638d710e9e1098d',
'src/core.py':'592e070b934c54ff7e5965ed7a4ee1cd6789b14cd4d59de216a40d229e54ec02',
'src/CORE_FREEZE.json':'b59b793c6a5e7c811e70cfb5c6af5a8b186598858d219a95295931cf6bd74cb0',
'src/author.py':'7cc3c8c1562cfc1e5440f7e4ca0bf5e13dcaa3bb341e52388660af4896c10c96',
'artifacts/AUTHOR_ACCOUNT.json':'77a12a678693e5630bd4506d5c59419917507a58373a2913615a9298137e6785',
'AUTHOR_READING.md':'2f7bc029c318ddbcd12b5fb264d41ca25515b30a8c43fda636665902c4333eff',
'AUTHOR_RECEIPT.json':'84e93e3230ba6621a391b005f1eee678ee96f50105ed80229f0ce4cf9c6f26b8'}
FIRST='IT2a|f83r.25|G004';SECOND='IT2a|f83r.28|G004'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def summary(execution):
 sel=execution['selection']
 return {'first_failure':execution['first_failure'],'complete':execution['complete_connected_primary'],
 'selected_producer':sel['selected_type']['producer_id'] if sel else None,
 'written_type_matches':sel['written_type_matches'] if sel else None,
 'late_source_assertion':execution['late_source_assertion'],'further_prescription':execution['further_prescription'],
 'row_statuses':[{'ID':r['source_group_id'],'status':r['status']} for r in execution['contributions']],
 'first_failure_detail':next((r['contribution'] for r in execution['contributions'] if r['status']=='first-failure'),None)}
def main():
 before={p:sha(BASE/p) for p in PINS};checks={'frozen_pins':all(before[p]==v for p,v in PINS.items())}
 if not checks['frozen_pins']:raise SystemExit('Pinned input failure: no author execution')
 native=load(ART/'NATIVE_SOURCE.json');account=load(ART/'AUTHOR_ACCOUNT.json');receipt=load(BASE/'AUTHOR_RECEIPT.json');freeze=load(BASE/'src/CORE_FREEZE.json');ack=load(ART/'ROOT_CORE_ACK.json')
 core=types.ModuleType('core');core.__file__=str(BASE/'src/core.py');exec(compile((BASE/'src/core.py').read_text(),core.__file__,'exec'),core.__dict__)
 ns={'__file__':str(BASE/'src/author.py'),'__name__':'independent_review'}
 with patch.dict(sys.modules,{'core':core}):exec(compile((BASE/'src/author.py').read_text(),ns['__file__'],'exec'),ns)
 generated=ns['build_account']();replay_bytes=(json.dumps(generated,ensure_ascii=False,indent=2)+'\n').encode();checks['account_replay_byte_identical']=hashlib.sha256(replay_bytes).hexdigest()==before['artifacts/AUTHOR_ACCOUNT.json']
 rows=native['rows'];reported=account['native_source']['rows'];counts=Counter(r['edition'] for r in rows);ids=[r['source_group_id'] for r in rows];field_diffs=[]
 reported_map={r['source_group_id']:r for r in reported}
 for r in rows:
  for field in r:
   if field not in reported_map.get(r['source_group_id'],{}) or reported_map[r['source_group_id']][field]!=r[field]:field_diffs.append({'ID':r['source_group_id'],'field':field})
 checks['native_source_object_exact']=account['native_source']==native
 checks['all97_native_fields_IDs']=len(rows)==len(reported)==len(set(ids))==97 and not field_diffs and set(ids)==set(reported_map)
 checks['reader_counts']=dict(counts)=={'ZL3b':33,'IT2a':32,'RF1b':32}
 order={e:[r['source_group_id'] for r in rows if r['edition']==e]==[r['source_group_id'] for r in reported if r['edition']==e] for e in counts};checks['per_reader_order']=all(order.values())
 primary=[r for r in rows if r['edition']=='IT2a'];baseline=generated['execution'];rival=generated['same_lexicon_latest_only'];cs=baseline['contributions'];lex=account['lexicon']
 checks['all32_primary_order_contributions']=len(cs)==32 and [c['source_group_id'] for c in cs]==[r['source_group_id'] for r in primary] and all(c['status']=='contributes' and c['contribution'] for c in cs)
 checks['exact23_whole_types']=set(lex)=={r['ivtff_group_raw'] for r in primary} and len(lex)==23
 checks['assemblies_no_repair']=all(''.join(v['parts'])==k for k,v in lex.items())
 checks['repeat_rule_identity']=all(c['raw']==r['ivtff_group_raw'] and c['lexical_rule']==lex[c['raw']] for c,r in zip(cs,primary))
 checks['core_receipt_pins']=freeze['core_sha256']==ack['core_sha256']==before['src/core.py'] and ack['freeze_sha256']==before['src/CORE_FREEZE.json']
 checks['final_receipt_pins']=all(sha(BASE/p)==v for p,v in receipt['pins_excluding_self'].items()) and all(sha(BASE/p)==v for p,v in account['input_pins'].items())
 checks['nominal_core_freeze_assemblies']=all(''.join(parts)==word for word,parts in freeze['literal_assemblies'].items())
 checks['core_declared_functions_present']=all(callable(getattr(core,name,None)) for name in ['nominal','lexical_nominal','qokedy','sol','source_predicate','qody'])
 nominal_base={w:core.lexical_nominal(w) for w in core.LICENSES};part_probes=[]
 for root in core.MATERIALS:
  materials=deepcopy(core.MATERIALS);materials[root]={'kind':'reviewer_'+root,'form':'reviewer_form_'+root}
  result={w:core.lexical_nominal(w,materials=materials) for w in core.LICENSES}
  changed=[w for w in result if result[w]!=nominal_base[w]]
  part_probes.append({'part':'material_'+root,'only_expected_two_forms_change':set(changed)=={root+'ey',root+'dy'},'nominal_outputs':result,
  'product_type_output':core.qokedy(result[root+'dy'],'reviewer_producer')})
 for state in core.STATES:
  states=deepcopy(core.STATES);states[state]['operations']=['reviewer_'+state];states[state]['stage']='reviewer_'+state
  result={w:core.lexical_nominal(w,states=states) for w in core.LICENSES}
  part_probes.append({'part':'state_'+state,'only_expected_two_forms_change':{w for w in result if result[w]!=nominal_base[w]}=={'che'+state,'she'+state},'nominal_outputs':result})
 checks['shared_parts_actual_output_sensitivity']=all(p['only_expected_two_forms_change'] for p in part_probes)
 changed_states=deepcopy(core.STATES);changed_states['dy']['operations']=['reviewer_conversion']
 process_run=ns['execute'](states=changed_states)
 checks['one_shared_process_value_reaches_both_types_and_qody']=process_run['first_failure'] is None and all(t['operations']==['reviewer_conversion'] for t in process_run['generated_types']) and process_run['further_prescription']['operations']==['reviewer_conversion','dry-set']
 q_calls=[];original_q=core.qokedy
 def record_q(recipe,producer_id):
  value=original_q(recipe,producer_id);q_calls.append({'producer':producer_id,'recipe':deepcopy(recipe),'result':deepcopy(value)});return value
 with patch.object(core,'qokedy',record_q):ns['execute']()
 checks['same_qokedy_two_actual_calls']=len(q_calls)==2 and [c['producer'] for c in q_calls]==[FIRST,SECOND] and all(c['result']['material']==c['recipe']['material'] and c['result']['operations']==c['recipe']['operations'] and c['result']['genealogy']['source_material']==c['recipe']['material'] and c['result']['genealogy']['recipe_operations']==c['recipe']['operations'] for c in q_calls)
 sol_alias=[];original_sol=core.sol
 def record_sol(types_,embedded,policy):
  selection=original_sol(types_,embedded,policy);sol_alias.append(selection['selected_type'] is types_[0]);return selection
 with patch.object(core,'sol',record_sol):ns['execute']()
 checks['selector_is_actual_earlier_object']=sol_alias==[True]
 producer_probes=[]
 for sid in [FIRST,SECOND]:
  for field,change in [('material',{'material':{'kind':'reviewer_changed'}}),('operations',{'operations':['reviewer_changed']})]:
   result=ns['execute'](producer_overrides={sid:change});producer_probes.append({'site':sid,'field':field,'stage':'immediately_after_producer','actual':summary(result)})
 return_probes=[]
 for field,change in [('material',{'material':{'kind':'reviewer_changed'}}),('operations',{'operations':['reviewer_changed']})]:
  result=ns['execute'](return_overrides={FIRST:change});return_probes.append({'site':FIRST,'field':field,'stage':'before_selection_after_other_type','actual':summary(result)})
 checks['early_producer_field_rejections']=all(p['actual']['first_failure']==(p['site'] if p['field']=='material' else p['site'].replace('G004','G005')) for p in producer_probes)
 checks['earlier_return_material_and_process_actual_selector_gate']=all(p['actual']['first_failure']=='IT2a|f83r.29|G001' for p in return_probes)
 late_probes=[]
 for field,change in [('operations',{'operations':['reviewer_late_operation']}),('material',{'material':{'kind':'reviewer_late_material'}})]:
  def altered_selection(types_,embedded,policy,change=change):
   selection=original_sol(types_,embedded,policy);ns['merge_fields'](selection['selected_type'],change);return selection
  with patch.object(core,'sol',altered_selection):result=ns['execute']()
  late_probes.append({'field':field,'stage':'post_selection_actual_selected_return','actual':summary(result)})
 checks['late_consumer_actual_process_payload']=late_probes[0]['actual']['first_failure'] is None and late_probes[0]['actual']['further_prescription']['operations']==['reviewer_late_operation','dry-set']
 checks['late_consumer_actual_material_gate']=late_probes[1]['actual']['first_failure']=='IT2a|f83r.29|G002' and late_probes[1]['actual']['late_source_assertion']['satisfied'] is False and late_probes[1]['actual']['further_prescription'] is None
 audit_run=ns['execute'](return_overrides={FIRST:{'genealogy':{'source_material':{'kind':'reviewer_audit_only'}}}})
 checks['irrelevant_genealogy_metadata_not_counted']=audit_run['first_failure'] is None and audit_run['further_prescription']==baseline['further_prescription'] and audit_run['late_source_assertion']==baseline['late_source_assertion']
 checks['fixed_rival_actual_first_failure']=rival['selection']['selected_type']['producer_id']==SECOND and rival['selection']['written_type_matches'] is False and rival['first_failure']=='IT2a|f83r.29|G002' and rival['further_prescription'] is None and all(c['status']=='not-reached-after-first-failure' for c in rival['contributions'][25:])
 inventory=account['cost_inventory'];recounts={'material_kind_primitives':len(core.MATERIALS),'nominal_state_primitives':len(core.STATES),'core_operator_senses':3,'core_source_predication_rule':1,'extension_primitive_senses':len(inventory['extension_primitive_senses']),'whole_residual_count':sum(bool(v.get('whole_residual')) for v in ns['EXTENSION'].values()),'distinct_primary_lexical_rules':len(lex),'literal_assemblies':sum(len(v['parts'])>1 for v in lex.values()),'source_aligned_bindings':len(ns['BINDINGS']),'reference_policies':len(freeze['rival_policies']),'scope_default_count':len(inventory['scope_defaults']),'aliases':len(inventory['aliases']),'overloads':len(inventory['overloads'])}
 checks['declared_inventory_counts']=all((len(inventory[k]) if isinstance(inventory[k],(dict,list)) else inventory[k])==v for k,v in recounts.items())
 checks['residual_inventory_exact']=sorted(inventory['extension_whole_residuals'])==sorted(w for w,v in ns['EXTENSION'].items() if v.get('whole_residual'))
 frozen_after={p:sha(BASE/p)==v for p,v in before.items()};checks['all_frozen_bytes_unchanged']=all(frozen_after.values())
 alternatives=[]
 for ed in ['ZL3b','RF1b']:
  edrows=[r for r in rows if r['edition']==ed]
  alternatives.append({'edition':ed,'rows':len(edrows),'full_semantic_account_authored':False,'unlicensed_exact_forms':[{'ID':r['source_group_id'],'raw':r['ivtff_group_raw']} for r in edrows if r['ivtff_group_raw'] not in lex],'meaning_limit':'Exact licensed form elsewhere does not supply this alternate clause binding; e.g. RF terminal SAIIN cannot inherit IT SAIRN closure.'})
 ledger=[{'ID':c['source_group_id'],'raw':c['raw'],'status':c['status'],'binding':c['binding'],'contribution':c['contribution']} for c in cs]
 out={'status':'FOCAL_COMPUTATION_AND_TYPE_RETURN_PASS_COMPLETE_IT32_AUTHORED_SEMANTIC_TRUTH_UNVERIFIED','meaning_confirmed':False,'scientific_PASS':False,'validator_sha256':sha(Path(__file__)),'frozen_plan_sha256':before['artifacts/VALIDATION_PLAN.md'],'checks':checks,'frozen_hashes':before,'frozen_bytes_unchanged':frozen_after,
 'native_preservation':{'rows':97,'counts':dict(counts),'fields_per_row':len(rows[0]),'field_differences':field_diffs,'per_reader_order':order,'global_order_same':reported==rows,'boundary_limit':'Inherited complete ZL paragraph, aligned IT/RF window; IT end and RF both flags absent'},
 'replay':{'account_byte_identical':checks['account_replay_byte_identical'],'account_sha256':hashlib.sha256(replay_bytes).hexdigest(),'reading_and_receipt':'Manually authored/pin verified; no separate deterministic generator supplied for these'},
 'core_freeze':{'code_hash':before['src/core.py'],'freeze_hash':before['src/CORE_FREEZE.json'],'root_ack_matches':checks['core_receipt_pins'],'chronology':'Documented core acknowledgment precedes extension; receipts alone are not independent secrecy or external chronology proof'},
 'computed_part_probes':part_probes,'shared_process_whole_run':summary(process_run),'qokedy_actual_calls':q_calls,'producer_interventions':producer_probes,'returned_type_interventions':return_probes,'late_selected_return_interventions':late_probes,
 'intervention_status':'Post-release read-only runtime diagnostics of frozen dependencies; first failures preserved. No source worlds, author repair or semantic evidence.',
 'audit_only_control':{'genealogy_copy_changed_late_semantic_outputs_unchanged':checks['irrelevant_genealogy_metadata_not_counted'],'limit':'Consumers read primary material and operations, not every duplicated genealogy/audit field'},
 'fixed_policy_consequences':{'earlier':summary(baseline),'latest':summary(rival),'limit':'Latest conflicts with frozen embedded restriction and late source assertion; no assertion of physical inability to dry-set sheet material'},
 'cost_inventory_recount':recounts,'cost_limit':'Defined declaration counts, not minimum description length or calibrated semantic economy; extension English/scope freedom remains unmeasured',
 'alternate_reader_statuses':alternatives,'all_primary_contributions':ledger,
 'criteria':{'1':'PASS pins/native97 fields and order; all alternate raw uncertainty retained','2':'PASS unchanged early focal core/receipts; independent secrecy unverified','3':'PASS actual common material/state nominal formation and literal local licenses','4':'PASS both material/state output probes; same-function operation value flows','5':'PASS two actual QOKEDY calls carrying material/process genealogy','6':'PASS explicit type/recipe/prescription ontology; physical/whole semantic truth UNVERIFIED','7':'PASS actual earlier-object selection and later material gate/process consumer; producer-only changes may reject earlier than late consumers','8':'PASS IT32 finite contributions; alternate full semantics PARTIAL/not authored','9':'PASS exact same-value policy consequence; latest stops .29G002, tail unexecuted','10':'PASS declared counts/repeat identities; broad semantic freedom disclosed','11':'PASS byte-identical account replay and frozen bytes unchanged','12':'PASS C0/scoped duty ceiling;0 confirmed meanings/no source selection'},
 'interpretive_limits':['This is a finite manually attached type/prescription program, not an independently inferred parser or morphology.','Four local nominal forms share a constructor;11 extension words remain whole residuals and32 bindings are paid choices.',
 'The first-source criterion and early second recipe are initialized before the row loop; later QOLCHEY/OTCHEY returns do not literally supply that seed. This does not replace the actual required TYPE return, but a claim that all32 word payloads form one causal pipeline would overstate the code.','Both recipe types carry the same dy operation; shared enclosure conditions are emitted attachments, not an execution/feasibility test of historical processing.','The exact SOL restriction and later CHEEY assertion partly repeat the same paid powder-material choice; their computation is real but not independent evidence.','The borrowed historical source relation motivates the question; no metal, mechanism, actual batch identity, source identification, independent meaning anchor or full IDEA876 label/prose transfer is established.','Whole physical/logical satisfiability and truth of English requirements are not independently proved. Nominal descriptions before type generation are expressly allowed.']}
 (ART/'VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 md=['# GDT1137 independent validation','', '**Actual focal composition and returned-type consumption pass. All32 primary positions contribute; manuscript meaning and whole physical/semantic truth remain unverified.**','',
 'The frozen source and author/core receipts match. All97 native rows preserve all19 fields and source order (ZL33/IT32/RF32), including literal uncertainty and native boundary flags. This is the inherited ZL paragraph with aligned IT/RF windows, not independent IT/RF paragraph closure. Account replay is byte-identical; no author/core/input/plan bytes changed. Reading and receipt are pin-verified manual artifacts, not claimed regenerated outputs.','',
 'One shared nominal function computes material, stage, operations and prepared form for CHEEY/CHEDY and SHEEY/SHEDY. Material changes affect both states of the selected root and leave the other root unchanged; state changes affect that state for both roots. One changed DY operation propagates through both actual QOKEDY returns and later QODY. Two instrumented calls verify the same QOKEDY function reads each supplied recipe and derives material/process genealogy. Literal licenses include CHE+EY/DY and SHE+EY/DY; CHEY remains CHE+Y without donated E.','',
 'SOL returns the actual earlier generated object, with material and process fields tested against the embedded CHEDY recipe. Immediately altering a producer material causes its source-agreement rejection at .25G004/.28G004; altering its process causes nominal-description rejection at .25G005/.28G005. Altering the earlier actual returned material/process immediately before selection rejects at .29G001. These are the real first failures: those probes do not reach late CHEEY or QODY.','',
 'Separate read-only post-selection instrumentation changes that actual selected object while later code and lexical expectations stay fixed. Changed material fails CHEEY at .29G002, and QODY is not reached. Changed operations pass the material-only CHEEY gate and alter QODY to [reviewer_late_operation, dry-set]. QODY therefore consumes actual returned operations, and CHEEY actually tests returned material. Altering only duplicated genealogy audit metadata leaves both semantic outputs unchanged; this is not counted as meaningful consumption.','',
 'The explicit-earlier policy selects .25G004 powder/granular surface-converted TYPE, satisfies the .29G002 source assertion and emits further surface-convert+dry-set prescription. Latest-only selects .28G004 sheet/laminar TYPE. Its .29G001 written_type_matches is false; the implementation continues until the next CHEEY assertion fails at .29G002. All remaining7 positions from .29G003 through .30G004 are marked not reached; no further prescription is generated. Same lexicon/operations/inputs are used. This is contradiction inside paid type/reference assertions, not inability of sheet material to undergo dry-setting, and not independent selection of those meanings.','',
 'The program initializes a first-source criterion and early second recipe before the row loop. QOLCHEY/OTCHEY later emit criteria rather than supplying that initial source object as a literal returned payload. Shared enclosure conditions are copied into the two generation contributions, rather than evaluated by QOKEDY as part of its material/process genealogy. These are paid context/type description choices; the actual required TYPE-to-late-consumer edge is intact, but no all32-return pipeline or physical execution is established.', '',
 'All32 IT contributions and their attachments are recorded in JSON. Early SHEDY and late CHEEY are recipe/type references, not silent production or loading events. Terminal constraints legitimately contribute without changing material state. ZL/RF semantic accounts remain incomplete; uncertain late assemblies are not normalized. RF terminal SAIIN happens to be licensed elsewhere but cannot inherit IT SAIRN closure merely by index. Fresh versus persistent batches of the same type remain indistinguishable.','',
 'Recounted choices:2 material primitives,2 state primitives,3 core operator senses,1 source-predication rule,7 extension primitives,11 whole residuals,23 lexical rules,10 literal assemblies,32 bindings,2 reference policies and12 scope/default decisions;0 aliases/overloads. These match declarations, not an economy optimum. The shared method/ontology and all English senses remain C0. No confirmed word, historical source identity, morphology, physical feasibility, full IDEA876 label/prose transfer, significance or reserve eligibility follows.','',
 '| Frozen criterion | Outcome |','|---|---|']
 md.extend('| '+k+' | '+v+' |' for k,v in out['criteria'].items())
 md+=['','Reproduce: `python experiments/yolo/gdt1137_material_process_type_return/src/validate.py`. Uses in-memory module loading and the released build/execute APIs; writes only its own validation files.','', 'Validator SHA256: `'+out['validator_sha256']+'`. Frozen plan SHA256: `'+out['frozen_plan_sha256']+'`.','']
 (ART/'VALIDATION.md').write_text('\n'.join(md))
 print(json.dumps({'status':out['status'],'checks':checks,'validator_sha256':out['validator_sha256']},indent=2))
 return 0 if all(checks.values()) else 1
if __name__=='__main__':raise SystemExit(main())
