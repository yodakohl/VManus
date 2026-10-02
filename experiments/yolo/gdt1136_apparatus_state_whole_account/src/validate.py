#!/usr/bin/env python3
"""Independent frozen-plan GDT1136 accounting and existing-API probes.
No source rewriting, fit, parser, chemistry proof or semantic certification.
"""
from pathlib import Path
import collections, contextlib, copy, csv, hashlib, io, json
from unittest.mock import patch
BASE = Path(__file__).resolve().parents[1]
ART = BASE / 'artifacts'
PINS = {
 'src/author.py':'d2a7f066600c49cad92f35711dc47efdb38bf54ee72cf8262c133e2ce004e6b4',
 'artifacts/AUTHOR_ACCOUNT.json':'a407db5b262e116f3195f75b8d6a35c5f05208f13e204de20fb1c7469ba17658',
 'artifacts/AUTHOR_READING.md':'0e08908045bcec71f3cecf61ebc5c9c8002bbfd5e917ab6f1bd04fd1dae4f76a',
 'artifacts/AUTHOR_RECEIPT.json':'aa3b030ef7a14e4fc70a46346e60ccda75872985f561926f8905c26838545337',
 'artifacts/NATIVE_GROUPS.tsv':'0f0533a11773dabf2051d1a8946014f9668475179820cea49c023beb7ac26c09',
 'METHOD.md':'3ef982c889acde16f3b4dc62e03c04db4132db03df7f3266807309111da0197e',
 'PREREGISTRATION.md':'3ef982c889acde16f3b4dc62e03c04db4132db03df7f3266807309111da0197e',
 'artifacts/WORD_PRIORS.json':'b795c35675ae50515f79b48e4b42dbccb2bb4ab2e23216c0c1215e85e49217e6',
 'artifacts/WORD_PRIORS_RECEIPT.json':'fdb6e1e548ff2103adfdc3e6ea65b678755e6ebed99d137652a2f2bfde28965c',
 'artifacts/VALIDATION_PLAN.md':'400cb5e837a72fbd05b329cf0923177f3b4d48412d618d98c6fd6d82213d904b'}
FIELDS = ['source_group_id','edition','locus','page','section','currier','hand','code','kind','grammar_scope','source_row_index','source_group_index','source_group_count','paragraph_start','paragraph_end','left_separator','right_separator','ivtff_group_raw']
COUNTS = {'ZL3b':227,'IT2a':209,'RF1b':229}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(f): return f['argument'] if f['op']=='NOT' else f
def property_values(chain): return {k:v['P_generated_by_law'] for k,v in chain['product_returns'].items()}
def compare_native(expected,reported):
 e={r['source_group_id']:r for r in expected};counts=collections.Counter(r['source_group_id'] for r in reported);r={x['source_group_id']:x for x in reported}
 differences=[{'ID':sid,'field':f} for sid in e.keys() & r.keys() for f in FIELDS if r[sid].get(f)!=e[sid][f]]
 order={ed:[r['source_group_id'] for r in reported if r['edition']==ed]==[r['source_group_id'] for r in expected if r['edition']==ed] for ed in COUNTS}
 return {'count':len(reported),'missing':sorted(e.keys()-r.keys()),'extra':sorted(r.keys()-e.keys()),'duplicate_IDs':{k:v for k,v in counts.items() if v!=1},'field_differences':differences,'per_edition_order':order,'global_presentation_order_same':[r['source_group_id'] for r in reported]==[r['source_group_id'] for r in expected]}
