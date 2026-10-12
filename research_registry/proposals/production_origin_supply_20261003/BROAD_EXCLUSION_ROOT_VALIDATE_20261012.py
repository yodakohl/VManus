"""Recheck old certificates and new logical corollary arithmetic, no new census."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re,subprocess,sys
P=Path('research_registry/proposals/production_origin_supply_20261003')

def main():
    receipts={}
    for name in ['BROAD_STATE_PROOF_VALIDATE_20261012.py','BROAD_REPETITION_VALIDATE_20261012.py']:
        receipts[name]=json.loads(subprocess.check_output([sys.executable,str(P/name)],text=True))
    p=Path('experiments/yolo/gdt1319_cross_word_endpoint_state/artifacts/EDGES.json')
    edges=json.loads(p.read_text());boundary={}
    for reader,ee in edges.items():
        adj=defaultdict(set)
        for e in ee:
            a,b=e['edge'];assert a.startswith('O:') and b.startswith('I:')
            adj[a].add(b);adj[b].add(a)
        seen=set();todo=[next(iter(adj))]
        while todo:
            node=todo.pop()
            if node in seen:continue
            seen.add(node);todo.extend(adj[node]-seen)
        assert seen==set(adj)
        entries=[v for v in seen if v.startswith('I:')];exits=[v for v in seen if v.startswith('O:')]
        # Sharp constant-reset countermodel: distinct exits, identical entries.
        exit_values={v:i+1 for i,v in enumerate(sorted(exits))}
        assert len(set(exit_values.values()))==len(exits)>1
        reset=lambda state:0
        assert all(reset(exit_values[e['edge'][0]])==0 for e in ee)
        boundary[reader]={'edge_count':len(ee),'active_entries':len(entries),'active_exits':len(exits),'components':1,'distinct_exit_constant_reset_countermodel':True}
    review=json.loads((P/'BROAD_REPETITION_REVIEW_20261012.json').read_text())
    raw=review['block_order'];pattern=re.compile(r'ch|sh|[a-z]')
    counts=[Counter(pattern.findall(w)) for w in raw]
    assert all(''.join(pattern.findall(w))==w for w in raw)
    signs=set().union(*(set(c) for c in counts));sig=defaultdict(list)
    for s in sorted(signs):sig[tuple(c[s] for c in counts)].append(s)
    assert sorted(sig.values())==sorted(c['members'] for c in review['signature_classes'])
    assert len(sig)==11 and sum(len(x)==1 for x in sig.values())==9
    proof_path=Path('experiments/yolo/gdt1287_whole_word_reversible_closure/artifacts/PROOFS.json')
    proofs=json.loads(proof_path.read_text());injective={}
    for reader,proof in proofs.items():
        assert proof['square']['ol'] and proof['square']['olol']
        assert all(r['units']==['o','l'] for r in proof['square']['ol'])
        assert all(r['units']==['o','l','o','l'] for r in proof['square']['olol'])
        tables={};derived=0;nodes=0
        for side,chain in proof['chains'].items():
            known={}
            for node in chain:
                parents=node['parents'];word=node['word']
                if parents:
                    a,b=(known[j] for j in parents)
                    assert b==(a+word if side=='LEFT' else word+a)
                    derived+=1
                else:assert node['source_ids']
                assert node['old_id'] not in known
                known[node['old_id']]=word;nodes+=1
            tables[side]=known
        assert len(proof['targets'])==22
        for sign,(side,index) in proof['targets'].items():assert tables[side][index]==[sign]
        injective[reader]={'positive_nodes':nodes,'derived_concatenations':derived,'targets':22}
    paths=[p,P/'BROAD_BOUNDARY_REVIEW_20261012.json',P/'BROAD_REPETITION_REVIEW_20261012.json',P/'BROAD_STATE_PROOF_REVIEW_20261012.json',P/'BROAD_STATE_PROOF_VALIDATE_20261012.py',P/'BROAD_REPETITION_VALIDATE_20261012.py']
    paths.extend([proof_path,P/'BROAD_INJECTIVE_WORD_REVIEW_20261012.json'])
    result={'status':'PASS_OLD_CERTIFICATES_AND_COROLLARY_ARITHMETIC','receipts':receipts,'reset_graphs':boundary,'injective_positive_chains':injective,'independent_regex_signature_classes':sorted(sig.values()),'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'limit':'General theorem steps reviewed in prose. No native units/boundaries or mechanism confirmed; no new native census or word meanings.'}
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
