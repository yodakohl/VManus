#!/usr/bin/env python3
"""Bounded source-native context, not a semantic decoder or corpus census."""
import argparse
import csv
import json
import runpy
from collections import Counter
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
BASE = runpy.run_path(str(ROOT / 'experiments/yolo/gdt819_written_predicate_boundary_review/src/run.py'))
query, enc, table, require = [BASE[k] for k in ['query', 'enc', 'table', 'require']]
META, GCOLS = BASE['META'], BASE['GROUP_COLS']
MARKS = {'DEFINITE_SPACE': '.', 'UNCERTAIN_SMALL_SPACE': ',',
         'DRAWING_INTERRUPTION': '<->', 'DRAWING_INTERRUPTION_UNALIGNED': '<~>'}


def read_table(path):
    with Path(path).open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def build():
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    pages = spec['pages']; editions = spec['editions']
    admissions = read_table(ROOT / 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv')
    admissions += read_table(ROOT / 'experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv')
    require(set(pages) <= {r['source_selector'] for r in admissions} and spec['sealed_data'] == ['f84', 'f84r'], 'Admission')
    selected = {}; origins = {}
    for path in spec['selection_inputs']:
        for row in read_table(ROOT / path):
            require(row['page'] in pages, 'Cached selection outside scope')
            if row['locus'] in selected:
                require(all(selected[row['locus']][k] == row[k] for k in ['page', 'kind', 'paragraph_start', 'paragraph_end', 'readings_json']), 'Overlap disagreement')
            selected[row['locus']] = row
            origins.setdefault(row['locus'], []).append(path)
    require(len(selected) == spec['expected_selected_loci'] and {r['page'] for r in selected.values()} == set(pages), 'Fixed union')
    lines, g1 = query('transcription/voynich_zl3b_lines.tsv', META, pages)
    cross, g2 = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus', *editions.values()], pages)
    atlas, g3 = query(spec['source_atlas'], GCOLS, pages)
    by = {r['locus']: dict(r) for r in lines}
    require(len(by) == len(lines) == len(cross) == len({r['locus'] for r in cross}), 'Unique source rows')
    for row in cross:
        require(row['locus'] in by and by[row['locus']]['eva_clean'] == row['zl3b_clean'], 'Cross join')
        by[row['locus']].update(row)
    order = sorted(selected, key=lambda loc: (selected[loc]['page'], int(loc.split('.')[1])))
    contexts = []
    for loc in order:
        source = by[loc]; old = selected[loc]
        require(all(source[k] == old[k] for k in ['page', 'kind', 'paragraph_start', 'paragraph_end']), 'Cache metadata')
        readings = {reader: source[reader] for reader in editions.values()}
        require(readings == json.loads(old['readings_json']), 'Cache clean readings')
        contexts.append({k: source[k] for k in META if k != 'eva_clean'} |
                        dict(readings_json=enc(readings), origins_json=enc(origins[loc])))
    groups = [r for r in atlas if r['locus'] in selected]
    by_group = {}
    for group in groups:
        by_group.setdefault((group['locus'], group['edition']), []).append(group)
    comparisons = []; native = {}
    for loc in order:
        for edition, reader in editions.items():
            group = sorted(by_group.get((loc, edition), []), key=lambda r: int(r['source_group_index']))
            require(group and [int(r['source_group_index']) for r in group] == list(range(1, len(group)+1)), 'Complete group indices')
            require(all(int(r['source_group_count']) == len(group) for r in group), 'Complete groups')
            require(group[0]['left_separator'] == 'LINE_START' and group[-1]['right_separator'] == 'LINE_END', 'Group endpoints')
            require(all(group[i]['right_separator'] == group[i+1]['left_separator'] for i in range(len(group)-1)), 'Group adjacency')
            by_group[loc, edition] = group
            raw = ''.join((MARKS[g['left_separator']] if i else '') + g['ivtff_group_raw'] for i, g in enumerate(group))
            native[loc, edition] = raw
            fragments = [w for g in group for w in g['clean_ascii_fragments'].split()]
            comparisons.append(dict(page=by[loc]['page'], locus=loc, edition=edition, source_group_count=len(group),
                raw_grouped_line=raw, ascii_fragment_count=len(fragments), current_clean_count=len(by[loc][reader].split()),
                flat_matches_current=int(fragments == by[loc][reader].split()),
                zero_fragment_groups=sum(g['clean_ascii_fragment_count'] == '0' for g in group),
                multi_fragment_groups=sum(int(g['clean_ascii_fragment_count']) > 1 for g in group)))
    block_map = {}
    for path in spec['block_inputs']:
        for old in read_table(ROOT / path):
            key = (old['page'], old['first'], old['last'])
            block_map[key] = dict(block_id=old['block_id'], page=old['page'], kind=old.get('kind', 'P'), first=old['first'], last=old['last'])
    blocks = sorted(block_map.values(), key=lambda b: (b['page'], int(b['first'].split('.')[1])))
    pairs = []
    def add_pair(left, right, kind, block_id='', skipped=()):
        if left['ivtff_group_raw'] != right['ivtff_group_raw']:
            return
        lg = by_group[left['locus'], left['edition']]; rg = by_group[right['locus'], right['edition']]
        li = int(left['source_group_index']) - 1; ri = int(right['source_group_index']) - 1
        pairs.append(dict(pair_id=left['source_group_id'] + '>>' + right['source_group_id'], edition=left['edition'],
            page=left['page'], pair_kind=kind, raw_group=left['ivtff_group_raw'], left_id=left['source_group_id'],
            right_id=right['source_group_id'], left_locus=left['locus'], right_locus=right['locus'],
            left_kind=by[left['locus']]['kind'], right_kind=by[right['locus']]['kind'],
            separator=left['right_separator'] if kind == 'WITHIN_RECORD' else 'PROSE_LINE_BREAK',
            block_id=block_id, intervening_labels_json=enc(list(skipped)),
            preceding_json=enc([g['ivtff_group_raw'] for g in lg[max(0, li-3):li]]),
            following_json=enc([g['ivtff_group_raw'] for g in rg[ri+1:ri+4]])))
    for loc in order:
        for edition in editions:
            group = by_group[loc, edition]
            for left, right in zip(group, group[1:]):
                add_pair(left, right, 'WITHIN_RECORD')
    for block in blocks:
        first = int(block['first'].split('.')[1]); last = int(block['last'].split('.')[1])
        stream = [by[f"{block['page']}.{n}"] for n in range(first, last+1)]
        require(all(r['locus'] in selected for r in stream), 'Incomplete selected block')
        if block['kind'] != 'P':
            continue
        prose = [r for r in stream if r['kind'] == 'P']
        require(prose[0]['paragraph_start'] == prose[-1]['paragraph_end'] == '1' and
                all(r['paragraph_start'] == '0' for r in prose[1:]) and all(r['paragraph_end'] == '0' for r in prose[:-1]), 'Whole paragraph')
        for left, right in zip(prose, prose[1:]):
            skipped = [r['locus'] for r in stream if int(left['locus'].split('.')[1]) < int(r['locus'].split('.')[1]) < int(right['locus'].split('.')[1])]
            require(all(by[loc]['kind'] == 'L' for loc in skipped), 'No skipped prose')
            for edition in editions:
                add_pair(by_group[left['locus'], edition][-1], by_group[right['locus'], edition][0], 'WITHIN_P_LINE_BREAK', block['block_id'], skipped)
    require(len({p['pair_id'] for p in pairs}) == len(pairs), 'No double-counted pair')
    doc = ['# GDT820 full source-group context reader', '',
        'Periods/commas/drawing markers are source separators; @entities stay opaque.',
        'Source groups are not decoded linguistic words. No line-end sentence rule.', '']
    for loc in order:
        row = by[loc]
        doc += [f"## {loc} [{row['kind']}] P-start={row['paragraph_start']} P-end={row['paragraph_end']}", '', 'ZL3b: `' + native[loc, 'ZL3b'] + '`']
        for edition in ['IT2a', 'RF1b']:
            doc += [edition + (': same source-group line as ZL3b.' if native[loc, edition] == native[loc, 'ZL3b'] else ': `' + native[loc, edition] + '`')]
        doc += ['']
    result = dict(experiment_id='GDT820', status='BOUNDED_GROUPED_REPETITION_CONTEXT_NOT_TRANSLATION', pages=pages,
        selected_loci=len(contexts), selected_kinds=dict(Counter(r['kind'] for r in contexts)), whole_blocks=len(blocks),
        complete_P_blocks=sum(b['kind'] == 'P' for b in blocks), source_groups=len(groups), comparisons=len(comparisons),
        flat_current_matches=sum(r['flat_matches_current'] for r in comparisons),
        zero_fragment_groups=sum(r['clean_ascii_fragment_count'] == '0' for r in groups),
        multi_fragment_groups=sum(int(r['clean_ascii_fragment_count']) > 1 for r in groups),
        pair_reading_rows=len(pairs), pair_kinds=dict(Counter(p['pair_kind'] for p in pairs)),
        per_edition_pairs=dict(Counter(p['edition'] for p in pairs)),
        guarded_queries=[g1, g2, g3], candidate_enriched_not_corpus_census=True, raw_identity_not_word_identity=True,
        extended_glyph_expansion=False, dictionary_changed=False, new_admissions=0,
        meanings_validated=False, confirmed_lexemes=0, confirmed_plaintext_clauses=0, sealed_data=['f84', 'f84r'])
    return {'CONTEXTS.tsv': table(contexts), 'BLOCKS.tsv': table(blocks), 'SOURCE_GROUPS.tsv': table(groups),
            'GROUP_COMPARISON.tsv': table(comparisons), 'REPETITIONS.tsv': table(pairs),
            'FULL_READER.md': '\n'.join(doc).rstrip()+'\n', 'RESULT.json': json.dumps(result, indent=2, sort_keys=True)+'\n'}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    for name, content in build().items():
        path = EXP / 'artifacts' / name
        if args.check:
            require(path.read_text() == content, 'Replay differs: ' + name)
        else:
            path.write_text(content)
    print('GDT820 grouped packet PASS (source representation only)')


if __name__ == '__main__':
    main()
