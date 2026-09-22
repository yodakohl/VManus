#!/usr/bin/env python3
"""Necessary shared-code bound; no semantic fit or target-driven edge choice."""
from pathlib import Path
from collections import Counter, deque
import argparse, hashlib, itertools, json
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
def load(path): return json.loads(path.read_text())
def save(name,obj): (EXP/'artifacts'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def matching_cover(adj):
    matched={}
    def augment(a, seen):
        for b in sorted(adj[a]):
            if b in seen: continue
            seen.add(b)
            if b not in matched or augment(matched[b],seen):
                matched[b]=a
                return True
        return False
    for a in sorted(adj): augment(a,set())
    inverse={a:b for b,a in matched.items()}
    za=set(adj)-set(inverse); zb=set(); queue=deque(sorted(za))
    while queue:
        a=queue.popleft()
        for b in adj[a]:
            if inverse.get(a)==b or b in zb: continue
            zb.add(b)
            if b in matched and matched[b] not in za:
                za.add(matched[b]);queue.append(matched[b])
    ca=sorted(set(adj)-za);cb=sorted(zb)
    assert all(a in ca or b in cb for a in adj for b in adj[a])
    assert len(ca)+len(cb)==len(matched)
    return dict(pairs=sorted([a,b] for b,a in matched.items()),cover_A=ca,cover_B=cb,size=len(matched))
def brute_size(adj):
    aa=list(adj)
    def visit(i,used):
        if i==len(aa):return 0
        return max([visit(i+1,used)]+[1+visit(i+1,used|{b}) for b in adj[aa[i]]-used])
    return visit(0,set())
def capacities(adj,B,pools):
    output=[]
    for pool in pools:
        bn={b for b,row in B.items() if row['entry'] in pool['forms']}
        an={a for a in adj if adj[a]&bn}
        output.append(dict(id=pool['id'],forms=pool['forms'],A_nodes=sorted(an),B_nodes=sorted(bn),A_capacity=len(an),B_capacity=len(bn)))
    return output
def self_test():
    n=0
    for na,nb in [(0,0),(1,2),(2,3),(3,3)]:
        edges=list(itertools.product(range(na),range(nb)))
        for mask in range(1<<len(edges)):
            adj={a:{b for j,(x,b) in enumerate(edges) if x==a and mask>>j&1} for a in range(na)}
            ans=matching_cover(adj)
            assert ans['size']==brute_size(adj);n+=1
    aa=Counter({'x':3,'y':1});bb=Counter({'x':1,'y':4})
    assert sum(min(aa[w],bb[w]) for w in aa|bb)==2
    pp=capacities({'a':{'b1','b2'},'a2':set()},{'b1':{'entry':'v'},'b2':{'entry':'v'}},[{'id':'P','forms':['v']}])
    assert pp[0]['A_capacity']==1 and pp[0]['B_capacity']==2
    assert not any(v['A_capacity']>=2 and v['B_capacity']>=2 for v in pp)
    return dict(status='PASS',all_graphs=n,alias_fixture=True,union_capacity_fixture=True,target_read=False)
def execute(spec):
    packet=load(ROOT/spec['packet']['path']);owned={}
    for p in packet['ZL3b']:
        if p['id'] not in {r['paragraph'] for r in spec['records']}:continue
        assert not p['page'].startswith('f84') and p['page']!='f116v'
        assert p['id'] not in owned;owned[p['id']]=p
    assert len(owned)==4
    atoms=load(EXP/'src/COMPATIBILITY.json')
    allowed={(x['A'],x['B']) for x in atoms['allowed_pairs']}
    A={};B={};scopes=[]
    counts={name:{family:Counter() for family in ['A','B']} for name in ['RAW_EXACT','LITERAL_LINES']}
    for record in spec['records']:
        old=load(ROOT/record['path']);receipt=old[record['receipt']];p=owned[record['paragraph']]
        rows=[]
        for line in p['lines']:
            assert len(line['words'])==len(line['source_ids'])
            for w,source_id in zip(line['words'],line['source_ids']):
                rows.append(dict(word=w,source_id=source_id,locus=line['locus'],anchor_eligible=line.get('anchor_eligible')))
        assert len(rows)==p['groups']==len(receipt)==record['groups']
        assert [r['word'] for r in rows]==[r.get('form',r.get('raw_form')) for r in receipt]
        nodes=A if record['family']=='A' else B
        for i,(target,source) in enumerate(zip(rows,receipt),1):
            assert source['position']==i
            key=source.get('form',source.get('raw_form'))
            assert key in atoms['entries'][record['family']]
            assert source['value']==atoms['entries'][record['family']][key]['value']
            node=f"{record['section']}:{i:03d}"
            nodes[node]=dict(section=record['section'],position=i,entry=key,value=source['value'])
            counts['RAW_EXACT'][record['family']][target['word']]+=1
            if target['anchor_eligible'] is True:counts['LITERAL_LINES'][record['family']][target['word']]+=1
        scopes.append(dict(section=record['section'],family=record['family'],paragraph=p['id'],page=p['page'],leaf=p['leaf'],groups=p['groups'],positions=rows))
    adj={a:{b for b,y in B.items() if (x['entry'],y['entry']) in allowed} for a,x in A.items()}
    cert=matching_cover(adj);tables={};results={};domains={}
    pools=load(EXP/'src/B_POOLS.json')['pools']
    forms=[w for pool in pools for w in pool['forms']]
    assert len(forms)==59 and set(forms)==set(atoms['entries']['B'])
    assert len({pool['id'] for pool in pools})==len(pools)
    pool_caps=capacities(adj,B,pools)
    for panel,cc in counts.items():
        table=[dict(form=w,A=cc['A'][w],B=cc['B'][w],required_pairs=min(cc['A'][w],cc['B'][w])) for w in sorted(cc['A']|cc['B'])]
        demand=sum(x['required_pairs'] for x in table);tables[panel]=table
        dd=[]
        for row in table:
            if not row['required_pairs']:continue
            possible=[v['id'] for v in pool_caps if v['A_capacity']>=row['A'] and v['B_capacity']>=row['B']]
            dd.append(dict(**row,possible_pools=possible,decision='NECESSARY_DOMAIN_NONEMPTY' if possible else 'EMPTY_NECESSARY_DOMAIN'))
        domains[panel]=dd;empty=sum(not row['possible_pools'] for row in dd)
        results[panel]=dict(A_positions=sum(cc['A'].values()),B_positions=sum(cc['B'].values()),shared_types=sum(x['required_pairs']>0 for x in table),required_pairs=demand,source_capacity=cert['size'],deficit=max(0,demand-cert['size']),empty_word_domains=empty,decision='REFUTED_FIXED_SHARED_CODE' if demand>cert['size'] or empty else 'NO_DECISION')
    return scopes,dict(A=A,B=B,adjacency={a:sorted(bs) for a,bs in adj.items()},certificate=cert),tables,dict(experiment='GDT1034',panels=results,source_positions={'A':len(A),'B':len(B)},allowed_entry_pairs=len(allowed),B_pools=len(pools),confirmed_words=0,independent_meaning_capacity=0,significance_claim=False),dict(pool_capacities=pool_caps,panels=domains)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    if args.self_test:print(json.dumps(self_test()));return
    for p,h in load(EXP/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    scope,graph,tables,result,domains=execute(load(EXP/'src/SPEC.json'))
    for name,value in [('SCOPE.json',scope),('CERTIFICATE.json',graph),('ALL_WORD_COUNTS.json',tables),('RESULT.json',result),('WORD_DOMAINS.json',domains)]:save(name,value)
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
