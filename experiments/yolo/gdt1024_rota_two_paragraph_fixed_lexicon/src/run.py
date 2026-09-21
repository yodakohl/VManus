from common import *
from model import compile_new,check_new,conditional_it

def main():
    check_lock();assert (A/'PUBLIC_REGISTRATION.json').exists();begun=now()
    s=source();spec=read(E/'src/SPEC.json');p=read(R/s['frozen_parent']['path']);sc=score()
    old=module('old_forward',OLD/'src/model.py')
    saved_graphs=read(OLD/'artifacts/GRAPHS.json');saved_traces=read(OLD/'artifacts/PERFORMANCES.json')
    lex={**p['lexicon'],**s['new_18_lexical_entries']};rows=[];graphs=[];conditional=[]
    assert not set(p['lexicon'])&set(s['new_18_lexical_entries'])
    for n in spec['n']:
        parent=old.compile_reading(p['target']['owned_projection']['records'],p['lexicon'],p['whole_paragraph_clauses'],n)
        assert parent==next(x['graph'] for x in saved_graphs if x['n']==n)
        for mode in spec['models']:
            g=compile_new(s['complete_new_block_clauses'],lex,s['complete_new_block_clauses'],parent,mode)
            graphs.append(dict(n=n,mode=mode,new_graph=g,parent_graph_reference='GDT1022/artifacts/GRAPHS.json n='+str(n)))
            for b in sc['documentary_duration_branches']:
                parts=parts_for(sc,b);trace=next(x for x in saved_traces if x['n']==n and x['branch']==b['id'] and x['mode']=='BASELINE')
                assert old.evaluate_contract(parent,parts,trace)==[]
                result=check_new(g,parent,parts,trace,mode)
                rows.append(dict(n=n,branch=b['id'],mode=mode,complete_trace_events=len(trace['events']),**result))
                if mode=='BASELINE':conditional.append(dict(n=n,branch=b['id'],**conditional_it(parent,parts)))
    write(A/'GRAPHS.json',graphs);write(A/'ROWS.json',rows);write(A/'CONDITIONAL_IT.json',conditional)
    it=s['target']['complete_IT_enclosing_block'];clauses=s['complete_new_block_clauses']+p['whole_paragraph_clauses'];issues=[]
    for line,c in zip(it['lines'],clauses):
        unknown=[w for w in line['words'] if w not in lex];tags=[lex[w]['tag'] if w in lex else 'UNBOUND:'+w for w in line['words']]
        if tags!=c['terminal_tags']:issues.append(dict(locus=line['locus'],raw=line['words'],unknown=unknown,actual_tags=tags,required_tags=c['terminal_tags'],status='NOT_ACCEPTED_BY_FIXED_GRAMMAR'))
    zunknown=[]
    for k in ['complete_ZL_new_block','complete_ZL_parent_block']:
        for line in s['target'][k]['lines']:
            for i,w in enumerate(line['words'],1):
                if w not in lex:zunknown.append(dict(locus=line['locus'],group=i,raw=w))
    write(A/'DIPLOMATIC_SCOPE.json',dict(ZL_unbound=zunknown,IT_complete_groups=it['groups'],IT_issues=issues,IT_status='NO_COMPLETE_FIXED_READING',independent_confirmation=False))
    write(A/'RESULT.json',dict(status='COMPLETED_PENDING_VALIDATION',started_utc=begun,finished_utc=now(),projected_groups=95,old_types=53,new_types=18,joint_types=71,reused_old_types=6,reused_old_positions=9,models={m:{v:sum(x['mode']==m and x['status']==v for x in rows) for v in ['COHERENT','CONTRADICTED']} for m in spec['models']},conditional_IT_cases=len(conditional),confirmed_words=0,independent_meaning_capacity=0))
    print(json.dumps(read(A/'RESULT.json'),indent=2))

if __name__=='__main__':main()
