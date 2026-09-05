#!/usr/bin/env python3
"""Same-author separate exact-coverage audit; not a semantic reviewer."""
import argparse
import copy
import csv
import json
import subprocess
from collections import Counter
from pathlib import Path

EXP=Path(__file__).resolve().parent.parent
ROOT=EXP.parents[2]
PRIOR=ROOT/'experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts'


def read(path):
    with path.open(newline='') as f: return list(csv.DictReader(f,delimiter='\t'))


def audit(trials,hits,coverage):
    source=read(PRIOR/'TRIALS.tsv'); groups=read(PRIOR/'SOURCE_GROUPS.tsv')
    expected={}
    for row in source:
        if row['world']!='ASCENT': continue
        words,ids=json.loads(row['source_groups_json']),json.loads(row['source_group_ids_json'])
        for i,w in enumerate(words):
            if w=='qolchedy': expected[ids[i]]=('JOINED',ids[i:i+1],words[i:i+1],row['locus'])
            elif words[i:i+2]==['qol','chedy']: expected[ids[i]]=('SPLIT',ids[i:i+2],words[i:i+2],row['locus'])
    assert len(hits)==len({h['hit_id'] for h in hits})==len(expected)==27
    for h in hits:
        e=expected[h['hit_id']]
        assert (h['form'],json.loads(h['group_ids_json']),json.loads(h['source_groups_json']),h['locus'])==e
    targets={v[3] for v in expected.values()}
    assert len(targets)==12 and Counter(v[0] for v in expected.values())=={'JOINED':13,'SPLIT':14}
    key=lambda r:(r['world'],r['locus'],r['edition'])
    orig={key(r):r for r in source if r['locus'] in targets}
    assert len(trials)==len({key(r) for r in trials})==len(orig)==72
    joined_changes=0
    for t in trials:
        o=orig[key(t)]
        assert all(t[k]==o[k] for k in o if k not in ['literal_json','confidence'])
        words,old,new=json.loads(t['source_groups_json']),json.loads(o['literal_json']),json.loads(t['literal_json'])
        assert len(words)==len(old)==len(new)
        for w,a,b in zip(words,old,new):
            expected_value={'qol':'daraus?','qolchedy':'daraus? wird?'}.get(w,a)
            assert b==expected_value
            joined_changes+=w=='qolchedy'
        assert t['confidence']=='C0_FIXED_COMPOSITION_NOT_IDENTIFIED_WORD'
    assert joined_changes==26
    # All already present GDT823 trial cells other than the new whole survive.
    prior823={key(r):r for r in read(ROOT/'experiments/yolo/gdt823_qol_source_anaphor_trial/artifacts/TRIALS.tsv')}
    for t in trials:
        if key(t) not in prior823: continue
        old=json.loads(prior823[key(t)]['literal_json'])
        for w,a,b in zip(json.loads(t['source_groups_json']),old,json.loads(t['literal_json'])):
            assert w=='qolchedy' or a==b
    contexts=read(PRIOR/'CONTEXTS.tsv'); wanted={c['block_id'] for c in contexts if c['locus'] in targets}
    expected_blocks=[b for b in read(PRIOR/'BLOCKS.tsv') if b['block_id'] in wanted]
    assert coverage==expected_blocks and len(coverage)==9 and all(b['complete']=='1' for b in coverage)
    reviewed=[c for c in contexts if c['block_id'] in wanted]
    assert len(reviewed)==164 and Counter(c['kind'] for c in reviewed)=={'P':155,'L':9}
    assert all(not g['page'].startswith('f84') for g in groups)
    return dict(reader_hits=27,joined=13,split=14,loci=12,paragraphs=9,reread_loci=164,literal_rows=72,new_joined_cells=26)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    trials,hits,coverage=[read(EXP/'artifacts'/n) for n in ['TRIALS.tsv','HITS.tsv','COVERAGE.tsv']]
    counts=audit(trials,hits,coverage); mutations={}
    def reject(name,t,h,c):
        try: audit(t,h,c)
        except AssertionError: mutations[name]='REJECTED'
        else: raise AssertionError(name)
    reject('omit_joined_hit',trials,hits[1:],coverage)
    reject('omit_full_paragraph',trials,hits,coverage[1:])
    for name,loc,ed,word,replacement in [
        ('erase_earlier_becomes','f77r.34','ZL3b','chedy',''),
        ('erase_air_repetition','f77r.34','IT2a','qokaiin',''),
        ('invent_source_fuel','f82r.2','ZL3b','dchedy','Brennstoff?'),
        ('translate_opaque_join','f77r.34','RF1b','qolche@152;y','daraus? wird?'),
        ('generalize_other_qol_prefix','f76r.26','ZL3b','qolain','daraus?')]:
        t=copy.deepcopy(trials);r=next(r for r in t if r['world']=='ASCENT' and r['locus']==loc and r['edition']==ed)
        words=json.loads(r['source_groups_json']);values=json.loads(r['literal_json'])
        values[max(i for i,w in enumerate(words) if w==word)]=replacement
        r['literal_json']=json.dumps(values,ensure_ascii=False);reject(name,t,hits,coverage)
    res=subprocess.run([str(ROOT/'vmanus-exp'),'check-edge-packet',str((EXP/'artifacts/RELATION_PACKET.tsv').relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True)
    intake=json.loads(res.stdout)
    assert res.returncode==1 and intake['score_ready'] is False and intake['eligible_edges']==0
    assert len(intake['errors'])==27 and all(e.endswith('formal access is not sealed') for e in intake['errors'])
    assert (EXP/'artifacts/RELATION_INTAKE.json').read_text()==res.stdout
    output=json.dumps(dict(status='PASS_ACCOUNTING_NOT_RELATION_GATE_OR_MEANING',counts=counts,mutations=mutations,
        relation_gate='INVALID_PACKET_PREVIOUS_FORMAL_ACCESS_NO_SCORE',same_author=True,meanings_validated=False),indent=2,sort_keys=True)+'\n'
    path=EXP/'artifacts/VALIDATION.json'
    if args.check: assert path.read_text()==output
    else: path.write_text(output)
    print('GDT824 accounting PASS, seven mutations rejected; relation gate FAIL and meaning unvalidated')


if __name__=='__main__': main()
