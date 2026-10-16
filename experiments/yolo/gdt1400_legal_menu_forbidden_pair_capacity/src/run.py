"""Small necessary menu-code adjacency bound; no key/path search."""
from pathlib import Path
from collections import Counter
import argparse,gzip,hashlib,itertools,json,math,random,re
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
S=json.loads((D/'src/SPEC.json').read_text())
def save(p,j):p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')

def step(c,r):
    occupied=[j for j,x in enumerate(c) if x];k=len(occupied)
    if r>=4*k+2:return None
    if r==4*k:return c
    if r==4*k+1:return (c[4],*c[:4])
    donor=occupied[r//4];x=r%4;target=x if x<donor else x+1
    d=list(c);d[donor]-=1;d[target]+=1;return tuple(d)

def cards(signs,E,size=4):
    out=[]
    for B in itertools.combinations(sorted(signs),2):
        Z=sorted(g for g in signs if all((g,b) not in E for b in B))
        ok=set(B)<=set(Z) and len(Z)>=size
        out.append({'B':list(B),'Z':Z,'compatible':ok,'A_extensions':math.comb(len(Z)-2,size-2) if ok else 0})
    return out

def controls():
    states=[c for c in itertools.product(range(6),repeat=5) if sum(c)==5];assert len(states)==126
    cases=0
    for c in states:
        for a in S['rank_A']:
            n=step(c,a)
            if n is not None:
                assert sum(v>0 for v in n)==4
                for b in S['rank_B']:assert step(n,b) is None;cases+=1
    rng=random.Random(1400);tests=0
    for n in [4,5,6]:
        signs=tuple(range(n));pairs=list(itertools.product(signs,repeat=2))
        graphs=[set(),set(pairs),{(0,0)},{(0,1),(1,0)}]
        graphs += [{e for e in pairs if rng.random()<0.2} for _ in range(40)]
        for E in graphs:
            for card in cards(signs,E):
                B=set(card['B']);actual=[t for t in itertools.combinations(signs,4) if B<=set(t) and not any((a,b) in E for a in t for b in B)]
                assert card['compatible']==bool(actual) and card['A_extensions']==len(actual);tests+=1
    return {'status':'PASS','states':126,'forbidden_continuations_checked':cases,'small_graph_B_cases':tests,'native_payload_read':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');args=ap.parse_args()
    if args.controls:save(A/'PRELOCK_CONTROLS.json',controls());print('source-free controls PASS');return
    assert not (A/'RESULT.json').exists()
    lock=json.loads((D/'LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    data=json.loads(gzip.decompress((ROOT/S['source']).read_bytes()));result={'experiment':'GDT1400','cases':{}};evidence={}
    for ed in S['readers']:
        leaves={}
        for row in data[ed]:leaves.setdefault(tuple(row['units']),set()).add(re.match(r'f(\d+)[rv]',row['page']).group(1))
        for panel in S['panels']:
            rows=[r for r in data[ed] if panel=='FULL' or len(leaves[tuple(r['units'])])>=2]
            counts=Counter();witness={}
            for row in rows:
                units=row['units'];assert units and set(units)<=set(S['signs'])
                for pos,pair in enumerate(zip(units,units[1:])):
                    counts[pair]+=1
                    candidate={'id':row['id'],'position':pos,'raw':row['ivtff_group_raw'],'source_group_index':row['source_group_index']}
                    if pair not in witness or (candidate['id'],pos)<(witness[pair]['id'],witness[pair]['position']):witness[pair]=candidate
            cc=cards(S['signs'],set(counts));survive=[c for c in cc if c['compatible']];key=ed+'_'+panel
            evidence[key]={'edges':[{'from':a,'to':b,'count':n,'witness':witness[a,b]} for (a,b),n in sorted(counts.items())],'cards':cc}
            result['cases'][key]={'reader':ed,'panel':panel,'groups':len(rows),'types':len({tuple(r['units']) for r in rows}),'adjacent_slots':sum(counts.values()),'distinct_edges':len(counts),'B_sets_tested':len(cc),'surviving_B_sets':len(survive),'admissible_A_B_patterns':sum(c['A_extensions'] for c in cc),'status':'ALL_KEYS_EXCLUDED_BY_LOCAL_BLOCK' if not survive else 'LOCAL_BLOCK_CAPACITY_NOT_EXCLUDED'}
    result['status']='ALL_FULL_READERS_EXCLUDED' if all(c['status']=='ALL_KEYS_EXCLUDED_BY_LOCAL_BLOCK' for c in result['cases'].values() if c['panel']=='FULL') else 'LOCAL_CAPACITY_REMAINS'
    (A/'EVIDENCE.json.gz').write_bytes(gzip.compress(json.dumps(evidence,sort_keys=True,separators=(',',':')).encode(),mtime=0));save(A/'RESULT.json',result)
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
