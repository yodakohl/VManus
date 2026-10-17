#!/usr/bin/env python3
"""Exact bounded word-centric DFS for a shared injective key and source bigrams."""
import argparse,concurrent.futures,gzip,hashlib,itertools,json,time,sys
sys.setrecursionlimit(10000)
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):
    data=p.read_bytes();return json.loads(gzip.decompress(data) if p.suffix=='.gz' else data)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):
    p=A/name
    if p.exists():assert read(p)==obj
    else:p.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
def parse(raw,signs):
    paths=[[] for _ in range(len(raw)+1)];paths[0]=[[]]
    for i in range(len(raw)):
        for u in signs:
            if raw.startswith(u,i):paths[i+len(u)]=(paths[i+len(u)]+[p+[u] for p in paths[i]])[:2]
    return paths[-1][0] if len(paths[-1])==1 else None

def load_records(s,gate_only=False):
    deot=read(ROOT/s['deot_path'])
    records={'deot':[x['words'] for x in deot['source_sections']]}
    if gate_only:return records
    recipes=read(ROOT/s['recipe_path']);other=read(ROOT/s['other_path'])
    for name in ['b4','w1','bs1','gr1']:records[name]=[x['words'] for x in recipes[name]]
    for name in ['OLD_ITALIAN_UD_CONTROL','LATIN_PROIEL_CONTROL','ANCIENT_GREEK_PROIEL_CONTROL']:
        units=other[name]['PRIMARY']['units'];assert len(units)==8000
        groups={}
        for row in units:groups.setdefault(row['sentence_index'],[]).append(row['unit'])
        records[name]=list(groups.values())
    assert set(records)==set(s['source_names'])
    return records

def graph(records):
    words=set();edges=set()
    for record in records:
        assert all(isinstance(w,str) and w for w in record)
        words.update(record);edges.update(zip(record,record[1:]))
    successors={w:[] for w in sorted(words)}
    for left,right in sorted(edges):successors[left].append(right)
    return {'words':sorted(words),'successors':successors,'alphabet':sorted(set(''.join(words))),'records':len(records),'tokens':sum(map(len,records)),'edges':len(edges)}

class Limit(Exception):pass

def solve(stream,G,signs,seconds,nodes_cap,checks_cap):
    begin=time.monotonic();deadline=begin+seconds;nodes=0;checks=0
    alphabet=G['alphabet'];N=len(stream);index={u:i for i,u in enumerate(signs)}
    assert all(u in index for u in stream) and N>0
    if len(alphabet)<len(signs):return {'status':'UNSAT','reason':'SOURCE_ALPHABET_TOO_SMALL_FOR_FULL_INJECTION','nodes':0,'checks':0}
    sequence=[index[u] for u in stream];failed=set()
    def visit(pos,previous,key,chosen):
        nonlocal nodes,checks
        if time.monotonic()>=deadline:raise Limit('TIME_CAP')
        if nodes>=nodes_cap:raise Limit('NODE_CAP')
        nodes+=1
        if pos==N:return key,chosen
        state=(pos,previous,key)
        if state in failed:return None
        candidates=G['words'] if previous is None else G['successors'][previous]
        for word in candidates:
            if checks>=checks_cap:raise Limit('CANDIDATE_CHECK_CAP')
            checks+=1
            if time.monotonic()>=deadline:raise Limit('TIME_CAP')
            if pos+len(word)>N:continue
            local=list(key);reverse={c:i for i,c in enumerate(key) if c is not None};valid=True
            for ui,c in zip(sequence[pos:pos+len(word)],word):
                if local[ui] is not None:
                    if local[ui]!=c:valid=False;break
                elif c in reverse:valid=False;break
                else:local[ui]=c;reverse[c]=ui
            if valid:
                answer=visit(pos+len(word),word,tuple(local),chosen+[word])
                if answer is not None:return answer
        failed.add(state);return None
    try:answer=visit(0,None,tuple([None]*len(signs)),[])
    except Limit as error:return {'status':'UNKNOWN','reason':str(error),'nodes':nodes,'checks':checks}
    except RecursionError:return {'status':'UNKNOWN','reason':'PYTHON_RECURSION_CAP','nodes':nodes,'checks':checks}
    if answer is None:return {'status':'UNSAT','reason':'EXHAUSTIVE_SEARCH','nodes':nodes,'checks':checks}
    vals,words=answer;vals=list(vals);available=iter(c for c in alphabet if c not in vals)
    for i,c in enumerate(vals):
        if c is None:vals[i]=next(available)
    key=dict(zip(signs,vals));decoded=''.join(key[u] for u in stream);assert decoded==''.join(words)
    assert len(set(key.values()))==len(signs)
    assert all(b in G['successors'][a] for a,b in zip(words,words[1:]))
    ends=[];cursor=0
    for word in words:cursor+=len(word);ends.append(cursor)
    return {'status':'SAT','key':key,'source_words':words,'breaks':ends,'decoded_stream':decoded,'nodes':nodes,'checks':checks}

