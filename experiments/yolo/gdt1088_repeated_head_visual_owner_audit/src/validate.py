#!/usr/bin/env python3
"""Check the fixed roster, complete join and source/image provenance."""
import csv
import hashlib
import itertools
import json
from pathlib import Path


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / 'AGENTS.md').is_file() and (candidate / '.git').exists():
            return candidate
    raise RuntimeError('repository root not found')


ROOT = repo_root(Path(__file__).resolve())
BASE = ROOT / 'experiments/yolo/gdt1088_repeated_head_visual_owner_audit'
GROUPS = {'kooiin': ['f2v', 'f29v'], 'o': ['f42r', 'f56r'],
          'pchor': ['f19r', 'f21r', 'f52v'], 'tshor': ['f15r', 'f53v']}


def read(path):
    with path.open(newline='') as file:
        return list(csv.DictReader(file, delimiter='\t'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    heads = read(ROOT / 'experiments/yolo/gdt1070_first_head_collision_capacity/artifacts/HEAD_MULTIPLICITIES.tsv')
    repeated = {r['head_surface']: set(r['pages'].split(',')) for r in heads if int(r['multiplicity']) > 1}
    assert repeated == {k: set(v) for k, v in GROUPS.items()}
    pages = set().union(*map(set, GROUPS.values()))
    assert len(pages) == 9
    new = read(BASE / 'src/PAGE_ADMISSIONS.tsv')
    assert {r['folio'] for r in new} == {'f19r', 'f29v', 'f42r', 'f52v'}
    source = read(BASE / 'artifacts/SOURCE.tsv')
    visual = read(BASE / 'artifacts/BLIND_VISUAL.tsv')
    assert len(source) == len(visual) == 9
    assert {r['folio'] for r in source} == {r['folio'] for r in visual} == pages
    for r in source:
        assert r['canvas_id'].endswith('/' + r['image_url'].split('/')[5])
        assert len(r['sha256']) == 64 and int(r['bytes']) > 100000
    for r in visual:
        assert all(r[k].strip() for k in ('leaves', 'roots', 'reproductive', 'architecture', 'uncertainty'))
    expected = {(k, a, b) for k, folios in GROUPS.items() for a, b in itertools.combinations(folios, 2)}
    assessments = read(BASE / 'src/ASSESSMENTS.tsv')
    output = read(BASE / 'artifacts/PAIR_CENSUS.tsv')
    assert len(assessments) == len(output) == 6
    for table in (assessments, output):
        assert {(r['head'], r['folio_a'], r['folio_b']) for r in table} == expected
        assert all(r['same_taxon'] in {'YES', 'NO', 'UNDECIDABLE'} and
                   r['shared_specific_organ'] in {'YES', 'NO', 'UNDECIDABLE'} for r in table)
    visual_by = {r['folio']: r for r in visual}
    for r in output:
        a, b = visual_by[r['folio_a']], visual_by[r['folio_b']]
        for field, row in (('visual_a', a), ('visual_b', b)):
            assert r[field] == '; '.join(f'{k}={row[k]}' for k in
                   ('leaves', 'roots', 'reproductive', 'architecture', 'uncertainty'))
    result = {'status': 'PASS', 'pages': 9, 'repeated_heads': 4,
              'all_same_head_pairs': 6, 'visual_sha256': sha(BASE / 'artifacts/BLIND_VISUAL.tsv'),
              'source_sha256': sha(BASE / 'artifacts/SOURCE.tsv'),
              'pair_sha256': sha(BASE / 'artifacts/PAIR_CENSUS.tsv'),
              'scope': 'structural/provenance checks only; visual judgments not machine-verified'}
    path = BASE / 'artifacts/VALIDATION.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS 9 pages, 4 heads, 6 fixed pairs')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
