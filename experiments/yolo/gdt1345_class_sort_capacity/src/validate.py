from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
PAT=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def maximum_clique(adj):
    best=set()
    def bron(r,p,x):
        nonlocal best
        if not p and not x:
            if len(r)>len(best):best=r
            return
        pivot=max(p|x,key=lambda u:len(p&adj[u])) if p|x else None
        for v in sorted(p-(adj[pivot] if pivot is not None else set())):
            bron(r|{v},p&adj[v],x&adj[v]);p.remove(v);x.add(v)
    bron(set(),set(adj),set());return len(best)
def main():
    lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    rows=json.loads(gzip.decompress((R/'experiments/yolo/gdt1342_qoky_written_predecessor/artifacts/SOURCE.json.gz').read_bytes()))
    allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
    assert len(rows)==94855 and all(r['page'] in allowed and not r['page'].startswith('f84') and r['page'] not in ['f1r','f116v'] for r in rows)
    classifications={r[0]:r[1] for r in json.loads(gzip.decompress((R/'experiments/yolo/gdt1343_default_vowel_terminal_capacity/artifacts/CLASSIFICATION.json.gz').read_bytes()))}
    strict=[];units={}
    for r in rows:
        ts=PAT.findall(r['raw']);ok=bool(ts) and ''.join(ts)==r['raw'] and all(r[s] in ['DEFINITE_SPACE','LINE_START','LINE_END'] for s in ['left','right'])
        assert ok==(classifications[r['id']]=='STRICT')
        if ok:strict.append(r);units[r['id']]=ts
    results=json.loads((B/'artifacts/RESULT.json').read_text());edge_checks=0;word_checks=0
    for ed in ['ZL3b','IT2a','RF1b']:
        rr=[r for r in strict if r['edition']==ed];leaves=defaultdict(set)
        for r in rr:leaves[r['raw']].add(re.match(r'f[0-9]+',r['page'])[0])
        for name in ['ALL_STRICT','TWO_PHYSICAL_LEAVES']:
            panel=rr if name=='ALL_STRICT' else [r for r in rr if len(leaves[r['raw']])>1]
            d=results[ed+'_'+name];actual={};act=set()
            for r in panel:
                ts=units[r['id']];act.update(ts)
                for u,v in itertools.permutations(sorted(set(ts)),2):
                    if ts.index(u)>=len(ts)-1-ts[::-1].index(v):continue
                    if (u,v) not in actual:actual[u,v]=[]
                    actual[u,v].append(r)
            assert d['groups']==len(panel) and d['types']==len({r['raw'] for r in panel}) and d['active_units']==sorted(act)
            assert d['directed_edges']==len(actual)==len(d['edge_evidence'])
            for e in d['edge_evidence']:
                u,v=e['before'],e['after'];observed=actual[u,v];r=observed[0];ts=units[r['id']]
                i,j=e['witness']['positions'];assert i<j and ts[i]==u and ts[j]==v and e['witness']['source']==r
                assert (e['tokens'],e['types'],e['physical_leaves'])==(len(observed),len({x['raw'] for x in observed}),len({re.match(r'f[0-9]+',x['page'])[0] for x in observed}))
                edge_checks+=1
            adj={u:{v for v in act if (u,v) in actual and (v,u) in actual} for u in act}
            assert d['conflict_edges']==sum(len(a) for a in adj.values())//2
            assert all(v in adj[u] for u,v in itertools.combinations(d['clique'],2))
            assert len(set(d['clique']))==len(d['clique'])==d['class_lower_bound']==maximum_clique(adj)
            flattened=sum(d['orders'],[]);assert sorted(flattened)==sorted(act)
            for r in panel:
                for order in d['orders']:
                    seq=[order.index(s) for s in units[r['id']] if s in order]
                    assert all(a<=b for a,b in zip(seq,seq[1:]))
                word_checks+=1
            assert d['class_upper_bound']==len(d['orders'])>=d['class_lower_bound']
            assert d['exact_minimum']==(d['class_lower_bound'] if d['class_lower_bound']==d['class_upper_bound'] else None)
    # All graphs on4vertices: independent clique algorithm matches brute subsets.
    pairs=list(itertools.combinations(range(4),2))
    for bits in range(64):
        adj={i:set() for i in range(4)}
        for j,(u,v) in enumerate(pairs):
            if bits>>j&1:adj[u].add(v);adj[v].add(u)
        brute=max(len(s) for n in range(5) for s in itertools.combinations(range(4),n) if all(v in adj[u] for u,v in itertools.combinations(s,2)))
        assert brute==maximum_clique(adj)
    # Directed3cycle: pair clique1does not certify single-class feasibility.
    cyc={('a','b'),('b','c'),('c','a')}
    assert not any(all(order.index(a)<order.index(b) for a,b in cyc) for order in itertools.permutations('abc'))
    assert all(not (v,u) in cyc for u,v in cyc)
    out={'status':'PASS','classified_rows':len(rows),'panels':len(results),'directed_certificates':edge_checks,'whole_group_order_checks':word_checks,'small_graph_fixtures':64,'scope':'Independent raw-cache eligibility, edge accounting, maximum clique and constructive upper bounds; no independent palaeography or meanings.'}
    (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
