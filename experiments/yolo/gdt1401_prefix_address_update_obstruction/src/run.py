"""Source-semantic invariant plus replay of old, already-known word pairs."""
from pathlib import Path
import argparse,hashlib,itertools,json
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
S=json.loads((D/'src/SPEC.json').read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def toggle(frontier,node,b):
    kids={node+(j,) for j in range(b)}
    if node in frontier:return (frontier-{node})|kids
    if kids<=frontier:return (frontier-kids)|{node}
    return None

def frontiers(b,depth):
    result=[frozenset({()})]
    if depth:
        child=frontiers(b,depth-1)
        for product in itertools.product(child,repeat=b):
            result.append(frozenset((i,)+x for i,sub in enumerate(product) for x in sub))
    return result

def controls():
    checked=0;first_legal=0
    for b,depth in [(2,3),(3,2)]:
        ff=frontiers(b,depth)
        assert len(ff)==(26 if b==2 else 9)
        nodes=[x for n in range(depth+1) for x in itertools.product(range(b),repeat=n)]
        for F in ff:
            assert all(not (len(x)<len(y) and y[:len(x)]==x) for x in F for y in F)
            for u in nodes:
                for v in nodes:
                    if len(v)>=len(u)+2 and v[:len(u)]==u:
                        after=toggle(F,u,b)
                        if after is not None:assert toggle(after,v,b) is None;first_legal+=1
                        checked+=1
        F=frozenset({()});after=toggle(F,(),b);child=(0,)
        assert toggle(after,child,b) is not None
        state=F
        for node in [(),child,child,()]:state=toggle(state,node,b);assert state is not None
        assert state==F
    return {'status':'PASS','finite_frontiers':35,'tested_ancestor_descendant_pairs':checked,'legal_first_updates_checked':first_legal,'scope_fixtures':['parent_then_child_allowed','inner_inverse_before_outer_merge_allowed'],'native_payload_read':False}

def parse(raw):
    out=[[] for _ in range(len(raw)+1)];out[0]=[()]
    for i in range(len(raw)):
        for sign in S['signs']:
            if raw.startswith(sign,i):
                j=i+len(sign);out[j]=(out[j]+[w+(sign,) for w in out[i]])[:2]
    assert len(out[-1])==1,(raw,out[-1]);return list(out[-1][0])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');args=ap.parse_args()
    if args.controls:save(A/'PRELOCK_CONTROLS.json',controls());print('source-free controls PASS');return
    assert not (A/'RESULT.json').exists()
    lock=json.loads((D/'LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    prior=json.loads((ROOT/S['pairs']).read_text());cases=[]
    for ed in S['readers']:
        for spec in S['witnesses']:
            matches=[x for x in prior[ed][spec['base']] if x['left']['locus']==spec['locus'] and x['right']['locus']==spec['locus'] and x['left']['ivtff_group_raw']==spec['base'] and x['right']['ivtff_group_raw']==spec['extended']]
            assert len(matches)==1,(ed,spec,len(matches));pair=matches[0];left,right=pair['left'],pair['right']
            assert left['edition']==right['edition']==ed
            assert left['page']==right['page'] and left['kind']==right['kind']=='P'
            assert int(right['source_group_index'])==int(left['source_group_index'])+1
            assert left['right_separator']==right['left_separator']=='DEFINITE_SPACE'
            u,v=parse(spec['base']),parse(spec['extended']);assert v==u+['d','y']
            cases.append({'reader':ed,'locus':spec['locus'],'base':spec['base'],'extended':spec['extended'],'left':left,'right':right,'left_units':u,'right_units':v,'extension_units':['d','y'],'minimum_path_distance':2,'status':'FORBIDDEN_UNDER_DECLARED_ADDRESS_CONTRACT'})
    save(A/'RESULT.json',{'experiment':'GDT1401','status':'PREFIX_FAITHFUL_SINGLE_UPDATE_FAMILY_EXCLUDED','case_count':len(cases),'physical_sites':len(S['witnesses']),'cases':cases,'new_native_census':False,'word_meanings_assigned':0,'selection':'Old1200pairs known before code lock; post-observation logical application, not independent prediction.'})
    print(json.dumps({'status':'PREFIX_FAITHFUL_SINGLE_UPDATE_FAMILY_EXCLUDED','verified_pair_cases':len(cases),'physical_sites':len(S['witnesses'])},sort_keys=True))
if __name__=='__main__':main()
