#!/usr/bin/env python3
"""Independent finite-choice SMT for a source-directed letter merger."""
import argparse, gzip, hashlib, itertools, json, time
from pathlib import Path
import z3
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):
    p=A/n
    if p.exists():assert read(p)==d
    else:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def configuration():
    lock=read(E/'LOCK.json')
    for p,h in lock['files'].items():assert not Path(p).is_absolute() and sha(ROOT/p)==h,p
    for p in [Path(__file__),E/'src/SPEC.json']:
        assert p.relative_to(ROOT).as_posix() in lock['files']
    return read(E/'src/SPEC.json')
def records(s,name):
    if name=='deot':return [r['words'] for r in read(ROOT/s['deot_path'])['source_sections']]
    if name in ('b4','w1','bs1','gr1'):return [r['words'] for r in read(ROOT/s['recipe_path'])[name]]
    rows=read(ROOT/s['other_path'])[name]['PRIMARY']['units'];assert len(rows)==8000
    blocks=[(i,list(g)) for i,g in itertools.groupby(rows,key=lambda x:x['sentence_index'])]
    assert len(blocks)==len({i for i,g in blocks})
    return [[r['unit'] for r in g] for i,g in blocks]
def graph(rs):
    assert all(all(isinstance(w,str) and w for w in r) for r in rs)
    return sorted({w for r in rs for w in r}),{p for r in rs for p in zip(r,r[1:])}
def row_map(word,units):
    if len(word)!=len(units):return None
    d={}
    for c,u in zip(word,units):
        if c in d and d[c]!=u:return None
        d[c]=u
    return d
def verify(result,groups,W,edges,signs):
    words=result['words'];key=result['key'];alphabet=set(''.join(W))
    assert len(words)==len(groups)>0 and set(key)==alphabet
    assert all(u in signs for u in key.values())
    assert all(w in W for w in words)
    assert all(p in edges for p in zip(words,words[1:]))
    assert [[key[c] for c in w] for w in words]==groups
    return True
def solve(groups,W,edges,signs,seconds,blocked=None):
    # Each query gets a new solver; no supplied key or target truth enters it.
    if not groups:return {'status':'UNSAT','reason':'empty_message'}
    alphabet=sorted(set(''.join(W)));glyph={u:i for i,u in enumerate(signs)}
    assert all(u in glyph for g in groups for u in g)
    candidates=[];maps=[]
    for group in groups:
        rows=[(w,row_map(w,group)) for w in W if len(w)==len(group)]
        rows=[(w,m) for w,m in rows if m is not None]
        candidates.append([w for w,m in rows]);maps.append([m for w,m in rows])
    if any(not cs for cs in candidates):return {'status':'UNSAT','reason':'empty_word_candidates'}
    slv=z3.Solver();slv.set(timeout=int(seconds*1000))
    f={c:z3.Int('f_'+str(i)) for i,c in enumerate(alphabet)}
    choices=[z3.Int('w_'+str(i)) for i in range(len(groups))]
    for v in f.values():slv.add(v>=0,v<len(signs))
    for i,cs in enumerate(candidates):
        slv.add(choices[i]>=0,choices[i]<len(cs))
        for j,m in enumerate(maps[i]):
            slv.add(z3.Implies(choices[i]==j,z3.And([f[c]==glyph[u] for c,u in m.items()])))
    successors={w:set() for w in W}
    for x,y in edges:successors[x].add(y)
    for i in range(len(groups)-1):
        nextindex={w:j for j,w in enumerate(candidates[i+1])}
        for j,w in enumerate(candidates[i]):
            allowed=[choices[i+1]==nextindex[v] for v in sorted(successors[w]) if v in nextindex]
            slv.add(z3.Implies(choices[i]==j,z3.Or(allowed)))
    if blocked is not None:
        assert len(blocked)==len(groups)
        slv.add(z3.Or([choices[i]!=candidates[i].index(w) for i,w in enumerate(blocked)]))
    outcome=slv.check()
    if outcome==z3.unknown:return {'status':'UNKNOWN','reason':slv.reason_unknown()}
    if outcome==z3.unsat:return {'status':'UNSAT','reason':'finite_choice_smt_exhaustive'}
    model=slv.model();words=[cs[model.eval(v).as_long()] for cs,v in zip(candidates,choices)]
    key={c:signs[model.eval(v,model_completion=True).as_long()] for c,v in f.items()}
    result={'status':'SAT','words':words,'key':key}
    verify(result,groups,W,edges,signs)
    if blocked is not None:assert words!=blocked
    return result
def oracle(groups,W,edges,signs):
    alpha=sorted(set(''.join(W)));messages=set()
    for vals in itertools.product(signs,repeat=len(alpha)):
        key=dict(zip(alpha,vals));choices=[[w for w in W if [key[c] for c in w]==g] for g in groups]
        for words in itertools.product(*choices):
            if all(p in edges for p in zip(words,words[1:])):messages.add(tuple(words))
    return messages
