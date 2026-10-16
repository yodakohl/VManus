#!/usr/bin/env python3
"""Independent many-to-one lexical table certificate and Z3 verification."""
import argparse,gzip,hashlib,itertools,json,time
from pathlib import Path
import z3
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    if p.exists():assert read(p)==x
    else:p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def collapse(xs):return [x for i,x in enumerate(xs) if not(i and x in ('e','i') and xs[i-1]==x)]
def parse(word,signs):
    paths={0:[[]]}
    for i in range(len(word)):
        for sign in signs:
            if word.startswith(sign,i):
                dest=i+len(sign)
                paths[dest]=(paths.get(dest,[])+[p+[sign] for p in paths.get(i,[])])[:2]
    return paths[len(word)][0] if len(paths.get(len(word),[]))==1 else None

def sources(s,only=False):
    d=read(ROOT/s['deot_path']);out={'deot':[w for section in d['source_sections'] for w in section['words']]}
    if only:return out
    recipes=read(ROOT/s['recipe_path']);other=read(ROOT/s['other_path'])
    for n in ['b4','w1','bs1','gr1']:out[n]=[w for r in recipes[n] for w in r['words']]
    for n in ['OLD_ITALIAN_UD_CONTROL','LATIN_PROIEL_CONTROL','ANCIENT_GREEK_PROIEL_CONTROL']:
        out[n]=[r['unit'] for r in other[n]['PRIMARY']['units']];assert len(out[n])==8000
    assert set(out)==set(s['source_names'])
    assert all(isinstance(w,str) and w for words in out.values() for w in words)
    return out

def solve(groups,words,signs,mode,seconds=30):
    deadline=time.monotonic()+seconds;alphabet=sorted(set(''.join(words)));W=set(words)
    solver=z3.Solver();variables={u:z3.Int('u'+str(i)) for i,u in enumerate(signs)}
    for var in variables.values():solver.add(z3.Or([var==ord(c) for c in alphabet]))
    bylen={}
    for w in W:
        bylen.setdefault(len(w),set()).add(w)
        if mode=='BIDIR':bylen[len(w)].add(w[::-1])
    for group in sorted(set(map(tuple,groups))):
        choices=[]
        for output in sorted(bylen.get(len(group),[])):
            if time.monotonic()>deadline:return {'status':'UNKNOWN','reason':'independent build limit'}
            mapping={};valid=True
            for u,c in zip(group,output):
                if u in mapping and mapping[u]!=c:valid=False;break
                mapping[u]=c
            if valid:choices.append(z3.And([variables[u]==ord(c) for u,c in mapping.items()]))
        solver.add(z3.Or(choices))
    remaining=int(1000*(deadline-time.monotonic()))
    if remaining<=0:return {'status':'UNKNOWN','reason':'independent build limit'}
    solver.set(timeout=remaining);answer=solver.check()
    out={'status':str(answer).upper()}
    if answer==z3.unknown:out['reason']=solver.reason_unknown()
    if answer==z3.sat:
        model=solver.model();key={u:chr(model.eval(v,model_completion=True).as_long()) for u,v in variables.items()}
        assert all(''.join(key[u] for u in g) in W or mode=='BIDIR' and ''.join(key[u] for u in g)[::-1] in W for g in groups)
        out['key']=key
    return out

def direct(result,groups,words,signs,mode):
    key=result['key'];W=set(words);alphabet=set(''.join(W))
    assert set(key)==set(signs) and all(isinstance(c,str) and len(c)==1 and c in alphabet for c in key.values())
    assert len(result['certificate'])==len(groups)
    for group,cert in zip(groups,result['certificate']):
        assert cert['units']==group and cert['source_word'] in W
        assert cert['direction'] in (['FWD'] if mode=='FWD' else ['FWD','REV'])
        expected=cert['source_word'] if cert['direction']=='FWD' else cert['source_word'][::-1]
        assert ''.join(key[u] for u in group)==expected
    return {'status':'SAT_CERTIFICATE_VERIFIED','positions':len(groups),'distinct_outputs':len(set(key.values()))}

