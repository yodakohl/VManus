#!/usr/bin/env python3
"""Independent run-inverse prefix-closure and frozen-codebook checker."""
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re
import time

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):
    raw=path.read_bytes();return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def parse(raw,signs):
    ways=[[] for _ in range(len(raw)+1)];ways[0]=[()]
    for i in range(len(raw)):
        for sign in signs:
            if ways[i] and raw.startswith(sign,i):
                j=i+len(sign);ways[j]=(ways[j]+[p+(sign,) for p in ways[i]])[:2]
    assert len(ways[-1])==1 and ways[-1][0]
    return ways[-1][0]


def collapse(word):return tuple(unit for i,unit in enumerate(word) if i==0 or unit not in ('e','i') or word[i-1]!=unit)


def closure(words):
    deadline=time.monotonic()+30
    known=set(words)
    while True:
        extra=set()
        for word in known:
            if time.monotonic()>deadline:raise TimeoutError('Independent30secondclosurebudget reached')
            for i in range(1,len(word)):
                if word[:i] in known:extra.add(word[i:])
        extra-=known
        if not extra:return known
        known.update(extra)


def head_bounds(closed,used):
    heads={word[0] for word in closed};forced={word[0] for word in closed if len(word)==1}
    two={word for word in closed if len(word)==2}
    followers={head:{word[1] for word in closed if len(word)>=2 and word[0]==head} for head in used}
    rows={}
    for head in sorted(used):
        required={head}
        while True:
            added={a for a,b in two if b in required}-required
            if not added:break
            required.update(added)
        conflict=required&forced
        bound=None if conflict else len(heads|{head})+sum(max(1,len(followers.get(unit,set())))-1 for unit in required)
        rows[head]={'required':sorted(required),'conflict':sorted(conflict),'bound':bound}
    basis={word for word in closed if not any(word[:i] in closed for i in range(1,len(word)))}
    return heads,forced,two,followers,rows,basis


def code_parse(word,codes):
    paths=[[] for _ in range(len(word)+1)];paths[0]=[()]
    for i in range(len(word)):
        for code in codes:
            end=i+len(code)
            if paths[i] and word[i:end]==code:
                paths[end]=(paths[end]+[path+(code,) for path in paths[i]])[:2]
    assert len(paths[-1])<=1,'Code is not uniquely decodable on supplied word'
    return paths[-1][0] if paths[-1] else None


def prefix_free(codes):return all(not (len(a)<len(b) and b[:len(a)]==a) for a in codes for b in codes)


def controls():
    fixtures=[([tuple('a'),tuple('bc')],[tuple(x) for x in ('abc','bca','aa')]),
              ([tuple('ab'),tuple('ac'),tuple('d')],[tuple(x) for x in ('abd','acd','dab','dac','dd')]),
              ([tuple('ab')],[tuple('ab')]),
              ([tuple('a'),tuple('bb')],[tuple('abb')]),
              ([tuple(c) for c in ('ab','ac','bd','be','f')],[tuple(c) for c in ('ab','ac','bd','be','f')])]
    checks=0
    for codes,words in fixtures:
        assert prefix_free(codes)
        closed=closure(words);H,F,T,B,rows,basis=head_bounds(closed,{u for word in words for u in word})
        assert prefix_free(basis)
        for word in closed:
            assert code_parse(word,codes) is not None and code_parse(word,basis) is not None;checks+=1
        for head in {code[0] for code in codes if len(code)>1}:
            assert rows[head]['bound'] is not None and rows[head]['bound']<=len(codes)
    H,F,T,B,heads,P=head_bounds(closure([tuple('abb')]),set('ab'))
    assert 'b' not in H and heads['b']['bound']==2
    H,F,T,B,heads,P=head_bounds(closure([tuple(c) for c in ('ab','ac','bd','be','f')]),set('abcdef'))
    assert heads['b']['bound']==5 and len(H|{'b'})+max(1,len(B['b']))-1==4
    initial=[tuple('a'),tuple('bb'),tuple('abbb')]
    nodes=[{'word':list(w),'parents':None} for w in initial]+[{'word':list('bbb'),'parents':[0,2]},{'word':['b'],'parents':[1,3]}]
    cert={'status':'COMPLETE','nodes':nodes,'rounds':3,'summary':summary(initial,closure(initial))}
    assert verify_certificate(cert,initial)==cert['summary']
    assert ('a',) not in closure([tuple('ab')]) # no1398two-letter sourceword obligation here
    assert collapse(tuple('aiin'))==collapse(tuple('ain'))
    assert collapse(tuple('aaeeiibb'))==tuple('aaeibb')
    assert collapse(('ch','ch','e','e'))==('ch','ch','e')
    # The whole encoded source word, not just each codeword, must be run-free.
    codes=[tuple('ae'),tuple('e')];assert prefix_free(codes)
    assert collapse(codes[0]+codes[1])==codes[0]
    assert codes[0]+codes[1]!=collapse(codes[0]+codes[1])
    for word in [tuple('eai'),('ch','e','a','i','n')]:
        runs=[i for i,u in enumerate(word) if u in ('e','i')]
        for lengths in itertools.product((1,2,3),repeat=len(runs)):
            count=dict(zip(runs,lengths));encoded=tuple(u for i,u in enumerate(word) for _ in range(count.get(i,1)))
            assert collapse(encoded)==word;checks+=1
    # Left cancellation needs prefix freedom; right cancellation is not assumed.
    assert code_parse(tuple('b'),[tuple('a'),tuple('ab')]) is None
    assert parse('qocheey',['q','o','ch','e','y'])==('q','o','ch','e','e','y')
    return {'status':'PASS_SOURCE_FREE_CONTROLS','checks':checks,'wholeword_cross_code_run_condition':True,
            'collapsed_aiin_ain_coincidence':True,'no_length2_singleton_seed':True,'native_access':False}


