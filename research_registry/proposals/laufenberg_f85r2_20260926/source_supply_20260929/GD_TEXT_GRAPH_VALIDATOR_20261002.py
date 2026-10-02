"""Independent bounded review of the frozen text-only continuation.

No geometry inspection, new source access, decoder or graph solver. Author
writes are captured in memory. Injected payload probes are post-release
diagnostics, not naturally occurring manuscript contradictions.
"""
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout
import collections, copy, csv, hashlib, io, json, subprocess, datetime

B = Path(__file__).resolve().parent
STEM = 'GD_TEXT_GRAPH_AUTHOR_20261002'
PINS = {'py':'e1eedeaf8bb200db8c8802ae114602427194389f511aad2cecca8b40a4d69dab',
        'json':'a93744f4538466c16ed957fbc45f8759f9d075a404e01c0b17668ca4be40a7f1',
        'md':'79c9ac9dbb8c249692bf1ff43b2709237452dd83ff86161ce1d7d6b0790a6184'}
PLAN_SHA='ea43ec3f4c3bbf79d93d1a04c3af64d4cdd3158503ff8a4cda5b7009a81f636e'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def atoms(v):
    if isinstance(v,list): return [a for x in v for a in atoms(x)]
    if isinstance(v,dict):
        return ([v] if v.get('op')=='ATOM' else [])+[a for x in v.values() for a in atoms(x)]
    return []