def controls():
    fixtures=[([['a','b']],['xx']),([['a','a']],['xy']),([['a','b'],['b','a']],['xy']),([['a'],['b']],['x']),([['a','b'],['a','a']],['xy','yy']),([['a','b'],['b','b']],['xy','xx'])]
    total=0
    for groups,words in fixtures:
        signs=['a','b','unused'];chars=sorted(set(''.join(words)))
        for mode in ['FWD','BIDIR']:
            possible=False
            for values in itertools.product(chars,repeat=len(signs)):
                key=dict(zip(signs,values));outputs=[''.join(key[u] for u in g) for g in groups]
                if all(w in words or mode=='BIDIR' and w[::-1] in words for w in outputs):possible=True;break
            assert solve(groups,words,signs,mode,3)['status']==('SAT' if possible else 'UNSAT');total+=1
    assert collapse(['e','e','a','a','i','i'])==['e','a','a','i']
    assert parse('aa',['a','aa']) is None
    return {'status':'PASS','brute_all_functions_vs_z3':total,'injection_imposed':False}

def lockcheck():
    lock=read(E/'LOCK.json')
    for p,h in lock['files'].items():assert not Path(p).is_absolute() and sha(ROOT/p)==h,p
    for p in [Path(__file__),E/'src/run.py',E/'src/SPEC.json']:assert p.relative_to(ROOT).as_posix() in lock['files']
    return read(E/'src/SPEC.json'),lock

def generated(s,words):
    alphabet=sorted(set(''.join(words)))[:20];indices=[i for i,w in enumerate(words) if set(w)<=set(alphabet)][:77];chosen=[words[i] for i in indices]
    assert len(chosen)==77
    counts={c:sum(w.count(c) for w in chosen) for c in alphabet}
    order=sorted(alphabet,key=lambda c:(-counts[c],c))
    safe=[c for c in order if all(c+c not in w for w in chosen)]
    assert len(safe)>=2
    key={'e':safe[0],'i':safe[1]}
    remaining=[c for c in alphabet if c not in key.values()]
    canonical=[u for u in s['signs'] if u not in ['cph','cfh']]
    for u,c in zip([u for u in canonical if u not in key],remaining):key[u]=c
    aliases=[c for c in order if c not in [key['e'],key['i']]][:2]
    key['cph'],key['cfh']=aliases
    inverse={key[u]:u for u in canonical};aliasdict=dict(zip(aliases,['cph','cfh']))
    base=[];encoded=[]
    for wi,w in enumerate(chosen):
        group=[aliasdict[c] if c in aliasdict and (wi+ci)%2 else inverse[c] for ci,c in enumerate(w)]
        base.append(group);encoded.append([u for ui,u in enumerate(group) for _ in range(1+(wi+ui)%3 if u in ['e','i'] else 1)])
    assert [collapse(g) for g in encoded]==base
    used={u for g in base for u in g}
    assert {'e','i','cph','cfh'}<=used and {inverse[c] for c in aliases}<=used
    assert any(len(x)>len(y) for x,y in zip(encoded,base))
    assert all(''.join(key[u] for u in g)==w for g,w in zip(base,chosen))
    return {'source_words':chosen,'planted_key':key,'encoded_groups':encoded,'collapsed_groups':base,'selection_indices':indices,'alias_pairs':[{'character':c,'canonical':inverse[c],'alias':aliasdict[c]} for c in aliases]}

def gate():
    s,lock=lockcheck();words=sources(s,True)['deot'];expected=generated(s,words);control=read(A/'CONTROL.json')
    assert control['status']=='GENERATED' and control['source']=='deot'
    for k,value in expected.items():assert control[k]==value,k
    assert control['result']['status']=='SAT'
    cert=direct(control['result'],expected['collapsed_groups'],words,s['signs'],'BIDIR')
    receipt={'experiment_id':'GDT1414','status':'PASS','source_free_controls':controls(),'certificate':cert,'native_access':False,'generated_aliases_verified':True,'pins':{'lock_sha256':sha(E/'LOCK.json'),'control_sha256':sha(A/'CONTROL.json'),'validator_sha256':sha(Path(__file__))}}
    save(A/'GATE_VALIDATION.json',receipt);print(json.dumps({'status':'PASS','native_access':False}))

