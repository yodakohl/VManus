"""Independent lexical-trie/injective-key checker; never imports the primary."""
import argparse
import gzip
import hashlib
import itertools
import json
import time
from pathlib import Path
B = Path(__file__).resolve().parents[1]
ROOT = B.parents[2]
A = B/'artifacts'

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (A/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

class Budget(Exception):
    pass

def independent_solve(stream, words, signs, mode, limits):
    """Character-wise trie traversal; terminal nodes offer a separate word break."""
    started = time.monotonic()
    alphabet = sorted(set(''.join(words)))
    if len(alphabet)<len(signs):
        return {'status':'UNSAT','reason':'alphabet_cardinality','nodes':0,'checks':0}
    seq = list(stream) if mode=='FWD' else list(reversed(stream))
    assert mode in ('FWD','REV','REVERSE')
    edges, terminal = [{}], [False]
    for word in sorted(set(words)):
        assert word
        node = 0
        for char in word:
            if char not in edges[node]:
                edges[node][char] = len(edges);edges.append({});terminal.append(False)
            node = edges[node][char]
        terminal[node] = True
    sign_index = {s:i for i,s in enumerate(signs)}
    values, used, failed = [None]*len(signs), set(), set()
    nodes = checks = 0
    def guard(candidate=False):
        nonlocal nodes,checks
        if candidate: checks += 1
        else: nodes += 1
        if nodes>limits['nodes_cap'] or checks>limits['candidate_checks_cap'] or time.monotonic()-started>limits['seconds_per_case']:
            raise Budget()
    def walk(position,node,ends):
        guard()
        if position==len(seq):
            if terminal[node] or not seq:
                return list(values), ends+([position] if seq else [])
            return None
        state=(position,node,tuple(values))
        if state in failed:return None
        if terminal[node]:
            found=walk(position,0,ends+[position])
            if found is not None:return found
        slot=sign_index[seq[position]]
        options = [(values[slot],edges[node][values[slot]])] if values[slot] in edges[node] else []
        if values[slot] is None:
            options=[(c,n) for c,n in sorted(edges[node].items()) if c not in used]
        for char,destination in options:
            guard(True)
            fresh=values[slot] is None
            if fresh:values[slot]=char;used.add(char)
            found=walk(position+1,destination,ends)
            if fresh:values[slot]=None;used.remove(char)
            if found is not None:return found
        failed.add(state)
        return None
    try:
        found=walk(0,0,[])
        if found is None:return {'status':'UNSAT','reason':'exhaustive_character_trie','nodes':nodes,'checks':checks}
        assignments,ends=found
        available=iter(c for c in alphabet if c not in assignments)
        key={s:(assignments[i] if assignments[i] is not None else next(available)) for i,s in enumerate(signs)}
        decoded=''.join(key[u] for u in seq)
        starts=[0]+ends[:-1]
        recovered=[decoded[a:b] for a,b in zip(starts,ends)]
        assert all(w in words for w in recovered) and ''.join(recovered)==decoded
        return {'status':'SAT','key':key,'source_words':recovered,'breaks':ends,'nodes':nodes,'checks':checks}
    except Budget:
        return {'status':'UNKNOWN','reason':'independent_budget','nodes':nodes,'checks':checks}

def oracle(stream,words,signs,mode):
    alphabet=sorted(set(''.join(words)))
    sequence=list(stream) if mode=='FWD' else list(reversed(stream))
    for values in itertools.permutations(alphabet,len(signs)):
        key=dict(zip(signs,values));text=''.join(key[u] for u in sequence)
        reachable={0}
        for j in range(1,len(text)+1):
            if any(text[i:j] in words for i in reachable):reachable.add(j)
        if len(text) in reachable:return True
    return False

def controls():
    universe=['x','y','xx','xy','yx','yy']
    limits={'nodes_cap':100000,'candidate_checks_cap':1000000,'seconds_per_case':5}
    count=0
    for mask in range(1,1<<len(universe)):
        words={w for i,w in enumerate(universe) if mask>>i&1}
        for n in range(5):
            for seq in itertools.product('ab',repeat=n):
                for mode in ['FWD','REVERSE']:
                    expected=oracle(seq,words,list('ab'),mode)
                    actual=independent_solve(seq,words,list('ab'),mode,limits)
                    assert actual['status']==('SAT' if expected else 'UNSAT'),(words,seq,mode,actual)
                    count+=1
    assert independent_solve(list('ab'),{'xy','yx'},list('ab'),'FWD',dict(limits,nodes_cap=0))['status']=='UNKNOWN'
    return {'status':'PASS_EXHAUSTIVE_SMALL_KEY_AND_WORDBREAK_ORACLE','comparisons':count,'budget_stop_checked':True,'primary_imported':False}

def sources(spec):
    recipes=read(ROOT/spec['recipe_path']);deot=read(ROOT/spec['deot_path']);other=read(ROOT/spec['other_path']);out={}
    for name in spec['source_names']:
        if name in ('b4','w1','bs1','gr1'):
            tokens=[w for record in recipes[name] for w in record['words']]
        elif name=='deot':tokens=[w for section in deot['source_sections'] for w in section['words']]
        else:
            tokens=[row['unit'] for row in other[name]['PRIMARY']['units']]
            assert len(tokens)==8000
        assert tokens and all(isinstance(w,str) and w for w in tokens)
        out[name]=tokens
    return out

def lock_and_spec():
    lockpath=B/'LOCK.json';lock=read(lockpath)
    for path,digest in lock['files'].items():assert sha(ROOT/path)==digest,path
    spec=read(B/'src/SPEC.json')
    for p in [B/'src/run.py',B/'src/validate.py',B/'src/SPEC.json',ROOT/spec['recipe_path'],ROOT/spec['deot_path'],ROOT/spec['other_path'],ROOT/spec['worksheet_path']]:
        assert str(p.relative_to(ROOT)) in lock['files']
    return spec,sha(lockpath)

def verify_sat(result,stream,words,signs,mode):
    assert result['status']=='SAT'
    key=result['key'];alphabet=set(''.join(words));W=set(words)
    assert set(key)==set(signs) and len(set(key.values()))==len(signs)
    assert all(isinstance(v,str) and len(v)==1 and v in alphabet for v in key.values())
    seq=list(stream) if mode=='FWD' else list(reversed(stream))
    decoded=''.join(key[u] for u in seq)
    assert result['decoded_unspaced']==decoded
    assert ''.join(result['source_words'])==decoded and all(w in W for w in result['source_words'])
    cursor=0
    assert len(result['segments'])==len(result['source_words'])
    for segment,word in zip(result['segments'],result['source_words']):
        assert segment=={'start':cursor,'end':cursor+len(word),'source_word':word}
        assert decoded[cursor:cursor+len(word)]==word
        cursor+=len(word)
    assert cursor==len(seq)
    active={u:key[u] for u in set(seq)}
    assert result['active_key']==active
    assert result['arbitrary_extension_units']==[u for u in signs if u not in active]
    return {'complete_stream_units':len(seq),'source_words':len(result['source_words']),
            'active_units':len(active),'arbitrary_extension_units':result['arbitrary_extension_units']}

def gate(spec,lock_hash):
    own=controls();words=sources(spec)
    toy=read(A/'TOY_CONTROLS.json');expected_inputs=[]
    for W in [['x','yz'],['xy','xz'],['x','y','z'],['xx','y','z'],['xy','zx','yz']]:
        for n in range(1,5):
            for stream in itertools.product('abc',repeat=n):expected_inputs.append((list(stream),W,list('abc')))
    assert len(toy['cases'])==len(expected_inputs)==600
    for case,expected in zip(toy['cases'],expected_inputs):
        assert (case['stream'],case['words'],case['signs'])==expected
        wanted='SAT' if oracle(*expected,'FWD') else 'UNSAT'
        assert case['expected_oracle_status']==case['result']['status']==wanted
        if wanted=='SAT':verify_sat(case['result'],case['stream'],case['words'],case['signs'],'FWD')
    generated=read(A/'GENERATED_CONTROL.json');W=sorted(set(words['deot']))
    assert generated['source']=='deot' and generated['source_selection']=='sorted distinct W words indices0..31'
    assert generated['source_words']==W[:32]
    alphabet=sorted(set(''.join(W)));assert len(alphabet)==len(spec['signs'])==22
    expected_key={u:alphabet[(7*j+3)%22] for j,u in enumerate(spec['signs'])}
    assert generated['planted_key']==expected_key
    decoded=''.join(expected_key[u] for u in generated['encoded_stream'])
    assert decoded==''.join(W[:32])
    assert generated['result']['status']=='SAT'
    certificate=verify_sat(generated['result'],generated['encoded_stream'],W,spec['signs'],'FWD')
    # This fresh search receives neither the planted key nor source segmentation.
    second=independent_solve(generated['encoded_stream'],W,spec['signs'],'FWD',spec)
    assert second['status']!='UNSAT','independent solver contradicted a verified SAT certificate'
    primary=read(A/'CONTROLS.json')
    assert primary['status']=='PASS' and primary['generated_status']=='SAT' and primary['oracle_cases']==600
    result={'status':'PASS','scope':'Source-free oracle and complete generated-control certificate; not native fit or semantic recovery.',
            'lock_sha256':lock_hash,'validator_sha256':sha(Path(__file__)),
            'independent_small_oracle':own,'primary_toy_cases_verified':600,
            'generated_source_and_encoding_verified':True,'generated_sat_certificate':certificate,
            'independent_generated_search':second,'primary_imported':False,
            'input_hashes':{str((A/n).relative_to(ROOT)):sha(A/n) for n in ['TOY_CONTROLS.json','GENERATED_CONTROL.json','CONTROLS.json']}}
    write('GATE_VALIDATION.json',result)
    return result

def unique_parse(raw,signs):
    # Exhaustive suffix dynamic programming, not primary longest-first tokenization.
    ways=[[] for _ in range(len(raw)+1)];ways[len(raw)]=[[]]
    for i in range(len(raw)-1,-1,-1):
        for sign in signs:
            if raw.startswith(sign,i):
                for tail in ways[i+len(sign)]:
                    ways[i].append([sign]+tail)
                    if len(ways[i])>=2:break
            if len(ways[i])>=2:break
    assert len(ways[0])==1,('not a unique22unit parse',raw)
    return ways[0][0]

def verify_native_input(spec):
    worksheet=read(ROOT/spec['worksheet_path']);source=worksheet['source_original_wrapper']['source_unit']
    packet=read(A/'NATIVE_INPUT.json')
    assert packet['original_source']==source
    assert source['edition']=='IT2a'
    assert [l['metadata']['locus'] for l in source['lines']]==[f'f75v.{i}' for i in range(43,50)]
    assert source['lines'][0]['metadata']['paragraph_start']=='1' and source['lines'][-1]['metadata']['paragraph_end']=='1'
    rows=[];stream=[]
    for line in source['lines']:
        for group in line['groups']:
            units=unique_parse(group[2],spec['signs'])
            rows.append({'original_group':group,'units':units,'start':len(stream),'end':len(stream)+len(units)})
            stream.extend(units)
    assert len(rows)==77 and len({g['original_group'][0] for g in rows})==77
    assert packet['groups']==rows and packet['forward_stream']==stream and packet['group_count']==77
    assert packet['raw_runs_preserved'] is True and packet['native_word_meanings']=='UNASSIGNED'
    return stream

def native(spec,lock_hash):
    gate_receipt=read(A/'GATE_VALIDATION.json');assert gate_receipt['status']=='PASS' and gate_receipt['lock_sha256']==lock_hash
    for path,digest in gate_receipt['input_hashes'].items():assert sha(ROOT/path)==digest
    stream=verify_native_input(spec);W=sources(spec);primary=read(A/'RESULT.json')
    expected=[(name,d) for name in spec['source_names'] for d in spec['directions']]
    assert [(c['source'],c['direction'])for c in primary['cases']]==expected
    checked=[];unconfirmed=0
    for case in primary['cases']:
        name,direction=case['source'],case['direction'];words=set(W[name]);r=case['result']
        assert case['stream_units']==len(stream) and case['source_word_types']==len(words)
        item={'source':name,'direction':direction,'primary_status':r['status']}
        if r['status']=='SAT':
            item.update(status='SAT_CERTIFICATE_VERIFIED',certificate=verify_sat(r,stream,words,spec['signs'],direction))
        elif r['status']=='UNSAT':
            second=independent_solve(stream,words,spec['signs'],direction,spec)
            assert second['status']!='SAT',('primary UNSAT contradicted',name,direction,second)
            item['independent_result']=second
            item['status']='UNSAT_INDEPENDENTLY_REPLICATED' if second['status']=='UNSAT' else 'UNSAT_NOT_INDEPENDENTLY_CONFIRMED'
            unconfirmed+=second['status']!='UNSAT'
        else:
            assert r['status']=='UNKNOWN' and r.get('reason')
            item['status']='PRIMARY_UNKNOWN_NO_EXCLUSION'
        checked.append(item)
        print(json.dumps({k:item[k] for k in ['source','direction','status']}),flush=True)
    result={'status':'PASS_INDEPENDENT_SOURCE_AND_ALL_DEFINITE_DECISIONS' if not unconfirmed else 'SOURCE_AND_SAT_CHECKS_PASS_UNSAT_REPLICATION_INCOMPLETE',
            'lock_sha256':lock_hash,'validator_sha256':sha(Path(__file__)),
            'result_sha256':sha(A/'RESULT.json'),'native_input_sha256':sha(A/'NATIVE_INPUT.json'),
            'source_groups':77,'stream_units':len(stream),'cases':checked,'unconfirmed_unsat_cases':unconfirmed,
            'method':'Independent unique-string segmentation, character-level lexical-trie/injective-key DFS, exhaustive smallkey+wordbreak oracle; no primary imports.',
            'limits':['Fixed source inventories and literal injective-key capacity only; no grammar or translation.',
                      'UNKNOWN is not UNSAT. An independently timed-out UNSAT replication is explicitly unconfirmed.',
                      'All77original groups, repetitions, flags and separators retained; plaintext boundaries alone are latent.',
                      'SAT witnesses receive complete readback verification; arbitrary unused-key extensions are not recovered values.']}
    write('VALIDATION.json',result)
    return result

def main():
    ap=argparse.ArgumentParser();m=ap.add_mutually_exclusive_group(required=True)
    m.add_argument('--controls',action='store_true');m.add_argument('--gate',action='store_true');m.add_argument('--native',action='store_true')
    args=ap.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True));return
    spec,lock_hash=lock_and_spec()
    result=gate(spec,lock_hash) if args.gate else native(spec,lock_hash)
    print(json.dumps({'status':result['status']},sort_keys=True))

if __name__=='__main__':main()
