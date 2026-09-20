#!/usr/bin/env python3
"""Meaningful source-only interface fixtures; no Voynich target read."""
import json
from pathlib import Path
from model import WRITERS, compile_trees, form_value, solve, witness

E = Path(__file__).resolve().parents[1]


def main():
    clauses = [dict(id='C1', tree=['AND', ['REL', 'A', 'B'], ['REL', 'B', 'A']]),
               dict(id='C2', tree=['MOVE', 'A', 'B', 'C']),
               dict(id='C3', tree=['IF', ['READY', 'A'], ['GOOD', 'C']])]
    roots = dict(AND='h', REL='x', A='u', B='v', MOVE='m', C='w', IF='n', READY='t', GOOD='g')
    frames = dict(P1='a', S1='d', P2='b', S2='e', P3='c', S3='f')
    pins = dict(roots=roots, frames=frames)
    rows = []
    for writer in WRITERS:
        events = compile_trees(clauses, writer)
        values = [form_value(e, roots, frames) for e in events]
        words = [''.join(values[i:i + 2]) for i in range(0, len(values), 2)]
        ok = solve(events, words, seconds=3, pins=pins)
        assert ok['status'] == 'SAT' and witness(events, words, roots, frames)['valid']
        first = next(i for i, e in enumerate(events) if e['role'])
        seam = sum(map(len, values[:first])) + 1
        text = ''.join(values)
        split = [text[:seam], text[seam:]]
        bad = solve(events, split, seconds=3, pins=pins)
        assert bad['status'] == 'UNSAT', bad['status']
        assert not witness(events, split, roots, frames)['valid']
        collision = dict(roots, B=roots['A'])
        collision_words = [''.join(form_value(e, collision, frames) for e in events)]
        assert not witness(events, collision_words, collision, frames)['valid']
        rows.append(dict(writer=writer, positive='SAT', forbidden_internal_frame_seam='UNSAT', root_collision='REJECTED', words=words))
    result = dict(status='PASS', scope='four-order shared-frame and whole-seam interface; no search null or meaning test', rows=rows)
    (E / 'artifacts/PRE_RUN_FIXTURES.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
