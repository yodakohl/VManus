#!/usr/bin/env python3
"""One separate, post-reading C0 verb; exact opaque source groups retained."""
import argparse
import json
import runpy
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
BASE = runpy.run_path(str(EXP / 'src/run.py'))
ROOT, query, read_table, enc, table, require = [BASE[k] for k in ['ROOT', 'query', 'read_table', 'enc', 'table', 'require']]


def build():
    proposal = json.loads((EXP / 'src/ASCENT_TRIAL.json').read_text())
    core = read_table(EXP / 'artifacts/SOURCE_GROUPS.tsv')
    exact = sorted({g['locus'] for g in core if g['ivtff_group_raw'] == proposal['whole']})
    require(exact == ['f66r.80', 'f77r.34'], 'All exact core raiin loci')
    targets = sorted(set(exact + proposal['comparators']))
    pages = sorted({loc.split('.')[0] for loc in targets})
    require(pages == ['f66r', 'f76r', 'f77r', 'f82r'], 'Existing admitted pages')
    admitted = read_table(ROOT / 'experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv')
    require(set(pages) <= {r['source_selector'] for r in admitted}, 'Admission')
    atlas, guard = query('experiments/semantic_assumptions/results/source_separator_transcription.tsv', BASE['GCOLS'], pages)
    selected = [g for g in atlas if g['locus'] in targets]
    rows = []; glosses = proposal['base_exact_glosses'] | {proposal['whole']: proposal['gloss_de']}
    for loc in targets:
        for edition in ['ZL3b', 'IT2a', 'RF1b']:
            gs = sorted([g for g in selected if g['locus'] == loc and g['edition'] == edition], key=lambda g: int(g['source_group_index']))
            require(gs and [int(g['source_group_index']) for g in gs] == list(range(1, len(gs)+1)) and all(int(g['source_group_count']) == len(gs) for g in gs), 'Complete reader groups')
            raw = [g['ivtff_group_raw'] for g in gs]
            rows.append(dict(page=loc.split('.')[0], locus=loc, edition=edition,
                selection_reason='EXACT_CORE_RAIIN' if loc in exact else 'KNOWN_SAL_RAIIN_COMPARATOR',
                source_group_ids_json=enc([g['source_group_id'] for g in gs]), source_groups_json=enc(raw),
                separators_json=enc([g['right_separator'] for g in gs[:-1]]),
                literal_trial_json=enc([glosses.get(w, '[' + w + ']') for w in raw]),
                exact_raiin_count=raw.count('raiin'), confidence=proposal['confidence']))
    result = dict(experiment_id='GDT820', phase=proposal['phase'], core_raiin_loci=exact,
        comparator_loci=proposal['comparators'], trial_loci=targets, trial_rows=len(rows),
        exact_raiin_occurrences=sum(r['exact_raiin_count'] for r in rows),
        added_records_outside_core=2, combined_unique_records=174, whole_comparator_paragraphs_read=False,
        all_raiin_in_admitted39=False, dictionary_changed=False, new_admissions=0,
        meanings_validated=False, confirmed_lexemes=0, confirmed_plaintext_clauses=0, guarded_query=guard)
    return {'ASCENT_TRIALS.tsv': table(rows), 'ASCENT_RESULT.json': json.dumps(result, indent=2, sort_keys=True)+'\n'}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    for name, content in build().items():
        path = EXP / 'artifacts' / name
        if args.check:
            require(path.read_text() == content, 'Ascent probe replay differs: ' + name)
        else:
            path.write_text(content)
    print('POST ascent literal displays reproduced; no semantic validation')


if __name__ == '__main__':
    main()
