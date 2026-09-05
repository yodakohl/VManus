#!/usr/bin/env python3
"""Independent bounded group reconstruction; synthetic boundaries are not evidence."""
import argparse
import copy
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
OLD = 'experiments/yolo/gdt818_fixed_material_container_relation/artifacts/'
PREV = 'experiments/yolo/gdt819_written_predicate_boundary_review/artifacts/'
INPUTS = [OLD + 'CONTEXTS.tsv', OLD + 'CONTINUATION_CONTEXTS.tsv', PREV + 'PARAGRAPHS.tsv', PREV + 'INTERLEAVED_LABELS.tsv']
BLOCK_INPUTS = [OLD + 'BLOCKS.tsv', PREV + 'BLOCKS.tsv']
PAGES = ['f31r', 'f66r', 'f67r2', 'f70v2', 'f72r3', 'f75r', 'f76r', 'f77r', 'f81r', 'f81v', 'f82r', 'f83r', 'f88v', 'f95v1']
EDITIONS = {'ZL3b': 'zl3b_clean', 'IT2a': 'it2a_clean', 'RF1b': 'rf1b_clean'}
META = ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean', 'ivtff_raw']
GCOLS = ['source_group_id', 'edition', 'locus', 'page', 'source_group_index', 'source_group_count', 'paragraph_start',
         'paragraph_end', 'left_separator', 'right_separator', 'ivtff_group_raw', 'clean_ascii_fragments',
         'clean_ascii_fragment_count', 'legacy_surface_positions_1based', 'legacy_mapping_status']
