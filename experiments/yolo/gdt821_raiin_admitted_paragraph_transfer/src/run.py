#!/usr/bin/env python3
"""All admitted exact raiin, full paragraphs and fixed C0 physical ascent."""
import argparse
import csv
import io
import json
import runpy
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
BASE = runpy.run_path(str(ROOT / 'experiments/yolo/gdt820_grouped_predicate_repetition_context/src/run.py'))
query, read_table, enc, require = [BASE[k] for k in ['query', 'read_table', 'enc', 'require']]
META, GCOLS, MARKS = BASE['META'], BASE['GCOLS'], BASE['MARKS']


def table(rows, fields=None):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fields or list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue()


def build():
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    proposal = json.loads((ROOT / spec['inherited_proposal']).read_text())
    require(proposal['whole'] == spec['whole'] == 'raiin' and
            proposal['sense'] == 'PHYSICAL_UPWARD_MOTION_NOT_INCREASE_HEATING_EVAPORATION_COPULA_OR_DESCENT', 'Fixed sense')
    admitted = [r for path in spec['admission_inputs'] for r in read_table(ROOT / path)]
    pages = sorted({r['source_selector'] for r in admitted})
    require(len(admitted) == len(pages) == spec['expected_admitted_selectors'] == 39 and
            not any(p.startswith('f84') for p in pages) and spec['sealed_data'] == ['f84', 'f84r'], 'Admission')
    lines, g1 = query('transcription/voynich_zl3b_lines.tsv', META, pages)
    cross, g2 = query('transcription/voynich_cross_transcription_lines.tsv', ['page', 'locus', *spec['editions'].values()], pages)
    atlas, g3 = query(spec['source_atlas'], GCOLS, pages)
    by = {r['locus']: dict(r) for r in lines}
    require(len(by) == len(lines) == len(cross) == len({r['locus'] for r in cross}), 'Unique source records')
    for r in cross:
        require(r['locus'] in by and by[r['locus']]['page'] == r['page'] and by[r['locus']]['eva_clean'] == r['zl3b_clean'], 'Reader join')
        by[r['locus']].update(r)
    hits = [r for r in atlas if r['ivtff_group_raw'] == 'raiin']
    clean_only = [r for r in atlas if r['ivtff_group_raw'] != 'raiin' and 'raiin' in r['clean_ascii_fragments'].split()]
    target_loci = {r['locus'] for r in hits}
    require(target_loci and target_loci <= set(by), 'Exact hit source loci')
    by_page = {p: sorted([r for r in by.values() if r['page'] == p], key=lambda r: int(r['locus'].split('.')[1])) for p in pages}
    selected = {}; block_map = {}; locus_block = {}
    for loc in sorted(target_loci):
        row = by[loc]; stream = by_page[row['page']]; ix = next(i for i, r in enumerate(stream) if r['locus'] == loc)
        if row['kind'] == 'P':
            starts = [i for i in range(ix+1) if stream[i]['kind'] == 'P' and stream[i]['paragraph_start'] == '1']
            ends = [i for i in range(ix, len(stream)) if stream[i]['kind'] == 'P' and stream[i]['paragraph_end'] == '1']
            require(starts and ends, 'Missing complete paragraph boundary: ' + loc)
            block = stream[starts[-1]:ends[0]+1]
            prose = [r for r in block if r['kind'] == 'P']
            require(all(r['kind'] in ['P', 'L'] for r in block) and all(r['paragraph_start'] == '0' for r in prose[1:]) and
                    all(r['paragraph_end'] == '0' for r in prose[:-1]), 'Crossed paragraph boundary: ' + loc)
        else:
            block = [row]; prose = []
        bid = block[0]['locus'] + '--' + block[-1]['locus']
        entry = dict(block_id=bid, page=row['page'], kind=row['kind'], first=block[0]['locus'], last=block[-1]['locus'],
            prose_loci=len(prose), separate_label_loci=enc([r['locus'] for r in block if r['kind'] == 'L']), triggers_json='')
        if bid not in block_map:
            block_map[bid] = entry | {'triggers': []}
        block_map[bid]['triggers'].append(loc)
        for r in block:
            require(r['locus'] not in locus_block or locus_block[r['locus']] == bid, 'Overlapping incompatible blocks')
            selected[r['locus']] = r; locus_block[r['locus']] = bid
    order = sorted(selected, key=lambda loc: (by[loc]['page'], int(loc.split('.')[1])))
    blocks = sorted(block_map.values(), key=lambda b: (b['page'], int(b['first'].split('.')[1])))
    for b in blocks:
        b['triggers_json'] = enc(sorted(b.pop('triggers'), key=lambda loc: int(loc.split('.')[1])))
    groups = [r for r in atlas if r['locus'] in selected]
    grouped = defaultdict(list)
    for r in groups:
        grouped[r['locus'], r['edition']].append(r)
    glosses = proposal['base_exact_glosses'] | {'raiin': proposal['gloss_de']}
    contexts, comparisons, trials = [], [], []
    doc = ['# GDT821 all admitted exact raiin: source-group paragraphs', '',
        'Raw source groups, not decoded words. Source periods are spaces, not sentence stops.',
        'Leading locus-placement tags remain in CONTEXTS raw field; unknown entities are opaque.', '']
    for loc in order:
        r = by[loc]
        contexts.append(dict(block_id=locus_block[loc], **{k: r[k] for k in META if k != 'eva_clean'},
            target=int(loc in target_loci), readings_json=enc({rd: r[rd] for rd in spec['editions'].values()})))
        native = {}
        for edition, rd in spec['editions'].items():
            gs = sorted(grouped[loc, edition], key=lambda g: int(g['source_group_index']))
            require(gs and [int(g['source_group_index']) for g in gs] == list(range(1,len(gs)+1)) and
                    all(int(g['source_group_count']) == len(gs) for g in gs), 'Complete source groups')
            require(gs[0]['left_separator'] == 'LINE_START' and gs[-1]['right_separator'] == 'LINE_END' and
                    all(gs[i]['right_separator'] == gs[i+1]['left_separator'] for i in range(len(gs)-1)), 'Separator adjacency')
            words = [g['ivtff_group_raw'] for g in gs]
            raw = ''.join((MARKS[g['left_separator']] if i else '') + g['ivtff_group_raw'] for i, g in enumerate(gs))
            native[edition] = raw
            fragments = [w for g in gs for w in g['clean_ascii_fragments'].split()]
            comparisons.append(dict(locus=loc, edition=edition, source_group_count=len(gs), raw_grouped_line=raw,
                flat_matches_current=int(fragments == r[rd].split()), exact_raiin_count=words.count('raiin')))
            trials.append(dict(block_id=locus_block[loc], page=r['page'], locus=loc, kind=r['kind'], edition=edition,
                target=int(loc in target_loci), source_group_ids_json=enc([g['source_group_id'] for g in gs]),
                source_groups_json=enc(words), separators_json=enc([g['right_separator'] for g in gs[:-1]]),
                literal_trial_json=enc([glosses.get(w, '['+w+']') for w in words]), confidence=proposal['confidence']))
        doc += [f"## {loc} [{r['kind']}] target={int(loc in target_loci)} P-start={r['paragraph_start']} P-end={r['paragraph_end']}", '']
        for edition in spec['editions']:
            doc += [edition + (': same source-group line as ZL3b.' if edition != 'ZL3b' and native[edition] == native['ZL3b'] else ': `' + native[edition] + '`')]
        doc += ['']
    result = dict(experiment_id='GDT821', status='ALL_ADMITTED_EXACT_RAIIN_FIXED_SPATIAL_TRIAL_NOT_TRANSLATION',
        admitted_selectors=39, admitted_pages=pages, inventory_source_loci=len(lines), inventory_source_groups=len(atlas),
        exact_hit_group_readings=len(hits), exact_hits_by_edition=dict(Counter(r['edition'] for r in hits)),
        clean_only_group_readings=len(clean_only), target_loci=len(target_loci), target_pages=sorted({by[loc]['page'] for loc in target_loci}),
        target_kinds=dict(Counter(by[loc]['kind'] for loc in target_loci)), blocks=len(blocks), complete_P_blocks=sum(b['kind']=='P' for b in blocks),
        context_loci=len(contexts), context_kinds=dict(Counter(r['kind'] for r in contexts)), source_groups=len(groups),
        group_comparisons=len(comparisons), flat_matches=sum(r['flat_matches_current'] for r in comparisons), literal_rows=len(trials),
        exact_raw_match_only=True, extended_glyph_expansion=False, all_admitted_exact_raiin=True, new_admissions=0,
        new_image_inspections=0, dictionary_changed=False, meanings_validated=False, confirmed_lexemes=0, confirmed_plaintext_clauses=0,
        guarded_queries=[g1,g2,g3], sealed_data=['f84','f84r'])
    return {'ADMITTED_SELECTORS.tsv': table([dict(source_selector=p) for p in pages]), 'EXACT_HITS.tsv': table(hits, GCOLS),
        'CLEAN_ONLY_HITS.tsv': table(clean_only, GCOLS), 'BLOCKS.tsv': table(blocks), 'CONTEXTS.tsv': table(contexts),
        'SOURCE_GROUPS.tsv': table(groups, GCOLS), 'GROUP_COMPARISON.tsv': table(comparisons), 'LITERAL_TRIALS.tsv': table(trials),
        'FULL_READER.md': '\n'.join(doc).rstrip()+'\n', 'RESULT.json': json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    for name,content in build().items():
        path=EXP/'artifacts'/name
        if args.check: require(path.read_text()==content, 'Replay differs: '+name)
        else: path.write_text(content)
    print('All-admitted exact raiin source/literal packet reproduced; no meaning validation')


if __name__=='__main__':
    main()
