#!/usr/bin/env python3
"""Exhaustive exposed f85 literal-family/type capacity audit; no decoder."""
from pathlib import Path
import csv
import hashlib
import json
import re
from collections import Counter


def root_at(start):
    for p in (start, *start.parents):
        if (p/'AGENTS.md').is_file() and (p/'.git').exists():
            return p
    raise RuntimeError('repository root not found')

ROOT=root_at(Path(__file__).resolve())
EXP=Path(__file__).resolve().parents[1]
ART=EXP/'artifacts'

def dump_tsv(path, fields, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

def packed(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def main():
    spec=json.loads((EXP/'src/SPEC.json').read_text())
    lock=json.loads((EXP/'src/PREREG_LOCK.json').read_text())
    for p,h in lock['inputs'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    source=ROOT/spec['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==spec['source_sha256']
    draft=json.loads((ROOT/spec['draft']).read_text())
    vocab={**draft['fixed_idea550_bindings'],**draft['new_whole_form_values']}
    assert len(vocab)==24
    with source.open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f,delimiter='\t');fields=reader.fieldnames;raw=list(reader)
    assert len(raw)==473
    rows=[]
    for r in raw:
        assert r['page']=='f85r2' and r['edition'] in spec['editions']
        m=re.fullmatch(r'f85r2\.(\d+)(?:[A-Za-z])?',r['locus']);assert m
        n=int(m[1]);assert n in spec['all_loci']
        block=next(b for b,ns in spec['blocks'].items() if n in ns)
        rows.append({**r,'line_number':n,'block':block})
    rows.sort(key=lambda r:(spec['editions'].index(r['edition']),r['line_number'],int(r['source_group_index'])))
    assert len({(r['edition'],r['source_group_id']) for r in rows})==473
    contexts=[]
    for r in rows:
        v=vocab.get(r['ivtff_group_raw'])
        contexts.append({**r,'baseline_type':v['type'] if v else 'UNASSIGNED','baseline_meaning':v['meaning'] if v else ''})
    dump_tsv(ART/'CONTEXTS.tsv',fields+['line_number','block','baseline_type','baseline_meaning'],contexts)
    cases=[]
    for r in rows:
        whole=r['ivtff_group_raw']
        if not whole.startswith('qod'):continue
        suffix=whole[3:]
        rule=spec['type_rules'].get(suffix)
        blockrows=[s for s in rows if s['edition']==r['edition'] and s['block']==r['block']]
        eligible=r['block']=='S' and r['line_number']==16
        present={role:any(s['line_number']==loc and s['ivtff_group_raw']==word for s in blockrows)
                 for role,(loc,word) in spec['licensed_frame']['required_tokens'].items()} if eligible else {}
        gaps=[role for role,v in present.items() if not v] if eligible else ['NO_LICENSED_BLOCK_FRAME']
        unknown=[{'id':s['source_group_id'],'raw':s['ivtff_group_raw']} for s in blockrows if s['ivtff_group_raw'] not in vocab]
        for candidate in spec['candidates']:
            typ=rule[candidate] if rule else 'UNBOUND_COMPONENT'
            typed=typ in ('TYPED','TYPED_WITH_LOC_OWNER')
            binding=('AUTHORED_S_GOAL_AGREEMENT' if not gaps else 'MISSING_EXACT_S_FRAME') if eligible else 'NO_LICENSED_TRANSFER_FRAME'
            if not typed:binding='NO_TYPED_OUTPUT'
            cases.append({'candidate':candidate,'edition':r['edition'],'source_group_id':r['source_group_id'],
                'locus':r['locus'],'group_index':r['source_group_index'],'block':r['block'],'raw':whole,'remainder':suffix,
                'remainder_type':rule['fixed_type'] if rule else 'UNASSIGNED','type_result':typ,
                'predicted_predicate':'ATTRACT(f,x,Goal=r)' if typed else '',
                'goal_derivation':rule['goal'] if typed else '',
                'extra_lift':str(typ=='TYPED_WITH_LOC_OWNER').lower(),'binding_result':binding,
                'frame_token_availability':packed(present),'missing_frame':packed(gaps),
                'context_group_count':len(blockrows),'baseline_unassigned_groups':len(unknown),
                'baseline_unassigned_context':packed(unknown),
                'meaning_confirmed':'false'})
    assert cases
    dump_tsv(ART/'CASES.tsv',list(cases[0]),cases)
    result={'status':'FIXED_FAMILY_TYPE_AND_BINDING_CAPACITY_ONLY','source_rows':len(rows),'f85_loci_per_edition':24,
       'baseline_values':len(vocab),'family_occurrences':len(cases)//2,
       'family_forms':dict(sorted(Counter(r['ivtff_group_raw'] for r in rows if r['ivtff_group_raw'].startswith('qod')).items())),
       'candidate_rows':len(cases),'candidates':{},'independent_meaning_confirmation':0,'new_target_access':False,
       'new_whole_senses':0,'new_atomic_dictionary_entries':0,
       'new_derived_form_predictions':['qodain'],
       'new_whole_senses_field_scope':'No new atomic sense values; qodain receives a new conditional derived form-to-meaning prediction.',
       'alternative_reader_independence':False,'counterexample_selection':'all literal qod-initial groups',
       'decision':'No productive or translated prefix selected. LOC_OWNER is an extra typed hypothesis; transfer requires written reference rules.'}
    for c in spec['candidates']:
        subset=[r for r in cases if r['candidate']==c]
        result['candidates'][c]={'type_results':dict(Counter(r['type_result'] for r in subset)),
            'binding_results':dict(Counter(r['binding_result'] for r in subset)),
            'nondevelopment_goal_comparisons':sum(r['block']!='S' and r['binding_result']=='AUTHORED_S_GOAL_AGREEMENT' for r in subset),
            'extra_loc_owner_applications':sum(r['extra_lift']=='true' for r in subset)}
    (ART/'RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