ATLAS = 'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
MARKS = {'DEFINITE_SPACE': '.', 'UNCERTAIN_SMALL_SPACE': ',', 'DRAWING_INTERRUPTION': '<->', 'DRAWING_INTERRUPTION_UNALIGNED': '<~>'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def enc(value):
    return json.dumps(value, ensure_ascii=False)


def exact(actual, expected):
    require(actual == expected, 'Independent reproduction differs')


def rejects(actual, expected):
    try:
        exact(actual, expected)
    except ValueError:
        return True
    return False


def table(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def query(path, columns, count):
    command = ['./vmanus-exp', 'query-tsv', path, '--selector', 'page']
    for page in PAGES:
        command += ['--allow', page]
    command += ['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    p = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    stats = [json.loads(s[12:]) for s in p.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    reader = csv.DictReader(io.StringIO(p.stdout), delimiter='\t')
    require(reader.fieldnames == columns and len(stats) == 1, 'Guard schema')
    rows = list(reader)
    require(len(rows) == stats[0]['selected'] == count and {r['page'] for r in rows} == set(PAGES), 'Guard coverage')
    return rows, dict(command=command, stats=stats[0], projection_sha256=hashlib.sha256(p.stdout.encode()).hexdigest())


def clean(raw):
    raw = re.sub(r'\[([^:\]]+)(?::[^\]]*)?\]', lambda m: m[1], raw)
    raw = re.sub(r'\{[^}]*\}', '', raw)
    raw = re.sub(r'<[^>]*>', ' ', raw).translate(str.maketrans('', '', "?!*'"))
    return [w for part in re.split(r'[\s.,;:=/\\|+\-]+', raw) if (w := re.sub('[^A-Za-z]', '', part).lower())]


def grouped_line(rows):
    require(rows and rows[0]['left_separator'] == 'LINE_START' and rows[-1]['right_separator'] == 'LINE_END', 'Group endpoints')
    raw, fragments, position = '', [], 1
    for i, row in enumerate(rows):
        require(int(row['source_group_index']) == i+1 and int(row['source_group_count']) == len(rows), 'Group coverage')
        require(row['source_group_id'] == f"{row['edition']}|{row['locus']}|G{i+1:03}", 'Group ID')
        require(all(row[k] == rows[0][k] for k in ['edition', 'locus', 'page', 'paragraph_start', 'paragraph_end']), 'Group metadata')
        words = clean(row['ivtff_group_raw'])
        exact(words, row['clean_ascii_fragments'].split())
        require(len(words) == int(row['clean_ascii_fragment_count']), 'Fragment count')
        state = 'ZERO_ASCII_FRAGMENT' if not words else 'ONE_ASCII_FRAGMENT' if len(words) == 1 else 'MULTI_ASCII_FRAGMENT'
        require(row['legacy_mapping_status'] == state and row['legacy_surface_positions_1based'] == ','.join(map(str, range(position, position+len(words)))), 'Loss accounting')
        if i:
            require(rows[i-1]['right_separator'] == row['left_separator'], 'Separator adjacency')
            raw += MARKS[row['left_separator']]
        raw += row['ivtff_group_raw']; fragments += words; position += len(words)
    return raw, fragments


def adjacent_prose(stream, selected):
    """Use complete source order; omitted P is not skipped, labels do not reset P."""
    previous = None; skipped = []
    for row in stream:
        if row['kind'] == 'L':
            skipped.append(row['locus']); continue
        if row['kind'] != 'P':
            previous = None; skipped = []; continue
        if previous and previous['page'] == row['page'] and previous['paragraph_end'] == row['paragraph_start'] == '0':
            if {previous['locus'], row['locus'], *skipped} <= selected:
                yield previous['locus'], row['locus'], list(skipped)
        previous = row; skipped = []


def same_raw(left, right):
    return left['ivtff_group_raw'] == right['ivtff_group_raw']


def equal_neighbors(rows):
    return [(a, b) for a, b in zip(rows, rows[1:]) if same_raw(a, b)]


def validate_ascent(core_groups, core_loci):
    """Separate POST annex; do not change core selection, dictionary or result."""
    base = {'qokaiin':'Luft?', 'qokain':'Wasser?', 'chedy':'wird?', 'sheedy':'wenn?', 'chedaiin':'ist?',
            'chealy':'kalt?', 'solkeey':'Dampf?', 'okaiin':'dessen?', 'daiin':'viel?'}
    phase = 'POST_GROUP_READING_C0_CONTINUATION'; confidence = 'C0_COMPLETION_MOTIVATED_NOT_LEXICAL_EVIDENCE'
    comparators = ['f76r.51','f82r.24']; pages = ['f66r','f76r','f77r','f82r']
    proposal = dict(phase=phase, whole='raiin', gloss_de='steigt?',
        sense='PHYSICAL_UPWARD_MOTION_NOT_INCREASE_HEATING_EVAPORATION_COPULA_OR_DESCENT',
        selection='ALL_EXACT_RAIIN_LOCI_IN_172_CORE_PLUS_TWO_PREVIOUSLY_KNOWN_SAL_RAIIN_COMPARATORS',
        comparators=comparators, base_exact_glosses=base, confidence=confidence,
        new_admissions=0, dictionary_changed=False, meanings_validated=False, sealed_data=['f84','f84r'])
    exact(json.loads((EXP/'src/ASCENT_TRIAL.json').read_text()), proposal)
    core = sorted({r['locus'] for r in core_groups if r['ivtff_group_raw']=='raiin'})
    exact(core, ['f66r.80','f77r.34'])
    targets = sorted(set(core+comparators))
    require(len(set(targets)-set(core_loci))==2 and len(set(targets)|set(core_loci))==174, 'Annex scope accounting')
    admitted = table(ROOT/'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv')
    require(set(pages)<={r['source_selector'] for r in admitted}, 'Annex admission')
    command = ['./vmanus-exp','query-tsv',ATLAS,'--selector','page']
    for page in pages: command += ['--allow',page]
    command += ['--columns',','.join(GCOLS),'--forbid-prefix','f84','--forbid-prefix','f84r']
    process = subprocess.run(command,cwd=ROOT,text=True,capture_output=True,check=True)
    stats = [json.loads(s[12:]) for s in process.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    reader = csv.DictReader(io.StringIO(process.stdout),delimiter='\t')
    require(reader.fieldnames==GCOLS and len(stats)==1, 'Annex guard schema')
    rows = list(reader)
    require(len(rows)==stats[0]['selected']==4570 and {r['page'] for r in rows}==set(pages), 'Annex guard coverage')
    guard = dict(command=command,stats=stats[0],projection_sha256=hashlib.sha256(process.stdout.encode()).hexdigest())
    selected = [r for r in rows if r['locus'] in targets]; trials = []; glosses = base | {'raiin':'steigt?'}
    for locus in targets:
        for edition in EDITIONS:
            groups = sorted([r for r in selected if r['locus']==locus and r['edition']==edition],key=lambda r:int(r['source_group_index']))
            grouped_line(groups)
            raw = [r['ivtff_group_raw'] for r in groups]; literal = [glosses.get(w,'['+w+']') for w in raw]
            require(len(literal)==len(raw)==len({r['source_group_id'] for r in groups}), 'Annex consume each group once')
            if locus=='f82r.24': require(raw.count('raiin')==literal.count('steigt?')==2, 'Both comparator raiin retained')
            if (locus,edition)==('f77r.34','RF1b'): require(raw[-1]=='@206;aiin' and literal[-1]=='[@206;aiin]' and raw.count('raiin')==0, 'Opaque RF variant')
            trials.append(dict(page=locus.split('.')[0],locus=locus,edition=edition,
                selection_reason='EXACT_CORE_RAIIN' if locus in core else 'KNOWN_SAL_RAIIN_COMPARATOR',
                source_group_ids_json=enc([r['source_group_id'] for r in groups]),source_groups_json=enc(raw),
                separators_json=enc([r['right_separator'] for r in groups[:-1]]),literal_trial_json=enc(literal),
                exact_raiin_count=raw.count('raiin'),confidence=confidence))
    require(len(trials)==12 and sum(r['exact_raiin_count'] for r in trials)==14, 'Annex exact occurrence counts')
    expected = [{k:str(v) for k,v in row.items()} for row in trials]
    exact(table(EXP/'artifacts/ASCENT_TRIALS.tsv'),expected)
    result = dict(experiment_id='GDT820',phase=phase,core_raiin_loci=core,comparator_loci=comparators,trial_loci=targets,
        trial_rows=12,exact_raiin_occurrences=14,added_records_outside_core=2,combined_unique_records=174,
        whole_comparator_paragraphs_read=False,all_raiin_in_admitted39=False,dictionary_changed=False,new_admissions=0,
        meanings_validated=False,confirmed_lexemes=0,confirmed_plaintext_clauses=0,guarded_query=guard)
    exact(json.loads((EXP/'artifacts/ASCENT_RESULT.json').read_text()),result)
    changed = copy.deepcopy(expected); rf = next(r for r in changed if (r['locus'],r['edition'])==('f77r.34','RF1b'))
    literal = json.loads(rf['literal_trial_json']); literal[-1]='steigt?'; rf['literal_trial_json']=enc(literal)
    negatives = {'opaque_entity_gloss_alias':rejects(changed,expected)}
    changed = copy.deepcopy(expected); zl = next(r for r in changed if (r['locus'],r['edition'])==('f82r.24','ZL3b'))
    literal = json.loads(zl['literal_trial_json']); second = [i for i,w in enumerate(json.loads(zl['source_groups_json'])) if w=='raiin'][1]
    literal.pop(second); zl['literal_trial_json']=enc(literal)
    negatives['second_raiin_omitted'] = rejects(changed,expected)
    require(all(negatives.values()),'Annex mutation rejection')
    return dict(status='PASS_INDEPENDENT_POST_ASCENT_SOURCE_LITERAL_DISPLAY',trial_loci=targets,trial_rows=12,exact_raiin_occurrences=14,
        combined_unique_records=174,whole_comparator_paragraphs_read=False,all_raiin_in_admitted39=False,meanings_validated=False,
        guarded_query=guard,negative_controls_rejected=negatives,
        artifact_sha256={n:hashlib.sha256((EXP/'artifacts'/n).read_bytes()).hexdigest() for n in ['ASCENT_TRIALS.tsv','ASCENT_RESULT.json']},
        proposal_sha256=hashlib.sha256((EXP/'src/ASCENT_TRIAL.json').read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    exact(spec, dict(experiment_id='GDT820', selection_inputs=INPUTS, block_inputs=BLOCK_INPUTS, pages=PAGES,
        expected_selected_loci=172, source_atlas=ATLAS, editions=EDITIONS, exact_raw_group_equality_only=True,
        cross_line_pairs='CONSECUTIVE_P_RECORDS_WITHIN_SAME_COMPLETE_SOURCE_PARAGRAPH', triple_policy='TWO_OVERLAPPING_ADJACENT_PAIRS',
        extended_glyph_expansion=False, dictionary_changed=False, meanings_validated=False, new_admissions=0, sealed_data=['f84', 'f84r']))
    admissions = table(ROOT / 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv')
    extra = table(ROOT / 'experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv')
    require(len(admissions) == 35 and len(extra) == 4 and set(PAGES) <= {r['source_selector'] for r in admissions+extra}, 'Admission')
    selected, origins = {}, defaultdict(list)
    for path in INPUTS:
        for row in table(ROOT / path):
            require(row['page'] in PAGES, 'Cached selection outside scope')
            if row['locus'] in selected:
                exact([selected[row['locus']][k] for k in ['page', 'kind', 'paragraph_start', 'paragraph_end', 'readings_json']],
                      [row[k] for k in ['page', 'kind', 'paragraph_start', 'paragraph_end', 'readings_json']])
            selected[row['locus']] = row; origins[row['locus']].append(path)
    require(len(selected) == 172 and sum(len(v)>1 for v in origins.values()) == 52, 'Deduplicated union')
    lines, g1 = query('transcription/voynich_zl3b_lines.tsv', META, 600)
    cross, g2 = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus', *EDITIONS.values()], 600)
    atlas, g3 = query(ATLAS, GCOLS, 10795)
    by = {r['locus']: dict(r) for r in lines}
    require(len(by) == len(cross) == len({r['locus'] for r in cross}) == 600, 'Unique source rows')
    for r in cross:
        require(r['locus'] in by and by[r['locus']]['page'] == r['page'] and by[r['locus']]['eva_clean'] == r['zl3b_clean'], 'Reader join')
        by[r['locus']].update(r)
    order = sorted(selected, key=lambda loc: (selected[loc]['page'], int(loc.split('.')[1])))
    contexts = []
    for loc in order:
        row = by[loc]; old = selected[loc]; readings = {rd: row[rd] for rd in EDITIONS.values()}
        require(all(row[k] == old[k] for k in ['page', 'kind', 'paragraph_start', 'paragraph_end']), 'Cache flags')
        exact(readings, json.loads(old['readings_json']))
        contexts.append({k: row[k] for k in META if k != 'eva_clean'} | dict(readings_json=enc(readings), origins_json=enc(origins[loc])))
    groups = [r for r in atlas if r['locus'] in selected]; grouped = defaultdict(list)
    for row in groups:
        grouped[row['locus'], row['edition']].append(row)
    require(len(groups) == 4734 and len(grouped) == 516, 'All-reader source-group coverage')
    comparisons, native, layout_annotations = [], {}, {}
    for loc in order:
        for edition, reader in EDITIONS.items():
            group = sorted(grouped[loc, edition], key=lambda r: int(r['source_group_index'])); grouped[loc, edition] = group
            raw, fragments = grouped_line(group); native[loc, edition] = raw
            if edition == 'ZL3b':
                original = by[loc]['ivtff_raw']; leading = re.match(r'^<![^>]*>', original)
                if leading: layout_annotations[loc] = leading[0]
                body = original[len(leading[0]):] if leading else original
                require(raw == body.replace('<%>', '').replace('<$>', ''), f'ZL raw mismatch {loc}')
                require(all(group[0][k] == by[loc][k] for k in ['page', 'paragraph_start', 'paragraph_end']), 'ZL paragraph flags')
            comparisons.append(dict(page=by[loc]['page'], locus=loc, edition=edition, source_group_count=len(group), raw_grouped_line=raw,
                ascii_fragment_count=len(fragments), current_clean_count=len(by[loc][reader].split()), flat_matches_current=int(fragments == by[loc][reader].split()),
                zero_fragment_groups=sum(not clean(g['ivtff_group_raw']) for g in group), multi_fragment_groups=sum(len(clean(g['ivtff_group_raw']))>1 for g in group)))
    block_map = {}
    for path in BLOCK_INPUTS:
        for row in table(ROOT / path):
            key = row['page'], row['first'], row['last']
            value = dict(block_id=row['block_id'], page=row['page'], kind=row.get('kind', 'P'), first=row['first'], last=row['last'])
            if key in block_map: exact(block_map[key], value)
            block_map[key] = value
    blocks = sorted(block_map.values(), key=lambda b: (b['page'], int(b['first'].split('.')[1])))
    pairs = []
    def pair(left, right, kind, block='', labels=()):
        if not same_raw(left, right): return
        lg = grouped[left['locus'], left['edition']]; rg = grouped[right['locus'], right['edition']]
        li, ri = int(left['source_group_index'])-1, int(right['source_group_index'])-1
        pairs.append(dict(pair_id=left['source_group_id']+'>>'+right['source_group_id'], edition=left['edition'], page=left['page'], pair_kind=kind,
            raw_group=left['ivtff_group_raw'], left_id=left['source_group_id'], right_id=right['source_group_id'], left_locus=left['locus'], right_locus=right['locus'],
            left_kind=by[left['locus']]['kind'], right_kind=by[right['locus']]['kind'], separator=left['right_separator'] if kind=='WITHIN_RECORD' else 'PROSE_LINE_BREAK',
            block_id=block, intervening_labels_json=enc(list(labels)), preceding_json=enc([g['ivtff_group_raw'] for g in lg[max(0,li-3):li]]),
            following_json=enc([g['ivtff_group_raw'] for g in rg[ri+1:ri+4]])))
    for loc in order:
        for edition in EDITIONS:
            for a, b in equal_neighbors(grouped[loc, edition]): pair(a, b, 'WITHIN_RECORD')
    for block in blocks:
        stream = [by[f"{block['page']}.{n}"] for n in range(int(block['first'].split('.')[1]), int(block['last'].split('.')[1])+1)]
        require(all(r['locus'] in selected for r in stream), 'Complete selected block')
        if block['kind'] != 'P': continue
        prose = [r for r in stream if r['kind']=='P']
        require(prose[0]['paragraph_start'] == prose[-1]['paragraph_end'] == '1' and all(r['paragraph_start']=='0' for r in prose[1:]) and
                all(r['paragraph_end']=='0' for r in prose[:-1]) and all(r['kind'] in ['P','L'] for r in stream), 'Complete P flags')
        for left, right, skipped in adjacent_prose(stream, set(selected)):
            for edition in EDITIONS: pair(grouped[left,edition][-1], grouped[right,edition][0], 'WITHIN_P_LINE_BREAK', block['block_id'], skipped)
    require(len(pairs) == len({p['pair_id'] for p in pairs}) == 67, 'Unique raw repeated pairs')
    expected = {'CONTEXTS.tsv': contexts, 'BLOCKS.tsv': blocks, 'SOURCE_GROUPS.tsv': groups, 'GROUP_COMPARISON.tsv': comparisons, 'REPETITIONS.tsv': pairs}
    expected = {name: [{k: str(v) for k,v in r.items()} for r in rows] for name,rows in expected.items()}
    for name, rows in expected.items(): exact(table(EXP / 'artifacts' / name), rows)
    doc = ['# GDT820 full source-group context reader', '', 'Periods/commas/drawing markers are source separators; @entities stay opaque.',
           'Source groups are not decoded linguistic words. No line-end sentence rule.', '']
    for loc in order:
        row = by[loc]; doc += [f"## {loc} [{row['kind']}] P-start={row['paragraph_start']} P-end={row['paragraph_end']}", '', 'ZL3b: `'+native[loc,'ZL3b']+'`']
        for edition in ['IT2a','RF1b']: doc += [edition+(': same source-group line as ZL3b.' if native[loc,edition]==native[loc,'ZL3b'] else ': `'+native[loc,edition]+'`')]
        doc += ['']
    exact((EXP/'artifacts/FULL_READER.md').read_text(), '\n'.join(doc).rstrip()+'\n')
    result = dict(experiment_id='GDT820', status='BOUNDED_GROUPED_REPETITION_CONTEXT_NOT_TRANSLATION', pages=PAGES, selected_loci=172,
        selected_kinds=dict(Counter(r['kind'] for r in contexts)), whole_blocks=len(blocks), complete_P_blocks=sum(b['kind']=='P' for b in blocks),
        source_groups=4734, comparisons=516, flat_current_matches=sum(r['flat_matches_current'] for r in comparisons),
        zero_fragment_groups=sum(not clean(r['ivtff_group_raw']) for r in groups), multi_fragment_groups=sum(len(clean(r['ivtff_group_raw']))>1 for r in groups),
        pair_reading_rows=67, pair_kinds=dict(Counter(p['pair_kind'] for p in pairs)), per_edition_pairs=dict(Counter(p['edition'] for p in pairs)),
        guarded_queries=[g1,g2,g3], candidate_enriched_not_corpus_census=True, raw_identity_not_word_identity=True, extended_glyph_expansion=False,
        dictionary_changed=False, new_admissions=0, meanings_validated=False, confirmed_lexemes=0, confirmed_plaintext_clauses=0, sealed_data=['f84','f84r'])
    require(result['flat_current_matches']==516 and result['zero_fragment_groups']==1 and result['multi_fragment_groups']==140, 'Loss counts')
    exact(json.loads((EXP/'artifacts/RESULT.json').read_text()), result)
    # These fixtures exercise this independent adjacency implementation, not the runner's API.
    left = dict(page='TEST',locus='TEST.1',kind='P',paragraph_start='1',paragraph_end='0')
    right = dict(page='TEST',locus='TEST.3',kind='P',paragraph_start='0',paragraph_end='1')
    label = dict(page='TEST',locus='TEST.2',kind='L',paragraph_start='0',paragraph_end='0')
    both = {left['locus'],right['locus']}; all_three = both | {label['locus']}
    positive_right = dict(right,locus='TEST.2')
    test_groups = {loc: [{'ivtff_group_raw':'TEST_WHOLE'}] for loc in all_three}
    def synthetic_breaks(stream, keep):
        return [(a,b,labs) for a,b,labs in adjacent_prose(stream,keep) if same_raw(test_groups[a][-1],test_groups[b][0])]
    synthetic = {'positive_exact_crossline_pair': synthetic_breaks([left,positive_right],{'TEST.1','TEST.2'})==[('TEST.1','TEST.2',[])],
        'label_does_not_reset_P': synthetic_breaks([left,label,right],all_three)==[('TEST.1','TEST.3',['TEST.2'])],
        'missing_P_blocks_jump': not synthetic_breaks([left,dict(label,kind='P'),right],both),
        'paragraph_boundary_blocks': not synthetic_breaks([dict(left,paragraph_end='1'),dict(right,paragraph_start='1')],both),
        'page_boundary_blocks': not synthetic_breaks([left,dict(right,page='OTHER')],both),
        'triple_retains_two_pairs': len(equal_neighbors([{'ivtff_group_raw':'X'}]*3))==2,
        'opaque_entity_not_d_alias': not equal_neighbors([{'ivtff_group_raw':'che@152;y'},{'ivtff_group_raw':'chedy'}])}
    negatives = {}
    for name, identity, raw in [('entity_expansion','RF1b|f77r.35|G007','chedaiin'), ('entity_split','RF1b|f77r.35|G007','che.aiin')]:
        changed = copy.deepcopy(expected['SOURCE_GROUPS.tsv']); next(r for r in changed if r['source_group_id']==identity)['ivtff_group_raw']=raw
        negatives[name] = rejects(changed, expected['SOURCE_GROUPS.tsv'])
    changed = [r for r in expected['SOURCE_GROUPS.tsv'] if r['source_group_id']!='ZL3b|f72r3.1|G015']
    negatives['zero_fragment_group_deleted'] = rejects(changed,expected['SOURCE_GROUPS.tsv'])
    negatives['actual_pair_deleted'] = rejects(expected['REPETITIONS.tsv'][1:],expected['REPETITIONS.tsv'])
    negatives['pair_counted_twice'] = rejects(expected['REPETITIONS.tsv']+[expected['REPETITIONS.tsv'][0]],expected['REPETITIONS.tsv'])
    negatives['false_crossline_pair'] = rejects(expected['REPETITIONS.tsv']+[dict(expected['REPETITIONS.tsv'][0],pair_kind='WITHIN_P_LINE_BREAK')],expected['REPETITIONS.tsv'])
    negatives['meaning_promoted'] = rejects(dict(result,meanings_validated=True),result)
    require(all(synthetic.values()) and all(negatives.values()), 'Synthetic/mutation controls')
    ascent_validation = validate_ascent(groups, set(selected))
    validation = dict(experiment_id='GDT820',status='PASS_INDEPENDENT_GROUPED_SOURCE_RECONSTRUCTION',selected_loci=172,source_groups=4734,
        reader_locus_comparisons=516,raw_repeat_reader_pairs=67,observed_crossline_pairs=0,synthetic_adjacency_checks=synthetic,
        negative_controls_rejected=negatives,guarded_queries=[g1,g2,g3],source_group_not_linguistic_word=True,runner_imported_or_called=False,
        leading_ZL_locus_annotations_preserved_in_CONTEXTS=layout_annotations,
        separate_post_ascent_annex=ascent_validation,
        synthetic_checks_cover_independent_validator_not_runner_API=True,meanings_validated=False,legacy_files_modified=False,
        artifact_sha256={n:hashlib.sha256((EXP/'artifacts'/n).read_bytes()).hexdigest() for n in [*expected,'FULL_READER.md','RESULT.json']},
        selection_input_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS+BLOCK_INPUTS})
    output=json.dumps(validation,indent=2,sort_keys=True)+'\n'; path=EXP/'artifacts/VALIDATION.json'
    if args.check: exact(path.read_text(),output)
    else: path.write_text(output)
    print(enc(dict(status=validation['status'],synthetic_checks=len(synthetic),mutations=len(negatives),meanings_validated=False)))


if __name__ == '__main__':
    main()
