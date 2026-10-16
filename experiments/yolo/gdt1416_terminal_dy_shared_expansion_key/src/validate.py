#!/usr/bin/env python3
"""Independent positional terminal-dy macro lexical-capacity validation."""
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

TAIL='@TAIL_dy'
def macro(group):return group[:-2]+[TAIL] if group[-2:]==['d','y'] else group[:]
def output(group,key,tail):return ''.join(tail if u==TAIL else key[u] for u in macro(group))
def solve(groups,words,signs,mode,seconds=30):
    deadline=time.monotonic()+seconds;alphabet=sorted(set(''.join(words)));W=set(words)
    solver=z3.Solver();variables={u:z3.Int('letter_'+str(i)) for i,u in enumerate(signs)};tail=z3.String('terminal_expansion')
    solver.add(z3.Length(tail)>0)
    for var in variables.values():solver.add(z3.Or([var==ord(c) for c in alphabet]))
    oriented=W|{w[::-1] for w in W} if mode=='BIDIR' else W
    for group in sorted(set(map(tuple,groups))):
        parsed=macro(list(group));has_tail=bool(parsed) and parsed[-1]==TAIL;body=parsed[:-1] if has_tail else parsed
        options=[]
        for word in sorted(oriented):
            if time.monotonic()>deadline:return {'status':'UNKNOWN','reason':'independent build limit'}
            if (has_tail and len(word)<=len(body)) or (not has_tail and len(word)!=len(body)):continue
            assignments={};valid=True
            for u,c in zip(body,word):
                if u in assignments and assignments[u]!=c:valid=False;break
                assignments[u]=c
            if not valid:continue
            terms=[variables[u]==ord(c) for u,c in assignments.items()]
            if has_tail:terms.append(tail==z3.StringVal(word[len(body):]))
            options.append(z3.And(terms))
        solver.add(z3.Or(options))
    remaining=int(1000*(deadline-time.monotonic()))
    if remaining<=0:return {'status':'UNKNOWN','reason':'independent build limit'}
    solver.set(timeout=remaining);answer=solver.check();result={'status':str(answer).upper()}
    if answer==z3.unknown:result['reason']=solver.reason_unknown()
    elif answer==z3.sat:
        model=solver.model();key={u:chr(model.eval(v,model_completion=True).as_long()) for u,v in variables.items()}
        t=model.eval(tail,model_completion=True).as_string();assert t
        assert all(output(list(g),key,t) in W or mode=='BIDIR' and output(list(g),key,t)[::-1] in W for g in groups)
        result.update(key=key,T=t)
    return result

def controls():
    fixtures=[([['d','y']],['x']),([['a','d','y'],['d','y']],['axx','xx']),([['d','y','d','y']],['aaaa']),([['a','d','y'],['a']],['xy','z']),([['a','d','y'],['d','y']],['ab','b']),([['d','y','a']],['xyx'])]
    count=0
    for groups,words in fixtures:
        signs=sorted(set(u for g in groups for u in g));letters=sorted(set(''.join(words)))
        for mode in ['FWD','BIDIR']:
            oriented=set(words)|{w[::-1] for w in words} if mode=='BIDIR' else set(words)
            tails={w[i:] for w in oriented for i in range(len(w))};possible=False
            for vals in itertools.product(letters,repeat=len(signs)):
                key=dict(zip(signs,vals))
                if any(all(output(g,key,t) in oriented for g in groups) for t in tails):possible=True;break
            assert solve(groups,words,signs,mode,3)['status']==('SAT' if possible else 'UNSAT');count+=1
    assert macro(list('dydydy'))==['d','y','d','y',TAIL]
    assert macro(list('dyad'))==list('dyad')
    assert collapse(['e','e','d','y'])==['e','d','y']
    return {'status':'PASS','exhaustive_function_and_tail_fixtures':count,'positional_macro_checks':3,'no_injection':True}

def lockcheck():
    lock=read(E/'LOCK.json')
    for p,h in lock['files'].items():assert not Path(p).is_absolute() and sha(ROOT/p)==h,p
    for p in [Path(__file__),E/'src/run.py',E/'src/SPEC.json']:assert p.relative_to(ROOT).as_posix() in lock['files']
    return read(E/'src/SPEC.json'),lock