def controls():
    checks=0
    for rs in [[['a','b','a']],[['ab','aa'],['b','ab']],[['a'],['b']]]:
        W,edges=graph(rs)
        for n in (1,2):
            for flat in itertools.product('xy',repeat=2*n):
                groups=[list(flat[2*i:2*i+2]) for i in range(n)]
                expected=oracle(groups,W,edges,list('xy'));r=solve(groups,W,edges,list('xy'),5)
                assert r['status']==('SAT' if expected else 'UNSAT');checks+=1
                if expected:
                    assert tuple(r['words']) in expected
                    second=solve(groups,W,edges,list('xy'),5,r['words'])
                    assert second['status']==('SAT' if len(expected)>1 else 'UNSAT')
    assert row_map('ab',['x','x'])=={'a':'x','b':'x'} and row_map('aa',['x','y']) is None
    W,edges=graph([['ab','ac']]);assert solve([['x','y'],['z','x']],W,edges,list('xyz'),5)['status']=='UNSAT'
    W,edges=graph([['a'],['b']]);r=solve([['x']],W,edges,list('xy'),5)
    assert solve([['x']],W,edges,list('xy'),5,r['words'])['status']=='SAT'
    W,edges=graph([['ab'],['c']]);r=solve([['x','y']],W,edges,list('xy'),5)
    assert solve([['x','y']],W,edges,list('xy'),5,r['words'])['status']=='UNSAT'
    return {'status':'PASS','complete_function_and_message_cases':checks,'collision_direction':True,
            'inconsistent_shared_key_rejected':True,'message_not_unused_key_uniqueness':True}
def gate(s):
    rs=records(s,'deot');W,edges=graph(rs);alpha=sorted(set(''.join(W)))
    idx=next((i for i,r in enumerate(rs) if len(r)>=32),None)
    if len(alpha)!=22 or idx is None:
        save('INDEPENDENT_CONTROL.json',{'status':'DOMAIN_ABSENT','reason':'source_alphabet_or_section'});return
    words=rs[idx][:32];active=set(''.join(words));pairs=[(alpha[0],alpha[20]),(alpha[1],alpha[21])]
    if not all(a in active and b in active for a,b in pairs):
        save('INDEPENDENT_CONTROL.json',{'status':'DOMAIN_ABSENT','reason':'required_collisions_not_active'});return
    key={c:s['signs'][j%20] for j,c in enumerate(alpha)};groups=[[key[c] for c in w] for w in words]
    verify({'words':words,'key':key},groups,W,edges,s['signs'])
    first=solve(groups,W,edges,s['signs'],s['independent_seconds']);second=None
    if first['status']=='UNSAT':status='INVALID_CONTROL_STOP'
    elif first['status']!='SAT':status=first['status']
    elif first['words']!=words:status='AMBIGUOUS'
    else:
        assert all(first['key'][c]==key[c] for c in active)
        second=solve(groups,W,edges,s['signs'],s['independent_seconds'],words)
        status='PASS_EXACT_UNIQUE' if second['status']=='UNSAT' else 'AMBIGUOUS' if second['status']=='SAT' else 'UNKNOWN'
    save('INDEPENDENT_CONTROL.json',{'experiment_id':'GDT1420','status':status,'section_index':idx,
         'planted_words':words,'planted_key':key,'encoded_groups':groups,'active_collision_pairs':pairs,
         'result':first,'second_message':second,'controls':controls(),'lock_sha256':sha(E/'LOCK.json')})
    print(json.dumps({'independent_gate':status}))
def native(s):
    assert read(A/'INDEPENDENT_CONTROL.json')['status']=='PASS_EXACT_UNIQUE'
    assert read(A/'GATE_VALIDATION.json')['status']=='PASS'
    packet=read(ROOT/s['native_path']);rows=[r for l in packet['source_unit']['lines'] for r in l['groups']]
    assert len(rows)==77 and rows==packet['original_groups']
    signs=sorted(s['signs'],key=lambda u:(-len(u),u));groups=[]
    for row in rows:
        text=row[2];pos=0;us=[]
        while pos<len(text):
            u=next((u for u in signs if text.startswith(u,pos)),None);assert u is not None
            us.append(u);pos+=len(u)
        groups.append(us)
    assert groups==packet['original_units']
    cases=[]
    for name in s['native_sources']:
        W,edges=graph(records(s,name));r=solve(groups,W,edges,s['signs'],s['native_seconds']);second=None
        if r['status']=='SAT':second=solve(groups,W,edges,s['signs'],s['native_seconds'],r['words'])
        cases.append({'source':name,'result':r,'second_message':second})
    save('INDEPENDENT_RESULT.json',{'experiment_id':'GDT1420','cases':cases,'original_groups':77})
    print(json.dumps({'independent_cases':[(c['source'],c['result']['status']) for c in cases]}))
