from common import *
from independent import recognize_reverse,verify
import csv

def main():
    check_lock();s=source();sp=spec();p=read(R/s['frozen_family']['parent_path']);p0=read(R/p['frozen_parent']['path'])
    lex={**p0['lexicon'],**p['new_18_lexical_entries']};assert lex==s['frozen_family']['all71_entries_unchanged']
    assert p['frozen_parent']['all_53_lexical_entries_unchanged']==p0['lexicon']
    assert p['frozen_parent']['original_14_clauses_unchanged']==p0['whole_paragraph_clauses']
    assert p['frozen_parent']['original_grammar_unchanged']==p0['grammar_contract']
    assert p['frozen_parent']['original_semantic_contract_unchanged']==p0['semantic_contract']
    assert {k:sp['lexicon'][k] for k in lex}==lex and len(lex)==71 and len(sp['lexicon'])==91
    old=module('old_independent',OLD/'src/independent.py');second=module('second_independent',SECOND/'src/independent.py')
    sc=read(R/'research_registry/work_batches/ten_hours_20260915/ROTA_SOURCE_EVENTS.json');saved=read(OLD/'artifacts/PERFORMANCES.json');sg=read(SECOND/'artifacts/GRAPHS.json')
    clauses,raw=recognize_reverse(s['target']['full_record']['lines'],sp['lexicon'],s['complete_new_clauses'])
    assert len(raw)==55 and len(set(raw))==38 and sum(w in lex for w in raw)==32 and len(set(raw)&set(lex))==18
    assert [w for p in s['complete_new_clauses'] for w in p['raw'].split()]==raw
    assert [a['raw'] for a in s['target']['all55_assignments']]==raw
    for a in s['target']['all55_assignments']:
        assert a['entry']['tag']==sp['lexicon'][a['raw']]['tag'] and a['entry']['meaning']==sp['lexicon'][a['raw']]['meaning']
    rows=read(A/'ROWS.json');graphs=read(A/'GRAPHS.json');pred=list(csv.DictReader((A/'PREDICTIONS.tsv').open(),delimiter='\t'));assert len(rows)==len(pred)==24
    checks=[];event_count=0
    for n in sp['n']:
        parent=old.compile_reverse(p0['target']['owned_projection']['records'],p0['lexicon'],p0['whole_paragraph_clauses'],n)
        one=next(x for x in graphs if x['n']==n);g=one['bindings'];assert one['clauses']==clauses and one['raw_roundtrip']==raw
        rota=parent['rota'];leader=rota[0];u,l=parent['pes'];bank={v:('ENTER:'+v if v in rota else 'FIRST_PART_START:'+v+':'+parent['assigned'][v]) for v in rota+[u,l]}
        assert g==dict(leader=leader,upper=u,lower=l,followers=rota[1:],later=rota[2:],predecessor={v:rota[i] for i,v in enumerate(rota[1:])},event_bank=bank,cue=parent['source_referents']['cue'],same_performance=True,r_calls=[dict(follower=x,first=bank[x],second=bank[rota[rota.index(x)-1]],final=bank[leader]) for x in rota[2:]],qokaiin_roles=dict(F06=[leader],F10=[[leader,x] for x in rota[2:]]),F11_event_pairs=[[bank[x],bank[leader]] for x in rota[2:]])
        for branch in sc['documentary_duration_branches']:
            parts=parts_for(sc,branch);trace=old.execute_arithmetic(parent,parts)
            original=next(x for x in saved if x['n']==n and x['branch']==branch['id'] and x['mode']=='BASELINE')
            for k,v in trace.items():assert original[k]==v
            assert old.independently_check(parent,parts,trace)==[];event_count+=len(trace['events'])
            prior=next(x['new_graph'] for x in sg if x['n']==n and x['mode']=='BASELINE');assert second.check_relations(prior,parent,parts,trace,'BASELINE')==[]
            for mode in sp['models']:
                r=next(x for x in rows if x['n']==n and x['branch']==branch['id'] and x['mode']==mode)
                errors=verify(parent,parts,trace,mode);assert errors==r['errors']
                prediction=next(x for x in pred if int(x['n'])==n and x['branch']==branch['id'] and x['mode']==mode)
                assert r['status']==prediction['predicted_status']==('CONTRADICTED' if errors else 'COHERENT')
                assert r['ending_capacity']==prediction['ending_capacity'] and r['new_entry_executions']==0
                assert len(r['evidence'])==11 and r['complete_trace_events']==len(trace['events'])
                for cid in ['F05','F10','F11']:
                    assert r['evidence'][cid]['vacuous']==(n==2) and len(r['evidence'][cid]['instances'])==n-2
                for x in r['evidence']['F05']['instances']:
                    period=sum(e['ticks'] for e in parts['P2']);assert x['period']==period and x['phase_at_entry']==trace['starts'][x['follower']]%period
                    assert x['times']==[trace['starts'][x['follower']],trace['starts'][x['predecessor']]]
                for x in r['evidence']['F11']['instances']:
                    assert x['times']==[trace['starts'][x['roles'][0]],0] and x['events']==['ENTER:'+v for v in x['roles']]
                    assert x['co_onset']==x['together']==False and x['guard_attained'] and x['same_relation_as_F10']
                checks.append(dict(n=n,branch=branch['id'],mode=mode,errors=errors,status='PASS'))
    scope=read(A/'DIPLOMATIC_SCOPE.json');it=scope['alternate_readers'][0];assert it['whole_blocks'][0]['groups']==54 and [x['locus'] for x in it['issues']]==['f76v.38','f76v.39']
    assert it['issues'][0]['unknown']==['lolsaiiin'] and it['issues'][1]['actual_tags'][8]=='ANY_ROTA_SINGER'
    assert len(scope['ZL_new_ineligible_lines'])==4
    write(A/'INDEPENDENT.json',dict(status='PASS',checks=checks,original_baseline_intervals_replayed=event_count,scope='Unchanged old arithmetic full traces, old second-paragraph checks, reverse recognition and separate new set/arithmetic constraints. Same author; no independent meaning.'))
    write(A/'VALIDATION.json',dict(status='PASS',executed_utc=now(),model_cases=24,complete_source_traces=12,new_groups=55,joint_groups=150,confirmed_words=0,independent_meaning_capacity=0))
    print(json.dumps(read(A/'VALIDATION.json'),indent=2))
if __name__=='__main__':main()
