#!/usr/bin/env python3
"""Reconstruct every first-group boundary from guarded source rows."""
import csv
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
PRIOR = ROOT/'experiments/yolo/gdt1062_schechter_plant_label_source_alignment/artifacts/LABEL_RESULTS.tsv'
SOURCE = ROOT/'experiments/semantic_assumptions/results/source_separator_transcription.tsv'


def tsv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def main():
    prior = tsv(PRIOR)
    observed = tsv(HERE/'artifacts/FIRST_HEAD_BOUNDARIES.tsv')
    result = json.loads((HERE/'artifacts/RESULT.json').read_text())
    loci = sorted({p['first_p_locus'] for p in prior})
    assert len(prior) == len(observed) == 69 and len(loci) == 23
    cmd = [str(ROOT/'vmanus-exp'),'query-tsv',str(SOURCE),'--selector','locus']
    for loc in loci: cmd += ['--allow',loc]
    cmd += ['--columns','edition,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
    query = subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    stats = json.loads(query.stderr.split('GUARD_STATS ',1)[1].splitlines()[0])
    assert stats == result['guard_stats'] and stats['skipped_forbidden'] > 0
    rows = list(csv.DictReader(io.StringIO(query.stdout),delimiter='\t'))
    indexed = {(r['edition'].lower(),r['locus']):r for r in rows
               if r['kind']=='P' and r['source_group_index']=='1'}
    checks = 0
    for p,o in zip(prior,observed):
        assert (p['page'],p['eva_label'],p['reader'],p['first_p_locus']) == (o['page'],o['eva_label'],o['reader'],o['first_p_locus'])
        s = indexed[(p['reader'],p['first_p_locus'])]
        assert o['source_group']==s['ivtff_group_raw']
        assert o['left_separator']==s['left_separator']=='LINE_START'
        assert o['right_separator']==s['right_separator']
        assert int(o['standalone_bounded']) == int(s['right_separator'] in ('DEFINITE_SPACE','LINE_END'))
        assert int(o['raw_equals_prior_group']) == int(s['ivtff_group_raw']==p['first_p_group'])
        assert int(o['prior_exact'])==int(p['first_p_exact'])
        checks += 6
    assert dict(Counter(o['right_separator'] for o in observed)) == result['right_separator_counts']
    for ed in ('zl3b','it2a','rf1b'):
        selected=[o for o in observed if o['reader']==ed]
        assert len(selected)==23
        assert sum(int(o['standalone_bounded']) for o in selected)==result['bounded_by_reader'][ed]
        assert sum(int(o['standalone_bounded']) and int(o['prior_exact']) for o in selected)==result['matched_and_bounded_by_reader'][ed]
        checks+=3
    for saved, row in zip(result['f9v'], [o for o in observed if o['page']=='f9v']):
        assert {k:str(v) for k,v in saved.items()} == row
    assert result['confirmed_words']==0
    report={'status':'PASS','checks':checks+4,'rows':len(observed),'loci':len(loci),
            'scope':'guarded independent source re-query and complete saved-row reconstruction; no semantic truth'}
    (HERE/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
