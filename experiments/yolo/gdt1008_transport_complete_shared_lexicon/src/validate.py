from common import *
from run import meanings
import collections,concurrent.futures,csv
import independent

def task(row):
    s,g=inputs();panel=read(A/'PANEL.json');ps=[panel[i] for i in row['system']]
    other=independent.check(ps,{},g,timeout=s['independent_milliseconds'],family=row['family'])
    assert not ({row['status'].lower(),other['status']}=={'sat','unsat'})
    for witness in row['witnesses']:
        code=witness['aliases'];assert set(code)==set(w for p in ps for w in p['words']) and len(witness['parses'])==len(ps)
        if row['family']=='BIJECTIVE':assert len({code[w] for w in ps[0]['words']})==len(set(ps[0]['words']))
        for pi,(p,parsed) in enumerate(zip(ps,witness['parses'])):
            cursor=0
            for clause in parsed:
                pattern=g['patterns'][clause['kind']];assert clause['start']==cursor and clause['end']==cursor+len(pattern);cursor=clause['end']
                assert clause['symbols']==[code[w] for w in p['words'][clause['start']:clause['end']]]
                assert all(x in g['types'][t[1:]] if t.startswith('@') else x==t for x,t in zip(clause['symbols'],pattern))
            assert cursor==len(p['words']) and parsed[0]['kind']=='INITIAL' and parsed[-1]['kind']=='CONCLUSION'
            for k in (g['patterns'] if pi==0 else ['INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION']):assert sum(x['kind']==k for x in parsed)==1+int(pi==0 and k=='THEN')
        assert witness['meaning_variants']==meanings(witness,s,g,True)
    return dict(id=row['id'],primary=row['status'],independent=other['status'],witnesses=len(row['witnesses']),variant_checks=len(row['witnesses'])*32)

def main():
    checklock();s,g=inputs();panel=read(A/'PANEL.json');rows=read(A/'ROWS.json');jobs=read(A/'PREDICTIONS.json')
    assert len(rows)==len(jobs)==6 and [x['id'] for x in rows]==[x['id'] for x in jobs]
    old=next(x for x in read(R/s['source_original']) if x['edition']=='ZL3b');assert panel[0]['words']==old['words'] and panel[0]['source_ids']==old['source_ids']
    source=read(R/s['source_contexts']);positive=[r['paragraph'] for r in read(R/s['source_context_results']) if any(q['candidate']!='UNPINNED' and q['status']=='sat' for q in r['rows'])]
    assert [p['id'] for p in panel[1:]]==positive
    for p in panel[1:]:
        q=next(x for x in source if x['id']==p['id'])
        assert all(p[k]==q[k] for k in p) and not p['page'].startswith('f84') and p['page']!='f116v'
    for r,j in zip(rows,jobs):
        for k,v in j.items():assert r[k]==v
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==6
    for t,r in zip(table,rows):assert t['system']==r['id'] and t['family']==r['family'] and t['status']==r['status'] and int(t['sampled_maps'])==len(r['witnesses'])
    with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:checks=list(pool.map(task,rows))
    out=dict(status='PASS',checks=checks,independent_unknowns=sum(c['independent']=='unknown' for c in checks),unverified_negatives=sum(c['primary']=='UNSAT' and c['independent']!='unsat' for c in checks),confirmed_words=0,independent_meaning_capacity=0)
    put('VALIDATION.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