def main():
 before={f:sha(BASE/f) for f in PINS};pincheck={f:before[f]==s for f,s in PINS.items()}
 if not all(pincheck.values()): raise SystemExit('Frozen input pin failure; no author execution')
 with (ART/'NATIVE_GROUPS.tsv').open() as h:
  reader=csv.DictReader(h,delimiter='\t');fields=reader.fieldnames;source=list(reader)
 account=json.loads((ART/'AUTHOR_ACCOUNT.json').read_text());receipt=json.loads((ART/'AUTHOR_RECEIPT.json').read_text())
 src=BASE/'src/author.py';ns={'__file__':str(src),'__name__':'independent_review'};exec(compile(src.read_text(),str(src),'exec'),ns)
 captured={}
 def capture(p,value,*args,**kwargs): captured[str(p.relative_to(BASE))]=value.encode(kwargs.get('encoding') or 'utf-8');return len(value)
 with patch.object(Path,'write_text',capture),contextlib.redirect_stdout(io.StringIO()): ns['run']()
 replay={f:hashlib.sha256(captured[f]).hexdigest()==before[f] for f in ['artifacts/AUTHOR_ACCOUNT.json','artifacts/AUTHOR_READING.md','artifacts/AUTHOR_RECEIPT.json']}
 sources=[r['source'] for r in account['all_native_alternatives']];native=compare_native(source,sources);it=[s for s in source if s['edition']=='IT2a'];rows=account['IT_per_group_reduction'];chain=ns['actual_chain']();written,origins=ns['written_product_assertions'](rows)
 flattened=[f for r in rows for f in r['returned_constraints']];formula=account['full_authored_formula'];lex=account['lexicon'];core=account['finite_core_AST'];mainids={t['source_group_id'] for t in chain['trace']}
 rowledger=[]
 for r in rows:
  sid=r['source']['source_group_id'];facts=r['returned_constraints'];card=r['lexical_card']
  rowledger.append({'source_group_id':sid,'raw':r['source_raw_preserved'],'type':card['type'],'semantic':card['semantic'],'status':r['assignment_status'],'predicates':[('NOT ' if f['op']=='NOT' else '')+atomic(f)['predicate'] for f in facts],'event':r['typed_bindings']['event_port']['event'],'material':r['typed_bindings']['material_port'],'output':r['typed_bindings']['output_port'],'scheduled_state_update':sid in mainids,'initial_preparation_seed_origin':sid==ns['sid'](1,1)})
 counts=collections.Counter(r['type'] for r in rowledger);alt=collections.Counter((r['source']['edition'],r['status']) for r in account['all_native_alternatives'])
 costs={
 'exact_lexical_semantic_residual_cards':len(lex),'listed_ordered_assembly_licenses':sum(c['assembly_cost'] for c in lex.values()),
 'component_value_hypotheses':len(account['component_hypotheses']),'manual_phrase_bindings':len(account['manual_phrase_map']),
 'reference_frame_defaults_and_identity_rules':len(account['priced_rules']),'causal_laws':len(account['causal_laws']),
 'scoped_polarity_qualifiers':sum(bool(c.get('property')) for c in core.values()),'scoped_homonym_decisions':sum(c['cost'] for c in account['scoped_homonyms']),
 'finite_core_compositions':len(core),'subsidiary_event_preservation_laws':len(account['subsidiary_event_laws'])}
 costscheck={k:account['costs'][k]==v for k,v in costs.items()}
 coreprobes=[]
 for raw in core:
  s=next(s for s in it if s['ivtff_group_raw']==raw);original=copy.deepcopy(ns['CORE_AST'][raw]);old=ns['reduction'](s,chain)['returned_constraints']
  ns['CORE_AST'][raw]={**original,'constructor':'REVIEWER_CHANGED','root':'REVIEWER_CHANGED','domain':'REVIEWER_CHANGED','reference':'REVIEWER_CHANGED','property':{'predicate':'REVIEWER_CHANGED','polarity':False},'noun':'REVIEWER_CHANGED','qualifier':'REVIEWER_CHANGED'}
  coreprobes.append({'raw':raw,'semantic_constraints_unchanged':old==ns['reduction'](s,chain)['returned_constraints']});ns['CORE_AST'][raw]=original
 oldcomponents=copy.deepcopy(ns['COMPONENTS']);ns['COMPONENTS']={k:'REVIEWER_CHANGED' for k in oldcomponents}
 componentprobe=all(ns['reduction'](s,chain)['returned_constraints']==r['returned_constraints'] for s,r in zip(it,rows));ns['COMPONENTS']=oldcomponents
 def return_intervention(index):
  state=copy.deepcopy(chain['trace'][index]['actual_return']);state['apparatus_state']=1-state['apparatus_state'];products={k:copy.deepcopy(v) for k,v in state['product_returns'].items()}
  for t in chain['trace'][index+1:]:
   state,p=ns['step'](state,t['operation'],t['source_group_id'])
   if p: products[p['identity']]=p
  return {k:v['P_generated_by_law'] for k,v in products.items()}
 conditionprobe=return_intervention(0);cleanprobe=return_intervention(4)
 changedchain=copy.deepcopy(chain);changedchain['product_returns']['O2']['identity']='REVIEWER_O2'
 negative=next(s for s in it if s['source_group_id']==ns['sid'](7,13));negativefacts=ns['reduction'](negative,changedchain)['returned_constraints']
 targetprobe=any(f['op']=='NOT' and f['argument']['arguments']==['REVIEWER_O2'] for f in negativefacts)
 state=copy.deepcopy(chain['trace'][0]['actual_return']);state['vessel']['identity']='REVIEWER_V'
 for t in chain['trace'][1:]: state,_=ns['step'](state,t['operation'],t['source_group_id'])
 vesselprobe={k:v['vessel']['identity'] for k,v in state['product_returns'].items()}
 bad=copy.deepcopy(chain['trace'][2]['actual_return']);bad['bulk']['identity']='B_WRONG'
 try: ns['step'](bad,'PRODUCT1',ns['sid'](6,8));badresult='NO_FAILURE'
 except ValueError as e: badresult=str(e)
 scenarios={label:property_values(ns['actual_chain'](**kwargs)) for label,kwargs in [('baseline',{}),('without_conditioning',{'conditioning':False}),('without_cleaning',{'cleaning':False}),('memoryless_bulk_reset',{'model':'memoryless_bulk'}),('adherent_A_film',{'model':'adherent_A_film'})]}
 references=[]
 for r in rows:
  b=r['typed_bindings']
  for name,value in [('material',b['material_port']),('output',b['output_port']),('event',b['event_port']['event'])]:
   if value not in account['declared_sort_environment']: references.append({'ID':r['source']['source_group_id'],'port':name,'value':value})
 prior_receipts=json.loads((ART/'WORD_PRIORS_RECEIPT.json').read_text())
 prior_scopes=[r['source_receipt']['inputs'] for r in prior_receipts]
 profile_counts=all(v['local_IT_count']==sum(s['ivtff_group_raw']==raw for s in it) for raw,v in account['profile_numbers_consulted_before_glossary_freeze'].items())
 alt_cards=all(a['raw_unchanged']==a['source']['ivtff_group_raw'] and a['lexical_card_if_exact']==lex.get(a['raw_unchanged']) and (a['status']=='UNASSIGNED_ALTERNATE_RAW')==(a['raw_unchanged'] not in lex) for a in account['all_native_alternatives'])
 assembled=all(c['raw']==raw and ''.join(c['components'])==raw for raw,c in lex.items())
 repeated=all(r['lexical_card']==lex[r['source_raw_preserved']] for r in rows)
 checks={'pins':all(pincheck.values()),'source_fields':fields==FIELDS,'rows665_counts':len(source)==665 and dict(collections.Counter(s['edition'] for s in source))==COUNTS,
 'source_scope':{s['page'] for s in source}=={'f101r'} and {s['locus'] for s in source}=={f'f101r.{n}' for n in range(1,11)},
 'exact_native_fields':not(native['missing'] or native['extra'] or native['duplicate_IDs'] or native['field_differences']) and all(native['per_edition_order'].values()),
 'replay_bytes':all(replay.values()),'IT209_exact_order':len(rows)==209 and [r['source'] for r in rows]==it,
 'exact144_lexicon_and_assemblies':set(lex)=={s['ivtff_group_raw'] for s in it} and len(lex)==144 and assembled,
 'prior_cache_scope179_excludes_target':all(v['selector_count']==179 and 'f101r' not in v['selectors'] for v in prior_scopes),'exact_local_profile_counts':profile_counts,'all_alternate_cards_and_unknown_statuses_honest':alt_cards,'repeated_whole_dictionary_identical':repeated,'all209_nonempty_collected':all(r['returned_constraints'] for r in rows) and flattened==formula['body']['arguments'] and len(flattened)==248,
 'reference_ports_declared':not references,'binders_sorts_identical':set(formula['binders'])==set(account['declared_sort_environment']),
 'cost_inventory_counts':all(costscheck.values()),'source_receipt_pins':all(sha(BASE/f)==v for f,v in account['source_receipts'].items()),
 'freeze_receipt_pins':receipt['author_code_sha256']==before['src/author.py'] and all(sha(ART/f)==v for f,v in receipt['outputs'].items()),
 'actual_condition_return_changes_later_P':conditionprobe=={'O1':False,'O2':False},'actual_clean_return_changes_later_P':cleanprobe=={'O1':True,'O2':True},
 'actual_forward_output_identity_consumed':targetprobe,'actual_vessel_return_consumed':set(vesselprobe.values())=={'REVIEWER_V'},'wrong_fresh_input_rejected':badresult!='NO_FAILURE'}
 unchanged={f:sha(BASE/f)==v for f,v in before.items()};checks['frozen_files_unchanged']=all(unchanged.values())
 out={'status':'ACCOUNTING_AND_PRIMARY_STATE_PROBES_PASS_WITH_COMPOSITION_FAILURE_AND_WHOLE_TRUTH_UNVERIFIED','scientific_or_meaning_PASS':False,
 'validator_sha256':sha(Path(__file__)),'plan_sha256':before['artifacts/VALIDATION_PLAN.md'],'checks':checks,'pin_checks':pincheck,'replay_exact_bytes':replay,'frozen_files_unchanged':unchanged,
 'native_conservation':native,'alternate_counts':[{'edition':e,'status':s,'count':n} for (e,s),n in sorted(alt.items())],
 'coverage':{'IT':209,'distinct_wholes':144,'constraints':248,'operation_positions':counts['operation'],'scheduled_state_update_positions':len(mainids),'other_operation_positions':counts['operation']-len(mainids),'initial_preparation_is_separate_seed_not_reduction_return':True,'type_counts':dict(counts),'distinct_lexical_semantic_labels':len({c['semantic'] for c in lex.values()}),'distinct_emitted_predicate_labels':len({atomic(f)['predicate'] for f in flattened})},
 'costs_recount':costs,'costs_match_declared':costscheck,'cost_meaning_limit':'Definition/declaration counts only; no minimal description length or semantic economy proof. Ten core AST entries are descriptions, not evaluated constructors.',
 'shared_part_probes':{'post_release_runtime_only':True,'all_ten_AST_interventions':coreprobes,'all_component_values_changed_constraints_unchanged':componentprobe,'actual_computed_component_derivations_demonstrated':0,'criterion3_actual_function_requirement':'FAIL'},
 'actual_return_probes':{'post_release_runtime_only':True,'conditioning_return_state_flip':conditionprobe,'cleaning_return_state_flip':cleanprobe,'written_P_literals_held_fixed':written,'forward_output_owner_mutation_consumed':targetprobe,'vessel_return_mutation_in_products':vesselprobe,'wrong_input_first_failure':badresult},
 'written_P_sources':origins,'fixed_scenarios':scenarios,'undeclared_reference_ports':references,'IT_contribution_ledger':rowledger,
 'whole_truth_review':{'proved':False,'source_program_coupling':'Seven hard-coded operation/source-ID pairs are checked against exact whole-card semantics. This is an explicit manually bound conditional program, not execution of shared-part constructors or all native operation predicates. PCHEOL is origin metadata on a manually initialized vessel/state packet; its lexical reducer returns constraints, not that packet.',
 'auxiliary_gap':'Before first actual loading at .5G018, .3G019 THOROUGH_STIR, .3G020 RETAINED_BULK, .4G006 CONTACT, .4G008 SETTLE_LIQUID, .4G009 MEASURED_WITHDRAWAL, .4G016 DRAIN_COMPLETELY, .4G017 CONTACT and .5G012 CONTACT bind B1 and V in E_prepareB1, also BULK_EMPTY(.4G007/.5G002). R08 allows preparatory nominal forward references but expressly not earlier vessel loading. No subsidiary transition/precondition/subevent order explains these asserted B1 actions in an empty not-yet-loaded V. R16 mentions pending events without an explicit modality or future event link for these action atoms. This is an unresolved authored auxiliary-account gap, not a demonstrated manuscript contradiction or merely missing exact mass balance.',
 'temporal_limit':'Boundary/adverb atoms often receive the identical composite phase twice (NEXT_PHASE, REPEAT, AFTER_SETTLING). No BEFORE atom links all phases in the conjunction. R19 order is a paid prose rule and seven-event schedule; interpreting these binary atoms as irreflexive ordering would add an undeclared axiom. Their full temporal truth is unverified.',
 'binding_limits':'FCH(E)OLAIN WASHING_QUANTITY and YFOLAIIN SUBSEQUENT_WASH_QUANTITY bind B2 rather than actual CLEAN agent Wash_R; ORAIIN OUTPUT_QUANTITY binds input B1; YPCHOLY PREVIOUS_STOCK_PREP_COMPLETE binds B2 though previous-feedstock CHOLP binds A. All are nominally type-compatible under broad material signatures, but intended relations to wash/previous/output owners are not computed or independently justified.',
 'type_limit':'Source attachment and declared port types checked; no independent theorem checks every descriptive predicate or physical precondition. Terminal properties may be real contributions without downstream consumers; that does not establish their joint satisfiability.'},
 'rival_limits':{'film_equivalent':scenarios['baseline']==scenarios['adherent_A_film'],'fixed_bulk_reset_fails_only_its_frozen_law':scenarios['memoryless_bulk_reset']!=written,'operation_sensitive_memoryless_counterexample':{'kind':'Post-release analytic boundary, no new solver or alteration of frozen rival','same_fresh_inputs':True,'written_product_operations':['PRODUCE_CONTACT','PRODUCE_WITHDRAWAL'],'stateless_law':'P = operation == PRODUCE_CONTACT','outputs':{'O1':True,'O2':False},'implication':'Unequal processing operations permit a memoryless operation-sensitive law matching both written outputs. Equal B premises do not establish equal processing law; text does not force memory.'},'new_vessel_and_changed_B':'Excluded only inside paid R01/R02/R03/R09 candidate; remain manuscript interpretation rivals'},
 'criteria':{'1':'PASS conservation/pins/replay; global presentation order preserved','2':'PASS209 finite attachments; complete semantic truth UNVERIFIED','3':'FAIL computed shared-part requirement; exact whole-card identity/assemblies PASS; no component evaluator','4':'PASS declaration count accounting; unverified semantic freedom disclosed','5':'PASS primary written conditioning/bulk-empty plus paid program; auxiliary loading gap UNVERIFIED','6':'PASS distinctness/equality under paid factories; processing laws differ in source operations','7':'PASS independent whole-card P/NOTP assertions and actual output referents; not part-derived','8':'PASS actual primary state edge; preparation seeded and seven operations manually scheduled','9':'PASS actual return-field sensitivity; diagnostic probes unchanged written literals','10':'PARTIAL primary witness passes; whole auxiliary formula truth UNVERIFIED','11':'PARTIAL fixed rivals honestly reported; memoryless operation-sensitive alternative survives','12':'PASS ceilings retained;0 confirmed meanings/no reserve eligibility'},
 'limits':['C0 complete authorship may be retained without independent meaning anchor.','No visual/native reading, chemistry, mechanism, temporal grammar, physical whole-model SAT, calibrated preference, decipherment or independently confirmed meaning is certified.','No author, source or frozen plan files changed.']}
 (ART/'VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 md=['# GDT1136 independent frozen-plan validation','', '**Accounting and the primary conditional state program pass. Computed shared-part composition fails; whole-account truth remains unverified. Confirmed meanings:0.**','',
 'All665 native rows preserve all18 source fields and reader order (IT209/ZL227/RF229); global presentation order is also exact. IT209 contributions use144 fixed whole cards and collect248 predicates. ZL39 and RF46 remain unassigned; neither alternate is a complete account. Frozen author/source/plan pins and the three nonmutating replay outputs match; no author bytes changed.','',
 'Changing the actual conditioning return flips product1 P; changing the cleaning return flips product2 P. Actual vessel payloads reach both products, and the forward negative assertion reads the actual later output identity. Incorrect fresh-input identity raises the existing consumer gate. Written P(O1) at .6G009 and NOT P(O2) at .7G013 remain separate whole-card lexical assertions, held fixed during these diagnostic interventions.','',
 'All ten AST declarations can have their semantic fields changed without changing emitted constraints. Changing all23 component values likewise leaves all209 constraints unchanged. The reducer dispatches whole-card semantic labels and copies ASTs as annotations. Its10 declarations are not10 computed shared-part derivations. The literal preparation card returns a constraint, while the state program manually seeds the vessel packet with that source as producer metadata. Seven source-ID/operation pairs are checked against the fixed lexicon and explicitly scheduled; this is a valid manually bound conditional program, not a compositional native compiler.','',
 'The44 operation occurrences include those seven scheduled updates and37 other positions; PCHEOL among the latter supplies the initial preparation seed origin. The remaining actions and terminal properties occur in the248-constraint conjunction, but do not receive subsidiary bulk/precondition execution. Before .5G018 first B1 loading, actual CONTACT, SETTLE_LIQUID, MEASURED_WITHDRAWAL and DRAIN_COMPLETELY atoms already bind B1 and V in E_prepareB1, alongside BULK_EMPTY. R08 permits forward nominal mentions and explicitly forbids earlier actual loading. A general mention of pending prepared events in R16 does not specify modality, future links or subevent order for those action assertions. No unmentioned fluid or loading repairs this gap. This is unresolved auxiliary construction truth, not a manuscript contradiction and not merely exact mass-balance accounting.','',
 'NEXT_PHASE/REPEAT/AFTER atoms sometimes relate the same composite phase to itself. They are not automatically false: no irreflexive temporal definition is supplied. They also do not compile R19 into an ordered whole formula. Washing-quantity/previous-stock/output-quantity defaults have broad compatible material types but some bind B2/B1 instead of Wash_R/A/output owners; their intended relation is unverified. Every209 position and its predicate contribution appears in the JSON ledger.','',
 'The apparatus and adherent-film models remain equivalent. The fixed bulk-reset model gives false/false under the paid uniform transfer law. This excludes that fixed law only: written product1 is contact completion, product2 withdrawal. A stateless operation-sensitive law P=(operation is PRODUCE_CONTACT) gives true/false with equal fresh inputs. This post-release analytic boundary uses the stated operation difference, and demonstrates that equal B alone does not force apparatus memory. New-vessel and unequal-B interpretations are assumed away only inside paid candidate rules.','',
 'Recounted decisions:144 residual cards,112 assembly licenses,23 component hypotheses,22 manual phrase bindings,26 reference/frame rules,4 causal laws,2 polarity qualifiers,4 homonym decisions,10 AST descriptions and28 subsidiary preservation-law descriptions. Counts agree with declarations; these overlapping costs are not a semantic economy score. Most words are residuals, all meanings are C0, and no near-complete reserve eligibility or meaning preference follows.','',
 '| Frozen criterion | Outcome |','|---|---|']
 md.extend('| '+k+' | '+v+' |' for k,v in out['criteria'].items())
 md+=['','Reproduce: `python experiments/yolo/gdt1136_apparatus_state_whole_account/src/validate.py`. It loads frozen code without running its main guard and intercepts all author writes; outputs only its own validation files. Reviewer interventions are post-release runtime diagnostics, not new preregistered source worlds. Full physical/type/temporal satisfiability is not certified.','', 'Validator SHA256: `'+out['validator_sha256']+'`. Frozen plan SHA256: `'+out['plan_sha256']+'`.','']
 (ART/'VALIDATION.md').write_text('\n'.join(md))
 print(json.dumps({'status':out['status'],'checks':checks,'shared_part_failure':True,'whole_truth_proven':False,'validator_sha256':out['validator_sha256']},indent=2))
 return 0 if all(checks.values()) else 1
if __name__=='__main__': raise SystemExit(main())
