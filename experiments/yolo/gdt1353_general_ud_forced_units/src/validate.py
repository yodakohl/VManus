from pathlib import Path
from collections import defaultdict,Counter
import csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
PAT=re.compile('ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def independent_close(words):
    known={(),*words}
    while True:
        suffixes=set();prefixes=set()
        for w in known:
            suffixes.update(w[i:] for i in range(1,len(w)) if w[:i] in known)
            prefixes.update(w[:i] for i in range(1,len(w)) if w[i:] in known)
        extra=(suffixes&prefixes)-known
        if not extra:return known
        known|=extra

def unique_parse(w,codes):
    paths={0:(1,())}
    for i in range(len(w)):
        if i not in paths:continue
        count,path=paths[i]
        for c in codes:
            if w[i:i+len(c)]==c:
                j=i+len(c);old=paths.get(j,(0,()))[0];paths[j]=(min(2,old+count),path+(c,))
    assert paths.get(len(w),(0,()))[0]==1
    return paths[len(w)][1]
def ud(codes):
    todo={v[len(u):] for u in codes for v in codes if u!=v and v[:len(u)]==u};seen=set()
    while todo:
        w=todo.pop()
        if not w:return False
        if w in seen:continue
        seen.add(w)
        for c in codes:
            if w[:len(c)]==c:todo.add(w[len(c):])
            if c[:len(w)]==w:todo.add(c[len(w):])
    return True

def main():
    for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};receipts={};proof_checks=parse_checks=0
    for reader,rows in sorted(data.items()):
        original=defaultdict(list)
        for row in rows:
            assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';parsed=PAT.findall(row['ivtff_group_raw']);assert ''.join(parsed)==row['ivtff_group_raw'] and parsed==row['units'];original[tuple(parsed)].append(row)
        alphabet=sorted({u for w in original for u in w});assert len(alphabet)==22
        for panel in ['FULL','GE2']:
            occ={w:rr for w,rr in original.items() if panel=='FULL' or len({re.match(r'f\d+',r['page'])[0] for r in rr})>=2};key=reader+'_'+panel;rr=result['panels'][key];certificate=read(B/f'artifacts/CERTIFICATE_{key}.json.gz');assert certificate['reader']==reader and certificate['panel']==panel;nodes=certificate['nodes'];known={};rootsets={};nodewords=[]
            for i,node in enumerate(nodes):
                w=tuple(node['units']);assert w not in known
                if node['kind']=='EMPTY':assert i==0 and w==() and node['round']==0;roots=set()
                elif node['kind']=='WHOLE':
                    assert w in occ and node['round']==0;src=node['source'];assert src['first_row']==occ[w][0] and src['count']==len(occ[w]);assert src['physical_leaves']==sorted({int(re.match(r'f(\d+)',r['page'])[1]) for r in occ[w]});roots={w}
                else:
                    assert node['kind']=='QUOTIENT';a,b,c,d=node['parents'];assert all(0<=j<i and nodes[j]['round']<node['round'] for j in [a,b,c,d]);x,xy,yz,z=(nodewords[j] for j in [a,b,c,d]);assert w and x+w==xy and w+z==yz;roots=set().union(*(rootsets[j] for j in [a,b,c,d]));proof_checks+=1
                rootsets[i]=roots;known[w]=i;nodewords.append(w)
            assert {w for w,i in known.items() if nodes[i]['kind']=='WHOLE'}==set(occ)
            if rr['closure_complete']:assert set(known)==independent_close(set(occ))
            assert rr['closure_nodes']==len(nodes) and rr['closure_rounds']==max(n['round'] for n in nodes)
            forced=sorted(w[0] for w in known if len(w)==1);assert forced==rr['forced_singletons'];assert rr['groups']==sum(map(len,occ.values())) and rr['types']==len(occ);assert rr['active_units']==sorted({u for w in occ for u in w})
            fixed={w for w in occ if all(u in forced for u in w)};assert rr['fully_forced_types']==len(fixed) and rr['fully_forced_groups']==sum(len(occ[w]) for w in fixed)
            for u in forced:
                support={tuple(x['units']):x for x in rr['proof_support'][u]};assert set(support)==rootsets[known[(u,)]]
                for w,s in support.items():assert s=={'units':list(w),'count':len(occ[w]),'physical_leaves':sorted({int(re.match(r'f(\d+)',r['page'])[1]) for r in occ[w]}),'first_id':occ[w][0]['id']}
            counter=certificate['countercodes'];assert sorted(counter)==rr['certified_not_forced'];expected_counter=[];unresolved=[]
            for h in alphabet:
                if h in forced:continue
                noend=all(w[-1]!=h for w in occ);nostart=all(w[0]!=h for w in occ)
                if noend or nostart:expected_counter.append(h)
                else:unresolved.append(h);continue
                entry=counter[h];direction='PREFIX' if noend else 'SUFFIX';assert entry['direction']==direction and entry['omits_singleton']==h
                codes=[tuple(c['units']) for c in entry['used_codes']];assert codes==sorted(set(codes)) and all(c for c in codes) and (h,) not in codes and all((u,) in codes for u in forced)
                comparison=codes if direction=='PREFIX' else [c[::-1] for c in codes]
                assert all(v[:len(u)]!=u for u in comparison for v in comparison if u!=v)
                assert ud(codes)
                # Check the frozen maximal-run construction independently through shape.
                assert all(c[-1]!=h and all(x==h for x in c[:-1]) for c in comparison)
                uses=Counter();active=0
                for w,rows_w in occ.items():
                    parts=unique_parse(w,codes);assert sum(parts,())==w;parse_checks+=1;active+=len(rows_w)*any(len(c)>1 for c in parts)
                    for c in parts:uses[c]+=len(rows_w)
                assert len(codes)==entry['entry_count'] and active==entry['compound_active_groups'];assert uses==Counter({tuple(c['units']):c['uses'] for c in entry['used_codes']});assert rr['countercode_summary'][h]=={k:v for k,v in entry.items() if k!='used_codes'}
            assert expected_counter==rr['certified_not_forced'] and unresolved==rr['unresolved'];assert rr['status']==('EXACT_SINGLETON_INTERSECTION' if rr['closure_complete'] and not unresolved else 'PARTIAL_SINGLETON_CLASSIFICATION');receipts[key]={'forced':len(forced),'countercodes':len(counter),'unresolved':unresolved,'status':rr['status']}
    # Small unrelated controls for the logical rule and countercode construction.
    assert ('b',) not in independent_close({tuple('a'),tuple('ab')})
    bad={tuple(w) for w in ['a','ab','bc','c']};assert not ud(bad) and ('b',) in independent_close(bad)
    good={tuple(w) for w in ['a','ab','bba']};assert ud(good);closed=independent_close(good|{a+b for a in good for b in good});assert all(unique_parse(w,good) is not None for w in closed if w)
    pair={tuple('ab'),tuple('ba')};assert ud(pair) and independent_close(pair)=={(),*pair}
    fixture_words=0
    for side in ['PREFIX','SUFFIX']:
        words=[tuple(w) for n in range(1,7) for w in itertools.product('ab',repeat=n) if (w[-1] if side=='PREFIX' else w[0])!='a'];codes={('a',)*k+('b',) for k in range(6)};codes=codes if side=='PREFIX' else {c[::-1] for c in codes};assert ud(codes)
        for w in words:assert sum(unique_parse(w,codes),())==w;fixture_words+=1
    out={'status':'PASS','proof_nodes_replayed':proof_checks,'unique_whole_type_parses':parse_checks,'source_free_named_fixtures':4,'source_free_omission_words':fixture_words,'panels':receipts,'scope':'Conditional freeUD obligations and per-sign countermodels only; no historical alphabet, sound assignments or joint omission/minimum-code claim.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
