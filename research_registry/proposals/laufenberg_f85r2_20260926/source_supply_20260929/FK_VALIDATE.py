#!/usr/bin/env python3
"""Reproduce FK frozen artifact conservation, never infer or confirm meanings."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]


def main():
    checks = []

    def check(condition, label):
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    spec = json.loads((BASE / 'FK_DIAGNOSTIC_SPEC.json').read_text())
    for name, bound_hash in spec['inputs'].items():
        check(digest(BASE / name) == bound_hash, 'frozen ' + name)
    target = json.loads((BASE / 'FK_TARGET.json').read_text())
    author = json.loads((BASE / 'FK_AUTHOR.json').read_text())
    check(author['target_sha256'] == digest(BASE / 'FK_TARGET.json'), 'author target binding')
    for receipt in target['source_receipts']:
        check(digest(ROOT / receipt['path']) == receipt['sha256'], 'source ' + receipt['path'])
    owned = {f'f85r1.{i}' for i in range(1, 7)}
    raw_by_id, lines_by_key, edition_counts = {}, {}, Counter()
    for line in target['raw_lines']:
        check(line['locus'] in owned, 'owned ' + line['edition'] + line['locus'])
        columns = line['columns']
        groups = [dict(zip(columns, group, strict=True)) for group in line['groups']]
        lines_by_key[(line['edition'], line['locus'])] = groups
        for index, group in enumerate(groups, 1):
            gid = f"{line['edition']}|{line['locus']}|G{index:03d}"
            check(group['source_group_id'] == gid, 'raw id ' + gid)
            check(group['page'] == 'f85r1' and group['locus'] == line['locus'], 'raw owner ' + gid)
            check(gid not in raw_by_id, 'unique id ' + gid)
            raw_by_id[gid] = group
            edition_counts[line['edition']] += 1
    check(dict(edition_counts) == {'IT2a': 60, 'ZL3b': 61, 'RF1b': 61}, '182 raw groups')
    check(len(lines_by_key) == 18, '18 raw lines')
    for paragraph in target['native_paragraphs']:
        check(paragraph['edition'] in {'IT2a', 'ZL3b'}, 'native paragraph edition')
        for line in paragraph['lines']:
            raw = lines_by_key[(paragraph['edition'], line['locus'])]
            check(line['words'] == [g['ivtff_group_raw'] for g in raw], 'native words ' + line['locus'])
            check(line['source_ids'] == [g['source_group_id'] for g in raw], 'native ids ' + line['locus'])
    primary = [g for (ed, locus), groups in lines_by_key.items() if ed == 'IT2a' for g in groups]
    check(len(author['positions']) == 60, '60 contributions')
    repeated, by_surface = defaultdict(list), {}
    for number, (position, group) in enumerate(zip(author['positions'], primary, strict=True), 1):
        check(position['position'] == number and position['id'] == group['source_group_id'], 'primary order ' + str(number))
        check(position['raw_surface'] == group['ivtff_group_raw'], 'primary surface ' + str(number))
        check(all(position[key] == group[key] for key in ('left_separator', 'right_separator')), 'primary separators ' + str(number))
        check(''.join(position['segmentation']) == position['raw_surface'], 'segmentation bytes ' + str(number))
        repeated[position['raw_surface']].append((position['segmentation'], position['A_contribution'], position['B_contribution'], position['paid_kind']))
        by_surface[position['raw_surface']] = position
    for form, rows in repeated.items():
        check(all(row == rows[0] for row in rows), 'repeated contribution ' + form)
    check(len(repeated) == 51, '51 primary forms')
    inventories = {'roots': 'lexical_roots', 'whole_residuals': 'whole_form_residuals', 'grammar': 'grammar_rules', 'defaults': 'defaults'}
    for name, key in inventories.items():
        check(len(author[key]) == author['inventories_counts'][name] <= author['caps'][name], 'inventory ' + name)
    lexical_surfaces = [r['surface'] for key in ('lexical_roots', 'whole_form_residuals') for r in author[key]]
    check(len(lexical_surfaces) == len(set(lexical_surfaces)) == 42, '42 lexical inventory bindings')
    with (BASE / 'FK_CANDIDATE_TABLE.tsv').open(newline='') as stream:
        table = list(csv.DictReader(stream, delimiter='\t'))
    check(len(table) == 60, 'candidate table length')
    for row, position in zip(table, author['positions'], strict=True):
        check(row['source_group_id'] == position['id'] and row['segmentation'] == '+'.join(position['segmentation']), 'candidate table identity ' + position['id'])
        check(all(row[key] == position[key] for key in ('A_contribution', 'B_contribution', 'attachment_and_binding', 'raw_surface')), 'candidate table contributions ' + position['id'])
    with (BASE / 'FK_ALTERNATE_DIAGNOSTICS.tsv').open(newline='') as stream:
        alternate = list(csv.DictReader(stream, delimiter='\t'))
    check(len(alternate) == 182 and {r['source_group_id'] for r in alternate} == set(raw_by_id), 'alternate full conservation')
    summaries = defaultdict(Counter)
    for row in alternate:
        original = raw_by_id[row['source_group_id']]
        check(row['raw_surface'] == original['ivtff_group_raw'], 'alternate raw ' + row['source_group_id'])
        check(all(row[key] == original[key] for key in ('left_separator', 'right_separator')), 'alternate separators ' + row['source_group_id'])
        position = by_surface.get(row['raw_surface'])
        for key in ('A_contribution', 'B_contribution'):
            check(row[key] == (position[key] if position else ''), 'alternate exact projection ' + row['source_group_id'] + key)
        summaries[row['edition']]['groups'] += 1
        summaries[row['edition']]['exact_surface_assigned' if position else 'unassigned'] += 1
    result = {'status': 'FROZEN_ARTIFACT_CONSERVATION_PASS', 'check_count': len(checks), 'checks': checks, 'reader_diagnostics': {k: dict(v) for k, v in summaries.items()}, 'meaning_confirmed': False, 'semantic_composition_validated': False, 'independent_confirmation': 0, 'ceiling': spec['not_checked']}
    (BASE / 'FK_VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'check_count', 'reader_diagnostics', 'meaning_confirmed', 'semantic_composition_validated')}))


if __name__ == '__main__':
    main()