def native():
    s,lock=lockcheck();gate_receipt=read(A/'GATE_VALIDATION.json')
    assert gate_receipt['status']=='PASS' and gate_receipt['pins']['lock_sha256']==sha(E/'LOCK.json')
    assert gate_receipt['pins']['control_sha256']==sha(A/'CONTROL.json')
    worksheet=read(ROOT/s['worksheet_path']);selected=[x for x in worksheet['units'] if x['unit_id']==s['passage_unit']];assert len(selected)==1
    lines=selected[0]['lines'];assert [x['metadata']['locus'] for x in lines]==['f75v.'+str(i) for i in range(43,50)]
    groups=[];originals=[]
    assert str(lines[0]['metadata']['paragraph_start'])=='1' and str(lines[-1]['metadata']['paragraph_end'])=='1'
    for line in lines:
        rows=line['original_groups'];meta=line['metadata']
        assert meta['page']=='f75v' and meta['edition']=='IT2a' and len(rows)==int(meta['source_group_count'])
        assert [int(r[1]) for r in rows]==list(range(1,len(rows)+1))
        for row in rows:
            assert len(row)==5
            parsed=parse(row[2],s['signs']);assert parsed is not None
            groups.append(collapse(parsed));originals.append(row)
    assert len(groups)==77==s['expected_passage_groups']
    result=read(A/'RESULT.json');assert result['groups']==groups and result['original_groups']==originals
    assert result['experiment_id']=='GDT1414' and result['status']=='LOCAL_HOMOPHONIC_KEY_CAPACITY'
    assert result['claim_ceiling']==s['claim_ceiling'] and result['global1406failures_retained'] is True
    assert [(c['source'],c['mode']) for c in result['cases']]==list(itertools.product(s['source_names'],s['modes']))
    W=sources(s);checks=[]
    for c in result['cases']:
        r=c['result'];status=r['status'];assert status in ['SAT','UNSAT','UNKNOWN']
        if status=='SAT':checked=direct(r,groups,W[c['source']],s['signs'],c['mode'])
        elif status=='UNKNOWN':checked={'status':'ORIGINAL_UNKNOWN_PRESERVED'}
        else:
            reply=solve(groups,W[c['source']],s['signs'],c['mode'],s['independent_seconds_per_case'])
            checked={'status':{'UNSAT':'UNSAT_INDEPENDENTLY_CONFIRMED','SAT':'DISAGREEMENT','UNKNOWN':'UNSAT_UNCONFIRMED'}[reply['status']],'independent':reply}
        checks.append({'source':c['source'],'mode':c['mode'],'primary_status':status,**checked})
    outcome='DISAGREEMENT' if any(c['status']=='DISAGREEMENT' for c in checks) else 'INCOMPLETE_UNSAT_UNCONFIRMED' if any(c['status']=='UNSAT_UNCONFIRMED' for c in checks) else 'PASS_INDEPENDENT_CERTIFICATE_AND_STATUS_ACCOUNTING'
    receipt={'experiment_id':'GDT1414','status':outcome,'cases':checks,'groups':77,'controls':controls(),'pins':{'lock_sha256':sha(E/'LOCK.json'),'validator_sha256':sha(Path(__file__)),'result_sha256':sha(A/'RESULT.json'),'gate_validation_sha256':sha(A/'GATE_VALIDATION.json')},'scope':'Local homophonic function, no injection; primary UNKNOWN preserved. SAT is lexical candidate capacity only, not grammar or meaning. Old globally closed source failures remain.'}
    save(A/'VALIDATION.json',receipt);print(json.dumps({'status':outcome}))
if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    for name in ['controls','gate','native']:g.add_argument('--'+name,action='store_true')
    a=p.parse_args()
    if a.controls:print(json.dumps(controls()))
    elif a.gate:gate()
    else:native()
