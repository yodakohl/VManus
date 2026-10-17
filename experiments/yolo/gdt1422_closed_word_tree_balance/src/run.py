"""Replay a known-source word-tree balance obstruction; no decoder."""
from pathlib import Path
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]

def read(relative):
    return json.loads((ROOT / relative).read_text())

def main():
    spec = json.loads((HERE / 'src/SPEC.json').read_text())
    lock = json.loads((HERE / 'LOCK.json').read_text())
    for name, digest in lock['sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    for name, digest in spec['inputs'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    base = 'experiments/yolo/gdt1200_stable_part_repetition_capacity/artifacts/'
    profiles = read(base+'FORM_PROFILES.json')
    lines = read(base+'REPEAT_SOURCE_LINES.json')
    cases = []
    forms = spec['forms']
    for reader in spec['readers']:
        entries = []
        for form in forms:
            rows = [r for r in profiles if r['edition']==reader and r['form']==form]
            assert len(rows)==1
            row=rows[0]
            assert row['n']==len(row['source_group_ids'])>0
            entries.append({'form':form,'n':row['n'],'source_group_ids':row['source_group_ids'],'loci':row['loci']})
        counts = [e['n'] for e in entries]
        assert counts==spec['expected_counts'][reader]
        witnesses=[]
        for locus in spec['joined_loci']:
            source=[r for r in lines if r['edition']==reader and r['locus']==locus]
            assert len(source)==1
            matches=[g for g in source[0]['groups'] if g['ivtff_group_raw']==forms[2]]
            assert len(matches)==1
            group=matches[0]
            assert group['left_separator']==group['right_separator']=='DEFINITE_SPACE'
            assert group['source_group_id'] in entries[2]['source_group_ids']
            witnesses.append(group)
        assert forms[0]+forms[1]==forms[2]
        vectors=[dict(sorted(Counter(w).items())) for w in forms]
        total=Counter()
        for k,v in zip([-1,-1,1],vectors):
            for u,n in v.items(): total[u]+=k*n
        assert all(v==0 for v in total.values())
        cases.append({'reader':reader,'counts':counts,'profiles':entries,'joinedWitnesses':witnesses,'vectors':vectors,'certificate':{'coefficients':[-1,-1,1],'lhs':dict(sorted(total.items())),'rhs':-1}})
    result={'status':'CLOSED_WORD_FIXED_ARITY_EXCLUDED','cases':cases,'input_hashes':spec['inputs'],'proof':'Every single finite rooted tree has sum(1-arity)=1; a literal concatenation of two such trees has sum2, not1.','claim_ceiling':spec['claim_ceiling'],'new_corpus_census':False,'new_meanings':0,'independent_readers':False}
    out=HERE/'artifacts/RESULT.json'
    assert not out.exists(), 'Refusing result overwrite'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(result['status'],len(cases),'reader cases / one manuscript')

if __name__=='__main__': main()
