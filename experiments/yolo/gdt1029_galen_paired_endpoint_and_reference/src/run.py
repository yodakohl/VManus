from collections import defaultdict
from common import *
from model import compile_pair,evaluate,projection,no,PM
PI=load_parent('independent')
check_lock();assert read(A/'PUBLIC_REGISTRATION.json')['commit']
s=source();cfg=spec();lex=lexicon(s);old_s=parent_source()
old_lines=old_s['target_choice']['whole_record']['lines'];new_record=s['first_three_records'][0]['whole_record'];new_lines=new_record['lines']
graphs=[];outputs=[];rows=[];summaries=[]
for c in cfg['candidates']:
    g=compile_pair(old_lines,new_lines,lex,c);assert g['status']=='COMPLETE_POSITION_GRAPH',g
    graphs.append(g);cr=[]
    for f in cases() if c['kind']=='SEMANTIC' else [dict(name='STATIC_WHOLE_GRAPH')]:
        o=evaluate(g,f);r=projection(c,f['name'],o);rows.append(r);cr.append(r)
        outputs.append(dict(candidate=c['id'],case=f['name'],output=o))
    summaries.append(dict(candidate=c['id'],kind=c['kind'],checked_rows=len(cr),facts_compatible=sum(r['status']=='COMPATIBLE_WITH_HYPOTHETICAL_FACTS' for r in cr),facts_contradicted=sum(r['status']=='CONTRADICTED_BY_HYPOTHETICAL_FACTS' for r in cr),static_contradictions=sum(r['status']=='STATIC_CONTRADICTION' for r in cr),binding_gaps=sum(r['status']=='UNBOUND_SEMANTIC_GENERALIZATION' for r in cr),norm_conformant=sum(r['norm_conformant']==1 for r in cr),ordinary_endpoint_observed=sum(r['ordinary_endpoint']=='OBSERVED_IN_FIXTURE' for r in cr),parent_values_literal=g['literal_parent_values'],broadened_parent_values=len(g['parent_broadening']),modified_new_values=len(g['new_value_rebindings']),independent_meaning_capacity=0))
table(A/'CASES.tsv',rows);table(A/'CANDIDATES.tsv',summaries);write(A/'GRAPHS.json',graphs);write(A/'OUTPUTS.json',outputs)
# Old program and all old fixtures are replayed in memory; parent artifacts are never overwritten.
parent_rows=[];no_checks=0;old_lex={e['form']:e for e in old_s['lexicon']}
for c in read(P/'src/SPEC.json')['candidates']:
    g=PM.compile_reading(old_lines,old_lex,c);assert g['status']=='COMPLETE_GRAPH'
    for f in read(P/'src/CASES.json') if c['syntax']=='QUOTED_FOOD_TRANSFER' else [dict(name='STATIC_WHOLE_GRAPH')]:
        o=PM.evaluate(g,f);PI.validate_output(c,f,g,o);parent_rows.append(PI.observe(c,f['name'],o))
        if o['status']!='STATIC_CONTRADICTION':
            k='J' if c['ownership']=='INTRINSIC' else 'K'
            assert no(['P_D','P_E'],lambda x:f['can_retain_all'][x][k])==(not any(v.startswith('C04_FULL_RETENTION_CAPACITY:') for v in o['violations']))
            no_checks+=1
table(A/'PARENT_REPLAY.tsv',parent_rows);assert read_table(A/'PARENT_REPLAY.tsv')==read_table(P/'artifacts/CASES.tsv')
write(A/'PARENT_REPLAY.json',dict(rows=len(parent_rows),generalized_no_original_capability_instantiations=no_checks,exact_old_projection_reproduced=True,parent_artifacts_modified=False,new_meaning_evidence=False))
positions=[];global_pos=0
for unit,record in [('II',old_s['target_choice']['whole_record']),('III',new_record)]:
    local=0
    for line in record['lines']:
        for w,sid in zip(line['words'],line['source_ids']):
            local+=1;global_pos+=1
            cl=old_s['token_receipt'][local-1]['clause'] if unit=='II' else s['exact_token_receipt'][local-1]['clause']
            positions.append(dict(position=global_pos,unit=unit,local_position=local,locus=line['locus'],source_id=sid,word=w,value=lex[w]['value'],denotation=lex[w]['denotation'],clause=cl,anchor_eligible=line['anchor_eligible'],value_status='BROADENED_QOKY' if w=='qoky' else 'LITERAL_PARENT' if w in old_lex else 'NEW',confirmed=0))
table(A/'ALL_POSITIONS.tsv',positions)
scope={}
for unit,rec in [('II',old_s['target_choice']['alternative_reader_records']['IT2a']),('III',s['first_three_records'][0]['alternatives']['IT2a'][0])]:
    ol=rec['lines'] if unit=='II' else old_lines;nl=rec['lines'] if unit=='III' else new_lines
    co=compile_pair(ol,nl,lex,cfg['candidates'][0]);scope[unit]=dict(reader='IT2a',groups=rec['groups'],status=co['status'],unknown=co.get('unknown',[]),whole_record=rec)
scope['RF1b']=dict(II=old_s['target_choice']['alternative_reader_records']['RF1b'],III=s['first_three_records'][0]['alternatives']['RF1b'])
write(A/'DIPLOMATIC_SCOPE.json',scope)
full=defaultdict(list);physical=defaultdict(list)
for c in cfg['candidates']:
    rr=[r for r in rows if r['candidate']==c['id']]
    full[json.dumps([{k:v for k,v in r.items() if k!='candidate'} for r in rr],sort_keys=True)].append(c['id'])
    if c['kind']=='SEMANTIC':physical[json.dumps([o['output']['parent_trace'] for o in outputs if o['candidate']==c['id']],sort_keys=True)].append(c['id'])
write(A/'EQUIVALENCE.json',dict(full_case_projection=list(full.values()),old_physical_trace_projection=list(physical.values()),meaning='conditional model equality, not empirical confirmation'))
result=dict(experiment='GDT1029',status='EXECUTED_PENDING_VALIDATION',utc=now(),whole_groups=global_pos,combined_types=len(set(x['word'] for x in positions)),new_groups=46,literal_old_values=35,broadened_old_values=1,new_forms=31,new_productions=6,new_assumptions=26,candidates=summaries,new_case_rows=len(rows),facts_compatible=sum(r['status']=='COMPATIBLE_WITH_HYPOTHETICAL_FACTS' for r in rows),facts_contradicted=sum(r['status']=='CONTRADICTED_BY_HYPOTHETICAL_FACTS' for r in rows),static_contradictions=2,strict_binding_gaps=1,parent_replay_rows=len(parent_rows),parent_generalized_no_instantiations=no_checks,full_projection_classes=len(full),physical_projection_classes=len(physical),confirmed_words=0,independent_meaning_capacity=0,clinical_observations=0,decision='Retain a conditional95-group paired hypothesis with qoky broadening and explicit discontinuous bindings. Proper softness is distinct from ordinary softness; factual compatibility and instruction conformity remain separate. No source or word identification, no strict36 transfer success.')
write(A/'RESULT.json',result);print(json.dumps({k:result[k] for k in ['status','new_case_rows','facts_compatible','facts_contradicted','parent_replay_rows','confirmed_words']}))