def summary(words,closed):
    used={unit for word in words for unit in word}
    H,F,T,B,head_data,basis=head_bounds(closed,used)
    heads={unit:{'predecessors':data['required'],'forced_conflict':data['conflict'],
                 'direct_bound':None if data['conflict'] else len(H|{unit})+max(1,len(B[unit]))-1,
                 'bound':data['bound']} for unit,data in head_data.items()}
    available=[data['bound'] for data in heads.values() if data['bound'] is not None]
    lower=min(available) if available else None
    assert prefix_free(basis)
    assert all(code_parse(word,basis) is not None for word in closed)
    return {'used_signs':sorted(used),'H':sorted(H),'F':sorted(F),'T':[list(pair) for pair in sorted(T)],
            'second_signs':{unit:sorted(B[unit]) for unit in used},'heads':heads,
            'necessary_nontrivial_bound':lower,
            'prefix_basis':[list(word) for word in sorted(basis,key=lambda w:(len(w),w))],
            'prefix_basis_size':len(basis),'status':'ALL_USED_CODES_SINGLETON' if not available else 'NECESSARY_BOUND_ONLY',
            'caps':{str(cap):'EXCLUDED_NONTRIVIAL' if lower is None or lower>cap else 'NOT_EXCLUDED' for cap in (22,26,28)}}


def verify_certificate(certificate,words):
    seeds=sorted(set(words),key=lambda w:(len(w),w));nodes=certificate['nodes']
    assert nodes[:len(seeds)]==[{'word':list(word),'parents':None} for word in seeds]
    seen=set()
    for index,node in enumerate(nodes):
        word=tuple(node['word']);assert word and word not in seen
        if index>=len(seeds):
            parents=node['parents'];assert len(parents)==2
            a,b=parents;assert 0<=a<index and 0<=b<index
            prefix,whole=tuple(nodes[a]['word']),tuple(nodes[b]['word'])
            assert len(prefix)<len(whole) and whole[:len(prefix)]==prefix and whole[len(prefix):]==word
        seen.add(word)
    assert type(certificate['rounds']) is int and certificate['rounds']>=1
    if certificate['status']=='UNKNOWN_TIMEOUT':return None
    assert certificate['status']=='COMPLETE'
    computed=closure(seeds);assert computed==seen
    computed_summary=summary(seeds,computed)
    assert certificate['summary']==computed_summary
    # Recover execution-round boundaries from ordered derivations, not by running engine.
    before=len(seeds);rounds_with_additions=0;last=None
    for index,node in enumerate(nodes[len(seeds):],len(seeds)):
        prefix_index,whole_index=node['parents'];scan=(whole_index,len(nodes[prefix_index]['word']))
        if last is None:
            rounds_with_additions=1
        elif whole_index>=before or scan<=last:
            rounds_with_additions+=1;before=index
        assert whole_index<before
        last=scan
    assert certificate['rounds']==rounds_with_additions+1
    return computed_summary


