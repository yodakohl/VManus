"""Validate already derived local word-alignment consequences; not a decoder repair."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import hashlib
import json
import z3

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def read(path):
    return json.loads(path.read_text())


def main():
    plan = read(E / 'artifacts/MANUAL_ALIGNMENT_PLAN.json')
    for pin in plan['inputs']:
        assert hashlib.sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256']
    spec = read(E / 'src/SPEC.json')
    signs = spec['signs']
    source = read(E / 'artifacts/SOURCE.json')
    hits = read(E / 'artifacts/PREFILTER.json')['packs']['latin']['witnesses']
    assert sorted(h['word'] for h in hits) == sorted(plan['candidates'])

    @lru_cache(None)
    def parses(raw):
        if not raw:
            return [()]
        return [(sign,) + rest for sign in signs if raw.startswith(sign)
                for rest in parses(raw[len(sign):])]

    receipts = []
    for unit in source['units']:
        reader = unit['edition']
        if reader not in ('IT2a', 'ZL3b'):
            continue
        groups = [dict(zip(unit['group_columns'], g)) for line in unit['lines'] for g in line['groups']]
        origin = next(i for i, g in enumerate(groups) if g['source_group_id'] == reader + '|f75r.38|G001')
        assert [g['ivtff_group_raw'] for g in groups[origin:origin+5]] == ['qokeedy', 'qokeedy', 'qokedy', 'qokedy', 'qokeedy']
        for hit in hits:
            word = hit['word']
            start = origin - hit['offset_zero_based']
            end = start + len(word)
            assert 0 < start < end < len(groups)
            targets = [(start - 1, ' ')] + [(start + i, c) for i, c in enumerate(word)] + [(end, ' ')]
            weights = {s: z3.Int('weight_' + s) for s in signs}
            solver = z3.Solver()
            solver.set(timeout=5000)
            for weight in weights.values():
                solver.add(weight >= 0, weight < 27)
            constraints = []
            for position, character in targets:
                group = groups[position]
                paths = parses(group['ivtff_group_raw'])
                value = 0 if character == ' ' else ord(character) - 96
                counts = Counter(paths[0]) if len(paths) == 1 else None
                if counts is not None:
                    solver.add(z3.Sum([count * weights[sign] for sign, count in counts.items()]) % 27 == value)
                constraints.append({'source_id': group['source_group_id'], 'raw': group['ivtff_group_raw'],
                                    'conditional_character': character, 'residue': value,
                                    'counts': dict(counts) if counts is not None else None})
            result = solver.check()
            status = 'SAT_LOCAL_ONLY' if result == z3.sat else 'UNSAT_LOCAL' if result == z3.unsat else 'UNKNOWN'
            assert status == plan['expected'][word], (reader, word, status)
            if result == z3.sat:
                witness = {s: solver.model().eval(w, model_completion=True).as_long() for s, w in weights.items()}
                assert all(c['counts'] is None or sum(n * witness[s] for s, n in c['counts'].items()) % 27 == c['residue'] for c in constraints)
            receipts.append({'reader': reader, 'word': word, 'offset': hit['offset_zero_based'],
                             'status': status, 'conditional_constraints': constraints})
    assert len(receipts) == 8
    report = {'experiment_id': 'GDT1388', 'status': 'PASS_KNOWN_MANUAL_CONSEQUENCES_ONLY',
              'cases': receipts, 'program_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'plan_sha256': hashlib.sha256((E / 'artifacts/MANUAL_ALIGNMENT_PLAN.json').read_bytes()).hexdigest(),
              'limits': plan['decision'], 'z3_version': z3.get_version_string()}
    (E / 'artifacts/MANUAL_ALIGNMENT_VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'cases': [(r['reader'], r['word'], r['status']) for r in receipts]}))


if __name__ == '__main__':
    main()