def validate(s):
    primary=read(A/'CONTROL.json');own=read(A/'INDEPENDENT_CONTROL.json')
    assert {primary['status'],own['status']}!={'PASS_EXACT_UNIQUE','AMBIGUOUS'}, 'Contradictory control uniqueness results'
    if own['status']=='DOMAIN_ABSENT':
        receipt={'experiment_id':'GDT1420','status':'PASS_CONTROL_DOMAIN_STOP_ACCOUNTING','native_authorized':False}
    else:
        W,edges=graph(records(s,'deot'));groups=own['encoded_groups']
        assert primary['source_words']==own['planted_words'] and primary['planted_key']==own['planted_key']
        assert primary['encoded_groups']==groups and primary['source_section_index']==own['section_index']
        assert primary['active_collision_pairs']==own['active_collision_pairs']
        def primary_certificate(r,gs,W,es):
            if r and r['status']=='SAT':verify({'words':r['source_words'],'key':r['key']},gs,W,es,s['signs'])
        primary_certificate(primary['result'],groups,W,edges)
        primary_certificate(primary.get('second_message'),groups,W,edges)
        if own['status']!='PASS_EXACT_UNIQUE' or primary['status']!='PASS_EXACT_UNIQUE':
            assert not (A/'RESULT.json').exists() and not (A/'INDEPENDENT_RESULT.json').exists()
            receipt={'experiment_id':'GDT1420','status':'PASS_CONTROL_STOP_ACCOUNTING','native_authorized':False,
                     'control_status':{'primary':primary['status'],'independent':own['status']}}
        else:
            assert primary['result']['source_words']==own['planted_words']
            assert primary['second_message']['status']=='UNSAT' and own['second_message']['status']=='UNSAT'
            p=read(A/'RESULT.json');q=read(A/'INDEPENDENT_RESULT.json');packet=read(ROOT/s['native_path'])
            assert p['groups']==packet['original_units'] and p['original_groups']==packet['original_groups']
            assert p['lock_sha256']==sha(E/'LOCK.json') and p['claim_ceiling']==s['claim_ceiling']
            assert [c['source'] for c in p['cases']]==[c['source'] for c in q['cases']]==s['native_sources']
            conclusions=[]
            for pc,qc in zip(p['cases'],q['cases']):
                W,edges=graph(records(s,pc['source']));gs=packet['original_units']
                primary_certificate(pc['result'],gs,W,edges);primary_certificate(pc.get('second_message'),gs,W,edges)
                for r in [qc['result'],qc.get('second_message')]:
                    if r and r['status']=='SAT':verify(r,gs,W,edges,s['signs'])
                statuses={pc['result']['status'],qc['result']['status']}
                assert statuses!={'SAT','UNSAT'}, 'Independent exact-result disagreement'
                for case,wordkey in [(pc,'source_words'),(qc,'words')]:
                    first=case['result'];second=case.get('second_message')
                    if first['status']=='SAT' and second and second['status']=='SAT':
                        assert first[wordkey]!=second[wordkey]
                if (pc['result']['status']==qc['result']['status']=='SAT'
                    and pc.get('second_message') and qc.get('second_message')
                    and pc['second_message']['status']==qc['second_message']['status']=='UNSAT'):
                    assert pc['result']['source_words']==qc['result']['words'], 'INVALID: incompatible unique messages'
                effective='SAT_CAPACITY_ONLY' if 'SAT' in statuses else 'UNSAT' if statuses=={'UNSAT'} else 'UNRESOLVED'
                conclusions.append({'source':pc['source'],'primary':pc['result']['status'],
                    'independent':qc['result']['status'],'effective':effective})
            receipt={'experiment_id':'GDT1420','status':'PASS_INDEPENDENT_CERTIFICATE_AND_DUAL_RESULT_ACCOUNTING',
                     'native_authorized':True,'cases':conclusions}
    receipt.update(validator_sha256=sha(Path(__file__)),lock_sha256=sha(E/'LOCK.json'),
        scope='Independent finite-choice SMT and direct certificate accounting only. No native semantics, language identification or historical writer claim.')
    save('VALIDATION.json',receipt);print(json.dumps({'status':receipt['status']}))
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    for mode in ('controls','gate','native','validate'):g.add_argument('--'+mode,action='store_true')
    a=p.parse_args()
    if a.controls:print(json.dumps(controls()));return
    s=configuration()
    if a.gate:gate(s)
    elif a.native:native(s)
    else:validate(s)
if __name__=='__main__':main()