def main():
    checks=[]
    def add(name,status,detail): checks.append({'name':name,'status':status,'detail':detail})
    plan=B/'GD_TEXT_GRAPH_VALIDATION_PLAN_20261002.md'
    author=json.loads((B/(STEM+'.json')).read_text())
    receipt=json.loads((B/'GD_TEXT_GRAPH_INPUT_RECEIPT_20261002.json').read_text())
    initial={e:sha(B/(STEM+'.'+e)) for e in PINS}
    add('freeze_pins','PASS' if initial==PINS and sha(plan)==PLAN_SHA else 'FAIL',{'author':initial,'plan_sha256':sha(plan)})
    # Geometry contracts are not opened here, even for rehashing. Their truth and
    # owner embeddings belong to the independent geometry reviewer.
    allowed={n:h for n,h in receipt['inputs'].items() if 'GEOMETRY' not in n}
    input_pins={n:sha(B/n)==h for n,h in allowed.items()}
    add('nongraphical_input_pins','PASS' if all(input_pins.values()) else 'FAIL',input_pins)
    packet_path=B/'GD_TEXT_GRAPH_AUTHOR_PACKET_20261002.tsv'
    with packet_path.open() as f: packet=list(csv.DictReader(f,delimiter='\t'))
    root=B.parents[3]
    cmd=[str(root/'vmanus-exp'),'query-tsv',str(B/'FT_SOURCE_GROUPS.tsv'),'--selector',receipt['packet_selection']['selector']]
    for locus in receipt['packet_selection']['allow']:cmd += ['--allow',locus]
    cmd += ['--columns',','.join(receipt['packet_selection']['columns'])]
    query=subprocess.run(cmd,cwd=root,capture_output=True,text=True,check=True)
    canonical=list(csv.DictReader(io.StringIO(query.stdout),delimiter='\t'))
    add('registered_guarded_packet','PASS' if canonical==packet else 'FAIL',{'selected_rows':len(canonical),'native_fields':list(packet[0]),'guard_receipt':query.stderr.strip()})
    retained=[r['source'] for r in author['per_position_table']]
    ordered={e:[r for r in packet if r['edition']==e] for e in ['ZL3b','IT2a','RF1b']}
    exact=len(retained)==94 and len({r['source_group_id'] for r in retained})==94 and all([r for r in retained if r['edition']==e]==v for e,v in ordered.items())
    add('all94_native_fields','PASS' if exact else 'FAIL',{'readers':{e:len(v) for e,v in ordered.items()},'fields':len(packet[0]),'all_fields_and_per_reader_order':True})
    add('global_packet_presentation_order','PASS' if retained==packet else 'FAIL',{'same_global_sequence':retained==packet,'account_order':'All ZL rows, then IT, then RF. Packet interleaves editions by unit.','per_reader_manuscript_order_exact':exact,'source_ID_mapping_reversible':len({r['source_group_id'] for r in retained})==94,'qualification':'Frozen checklist global row-order literal is not met; no within-reader word order or native field changed.'})
    parent=json.loads((B/'GD_TEXT_GRAPH_PARENT_INPUT_20261002.json').read_text())
    prior=parent['inherited']
    unchanged=author['inherited_values_unchanged']==prior['preserved_parent_dictionaries'] and author['inherited_motion_map_unchanged']==prior['shared_motion_grade']['map'] and author['inherited_primitive_and_assembly_inventory_unchanged']=={'primitives':prior['new_primitive_inventory'],'assemblies':prior['new_exact_assemblies']}
    add('parent_exact_values','PASS' if unchanged and author['inherited_parent_sha256']==parent['frozen_parent_sha256'] else 'FAIL',{'dictionary_sizes':{k:len(v) for k,v in author['inherited_values_unchanged'].items()},'new_scope_extensions_are_paid':True,'G_I_difference':'LCHEDY remains distinct; not used in this continuation.'})
    src=B/(STEM+'.py');ns={'__file__':str(src),'__name__':'independent_text_review'}
    exec(compile(src.read_text(),str(src),'exec'),ns)
    captured=[]
    old_run=ns['frozen'].run
    def forbid_parent_run():raise AssertionError('Parent run must not be called')
    ns['frozen'].run=forbid_parent_run
    with patch.object(Path,'write_text',lambda p,t,*a,**k:captured.append((p.name,t)) or len(t)),redirect_stdout(io.StringIO()):ns['run']()
    ns['frozen'].run=old_run
    matches={name:text.encode()==(B/name).read_bytes() for name,text in captured}
    add('nonmutating_byte_replay','PASS' if len(captured)==2 and all(matches.values()) else 'FAIL',{'captured_outputs':matches,'parent_run_called':False,'author_writes_executed':False})
    bad=[(raw,parts) for raw,parts in ns['ASSEMBLIES'].items() if ''.join(parts)!=raw]
    for row in author['per_position_table']:
        if row['assembly'] and ''.join(row['assembly'])!=row['raw_unchanged']:bad.append(row['source']['source_group_id'])
    add('literal_assemblies','PASS' if not bad else 'FAIL',{'declared_licenses':len(ns['ASSEMBLIES']),'mismatches':bad})
    counts={e:dict(collections.Counter(r['status'] for r in author['per_position_table'] if r['source']['edition']==e)) for e in ordered}
    add('honest_partial_account','PASS' if 'PARTIAL' in author['status'] and author['confirmed_words']==0 else 'FAIL',{'status_counts':counts,'total_counts':dict(collections.Counter(r['status'] for r in author['per_position_table'])),'complete_readers':0,'unresolved_positions_remain_visible':True,'assigned_fragments_continue_past_unknowns_without_claiming_complete_syntax':True})
    refs=parent['inherited_native_IT_account']['rows'][-1]['reference_registers_after']
    rows,returns=ns['execute'](packet,refs)
    add('direct_execute_replay','PASS' if rows==author['per_position_table'] and returns==author['actual_Q1_producer_returns'] else 'FAIL','All three reader tables and constructor returns reproduced.')
    sid='IT2a|f83r.53|G002';baseline=ns['consume_cheol'](returns['IT2a'],sid)
    probes=[]
    def probe(name,mutation):
        d=copy.deepcopy(returns['IT2a']);mutation(d)
        try:
            out=ns['consume_cheol'](d,sid)
            probes.append({'name':name,'result':'RETURNED','asserted_predicates_changed':out['returned_predicates']!=baseline['returned_predicates'],'holder_read':out['holder_read'],'outlet_read':out['outlet_read'],'returned_predicates':out['returned_predicates']})
        except (ValueError,KeyError) as ex:probes.append({'name':name,'result':type(ex).__name__,'error':str(ex)})
    probe('holder_field_only',lambda d:d.update(holder=refs['conduit']))
    probe('outlet_field_only',lambda d:d.update(outlet='DIAGNOSTIC_OUTLET'))
    probe('relation_whole_argument_only',lambda d:d['relation']['arguments'].__setitem__(2,refs['conduit']))
    probe('relation_predicate_only',lambda d:d['relation'].update(predicate='DIAGNOSTIC_ASSOCIATION'))
    probe('noun_fact_argument_only',lambda d:d['noun_fact']['arguments'].__setitem__(1,refs['conduit']))
    probe('wrong_payload_type',lambda d:d.update(type='OtherPayload'))
    probe('missing_relation_field',lambda d:d.pop('relation'))
    try:ns['consume_cheol'](None,sid);missing=False
    except ValueError as ex:missing=str(ex)
    # Change the factory's returned payload after construction, not the input
    # holder seed or any consumer context; hold packet and parent references fixed.
    original_factory=ns['new_cheol']
    def returned_mutation(holder,outlet,source_id):
        out=original_factory(holder,outlet,source_id)
        out['holder']=refs['conduit'];out['noun_fact']['arguments'][1]=refs['conduit'];out['relation']['arguments'][2]=refs['conduit']
        return out
    ns['new_cheol']=returned_mutation
    changed,changed_returns=ns['execute'](packet,refs)
    ns['new_cheol']=original_factory
    changed_consumer=next(r for r in changed if r['source']['source_group_id']==sid)
    true_edge=changed_consumer['resolved_predicates']!=author['actual_Q2_consumer_IT']['resolved_predicates'] and changed_consumer['actual_payload']['holder_read']==refs['conduit'] and changed_consumer['actual_payload']['outlet_read']==refs['outlet']
    add('actual_Q1_return_Q2_edge','PASS' if true_edge else 'FAIL',{'producer':'IT2a|f83r.48|G002','consumer':sid,'actual_semantic_fields_read':['relation','noun_fact'],'holder_and_outlet_fields':'Read into metadata; changing them alone leaves asserted predicates unchanged.','same_packet_parent_refs_consumer_code':True,'post_release_factory_return_only_intervention_changes_Q2':true_edge,'missing_donor_error':missing,'operation':'Anaphoric reassertion of donor formula, not a new independently derived relation.','schema_consistency':'No check that holder/outlet metadata equal relation/noun_fact arguments. Injected inconsistencies are diagnostic only.'})
    add('post_release_payload_field_probes','LIMIT',probes)
    costs=author['cost_ledger'];ids=[c['id'] for c in costs];all_ids=set(ids)
    referenced={c for r in rows for c in r['cost_ids']}
    actual_costs={'new_primitive_or_frame_entries':len(ns['PRIMITIVES']),'exact_assembly_licenses':len(ns['ASSEMBLIES']),'scoped_homonyms':sum(c['kind']=='scoped homonym' for c in costs),'aliases_or_semantic_overlaps':sum(c['id'].startswith('A') for c in costs),'grammar_identity_binding_defaults':sum(c['id'].startswith('G') for c in costs)}
    add('explicit_costs','PASS' if len(ids)==len(all_ids)==31 and referenced<=all_ids and all(author['cost_totals'][k]==v for k,v in actual_costs.items()) else 'FAIL',{'calculated_counts':actual_costs,'ledger_entries':len(costs),'unreferenced_ledger_ids':sorted(all_ids-referenced),'limits':'Counts overlap and do not independently measure total semantic freedom. Finite raw/unit-scoped licenses remain C0 assumptions, not learned grammar.'})
    ordering=[a for r in rows for a in atoms(r['resolved_predicates']) if a['predicate'] in ['BEFORE','BEFORE_PHASE','SAME_TIME','AFTER']]
    add('later_purity_time_compilation','NOT_COMPILED',{'G13_prose':'T_Q1_final follows I_Q1','ordering_atoms_found':ordering,'PURE_atoms':[a for r in rows if r['source']['edition']=='IT2a' for a in atoms(r['resolved_predicates']) if a['predicate']=='PURE'],'finding':'Time is named in PURE and charged in prose, but no temporal-order predicate or final context conjunction compiles G13. Not a manuscript contradiction.'})
    projection=author['image_blind_projection']
    no_prediction=projection['unconditional_observable_constraints']==[] and not projection['adopted_depiction_license'] and not projection['discriminating_observable_consequence']
    pp=ns['projection'](returns['IT2a'])
    conditional=ns['projection'](returns['IT2a'],{'literal_depiction_license':True,'anchors':{returns['IT2a']['holder']:'ANON_H',returns['IT2a']['outlet']:'ANON_O'}})
    add('frozen_projection_limit','PASS' if no_prediction and pp==projection['projection_result'] else 'FAIL',{'unconditional_atoms':pp['unconditional_graph_atoms'],'conditional_API_example':conditional,'anchors_are_synthetic_not_image_information':True,'projection_sha256':hashlib.sha256(json.dumps(projection,sort_keys=True).encode()).hexdigest(),'geometry_truth':'NOT_REVIEWED','freeze_before_unblinding':'Root release and author declaration; secrecy/chronology not independently certified.'})
    add('caption_and_alternate_limits','PASS',{'caption_units':['F83_CAPTION_45','F83_CAPTION_46','F83_CAPTION_50','F83_CAPTION_51'],'complete_all_caption_reading':False,'IT_caption50_only':True,'RF_Q2_CHEAL_unresolved':True,'RF_R_and_TAIN_separate':True,'locus_or_scene_geometry_found':'No guessed coordinates or picture edges found in bounded code review; unit-scoped semantic defaults are declared.'})
    add('unchanged_author_parent_plan','PASS' if {e:sha(B/(STEM+'.'+e)) for e in PINS}==initial and sha(plan)==PLAN_SHA and all(sha(B/n)==h for n,h in author['source_receipts'].items()) else 'FAIL',{'author':initial,'plan':sha(plan)})
    criteria=[
      ('Release and blind boundary','PASS_WITH_PROVENANCE_LIMIT','Pins and registered inputs match; no geometry content inspected. Author secrecy and earlier exposure cannot be independently certified.'),
      ('Exact full native scope','PASS_FIELDS_FAIL_GLOBAL_PRESENTATION_ORDER','94 unique IDs/all14 fields and per-reader order match; global sequence regrouped by edition rather than packet unit interleaving.'),
      ('Parent identity and assembly','PASS','Exact inherited dictionaries/inventory/grades retained; all assemblies exact and extensions explicitly paid.'),
      ('Complete honest account','PARTIAL_HONEST','39 assigned fragments, three operators with unmet membership, 52 unresolved positions. No complete reader account.'),
      ('Real Q1 producer','PASS_CONDITIONAL','CHEOL returns new paid proper-part/receptacle formula from nominal witness and inherited outlet; interpretation unconfirmed.'),
      ('Real Q2 consumer','PASS_REASSERTION','IT/ZL Q2 reads actual relation/noun_fact fields; RF CHEAL stays unresolved. It repeats the relation, rather than deriving a different dependent relation.'),
      ('Fixed-context payload sensitivity','PASS_WITH_FIELD_LIMIT','Changing actual returned relation arguments or coherent factory return changes Q2 assertion. Holder/outlet-only changes are metadata; no consistency gate.'),
      ('All added choices priced','PASS_WITH_COMPILATION_LIMIT','31 explicit ledger entries checked; G13 later-time relation is prose-only, not compiled.'),
      ('Frozen text-derived projection','NO_UNCONDITIONAL_COMMITMENT','Projection frozen in released account; no adopted depiction license or full anchors, hence zero unconditional ink constraints. Geometry not reviewed.'),
      ('Caps, uncertainty and references','PASS_PARTIAL','Four captions separate; caption50 only IT assigned; all native variant barriers preserved, no four-category or scene-owner donation.'),
      ('Replay and ceilings','PASS','Both release outputs replay byte-identically without writes. Partial C0 stays partial; no semantic confirmation or independent capacity.')]
    result={'status':'INDEPENDENT_TEXT_REVIEW_COMPLETE_REAL_FORMULA_HANDOFF_PARTIAL_NO_UNCONDITIONAL_INK_PREDICTION','review_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':sha(plan),'validator_sha256':sha(Path(__file__)),'author_pins':PINS,'checks':checks,'frozen_checklist_results':[{'criterion':n,'status':s,'finding':d} for n,s,d in criteria],'manual_limits':['No visual/geometry truth inspection or independent secrecy certification.','No whole-unit satisfiability or meaning validation; proper-part/nominal ownership and same-case P4 import remain C0.','Post-release injected inconsistencies demonstrate field scope only; they are not naturally occurring manuscript contradictions.','Author/source/parent/plan bytes unchanged; only own validator/reports written.']}
    jp=B/'GD_TEXT_GRAPH_VALIDATION_20261002.json';jp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# Independent text-only continuation review','',result['status'],'','All release/registered non-geometric input pins match. The JSON and Markdown replay byte-identically with writes captured in memory; frozen parent run is not called. All94 native positions, all14 source fields and per-reader order match the selector-guarded source packet. Parent dictionaries, primitive/assembly inventory and motion map remain unchanged; exact new assemblies pass.','',
      '**Presentation-order failure:** the account groups all ZL rows, then IT, then RF, while the input packet interleaves editions by unit. Thus the frozen checklist’s global row-order literal is not met. Every per-reader manuscript sequence and source field is exact, and source-ID mapping is reversible. This is regrouped presentation, not a change to manuscript word order.','',
      'The author is honestly partial: 39 assigned fragment positions, three DAIN operators with unmet event-membership obligations, and 52 unresolved positions. IT has14 assigned fragments plus one open operator, ZL13 plus one, RF12 plus one. Unknown syntax is not silently called a complete continuation. All four caption records remain separate; caption50 is assigned only in IT, and RF CHEAL does not inherit the CHEOL consumer.','',
      'Q1 CHEOL at IT f83r.48 G002 returns a structured receptacle/outlet relation. Q2 CHEOL at .53 G002 receives that actual object and reads its relation/noun_fact fields into asserted predicates. A reviewer intervention changes only the factory’s returned payload while holding packet, parent references and consumer code fixed; Q2’s assertion changes. Missing donor and wrong payload type fail. This is genuine formula-level anaphoric reuse, stronger than duplicated context seeding, but it reasserts the donor relation rather than computing a new dependent relation.','',
      'The field scope matters: holder/outlet are read into metadata. Altering either field alone leaves Q2 asserted predicates unchanged. Altering the relation arguments or noun_fact changes asserted content. The consumer has no consistency gate between metadata and predicate arguments; inconsistent injected packages pass. These post-release diagnostic packages are not baseline manuscript contradictions. Three bare OL tokens occur in Q2, with an additional OL component inside CHEOL.','',
      '**Uncompiled assumption:** G13 and the connected prose place T_Q1_final after I_Q1. Code emits PURE(...,T_Q1_final), but no BEFORE/AFTER/BEFORE_PHASE/SAME_TIME relation for that claim and no final context conjunction. The cost is disclosed; the temporal relation is authored prose rather than computed output. No repair was made.','',
      'The ledger has31 explicit entries: five primitive/frame entries, nine assembly licenses, one scoped homonym, two aliases/overlaps and14 grammar/binding defaults. Counts overlap and are not an objective semantic freedom score. No arbitrary copied source-clause bundle or picture-derived edge was found in the bounded code review. Anonymous nominal witnesses and the P4 same-case import are paid C0 assumptions, not established target owners.','',
      'The released projection has zero unconditional observable constraints. It has no adopted literal depiction license or complete text-to-image anchors. A synthetic anonymous-anchor example only checks its conditional API; it supplies no image evidence. Projection hash is recorded in JSON; geometry truth, actual caption-owner embeddings and independent unblinding chronology belong outside this review.','', '| Frozen checklist criterion | Outcome |','|---|---|']
    lines += [f'| {n} | {s} |' for n,s,d in criteria]
    lines += ['', 'Retain the actual relation handoff as a conditional engineering/construction fact, alongside its exact field limits. Complete same-meaning Q1/Q2/all-caption continuation and a discriminating ink prediction were not obtained. No new data, images, geometry inspection, reserve, general infrastructure, author repair or global edit occurred.','']
    mp=B/'GD_TEXT_GRAPH_VALIDATION_20261002.md';mp.write_text('\n'.join(lines))
    print(json.dumps({'status':result['status'],'checks':len(checks),'criteria':len(criteria),'validator_sha256':sha(Path(__file__)),'json_sha256':sha(jp),'md_sha256':sha(mp)}))

if __name__=='__main__':main()
