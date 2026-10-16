"""Bounded structural menu-code capacity; no lexical assignments."""
import argparse, concurrent.futures, hashlib, itertools, json, random, time
from pathlib import Path
import z3
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
S=json.loads((D/'src/SPEC.json').read_text())

def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')

def menu_step(c,r):
    k=sum(v>0 for v in c)
    if not 0<=r<4*k+2:return None
    if r==4*k:return tuple(c)
    if r==4*k+1:return (c[4],*c[:4])
    donor=[j for j,v in enumerate(c) if v>0][r//4]
    rem=r%4;target=rem if rem<donor else rem+1
    out=list(c);out[donor]-=1;out[target]+=1
    return tuple(out)

def symbolic_next(c,r):
    occupied=[z3.If(v>0,1,0) for v in c];k=z3.Sum(occupied)
    donor=z3.Sum([z3.If(z3.And(c[j]>0,r/4==z3.Sum(occupied[:j]) if j else r/4==0),j,0) for j in range(5)])
    target=z3.If(r%4<donor,r%4,r%4+1)
    return r<4*k+2,[z3.If(r==4*k+1,c[(j-1)%5],c[j]-z3.If(z3.And(r<4*k,donor==j),1,0)+z3.If(z3.And(r<4*k,target==j),1,0)) for j in range(5)]

def fit(units,timeout_ms,fixed=None):
    solver=z3.Solver();solver.set(timeout=timeout_ms,random_seed=S['random_seed'],threads=1)
    key=[z3.Int('K_'+str(i)) for i in range(22)]
    solver.add(*[z3.And(v>=0,v<22) for v in key],z3.Distinct(key))
    used=set(units);unused=[i for i,g in enumerate(S['signs']) if g not in used]
    solver.add(*[key[a]<key[b] for a,b in zip(unused,unused[1:])])
    if fixed is not None:solver.add(*[key[i]==v for i,v in enumerate(fixed)])
    states=[[z3.Int('C_'+str(i)+'_'+str(j)) for j in range(5)] for i in range(len(units)+1)]
    solver.add(*[states[0][j]==1 for j in range(5)])
    for c in states:solver.add(z3.Sum(c)==5,*[z3.And(v>=0,v<=5) for v in c])
    indices={g:i for i,g in enumerate(S['signs'])}
    for i,g in enumerate(units):
        r=key[indices[g]];legal,nxt=symbolic_next(states[i],r)
        solver.add(legal,*[states[i+1][j]==nxt[j] for j in range(5)])
    answer=solver.check();result={'status':str(answer).upper()}
    if answer==z3.sat:
        m=solver.model();result['key']={g:m.eval(key[i]).as_long() for i,g in enumerate(S['signs'])}
        result['states']=[[m.eval(v).as_long() for v in c] for c in states]
    elif answer==z3.unknown:result['reason']=solver.reason_unknown()
    return result

def parse(raw):
    ways=[[] for _ in range(len(raw)+1)];ways[0]=[()]
    for i in range(len(raw)):
        for g in S['signs']:
            if raw.startswith(g,i):
                end=i+len(g);ways[end]=(ways[end]+[p+(g,) for p in ways[i]])[:2]
    assert len(ways[-1])==1,(raw,ways[-1]);return ways[-1][0]

def source_cases():
    w=json.loads((ROOT/S['worksheet']).read_text());u=next(x for x in w['units'] if x['unit_id']==S['unit_id'])
    assert u['lines'][0]['metadata']['paragraph_start']=='1' and u['lines'][-1]['metadata']['paragraph_end']=='1'
    groups=[]
    for line in u['lines']:
        assert line['metadata']['edition']=='IT2a' and line['metadata']['page']=='f75v'
        assert len(line['original_groups'])==int(line['metadata']['source_group_count'])
        for row in line['original_groups']:
            groups.append({'id':row[0],'source_group_index':row[1],'raw':row[2],'units':list(parse(row[2]))})
    assert len(groups)==77
    cases=[]
    for setting in S['cases']:
        order=list(range(len(groups)))
        if setting['shuffle_seed'] is not None:random.Random(setting['shuffle_seed']).shuffle(order)
        chosen=[groups[i] for i in order]
        cases.append({'id':setting['id'],'shuffle_seed':setting['shuffle_seed'],'group_order':order,'groups':chosen,'units':[g for row in chosen for g in row['units']]})
    return cases

def controls():
    count=0
    for c in itertools.product(range(6),repeat=5):
        if sum(c)!=5:continue
        for r in range(22):
            legal,out=symbolic_next([z3.IntVal(x) for x in c],z3.IntVal(r));ok=z3.is_true(z3.simplify(legal));exact=menu_step(c,r)
            assert ok==(exact is not None),(c,r)
            if ok:assert tuple(z3.simplify(v).as_long() for v in out)==exact,(c,r)
            count+=1
    assert menu_step(menu_step((1,1,1,1,1),16),16)==(2,1,1,1,0)
    assert menu_step(menu_step((1,1,1,1,1),16),18) is None
    # A complete synthetic program restores stock after each taught move.
    ranks=[]
    for r in range(20):
        c=menu_step((1,1,1,1,1),r);back=next(q for q in range(22) if menu_step(c,q)==(1,1,1,1,1));ranks += [r,back]
    ranks += [20,21];units=[S['signs'][r] for r in ranks]
    benchmark=fit(units,10000)
    assert benchmark['status']=='SAT',benchmark
    fixed_invalid=fit([S['signs'][16],S['signs'][18]],10000,list(range(22)))
    assert fixed_invalid['status']=='UNSAT',fixed_invalid
    return {'status':'PASS','finite_transitions_checked':count,'unknown_key_fullalphabet_fixture':'SAT','fixed_key_illegal_fixture':'UNSAT','native_payload_read':False}

def one_case(case):
    result=fit(case['units'],S['timeout_ms']);result.update({k:case[k] for k in ['id','shuffle_seed','group_order','groups','units']});return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args()
    if a.controls:save(A/'PRELOCK_CONTROLS.json',controls());print('source-free controls PASS');return
    assert not (A/'RESULT.json').exists()
    lock=json.loads((D/'LOCK.json').read_text())
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert z3.get_version_string()==S['z3_version']
    cases=source_cases()
    with concurrent.futures.ProcessPoolExecutor(max_workers=S['workers']) as pool:results=list(pool.map(one_case,cases))
    out={'experiment':'GDT1399','z3_version':z3.get_version_string(),'cases':{r['id']:r for r in results},'status':'RAW_BOUNDED_SEARCH_REQUIRES_INDEPENDENT_VALIDATION'}
    save(A/'RESULT.json',out);print(json.dumps({k:v['status'] for k,v in out['cases'].items()},sort_keys=True))
if __name__=='__main__':main()
