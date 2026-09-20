from common import *
import collections,concurrent.futures,csv

def ground(row,p,g,s,c):
    assert set(row['code'])==set(p['words']);cursor=0
    for clause in row['parse']:
        pattern=g['patterns'][clause['kind']]
        assert clause['start']==cursor and clause['end']==cursor+len(pattern);cursor=clause['end']
        assert clause['symbols']==[row['code'][w] for w in p['words'][clause['start']:clause['end']]]
        assert all(x in g['types'][t[1:]] if t.startswith('@') else x==t for x,t in zip(clause['symbols'],pattern))
    assert cursor==len(p['words']) and row['parse'][0]['kind']=='INITIAL' and row['parse'][-1]['kind']=='CONCLUSION'
    for kind in ['INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION']:assert sum(x['kind']==kind for x in row['parse'])==1
    if c:
        assert row['variant']==c['variant']
        for w,v in c['values'].items():
            if w in row['code']:assert row['code'][w]==v
    independent=replay(row['parse'],row['variant'],s,True)
    assert independent==row['replay'] and independent['status']=='COHERENT'

def task(args):
    p,primary=args;s,g=inputs();candidates=read(A/'CANDIDATE_PREDICTIONS.json');ind=load(s['independent'],'ind1003');begin=time.monotonic();checks=[]
    for base in [True,False]:
        solver,xs,num,other,there=ind.build([p],{} if base else base_roles(candidates),g,s['query_milliseconds'])
        for c in [None] if base else candidates:
            cid='UNPINNED' if c is None else c['id'];row=next(x for x in primary['rows'] if x['candidate']==cid)
            if row['status']=='sat':ground(row,p,g,s,c)
            solver.push()
            if c:
                for w,v in c['values'].items():
                    if w in xs:solver.add(xs[w]==num[v])
                solver.add(other==int(c['variant']['other']=='FIRST'),there==int(c['variant']['there']=='CURRENT'))
            remaining=s['paragraph_worker_seconds']-(time.monotonic()-begin)
            if remaining<=0:status='unknown_batch_limit'
            else:
                solver.set('tlimit-per',max(1,min(s['query_milliseconds'],int(remaining*1000))));status=str(solver.check())
            solver.pop()
            assert not ({status,row['status']}=={'sat','unsat'}),(p['id'],cid,row['status'],status)
            checks.append(dict(candidate=cid,primary=row['status'],cvc5=status,ground_replay_verified=row['status']=='sat'))
    return dict(paragraph=p['id'],checks=checks,wall_seconds=time.monotonic()-begin)

def main():
    checklock();s,g=inputs();panel=read(A/'PANEL.json');census=read(A/'CENSUS.json');candidates=read(A/'CANDIDATE_PREDICTIONS.json');rows=read(A/'ROWS.json');pred=read(A/'PREDICTIONS.json')
    assert len(census)==1349 and len(panel)==pred['query_paragraphs']
    # Independent reconstruction of complete scope/identity and literal ownership.
    actual=[];expected_panel=[]
    for edition,paragraphs in read(R/s['source_paragraphs']).items():
        for p in paragraphs:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            words=sum((line['words'] for line in p['lines']),[]);ids=sum((line['source_ids'] for line in p['lines']),[])
            scope='ORIGINAL_LEAF' if p['leaf']==83 else 'NO_EXACT_CHEDY' if 'chedy' not in words else 'BELOW_SCOPE' if len(words)<26 else 'ABOVE_SCOPE' if len(words)>37 else 'QUERY'
            entry=dict(id=edition+'|'+p['id'],edition=edition,paragraph=p['id'],page=p['page'],leaf=p['leaf'],groups=len(words),chedy_occurrences=words.count('chedy'),scope_status=scope,strict_anchor_eligible=all(x['anchor_eligible'] for x in p['lines']),independent_meaning_capacity=0)
            actual.append(entry)
            if scope=='QUERY':expected_panel.append(dict(**entry,words=words,source_ids=ids))
    assert actual==census and expected_panel==panel
    source=read(R/s['source_candidates'])
    for c,t in zip(candidates,source['positive_tuples']):
        assert c['values']==t['values'] and c['variant']==source['attempts'][t['attempt']]['replays'][t['variant_index']]['variant'] and c['original_tuple']==t['tuple']
    assert len(candidates)==36 and [r['paragraph'] for r in rows]==[p['id'] for p in panel]
    for r in rows:
        assert [q['candidate'] for q in r['rows']]==['UNPINNED',*[c['id'] for c in candidates]]
        assert not (r['rows'][0]['status']=='unsat' and any(q['status']=='sat' for q in r['rows'][1:]))
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==len(panel)*37
    for t,(p,r,q) in zip(table,[(p,r,q) for p,r in zip(panel,rows) for q in r['rows']]):
        assert t['paragraph']==p['id'] and t['candidate']==q['candidate'] and t['status']==q['status'] and json.loads(t['code'])==q.get('code',{}) and json.loads(t['variant'])==q.get('variant',{})
    checks=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:
        for c in pool.map(task,zip(panel,rows)):checks.append(c);print(json.dumps(dict(validated=len(checks),total=len(panel))),flush=True)
    put('INDEPENDENT_QUERIES.json',checks);flat=[x for c in checks for x in c['checks']]
    out=dict(status='PASS',whole_scope_rows=len(census),complete_paragraphs=len(panel),queries=len(flat),ground_positive_replays=sum(x['ground_replay_verified'] for x in flat),independent_counts=dict(collections.Counter(x['cvc5'] for x in flat)),independently_verified_negative_queries=sum(x['primary']==x['cvc5']=='unsat' for x in flat),unverified_primary_negatives=sum(x['primary']=='unsat' and x['cvc5']!='unsat' for x in flat),confirmed_words=0,independent_meaning_capacity=0,scope='Complete necessary projection transfer under fixed source grammar; no shared full original dictionary or independent meaning test.')
    put('VALIDATION.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
