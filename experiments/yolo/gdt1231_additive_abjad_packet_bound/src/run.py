#!/usr/bin/env python3
"""Find arithmetic witnesses and finite-domain contradiction certificates."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
from functools import lru_cache
import hashlib,json,re,time
import z3
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def save(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def parse(w,inventory):
    if not re.fullmatch('[a-z]+',w):return []
    dp=[[] for _ in range(len(w)+1)];dp[0]=[[]]
    for pos in range(len(w)):
        for g in inventory:
            if w.startswith(g,pos):dp[pos+len(g)].extend(x+[g] for x in dp[pos])
    return dp[-1]
def extract(packet,spec):
    selected=defaultdict(lambda:defaultdict(list));excluded=defaultdict(Counter)
    for line in packet['lines']:
        assert line['page'] not in ('f84','f84r','f116v')
        for row in line['groups']:
            ed=row['edition'];raw=row['ivtff_group_raw'];pp=parse(raw,spec['inventory'])
            reason=('NON_PROSE' if row['kind']!='P' else 'NOT_STRICT_INTERIOR' if row['left_separator']!='DEFINITE_SPACE' or row['right_separator']!='DEFINITE_SPACE' else 'NONLITERAL_OR_NONUNIQUE_PARSE' if len(pp)!=1 else None)
            if reason:excluded[ed][reason]+=1
            else:selected[ed][raw].append(dict(row,units=pp[0]))
    return {ed:{'forms':[{'form':w,'counts':dict(sorted(Counter(rows[0]['units']).items())),'occurrences':rows} for w,rows in sorted(selected[ed].items())],'excluded':dict(excluded[ed])} for ed in spec['readers']}

def csp(constraints,values,seconds,targets=None):
    targets=values if targets is None else targets;cap=max(targets);target_bits=sum(1<<t for t in targets);mask=(1<<(cap+1))-1;deadline=time.monotonic()+seconds
    names=sorted({v for c in constraints for v in c});initial={v:tuple(values) for v in names};nodes=0
    def check():
        if time.monotonic()>deadline:raise TimeoutError
    @lru_cache(maxsize=100000)
    def reachable(parts):
        bits=1
        for coefficient,domain in parts:
            out=0
            for value in domain:out|=bits<<(coefficient*value)
            bits=out&mask
            if not bits:break
        return bits
    def supported(c,var,domains):
        parts=tuple((coef,domains[v]) for v,coef in sorted(c.items()) if v!=var)
        rest=reachable(parts);co=c[var]
        return tuple(x for x in domains[var] if ((rest<<(co*x))&target_bits))
    def visit(parent):
        nonlocal nodes
        nodes+=1;check();ds=dict(parent);reductions=[]
        while True:
            changed=False
            for i,c in enumerate(constraints):
                check()
                for v in sorted(c):
                    keep=supported(c,v,ds)
                    if keep!=ds[v]:
                        reductions.append({'constraint':i,'variable':v,'keep':list(keep)});ds[v]=keep;changed=True
                        if not keep:return {'reductions':reductions,'empty_variable':v},None
            if not changed:break
        if all(len(v)==1 for v in ds.values()):
            witness={v:d[0] for v,d in ds.items()}
            assert all(sum(witness[v]*co for v,co in c.items()) in targets for c in constraints)
            return None,witness
        v=min((v for v in names if len(ds[v])>1),key=lambda v:(len(ds[v]),-sum(v in c for c in constraints),v));children=[]
        for x in ds[v]:
            branch=dict(ds);branch[v]=(x,);child,witness=visit(branch)
            if witness is not None:return None,witness
            children.append({'value':x,'node':child})
        return {'reductions':reductions,'branch_variable':v,'children':children},None
    started=time.monotonic()
    try:
        certificate,witness=visit(initial);return {'status':'SAT' if witness is not None else 'UNSAT','certificate':certificate,'witness':witness,'nodes':nodes,'elapsed_seconds':time.monotonic()-started}
    except TimeoutError:return {'status':'UNKNOWN_TIMEOUT','nodes':nodes,'elapsed_seconds':time.monotonic()-started}

def solver(forms,values,seconds,reduce_seconds):
    names=sorted({v for row in forms for v in row['counts']});variables={v:z3.Int('w_'+v) for v in names};s=z3.Solver();s.set(timeout=int(seconds*1000))
    for v in variables.values():s.add(z3.Or([v==x for x in values]))
    for i,row in enumerate(forms):
        total=z3.Sum([co*variables[v] for v,co in row['counts'].items()]);s.assert_and_track(z3.Or([total==x for x in values]),f'word_{i}')
    started=time.monotonic();r=s.check();elapsed=time.monotonic()-started
    if r==z3.sat:return {'status':'SAT','witness':{v:s.model()[x].as_long() for v,x in variables.items()},'elapsed_seconds':elapsed}
    if r!=z3.unsat:return {'status':'UNKNOWN','reason':s.reason_unknown(),'elapsed_seconds':elapsed}
    core=sorted(int(str(x).split('_')[1]) for x in s.unsat_core());end=time.monotonic()+reduce_seconds
    for old in core[:]:
        left=end-time.monotonic()
        if left<=0:break
        trial=[i for i in core if i!=old];q=z3.Solver();q.set(timeout=max(1,int(min(left,5)*1000)))
        for v in variables.values():q.add(z3.Or([v==x for x in values]))
        for i in trial:
            total=z3.Sum([co*variables[v] for v,co in forms[i]['counts'].items()]);q.add(z3.Or([total==x for x in values]))
        if q.check()==z3.unsat:core=trial
    return {'status':'UNSAT','core_indices':core,'core_forms':[forms[i]['form'] for i in core],'elapsed_seconds':elapsed,'reduction_finished_utc':datetime.now(timezone.utc).isoformat()}

def fixtures():
    cases=[('positive',[{'a':1,'b':1}],[1,2,3],[1,2,3]),('empty_support',[{'a':2}],[1,3],[1,3]),('branch_triangle',[{'a':1,'b':1},{'b':1,'c':1},{'a':1,'c':1}],[1,2],[3]),('repeated_coefficient',[{'a':2,'b':1}],[1,2],[5])]
    out=[]
    for name,cs,values,targets in cases:out.append({'name':name,'constraints':cs,'values':values,'targets':targets,**csp(cs,values,10,targets)})
    assert [x['status'] for x in out]==['SAT','UNSAT','UNSAT','SAT'];assert out[2]['nodes']>1
    return out

def main():
    assert not(A/'RESULT.json').exists();started=datetime.now(timezone.utc).isoformat();spec=json.loads((D/'src/SPEC.json').read_text())
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert json.loads((ROOT/spec['packet_validation']).read_text())['status']=='PASS'
    save('FIXTURES.json',fixtures());packet=json.loads((ROOT/spec['packet']).read_text());selected=extract(packet,spec);save('SELECTED_GROUPS.json',selected)
    result=[]
    for ed in spec['readers']:
        forms=selected[ed]['forms'];r=solver(forms,spec['values'],spec['solver_seconds_per_reader'],spec['core_reduction_seconds_per_reader']);out={'reader':ed,'types':len(forms),'tokens':sum(len(f['occurrences']) for f in forms),'excluded':selected[ed]['excluded'],'solver':r}
        if r['status']=='UNSAT':
            cs=[forms[i]['counts'] for i in r['core_indices']];cert=csp(cs,spec['values'],spec['independent_csp_seconds_per_reader']);save(f'CERTIFICATE_{ed}.json',{'reader':ed,'core_indices':r['core_indices'],'constraints':cs,**cert});out['independent_search']={k:v for k,v in cert.items() if k not in ('certificate','witness')};out['decision']='CERTIFICATE_READY_FOR_REPLAY' if cert['status']=='UNSAT' else 'UNCERTIFIED_SOLVER_UNSAT'
        elif r['status']=='SAT':out['decision']='ARITHMETIC_WITNESS_READY_FOR_CHECK'
        else:out['decision']='INCONCLUSIVE'
        result.append(out);print(json.dumps(out),flush=True)
    save('RESULT.json',{'experiment':'GDT1231','status':'AWAITING_INDEPENDENT_VALIDATION','readers':result,'claim_ceiling':spec['claim_ceiling']});save('RUN_RECEIPT.json',{'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'z3_version':z3.get_version_string(),'new_native_queries':0})
if __name__=='__main__':main()
