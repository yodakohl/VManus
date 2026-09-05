#!/usr/bin/env python3
"""Factorized eight-model dar trial; store each source line only once."""
import argparse
import json
import runpy
from collections import Counter
from pathlib import Path

EXP=Path(__file__).resolve().parent.parent;ROOT=EXP.parents[2]
H=runpy.run_path(str(ROOT/'experiments/yolo/gdt823_qol_source_anaphor_trial/src/run.py'))
read,table,enc=[H[k] for k in ['read','table','enc']]
PRIOR=ROOT/'experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts'


def build():
    spec=json.loads((EXP/'src/SPEC.json').read_text())
    assert spec['whole_slots']=={'dar':'DAR','qopchedy':'MATERIAL','raiin':'RAIIN'}
    assert spec['sealed_data']==['f84','f84r']
    groups,contexts,blocks,old=[read(PRIOR/n) for n in ['SOURCE_GROUPS.tsv','CONTEXTS.tsv','BLOCKS.tsv','TRIALS.tsv']]
    assert len(groups)==8391 and len(contexts)==320 and all(not g['page'].startswith('f84') for g in groups)
    hits=[g for g in groups if g['ivtff_group_raw']=='dar'];loci={g['locus'] for g in hits}
    bids={c['block_id'] for c in contexts if c['locus'] in loci};coverage=[b for b in blocks if b['block_id'] in bids]
    templates=[];doc=['# GDT826 factorized full target lines','','Each {slot} has the two fixed values in SPEC. This is not a translation.','']
    for r in old:
        if r['world']!='ASCENT' or r['locus'] not in loci:continue
        words=json.loads(r['source_groups_json']);literal=json.loads(r['literal_json'])
        template=[{'slot':spec['whole_slots'][w]} if w in spec['whole_slots'] else
            {'qol':'daraus?','qolchedy':'daraus? wird?'}.get(w,a) for w,a in zip(words,literal)]
        templates.append({k:v for k,v in r.items() if k not in ['world','literal_json','confidence']} |
            {'template_json':enc(template),'confidence':spec['confidence']})
        doc += [r['locus']+' '+r['edition']+': '+' | '.join('{'+x['slot']+'}' if isinstance(x,dict) else x for x in template)]
    reviewed=[c for c in contexts if c['block_id'] in bids]
    result=dict(experiment_id='GDT826',status='C0_PROPERTY_PARSE_OPEN_DRY_WATER_PRESSURE_NO_WINNER',
        cached_loci=320,exact_reader_hits=len(hits),by_edition=dict(Counter(g['edition'] for g in hits)),target_loci=len(loci),
        blocks=len(coverage),P_blocks=sum(b['kind']=='P' for b in coverage),reread_loci=len(reviewed),
        reread_kinds=dict(Counter(c['kind'] for c in reviewed)),stored_templates=len(templates),virtual_model_rows=8*len(templates),
        all39_census=False,new_admissions=0,new_images=0,dictionary_changed=False,meanings_validated=False,
        confirmed_lexemes=0,confirmed_clauses=0,sealed_data=['f84','f84r'])
    return {'HITS.tsv':table(hits),'COVERAGE.tsv':table(coverage),'TEMPLATES.tsv':table(templates),
        'READER.md':'\n'.join(doc)+'\n','RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,text in build().items():
        path=EXP/'artifacts'/name
        if args.check:assert path.read_text()==text,name
        else:path.write_text(text)
    print('GDT826 factorized eight-model packet reproduced; no word or role proved')


if __name__=='__main__':main()
