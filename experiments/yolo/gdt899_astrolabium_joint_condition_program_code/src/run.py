#!/usr/bin/env python3
"""Complete finite-language word equations, solved with cvc5. No corpus repair."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compiled(source, order):
    assert sorted(order) == ['companion', 'location', 'mercury']
    programs = source['programs']
    assert programs and len({p['id'] for p in programs}) == len(programs)
    rows = []
    for p in programs:
        seq = sum((p['header_factors'][role] for role in order), [])
        seq += p['after_header'] + p['body_atoms']
        assert seq and all(isinstance(x, str) and x for x in seq)
        rows.append((p['id'], seq))
    return rows


def fit(source, target, order, seconds, emit):
    import cvc5
    from cvc5 import Kind as K
    started = time.monotonic()
    deadline = started + seconds
    rows = compiled(source, order)
    candidates = target['panels']['IT2a']
    assert all(not t['page'].startswith('f84') and int(t['physical_folio'][1:]) % 2 == 1 for t in candidates)
    by_text = {}
    for t in candidates:
        assert t['text'] == ' '.join(t['words'])
        by_text.setdefault(t['text'], []).append(t['id'])
    assert len(by_text) >= len(rows)
    max_chars = max(map(len, by_text))
    counts = [Counter(seq) for _, seq in rows]
    atoms = sorted(set().union(*counts))
    bounds = {a: min((max_chars - (sum(c.values()) - c[a])) // c[a]
                     for c in counts if c[a]) for a in atoms}
    s = cvc5.Solver()
    s.setLogic('QF_SLIA')
    s.setOption('produce-models', 'true')
    s.setOption('incremental', 'true')
    s.setOption('strings-exp', 'true')
    sort = s.getStringSort()
    variables = {a: s.mkConst(sort, f'a{i:03}') for i, a in enumerate(atoms)}
    for a, v in variables.items():
        length = s.mkTerm(K.STRING_LENGTH, v)
        s.assertFormula(s.mkTerm(K.GEQ, length, s.mkInteger(1)))
        s.assertFormula(s.mkTerm(K.LEQ, length, s.mkInteger(bounds[a])))
    for a, b in itertools.combinations(atoms, 2):
        va, vb = variables[a], variables[b]
        s.assertFormula(s.mkTerm(K.NOT, s.mkTerm(K.STRING_PREFIX, va, vb)))
        s.assertFormula(s.mkTerm(K.NOT, s.mkTerm(K.STRING_PREFIX, vb, va)))
    strings = [(txt, s.mkString(txt)) for txt in sorted(by_text)]
    expressions = {}
    for rid, seq in rows:
        expr = s.mkTerm(K.STRING_CONCAT, *[variables[a] for a in seq])
        expressions[rid] = expr
        eligible = [constant for txt, constant in strings if len(txt) >= len(seq)]
        s.assertFormula(s.mkTerm(K.OR, *[s.mkTerm(K.EQUAL, expr, txt) for txt in eligible])
                        if len(eligible) > 1 else s.mkTerm(K.EQUAL, expr, eligible[0])
                        if eligible else s.mkBoolean(False))
    s.assertFormula(s.mkTerm(K.DISTINCT, *expressions.values()))

    def check(cap=None):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return 'UNKNOWN_BUDGET'
        s.setOption('tlimit-per', str(max(1, int(1000 * min(remaining, cap if cap else remaining)))))
        answer = s.checkSat()
        if answer.isSat(): return 'SAT'
        if answer.isUnsat(): return 'UNSAT'
        return 'UNKNOWN_' + str(answer.getUnknownExplanation())

    answer = {'schema': 'GDT899_CVC5_COMPLETE_MODEL_V1', 'solver': 'cvc5',
              'solver_version': s.getVersion().decode(), 'header_order': order,
              'source_records': len(rows), 'target_paragraphs': len(candidates),
              'target_distinct_strings': len(by_text), 'atom_count': len(atoms),
              'derived_codeword_length_bounds': bounds,
              'budget_seconds': seconds, 'status': check()}
    answer['elapsed_seconds'] = time.monotonic() - started
    if answer['status'] != 'SAT':
        emit(answer)
        return answer
    code = {a: s.getValue(v).getStringValue() for a, v in variables.items()}
    values = {rid: s.getValue(expr).getStringValue() for rid, expr in expressions.items()}
    assert all(code.values()) and len(set(code.values())) == len(code)
    assert not any(code[a].startswith(code[b]) or code[b].startswith(code[a]) for a, b in itertools.combinations(atoms, 2))
    assert len(set(values.values())) == len(rows)
    for rid, seq in rows:
        assert ''.join(code[a] for a in seq) == values[rid] and values[rid] in by_text
    answer.update(codeword_witness=code, program_outputs=values,
                  target_ids={rid: by_text[val] for rid, val in values.items()},
                  witness_validation='PASS_COMPLETE_EQUATIONS',
                  atom_projection={}, program_projection={})
    emit(answer)
    # Projection queries examine the ORIGINAL complete model, not the witness
    # with other variables fixed. Every push is popped before the next query.
    for name, terms, witness, dest in [('atom', variables, code, 'atom_projection'),
                                        ('program', expressions, values, 'program_projection')]:
        for key in sorted(terms):
            s.push()
            s.assertFormula(s.mkTerm(K.NOT, s.mkTerm(K.EQUAL, terms[key], s.mkString(witness[key]))))
            alternative = check(30)
            s.pop()
            answer[dest][key] = {'alternative_query': alternative,
                                'status': 'FIXED_WITHIN_HEADER' if alternative == 'UNSAT' else
                                          'AMBIGUOUS_WITHIN_HEADER' if alternative == 'SAT' else 'UNRESOLVED'}
            answer['elapsed_seconds'] = time.monotonic() - started
            emit(answer)
    return answer


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--header-order', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--budget-seconds', type=float, default=1200)
    a = p.parse_args()
    source = json.loads(a.source.read_text())
    assert source['program_count'] == 24 and len(source['programs']) == 24
    target = json.loads(a.target.read_text())
    bindings = {'source_sha256': sha(a.source), 'target_sha256': sha(a.target)}
    def emit(result):
        result.update(bindings)
        tmp = a.output.with_suffix(a.output.suffix + '.tmp')
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        tmp.replace(a.output)
    result = fit(source, target, a.header_order.split(','), a.budget_seconds, emit)
    emit(result)
    print(result['status'], result['header_order'], flush=True)


if __name__ == '__main__':
    main()