def generate(s,words):
    alphabet=sorted(set(''.join(words)))[:20];W=sorted({w for w in words if set(w)<=set(alphabet)})
    for tail in sorted(W,key=lambda w:(len(w),w)):
        if len(tail)<2:continue
        ends=[w for w in W if w!=tail and w.endswith(tail)];others=[w for w in W if not w.endswith(tail)]
        if len(ends)>=10 and len(others)>=10:break
    else:raise AssertionError('Declared generator domain absent')
    cycle=[tail]+ends[:10]+others[:10];chosen=[cycle[i%len(cycle)] for i in range(77)]
    bodies=[w[:-len(tail)] if w.endswith(tail) else w for w in chosen]
    counts={c:sum(b.count(c) for b in bodies) for c in alphabet};rank=sorted(alphabet,key=lambda c:(-counts[c],c))
    safe=[c for c in rank if counts[c]>0 and all(c+c not in b for b in bodies)];assert len(safe)>=2
    canonical=[u for u in s['signs'] if u not in ['d','y']];key={'e':safe[0],'i':safe[1]}
    rest=[c for c in alphabet if c not in key.values()]
    key.update(zip([u for u in canonical if u not in key],rest))
    aliases=rank[:2]
    if ''.join(aliases)==tail:aliases=aliases[::-1]
    key['d'],key['y']=aliases;assert key['d']+key['y']!=tail
    inverse={key[u]:u for u in canonical};aliasmap=dict(zip(aliases,['d','y']))
    base=[];encoded=[]
    for wi,(word,body) in enumerate(zip(chosen,bodies)):
        has=word.endswith(tail);group=[]
        for ci,c in enumerate(body):
            alias=c in aliasmap and (wi+ci)%2==1 and (has or ci<len(body)-2)
            group.append(aliasmap[c] if alias else inverse[c])
        if has:group+=['d','y']
        base.append(group);encoded.append([u for ui,u in enumerate(group) for _ in range(1+(wi+ui)%3 if u in ['e','i'] else 1)])
    assert [collapse(g) for g in encoded]==base
    ordinary={u for g in base for u in macro(g) if u!=TAIL};assert {'d','y'}<=ordinary
    assert any(TAIL in macro(g) for g in base) and any(TAIL not in macro(g) for g in base)
    assert any(len(a)>len(b) for a,b in zip(encoded,base))
    assert [output(g,key,tail) for g in base]==chosen
    return chosen,key,tail,encoded,base

def direct(result,groups,words,signs,mode):
    key=result['key'];tail=result['tail'];W=set(words);alphabet=set(''.join(W))
    assert set(key)==set(signs) and all(isinstance(c,str) and len(c)==1 and c in alphabet for c in key.values())
    assert isinstance(tail,str) and tail and set(tail)<=alphabet
    assert len(result['certificate'])==len(groups)
    for group,entry in zip(groups,result['certificate']):
        assert entry['units']==group and entry['atoms']==macro(group)
        assert entry['source_word'] in W and entry['direction'] in (['FWD'] if mode=='FWD' else ['FWD','REV'])
        expected=entry['source_word'] if entry['direction']=='FWD' else entry['source_word'][::-1]
        assert output(group,key,tail)==expected
    return {'status':'SAT_CERTIFICATE_VERIFIED','positions':len(groups),'tail_length':len(tail),'distinct_ordinary_values':len(set(key.values()))}

def gate():
    s,lock=lockcheck();words=sources(s,True)['deot'];control=read(A/'CONTROL.json')
    assert control['source']=='deot'
    if control['status']=='DOMAIN_ABSENT':
        save(A/'GATE_VALIDATION.json',{'experiment_id':'GDT1416','status':'STOP_DOMAIN_ABSENT_NOT_MODEL_REJECTION','control_sha256':sha(A/'CONTROL.json'),'lock_sha256':sha(E/'LOCK.json'),'scope':'Primary generator domain stop retained; no native permission or model exclusion.'});return
    assert control['status']=='GENERATED'
    chosen,key,tail,encoded,base=generate(s,words)
    for field,value in {'source_words':chosen,'planted_key':key,'planted_tail':tail,'encoded_groups':encoded,'collapsed_groups':base,'words_cycle':chosen[:21],'ordinary_alias_chars':[key['d'],key['y']]}.items():assert control[field]==value,field
    if control['result']['status']!='SAT':
        save(A/'GATE_VALIDATION.json',{'experiment_id':'GDT1416','status':'STOP_CONTROL_NOT_SAT','control_sha256':sha(A/'CONTROL.json'),'lock_sha256':sha(E/'LOCK.json'),'primary_status':control['result']['status'],'scope':'No native inference; known writer and search outcome separate.'});return
    cert=direct(control['result'],base,words,s['signs'],'BIDIR')
    receipt={'experiment_id':'GDT1416','status':'PASS','source_free_controls':controls(),'certificate':cert,'native_access':False,'generated_writer_verified':True,'pins':{'lock_sha256':sha(E/'LOCK.json'),'control_sha256':sha(A/'CONTROL.json'),'validator_sha256':sha(Path(__file__))}}
    save(A/'GATE_VALIDATION.json',receipt);print(json.dumps({'status':'PASS','native_access':False}))

