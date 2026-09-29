#!/usr/bin/env python3
"""Reproducible join of a frozen image-only inventory and all repeated heads."""
import csv
import itertools
from pathlib import Path


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / 'AGENTS.md').is_file() and (candidate / '.git').exists():
            return candidate
    raise RuntimeError('repository root not found')


ROOT = repo_root(Path(__file__).resolve())
BASE = ROOT / 'experiments/yolo/gdt1088_repeated_head_visual_owner_audit'
HEADS = ROOT / 'experiments/yolo/gdt1070_first_head_collision_capacity/artifacts/HEAD_MULTIPLICITIES.tsv'
WANT = {
    'kooiin': ('f2v', 'f29v'),
    'o': ('f42r', 'f56r'),
    'pchor': ('f19r', 'f21r', 'f52v'),
    'tshor': ('f15r', 'f53v'),
}
FIELDS = ('head', 'folio_a', 'folio_b', 'visual_a', 'visual_b', 'same_taxon',
          'shared_specific_organ', 'conflicts', 'rationale')


def rows(path: Path):
    with path.open(newline='') as file:
        return list(csv.DictReader(file, delimiter='\t'))


def visual_text(row):
    return '; '.join(f'{key}={row[key]}' for key in
                     ('leaves', 'roots', 'reproductive', 'architecture', 'uncertainty'))


def main() -> int:
    actual = {r['head_surface']: tuple(r['pages'].split(','))
              for r in rows(HEADS) if int(r['multiplicity']) > 1}
    if {k: set(v) for k, v in actual.items()} != {k: set(v) for k, v in WANT.items()}:
        raise ValueError(f'GDT1070 repeated-head roster changed: {actual!r}')
    expected = {(head, a, b) for head, pages in WANT.items()
                for a, b in itertools.combinations(pages, 2)}
    visuals = {r['folio']: r for r in rows(BASE / 'artifacts/BLIND_VISUAL.tsv')}
    sources = {r['folio']: r for r in rows(BASE / 'artifacts/SOURCE.tsv')}
    pages = {f for group in WANT.values() for f in group}
    if len(visuals) != 9 or set(visuals) != set(sources) or set(visuals) != pages:
        raise ValueError('exact nine-page image scope mismatch')
    assessments = rows(BASE / 'src/ASSESSMENTS.tsv')
    judged = {(r['head'], r['folio_a'], r['folio_b']): r for r in assessments}
    if len(judged) != 6 or set(judged) != expected:
        raise ValueError('all six fixed pair assessments required')
    out = BASE / 'artifacts/PAIR_CENSUS.tsv'
    with out.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for head in sorted(WANT):
            for a, b in itertools.combinations(WANT[head], 2):
                assessment = judged[(head, a, b)]
                if assessment['same_taxon'] not in {'YES', 'NO', 'UNDECIDABLE'} or assessment['shared_specific_organ'] not in {'YES', 'NO', 'UNDECIDABLE'}:
                    raise ValueError(f'bad assessment decision {head} {a} {b}')
                writer.writerow({'head': head, 'folio_a': a, 'folio_b': b,
                    'visual_a': visual_text(visuals[a]), 'visual_b': visual_text(visuals[b]),
                    'same_taxon': assessment['same_taxon'],
                    'shared_specific_organ': assessment['shared_specific_organ'],
                    'conflicts': assessment['conflicts'], 'rationale': assessment['rationale']})
    print(out.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
