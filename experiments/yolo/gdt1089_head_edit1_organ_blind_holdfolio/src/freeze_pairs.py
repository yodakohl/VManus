#!/usr/bin/env python3
"""Recreate the fixed pre-image one-edit roster and matched-control pages."""
import csv
import itertools
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'experiments/yolo/gdt1089_head_edit1_organ_blind_holdfolio/src'
HEADS = ROOT / 'experiments/yolo/gdt1070_first_head_collision_capacity/artifacts/HEAD_MULTIPLICITIES.tsv'
A = ROOT / 'experiments/yolo/gdt1087_botanical_blind_name_audit/artifacts/BLIND_VISUAL.tsv'
B = ROOT / 'experiments/yolo/gdt1088_repeated_head_visual_owner_audit/artifacts/BLIND_VISUAL.tsv'


def read(path):
    with path.open(newline='') as file:
        return list(csv.DictReader(file, delimiter='\t'))


def write(name, fields, rows):
    with (BASE / name).open('w', newline='') as file:
        writer = csv.writer(file, delimiter='\t', lineterminator='\n')
        writer.writerow(fields)
        writer.writerows(rows)


def edit_distance(x, y):
    previous = list(range(len(y) + 1))
    for i, letter in enumerate(x, 1):
        current = [i]
        for j, other in enumerate(y, 1):
            current.append(min(previous[j] + 1, current[-1] + 1,
                               previous[j - 1] + (letter != other)))
        previous = current
    return previous[-1]


def folio_number(folio):
    return int(re.match(r'f(\d+)', folio).group(1))


def main():
    heads = {folio: row['head_surface'] for row in read(HEADS)
             for folio in row['pages'].split(',')}
    if len(heads) != 89:
        raise ValueError('GDT1070 roster changed')
    old = {row['folio'] for path in (A, B) for row in read(path)}
    if len(old) != 29:
        raise ValueError('old visual union changed')
    pairs = sorted((a, b, heads[a], heads[b])
                   for a, b in itertools.combinations(sorted(heads), 2)
                   if min(len(heads[a]), len(heads[b])) >= 4
                   and edit_distance(heads[a], heads[b]) == 1)
    if len(pairs) != 25:
        raise ValueError('one-edit population changed')
    pages = sorted((old | {f for a, b, _, _ in pairs for f in (a, b)}) & set(heads))
    new = sorted(set(pages) - old - {'f6v'})
    if len(pages) != 38 or len(new) != 11:
        raise ValueError('image admission population changed')
    write('FIXED_EDIT1_PAIRS.tsv', ['folio_a', 'folio_b', 'head_a', 'head_b', 'newly_covered'],
          [(a, b, x, y, int(a not in old or b not in old)) for a, b, x, y in pairs])
    write('BLIND_IMAGE_LIST.tsv', ['folio'], [(f,) for f in pages])
    write('NEW_IMAGE_ADMISSIONS.tsv', ['folio', 'purpose'],
          [(f, 'whole-plant architecture for preselected edit1 test') for f in new])
    controls = []
    for a, b, x, y in pairs:
        distance = abs(folio_number(a) - folio_number(b))
        candidates = [c for c in pages if c not in (a, b)
                      and min(len(x), len(heads[c])) >= 4
                      and edit_distance(x, heads[c]) >= 3]
        c = min(candidates, key=lambda c: (
            abs(abs(folio_number(a) - folio_number(c)) - distance),
            abs(len(heads[c]) - len(y)), c))
        controls.append((a, b, c, x, y, heads[c], int(a not in old or b not in old)))
    write('FIXED_CONTROLS.tsv',
          ['anchor_folio', 'edit1_folio', 'control_folio', 'anchor_head',
           'edit1_head', 'control_head', 'newly_covered'], controls)
    print('89 heads; 25 one-edit pairs; 38 images; 11 new visual admissions; 25 controls')


if __name__ == '__main__':
    main()
