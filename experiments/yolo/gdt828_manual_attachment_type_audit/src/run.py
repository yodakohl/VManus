#!/usr/bin/env python3
"""Audit two fixed proposed constructions, without scoring lexical meanings."""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]


def build():
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    source = ROOT / spec['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == spec['source_sha256']
    assert spec['sealed_data'] == ['f84', 'f84r']
    # This exact hash binds an admitted-only packet, not a mixed raw corpus.
    with source.open(newline='') as f:
        lines = list(csv.DictReader(f, delimiter='\t'))
    assert len(lines) == 150
    assert {line['page'] for line in lines} == set(spec['allowed_pages'])
    counts = Counter()
    rows = []
    for line in lines:
        assert not line['page'].startswith('f84')
        assert line['edition'] in spec['editions']
        words = json.loads(line['groups_json'])
        ids = json.loads(line['source_ids_json'])
        metadata = {key: json.loads(line[key + '_json']) for key in ('left', 'right', 'start', 'end')}
        assert all(len(value) == len(words) for value in [ids, *metadata.values()])
        for i, word in enumerate(words):
            if word != spec['target']:
                continue
            for rule, offset in spec['rules'].items():
                j = i + offset
                present = 0 <= j < len(words)
                neighbor = words[j] if present else ''
                proposed_type = spec['types'].get(neighbor, 'UNKNOWN') if present else 'LINE_EDGE'
                if proposed_type in ('NOMINAL', 'NOMINAL_PRONOUN'):
                    status = 'TYPE_COMPATIBLE_ONLY'
                elif proposed_type in ('IMPERATIVE', 'RELATION'):
                    status = 'TYPE_CONFLICT'
                else:
                    status = 'UNRESOLVED'
                row = {k: line[k] for k in ('block_id', 'page', 'locus', 'edition')}
                row.update(target_index=i, source_group_id=ids[i], rule=rule,
                    neighbor_index=j if present else -1, neighbor_raw=neighbor,
                    neighbor_type=proposed_type, status=status,
                    target_left_separator=metadata['left'][i], target_right_separator=metadata['right'][i],
                    paragraph_start=metadata['start'][i], paragraph_end=metadata['end'][i])
                rows.append(row)
                counts[line['edition'], rule, status] += 1
    summary = []
    for edition in spec['editions']:
        for rule in spec['rules']:
            values = {s.lower(): counts[edition, rule, s] for s in
                ('TYPE_COMPATIBLE_ONLY', 'TYPE_CONFLICT', 'UNRESOLVED')}
            summary.append(dict(edition=edition, rule=rule, targets=sum(values.values()), **values,
                construction_status='FAIL_FIXED_CONSTRUCTION' if values['type_conflict'] else 'NO_CONFLICT_NOT_VALIDATION'))
    result = dict(experiment_id='GDT828',
        status='C0_IMMEDIATE_ATTACHMENT_CONSTRUCTIONS_FAIL_NO_LEXICAL_VERDICT',
        source_sha256=spec['source_sha256'], source_lines=len(lines),
        source_loci=len({line['locus'] for line in lines}),
        chedy_positions=len(rows)//2, unique_target_loci=len({r['locus'] for r in rows}),
        by_reading_rule=summary, exposure=spec['exposure'],
        interpretation='Conditional construction failures; proposed types are not decoded POS; unknown is unresolved.',
        dictionary_changed=False, confirmed_lexemes=0, confirmed_clauses=0,
        new_admissions=0, new_images=0, new_scored_relations=0, sealed_data=spec['sealed_data'])
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return {'NEIGHBORS.tsv': out.getvalue(), 'RESULT.json': json.dumps(result, indent=2, sort_keys=True)+'\n'}


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
    print('GDT828 fixed-construction accounting reproduced; no lexical validation')


if __name__ == '__main__':
    main()
