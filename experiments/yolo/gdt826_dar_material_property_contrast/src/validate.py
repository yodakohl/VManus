#!/usr/bin/env python3
"""Separate same-author expansion/coverage audit, not semantic validation."""
import argparse
import copy
import csv
import itertools
import json
from pathlib import Path
EXP=Path(__file__).resolve().parent.parent;ROOT=EXP.parents[2]
PRIOR=ROOT/'experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts'


def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f,delimiter='\t'))


def audit(rows,hits,coverage):
    groups=read(PRIOR/'SOURCE_GROUPS.tsv');expected=[g for g in groups if g['ivtff_group_raw']=='dar']
    assert hits==expected and len(hits)==81
    loci={h['locus'] for h in hits};assert len(loci)==30
    contexts=read(PRIOR/'CONTEXTS.tsv');bids={c['block_id'] for c in contexts if c['locus'] in loci}
    assert coverage==[b for b in read(PRIOR/'BLOCKS.tsv') if b['block_id'] in bids]
    assert len(coverage)==16 and len([c for c in contexts if c['block_id'] in bids])==176
    old={(r['locus'],r['edition'],r['world']):r for r in read(PRIOR/'TRIALS.tsv') if r['locus'] in loci}
    assert len(rows)==len({(r['locus'],r['edition']) for r in rows})==90
    assert {(r['locus'],r['edition']) for r in rows}=={(a,b) for a,b,c in old}
    count=0
    for r in rows:
        o=old[r['locus'],r['edition'],'ASCENT']
        assert all(r[k]==o[k] for k in o if k not in ['world','literal_json','confidence'])
        words=json.loads(o['source_groups_json']);tmp=json.loads(r['template_json']);assert len(tmp)==len(words)
        for d,m,(world,rv) in itertools.product(['Erde?','trocken?'],['Holz?','Holzkohle?'],[('ASCENT','steigt?'),('LIGHTNESS','leicht?')]):
            vals={'DAR':d,'MATERIAL':m,'RAIIN':rv}
            actual=[vals[x['slot']] if isinstance(x,dict) else x for x in tmp]
            baseline=json.loads(old[r['locus'],r['edition'],world]['literal_json'])
            expected=[{'dar':d,'qopchedy':m,'qol':'daraus?','qolchedy':'daraus? wird?'}.get(w,x) for w,x in zip(words,baseline)]
            assert actual==expected
            count+=1
    assert count==720


def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    rows,hits,coverage=[read(EXP/'artifacts'/n) for n in ['TEMPLATES.tsv','HITS.tsv','COVERAGE.tsv']]
    audit(rows,hits,coverage);mutations={}
    for name,loc,edition,word,replacement in [
        ('water_to_unknown','f75r.35','ZL3b','qokain','[qokain]'),
        ('omit_dar_repeat','f75r.35','IT2a','dar',''),
        ('humoral_dry_rescue','f76r.51','ZL3b','dar','humoral trocken?'),
        ('split_dardardy','f75r.36','ZL3b','dardardy',{'slot':'DAR'}),
        ('erase_becomes','f76r.51','IT2a','chedy','')]:
        changed=copy.deepcopy(rows);r=next(r for r in changed if r['locus']==loc and r['edition']==edition)
        words=json.loads(r['source_groups_json']);v=json.loads(r['template_json']);v[max(i for i,w in enumerate(words) if w==word)]=replacement;r['template_json']=json.dumps(v)
        try:audit(changed,hits,coverage)
        except AssertionError:mutations[name]='REJECTED'
        else:raise AssertionError(name)
    out=json.dumps(dict(status='PASS_ACCOUNTING_NOT_SYNTAX_OR_MEANING',templates=90,expanded_rows_checked=720,
        mutations=mutations,same_author=True,meanings_validated=False),indent=2,sort_keys=True)+'\n'
    path=EXP/'artifacts/VALIDATION.json'
    if args.check:assert path.read_text()==out
    else:path.write_text(out)
    print('GDT826 720 expansions and five mutations checked; no syntactic or lexical proof')


if __name__=='__main__':main()
