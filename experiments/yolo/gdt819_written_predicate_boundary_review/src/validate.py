#!/usr/bin/env python3
"""Independent source/metadata reproduction; no glyph or meaning validation."""
import argparse
import copy
import csv
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
PAGES = ['f76r', 'f77r', 'f81r']
TARGETS = ['f76r.23', 'f77r.12', 'f77r.34', 'f77r.35', 'f81r.19']
SPANS = [['f76r', 1, 38], ['f77r', 9, 24], ['f77r', 25, 37], ['f81r', 16, 31]]
EDITIONS = {'ZL3b': 'zl3b_clean', 'IT2a': 'it2a_clean', 'RF1b': 'rf1b_clean'}
META = ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean', 'ivtff_raw']
GCOLS = ['source_group_id', 'edition', 'locus', 'page', 'source_group_index', 'source_group_count',
         'paragraph_start', 'paragraph_end', 'left_separator', 'right_separator', 'ivtff_group_raw',
         'clean_ascii_fragments', 'clean_ascii_fragment_count', 'legacy_surface_positions_1based', 'legacy_mapping_status']
ATLAS = 'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
CANVASES = {'f76r': ('1006210', 2793, 3769), 'f77r': ('1006212', 2793, 3752), 'f81r': ('1006220', 2776, 3737)}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def enc(value):
    return json.dumps(value, ensure_ascii=False)


def exact(actual, expected, message):
    require(actual == expected, message)


def rejects(actual, expected):
    try:
        exact(actual, expected, 'Deliberately corrupted fixture')
    except ValueError:
        return True
    return False


