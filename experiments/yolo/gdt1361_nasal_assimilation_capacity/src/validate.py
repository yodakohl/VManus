"""Independent GDT1361 replay. Does not import primary or predecessor runners."""
from pathlib import Path
from itertools import product
import gzip
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parents[1]
OLD = ROOT / 'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def encode(word, pairs):
    table = dict(pairs)
    return tuple(table[x] if x in table and i+1 < len(word) and word[i+1] == table[x] else x for i,x in enumerate(word))

def valid_image(word, pairs):
    for n,t in pairs:
        for i in range(len(word)-1):
            if word[i:i+2] == (n,t) and (i+2 == len(word) or word[i+2] != t):
                return False
    return True

def explicit_preimage(word, pairs):
    source = list(word)
    for n,t in pairs:
        for i in range(len(word)-1):
            if word[i:i+2] == (n,t):
                source[i+1] = n
    return tuple(source)

def fixtures():
    summary=[]
    for alphabet,pairs,maximum in [('NTX',[('N','T')],8),('NTPQX',[('N','T'),('P','Q')],6)]:
        total=0
        for length in range(maximum+1):
            words=list(product(alphabet,repeat=length))
            image={encode(w,pairs) for w in words}
            characterized={w for w in words if valid_image(w,pairs)}
            assert image == characterized
            for w in characterized:
                assert encode(explicit_preimage(w,pairs),pairs) == w
            total+=len(words)
        summary.append({'alphabet':alphabet,'pairs':pairs,'max_length':maximum,'source_and_candidate_words_each':total})
    assert encode(tuple('NNT'),[('N','T')]) == tuple('NTT')
    assert encode(tuple('NT'),[('N','T')]) == encode(tuple('TT'),[('N','T')])
    assert not valid_image(tuple('NT'),[('N','T')])
    assert not valid_image(tuple('NTX'),[('N','T')])
    return summary

def parse_unique(raw, signs):
    paths=[[] for _ in range(len(raw)+1)]
    paths[0]=[()]
    for i in range(len(raw)):
        for prefix in paths[i]:
            for sign in signs:
                if raw.startswith(sign,i):
                    paths[i+len(sign)].append(prefix+(sign,))
    assert len(paths[-1]) == 1
    return paths[-1][0]

def independently_count():
    spec=json.loads((OLD/'src/SPEC.json').read_text())
    signs=spec['signs']; assert len(signs)==len(set(signs))==22
    allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed']
    assert len(allowed)==179 and not any(p.startswith('f84') or p=='f116v' for p in allowed)
    rows=json.loads(gzip.decompress((OLD/'artifacts/GROUPS.json.gz').read_bytes()))
    assert set(rows)=={'ZL3b','IT2a','RF1b'}
    readers={}
    for edition, groups in rows.items():
        pairdata={(n,t):{'N':n,'T':t,'violations':0,'NT_events':0,'NT_physical_leaves':set(),'TT_events':0,'TT_physical_leaves':set(),'first_violation':None,'first_final_violation':None} for n in signs for t in signs if n!=t}
        ids=set(); parsed_cache={}
        for row in groups:
            assert row['edition']==edition and row['page'] in allowed
            assert not row['page'].startswith('f84') and row['page'] not in ('f116v','f1r')
            assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            assert row['locus'].split('.')[0]==row['page']
            identifier=f"{edition}|{row['locus']}|G{int(row['source_group_index']):03d}"
            assert row['id']==identifier and identifier not in ids; ids.add(identifier)
            raw=row['ivtff_group_raw']; assert raw and all('a'<=x<='z' for x in raw)
            if raw not in parsed_cache: parsed_cache[raw]=parse_unique(raw,signs)
            units=parsed_cache[raw]; assert list(units)==row['units']
            match=re.fullmatch(r'f(\d+)[rv]\d*',row['page']); assert match
            leaf='f'+match.group(1)
            broken=set()
            for i,(a,b) in enumerate(zip(units,units[1:])):
                if a==b:
                    for n in signs:
                        if n!=a:
                            entry=pairdata[n,a];entry['TT_events']+=1;entry['TT_physical_leaves'].add(leaf)
                else:
                    entry=pairdata[a,b]; entry['NT_events']+=1;entry['NT_physical_leaves'].add(leaf)
                    if i+2==len(units) or units[i+2]!=b:
                        broken.add((a,b))
                        witness={'source':dict(row),'id':identifier,'unit_index':i,'page':row['page'],'locus':row['locus'],'raw':raw,'units':list(units),'following':units[i+2] if i+2<len(units) else None}
                        if entry['first_violation'] is None: entry['first_violation']=witness
                        if i+2==len(units) and entry['first_final_violation'] is None: entry['first_final_violation']=witness
            for pair in broken:pairdata[pair]['violations']+=1
        output=[]
        for entry in pairdata.values():
            entry['NT_physical_leaf_ids']=sorted(entry['NT_physical_leaves'])
            entry['TT_physical_leaf_ids']=sorted(entry['TT_physical_leaves'])
            entry['NT_physical_leaves']=len(entry['NT_physical_leaves'])
            entry['TT_physical_leaves']=len(entry['TT_physical_leaves'])
            entry['survives']=entry['violations']==0
            entry['active_survivor']=entry['survives'] and entry['TT_events']>0
            entry['recurrent_capable']=entry['survives'] and entry['TT_physical_leaves']>=2
            output.append(entry)
        readers[edition]={'group_occurrences':len(groups),'pairs':output}
    return readers

