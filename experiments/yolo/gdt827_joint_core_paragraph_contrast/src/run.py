#!/usr/bin/env python3
"""One source packet, exact-whole competing models; no semantic scoring."""
import argparse
import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
PRIOR = ROOT / 'experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts'


def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def enc(value):
    return json.dumps(value, ensure_ascii=False)


def table(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def render(words, glosses):
    return [glosses.get(w, '[' + w + ']') for w in words]


def build():
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    models = json.loads((EXP / 'src/MODELS.json').read_text())
    assert spec['sealed_data'] == ['f84', 'f84r']
    contexts = [c for c in read(PRIOR / 'CONTEXTS.tsv') if c['block_id'] in spec['blocks']]
    assert len(contexts) == 50 and all(c['kind'] == 'P' and not c['page'].startswith('f84') for c in contexts)
    loci = {c['locus'] for c in contexts}
    grouped = defaultdict(list)
    for g in read(PRIOR / 'SOURCE_GROUPS.tsv'):
        if g['locus'] in loci:
            grouped[g['locus'], g['edition']].append(g)
    rows = []
    counts = Counter()
    doc = ['# GDT827 complete selected windows, ZL display', '',
           'All three source-native alternates and flags are in SOURCE_LINES.tsv.',
           'Exact glosses only; all brackets and repetitions remain. No line is declared a sentence.', '']
    previous = None
    for c in contexts:
        if c['block_id'] != previous:
            doc += ['## ' + c['block_id'], '']
            previous = c['block_id']
        for edition in spec['editions']:
            gs = grouped[c['locus'], edition]
            words = [g['ivtff_group_raw'] for g in gs]
            row = dict(block_id=c['block_id'], page=c['page'], locus=c['locus'], edition=edition,
                source_ids_json=enc([g['source_group_id'] for g in gs]), groups_json=enc(words),
                left_json=enc([g['left_separator'] for g in gs]), right_json=enc([g['right_separator'] for g in gs]),
                start_json=enc([g['paragraph_start'] for g in gs]), end_json=enc([g['paragraph_end'] for g in gs]))
            rows.append(row)
            for name, model in models.items():
                counts[name, edition] += sum(w in model['glosses'] for w in words)
            if edition == 'ZL3b':
                doc += [c['locus'] + ': ' + ' | '.join(words)]
                doc += [name + ': ' + ' | '.join(render(words, m['glosses'])) for name, m in models.items()]
                doc.append('')
    coverage = [dict(model=n, edition=e, exact_gloss_positions=counts[n,e],
        source_positions=sum(len(grouped[c['locus'],e]) for c in contexts),
        interpretation='HYPOTHESIS_COVERAGE_NOT_ACCURACY') for n in models for e in spec['editions']]
    result = dict(experiment_id='GDT827', status='C0_CORE_UNDERDETERMINED_NO_MODEL_WINNER',
        selected_windows=4, loci=50, reader_lines=len(rows), source_groups=sum(len(v) for v in grouped.values()),
        models=list(models), virtual_renderings=len(rows)*len(models),
        source_boundary_correction='IT2a f81r.23 END and f81r.24 START; ZL one window; RF no paragraph flags',
        blind=False, dictionary_changed=False, confirmed_lexemes=0, confirmed_clauses=0,
        new_admissions=0, new_downloads=0, reinspected_images=2,
        image_coverage='f81r full image and f77r middle text crop, not two full diagram pages',
        sealed_data=['f84','f84r'])
    return {'SOURCE_LINES.tsv':table(rows), 'COVERAGE.tsv':table(coverage),
            'READER.md':'\n'.join(doc).rstrip()+'\n', 'RESULT.json':json.dumps(result,indent=2,sort_keys=True)+'\n'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, content in build().items():
        path = EXP / 'artifacts' / name
        if args.check:
            assert path.read_text() == content, name
        else:
            path.write_text(content)
    print('GDT827 source/model packet reproduced; no meanings validated')


if __name__ == '__main__':
    main()