def controls():
    fixtures=[(['a','b','a','b'],[['xy','xy']],['a','b']),(['a','b','b','a'],[['xy','xy']],['a','b']),(['a','b'],[['x'],['y']],['a','b']),(['a','a'],[['x','x'],['y']],['a','b']),(['a','b','a'],[['x','yx']],['a','b'])]
    checks=0
    for stream,records,signs in fixtures:
        G=graph(records);W=set(G['words']);edges={(a,b) for a in W for b in G['successors'][a]};possible=False
        for values in itertools.permutations(G['alphabet'],len(signs)):
            key=dict(zip(signs,values));text=''.join(key[u] for u in stream)
            for mask in range(1<<max(0,len(text)-1)):
                cuts=[0]+[i for i in range(1,len(text)) if mask>>(i-1)&1]+[len(text)]
                ws=[text[a:b] for a,b in zip(cuts,cuts[1:])]
                if all(w in W for w in ws) and all(pair in edges for pair in zip(ws,ws[1:])):possible=True
        result=solve(stream,G,signs,5,10000,100000)
        assert result['status']==('SAT' if possible else 'UNSAT');checks+=1
    assert ('x','y') not in {(a,b) for a,bs in graph([['x'],['y']])['successors'].items() for b in bs}
    return {'status':'PASS','exhaustive_key_and_segmentation_cases':checks,'no_cross_record_edge':True}

def setup():
    lock=read(E/'LOCK.json')
    for p,h in lock['files'].items():assert not Path(p).is_absolute() and sha(ROOT/p)==h,p
    for p in [Path(__file__),E/'src/SPEC.json']:assert p.relative_to(ROOT).as_posix() in lock['files']
    return read(E/'src/SPEC.json'),lock

def gate():
    s,lock=setup();toy=controls();records=load_records(s,True)['deot'];G=graph(records)
    if len(G['alphabet'])!=22:
        save('CONTROL.json',{'experiment_id':'GDT1418','source':'deot','status':'NO_CAPACITY','reason':'SOURCE_ALPHABET_NOT_22','source_free_controls':toy});return
    selected=next((i for i,r in enumerate(records) if len(r)>=32),None)
    if selected is None:
        save('CONTROL.json',{'experiment_id':'GDT1418','status':'DOMAIN_ABSENT','reason':'NO_32_WORD_SECTION','source_free_controls':toy});return
    words=records[selected][:32];key={u:G['alphabet'][(7*j+3)%22] for j,u in enumerate(s['signs'])};inverse={c:u for u,c in key.items()}
    stream=[inverse[c] for c in ''.join(words)]
    assert all(b in G['successors'][a] for a,b in zip(words,words[1:]))
    result=solve(stream,G,s['signs'],s['control_seconds'],s['nodes_cap'],s['candidate_checks_cap'])
    save('CONTROL.json',{'experiment_id':'GDT1418','status':'GENERATED','source':'deot','source_section_index':selected,'source_words':words,'planted_key':key,'encoded_stream':stream,'source_free_controls':toy,'result':result,'lock_sha256':sha(E/'LOCK.json')})
    print(json.dumps({'control_status':result['status']}))

def native_input(s):
    worksheet=read(ROOT/s['worksheet_path']);wrapper=worksheet['source_original_wrapper']
    assert wrapper['unit_id']==s['passage_unit']
    unit=wrapper['source_unit'];lines=unit['lines']
    assert [l['metadata']['locus'] for l in lines]==['f75v.'+str(i) for i in range(43,50)]
    originals=[];parsed=[]
    for line in lines:
        meta=line['metadata'];rows=line['groups']
        assert meta['page']=='f75v' and meta['edition']=='IT2a' and len(rows)==int(meta['source_group_count'])
        assert [int(g[1]) for g in rows]==list(range(1,len(rows)+1))
        for group in rows:
            assert len(group)==5
            units=parse(group[2],s['signs']);assert units is not None
            originals.append(group);parsed.append(units)
    assert len(originals)==77
    return {'unit_id':s['passage_unit'],'source_unit':unit,'original_groups':originals,'original_units':parsed,'lines':lines,'stream':[u for group in parsed for u in group]}

def work(job):
    name,direction,stream,G,s=job
    ordered=stream if direction=='FWD' else stream[::-1]
    return {'source':name,'mode':direction,'result':solve(ordered,G,s['signs'],s['seconds_per_case'],s['nodes_cap'],s['candidate_checks_cap'])}

def native():
    s,lock=setup();gr=read(A/'GATE_VALIDATION.json');control=read(A/'CONTROL.json')
    assert gr['status']=='PASS' and control['result']['status']=='SAT'
    packet=native_input(s);save('NATIVE_INPUT.json',packet)
    records=load_records(s);graphs={n:graph(records[n]) for n in s['source_names']}
    jobs=[(n,d,packet['stream'],graphs[n],s) for n in s['source_names'] for d in s['directions']]
    with concurrent.futures.ProcessPoolExecutor(max_workers=min(8,s['workers'])) as pool:cases=list(pool.map(work,jobs))
    save('RESULT.json',{'experiment_id':'GDT1418','status':'FIXED_SOURCE_BIGRAM_KEY_CAPACITY','cases':cases,'native_groups':77,'native_units':len(packet['stream']),'source_graphs':{n:{k:v for k,v in graphs[n].items() if k not in ['words','successors']} for n in s['source_names']},'word_meanings_assigned':0,'claim_ceiling':s['claim_ceiling']})
    print(json.dumps({'cases':[{'source':c['source'],'mode':c['mode'],'status':c['result']['status']} for c in cases]}))

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--gate',action='store_true');g.add_argument('--native',action='store_true');args=p.parse_args()
    if args.gate:gate()
    else:native()