def projection(spec):
    cache=read(ROOT/spec['native_path']);panels={};families={}
    for reader in spec['readers']:
        rows=cache[reader];byform=defaultdict(list)
        assert len({row['id'] for row in rows})==len(rows)
        for row in rows:
            assert row['edition']==reader and row['kind']=='P'
            assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            assert not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v')
            assert list(parse(row['ivtff_group_raw'],spec['signs']))==row['units']
            byform[row['ivtff_group_raw']].append(row)
        records=[]
        for form,occurrences in sorted(byform.items()):
            units=parse(form,spec['signs']);short=collapse(units)
            records.append({'form':form,'units':list(units),'collapsed_units':list(short),
                            'count':len(occurrences),'leaves':sorted({re.match(r'f\d+',row['page']).group() for row in occurrences}),
                            'ids':sorted(row['id'] for row in occurrences)})
        families[reader]=records
        leaf2forms={row['form'] for row in records if len(row['leaves'])>=2}
        for panel in spec['panels']:
            selected=rows if panel=='FULL' else [row for row in rows if row['ivtff_group_raw'] in leaf2forms]
            panels[(reader,panel)]=[(row,collapse(tuple(row['units']))) for row in selected]
    return panels,families


def upper_table(selected,head,tails,signs):
    codes={(unit,) for unit in signs if unit!=head}|{(head,tail) for tail in tails}
    assert len(codes)==27 and prefix_free(codes)
    used=Counter();failed=[];active=0
    for row,word in selected:
        decoded=code_parse(word,codes)
        if decoded is None:
            failed.append(row['id']);continue
        assert sum(decoded,())==word
        used.update(decoded);active+=any(len(code)>1 for code in decoded)
    if not failed:
        reduced=set(used)
        assert prefix_free(reduced)
        assert all(code_parse(word,reduced) is not None for row,word in selected)
    return {'offered_set':codes,'used_counter':used,'failed_ids':failed,'active_groups':active}


def pattern_key(word):
    first=[next(j for j in range(i+1) if word[j]==word[i]) for i in range(len(word))]
    representatives=sorted(set(first))
    return '.'.join(str(representatives.index(j)) for j in first)


