#!/usr/bin/env python3
"""Local many-to-one word-list key candidates, not translated meanings."""
import argparse
import collections
import gzip
import hashlib
import itertools
import json
import re
import time
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(path):
    p=Path(path);raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def save(name,value):(B/'artifacts'/name).write_text(json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n')
def collapse(g):return [u for i,u in enumerate(g) if not(i and u in ('e','i') and u==g[i-1])]
def verifylock():
    for name,digest in read(B/'LOCK.json')['files'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name

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
    started=time.monotonic();checks=0;nodes=0
    W=set(words);alphabet=sorted(set(''.join(words)));unique=sorted(set(map(tuple,groups)))
    assert alphabet and mode in ('FWD','BIDIR')
    def tick(amount=1):
        nonlocal checks
        checks+=amount
        if checks>spec['candidate_checks_cap']:raise Limit('candidate_checks')
        if time.monotonic()-started>spec['seconds_per_case']:raise Limit('wall_seconds')
    try:
        bylength=collections.defaultdict(set)
        for w in sorted(W):
            bylength[len(w)].add(w)
            if mode=='BIDIR':bylength[len(w)].add(w[::-1])
        tables=[]
        for g in unique:
            options=set()
            for output in sorted(bylength[len(g)]):
                tick();mapping={};ok=True
                for unit,c in zip(g,output):
                    if unit in mapping and mapping[unit]!=c:ok=False;break
                    mapping[unit]=c
                if ok:options.add(tuple(sorted(mapping.items())))
            if not options:return dict(status='UNSAT',reason='empty_initial_word_table',checks=checks,nodes=nodes)
            tables.append(tuple(sorted(options)))
        # Exact finite word-table joins, with function equality but no injection.
        def visit(key,left):
            nonlocal nodes
            nodes+=1
            if nodes>spec['nodes_cap']:raise Limit('nodes')
            tick(0)
            if not left:return key
            best=None;domain=None
            for index in left:
                choices=[]
                for row in tables[index]:
                    tick()
                    if all(u not in key or key[u]==c for u,c in row):choices.append(row)
                if not choices:return None
                if domain is None or len(choices)<len(domain):best=index;domain=choices
            remaining=[index for index in left if index!=best]
            for row in domain:
                nextkey=dict(key);nextkey.update(row)
                result=visit(nextkey,remaining)
                if result is not None:return result
            return None
        key=visit({},list(range(len(tables))))
        if key is None:return dict(status='UNSAT',reason='exhausted_exact_search',checks=checks,nodes=nodes)
        for unit in signs:key.setdefault(unit,alphabet[0])
        cert=[]
        for group in groups:
            output=''.join(key[u] for u in group)
            if output in W:source=output;direction='FWD'
            else:
                assert mode=='BIDIR' and output[::-1] in W
                source=output[::-1];direction='REV'
            cert.append(dict(units=group,source_word=source,direction=direction))
        return dict(status='SAT',key=key,certificate=cert,checks=checks,nodes=nodes)
    except Limit as e:return dict(status='UNKNOWN',reason=str(e),checks=checks,nodes=nodes)

def controls():
    spec=dict(nodes_cap=100000,candidate_checks_cap=1000000,seconds_per_case=3)
    source=['x','y','xy'];native=[['a'],['b'],['a','b'],['a','a']];n=0
    for wmask in range(1,8):
        W=[w for i,w in enumerate(source) if wmask>>i&1]
        chars=sorted(set(''.join(W)))
        for gmask in range(1,16):
            groups=[g for i,g in enumerate(native) if gmask>>i&1]
            for mode in ('FWD','BIDIR'):
                expected=False
                for values in itertools.product(chars,repeat=3):
                    key=dict(zip(['a','b','c'],values))
                    if all((z:=''.join(key[u] for u in g)) in W or mode=='BIDIR' and z[::-1] in W for g in groups):expected=True;break
                result=solve(groups,W,['a','b','c'],mode,spec)
                assert result['status']==('SAT' if expected else 'UNSAT'),(W,groups,mode,result)
                n+=1
    forced=solve([['a','b']],['xx'],['a','b','c'],'FWD',spec)
    assert forced['status']=='SAT' and forced['key']['a']==forced['key']['b']=='x'
    limited=solve([['a','b']],['xy'],['a','b'],'FWD',dict(spec,nodes_cap=0))
    assert limited['status']=='UNKNOWN'
    assert collapse(['e','e','a','a','i','i'])==['e','a','a','i']
    return dict(status='PASS',cases=n,forced_collision_positive=True,cap_unknown=True)

def generated(spec,allwords):
    words=allwords['deot'];chars=sorted(set(''.join(words)))[:20]
    selected=[(i,w) for i,w in enumerate(words) if set(w)<=set(chars)][:77]
    absent=lambda why:dict(status='DOMAIN_ABSENT',reason=why)
    if len(selected)!=77:return absent('fewer_than77eligible_tokens')
    indices=[i for i,w in selected];window=[w for i,w in selected]
    freq=collections.Counter(''.join(window));ranked=sorted(chars,key=lambda c:(-freq[c],c))
    eligible=[c for c in ranked if freq[c]>0 and all(c+c not in w for w in window)]
    if len(eligible)<2:return absent('no_two_repetition_safe_active_e_i_characters')
    safe=eligible[:2];key=dict(zip(['e','i'],safe))
    canonical=[u for u in spec['signs'] if u not in ('cph','cfh')]
    restunits=[u for u in canonical if u not in ('e','i')]
    key.update(zip(restunits,[c for c in chars if c not in safe]))
    inverse={c:u for u,c in key.items()};aliaschars=[c for c in ranked if c not in safe and freq[c]>0][:2]
    if len(aliaschars)!=2:return absent('too_few_other_active_alias_characters')
    pairs=[]
    for unit,c in zip(['cph','cfh'],aliaschars):
        key[unit]=c;pairs.append(dict(character=c,canonical=inverse[c],alias=unit))
    aliases={x['character']:x['alias'] for x in pairs};base=[];encoded=[]
    for wi,w in enumerate(window):
        group=[aliases[c] if c in aliases and (wi+ci)%2 else inverse[c] for ci,c in enumerate(w)]
        base.append(group)
        encoded.append([u for ui,u in enumerate(group) for _ in range(1+(wi+ui)%3 if u in ('e','i') else 1)])
    seen=set(sum(base,[]))
    if not {'e','i'}<=seen or any(not {p['canonical'],p['alias']}<=seen for p in pairs):return absent('required_alias_or_run_units_unused')
    if base==encoded:return absent('no_actual_run_expansion')
    assert [collapse(g) for g in encoded]==base
    assert len(key)==22 and len(set(key.values()))==20
    return dict(status='GENERATED',source='deot',source_words=window,planted_key=key,encoded_groups=encoded,collapsed_groups=base,alias_pairs=pairs,selection_indices=indices)

def native(spec):
    ws=read(R/spec['worksheet_path']);units=[u for u in ws['units'] if u['unit_id']==spec['passage_unit']];assert len(units)==1
    rx=re.compile('|'.join(re.escape(u) for u in sorted(spec['signs'],key=lambda u:(-len(u),u))))
    groups=[];original=[]
    for line in units[0]['lines']:
        assert line['metadata']['page']=='f75v' and line['metadata']['edition']=='IT2a'
        for g in line['original_groups']:
            parsed=rx.findall(g[2]);assert ''.join(parsed)==g[2]
            groups.append(collapse(parsed));original.append(g)
    assert len(groups)==77
    return groups,original

def main():
    p=argparse.ArgumentParser();p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');args=p.parse_args()
    verifylock();spec=read(B/'src/SPEC.json');W=sources(spec)
    if args.gate:
        control=generated(spec,W);control['source_free_controls']=controls()
        if control['status']=='GENERATED':control['result']=solve(control['collapsed_groups'],W['deot'],spec['signs'],'BIDIR',spec)
        save('CONTROL.json',control);print(json.dumps(dict(control=control['status'],solver=control.get('result',{}).get('status'))));return
    assert args.native
    assert read(B/'artifacts/GATE_VALIDATION.json')['status']=='PASS'
    assert read(B/'artifacts/CONTROL.json')['result']['status']=='SAT'
    groups,original=native(spec);cases=[]
    for name in spec['source_names']:
        for mode in spec['modes']:
            result=solve(groups,W[name],spec['signs'],mode,spec)
            cases.append(dict(source=name,mode=mode,result=result))
            print(json.dumps(dict(source=name,mode=mode,status=result['status'],nodes=result['nodes'],checks=result['checks'])),flush=True)
    save('RESULT.json',dict(experiment_id='GDT1414',status='LOCAL_HOMOPHONIC_KEY_CAPACITY',groups=groups,original_groups=original,cases=cases,claim_ceiling=spec['claim_ceiling'],global1406failures_retained=True))
if __name__=='__main__':main()
