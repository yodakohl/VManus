#!/usr/bin/env python3
"""Post-result public wordset replay; never opens the six external raw caches."""
import sys
sys.dont_write_bytecode=True
import collections
import csv
import importlib.util
import json
import re
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]; A=E/'artifacts'
module_spec=importlib.util.spec_from_file_location('frozen_validator',E/'src/validate.py')
v=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(v)
read,sha=v.read,v.sha

def main():
    s=read(E/'src/SPEC.json');lock=read(E/'LOCK.json')
    manifest=read(ROOT/s['vocabulary_pins_path'])
    oldpins={x['path']:x['sha256'] for x in manifest['inputs']}
    external={s['source_directory']+'/'+p+'.txt' for p in s['source_packs']}
    assert len(external)==6 and external<=set(lock['files'])
    for path,h in lock['files'].items():
        assert not Path(path).is_absolute()
        if path in external: assert h==oldpins[path]
        else: assert sha(ROOT/path)==h,path
    guard=read(ROOT/s['native_guard_path']);oldspec=read(ROOT/s['native_spec_path'])
    cache=ROOT/s['native_cache_path'];assert sha(cache)==guard['sha256']
    assert len(oldspec['allowed'])==179
    lines=collections.defaultdict(list)
    with cache.open(encoding='utf-8',newline='') as stream:
        for row in csv.DictReader(stream,delimiter='\t'):
            assert row['page'] in oldspec['allowed'] and not row['page'].startswith('f84')
            lines[row['edition'],row['locus']].append(row)
    assert sum(map(len,lines.values()))==guard['stats']['selected']
    found=[]
    for key,rows in sorted(lines.items()):
        if rows[0]['kind']!='P':continue
        rows.sort(key=lambda r:int(r['source_group_index']))
        assert all(r['kind']=='P' for r in rows)
        assert len(rows)==int(rows[0]['source_group_count'])
        assert [int(r['source_group_index']) for r in rows]==list(range(1,len(rows)+1))
        found.extend(v.runs(rows))
    assert [original for original,rows in found]==read(ROOT/s['native_runs_path'])
    signs=read(ROOT/s['signs_path'])['signs']
    panel={'guard_sha256':sha(ROOT/s['native_guard_path']),'cache_sha256':sha(cache),'old_runs_sha256':sha(ROOT/s['native_runs_path']),'readers':{}}
    for ed in s['editions']:
        yes=[];no=[]
        for original,rows in found:
            if original['edition']!=ed:continue
            units=v.parse(original['word'],signs)
            if units is None:no.append({'original':original,'reason':'NO_UNIQUE_22_UNIT_PARSE','source_rows':rows})
            else:yes.append({'original':original,'working_units':units,'source_rows':rows})
        maximum=max(x['original']['length'] for x in yes)
        panel['readers'][ed]={'retained_runs':yes,'unparsed_runs':no,'max_native_run':maximum,'required_source_run':maximum-1,'maximum_run_witnesses':[x['original'] for x in yes if x['original']['length']==maximum]}
    assert panel==read(A/'NATIVE_PANEL.json')
    words_by_pack={};catalog={};snapshot_pins={}
    for pack in s['source_packs']:
        path=E/'source'/(pack+'_words.txt');data=path.read_text(encoding='utf-8');words=data.splitlines()
        assert words==sorted(set(words)) and all(re.fullmatch('[a-z]+',w) for w in words)
        assert data=='\n'.join(words)+'\n'
        assert len(words)==manifest['vocabularies'][pack]['size']
        assert sha(path)==v.wordhash(words)==manifest['vocabularies'][pack]['sha256']
        snapshot_pins[path.relative_to(ROOT).as_posix()]=sha(path)
        letters={}
        for c in 'abcdefghijklmnopqrstuvwxyz':
            maximum=max(v.longest(w,c) for w in words)
            example=next((w for w in words if v.longest(w,c)==maximum),None) if maximum else None
            letters[c]={'max_run':maximum,'longest_example':example}
        rawpath=s['source_directory']+'/'+pack+'.txt'
        catalog[pack]={'path':rawpath,'source_sha256':oldpins[rawpath],'vocabulary_size':len(words),'vocabulary_sha256':v.wordhash(words),'letters':letters}
        words_by_pack[pack]=words
    assert {'packs':catalog}==read(A/'VOCABULARY_RUNS.json')
    cases=[]
    for ed in s['editions']:
        r=panel['readers'][ed]['max_native_run']
        for pack in s['source_packs']:
            options=[]
            for c in s['candidate_letters']:
                matches=[] if c==' ' else [w for w in words_by_pack[pack] if c*(r-1) in w]
                maximum=1 if c==' ' else catalog[pack]['letters'][c]['max_run']
                options.append({'character':'SPACE' if c==' ' else c,'max_source_run':maximum,'eligible':maximum>=r-1,'word_count':len(matches),'words_sha256':None if c==' ' else v.wordhash(matches),'examples':matches[:s['examples_per_letter']]})
            survivors=[x['character'] for x in options if x['eligible']]
            cases.append({'edition':ed,'pack':pack,'max_native_run':r,'required_source_run':r-1,'beta_options':options,'surviving_beta':survivors,'decision':'RUN_BOUND_CAPACITY_ONLY' if survivors else 'FIXED_WORDSTAR_CONSTANT_DIAGONAL_EXCLUDED'})
    result={'experiment_id':'GDT1412','status':'COMPLETE_FIXED_WORDSTAR_REPEAT_BOUND','cases':cases,'word_meanings_assigned':0,'claim_ceiling':s['claim_ceiling']}
    assert result==read(A/'RESULT.json')
    receipt={'status':'PASS_PUBLIC_WORDSET_AND_NATIVE_REPLAY','experiment_id':'GDT1412','verifier_sha256':sha(Path(__file__)),'scientific_lock_sha256':sha(E/'LOCK.json'),'snapshot_pins':snapshot_pins,'external_raw_pins_metadata_only':{p:oldpins[p] for p in sorted(external)},'scientific_nonraw_pins_verified':{p:h for p,h in lock['files'].items() if p not in external},'outputs':{n:sha(A/n) for n in ['NATIVE_PANEL.json','VOCABULARY_RUNS.json','RESULT.json']},'cases':len(cases),'scope':'Post-result engineering replay of frozen wordsets and native selected cache. Reuses frozen validator pure functions; not a new independent raw-text extraction. Six external raw caches neither read nor required; their hashes are metadata comparisons only. No perception, key, language identification or translation claim.'}
    destination=A/'PUBLIC_REPLAY.json'
    if destination.exists():assert read(destination)==receipt
    else:destination.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':receipt['status'],'cases':len(cases)}))
if __name__=='__main__':main()
