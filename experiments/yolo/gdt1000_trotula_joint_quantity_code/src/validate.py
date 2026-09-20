#!/usr/bin/env python3
"""Independent quantity enumeration, full pair census, ground readings, Z3 replay."""
import argparse,collections,concurrent.futures,csv,gzip,hashlib,itertools,json,re,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
Q={'QD1','QD2','QS1'}

def frames(d1,d2,s1=None):
    out=[]
    for left_size in range(len(d1)+1):
        for right_start in range(left_size+1,len(d1)+1):
            left,i,right=d1[:left_size],d1[left_size:right_start],d1[right_start:]
            if not left+right or d2!=left+i+i+right:continue
            f=dict(I=i,L_D=left,R_D=right)
            if s1 is None:out.append(f);continue
            for sl in range(len(s1)+1):
                sr=sl+len(i)
                if s1[sl:sr]==i and sr<=len(s1) and s1[:sl]+s1[sr:] and (s1[:sl],s1[sr:])!=(left,right):out.append(dict(f,L_S=s1[:sl],R_S=s1[sr:]))
    return out

def enumeration(recipe,stream,words):
    if len(words)>len(stream):return 'CONTRADICTED_WORD_CAPACITY',[]
    if sum(map(len,words))<len(stream):return 'CONTRADICTED_NONEMPTY_LENGTH',[]
    qi=[i for i,a in enumerate(stream) if a in Q];out=[]
    for i,j in itertools.combinations(range(len(words)),2):
        source_sizes=(qi[0],qi[1]-qi[0]-1,len(stream)-qi[1]-1)
        chunks=(words[:i],words[i+1:j],words[j+1:])
        valid=True
        for n,ws in zip(source_sizes,chunks):
            if n==0:valid=valid and not ws
            else:valid=valid and 1<=len(ws)<=n<=sum(len(w) for w in ws)
        if not valid:continue
        vals={stream[qi[0]]:words[i],stream[qi[1]]:words[j]}
        if recipe=='IV15':
            f=frames(vals['QD1'],vals['QD2'])
            if f:out.append(dict(values=vals,indices=[i,j],frames=f))
        else:
            x,y=vals['QD1'],vals['QS1'];common=set()
            if x!=y:
                for lo in range(len(x)):
                    for hi in range(lo+1,len(x)+1):
                        z=x[lo:hi]
                        if len(z)<len(x) and len(z)<len(y) and z in y:common.add(z)
            if common:out.append(dict(values=vals,indices=[i,j],possible_I=sorted(common)))
    return ('NECESSARY_QUANTITY_COMPATIBLE' if out else 'CONTRADICTED_QUANTITY_PLACEMENT'),out

def independent_joint(a,b):
    ds={(x['values']['QD1'],x['values']['QD2']) for x in a};ss={(x['values']['QD1'],x['values']['QS1']) for x in b};out=[]
    for one,two in sorted(ds):
        for d,s in sorted(ss):
            if d!=one or len({one,two,s})!=3:continue
            f=frames(one,two,s)
            if f:out.append(dict(values=dict(QD1=one,QD2=two,QS1=s),frames=f))
    return out

def normalized(xs):return sorted(json.dumps(x,sort_keys=True) for x in xs)

def ground(st,words,code,numeric):
    assert set(code)==set().union(*map(set,st));assert all(isinstance(x,str) and x for x in code.values())
    ordinary=[v for a,v in code.items() if a not in Q]
    assert all(not x.startswith(y) and not y.startswith(x) for x,y in itertools.combinations(ordinary,2))
    vals={a:code[a] for a in Q};assert any(x['values']==vals for x in numeric)
    for atoms,ws in zip(st,words):
        # Decode every whole group by consuming entire atom values; quantity is a single whole group.
        index=0
        for word in ws:
            if index<len(atoms) and atoms[index] in Q:
                assert word==code[atoms[index]];index+=1;continue
            assert word not in vals.values();remaining=word
            while remaining:
                assert index<len(atoms) and atoms[index] not in Q
                value=code[atoms[index]];assert remaining.startswith(value)
                remaining=remaining[len(value):];index+=1
        assert index==len(atoms)

