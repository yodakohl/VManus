from collections import Counter
from common import *
from model import compile_reading,execute
from independent import fact_violations

check_lock(); assert read(A/'PUBLIC_REGISTRATION.json')['commit']
s=source();cfg=spec();lex=s['all_30_new_lexical_entries'];ws=worlds()
lines=s['target']['complete_raw_record']['lines']
graphs=[]; rows=[]; traces=[]; summary=[]
for c in cfg['candidates']:
    g=compile_reading(lines,lex,c);assert g['status']=='COMPLETE',g
    graphs.append(g); coherent=0; self_coherent=0; counts_by_seed={}
    for seedcase,counts in enumerate(cfg['seed_cases']):
        allowed=0
        for w in ws:
            out=execute(g,counts,w)
            violations=fact_violations(c,counts,w)
            assert out['coherent']==(not violations),(c,counts,w)
            rows.append(dict(candidate=c['id'],seed_case=seedcase,world=w['id'],coherent=int(out['coherent']),all_violations='|'.join(violations) or '[]',first_failure_step=out['first_failure_step'] or 0,first_violations='|'.join(out['first_violations']) or '[]',completed_actions=out['completed_actions']))
            coherent+=out['coherent'];allowed+=out['coherent']
            self_coherent+=out['coherent'] and w['actor']==w['recipient']
        counts_by_seed[str(seedcase)]=allowed
    for mode in ['NONE']+cfg['countercases']:
        w=good_world();out=execute(g,[4],w,mode,True)
        traces.append(dict(candidate=c['id'],case=mode,counts=[4],world=w,output=out))
    if c['knowledge']=='DIFFERENT_OBJECTS':
        w=dict(id='SELF_WITNESS',actor='A',recipient='A',knowledge={'A':dict(P_rite=False,P_attach=True,P_purpose=False)},purity={'A':True})
        traces.append(dict(candidate=c['id'],case='SELF_WITNESS',counts=[4],world=w,output=execute(g,[4],w,store_trace=True)))
    summary.append(dict(candidate=c['id'],quantity=c['quantity'],knowledge=c['knowledge'],purity=c['purity'],total=1904,coherent=coherent,contradicted=1904-coherent,self_coherent=self_coherent,coherent_by_seed=counts_by_seed,extra_countercases=6,independent_meaning_capacity=0))
table(A/'CASES.tsv',rows);write(A/'WORLDS.json',ws);write(A/'GRAPHS.json',graphs);write(A/'TRACES.json',traces)
table(A/'CANDIDATES.tsv',[{**{k:v for k,v in x.items() if k!='coherent_by_seed'},'coherent_by_seed':json.dumps(x['coherent_by_seed'])} for x in summary])
positions=[];p=0
for line in lines:
    for w,sid in zip(line['words'],line['source_ids']):
        p+=1; entry=lex[w]
        clause=next(cl for cl in s['complete_clauses'] if cl['inclusive_positions'][0]<=p<=cl['inclusive_positions'][1])
        positions.append(dict(position=p,locus=line['locus'],source_id=sid,word=w,tag=entry['tag'],hypothetical_value=entry['meaning'],clause=clause['id'],anchor_eligible=line['anchor_eligible'],different_object_change='chey:P_attach replaces P_rite' if w=='chey' else '[]',confirmed_meaning=0))
table(A/'ALL_POSITIONS.tsv',positions)
scope={}
for rd,key in [('ZL3b','complete_raw_record'),('IT2a','IT2a_complete_alternative')]:
    rec=s['target'][key];comp=compile_reading(rec['lines'],lex,cfg['candidates'][0])
    scope[rd]=dict(groups=rec['groups'],status=comp['status'],unknown=comp.get('unknown',[]),ineligible_lines=[l['locus'] for l in rec['lines'] if not l['anchor_eligible']],record=rec)
packet=read(R/s['source_bindings'][2]['path'])
rf=[p for p in packet['RF1b'] if p['id']==s['target']['id']]
scope['RF1b']=dict(complete_matching_paragraphs=len(rf),records=rf)
write(A/'DIPLOMATIC_SCOPE.json',scope)
counts=Counter(w for l in lines for w in l['words'])
result=dict(experiment='GDT1027',status='EXECUTED_PENDING_VALIDATION',utc=now(),whole_groups=p,exact_types=len(counts),singleton_types=sum(n==1 for n in counts.values()),clauses=5,baseline_binding_assumptions=11,inherited_meanings=0,main_new_values=30,different_object_changed_macro_values=1,literally_shared_values=29,candidates=summary,case_rows=len(rows),coherent_rows=sum(r['coherent'] for r in rows),countercase_traces=48,total_stored_traces=len(traces),confirmed_words=0,independent_meaning_capacity=0,clinical_effects_observed=0,decision='Retain coherent new-family readings provisionally; participant distinctness depends on the knowledge-object assumption. Do not rank by truth-world counts; Greek source actor-purity fidelity separate from internal consistency.')
write(A/'RESULT.json',result)
print(json.dumps({k:result[k] for k in ['status','case_rows','coherent_rows','confirmed_words']}))
