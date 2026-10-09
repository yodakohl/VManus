"""Independent dynamic parsing and complete result reconstruction."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import gzip,json,hashlib,time
D=Path('experiments/yolo/gdt1237_one_compound_letter_exceptions');A=D/'artifacts'


def parse(w,g,long):
    # Integer path count plus one actual source sequence; no local-condition test.
    ways=[0]*(len(w)+1);ways[0]=1
    route=[None]*(len(w)+1);route[0]=()
    for i in range(len(w)):
        if not ways[i]:continue
        options=[]
        if w[i]!=g:options.append((i+1,w[i]))
        if tuple(w[i:i+2])==long:options.append((i+2,g))
        for j,letter in options:
            ways[j]+=ways[i];route[j]=route[i]+(letter,)
    assert max(ways)<=1,'code unexpectedly ambiguous'
    return route[-1]if ways[-1]else None


def best(rows,N,percentages):
    active=[x for x in rows if x['active_tokens']]
    def minimum(R):
        if not R:return {'status':'NO_CAPACITY','minimum_failed_tokens':None,'model_ids':[]}
        costs=sorted({r['failed_tokens']for r in R});v=costs[0]
        return {'status':'DESCRIPTIVE_MINIMUM','minimum_failed_tokens':v,'model_ids':[r['id']for r in R if r['failed_tokens']==v]}
    thresholds={}
    for p in percentages:
        n=(N*p+99)//100;v=minimum([r for r in active if 100*r['active_tokens']>=N*p]);v['minimum_active_tokens']=n;thresholds[str(p)]=v
    frontier=[]
    bycost=defaultdict(list)
    for r in active:bycost[r['failed_tokens']].append(r)
    largest=-1
    for cost in sorted(bycost):
        local=max(r['active_tokens']for r in bycost[cost])
        if local>largest:frontier.extend(r['id']for r in bycost[cost]if r['active_tokens']==local)
        largest=max(largest,local)
    return {'active_at_least_one':minimum(active),'activity_percentages':thresholds,
            'per_missing_sign':{g:minimum([r for r in active if r['missing_singleton']==g])for g in sorted({r['missing_singleton']for r in rows})},
            'pareto_model_ids':sorted(frontier)}


def main():
    started=time.monotonic();s=json.loads((D/'src/SPEC.json').read_text());lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    groups=json.loads(gzip.decompress(Path(s['source']).read_bytes()))
    result=json.loads((A/'RESULT.json').read_text());models=json.loads((A/'CODEBOOKS.json').read_text())
    expected=[]
    for g in s['signs']:
        for h in s['signs']:
            for side in('after','before'):
                if g==h and side=='before':continue
                expected.append({'id':len(expected),'missing_singleton':g,'companion':h,'side':side,'compound':[g,h]if side=='after'else[h,g]})
    assert models==expected and len(models)==946
    assert len({(x['missing_singleton'],tuple(x['compound']))for x in models})==946
    counts_checked={}
    for reader in s['readers']:
        source=groups[reader];c=Counter(tuple(r['units'])for r in source);ids=defaultdict(list);pages=defaultdict(set)
        for r in source:ids[tuple(r['units'])].append(r['id']);pages[tuple(r['units'])].add(r['page'])
        words=sorted(c,key=lambda w:(len(w),w))
        packet=json.loads(gzip.decompress((A/('ACCOUNT_'+reader+'.json.gz')).read_bytes()))
        expected_words=[{'units':list(w),'count':c[w],'pages':sorted(pages[w]),'source_ids':ids[w]}for w in words]
        assert packet['words']==expected_words
        rows=[]
        for model,row in zip(models,packet['models'],strict=True):
            g=model['missing_singleton'];long=tuple(model['compound']);failed=[];active=[];uses=0
            for i,w in enumerate(words):
                if g not in w:continue
                decoded=parse(w,g,long)
                if decoded is None:failed.append(i)
                else:
                    k=decoded.count(g);assert k>0
                    # The independently reconstructed source writes exactly w.
                    back=tuple(x for ch in decoded for x in(long if ch==g else(ch,)))
                    assert back==w
                    active.append(i);uses+=c[w]*k
            record={**model,'failed_type_indices':failed,'active_type_indices':active,
                    'failed_tokens':sum(c[words[i]]for i in failed),'failed_types':len(failed),
                    'active_tokens':sum(c[words[i]]for i in active),'active_types':len(active),'compound_occurrences':uses,
                    'unchanged_singleton_tokens':sum(c[w]for w in words if g not in w)}
            assert record==row,(reader,model)
            assert record['failed_tokens']+record['active_tokens']+record['unchanged_singleton_tokens']==len(source)
            rows.append(record)
            if time.monotonic()-started>s['runtime_seconds']:raise TimeoutError('validator runtime cap')
        summary=best(rows,len(source),s['activity_percentages'])
        assert summary==result['readers'][reader]['summary']
        assert result['readers'][reader]['tokens']==len(source)and result['readers'][reader]['types']==len(words)
        counts_checked[reader]={'codebooks':len(rows),'whole_types':len(words),'whole_tokens':len(source)}
    out={'status':'PASS','validated_utc':datetime.now(timezone.utc).isoformat(),'checks':counts_checked,'source_hashes':'PASS','actual_source_roundtrips':'PASS','counts_minima_frontiers':'PASS','elapsed_seconds':time.monotonic()-started}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out)

if __name__=='__main__':main()
