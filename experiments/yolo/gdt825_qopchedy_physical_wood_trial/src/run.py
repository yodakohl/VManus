#!/usr/bin/env python3
"""Batch two concrete material guesses over the same small cached packet."""
import argparse
import json
import runpy
from collections import Counter
from pathlib import Path

EXP=Path(__file__).resolve().parent.parent
ROOT=EXP.parents[2]
H=runpy.run_path(str(ROOT/'experiments/yolo/gdt823_qol_source_anaphor_trial/src/run.py'))
read,table,enc=[H[k] for k in ['read','table','enc']]
PRIOR=ROOT/'experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts'


def build():
    spec=json.loads((EXP/'src/SPEC.json').read_text())
    assert spec['whole']=='qopchedy' and spec['candidates']=={'WOOD':'Holz?','CHARCOAL':'Holzkohle?'}
    assert spec['sealed_data']==['f84','f84r']
    groups,contexts,blocks,old=[read(PRIOR/n) for n in ['SOURCE_GROUPS.tsv','CONTEXTS.tsv','BLOCKS.tsv','TRIALS.tsv']]
    assert len(groups)==8391 and len(contexts)==320 and all(not g['page'].startswith('f84') for g in groups)
    hits=[g for g in groups if g['ivtff_group_raw']==spec['whole']]
    loci={g['locus'] for g in hits};bids={c['block_id'] for c in contexts if c['locus'] in loci}
    coverage=[b for b in blocks if b['block_id'] in bids]
    assert all(b['complete']=='1' and b['kind']=='P' for b in coverage)
    trials=[]
    for r in old:
        if r['locus'] not in loci: continue
        words=json.loads(r['source_groups_json'])
        for material,gloss in spec['candidates'].items():
            literal=json.loads(r['literal_json'])
            for i,w in enumerate(words):
                literal[i]={'qol':'daraus?','qolchedy':'daraus? wird?',spec['whole']:gloss}.get(w,literal[i])
            trials.append({'material':material,**r,'literal_json':enc(literal),'confidence':spec['confidence']})
    reviewed=[c for c in contexts if c['block_id'] in bids]
    result=dict(experiment_id='GDT825',status='C0_WOOD_CHARCOAL_UNRESOLVED_INPUT_AND_RESULT',cache_loci=320,
        exact_reader_hits=len(hits),by_edition=dict(Counter(g['edition'] for g in hits)),target_loci=len(loci),
        full_paragraphs=len(coverage),reread_loci=len(reviewed),reread_kinds=dict(Counter(c['kind'] for c in reviewed)),
        literal_rows=len(trials),material_models=2,raiin_models=2,selected_material=None,
        all39_census=False,new_admissions=0,new_images=0,dictionary_changed=False,meanings_validated=False,
        confirmed_lexemes=0,confirmed_clauses=0,sealed_data=['f84','f84r'])
    doc=['# GDT825 full target vectors','','Both material guesses and both raiin worlds; not translated clauses.',
        'Full surrounding source paragraphs are reused via COVERAGE and GDT822 FULL_READER.','']
    for c in contexts:
        if c['locus'] not in loci: continue
        doc+=['## '+c['locus'],'']
        for e in ['ZL3b','IT2a','RF1b']:
            rs=[r for r in trials if r['locus']==c['locus'] and r['edition']==e]
            doc += [e+' groups: '+rs[0]['source_groups_json'], 'Separators: '+rs[0]['separators_json']]
            for r in rs: doc.append(r['material']+'/'+r['world']+': '+' | '.join(json.loads(r['literal_json'])))
        doc.append('')
    return {'HITS.tsv':table(hits),'COVERAGE.tsv':table(coverage),'TRIALS.tsv':table(trials),
        'READER.md':'\n'.join(doc).rstrip()+'\n','RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,text in build().items():
        path=EXP/'artifacts'/name
        if args.check: assert path.read_text()==text,name
        else: path.write_text(text)
    print('GDT825 two-material/fixed-raiin batch reproduced, no identified meaning')


if __name__=='__main__': main()