def z3replay(job):
    import z3
    s=z3.Solver();s.set(timeout=1000)
    streams=job['streams'];words=job['words'];atoms=sorted(set().union(*map(set,streams)));v={a:z3.String(a) for a in atoms}
    maxlen=max(map(len,itertools.chain.from_iterable(words)))
    for a in atoms:s.add(z3.Length(v[a])>=1,z3.Length(v[a])<=maxlen)
    ordinary=[a for a in atoms if a not in Q]
    for a,b in itertools.combinations(ordinary,2):s.add(z3.Not(z3.PrefixOf(v[a],v[b])),z3.Not(z3.PrefixOf(v[b],v[a])))
    s.add(z3.Or(*[z3.And(*[v[a]==value for a,value in x['values'].items()]) for x in job['numeric']]))
    for stream,ws in zip(streams,words):
        s.add(z3.Concat(*[v[a] for a in stream])==''.join(ws));p=[z3.IntVal(0)]
        for a in stream:p.append(p[-1]+z3.Length(v[a]))
        ends=list(itertools.accumulate(map(len,ws)));starts=[0]+ends[:-1]
        for end in ends:s.add(z3.Or(*[end==b for b in p[1:]]))
        for i,a in enumerate(stream):
            if a in Q:s.add(z3.Or(*[z3.And(p[i]==lo,p[i+1]==hi) for lo,hi in zip(starts,ends)]))
        for lo,hi,w in zip(starts,ends,ws):
            occupied=z3.Or(*[z3.And(p[i]==lo,p[i+1]==hi) for i,a in enumerate(stream) if a in Q])
            s.add(z3.Implies(z3.Or(*[v[a]==w for a in Q]),occupied))
    r=s.check();return dict(status=str(r),solver='z3',version=z3.get_version_string())

def isolate(job):
    try:
        p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--z3-json'],input=json.dumps(job),text=True,capture_output=True,timeout=8)
        return json.loads(p.stdout) if p.returncode==0 else dict(status='error',exit_code=p.returncode)
    except subprocess.TimeoutExpired:return dict(status='unknown_wall')

