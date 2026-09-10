#!/usr/bin/env python3
"""Independent finite-language, nonerasing prefix-code fitter (Z3).

No primary solver/compiler imports. Every program is constrained against the
whole IT2a language; all encoded program outputs must differ. Header order is a
single supplied global permutation. A case result makes no cross-case claim.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time
import z3


class BudgetExpired(Exception):
    pass


def compile_programs(source, order):
    programs = source['programs']
    if not programs or len(order) != 3 or len(set(order)) != 3:
        raise ValueError('Need programs and three distinct header roles')
    compiled = []
    seen = set()
    for p in programs:
        pid = p['id']
        if not isinstance(pid, str) or pid in seen:
            raise ValueError('Program IDs must be distinct strings')
        seen.add(pid)
        factors = p['header_factors']
        if set(factors) != set(order):
            raise ValueError('Header order must use exactly the three roles')
        segments = [factors[r] for r in order] + [p['after_header'], p['body_atoms']]
        if any(not isinstance(s, list) for s in segments):
            raise ValueError('Atom sequences must be arrays')
        tokens = [t for segment in segments for t in segment]
        if not tokens or any(not isinstance(t, str) or not t for t in tokens):
            raise ValueError('Atoms must be nonempty string identifiers')
        compiled.append((pid, tokens))
    return compiled


def decode_model_string(model, expression):
    # as_string() can expose Unicode escapes, so recover actual code points.
    value = model.eval(expression, model_completion=True)
    length = z3.simplify(z3.Length(value)).as_long()
    return ''.join(chr(z3.simplify(z3.StrToCode(z3.SubString(value, i, 1))).as_long())
                   for i in range(length))


def solve(source, target, order, seconds, projection=True, start=None):
    began = time.monotonic() if start is None else start
    deadline = began + seconds
    result = {'schema': 'GDT899_INDEPENDENT_Z3_CASE_V1',
              'solver': 'Z3', 'solver_version': z3.get_version_string(),
              'header_order': list(order), 'budget_seconds': seconds,
              'first_status': 'UNKNOWN', 'scope': 'THIS_HEADER_ORDER_ONLY',
              'projection_requested': projection}

    def remaining():
        r = deadline - time.monotonic()
        if r <= 0:
            raise BudgetExpired()
        return r

    try:
        remaining()
        programs = compile_programs(source, order)
        entries = target['panels']['IT2a']
        if not isinstance(entries, list) or not entries:
            raise ValueError('Nonempty IT2a target language required')
        ids = set()
        for e in entries:
            if not isinstance(e['id'], str) or e['id'] in ids:
                raise ValueError('Target IDs must be unique strings')
            ids.add(e['id'])
            if not isinstance(e['text'], str):
                raise ValueError('Target text must be literal strings')
        language = sorted({e['text'] for e in entries})
        maximum = max(map(len, language))
        alphabet = sorted({t for _, ts in programs for t in ts})
        # With k occurrences of a among m atoms, all other m-k codewords
        # contribute at least one character: k*len(a)+(m-k) <= max target.
        upper = {a: min((maximum - (len(ts)-ts.count(a))) // ts.count(a)
                        for _, ts in programs if a in ts) for a in alphabet}
        result.update(program_count=len(programs), atom_count=len(alphabet),
                      target_entry_count=len(entries), distinct_target_texts=len(language),
                      sound_length_upper_bounds=upper)
        variables = {a: z3.String('atom_' + str(i)) for i, a in enumerate(alphabet)}
        solver = z3.Solver()
        solver.set(random_seed=0)
        for a in alphabet:
            remaining()
            solver.add(z3.Length(variables[a]) >= 1, z3.Length(variables[a]) <= upper[a])
        for a, b in itertools.combinations(alphabet, 2):
            remaining()
            solver.add(z3.Not(z3.PrefixOf(variables[a], variables[b])),
                       z3.Not(z3.PrefixOf(variables[b], variables[a])))
        exprs = {}
        literals = [z3.StringVal(w) for w in language]
        for pid, ts in programs:
            remaining()
            vv = [variables[a] for a in ts]
            expr = vv[0] if len(vv) == 1 else z3.Concat(*vv)
            exprs[pid] = expr
            solver.add(z3.Or(*[expr == w for w in literals]))
        solver.add(z3.Distinct(*list(exprs.values())))
        result['build_seconds'] = time.monotonic() - began

        def check(cap=None):
            budget = remaining()
            if cap is not None:
                budget = min(budget, cap)
            solver.set(timeout=max(1, int(budget*1000)))
            before = time.monotonic()
            answer = solver.check()
            return answer, time.monotonic()-before

        answer, duration = check()
        result['first_check_seconds'] = duration
        result['first_status'] = str(answer).upper()
        if answer == z3.unknown:
            result['first_reason_unknown'] = solver.reason_unknown()
        if answer == z3.sat:
            model = solver.model()
            code = {a: decode_model_string(model, variables[a]) for a in alphabet}
            outputs = {pid: ''.join(code[a] for a in ts) for pid, ts in programs}
            # Independent Python witness check uses the original complete words.
            assert all(1 <= len(code[a]) <= upper[a] for a in alphabet)
            assert all(not code[a].startswith(code[b]) and not code[b].startswith(code[a])
                       for a,b in itertools.combinations(alphabet,2))
            assert len(set(outputs.values())) == len(outputs)
            assert all(s in language for s in outputs.values())
            result['codewords'] = code
            result['program_outputs'] = [
                {'id': pid, 'text': outputs[pid],
                 'target_ids': [e['id'] for e in entries if e['text'] == outputs[pid]]}
                for pid,_ in programs]
            result['witness_replay'] = 'PASS'
            if projection:
                requests = [('atom', a, variables[a], code[a]) for a in alphabet]
                requests += [('program', pid, exprs[pid], outputs[pid]) for pid,_ in programs]
                projection_results = []
                result['projections'] = projection_results
                for kind, key, expression, value in requests:
                    item = {'kind': kind, 'id': key, 'status': 'UNKNOWN'}
                    projection_results.append(item)
                    try:
                        remaining()
                    except BudgetExpired:
                        item['reason'] = 'SHARED_CASE_BUDGET_EXHAUSTED'
                        continue
                    solver.push()
                    try:
                        solver.add(expression != z3.StringVal(value))
                        status, elapsed = check(30.0)
                        item['solver_status'] = str(status).upper()
                        item['seconds'] = elapsed
                        if status == z3.sat:
                            item['status'] = 'AMBIGUOUS_WITHIN_HEADER'
                            item['alternative_value'] = decode_model_string(solver.model(), expression)
                            assert item['alternative_value'] != value
                        elif status == z3.unsat:
                            item['status'] = 'FIXED_WITHIN_HEADER'
                        else:
                            item['reason'] = solver.reason_unknown()
                    except BudgetExpired:
                        item['reason'] = 'SHARED_CASE_BUDGET_EXHAUSTED'
                    finally:
                        solver.pop()
    except BudgetExpired:
        result['budget_status'] = 'EXHAUSTED'
    result['elapsed_seconds'] = time.monotonic() - began
    result['budget_exhausted'] = time.monotonic() >= deadline
    return result


def self_test():
    programs = [{'id': str(i), 'header_factors': {'location':['A'], 'mercury':['B'], 'companion':['C']},
                 'after_header':['D'], 'body_atoms':[atom]} for i,atom in enumerate(['E','F'])]
    src = {'programs': programs}
    order = ['location','mercury','companion']
    tgt = {'panels': {'IT2a':[{'id':'x','text':'ab de'}, {'id':'y','text':'ab df'}]}}
    sat = solve(src, tgt, order, 15, projection=True)
    assert sat['first_status'] == 'SAT' and sat['witness_replay'] == 'PASS'
    assert len(sat['projections']) == 8
    assert all(x['status'] != 'UNKNOWN' for x in sat['projections'])
    impossible = {'panels': {'IT2a':[{'id':'x','text':'abcd'}]}}
    assert solve(src, impossible, order, 15, projection=False)['first_status'] == 'UNSAT'
    duplicate_outputs = {'panels': {'IT2a':[{'id':'x','text':'abcde'}, {'id':'y','text':'abcde'}]}}
    assert solve(src, duplicate_outputs, order, 15, projection=False)['first_status'] == 'UNSAT'
    atomic = {'programs': [{'id': str(i), 'header_factors': {r: [] for r in order},
                           'after_header': [], 'body_atoms': [atom]}
                          for i, atom in enumerate(['X','Y'])]}
    prefix_collision = {'panels': {'IT2a': [{'id':'x','text':'a'}, {'id':'y','text':'aa'}]}}
    assert solve(atomic, prefix_collision, order, 15, projection=False)['first_status'] == 'UNSAT'
    prefix_free = {'panels': {'IT2a': [{'id':'x','text':'0'}, {'id':'y','text':'10'}]}}
    assert solve(atomic, prefix_free, order, 15, projection=False)['first_status'] == 'SAT'
    assert solve(src, tgt, order, 0, projection=False)['first_status'] == 'UNKNOWN'
    assert compile_programs(src, list(reversed(order)))[0][1] == ['C','B','A','D','E']
    model_solver = z3.Solver(); v = z3.String('unicode_fixture')
    model_solver.add(v == z3.StringVal('α a\\b\n')); assert model_solver.check() == z3.sat
    assert decode_model_string(model_solver.model(), v) == 'α a\\b\n'
    print('PASS: synthetic SAT/projections, length UNSAT, duplicate-output/prefix UNSAT, variable-length SAT, budget UNKNOWN, header order, Unicode/space replay')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path)
    p.add_argument('--target', type=Path)
    p.add_argument('--header-order')
    p.add_argument('--output', type=Path)
    p.add_argument('--budget-seconds', type=float, default=1200)
    p.add_argument('--no-projection', action='store_true')
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test:
        self_test(); return
    if any(x is None for x in (a.source,a.target,a.header_order,a.output)):
        p.error('source, target, header-order and output are required')
    if a.budget_seconds <= 0:
        p.error('budget must be positive')
    start = time.monotonic()
    source_bytes, target_bytes = a.source.read_bytes(), a.target.read_bytes()
    result = solve(json.loads(source_bytes), json.loads(target_bytes), a.header_order.split(','),
                   a.budget_seconds, not a.no_projection, start=start)
    result['source_sha256'] = hashlib.sha256(source_bytes).hexdigest()
    result['target_sha256'] = hashlib.sha256(target_bytes).hexdigest()
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(result['first_status'])


if __name__ == '__main__':
    main()
