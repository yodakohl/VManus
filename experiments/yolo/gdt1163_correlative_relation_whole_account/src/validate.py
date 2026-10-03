#!/usr/bin/env python3
"""Independent GDT1163 reconstruction. No runner/author imports."""
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').exists() and (p/'.git').exists())
BASE = Path(__file__).resolve().parents[1]
ART = BASE/'artifacts'
POLICIES = ('FORWARD_ORIGIN','INVERTED_ORIGIN','INVERTED_DESTINATION')
NOMINALS = {'chey':('UNDERSTAND','ACT'),'cheey':('UNDERSTAND','ACTIVE'),'chedy':('UNDERSTAND','RECEPTIVE'),'shey':('LOVE','ACT'),'sheey':('LOVE','ACTIVE'),'shedy':('LOVE','RECEPTIVE'),'qokeey':(None,'ACTIVE')}
LICENSED = set(NOMINALS)|{'qokedy','solchedy','qody'}
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def local(groups, i, policy='FORWARD_ORIGIN'):
    if i==0 or i+1==len(groups): return {'status':'not_applicable','edge':None}
    a,m,b=groups[i-1:i+2]
    seams=[a['right_separator'],m['left_separator'],m['right_separator'],b['left_separator']]
    if any(s!='DEFINITE_SPACE' for s in seams): return {'status':'unknown','edge':None}
    if a['ivtff_group_raw'] not in NOMINALS or b['ivtff_group_raw'] not in NOMINALS:
        return {'status':'not_applicable','edge':None}
    na,nb=NOMINALS[a['ivtff_group_raw']],NOMINALS[b['ivtff_group_raw']]
    if sorted([na[1],nb[1]])!=['ACTIVE','RECEPTIVE']: return {'status':'contradiction','edge':None}
    active,receive=(a,b) if na[1]=='ACTIVE' else (b,a)
    ar,rr=NOMINALS[active['ivtff_group_raw']][0],NOMINALS[receive['ivtff_group_raw']][0]
    if rr is None or ar not in (None,rr): return {'status':'contradiction','edge':None}
    x={'root':rr,'role':'ACTIVE','source_id':active['source_group_id']}
    y={'root':rr,'role':'RECEPTIVE','source_id':receive['source_group_id']}
    origin,destination=(x,y) if policy=='FORWARD_ORIGIN' else (y,x)
    return {'status':'compatible','edge':{'producer_id':m['source_group_id'],'root':rr,'origin':origin,'destination':destination}}
def consume(edges, policy, actor_root='UNDERSTAND'):
    candidates=[e for e in edges if e['root']=='UNDERSTAND']
    if not candidates: return {'status':'NO_REFERENCE','producer_id':None}
    e=candidates[-1]
    endpoint=e['destination' if policy=='INVERTED_DESTINATION' else 'origin']
    ok=endpoint['role']=='ACTIVE' and endpoint['root']==actor_root and e['root']==actor_root
    return {'status':'PASS' if ok else 'FAIL','producer_id':e['producer_id'],'endpoint':copy.deepcopy(endpoint)}