def native():
    s,lock=lockcheck();gr=read(A/'GATE_VALIDATION.json')
    assert gr['status']=='PASS' and gr['pins']['lock_sha256']==sha(E/'LOCK.json') and gr['pins']['control_sha256']==sha(A/'CONTROL.json')
    worksheet=read(ROOT/s['worksheet_path']);selected=[x for x in worksheet['units'] if x['unit_id']==s['passage_unit']];assert len(selected)==1
    lines=selected[0]['lines'];assert [l['metadata']['locus'] for l in lines]==['f75v.'+str(i) for i in range(43,50)]
    assert str(lines[0]['metadata']['paragraph_start'])=='1' and str(lines[-1]['metadata']['paragraph_end'])=='1'
    originals=[];groups=[]
    for line in lines:
        rows=line['original_groups'];meta=line['metadata']
        assert meta['page']=='f75v' and meta['edition']=='IT2a' and len(rows)==int(meta['source_group_count'])
        assert [int(r[1]) for r in rows]==list(range(1,len(rows)+1))
        for row in rows:
            assert len(row)==5
            parsed=parse(row[2],s['signs']);assert parsed is not None
            groups.append(collapse(parsed));originals.append(row)
    assert len(groups)==77==s['expected_passage_groups']
    result=read(A/'RESULT.json')
    assert result['experiment_id']=='GDT1416' and result['status']=='LOCAL_TERMINAL_DY_KEY_CAPACITY'
    assert result['groups']==groups and result['original_groups']==originals
    assert result['claim_ceiling']==s['claim_ceiling'] and result['global1406failures_retained'] is True
    assert [(c['source'],c['mode']) for c in result['cases']]==list(itertools.product(s['source_names'],s['modes']))
    W=sources(s);checked=[]
    for c in result['cases']:
        r=c['result'];status=r['status'];assert status in ['SAT','UNSAT','UNKNOWN']
        if status=='SAT':answer=direct(r,groups,W[c['source']],s['signs'],c['mode'])
        elif status=='UNKNOWN':answer={'status':'ORIGINAL_UNKNOWN_PRESERVED'}
        else:
            independent=solve(groups,W[c['source']],s['signs'],c['mode'],s['independent_seconds_per_case'])
            answer={'status':{'UNSAT':'UNSAT_INDEPENDENTLY_CONFIRMED','SAT':'DISAGREEMENT','UNKNOWN':'UNSAT_UNCONFIRMED'}[independent['status']],'independent':independent}
        checked.append({'source':c['source'],'mode':c['mode'],'primary_status':status,**answer})
    status='DISAGREEMENT' if any(c['status']=='DISAGREEMENT' for c in checked) else 'INCOMPLETE_UNSAT_UNCONFIRMED' if any(c['status']=='UNSAT_UNCONFIRMED' for c in checked) else 'PASS_INDEPENDENT_CERTIFICATE_AND_STATUS_ACCOUNTING'
    receipt={'experiment_id':'GDT1416','status':status,'groups':77,'cases':checked,'controls':controls(),'pins':{'lock_sha256':sha(E/'LOCK.json'),'validator_sha256':sha(Path(__file__)),'result_sha256':sha(A/'RESULT.json'),'gate_validation_sha256':sha(A/'GATE_VALIDATION.json')},'scope':'Independent finite lexical disjunctions with ordinary one-codepoint variables and one nonempty String expansion. No injection or arbitrary tail length cap. Native positional dy parsing differs from free UD; old failures retained. SAT is unassigned lexical capacity only.'}
    save(A/'VALIDATION.json',receipt);print(json.dumps({'status':status}))
if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    for name in ['controls','gate','native']:g.add_argument('--'+name,action='store_true')
    args=p.parse_args()
    if args.controls:print(json.dumps(controls()))
    elif args.gate:gate()
    else:native()
