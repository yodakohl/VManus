from common import *
import collections,concurrent.futures,csv,subprocess,z3

def primary_query(b,c,world,s):
    solver=b['solver'];solver.push()
    if c:
        for w,v in c['values'].items():
            if w in b['xs']:solver.add(b['xs'][w]==b['num'][v])
            elif w in b['lexicon']:assert b['lexicon'][w]==v
        solver.add(b['other_first']==(c['variant']['other']=='FIRST'),b['there_current']==(c['variant']['there']=='CURRENT'))
    status=str(solver.check());out=dict(status=status)
    if status=='sat':
        witness=world.witness(b);parse=witness['parses'][0];code={w:{**b['lexicon'],**witness['aliases']}[w] for w in b['paragraphs'][0]['words']}
        if c:
            assert witness['variant']==c['variant']
            assert all(code[w]==v for w,v in c['values'].items() if w in code)
        detail=replay(parse,witness['variant'],s);assert detail['status']=='COHERENT'
        out.update(code=code,parse=parse,variant=witness['variant'],replay=detail)
    solver.pop();return out

def task(p):
    s,g=inputs();candidates=read(A/'CANDIDATE_PREDICTIONS.json');world=load(s['primary'],'world1003');start=time.monotonic();rows=[]
    base=world.build([p],{},g,s['query_milliseconds']);result=primary_query(base,None,world,s);rows.append(dict(candidate='UNPINNED',**result))
    b=world.build([p],base_roles(candidates),g,s['query_milliseconds'])
    for c in candidates:
        remaining=s['paragraph_worker_seconds']-(time.monotonic()-start)
        if remaining<=0:result=dict(status='unknown_batch_limit')
        else:
            b['solver'].set(timeout=max(1,min(s['query_milliseconds'],int(remaining*1000))))
            result=primary_query(b,c,world,s)
        rows.append(dict(candidate=c['id'],**result))
    return dict(paragraph=p['id'],rows=rows,wall_seconds=time.monotonic()-start)

def main():
    checklock();s,g=inputs();receipt=read(A/'PUBLIC_REGISTRATION.json');subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],check=True,cwd=R)
    panel=read(A/'PANEL.json');start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:
        results=[]
        for r in pool.map(task,panel):results.append(r);print(json.dumps(dict(done=len(results),total=len(panel))),flush=True)
    put('ROWS.json',results);counts=collections.Counter(row['status'] for r in results for row in r['rows']);candidate_counts={}
    for cid in ['UNPINNED',*[c['id'] for c in read(A/'CANDIDATE_PREDICTIONS.json')]]:
        candidate_counts[cid]=dict(collections.Counter(row['status'] for r in results for row in r['rows'] if row['candidate']==cid))
    put('RESULT.json',dict(experiment='GDT1007',status='PROJECTED_CONTEXT_SEARCH_COMPLETE',paragraphs=len(panel),query_rows=sum(len(r['rows']) for r in results),counts=dict(counts),candidate_counts=candidate_counts,confirmed_words=0,independent_meaning_capacity=0,full_original_dictionary_transfer=False,significance=False))
    put('EXECUTION_RECEIPT.json',dict(started_utc=start,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registration_commit=receipt['commit']))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['paragraph','candidate','status','strict_source','chedy_class','code','variant','independent_meaning_capacity'])
        cs={c['id']:c for c in read(A/'CANDIDATE_PREDICTIONS.json')};ps={p['id']:p for p in panel}
        for r in results:
            for q in r['rows']:w.writerow([r['paragraph'],q['candidate'],q['status'],ps[r['paragraph']]['strict_anchor_eligible'],cs[q['candidate']]['chedy_class'] if q['candidate']!='UNPINNED' else 'UNBOUND',json.dumps(q.get('code',{}),sort_keys=True),json.dumps(q.get('variant',{}),sort_keys=True),0])
    print(json.dumps(read(A/'RESULT.json'),indent=2))
if __name__=='__main__':main()
