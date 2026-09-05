#!/usr/bin/env python3
"""Separate same-author exact substitution audit, no semantic scoring."""
import argparse
import copy
import csv
import json
from pathlib import Path

EXP=Path(__file__).resolve().parent.parent;ROOT=EXP.parents[2]
PRIOR=ROOT/'experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts'


def read(p):
    with p.open(newline='') as f: return list(csv.DictReader(f,delimiter='\t'))


def audit(rows,hits,coverage):
    groups=read(PRIOR/'SOURCE_GROUPS.tsv')
    expected=[g for g in groups if g['ivtff_group_raw']=='qopchedy']
    assert hits==expected and len(hits)==18
    loci={h['locus'] for h in hits};assert len(loci)==6
    contexts=read(PRIOR/'CONTEXTS.tsv');bids={c['block_id'] for c in contexts if c['locus'] in loci}
    assert coverage==[b for b in read(PRIOR/'BLOCKS.tsv') if b['block_id'] in bids] and len(coverage)==6
    assert len([c for c in contexts if c['block_id'] in bids])==102
    key=lambda r:(r['world'],r['locus'],r['edition'])
    old={key(r):r for r in read(PRIOR/'TRIALS.tsv') if r['locus'] in loci}
    assert len(rows)==72 and len({(r['material'],key(r)) for r in rows})==72
    assert {(r['material'],key(r)) for r in rows}=={(m,k) for m in ['WOOD','CHARCOAL'] for k in old}
    changes=0
    for r in rows:
        o=old[key(r)];assert all(r[k]==o[k] for k in o if k not in ['literal_json','confidence'])
        ws,a,b=json.loads(o['source_groups_json']),json.loads(o['literal_json']),json.loads(r['literal_json'])
        assert len(ws)==len(a)==len(b)
        for w,x,y in zip(ws,a,b):
            gloss={'qol':'daraus?','qolchedy':'daraus? wird?','qopchedy':{'WOOD':'Holz?','CHARCOAL':'Holzkohle?'}[r['material']]}.get(w,x)
            assert y==gloss
            changes+=w=='qopchedy'
    assert changes==72


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    rows,hits,coverage=[read(EXP/'artifacts'/n) for n in ['TRIALS.tsv','HITS.tsv','COVERAGE.tsv']]
    audit(rows,hits,coverage);mutations={}
    for name,loc,edition,word,new in [
        ('drop_second_material','f77r.9','IT2a','qopchedy',''),
        ('turn_becomes_into_heats','f76r.51','ZL3b','chedy','erwärmt?'),
        ('invent_wood_source','f76r.51','ZL3b','dar','Holz?'),
        ('merge_reader_variant','f81v.15','ZL3b','qofchedy','Holz?'),
        ('change_material_between_occurrences','f81r.20','IT2a','qopchedy','Holzkohle?')]:
        changed=copy.deepcopy(rows);r=next(r for r in changed if r['material']=='WOOD' and r['world']=='ASCENT' and r['locus']==loc and r['edition']==edition)
        ws=json.loads(r['source_groups_json']);v=json.loads(r['literal_json']);v[max(i for i,w in enumerate(ws) if w==word)]=new;r['literal_json']=json.dumps(v)
        try: audit(changed,hits,coverage)
        except AssertionError: mutations[name]='REJECTED'
        else: raise AssertionError(name)
    output=json.dumps(dict(status='PASS_ACCOUNTING_NOT_MEANING',mutations=mutations,reader_hits=18,loci=6,trial_rows=72,
        same_author=True,meanings_validated=False),indent=2,sort_keys=True)+'\n'
    path=EXP/'artifacts/VALIDATION.json'
    if args.check: assert path.read_text()==output
    else: path.write_text(output)
    print('GDT825 accounting PASS, five mutations rejected; neither material identified')


if __name__=='__main__': main()
