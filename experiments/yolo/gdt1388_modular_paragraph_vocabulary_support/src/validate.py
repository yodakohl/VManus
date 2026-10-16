#!/usr/bin/env python3
"""Independent finite-automaton encoding and direct witness checks; no runner imports."""
import argparse
import hashlib
import itertools
import json
import time
import signal
import concurrent.futures
import multiprocessing
from pathlib import Path
import z3

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
SIGN=('a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def unique_parse(raw, alphabet=SIGN):
    # Independent complete segmentation DP, retaining up to two distinct parses.
    paths=[[] for _ in range(len(raw)+1)]
    paths[0]=[()]
    for i in range(len(raw)):
        for p in paths[i]:
            for j,sign in enumerate(alphabet):
                if raw.startswith(sign,i):
                    k=i+len(sign)
                    candidate=p+(j,)
                    if candidate not in paths[k] and len(paths[k])<2:
                        paths[k].append(candidate)
    if len(paths[-1])!=1 or not raw:
        return None
    counts=[0]*len(alphabet)
    for j in paths[-1][0]: counts[j]+=1
    return counts


def direct_legal(text, vocabulary):
    return bool(text) and not text.startswith(' ') and not text.endswith(' ') and '  ' not in text and all(w in vocabulary for w in text.split(' '))


def automaton(words, n, deadline):
    nodes=[{}];terminal=set()
    for word in sorted(words):
        if len(word)>n: continue
        state=0
        for char in word:
            if char not in nodes[state]:
                nodes[state][char]=len(nodes);nodes.append({})
            state=nodes[state][char]
        terminal.add(state)
        if time.monotonic()>deadline: raise TimeoutError('independent DFA build ceiling')
    classes={};representatives=[];mapped={}
    for state in range(len(nodes)-1,-1,-1):
        signature=(state in terminal,tuple((ord(c)-96,mapped[t]) for c,t in sorted(nodes[state].items())))
        if signature not in classes:
            classes[signature]=len(representatives);representatives.append(signature)
        mapped[state]=classes[signature]
    root=mapped[0]
    table=z3.K(z3.IntSort(),z3.IntVal(-1))
    accepting=z3.K(z3.IntSort(),z3.BoolVal(False))
    for s,(end,edges) in enumerate(representatives):
        for char,t in edges:
            table=z3.Store(table,s*27+char,t)
        if end:
            table=z3.Store(table,s*27,root)
            accepting=z3.Store(accepting,s,True)
        if time.monotonic()>deadline: raise TimeoutError('independent DFA table ceiling')
    return root,table,accepting,len(representatives)


def solve_vectors(vectors, vocabulary, weights_count, timeout_ms=60000, build_seconds=60, fixed_weights=None):
    start=time.monotonic();deadline=start+build_seconds
    try:
        root,table,accepting,states_n=automaton(vocabulary,len(vectors),deadline)
        solver=z3.Solver();solver.set(timeout=timeout_ms)
        weights=[z3.Int('iw_%d'%i) for i in range(weights_count)]
        chars=[z3.Int('ic_%d'%i) for i in range(len(vectors))]
        states=[z3.Int('is_%d'%i) for i in range(len(vectors)+1)]
        solver.add(states[0]==root)
        for w in weights: solver.add(w>=0,w<27)
        if fixed_weights is not None:
            for w,value in zip(weights,fixed_weights):solver.add(w==value)
        for i,(vector,c) in enumerate(zip(vectors,chars)):
            solver.add(c>=0,c<27)
            if vector is not None:
                solver.add(c==z3.Sum([n*w for n,w in zip(vector,weights) if n])%27)
            solver.add(states[i+1]==z3.Select(table,states[i]*27+c),states[i+1]>=0,states[i+1]<states_n)
            if time.monotonic()>deadline:raise TimeoutError('independent constraint build ceiling')
        solver.add(z3.Select(accepting,states[-1]))
    except TimeoutError as exc:
        return {'status':'UNKNOWN','reason':str(exc)}
    status=solver.check()
    if status==z3.unsat:return {'status':'UNSAT','reason':'Independent integer modulo constraints plus minimized DFA; same Z3 theorem kernel.'}
    if status==z3.unknown:return {'status':'UNKNOWN','reason':solver.reason_unknown()}
    model=solver.model()
    key=[model.eval(w,model_completion=True).as_long() for w in weights]
    values=[model.eval(c,model_completion=True).as_long() for c in chars]
    text=''.join(' ' if c==0 else chr(96+c) for c in values)
    assert direct_legal(text,vocabulary)
    assert all(v is None or sum(a*b for a,b in zip(v,key))%27==c for v,c in zip(vectors,values))
    return {'status':'SAT','weights':key,'plaintext':text,'source_character_values':values}


def brute(vectors, vocabulary, weights_count):
    found=False
    for key in itertools.product(range(27),repeat=weights_count):
        free=[i for i,v in enumerate(vectors) if v is None]
        for free_values in itertools.product(range(27),repeat=len(free)):
            replacements=dict(zip(free,free_values))
            values=[replacements[i] if v is None else sum(a*b for a,b in zip(v,key))%27 for i,v in enumerate(vectors)]
            text=''.join(' ' if c==0 else chr(96+c) for c in values)
            if direct_legal(text,vocabulary):found=True
    return found


def controls():
    cases=[('homophony',[[1,0],[0,1]],{'aa'},2),
           ('encoded_space',[[1,0],[0,1],[1,0]],{'a'},2),
           ('opaque_free',[[1],None,[1]],{'a'},1),
           ('all_positions',[[1],[1]],{'ab'},1),
           ('mod27_not3',[[3]],{'i'},1),
           ('mod27_impossible',[[3]],{'a'},1),
           ('space_not_edge',[[0]],{'a'},1),
           ('no_double_space',[[1],[0],[0],[1]],{'a'},1),
           ('word_concatenation',[[1],[2]],{'a','b'},1),
           ('whole_word',[[1],[2]],{'ab'},1)]
    results=[]
    for name,vocabrows,bank,nw in cases:
        expected=brute(vocabrows,bank,nw)
        result=solve_vectors(vocabrows,bank,nw,timeout_ms=10000)
        assert result['status']!='UNKNOWN',(name,result)
        assert (result['status']=='SAT')==expected,(name,result,expected)
        results.append({'fixture':name,'status':result['status'],'exhaustive_key_space':27**nw})
    assert unique_parse('sh',('s','h','sh')) is None
    assert unique_parse('qokedy') is not None
    assert unique_parse('qok@152;y') is None
    return {'status':'PASS_SOURCE_FREE_ONLY','cases':results,'native_payload_read':False}


def aabba_hits(vocabulary):
    hits=[]
    for word in sorted(vocabulary):
        for i in range(len(word)-4):
            letters=word[i:i+5]
            if letters[0]==letters[1]==letters[4] and letters[2]==letters[3]:
                hits.append({'word':word,'start':i,'substring':letters})
    return hits


def verify_positive(case,vectors,vocabulary):
    key=case['weights'];text=case['plaintext']
    assert len(key)==len(SIGN) and all(type(v) is int and 0<=v<27 for v in key)
    assert len(text)==len(vectors) and direct_legal(text,vocabulary)
    values=[0 if c==' ' else ord(c)-96 for c in text]
    assert all(0<=v<27 for v in values)
    assert values==case['source_character_values']
    assert case['words']==text.split(' ')
    for v,c in zip(vectors,values):
        if v is not None:assert sum(a*b for a,b in zip(v,key))%27==c


def negative_worker(item):
    reader,pack,vectors,vocabulary,execution=item
    def expired(signum,frame):
        raise TimeoutError('independent outer-case ceiling')
    signal.signal(signal.SIGALRM,expired)
    signal.alarm(int(execution['outer_case_seconds']))
    try:
        result=solve_vectors(vectors,vocabulary,len(SIGN),timeout_ms=int(execution['solver_seconds']*1000),build_seconds=execution['model_build_seconds'])
    except TimeoutError as exc:
        result={'status':'UNKNOWN','reason':str(exc)}
    finally:
        signal.alarm(0)
    return reader,pack,result


def native_validate():
    lock_path=E/'src/REGISTRATION_LOCK.json'
    lock=read(lock_path)
    locked={row['path']:row['sha256'] for row in lock['files']}
    assert len(locked)==len(lock['files'])
    for path,h in locked.items():assert sha(ROOT/path)==h,path
    for path in ['src/run.py','src/validate.py','src/SPEC.json','METHOD.md','PREREGISTRATION.md']:
        assert str((E/path).relative_to(ROOT)) in locked
    spec=read(E/'src/SPEC.json')
    assert tuple(spec['signs'])==SIGN
    for p in spec['inputs']:assert sha(ROOT/p['path'])==p['sha256'],p['path']
    source=read(ROOT/spec['source'])
    assert sha(E/'artifacts/SOURCE.json')==sha(ROOT/spec['source'])
    assert read(E/'artifacts/SOURCE.json')==source
    manifest=read(ROOT/spec['pack_manifest'])
    vocabularies={};bank_hashes={};pattern_hits={}
    for pack in spec['languages']:
        path=ROOT/'.gdt001/language_packs'/ (pack+'.txt')
        assert sha(path)==manifest['packs'][pack]['prepared_sha256']
        words=path.read_text().split()
        assert words and all(w and all('a'<=c<='z' for c in w) for w in words)
        bank=set(words);vocabularies[pack]=bank;bank_hashes[pack]=sha(path)
        pattern_hits[pack]=aabba_hits(bank)
    input_manifest=read(E/'artifacts/INPUT_MANIFEST.json')
    assert input_manifest['spec_sha256']==sha(E/'src/SPEC.json')
    assert input_manifest['lock_sha256']==sha(lock_path)
    assert input_manifest['inputs']==spec['inputs'] and input_manifest['signs']==spec['signs']
    assert input_manifest['z3_version']==z3.get_version_string()
    for pack,bank in vocabularies.items():
        assert input_manifest['vocabularies'][pack]=={'size':len(bank),'sha256':hashlib.sha256(('\n'.join(sorted(bank))+'\n').encode()).hexdigest()}
    prefilter=read(E/'artifacts/PREFILTER.json')
    assert prefilter['pattern_spec']==spec['fixed_support_prefilter']
    for pack,bank in vocabularies.items():
        hits=pattern_hits[pack]
        expected={'vocabulary_size':len(bank),'matching_word_count':len({h['word'] for h in hits}),'matching_substring_count':len(hits),'witnesses':[{'word':h['word'],'offset_zero_based':h['start'],'substring':h['substring']} for h in hits]}
        assert prefilter['packs'][pack]==expected
    units={};templates={};boundary_statuses={}
    for unit in source['units']:
        reader=unit['edition'];assert reader not in units
        boundary_statuses[reader]=unit['boundary_status']
        groups=[];target=None
        for line in unit['lines']:
            assert line['metadata']['page']=='f75r'
            line_groups=[dict(zip(unit['group_columns'],r)) for r in line['groups']]
            groups.extend(line_groups)
            if line['metadata']['locus']=='f75r.38':target=line_groups
        vectors=[unique_parse(g['ivtff_group_raw']) for g in groups]
        units[reader]=(groups,vectors)
        # Check only the preselected physical target, not a searched pattern.
        expected=['qokeedy','qokeedy','qokedy','qokedy','qokeedy']
        applicable=(target is not None and [g['ivtff_group_raw'] for g in target[:5]]==expected
                    and all(unique_parse(g['ivtff_group_raw']) is not None for g in target[:5]))
        if reader in spec['fixed_support_prefilter']['readers']:
            assert applicable
            assert [int(g['source_group_index']) for g in target[:5]]==spec['fixed_support_prefilter']['group_indices']
            assert all(a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(target[:4],target[1:5]))
            assert prefilter['readers'][reader]=={'source_ids':[g['source_group_id'] for g in target[:5]],'raw':expected}
        else:
            applicable=False
        templates[reader]=applicable
    assert set(units)=={'IT2a','ZL3b','RF1b'} and len(source['units'])==3
    result=read(E/'artifacts/RESULT.json')
    assert result['status']=='MODULAR_PARAGRAPH_VOCABULARY_SUPPORT'
    cases=result['cases']
    assert len(cases)==18
    assert {(r['reader'],r['pack']) for r in cases}==set(itertools.product(units,spec['languages']))
    assert set(result['decision_counts']) <= {'SAT','UNSAT','UNKNOWN'}
    for status in ['SAT','UNSAT','UNKNOWN']:
        assert result['decision_counts'].get(status,0)==sum(c['status']==status for c in cases)
    checked=[];jobs=[]
    for case in cases:
        reader,pack=case['reader'],case['pack'];groups,vectors=units[reader];bank=vocabularies[pack]
        assert case['source_group_count']==len(groups)
        assert case['source_ids']==[g['source_group_id'] for g in groups]
        assert case['boundary_status']==boundary_statuses[reader]
        eligible=sorted(w for w in bank if len(w)<=len(groups))
        assert case['eligible_vocabulary_sha256']==hashlib.sha256(('\n'.join(eligible)+'\n').encode()).hexdigest()
        assert case['parsed_groups']==sum(v is not None for v in vectors)
        assert case['free_groups']==sum(v is None for v in vectors)
        assert case['vocabulary_size']==len(bank)
        assert case['eligible_vocabulary_size']==sum(len(w)<=len(groups) for w in bank)
        status=case['status'];assert status in ['SAT','UNSAT','UNKNOWN']
        assert case['prefilter_applied']==templates[reader]
        assert case['prefilter_matching_substrings']==(len(pattern_hits[pack]) if templates[reader] else None)
        should_exclude=templates[reader] and not pattern_hits[pack]
        assert case['mechanism']==('PREFILTER' if should_exclude else 'SOLVER')
        if should_exclude:
            assert status=='UNSAT' and case['reason']=='NECESSARY_AABBA_WORD_SUBSTRING_ABSENT'
        if status!='SAT':
            assert all(case[key] is None for key in ['weights','plaintext','words','source_character_values'])
        receipt={'reader':reader,'pack':pack,'primary_status':status}
        if status=='SAT':
            verify_positive(case,vectors,bank)
            receipt['validation']='DIRECT_FULL_WITNESS_PASS'
        elif status=='UNSAT' and templates[reader] and not pattern_hits[pack]:
            receipt['validation']='EXHAUSTIVE_FIXED_AABBA_INVENTORY_CERTIFICATE_PASS'
        elif status=='UNSAT':
            receipt['validation']='PENDING_INDEPENDENT_DFA'
            jobs.append((reader,pack,vectors,bank,spec['execution']))
        else:
            assert case['weights'] is None and case['plaintext'] is None
            receipt['validation']='UNKNOWN_RETAINED_NO_EXCLUSION'
        checked.append(receipt)
    if jobs:
        ctx=multiprocessing.get_context('spawn')
        with concurrent.futures.ProcessPoolExecutor(max_workers=spec['execution']['max_workers'],mp_context=ctx) as pool:
            futures=[pool.submit(negative_worker,j) for j in jobs]
            for f in concurrent.futures.as_completed(futures):
                reader,pack,replay=f.result()
                receipt=next(r for r in checked if (r['reader'],r['pack'])==(reader,pack))
                receipt['independent_replay']=replay
                if replay['status']=='UNSAT':receipt['validation']='INDEPENDENT_ENCODING_SAME_Z3_UNSAT'
                elif replay['status']=='UNKNOWN':receipt['validation']='UNVERIFIED_NEGATIVE_MUST_REMAIN_UNKNOWN'
                else:receipt['validation']='FAIL_PRIMARY_NEGATIVE_CONTRADICTED'
    valid=all(not r['validation'].startswith(('FAIL','UNVERIFIED')) for r in checked)
    report={'experiment_id':'GDT1388','status':'PASS' if valid else 'VALIDATION_GAP',
            'spec_sha256':sha(E/'src/SPEC.json'),'lock_sha256':sha(lock_path),'result_sha256':sha(E/'artifacts/RESULT.json'),
            'source_sha256':sha(ROOT/spec['source']),'bank_sha256':bank_hashes,'cases':checked,
            'aabba_applicable':templates,'aabba_full_inventory_hits':pattern_hits,
            'independent_negative_encoding':'Integer modulo27 source characters and minimized-trie finite automaton via constant transition arrays. Same Z3 backend; not an independent proof kernel.',
            'meaning_confirmation':False}
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'cases':checked},sort_keys=True))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--controls','--controls-only',action='store_true');args=parser.parse_args()
    if args.controls:
        assert aabba_hits({'aabba','aaaaa','abbba','ababa'})==[{'word':'aaaaa','start':0,'substring':'aaaaa'},{'word':'aabba','start':0,'substring':'aabba'}]
        print(json.dumps(controls(),sort_keys=True));return
    native_validate()


if __name__=='__main__':main()