def read_table(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def query(path, columns, count):
    command = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
    for page in PAGES:
        command += ['--allow', page]
    command += ['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    stats = [json.loads(s[12:]) for s in result.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    parser = csv.DictReader(io.StringIO(result.stdout), delimiter='\t')
    require(parser.fieldnames == columns and len(stats) == 1, 'Guard schema/stats')
    rows = list(parser)
    require(len(rows) == stats[0]['selected'] == count and {r['page'] for r in rows} == set(PAGES), 'Guard coverage')
    return rows, dict(command=command, stats=stats[0], projection_sha256=hashlib.sha256(result.stdout.encode()).hexdigest())


def legacy_fragments(raw):
    raw = re.sub(r'\[([^:\]]+)(?::[^\]]*)?\]', lambda m: m[1], raw)
    raw = re.sub(r'\{[^}]*\}', '', raw)
    raw = re.sub(r'<[^>]*>', ' ', raw).translate(str.maketrans('', '', "?!*'"))
    return [word for part in re.split(r'[\s.,;:=/\\|+\-]+', raw)
            if (word := re.sub('[^A-Za-z]', '', part).lower())]


def source_raw(groups):
    marks = {'DEFINITE_SPACE': '.', 'UNCERTAIN_SMALL_SPACE': ',',
             'DRAWING_INTERRUPTION': '<->', 'DRAWING_INTERRUPTION_UNALIGNED': '<~>'}
    require(groups[0]['left_separator'] == 'LINE_START' and groups[-1]['right_separator'] == 'LINE_END', 'Group endpoints')
    text, position = '', 1
    for i, group in enumerate(groups):
        require(int(group['source_group_index']) == i + 1 and int(group['source_group_count']) == len(groups), 'Group numbering')
        require(group['source_group_id'] == f"{group['edition']}|{group['locus']}|G{i+1:03}", 'Group identity')
        require(group['paragraph_start'] == group['paragraph_end'] == '0', 'Target paragraph flags')
        fragments = legacy_fragments(group['ivtff_group_raw'])
        require(fragments == group['clean_ascii_fragments'].split() and len(fragments) == int(group['clean_ascii_fragment_count']), 'Entity cleaner accounting')
        require(group['legacy_surface_positions_1based'] == ','.join(map(str, range(position, position + len(fragments)))), 'Fragment positions')
        state = 'ZERO_ASCII_FRAGMENT' if not fragments else 'ONE_ASCII_FRAGMENT' if len(fragments) == 1 else 'MULTI_ASCII_FRAGMENT'
        require(group['legacy_mapping_status'] == state, 'Fragment status')
        position += len(fragments)
        if i:
            require(groups[i-1]['right_separator'] == group['left_separator'], 'Separator adjacency')
            text += marks[group['left_separator']]
        text += group['ivtff_group_raw']
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only validation')
    args = parser.parse_args()
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    require(spec == dict(experiment_id='GDT819', pages=PAGES, targets=TARGETS, paragraphs=SPANS,
        source_atlas=ATLAS, source_spec='experiments/semantic_assumptions/SOURCE_SEPARATOR_TRANSCRIPTION_SPEC.md',
        editions=EDITIONS, sealed_data=['f84', 'f84r'], extended_glyph_expansion=False,
        historical_sources_modified=False, new_admissions=0, dictionary_changed=False, meanings_validated=False), 'Fixed design')
    admissions = read_table(ROOT / 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv')
    require(set(PAGES) <= {r['source_selector'] for r in admissions}, 'Unadmitted page')
    lines, guard1 = query('transcription/voynich_zl3b_lines.tsv', META, 137)
    cross, guard2 = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus', *EDITIONS.values()], 137)
    atlas, guard3 = query(ATLAS, GCOLS, 3296)
    by = {r['locus']: dict(r) for r in lines}
    require(len(by) == len(cross) == len({r['locus'] for r in cross}) == 137, 'Unique loci')
    for r in cross:
        require(r['locus'] in by and by[r['locus']]['page'] == r['page'] and by[r['locus']]['eva_clean'] == r['zl3b_clean'], 'Reader join')
        by[r['locus']].update(r)
    def record(r):
        return {k: r[k] for k in META if k != 'eva_clean'} | {'readings_json': enc({rd: r[rd] for rd in EDITIONS.values()})}
    expected = {'TARGETS.tsv': [record(by[t]) for t in TARGETS], 'BLOCKS.tsv': [],
                'PARAGRAPHS.tsv': [], 'INTERLEAVED_LABELS.tsv': [], 'NEIGHBORS.tsv': []}
    document = ['# GDT819 target paragraphs and separate interleaved labels', '',
                'Legacy clean readings below are for locus registration, NOT diplomatic group boundaries.',
                'GROUP_COMPARISON.tsv / SOURCE_GROUPS.tsv govern the five target source-group claims.', '']
    for page, first, last in SPANS:
        block = [by[f'{page}.{n}'] for n in range(first, last + 1)]
        prose = [r for r in block if r['kind'] == 'P']; labels = [r for r in block if r['kind'] == 'L']
        require(len(prose) + len(labels) == len(block), 'Unaccounted kind')
        require(prose[0]['paragraph_start'] == prose[-1]['paragraph_end'] == '1' and
                all(r['paragraph_start'] == '0' for r in prose[1:]) and all(r['paragraph_end'] == '0' for r in prose[:-1]), 'Whole P boundaries')
        bid = f'{page}.{first}--{page}.{last}'
        expected['BLOCKS.tsv'].append(dict(block_id=bid, page=page, first=prose[0]['locus'], last=prose[-1]['locus'],
            prose_loci=len(prose), interleaved_label_loci=enc([r['locus'] for r in labels])))
        for kind, rows in [('PARAGRAPHS.tsv', prose), ('INTERLEAVED_LABELS.tsv', labels)]:
            expected[kind] += [dict(block_id=bid, **record(r)) for r in rows]
        document += ['## ' + bid, '']
        for r in block:
            document += [f"{r['locus']} [{r['kind']}] ZL clean: `{r['zl3b_clean']}`"]
            document += [rd + ': `' + r[rd] + '`' for rd in ['it2a_clean', 'rf1b_clean'] if r[rd] != r['zl3b_clean']] + ['']
        for i, r in enumerate(prose):
            if r['locus'] in TARGETS:
                n = int(r['locus'].split('.')[1]); previous = by[f'{page}.{n-1}']
                expected['NEIGHBORS.tsv'].append(dict(page=page, locus=r['locus'], block_id=bid,
                    prev_prose=prose[i-1]['locus'], next_prose=prose[i+1]['locus'], prev_record=previous['locus'],
                    prev_record_kind=previous['kind'], next_record=f'{page}.{n+1}'))
    groups = [r for r in atlas if r['locus'] in TARGETS]
    comparisons = []
    for target in TARGETS:
        for edition, reader in EDITIONS.items():
            selected = sorted([r for r in groups if r['locus'] == target and r['edition'] == edition], key=lambda r: int(r['source_group_index']))
            raw = source_raw(selected)
            if edition == 'ZL3b':
                require(raw == by[target]['ivtff_raw'], 'Independent ZL raw reconstruction')
            fragments = [w for r in selected for w in legacy_fragments(r['ivtff_group_raw'])]
            comparisons.append(dict(page=by[target]['page'], locus=target, edition=edition, source_group_count=len(selected),
                source_groups_json=enc([r['ivtff_group_raw'] for r in selected]), separators_json=enc([r['right_separator'] for r in selected[:-1]]),
                atlas_ascii_fragments_json=enc(fragments), current_clean=by[target][reader], current_clean_token_count=len(by[target][reader].split()),
                atlas_flat_equals_current=int(fragments == by[target][reader].split())))
    issues = [r for r in groups if int(r['clean_ascii_fragment_count']) != 1 or '@' in r['ivtff_group_raw'] or
              'UNCERTAIN_SMALL_SPACE' in (r['left_separator'], r['right_separator'])]
    expected.update({'SOURCE_GROUPS.tsv': groups, 'GROUP_COMPARISON.tsv': comparisons, 'ISSUE_GROUPS.tsv': issues})
    expected = {name: [{k: str(v) for k, v in row.items()} for row in rows] for name, rows in expected.items()}
    for name, rows in expected.items():
        exact(read_table(EXP / 'artifacts' / name), rows, 'Exact source reproduction: ' + name)
    require((EXP / 'artifacts/FULL_READER.md').read_text() == '\n'.join(document).rstrip() + '\n', 'Complete reader reproduction')
    require([len(expected[n]) for n in ['PARAGRAPHS.tsv', 'INTERLEAVED_LABELS.tsv', 'SOURCE_GROUPS.tsv', 'GROUP_COMPARISON.tsv', 'ISSUE_GROUPS.tsv']] == [74, 9, 129, 15, 16], 'Packet counts')
    result = dict(experiment_id='GDT819', status='SOURCE_GROUP_AND_VISUAL_BOUNDARIES_NOT_MEANINGS', pages=PAGES, targets=TARGETS,
        source_loci=137, atlas_projected_groups=3296, target_rows=5, paragraph_blocks=4, prose_loci=74, interleaved_labels=9,
        target_source_groups=129, comparisons=15, issue_groups=16, atlas_flat_current_matches=sum(r['atlas_flat_equals_current'] for r in comparisons),
        guarded_queries=[guard1, guard2, guard3], source_group_not_authorial_word=True, extended_glyph_expansion=False,
        historical_sources_modified=False, new_admissions=0, dictionary_changed=False, confirmed_lexemes=0,
        confirmed_plaintext_clauses=0, meanings_validated=False, sealed_data=['f84', 'f84r'])
    require(result['atlas_flat_current_matches'] == 15, 'Current cleaner correspondence')
    exact(json.loads((EXP / 'artifacts/RESULT.json').read_text()), result, 'Result provenance/ceiling')
    canvases = json.loads((EXP / 'src/CANVASES.json').read_text())
    require(len(canvases) == 3 and {c['page'] for c in canvases} == set(PAGES), 'Canvas coverage')
    for c in canvases:
        ident, width, height = CANVASES[c['page']]
        require(c == dict(page=c['page'], canvas_label=c['page'][1:], canvas_id='https://collections.library.yale.edu/manifests/oid/2002046/canvas/' + ident,
                width=width, height=height, image_id=ident, service_url='https://collections.library.yale.edu/iiif/2/' + ident), 'Public canvas metadata')
    image_fields = ['image_key', 'page', 'image_id', 'canvas_width', 'canvas_height', 'region_x', 'region_y', 'region_width', 'region_height', 'url', 'width', 'height', 'sha256']
    images = []
    for page, count in zip(PAGES, [3, 7, 3]):
        rows = read_table(EXP / ('src/' + page.upper() + '_IMAGES.tsv'))
        require(len(rows) == count and all(list(r) == image_fields and r['page'] == page for r in rows), 'Image schema/coverage')
        ident, cw, ch = CANVASES[page]
        for r in rows:
            x, y, w, h, ow, oh = [int(r[k]) for k in ['region_x', 'region_y', 'region_width', 'region_height', 'width', 'height']]
            require(r['image_id'] == ident and (int(r['canvas_width']), int(r['canvas_height'])) == (cw, ch), 'Image identity')
            require(0 <= x < cw and 0 <= y < ch and 0 < w <= cw-x and 0 < h <= ch-y and ow > 0 and oh > 0, 'Region bounds')
            prefix = 'https://collections.library.yale.edu/iiif/2/' + ident + '/'
            require(r['url'].startswith(prefix) and r['url'].endswith('/0/default.jpg'), 'Public unmodified image URL')
            region, size, rotation, quality = r['url'][len(prefix):].split('/')
            require(region == ','.join(map(str, [x, y, w, h])) or region == 'full' and [x, y, w, h] == [0, 0, cw, ch], 'URL region')
            require((size == 'full' and (ow, oh) == (w, h)) or (size == f'{ow},' and ow <= w and abs(oh - h*ow/w) <= 1), 'Derivative dimensions')
            require(re.fullmatch('[0-9a-f]{64}', r['sha256']) is not None, 'SHA256 format')
        images += rows
    require(len({r['image_key'] for r in images}) == 13, 'Unique image keys')
    mutations = {}
    cases = [('entity_split', 'RF1b|f77r.35|G007', 'che.aiin'),
             ('entity_to_d', 'RF1b|f77r.35|G007', 'chedaiin'),
             ('qotaiin_merge', 'RF1b|f77r.35|G006', 'qokaiin'),
             ('IT_shedaiin_smoothed', 'IT2a|f77r.12|G004', 'chedaiin')]
    for label, identity, replacement in cases:
        changed = copy.deepcopy(expected['SOURCE_GROUPS.tsv'])
        next(r for r in changed if r['source_group_id'] == identity)['ivtff_group_raw'] = replacement
        mutations[label] = rejects(changed, expected['SOURCE_GROUPS.tsv'])
    changed = copy.deepcopy(expected['SOURCE_GROUPS.tsv'])
    changed.remove(next(r for r in changed if r['source_group_id'] == 'ZL3b|f76r.23|G004'))
    mutations['deleted_actual_doublet'] = rejects(changed, expected['SOURCE_GROUPS.tsv'])
    mutations['glyph_truth_promoted'] = rejects(dict(result, extended_glyph_expansion=True, confirmed_lexemes=1), result)
    require(len(mutations) == 6 and all(mutations.values()), 'Mutation rejection')
    validation = dict(experiment_id='GDT819', status='PASS_INDEPENDENT_SOURCE_METADATA_RECONSTRUCTION',
        source_loci=137, target_source_groups=129, complete_prose_loci=74, interleaved_labels=9, comparisons=15,
        public_image_metadata_rows=13, guarded_queries=[guard1, guard2, guard3], negative_controls_rejected=mutations,
        source_groups_not_linguistic_words=True, legacy_inputs_modified=False, glyph_truth_validated=False,
        image_bytes_validated=False, meanings_validated=False, runner_imported_or_called=False,
        checked_source_metadata_hashes={n: hashlib.sha256((EXP / 'src' / n).read_bytes()).hexdigest()
            for n in ['SPEC.json', 'CANVASES.json', 'F76R_IMAGES.tsv', 'F77R_IMAGES.tsv', 'F81R_IMAGES.tsv']},
        checked_artifact_hashes={n: hashlib.sha256((EXP / 'artifacts' / n).read_bytes()).hexdigest() for n in [*expected, 'FULL_READER.md', 'RESULT.json']})
    output = json.dumps(validation, indent=2, sort_keys=True) + '\n'
    target = EXP / 'artifacts/VALIDATION.json'
    if args.check:
        require(target.read_text() == output, 'Stored validation differs')
    else:
        target.write_text(output)
    print(enc({'status': validation['status'], 'negative_controls': len(mutations), 'meanings_validated': False}))


if __name__ == '__main__':
    main()
