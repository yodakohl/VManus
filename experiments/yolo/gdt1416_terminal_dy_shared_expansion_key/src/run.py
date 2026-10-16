#!/usr/bin/env python3
"""One terminal dy macro plus a shared literal key; meanings unassigned."""
import argparse,collections,gzip,hashlib,itertools,json,re,time
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];TAIL='@TAIL_dy'
def read(p):
    p=Path(p);v=p.read_bytes();return json.loads(gzip.decompress(v) if p.suffix=='.gz' else v)
def save(n,v):(B/'artifacts'/n).write_text(json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2)+'\n')
def collapse(g):return [u for j,u in enumerate(g) if not(j and u in ('e','i') and g[j-1]==u)]
def atoms(g):return list(g[:-2])+[TAIL] if list(g[-2:])==['d','y'] else list(g)
def expand(g,key,tail):return ''.join(tail if u==TAIL else key[u] for u in atoms(g))
def lockcheck():
    for p,h in read(B/'LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
def sources(spec):
    recipes=read(R/spec['recipe_path']);deot=read(R/spec['deot_path']);other=read(R/spec['other_path']);out={}
    for n in spec['source_names']:
        if n in ('b4','w1','bs1','gr1'):out[n]=[w for r in recipes[n] for w in r['words']]
        elif n=='deot':out[n]=[w for section in deot['source_sections'] for w in section['words']]
        else:
            out[n]=[x['unit'] for x in other[n]['PRIMARY']['units']];assert len(out[n])==8000
    assert all(isinstance(w,str) and w for words in out.values() for w in words)
    return out

class Limit(Exception):pass

def solve(groups,words,signs,mode,spec):
    start=time.monotonic();checks=0;nodes=0;W=set(words);alphabet=sorted(set(''.join(words)))
    unique=sorted(set(map(tuple,groups)));tables=[];trace=[]
    def tick():
        nonlocal checks
        checks+=1
        if checks>spec['candidate_checks_cap']:raise Limit('candidate_checks')
        if time.monotonic()-start>spec['seconds_per_case']:raise Limit('wall_seconds')
    try:
        outputs=sorted(W | ({w[::-1] for w in W} if mode=='BIDIR' else set()))
        for g in unique:
            ag=atoms(g);has=bool(ag and ag[-1]==TAIL);body=ag[:-1] if has else ag;rows=set()
            for z in outputs:
                tick()
                if (has and len(z)<=len(body)) or (not has and len(z)!=len(body)):continue
                row={};valid=True
                for u,c in zip(body,z):
                    if u in row and row[u]!=c:valid=False;break
                    row[u]=c
                if valid:
                    if has:row[TAIL]=z[len(body):]
                    rows.add(tuple(sorted(row.items())))
            if not rows:return dict(status='UNSAT',reason='empty_initial_table',checks=checks,nodes=nodes,trace=trace)
            tables.append(sorted(rows));trace.append(dict(units=list(g),candidate_maps=len(rows)))
        domains=[{dict(row)[TAIL] for row in t} for t in tables if TAIL in dict(t[0])]
        common=set.intersection(*domains) if domains else None
        if common is not None:
            if not common:return dict(status='UNSAT',reason='no_shared_tail_string',checks=checks,nodes=nodes,trace=trace)
            tables=[[row for row in t if TAIL not in dict(row) or dict(row)[TAIL] in common] for t in tables]
        def visit(key,left):
            nonlocal nodes
            nodes+=1
            if nodes>spec['nodes_cap']:raise Limit('nodes')
            tick()
            if not left:return key
            chosen=None;domain=None
            for j in left:
                choices=[]
                for row in tables[j]:
                    tick()
                    if all(u not in key or key[u]==c for u,c in row):choices.append(row)
                if not choices:return None
                if domain is None or len(choices)<len(domain):chosen=j;domain=choices
            rest=[j for j in left if j!=chosen]
            for row in domain:
                nextkey=dict(key);nextkey.update(row)
                found=visit(nextkey,rest)
                if found is not None:return found
            return None
        found=visit({},list(range(len(tables))))
        if found is None:return dict(status='UNSAT',reason='exhausted_exact_function_join',checks=checks,nodes=nodes,trace=trace)
        tail=found.pop(TAIL,alphabet[0]);key={u:found.get(u,alphabet[0]) for u in signs};cert=[]
        assert tail
        for g in groups:
            z=expand(g,key,tail)
            if z in W:word=z;direction='FWD'
            else:assert mode=='BIDIR' and z[::-1] in W;word=z[::-1];direction='REV'
            cert.append(dict(units=g,atoms=atoms(g),source_word=word,direction=direction))
        return dict(status='SAT',key=key,tail=tail,certificate=cert,checks=checks,nodes=nodes,trace=trace)
    except Limit as e:return dict(status='UNKNOWN',reason=str(e),checks=checks,nodes=nodes,trace=trace)

def controls():
    spec=dict(nodes_cap=100000,candidate_checks_cap=1000000,seconds_per_case=3);checked=0
    fixtures=[([list('dy')],['xx']),([list('dy'),list('ady')],['xx','yxx']),([list('dy'),list('dydy')],['xx','xyxx']),([list('dy'),list('dydydy')],['yy','xyxyyy']),([list('dy'),list('ady'),list('a')],['x','yx','y']),([list('dy'),list('ady')],['x','yy']),([list('dy'),list('dyady')],['xy','xyxxy']),([list('adyb'),list('dy')],['xyxy','xy'])]
    for groups,W in fixtures:
        letters=sorted(set(''.join(W)));signs=sorted(set(sum(groups,[])));maxlen=max(map(len,W))
        for mode in ['FWD','BIDIR']:
            expected=False
            for letterskey in itertools.product(letters,repeat=len(signs)):
                key=dict(zip(signs,letterskey))
                for n in range(1,maxlen+1):
                    for chars in itertools.product(letters,repeat=n):
                        tail=''.join(chars)
                        if all((z:=expand(g,key,tail)) in W or mode=='BIDIR' and z[::-1] in W for g in groups):expected=True;break
                    if expected:break
                if expected:break
            result=solve(groups,W,signs,mode,spec)
            assert result['status']==('SAT' if expected else 'UNSAT'),(groups,W,mode,result);checked+=1
    assert atoms(list('dydydy'))==['d','y','d','y',TAIL]
    assert expand(list('dydydy'),{'d':'x','y':'y'},'zz')=='xyxyzz'
    assert atoms(list('adyb'))==list('adyb')
    assert solve([list('dy')],['xy'],['d','y'],'FWD',dict(spec,nodes_cap=0))['status']=='UNKNOWN'
    return dict(status='PASS',exhaustive_cartesian_function_and_string_fixtures=checked,terminal_priority_not_freeUD=True,internal_d_y_literals=True,cap_unknown=True)

def generated(spec,W):
    alphabet=sorted(set(''.join(W)))[:20];eligible=sorted({w for w in W if set(w)<=set(alphabet)})
    selected=None
    for tail in sorted(eligible,key=lambda w:(len(w),w)):
        if len(tail)<2:continue
        yes=[w for w in eligible if w!=tail and w.endswith(tail)]
        no=[w for w in eligible if not w.endswith(tail)]
        if len(yes)>=10 and len(no)>=10:selected=(tail,[tail]+yes[:10]+no[:10]);break
    if selected is None:return dict(status='DOMAIN_ABSENT',reason='no_declared_tail_source_domain')
    tail,cycle=selected;words=[cycle[j%len(cycle)] for j in range(77)]
    bodies=[w[:-len(tail)] if w.endswith(tail) else w for w in words];freq=collections.Counter(''.join(bodies));ranked=sorted(alphabet,key=lambda c:(-freq[c],c))
    safe=[c for c in ranked if freq[c]>0 and all(c+c not in body for body in bodies)]
    if len(safe)<2:return dict(status='DOMAIN_ABSENT',reason='no_safe_e_i_body_chars')
    key={'e':safe[0],'i':safe[1]};canonical=[u for u in spec['signs'] if u not in ('d','y')]
    key.update(zip([u for u in canonical if u not in key],[c for c in alphabet if c not in safe[:2]]))
    inverse={c:u for u,c in key.items()};alias=[c for c in ranked if freq[c]>0][:2]
    if len(alias)<2:return dict(status='DOMAIN_ABSENT',reason='insufficient_active_alias_chars')
    if ''.join(alias)==tail:alias.reverse()
    key['d'],key['y']=alias;aliases=dict(zip(alias,['d','y']));base=[];encoded=[]
    for wi,(word,body) in enumerate(zip(words,bodies)):
        has=word.endswith(tail);g=[]
        for ci,c in enumerate(body):
            use=c in aliases and (wi+ci)%2 and (has or ci<len(body)-2)
            g.append(aliases[c] if use else inverse[c])
        if has:g+=['d','y']
        base.append(g);encoded.append([u for ui,u in enumerate(g) for _ in range(1+(wi+ui)%3 if u in ('e','i') else 1)])
    internal=set(u for g in base for u in atoms(g) if u!=TAIL)
    if not {'d','y'}<=internal or base==encoded:return dict(status='DOMAIN_ABSENT',reason='inactive_alias_or_expansion_duty')
    assert [collapse(g) for g in encoded]==base
    assert tail!=key['d']+key['y'] and all(expand(g,key,tail)==w for g,w in zip(base,words))
    return dict(status='GENERATED',source='deot',source_words=words,planted_key=key,planted_tail=tail,words_cycle=cycle,ordinary_alias_chars=alias,encoded_groups=encoded,collapsed_groups=base)

def native(spec):
    worksheet=read(R/spec['worksheet_path']);unit=[u for u in worksheet['units'] if u['unit_id']==spec['passage_unit']];assert len(unit)==1
    rx=re.compile('|'.join(re.escape(u) for u in sorted(spec['signs'],key=lambda u:(-len(u),u))));groups=[];original=[]
    for line in unit[0]['lines']:
        assert line['metadata']['page']=='f75v' and line['metadata']['edition']=='IT2a'
        for g in line['original_groups']:
            parsed=rx.findall(g[2]);assert ''.join(parsed)==g[2];groups.append(collapse(parsed));original.append(g)
    assert len(groups)==77
    return groups,original

def main():
    parser=argparse.ArgumentParser();p=parser.add_mutually_exclusive_group(required=True);p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');args=parser.parse_args()
    lockcheck();spec=read(B/'src/SPEC.json');W=sources(spec)
    if args.gate:
        c=generated(spec,W['deot']);c.setdefault('source','deot');c['source_free_controls']=controls()
        if c['status']=='GENERATED':c['result']=solve(c['collapsed_groups'],W['deot'],spec['signs'],'BIDIR',spec)
        save('CONTROL.json',c);print(json.dumps(dict(control=c['status'],solver=c.get('result',{}).get('status'))));return
    assert read(B/'artifacts/GATE_VALIDATION.json')['status']=='PASS'
    groups,original=native(spec);cases=[]
    for name in spec['source_names']:
        for mode in spec['modes']:
            result=solve(groups,W[name],spec['signs'],mode,spec);cases.append(dict(source=name,mode=mode,result=result));print(json.dumps(dict(source=name,mode=mode,status=result['status'],nodes=result['nodes'],checks=result['checks'])),flush=True)
    save('RESULT.json',dict(experiment_id='GDT1416',status='LOCAL_TERMINAL_DY_KEY_CAPACITY',groups=groups,original_groups=original,cases=cases,claim_ceiling=spec['claim_ceiling'],global1406failures_retained=True))
if __name__=='__main__':main()
