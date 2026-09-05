#!/usr/bin/env python3
"""Bounded cached whole-qol trial; no raw corpus access or semantic score."""
import argparse
import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]


def read(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def table(rows, columns=None):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=columns or list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def enc(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def build():
    spec = json.loads((EXP/'src/SPEC.json').read_text())
    assert spec['whole'] == 'qol' and spec['gloss_de'] == 'daraus?'
    assert spec['sealed_data'] == ['f84', 'f84r']
    prior = ROOT/spec['prior']/'artifacts'
    groups, contexts, blocks, old = [read(prior/name) for name in
        ['SOURCE_GROUPS.tsv', 'CONTEXTS.tsv', 'BLOCKS.tsv', 'TRIALS.tsv']]
    assert len(groups) == 8391 and len(contexts) == 320 and len(old) == 1920
    assert all(not r['page'].startswith('f84') for r in groups + contexts + blocks)
    hits = [g for g in groups if g['ivtff_group_raw'] == 'qol']
    targets = {g['locus'] for g in hits}
    by = {r['locus']: r for r in contexts}
    selected_blocks = {by[l]['block_id'] for l in targets}
    assert set(spec['core_blocks']) <= selected_blocks
    selected = [r for r in contexts if r['block_id'] in selected_blocks]
    selected_groups = defaultdict(list)
    for g in groups:
        selected_groups[g['locus'], g['edition']].append(g)
    trials, neighbourhoods = [], []
    for r in old:
        if r['locus'] not in targets:
            continue
        words, literal = json.loads(r['source_groups_json']), json.loads(r['literal_json'])
        for i, word in enumerate(words):
            if word == 'qol':
                assert literal[i] == '[qol]'
                literal[i] = spec['gloss_de']
        trials.append(r | {'literal_json': enc(literal), 'confidence': spec['confidence']})
    for h in hits:
        vector = sorted(selected_groups[h['locus'], h['edition']], key=lambda g: int(g['source_group_index']))
        i = int(h['source_group_index']) - 1
        neighbourhoods.append(h | {'block_id': by[h['locus']]['block_id'],
            'left_group': vector[i-1]['ivtff_group_raw'] if i else 'LINE_START',
            'right_group': vector[i+1]['ivtff_group_raw'] if i+1 < len(vector) else 'LINE_END'})
    coverage = [b | {'core': int(b['block_id'] in spec['core_blocks']),
        'qol_loci_json': enc([l for l in json.loads(b['loci_json']) if l in targets]),
        'reading_scope': 'FULL_NATIVE_PARAGRAPH_ALL_THREE_ALTERNATES_IN_822_READER'}
        for b in blocks if b['block_id'] in selected_blocks]
    lookup = {(r['locus'], r['edition'], r['world']): r for r in trials}
    doc = ['# GDT823 exact-qol trial lines', '',
        'Full paragraphs: GDT822 artifacts/FULL_READER.md, blocks in COVERAGE.tsv.',
        'Only exact qol changes. Brackets are unknowns; question marks mark guesses.',
        'Dots/commas are source spaces, NOT clause punctuation. No antecedent assigned.', '']
    for c in contexts:
        loc = c['locus']
        if loc not in targets:
            continue
        doc += ['## '+loc+' ('+c['block_id']+')', '']
        for edition in ['ZL3b', 'IT2a', 'RF1b']:
            a, b = [lookup[loc, edition, world] for world in ['ASCENT', 'LIGHTNESS']]
            doc.append(edition+': '+enc(json.loads(a['source_groups_json'])))
            doc.append('Separators: '+a['separators_json'])
            doc.append('ASCENT: '+' | '.join(json.loads(a['literal_json'])))
            doc.append('LIGHTNESS: '+('same literal vector' if a['literal_json'] == b['literal_json'] else ' | '.join(json.loads(b['literal_json']))))
        doc.append('')
    result = dict(experiment_id='GDT823', status='C0_SOURCE_ANAPHOR_POSSIBLE_REFERENTS_UNRESOLVED',
        cached_inventory_loci=len(contexts), cached_inventory_groups=len(groups),
        exact_qol_reader_groups=len(hits), exact_by_edition=dict(Counter(g['edition'] for g in hits)),
        target_loci=len(targets), target_pages=sorted({by[l]['page'] for l in targets}),
        complete_paragraphs=len(coverage), reread_loci=len(selected), reread_kinds=dict(Counter(r['kind'] for r in selected)),
        core_loci=sum(r['block_id'] in spec['core_blocks'] for r in selected), literal_rows=len(trials),
        substituted_positions_two_worlds=2*len(hits), all39_qol_census=False,
        immediately_before_chedy_reader_groups=sum(r['right_group'] == 'chedy' for r in neighbourhoods),
        immediately_after_chedy_reader_groups=sum(r['left_group'] == 'chedy' for r in neighbourhoods),
        new_admissions=0, new_images=0, dictionary_changed=False, meanings_validated=False,
        confirmed_lexemes=0, confirmed_clauses=0, sealed_data=['f84','f84r'])
    return {'EXACT_HITS.tsv': table(neighbourhoods), 'COVERAGE.tsv': table(coverage),
        'TRIALS.tsv': table(trials), 'READER.md': '\n'.join(doc).rstrip()+'\n',
        'RESULT.json': json.dumps(result, indent=2, sort_keys=True)+'\n'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, content in build().items():
        path = EXP/'artifacts'/name
        if args.check:
            assert path.read_text() == content, name
        else:
            path.write_text(content)
    print('GDT823 bounded source-anaphor trial reproduced; meanings unvalidated')


if __name__ == '__main__':
    main()
