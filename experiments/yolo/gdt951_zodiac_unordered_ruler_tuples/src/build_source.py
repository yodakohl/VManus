"""Materialize all historical predictions before any target label intake."""
from collections import Counter, defaultdict
import csv
import io
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]


def save(name, text):
    p = E / 'src' / name
    if p.exists():
        assert p.read_text() == text, 'fixed source changed: ' + name
    else:
        p.write_text(text)


def main():
    evidence = json.loads((E / 'src/HISTORICAL_RULES.json').read_text())
    spec = json.loads((E / 'src/SPEC.json').read_text())
    systems = evidence['systems']
    mono = systems['monomoiria']
    rows = []
    for sign, faces in systems['decanic_faces']['by_sign'].items():
        assert len(faces) == 3
        canonical = 'SCORPIUS' if sign == 'Scorpio' else sign.upper()
        ranges = systems['egyptian_bounds']['by_sign'][sign]
        assert len(ranges) == 5
        assert [d for term in ranges for d in range(term['integer_degrees'][0],
                    term['integer_degrees'][1] + 1)] == list(range(1, 31))
        for term in ranges:
            assert term['integer_degrees'][1] == term['cumulative_end_degree']
        group = mono['sign_to_group'][sign]
        sequence = mono['group_degrees_1_to_30'][group]
        assert len(sequence) == 30
        assert sequence == [mono['group_cycle_1_to_7'][group][i % 7] for i in range(30)]
        for d in range(1, 31):
            matches = [term['planet'] for term in ranges
                       if term['integer_degrees'][0] <= d <= term['integer_degrees'][1]]
            assert len(matches) == 1
            rows.append({'sign': canonical, 'degree': d, 'decan': faces[(d - 1) // 10],
                         'term': matches[0], 'monomoirion': sequence[d - 1],
                         'domicile': group})
    assert len(rows) == 360 and len({(r['sign'], r['degree']) for r in rows}) == 360
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    save('HISTORICAL_DEGREES.tsv', out.getvalue())
    predictions = {}
    for model, fields in spec['models'].items():
        counts = defaultdict(Counter)
        degrees = defaultdict(list)
        for row in rows:
            if row['sign'] in spec['sign_order']:
                key = tuple(row[f] for f in fields)
                counts[key][row['sign']] += 1
                degrees[key].append({'sign': row['sign'], 'degree': row['degree']})
        predictions[model] = [{'id': f'{model}-{i:03}', 'values': dict(zip(fields, key)),
                              'counts': {s: counts[key][s] for s in spec['sign_order']},
                              'source_degrees': degrees[key]}
                             for i, key in enumerate(sorted(counts))]
        assert all(sum(t['counts'][s] for t in predictions[model]) == 30
                   for s in spec['sign_order'])
    save('SOURCE_PREDICTIONS.json', json.dumps(predictions, separators=(',', ':')) + '\n')
    print(json.dumps({m: {'tuple_types': len(ts), 'distinct_by_sign': {
        s: sum(t['counts'][s] > 0 for t in ts) for s in spec['sign_order']}}
        for m, ts in predictions.items()}))


if __name__ == '__main__':
    main()