def main():
    checks=[]
    def ck(name, condition, detail=None):
        checks.append({'check':name,'pass':bool(condition),'detail':detail})
    core=read(BASE/'src/CORE_FREEZE.json')
    for rel in ['METHOD.md','PREREGISTRATION.md','src/CORE_FREEZE.json','artifacts/ROOT_CORE_ACK.json','VALIDATION_PLAN.md']:
        p=BASE/rel
        old=subprocess.check_output(['git','show','0e9749440:'+str(p.relative_to(ROOT))],cwd=ROOT)
        ck('public_registration:'+rel,old==p.read_bytes())
    ack=read(ART/'ROOT_CORE_ACK.json')
    ck('ack_core_hash',sha(BASE/'src/CORE_FREEZE.json')==ack['core_sha256'])
    pins=[(core['input']['native_packet'],core['input']['native_packet_sha256']),(core['word_prior_source'],core['word_prior_sha256']),(core['diagnostic_scope']['input'],core['diagnostic_scope']['sha256'])]
    for p,h in pins: ck('source_pin:'+p,sha(ROOT/p)==h)
    if not all(c['pass'] for c in checks): raise AssertionError('Input pins fail')
    source=read(ROOT/core['input']['native_packet']); cases=read(ROOT/core['diagnostic_scope']['input'])
    groups=[g for c in source['contexts'] for l in c['lines'] for g in l['groups']]
    ck('native_97_unique',len(groups)==97==len({g['source_group_id'] for g in groups}))
    it=next(c for c in source['contexts'] if c['edition']=='IT2a')
    itgroups=[g for l in it['lines'] for g in l['groups']]
    ck('IT_32',len(itgroups)==32)
    ck('qokeedy_three',sum(g['ivtff_group_raw']=='qokeedy' for g in itgroups)==3)
    ck('core_input_all_lines',all([g['ivtff_group_raw'] for g in l['groups']]==core['input']['groups'][l['locus'].split('.')[1]] for l in it['lines']))
    ck('frozen_core_count',len(core['whole_word_licenses'])==10 and len(core['constructions'])==3)
    core_results={}; probes={}
    for policy in POLICIES:
        edges=[]
        for line in it['lines']:
            for i,g in enumerate(line['groups']):
                if g['ivtff_group_raw']=='qokedy':
                    r=local(line['groups'],i,policy)
                    if r['edge']: edges.append(r['edge'])
        consumers=[]
        for line in it['lines']:
            for j,g in enumerate(line['groups']):
                if g['ivtff_group_raw']=='qody':
                    block=line['groups'][j-2:j+1] if j>=2 else []
                    valid=len(block)==3 and block[0]['ivtff_group_raw']=='solchedy' and NOMINALS.get(block[1]['ivtff_group_raw'],(None,None))[1]=='ACTIVE' and all(x=='DEFINITE_SPACE' for x in [block[0]['right_separator'],block[1]['left_separator'],block[1]['right_separator'],block[2]['left_separator']])
                    ck('actual_written_consumer:'+policy,valid)
                    prior_ids={h['source_group_id'] for h in itgroups[:itgroups.index(block[0])]} if valid else set()
                    prior_edges=[e for e in edges if e['producer_id'] in prior_ids]
                    evaluated=consume(prior_edges,policy,NOMINALS[block[1]['ivtff_group_raw']][0]) if valid else {'status':'INVALID_CONSUMER'}
                    consumers.append({'reference_id':block[0]['source_group_id'] if valid else None,'actor_id':block[1]['source_group_id'] if valid else None,'consumer_id':g['source_group_id'],'outcome':evaluated})
        ck('one_written_consumer:'+policy,len(consumers)==1)
        outcome=consumers[0]['outcome']
        core_results[policy]={'edges':edges,'endpoint_check':outcome,'written_consumers':consumers,'conditional_only':True}
        ck('two_actual_producers:'+policy,[e['producer_id'] for e in edges]==['IT2a|f83r.25|G004','IT2a|f83r.28|G004'])
        ck('policy_outcome:'+policy,outcome['status']==('FAIL' if policy=='INVERTED_ORIGIN' else 'PASS'))
        deleted=consume(edges[1:],policy)
        changed=copy.deepcopy(edges);changed[0]['root']='LOVE'; changed_root=consume(changed,policy)
        swapped=copy.deepcopy(edges);swapped[0]['origin'],swapped[0]['destination']=swapped[0]['destination'],swapped[0]['origin']; reversed_edge=consume(swapped,policy)
        identity=copy.deepcopy(edges);identity[0]['producer_id']='INTERVENTION_ONLY_RENAMED_PRODUCER'; renamed=consume(identity,policy)
        probes[policy]={'delete_selected_producer':deleted,'change_selected_root':changed_root,'swap_returned_endpoints':reversed_edge,'rename_selected_producer':renamed}
        ck('causal_delete:'+policy,deleted['status']=='NO_REFERENCE')
        ck('causal_root:'+policy,changed_root['status']=='NO_REFERENCE')
        ck('causal_endpoint:'+policy,reversed_edge['status']!=outcome['status'])
        ck('producer_identity_propagates:'+policy,renamed['producer_id']=='INTERVENTION_ONLY_RENAMED_PRODUCER' and renamed['status']==outcome['status'])
    reconstructed=[]
    for c in cases:
        gs=c['complete_line_groups']; focal=c['left']['source_group_id']; i=next(i for i,g in enumerate(gs) if g['source_group_id']==focal)
        r=local(gs,i)
        reconstructed.append({'case_id':focal,'edition':c['edition'],'locus':c['locus'],'local_status':r['status'],'unknown_group_ids':[g['source_group_id'] for g in gs if g['ivtff_group_raw'] not in LICENSED],'policy_edges':{p:local(gs,i,p)['edge'] for p in POLICIES}})
    totals=dict(Counter(r['local_status'] for r in reconstructed))
    ck('35_cases_13_loci',len(cases)==35 and len({c['locus'] for c in cases})==13)
    ck('all_whole_lines_unresolved',all(r['unknown_group_ids'] for r in reconstructed))
    if (ART/'DIAGNOSTICS.json').exists():
        reported=read(ART/'DIAGNOSTICS.json')
        ck('diagnostic_source_hash',reported['input_sha256']==core['diagnostic_scope']['sha256'])
        ck('diagnostic_core_hash',reported['core_sha256']==sha(BASE/'src/CORE_FREEZE.json'))
        ck('diagnostic_order_all35',[r['case_id'] for r in reported['rows']]==[r['case_id'] for r in reconstructed])
        def simple_edge(e):
            if e is None:return None
            return {'producer_id':e['producer_id'],'root':e['root'],**{k:{'root':e[k]['root'],'role':e[k]['role'],'source_id':e[k]['source_group_id']} for k in ('origin','destination')}}
        for old,expected,r in zip(cases,reconstructed,reported['rows']):
            cid=expected['case_id']; gs=old['complete_line_groups']
            ck('full_line_retained:'+cid,r['complete_line_groups']==gs and r['metadata']==old['metadata'] and r['native_raw_groups_in_order']==[g['ivtff_group_raw'] for g in gs])
            ck('diagnostic_local:'+cid,r['local']['status']==expected['local_status'])
            ck('diagnostic_unknowns:'+cid,r['whole_context']['unknown_group_ids']==expected['unknown_group_ids'] and r['whole_context']['status']=='unknown')
            allprod=[(g['source_group_id'],local(gs,i)['status']) for i,g in enumerate(gs) if g['ivtff_group_raw']=='qokedy']
            ck('all_local_heads:'+cid,[(a['producer_id'],a['status']) for a in r['all_qokedy_constructions_in_line']]==allprod)
            consumed=set()
            for i,g in enumerate(gs):
                if g['ivtff_group_raw']=='qokedy' and local(gs,i)['status']=='compatible':consumed.update(x['source_group_id'] for x in gs[i-1:i+2])
            ck('unconsumed_scope:'+cid,r['whole_context']['unconsumed_or_scope_unresolved_group_ids']==[g['source_group_id'] for g in gs if g['source_group_id'] not in consumed])
            ck('prior_classification_retained:'+cid,r['predecessor']['classification']==old['classification'] and r['predecessor']['outcome']==old['outcome'] and r['predecessor']['old_recipe_and_product_semantics_imported'] is False)
            for policy in POLICIES:
                rp=r['policy_results'][policy]
                ck('diagnostic_policy:'+cid+':'+policy,simple_edge(rp['conditional_local_edge'])==expected['policy_edges'][policy] and rp['local_status']==expected['local_status'] and rp['whole_status']=='unknown' and rp['endpoint_assertion_tested'] is False)
            ck('no_unbound_reference_claim:'+cid,all(x['status']=='unknown' and x['conditional_selected_producer'] is None for x in r['whole_context']['reference_obligations']))
        ck('diagnostic_aggregates',reported['totals']['cases']==35 and all(reported['totals']['local'][k]==totals.get(k,0) for k in ['compatible','contradiction','unknown','not_applicable']) and reported['totals']['whole_context']['unknown']==35)
    author_checked=False
    if (ART/'AUTHOR_LOCK.json').exists():
        lock=read(ART/'AUTHOR_LOCK.json')
        ck('author_lock_release_pin',sha(ART/'AUTHOR_LOCK.json')=='993147a54c2cde15d8c8c2ea05ff1103abe4e2d872c1c944f56b2ea6d2333208')
        for path,h in lock['files'].items():ck('author_pin:'+path,sha(ROOT/path)==h)
        account=read(ART/'AUTHOR_ACCOUNT.json')
        ck('all97_native_source_exact',account['native_source']==source)
        original_it=[g for g in source['rows'] if g['edition']=='IT2a']
        contributions=account['contributions']; extensions=account['extension_lexicon']
        ck('all32_contributions_order',[c['source_group_id'] for c in contributions]==[g['source_group_id'] for g in original_it])
        counts=Counter(); byword={}
        for g,c in zip(original_it,contributions):
            w=g['ivtff_group_raw']; status='CORE_C0' if w in LICENSED else ('EXTENSION_C0' if w in extensions else 'UNKNOWN');counts[status]+=1
            ck('native_contribution:'+g['source_group_id'],c['native_row']==g and c['raw']==w and c['lexical_status']==status)
            ck('contribution_accounted:'+g['source_group_id'],bool(c['meaning']) and bool(c['attachment']) and bool(c['attachment_debt']))
            byword.setdefault(w,set()).add(c['meaning'])
            if status=='UNKNOWN':ck('unknown_unresolved:'+g['source_group_id'],c['scope_status']=='UNRESOLVED' and c['meaning']=='UNKNOWN['+w+']')
        ck('no_per_occurrence_lexical_change',all(len(v)==1 for v in byword.values()))
        unknowns=[c['source_group_id'] for c in contributions if c['lexical_status']=='UNKNOWN']
        cov=account['lexical_coverage']; caps=account['cap_ledger']
        ck('coverage_actual_counts',cov['core_c0_positions']==counts['CORE_C0']==12 and cov['extension_c0_positions']==counts['EXTENSION_C0']==7 and cov['unknown_positions']==counts['UNKNOWN']==13 and cov['complete_translation'] is False)
        ck('unbound_core_parameter',cov['unbound_core_parameters']==['IT2a|f83r.26|G002'] and next(c for c in contributions if c['source_group_id']=='IT2a|f83r.26|G002')['scope_status']=='UNBOUND_PARAMETER')
        ck('all_unknown_dependencies',[d['source_group_id'] for d in account['unknown_dependencies']]==unknowns+cov['unbound_core_parameters'])
        ck('binding_choices_all32',account['binding_choices']['count']==32 and account['binding_choices']['items']==[{'source_group_id':c['source_group_id'],'attachment':c['attachment'],'debt':c['attachment_debt']} for c in contributions])
        roots=sorted({r for v in extensions.values() for r in v['roots']}); heads=sorted({h for v in extensions.values() for h in v['heads']})
        for name,actual,maximum in [('additional_content_roots',roots,3),('additional_functional_heads',heads,4),('exceptional_whole_form_entries',sorted(extensions),8)]:
            ck('caps_recomputed:'+name,sorted(caps[name]['items'])==actual and caps[name]['count']==len(actual)<=maximum)
        ck('construction_cap',caps['constructions_total']['count']==len(caps['constructions_total']['items'])==6)
        ck('extensions_fixed_small_set',set(extensions)=={'qokeedy','qolchey','otchey','qoky'} and not(set(extensions)&LICENSED))
        ck('connected_unknown_repeats',all(account['connected_reading'].count('UNKNOWN['+w+']')==sum(c['raw']==w and c['lexical_status']=='UNKNOWN' for c in contributions) for w in {c['raw'] for c in contributions if c['lexical_status']=='UNKNOWN'}))
        def author_edge(e):
            if e is None:return None
            return {'producer_id':e['producer'],'root':e['root'],**{k:{'root':e[k]['root'],'role':e[k]['role'],'source_id':e[k]['source_group_id']} for k in ('origin','destination')}}
        ck('three_authored_policies',[e['policy'] for e in account['policy_executions']]==list(POLICIES))
        for e in account['policy_executions']:
            policy=e['policy']; expected=core_results[policy]; outcome=expected['endpoint_check']; suffix=itgroups[26:] if outcome['status']=='FAIL' else []
            ck('author_actual_edges:'+policy,[author_edge(x) for x in e['relations']]==expected['edges'])
            ck('author_returned_edge:'+policy,author_edge(e['returned_relation'])==expected['edges'][0])
            consumer=e['consumer'];endpoint=consumer['consumed_endpoint']
            ck('author_actual_consumer:'+policy,e['status']==e['conditional_core_result']==consumer['result']==outcome['status'] and consumer['consumed_producer']==outcome['producer_id'] and {'root':endpoint['root'],'role':endpoint['role'],'source_id':endpoint['source_group_id']}==outcome['endpoint'] and consumer['source_group_id']=='IT2a|f83r.29|G003' and consumer['named_active']['source_group_id']=='IT2a|f83r.29|G002')
            ck('failed_tail_not_executed:'+policy,e['not_executed_tail']==[g['source_group_id'] for g in suffix])
            ck('whole_scope_blocked:'+policy,e['whole_execution']=={'status':'BLOCKED_UNKNOWN_SCOPE','first_blocker':unknowns[0],'first_blocker_raw':'otal','no_whole_assertion':True})
            trace=e['trace']; tedges=[x['relation'] for x in trace if x['event']=='relation_produced'];tref=[x for x in trace if x['event']=='relation_reference'];tc=[x for x in trace if x['event']=='endpoint_consumer']
            ck('trace_producer_reference_consumer:'+policy,tedges==e['relations'] and len(tref)==len(tc)==1 and tref[0]['returned_relation']==e['returned_relation'] and tref[0]['candidate_producers']==[outcome['producer_id']] and tc[0]['consumed_endpoint']==endpoint and tc[0]['result']==outcome['status'])
            omitted={g['source_group_id'] for g in suffix}
            ck('trace_unknown_scope_retained:'+policy,[x['source_group_id'] for x in trace if x['event']=='UNRESOLVED_SCOPE']==[u for u in unknowns if u not in omitted])
        ck('partial_decision_not_lexical_success',account['status']==lock['status']=='PARTIAL_NO_COMPLETE_READING' and bool(unknowns))
        author_checked=True
    probes_checked=False; result_checked=False
    if author_checked and (ART/'ROOT_PROBES.json').exists():
        rootprobes=read(ART/'ROOT_PROBES.json')
        names=['baseline','delete_selected_edge','change_relation_root','swap_endpoints','toggle_origin_role','change_origin_root','forge_producer_id','substitute_other_written_producer']
        ck('root_probe_pins',rootprobes['author_lock_sha256']==sha(ART/'AUTHOR_LOCK.json') and rootprobes['probe_code_sha256']==sha(BASE/'src/probe_author.py'))
        ck('all24_probes_order',[(r['policy'],r['intervention']) for r in rootprobes['rows']]==[(p,n) for p in POLICIES for n in names])
        independently_expected=[]
        for row in rootprobes['rows']:
            policy,name=row['policy'],row['intervention']; execution=row['result']; edges=copy.deepcopy(core_results[policy]['edges'])
            first=edges[0]
            if name=='delete_selected_edge':edges=edges[1:]
            elif name=='change_relation_root':first['root']='LOVE'
            elif name=='swap_endpoints':first['origin'],first['destination']=first['destination'],first['origin']
            elif name=='toggle_origin_role':first['origin']['role']='RECEPTIVE' if first['origin']['role']=='ACTIVE' else 'ACTIVE'
            elif name=='change_origin_root':first['origin']['root']='LOVE'
            elif name=='forge_producer_id':first['producer_id']='INTERVENTION_ONLY_NO_WRITTEN_PRODUCER'
            elif name=='substitute_other_written_producer':first['producer_id']='IT2a|f83r.28|G004'
            # Explicit provenance guard: changing a producer ID while retaining the old
            # written argument ownership does not establish a different real producer.
            valid=[e for e in edges if not(e is first and name in ['forge_producer_id','substitute_other_written_producer'])]
            expected=consume(valid,policy)
            wanted='UNKNOWN' if expected['status']=='NO_REFERENCE' else expected['status']
            tag=policy+':'+name
            ck('probe_actual_mutated_edges:'+tag,[author_edge(e) for e in execution['relations']]==edges)
            ck('probe_consumer_result:'+tag,execution['status']==execution['conditional_core_result']==execution['consumer']['result']==wanted)
            expected_return=next((e for e in reversed(valid) if e['root']=='UNDERSTAND'),None)
            ck('probe_actual_returned_edge:'+tag,author_edge(execution['returned_relation'])==expected_return)
            if expected_return:
                endpoint=execution['consumer']['consumed_endpoint']
                ck('probe_actual_consumed_endpoint:'+tag,{'source_id':endpoint['source_group_id'],'root':endpoint['root'],'role':endpoint['role']}==expected['endpoint'] and execution['consumer']['consumed_producer']==expected['producer_id'])
            else:
                ck('probe_no_invented_endpoint:'+tag,'consumed_endpoint' not in execution['consumer'])
            tails=[g['source_group_id'] for g in itgroups[26:]] if wanted!='PASS' else []
            ck('probe_inactive_tail:'+tag,execution['not_executed_tail']==tails)
            ck('probe_whole_still_blocked:'+tag,execution['whole_execution']['status']=='BLOCKED_UNKNOWN_SCOPE' and execution['whole_execution']['first_blocker']=='IT2a|f83r.25|G006')
            if name=='baseline':ck('probe_exact_baseline:'+tag,execution==next(e for e in account['policy_executions'] if e['policy']==policy))
            independently_expected.append({'policy':policy,'intervention':name,'expected_result':wanted,'returned_producer':expected['producer_id']})
        probes_checked=True
    if author_checked and (ART/'RESULT.json').exists():
        result=read(ART/'RESULT.json')
        ck('final_result_pins',result['author_lock_sha256']==sha(ART/'AUTHOR_LOCK.json') and result['author_account_sha256']==sha(ART/'AUTHOR_ACCOUNT.json') and result['core_sha256']==sha(BASE/'src/CORE_FREEZE.json') and result['diagnostics_sha256']==sha(ART/'DIAGNOSTICS.json'))
        ck('final_status_and_coverage',result['status']=='PARTIAL_NO_COMPLETE_READING' and result['accounting']==cov and result['unknown_position_ids']==unknowns and result['unbound_core_parameter_ids']==cov['unbound_core_parameters'] and result['whole_context_blocked'] is True)
        for name,maximum in [('additional_content_roots',3),('additional_functional_heads',4),('constructions_total',6),('exceptional_whole_form_entries',8)]:
            ck('final_cap:'+name,result['cap_checks'][name]=={'count':caps[name]['count'],'limit':maximum,'within_cap':caps[name]['count']<=maximum})
        ck('final_policy_records',result['policy_results']==[{k:e[k] for k in ['policy','conditional_core_result','whole_execution','returned_relation','consumer','not_executed_tail']} for e in account['policy_executions']])
        ck('final_diagnostic_totals',result['diagnostic_totals']==reported['totals'] and result['diagnostic_by_reader']==reported['by_reader'])
        for reader in ('IT2a','RF1b','ZL3b'):
            selected=[r for r in reconstructed if r['edition']==reader]; rc=result['diagnostic_by_reader'][reader]
            ck('independent_reader_aggregate:'+reader,rc['cases']==len(selected) and rc['whole_context']['unknown']==len(selected) and all(rc['local'][k]==sum(r['local_status']==k for r in selected) for k in ['compatible','contradiction','unknown','not_applicable']))
        ck('no_confirmed_word_or_holdout',result['confirmed_words']==result['independent_meaning_confirmation_capacity']==result['new_target_access']==0)
        result_checked=True



    output={'status':('PASS' if all(c['pass'] for c in checks) else 'FAIL') if probes_checked and result_checked else 'PENDING_REMAINING_OUTPUTS','checks':checks,'independent_core':core_results,'independent_interventions':probes,'independent_diagnostics':reconstructed,'diagnostic_totals':totals,'root_probe_predictions':independently_expected if probes_checked else [],'validated_output_hashes':{name:sha(ART/name) for name in ['AUTHOR_LOCK.json','AUTHOR_ACCOUNT.json','DIAGNOSTICS.json','ROOT_PROBES.json','RESULT.json'] if (ART/name).exists()},'limitations':['Conditional reconstruction is not semantic truth.','Source schema excerpts were inspected after public release but before local pin assertions; hashes matched before computation.','Standalone generic-edge rename probe intentionally separates provenance from truth. The actual author reference adds a source/argument provenance guard, independently checked by rejecting both forged and substituted producer IDs in ROOT_PROBES.','Manual review: six listed constructions include three additions; unresolved complementary attachments are disclosed, not completed. Full semantic truth and historical source identity are not validated.']}
    (ART/'VALIDATION.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'checks':len(checks),'failed':[c for c in checks if not c['pass']],'diagnostics':totals,'status':output['status']}))
    return int(any(not c['pass'] for c in checks))
if __name__=='__main__':raise SystemExit(main())