def check_bridge(case,selected,computed_summary,spec,envelopes):
    forced=set(computed_summary['F']) if computed_summary is not None else set()
    counterforms=[]
    for form,declared in spec['retained_counterforms'].items():
        units=parse(form,spec['signs']);word=collapse(units)
        assert list(units)==declared and word==units
        present=[row for row,short in selected if row['ivtff_group_raw']==form]
        key=pattern_key(word)
        counterforms.append({'form':form,'present':bool(present),'count':len(present),
                             'leaves':sorted({re.match(r'f\d+',row['page']).group() for row in present}),
                             'collapsed_units':list(word),'forced':set(word)<=forced,
                             'not_forced':sorted(set(word)-forced),'pattern_key':key,
                             'source_missing':{name:key not in envelopes['sources'][name]['modes']['BIDIR'] for name in spec['source_names']}})
    assert case['retained_counterforms']==counterforms
    excluded={}
    for name in spec['source_names']:
        witnesses=[c['form'] for c in counterforms if c['present'] and c['forced'] and c['source_missing'][name]]
        excluded[name]={'status':'UNKNOWN_INCOMPLETE' if computed_summary is None else 'EXCLUDED_BY_FORCED_SINGLETON_COUNTERFORM' if witnesses else 'NO_RETAINED_COUNTERFORM_EXCLUSION',
                        'witnesses':witnesses}
    assert case['source_exclusions']==excluded
    return excluded


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath)
    pins=lock['files'] if isinstance(lock['files'],dict) else {p['path']:p['sha256'] for p in lock['files']}
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'METHOD.md',E/'PREREGISTRATION.md'):
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    for entry in spec['inputs']:assert pins[entry['path']]==entry['sha256']==sha(ROOT/entry['path'])
    assert spec['experiment_id']=='GDT1405' and spec['readers']==['IT2a','RF1b','ZL3b']
    assert spec['panels']==['FULL','LEAF2'] and spec['caps']==[22,26,28,32]
    assert spec['closure_seconds_per_case']==30
    assert spec['fixed_tables']=={'cfh':['a','d','e','o','s','y'],'cph':['a','d','e','k','o','y']}
    assert spec['retained_counterforms']=={'cholols':['ch','o','l','o','l','s'],'dydydy':['d','y','d','y','d','y']}
    panels,families=projection(spec)
    family_path=A/'FAMILIES.json.gz'
    if family_path.exists():assert read(family_path)=={'readers':families}
    envelopes=read(ROOT/spec['source_envelope_path'])
    assert set(envelopes['sources'])==set(spec['source_names']) and len(spec['source_names'])==8
    result=read(A/'RESULT.json');cases=result['cases']
    assert [(c['reader'],c['panel']) for c in cases]==[(r,p) for r in spec['readers'] for p in spec['panels']]
    records=[];certificate_hashes={}
    for case in cases:
        reader,panel=case['reader'],case['panel'];selected=panels[(reader,panel)]
        words=[word for row,word in selected]
        assert case['groups']==len(selected)
        assert case['raw_types']==len({row['ivtff_group_raw'] for row,word in selected})
        assert case['collapsed_types']==len(set(words))
        assert case['changed_groups']==sum(tuple(row['units'])!=word for row,word in selected)
        expected_filename='CERT_'+reader+'_'+panel+'.json.gz'
        assert case['certificate']==expected_filename
        path=A/expected_filename;certificate=read(path);certificate_hashes[expected_filename]=sha(path)
        assert case['closure_status']==certificate['status']
        computed=verify_certificate(certificate,words)
        assert case['summary']==computed
        lower=computed['necessary_nontrivial_bound'] if computed is not None else None
        caps={str(cap):'UNKNOWN_INCOMPLETE' if computed is None else 'EXCLUDED_NONTRIVIAL' if lower is None or lower>cap else 'NOT_EXCLUDED' for cap in spec['caps']}
        assert case['caps']==caps
        upper_bounds=[]
        assert [table['head'] for table in case['upper_tables']]==list(spec['fixed_tables'])
        for table in case['upper_tables']:
            head=table['head'];upper=upper_table(selected,head,spec['fixed_tables'][head],spec['signs'])
            codes=upper['offered_set'];usage=upper['used_counter'];failed=sorted(upper['failed_ids'])
            assert table['offered_codes']==[list(c) for c in sorted(codes)]
            assert table['used_codes']==[list(c) for c in sorted(usage)]
            assert table['used_entries']==len(usage)
            assert table['code_usage']==[{'code':list(c),'occurrences':usage[c]} for c in sorted(usage)]
            assert table['failed_ids']==failed and table['failed_groups']==len(failed)
            assert table['active_groups']==upper['active_groups']
            assert table['covers_all']==(not failed)
            if not failed and upper['active_groups']>0:
                upper_bounds.append(len(usage))
                if lower is not None:assert len(usage)>=lower
        bridge=check_bridge(case,selected,computed,spec,envelopes)
        records.append({'reader':reader,'panel':panel,'closure_status':certificate['status'],
                        'closure_nodes':len(certificate['nodes']),'all_proof_nodes_and_fixedpoint_verified':computed is not None,
                        'necessary_nontrivial_bound':lower,'constructed_nontrivial_upper_bounds':upper_bounds,
                        'exact_conditional_minimum':lower if lower is not None and lower in upper_bounds else None,
                        'caps':caps,'source_exclusions':bridge})
    complete=all(record['closure_status']=='COMPLETE' for record in records)
    assert result['experiment_id']=='GDT1405'
    assert result['status']==('COMPLETE_PREFIX_CAPACITY' if complete else 'UNKNOWN_INCOMPLETE')
    assert result['claim_ceiling']==spec['claim_ceiling']
    receipt={'experiment_id':'GDT1405','status':'PASS_INDEPENDENT_VALIDATION' if complete else 'PARTIAL_VALIDATION_ORIGINAL_UNKNOWN_RETAINED',
             'scientific_status':result['status'],'cases':records,'source_free_controls':controls(),
             'implementation':'Independent repeated proper-prefix scans, predecessor sets and branch bounds; exact parent-chain verification; dynamic codeword parsing of only the two inherited tables. Neither primary nor legacy engine imported.',
             'source_bridge_scope':'Only the two predeclared old counterforms and pinned audited1403BIDIR envelope membership. This does not repeat the original source-wordbook audit.',
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),'result_sha256':sha(A/'RESULT.json'),
                     'certificates':certificate_hashes,'source_envelope_sha256':sha(ROOT/spec['source_envelope_path'])},
             'limits':['Necessary capacity after hypothetical run inversion, not identified source letters, linguistic units or sounds.',
                       'An underlying coded sourceword must be run-free across code boundaries for the full writer inverse; capacity bounds do not supply a real source language.',
                       'Raw LEAF2 eligibility precedes collapse; duplicate formal constraints merge only afterward.',
                       'Inherited fixed-table coverage is an upper bound only when complete and compound-active; no table optimization performed.',
                       'All older failures and the unselected status of e/i allography remain unchanged.']}
    if family_path.exists():receipt['pins']['families_sha256']=sha(family_path)
    assert not (A/'VALIDATION.json').exists();save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'cases':[{k:r[k] for k in ('reader','panel','necessary_nontrivial_bound','constructed_nontrivial_upper_bounds','exact_conditional_minimum')} for r in records]},sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