# Schema supplied by root before any primary/native result was read.
def compare(primary, expected):
    assert primary['status']=='PAIR_CAPACITY_ENUMERATED'
    assert set(primary['readers'])==set(expected)
    for edition, independent in expected.items():
        observed=primary['readers'][edition]
        assert observed['groups']==independent['group_occurrences']
        by_pair={(p['N'],p['T']):p for p in observed['pairs']}
        assert len(observed['pairs'])==len(by_pair)==462
        for p in independent['pairs']:
            q=by_pair[p['N'],p['T']]
            for mine,theirs in [('violations','violating_groups'),('NT_events','NT_events'),('TT_events','TT_events'),('NT_physical_leaves','NT_leaves'),('TT_physical_leaves','TT_leaves')]:
                assert p[mine]==q[theirs], (edition,p['N'],p['T'],mine,p[mine],q[theirs])
            if p['first_violation'] is None:
                assert q['first_violation'] is None
            else:
                assert q['first_violation']['source']==p['first_violation']['source']
                assert q['first_violation']['offset_zero_based']==p['first_violation']['unit_index']
        definitions={'survivors':lambda p:p['survives'],'active_survivors':lambda p:p['active_survivor'],'recurrent_TT_survivors':lambda p:p['recurrent_capable'],'active_with_visible_NT':lambda p:p['active_survivor'] and p['NT_events']>0}
        for key,predicate in definitions.items():
            assert {tuple(p) for p in observed[key]}=={(p['N'],p['T']) for p in independent['pairs'] if predicate(p)}
            assert len(observed[key])==len({tuple(p) for p in observed[key]})

def main():
    controls=fixtures()
    expected=independently_count()
    result_path=D/'artifacts/RESULT.json'
    if not result_path.exists():
        raise SystemExit('RESULT missing; no primary output read. Validator logic ready.')
    primary=json.loads(result_path.read_text())
    compare(primary,expected)
    report={'status':'PASS','independence':'No primary runner imported/read before validator logic freeze; inherited packet replay, independent unique segmentation and event scan.','fixtures':controls,'readers':{e:{'group_occurrences':v['group_occurrences'],'pairs':len(v['pairs'])} for e,v in expected.items()},'source_sha256':sha(OLD/'artifacts/GROUPS.json.gz'),'limits':'No source reconstruction, palaeography, actual source NT use, phonetic binding, independent held evidence or semantic validation.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