def selftest():
    # Exhaust all short binary d1/d2 strings by a different source enumeration.
    from model import unit_frames,other_unit,joint_numeric,prelim
    strings=[''.join(t) for n in range(1,5) for t in itertools.product('ab',repeat=n)];n=0
    for one in strings:
        for two in strings:
            assert normalized(frames(one,two))==normalized(unit_frames(one,two));n+=1
    source=read(E/'src/SOURCE.json')
    for name,obj in source['recipes'].items():assert obj['atoms']==[a for p in obj['ownership'] for a in p['atoms']]
    # Small generic streams include both source directions and absent/overlong segments.
    cases=0
    for name,st in [('IV15',['X','QD1','Y','QD2']),('V19',['X','QD1','Y','QS1','Z'])]:
        for stream in (st,list(reversed(st))):
            for ws in itertools.product(['x','ab','aab','bb'],repeat=4):
                a=prelim(name,stream,list(ws));b,opts=enumeration(name,stream,list(ws));assert a['status']==b and normalized(a['options'])==normalized(opts);cases+=1
    out=dict(status='PASS',numeric_string_pairs=n,placement_cases=cases,scope='Independent finite enumeration and source inventory checks only')
    put('VALIDATOR_PREFLIGHT.json',out);print(json.dumps(out,indent=2))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--selftest',action='store_true');ap.add_argument('--z3-json',action='store_true');a=ap.parse_args()
    if a.z3_json:print(json.dumps(z3replay(json.load(sys.stdin))));return
    if a.selftest:selftest();return
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    spec=read(E/'src/SPEC.json');src=read(E/'src/SOURCE.json');target=read(R/spec['input']);rows=read(A/'PARAGRAPH_CASES.json');details=read(A/'JOINT_CASES.json');result=read(A/'RESULT.json')
    expected=[];streams={}
    for writer in spec['writers']:
        streams[writer]={k:v['atoms'] if writer=='FORWARD' else v['atoms'][::-1] for k,v in src['recipes'].items()}
        for ed,ps in target.items():
            for recipe in spec['source_ids']:
                for p in ps:expected.append((writer,ed,recipe,p))
    assert len(rows)==len(expected)==result['paragraph_cases']
    for i,(r,(writer,ed,recipe,p)) in enumerate(zip(rows,expected)):
        assert r['index']==i and r['writer']==writer and r['edition']==ed and r['recipe']==recipe and r['paragraph']==p['id'] and r['leaf']==p['leaf'] and r['page']==p['page']
        assert not r['page'].startswith('f84') and r['page']!='f116v'
        ws=[w for l in p['lines'] for w in l['words']];assert r['words']==ws
        literal=all(l['anchor_eligible'] for l in p['lines']) and all(re.fullmatch('[a-z]+',w) for w in ws)
        status,opts=enumeration(recipe,streams[writer][recipe],ws) if literal else ('UNKNOWN_SOURCE',[])
        assert r['status']==status and normalized(r['options'])==normalized(opts)
    dm={(d['iv15_index'],d['v19_index']):d for d in details};seen=set();counts=collections.Counter();jobs=[];witnesses=0;expected_pairs=0;same_leaf=0;eligible=[]
    panels=collections.defaultdict(lambda:collections.defaultdict(list))
    for r in rows:panels[(r['writer'],r['edition'])][r['recipe']].append(r)
    with gzip.open(A/'PAIR_DECISIONS.tsv.gz','rt') as f:
        table=csv.DictReader(f,delimiter='\t')
        for (writer,ed),panel in panels.items():
            for a in panel['IV15']:
                for b in panel['V19']:
                    if a['leaf']==b['leaf']:same_leaf+=1;continue
                    expected_pairs+=1;r=next(table);assert int(r['iv15_index'])==a['index'] and int(r['v19_index'])==b['index']
                    if a['status'].startswith('CONTRADICTED'):status='CONTRADICTED_IV15'
                    elif b['status'].startswith('CONTRADICTED'):status='CONTRADICTED_V19'
                    elif a['status']=='UNKNOWN_SOURCE' or b['status']=='UNKNOWN_SOURCE':status='UNKNOWN_SOURCE'
                    else:
                        numeric=independent_joint(a['options'],b['options']);key=(a['index'],b['index'])
                        if not numeric:status='CONTRADICTED_SHARED_QUANTITY';assert key not in dm
                        else:
                            assert key in dm;d=dm[key];seen.add(key);assert normalized(d['numeric_options'])==normalized(numeric);status=d['status']
                            order=hashlib.sha256(f"{ed}|{a['paragraph']}|{b['paragraph']}|{writer}".encode()).hexdigest();eligible.append((order,*key))
                            job=dict(streams=[streams[writer]['IV15'],streams[writer]['V19']],words=[a['words'],b['words']],numeric=numeric)
                            if status=='SAT':
                                ground(job['streams'],job['words'],d['code'],numeric);witnesses+=1
                                if d.get('alternative_status')=='SAT':ground(job['streams'],job['words'],d['alternative_code'],numeric);assert d['code']!=d['alternative_code']
                            elif status=='UNSAT_SOLVER':jobs.append((key,job))
                    assert status==r['status'];counts[status]+=1
        assert next(table,None) is None
    assert seen==set(dm);eligible.sort();selected={(a,b) for _,a,b in eligible[:spec['max_joint_jobs']]}
    for key,d in dm.items():assert (d['status']=='UNKNOWN_JOB_CAP')==(key not in selected)
    assert expected_pairs==result['candidate_pairs'] and same_leaf==result['same_leaf_pairs_excluded'] and dict(counts)==result['pair_status_counts']
    assert len(eligible)==result['compatible_numeric_pairs'] and len(selected)==result['solver_jobs'] and witnesses==result['full_joint_witnesses']
    replays=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:
        fs={pool.submit(isolate,job):key for key,job in jobs}
        for f in concurrent.futures.as_completed(fs):
            v=f.result();assert v['status']!='sat','Independent solver contradicts registered UNSAT';replays.append(dict(indices=fs[f],**v))
    replays.sort(key=lambda x:x['indices']);put('INDEPENDENT_SOLVER_REPLAY.json',replays)
    out=dict(status='PASS',paragraph_cases_checked=len(rows),pair_decisions_checked=expected_pairs,numeric_joint_cases_checked=len(dm),complete_witnesses_ground_checked=witnesses,independent_solver_replay_counts=dict(collections.Counter(x['status'] for x in replays)),scope='Independent quantity/census construction and literal whole-code checking; negative SMT results corroborated only where independent replay is unsat.',confirmed_words=0,independent_meaning_capacity=0)
    put('VALIDATION.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
