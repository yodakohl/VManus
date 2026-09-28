#!/usr/bin/env python3
"""Complete first-prose-group boundary audit for the frozen GDT1062 claims."""
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
PRIOR = ROOT / 'experiments/yolo/gdt1062_schechter_plant_label_source_alignment'
SOURCE = ROOT / 'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
HASHES = {
    PRIOR/'src/claims.tsv': '8fff37db44c619c21b86422125e985d105bed5e2a6b6cd66e650390477c9d4f0',
    PRIOR/'artifacts/LABEL_RESULTS.tsv': '616e0813b249641eb2519fde9989a3efaff0cfb7d942880e66ba623c78dde4c3',
    SOURCE: '4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0',
}
FIELDS = ['page','eva_label','claimed_plant','reader','first_p_locus',
          'prior_exact','source_group','left_separator','right_separator',
          'standalone_bounded','raw_equals_prior_group']


def read_tsv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def main():
    for path, expected in HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
    claims = read_tsv(PRIOR/'src/claims.tsv')
    prior = read_tsv(PRIOR/'artifacts/LABEL_RESULTS.tsv')
    assert len(claims) == 23 and len({r['page'] for r in claims}) == 23
    assert len(prior) == 69
    loci = sorted({r['first_p_locus'] for r in prior})
    assert len(loci) == 23
    cmd = [str(ROOT/'vmanus-exp'), 'query-tsv', str(SOURCE), '--selector', 'locus']
    for locus in loci:
        cmd += ['--allow', locus]
    cmd += ['--columns', 'edition,locus,kind,source_group_index,source_group_count,ivtff_group_raw,left_separator,right_separator']
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    stats = json.loads(proc.stderr.partition('GUARD_STATS ')[2].splitlines()[0])
    assert stats['skipped_forbidden'] > 0 and stats['selected'] > 0
    source_rows = list(csv.DictReader(io.StringIO(proc.stdout), delimiter='\t'))
    first = {(r['edition'].lower(), r['locus']): r for r in source_rows
             if r['source_group_index'] == '1' and r['kind'] == 'P'}
    assert len(first) == 69
    out = []
    for p in prior:
        r = first[(p['reader'], p['first_p_locus'])]
        out.append({
            'page':p['page'], 'eva_label':p['eva_label'],
            'claimed_plant':p['claimed_plant'], 'reader':p['reader'],
            'first_p_locus':p['first_p_locus'], 'prior_exact':p['first_p_exact'],
            'source_group':r['ivtff_group_raw'],
            'left_separator':r['left_separator'],
            'right_separator':r['right_separator'],
            'standalone_bounded':int(r['right_separator'] in ('DEFINITE_SPACE','LINE_END')),
            'raw_equals_prior_group':int(r['ivtff_group_raw'] == p['first_p_group'])
        })
    assert len(out) == 69
    artifact = HERE/'artifacts/FIRST_HEAD_BOUNDARIES.tsv'
    with artifact.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(out)
    result = {
        'status':'DESCRIPTIVE_BOUNDARY_ELIGIBILITY_ONLY',
        'claim_count':23, 'reader_rows':69,
        'right_separator_counts':dict(sorted(Counter(r['right_separator'] for r in out).items())),
        'bounded_by_reader':{ed:sum(int(r['standalone_bounded']) for r in out if r['reader']==ed)
                             for ed in ('zl3b','it2a','rf1b')},
        'matched_and_bounded_by_reader':{ed:sum(int(r['standalone_bounded']) and int(r['prior_exact'])
                                            for r in out if r['reader']==ed)
                                         for ed in ('zl3b','it2a','rf1b')},
        'guard_stats':stats,
        'f9v':[r for r in out if r['page']=='f9v'],
        'confirmed_words':0,
        'claim_ceiling':'physical first-group boundary, never plant-name meaning or independence'
    }
    (HERE/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:result[k] for k in ('status','claim_count','reader_rows','right_separator_counts','bounded_by_reader','matched_and_bounded_by_reader')},indent=2))


if __name__ == '__main__':
    main()
