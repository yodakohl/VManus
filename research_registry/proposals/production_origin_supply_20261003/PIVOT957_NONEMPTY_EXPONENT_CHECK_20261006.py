#!/usr/bin/env python3
"""Small certificate replay of an exposed conditional grammatical consequence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
specpath=P/'PIVOT957_NONEMPTY_EXPONENT_BOUND_20261006.json'
spec=json.loads(specpath.read_text())
for p,h in spec['input_hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
old=ROOT/'experiments/yolo/gdt857_cyclic_inventory_triple_bound/artifacts'
assert json.loads((old/'VALIDATION.json').read_text())['status']=='PASS_INDEPENDENT_TRIPLE_ENUMERATION_AND_DIRECT_SOURCE_WITNESSES'
hits=json.loads((old/'HITS.json').read_text());assert len(hits)==18
wanted={'chol':('f47r.7',4,['ch','o','l']), 'ytaiin':('f86v3.3',2,['y','t','a','i','i','n'])}
readers={}
for ed in ['IT2a','RF1b','ZL3b']:
    witnesses=[]
    for word,(locus,start,units)in wanted.items():
        matched=[r for r in hits if r['edition']==ed and r['raw']==word and r['locus']==locus and int(r['start_index'])==start]
        assert len(matched)==1;r=matched[0]
        assert ''.join(units)==word and all(g['ivtff_group_raw']==word for g in r['groups'])
        assert [int(g['source_group_index'])for g in r['groups']]==list(range(start,start+3))
        assert all(g['left_separator']==g['right_separator']=='DEFINITE_SPACE'for g in r['groups'])
        assert r['metadata']['kind']=='P'and not r['page'].startswith(('f84','f116v'))
        witnesses.append({'word':word,'units':units,'locus':locus,'start_index':start,'source_ids':r['source_ids']})
    common=set.intersection(*(set(w['units'])for w in witnesses));assert not common
    readers[ed]={'witnesses':witnesses,'common_working_signs':sorted(common)}
result={'status':'FIXED_NONEMPTY_LITERAL_SAME_EXPONENT_EXCLUDED_ANY_POSITION','checked_utc':datetime.now(timezone.utc).isoformat(),
        'proof_sha256':hashlib.sha256(specpath.read_bytes()).hexdigest(),'readers':readers,
        'algebra':'A common nonempty written exponent must contribute at least one sign to both words; their sign sets are disjoint. Any global bijection preserves disjointness.',
        'validation_scope':'Source hashes, exact old curated witnesses, whole-boundary fields and symbol-set certificate only. The grammar lemma is a separate human proof.',
        'claim_ceiling':spec['claim_ceiling']}
out=P/'PIVOT957_NONEMPTY_EXPONENT_RESULT_20261006.json';assert not out.exists()
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'readers':list(readers),'new_raw_queries':0,'new_word_meanings':0}))
