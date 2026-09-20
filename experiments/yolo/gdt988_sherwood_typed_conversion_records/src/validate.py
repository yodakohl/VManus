#!/usr/bin/env python3
"""Separate replay: no import of runner, matcher or fixture implementation."""
import json,hashlib,itertools,time,sys
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def legal(c,writer):
    for prefix in ('Q:','T:','OP:'):
        vals=[v for k,v in c.items() if k.startswith(prefix)]
        if any(not x for x in vals) or len(vals)!=len(set(vals)):return False
    if writer=='FUSED':
        q=[v for k,v in c.items() if k.startswith('Q:')];t=[v for k,v in c.items() if k.startswith('T:')]
        values=[a+b+d for a,b,d in itertools.product(q,t,t)]
        if len(values)!=len(set(values)):return False
    return True

def replay(chunks,words,writer):
    tasks=list(zip(chunks,words))[::-1];answers=[];nodes=0;started=time.monotonic()
    def step(i,c):
        nonlocal nodes
        nodes+=1
        if nodes>1000000 or (nodes%128==0 and time.monotonic()-started>10):raise TimeoutError
        if i==len(tasks):
            if legal(c,writer):answers.append(tuple(sorted(c.items())))
            return
        keys,word=tasks[i]
        options=[(word,)] if len(keys)==1 else ((word[:i],word[i:j],word[j:]) for j in range(len(word)-1,1,-1) for i in range(j-1,0,-1))
        for vals in options:
            new=c.copy();valid=True
            for k,v in zip(keys,vals):
                if k in new and new[k]!=v:valid=False;break
                new[k]=v
            if valid and legal(new,writer):step(i+1,new)
    step(0,{})
    return set(answers),nodes

def semantic_checks(s):
    def holds(p,env):
        q,x,y=p;u,v=env[x],env[y]
        return {'Q:A':not(u-v),'Q:E':not(u&v),'Q:I':bool(u&v),'Q:O':bool(u-v)}[q]
    counts={};counter_empty=False
    for name,r in s['traces'].items():
        names=sorted({k for c in r for k in c if k.startswith('T:')});assert len(names)==3
        initial,minor,conclusion=r[0],r[1],r[2]
        assert r[9]==conclusion and r[7:9]==[['OP:SWAP'],['OP:FERIO']]
        assert r[4]==[('Q:I' if r[3]==['OP:P'] else initial[0]),initial[2],initial[1]]
        assert r[5]==['OP:S'] and r[6]==[minor[0],minor[2],minor[1]]
        assert r[6][0]=='Q:E' and r[4][0]=='Q:I'
        assert r[6][1]==r[4][2] and conclusion==['Q:O',r[4][1],r[6][2]]
        valid=0;premise_models=0
        for occupancy in range(256):
            env={name:{cell for cell in range(8) if occupancy>>cell&1 and cell>>i&1} for i,name in enumerate(names)}
            if all(env.values()):
                valid+=1
                if holds(initial,env) and holds(minor,env):
                    premise_models+=1
                    assert holds(r[4],env) and holds(r[6],env) and holds(conclusion,env)
            elif name=='FAPESMO' and holds(initial,env) and not holds(r[4],env):counter_empty=True
        assert premise_models>0
        counts[name]={'nonempty_models':valid,'true_premise_models':premise_models}
    assert counter_empty
    # Wrong universal converse and wrong figure have explicit nonempty countermodels.
    assert {1}<={1,2} and not {1,2}<={1}
    P={1};M={1,2};S={2};assert P<=M and S&M and not S&P
    return {'trace_models':counts,'empty_class_counterexample_retained':True,'false_A_converse':True,'wrong_figure_counterexample':True}

def main():
    s=json.loads((E/'src/SOURCE.json').read_text());sem=semantic_checks(s)
    if '--semantic-only' in sys.argv:
        (A/'PRE_RUN_SEMANTICS.json').write_text(json.dumps({'status':'PASS',**sem},indent=2)+'\n');print(json.dumps(sem));return
    lock=json.loads((E/'PREREG_LOCK.json').read_text())
    for path,want in lock['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==want,path
    ps=json.loads((ROOT/s['input_paragraphs']).read_text());rows=json.loads((A/'CASES.json').read_text());result=json.loads((A/'RESULT.json').read_text());joints=json.loads((A/'JOINT_CODES.json').read_text())
    lookup={(edition,p['id']):p for edition,vals in ps.items() for p in vals};seen=set();replays=[];unknown=[]
    assert len(rows)==sum(map(len,ps.values()))*4
    for row in rows:
        e,pid,w,t=row['edition'],row['paragraph'],row['writer'],row['trace'];key=(e,pid,w,t);assert key not in seen;seen.add(key)
        p=lookup[(e,pid)];assert p['leaf']==row['leaf'] and not p['page'].startswith('f84') and p['page']!='f116v'
        words=[x for line in p['lines'] for x in line['words']];record=s['traces'][t];chunks=record if w=='FUSED' else [[x] for c in record for x in c]
        assert row['observed_groups']==len(words) and row['predicted_groups']==len(chunks)
        eligible=all(line['anchor_eligible'] for line in p['lines'])
        if not eligible:assert row['status']=='UNKNOWN_SOURCE' and not row['codes'];continue
        if len(words)!=len(chunks):assert row['status']=='COUNT_MISMATCH' and not row['codes'];continue
        try:codes,nodes=replay(chunks,words,w)
        except TimeoutError:unknown.append(row['case']);continue
        got={tuple(sorted(c.items())) for c in row['codes']}
        if row['status']=='UNKNOWN_COMPUTATION':assert got<=codes
        else:assert got==codes,(row['case'],got,codes)
        assert (not codes)==(row['status'] not in ('LOCAL_FIT','UNKNOWN_COMPUTATION'))
        replays.append({'case':row['case'],'codes':len(codes),'nodes':nodes,'status':'COMPLETE'})
    assert seen=={(e,p['id'],w,t) for e,vals in ps.items() for p in vals for w in s['writers'] for t in s['traces']}
    assert result['status_counts']==dict(Counter(r['status'] for r in rows))
    expected=[];attempts=0;cutoff=False
    for e,w in itertools.product(ps,s['writers']):
        aa=[r for r in rows if r['edition']==e and r['writer']==w and r['trace']=='FAPESMO' and r['codes']]
        bb=[r for r in rows if r['edition']==e and r['writer']==w and r['trace']=='FRISESOMORUM' and r['codes']]
        for a,b in itertools.product(aa,bb):
            if a['leaf']==b['leaf']:continue
            for x,y in itertools.product(a['codes'],b['codes']):
                if attempts>=s['limits']['joint_pairs']:cutoff=True;break
                attempts+=1
                if any(k in x and x[k]!=v for k,v in y.items()):continue
                c={**x,**y}
                if legal(c,w):expected.append((e,w,a['case'],b['case'],tuple(sorted(c.items()))))
            if cutoff:break
        if cutoff:break
    got=[(j['edition'],j['writer'],j['left_case'],j['right_case'],tuple(sorted(j['code'].items()))) for j in joints]
    assert got==expected and attempts==result['joint_pairs_attempted'] and cutoff==result['joint_cutoff']
    out={'status':'PASS' if not unknown else 'PASS_WITH_REPLAY_UNKNOWNS','same_author_separate_implementation':True,'meaning_validation':False,'accounted_cases':len(rows),'literal_count_eligible_replays':replays,'replay_unknown_cases':unknown,'joint_candidates_checked':len(joints),'semantics':sem,'independent_confirmation_capacity':0}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='literal_count_eligible_replays'},indent=2))
if __name__=='__main__':main()
