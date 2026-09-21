from common import *
from independent import recognize,check_relations
import csv

def main():
    check_lock();s=source();p=read(R/s['frozen_parent']['path']);sc=score()
    assert s['frozen_parent']['all_53_lexical_entries_unchanged']==p['lexicon']
    assert s['frozen_parent']['original_14_clauses_unchanged']==p['whole_paragraph_clauses']
    assert s['frozen_parent']['original_grammar_unchanged']==p['grammar_contract']
    assert s['frozen_parent']['original_semantic_contract_unchanged']==p['semantic_contract']
    lex={**p['lexicon'],**s['new_18_lexical_entries']}
    old=module('old_independent',OLD/'src/independent.py');saved=read(OLD/'artifacts/PERFORMANCES.json')
    rows=read(A/'ROWS.json');graphs=read(A/'GRAPHS.json');pred=list(csv.DictReader((A/'PREDICTIONS.tsv').open(),delimiter='\t'))
    assert len(rows)==len(pred)==60 and len(graphs)==15
    checks=[];events=0
    for n in (2,3,4):
        parent=old.compile_reverse(p['target']['owned_projection']['records'],p['lexicon'],p['whole_paragraph_clauses'],n)
        for branch in sc['documentary_duration_branches']:
            parts={k:[] for k in ('M','P1','P2')}
            for name in parts:
                for e in sc['events']:
                    if e['part']!=name:continue
                    d=Fraction(branch['changes'].get(e['id'],sc['baseline_conditional_duration_breves'][e['id']]))
                    assert (2*d).denominator==1
                    parts[name].append(dict(id=e['id'],ticks=int(2*d),kind={'note':'note','pause':'rest'}[e['kind']],pitch=(e.get('pitch_reading') or {}).get('midi_under_c4_octave_convention')))
            trace=old.execute_arithmetic(parent,parts)
            original=next(x for x in saved if x['n']==n and x['branch']==branch['id'] and x['mode']=='BASELINE')
            for key,value in trace.items():assert original[key]==value
            assert old.independently_check(parent,parts,trace)==[]
            events+=len(trace['events'])
            for mode in read(E/'src/SPEC.json')['models']:
                g=next(x['new_graph'] for x in graphs if x['n']==n and x['mode']==mode)
                clauses,raw=recognize(s['complete_new_block_clauses'],lex,s['complete_new_block_clauses'])
                assert g['clauses']==clauses and g['raw_roundtrip']==raw
                assert [i for c in clauses for i in range(c['start'],c['end'])]==list(range(33))
                assert len(raw+parent['raw_roundtrip'])==95 and len(set(raw+parent['raw_roundtrip']))==71
                assert len(set(raw)&set(p['lexicon']))==6 and sum(w in p['lexicon'] for w in raw)==9
                assert g['parent_roles']==dict(rota=parent['rota'],pes=['U','L'],leader='R0')
                assert g['sole_starter']=='R0' and g['case_binding']=='next explicit ROTA: f83r.31'
                bank={v:('ENTER:'+v if v in parent['rota'] else 'FIRST_PART_START:'+v+':'+parent['assigned'][v]) for v in parent['rota']+['U','L']}
                assert g['event_bank']==bank
                members=['U','U'] if mode=='DUPLICATE_PES_CURSOR' else ['U','L']
                assert g['pes_enumeration']==members and g['cursor_final']==2
                assert g['onset_declarations']==[dict(clause='D01',events=[bank[v] for v in ['R0','U','L']],kind='INITIAL'),dict(clause='D03',events=[bank[v] for v in ['R0']+members],kind='RESTATE')]
                assert g['co_onset_pairs']==[['R0','U','L'],['U','R0']]
                assert g['upper']=='U' and g['lower']=='L' and g['preserve_cycles']==['U','L']
                assert g['silent_at_initial']==parent['rota'][1:]
                companions=['U','L'] if mode=='COMPANIONS_AS_PES' else parent['rota']
                assert g['companions']==companions and g['group_disjoint']==[['U','L'],companions]
                result=next(x for x in rows if x['n']==n and x['branch']==branch['id'] and x['mode']==mode)
                issues=check_relations(g,parent,parts,trace,mode)
                assert result['errors']==issues
                prediction=next(x for x in pred if int(x['n'])==n and x['branch']==branch['id'] and x['mode']==mode)
                assert result['status']==prediction['predicted_status']==('CONTRADICTED' if issues else 'COHERENT')
                assert result['complete_trace_events']==len(trace['events'])
                if mode=='EVERY_MENTION_EXECUTES':
                    steps=result['evidence']['literal_mentions'];assert len(steps)==4 and steps[-1]['already_active'] and steps[-1]['event']=='ENTER:R0'
                if mode=='CO_ONSET_EVERY_MAIN_CYCLE':
                    actual=result['evidence']['every_main_cycle']
                    expected_times=list(range(0,trace['window_end'],sum(x['ticks'] for x in parts['M'])))
                    assert [x['time_ticks'] for x in actual]==expected_times
                    for row in actual:
                        for v in ('U','L'):assert row['pes_first_event'][v]==(row['time_ticks']%sum(x['ticks'] for x in parts[parent['assigned'][v]])==0)
                checks.append(dict(n=n,branch=branch['id'],mode=mode,status='PASS',errors=issues))
            it=next(x for x in read(A/'CONDITIONAL_IT.json') if x['n']==n and x['branch']==branch['id'])
            assert it['status']=='CONTRADICTED' and len(it['rows'])==n
            assert all(x['part']=='M' and x['terminal_event']==parts['M'][-1]['id'] and x['has_terminal_rest'] and x['violates_new_without_terminal_rest'] for x in it['rows'])
    scope=read(A/'DIPLOMATIC_SCOPE.json')
    assert [x['raw'] for x in scope['ZL_unbound']]==["salche'dy",'saii@208;','[?:s]cheol','so[r:s]']
    bad=next(x for x in scope['IT_issues'] if x['locus']=='f83r.29')
    assert bad['actual_tags'][0]=='EACH_ROTA_SINGER' and bad['required_tags'][0]=='LOWER_PES_REFERENCE' and not bad['unknown']
    write(A/'INDEPENDENT.json',dict(status='PASS',checks=checks,full_original_baseline_intervals_compared=events,implementation='Reverse new recognizer, relational checker and unchanged old arithmetic replay; same author, no independent meaning.'))
    write(A/'VALIDATION.json',dict(status='PASS',executed_utc=now(),model_cases=60,baseline_cases=12,conditional_IT_cases=12,projected_groups=95,new_types=18,old_types_reused=6,raw_forms_unbound=4,confirmed_words=0,independent_meaning_capacity=0))
    print(json.dumps(read(A/'VALIDATION.json'),indent=2))

if __name__=='__main__':main()
