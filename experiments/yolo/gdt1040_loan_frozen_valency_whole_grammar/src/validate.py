#!/usr/bin/env python3
"""Independent Z3 sequential-debt oracle; no runner imports or semantic execution."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import re
import z3

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
ART = EXP/'artifacts'
FIXED = {'shedy': -1, 'qokaiin': -1, 'lchedy': -1, 'chedy': 0, 'qokeedy': 1, 'qokedy': 0, 'qoteedy': 0}
OPTIONS = (-1, 1, 2)
EXPECTED_BINDINGS = {
    'original': '0400e17f9483891b8dac47d7459bbda839f010e52d2e0cb4682e22c7e7522142',
    'offer': 'f2e00c31f2ac1489c5c4b55f16cc1e151f171cb5b87341690a796caae8a97c29',
    'paragraphs': '667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b',
    'W41': '32d02fcc71a98ad7414ac72adb99c4216f7e8cc4760bc041865f1b0c5d509c55',
    'GDT979': 'cb69d1dd5b4741923607151387db23a194a4cbc6370acb0de860f6d9200aa688',
}


def require(test, message):
    if not test:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


class DebtOracle:
    """A head opens arity slots; nouns consume exactly one outstanding slot."""
    def __init__(self, streams, fixed, assignment=None, full=False):
        self.streams = streams
        forms = sorted({w for words in streams.values() for w in words})
        self.cat = {w: z3.Int('cat_'+str(i)) for i, w in enumerate(forms)}
        self.length, self.formulas, self.metadata = {}, {}, {}

        def add(expr, metadata):
            key = 'constraint_'+str(len(self.formulas))
            self.formulas[key], self.metadata[key] = expr, metadata

        for word in forms:
            allowed = [fixed[word]] if word in fixed else list(OPTIONS)
            add(z3.Or([self.cat[word] == v for v in allowed]), dict(kind='category_domain', word=word, allowed=allowed))
        for word, value in (assignment or {}).items():
            add(self.cat[word] == value, dict(kind='recurrent_assignment', word=word, category=value))
        for j, (name, words) in enumerate(streams.items()):
            n = len(words)
            length = z3.Int('length_'+str(j))
            self.length[name] = length
            debt = [z3.Int(f'debt_{j}_{i}') for i in range(n+1)]
            add(z3.And(length >= 0, length <= n), dict(kind='prefix_length_domain', model=name))
            add(debt[0] == 0, dict(kind='initial_debt_zero', model=name))
            for i, state in enumerate(debt):
                add(z3.And(state >= 0, state <= 2), dict(kind='debt_domain', model=name, boundary=i))
                add(z3.Implies(length == i, state == 0), dict(kind='complete_prefix_end', model=name, boundary=i))
            for i, word in enumerate(words):
                cat = self.cat[word]
                head = z3.And(debt[i] == 0, cat >= 0, debt[i+1] == cat)
                argument = z3.And(debt[i] > 0, cat == -1, debt[i+1] == debt[i]-1)
                add(z3.Implies(i < length, z3.Or(head, argument)), dict(kind='ordered_token', model=name, position=i+1, word=word))
            if full:
                add(length == n, dict(kind='require_whole_unit', model=name, groups=n))

    def solver(self, tracked=False):
        solver = z3.Solver()
        solver.set(timeout=30000)
        for key, expr in self.formulas.items():
            solver.assert_and_track(expr, z3.Bool(key)) if tracked else solver.add(expr)
        return solver

    def whole_status_and_core(self):
        solver = self.solver(tracked=True)
        outcome = solver.check()
        if outcome == z3.unknown:
            return dict(status='UNKNOWN_SOLVER', reason=solver.reason_unknown())
        if outcome == z3.sat:
            model = solver.model()
            return dict(status='SAT', category_witness={w: model.eval(v).as_long() for w, v in self.cat.items()})
        core = [str(x) for x in solver.unsat_core()]
        replay = z3.Solver()
        replay.add([self.formulas[key] for key in core])
        require(replay.check() == z3.unsat, 'UNSAT core did not replay')
        return dict(status='UNSAT', core_replayed=True, core=[dict(id=k, **self.metadata[k]) for k in core], core_minimality='Not claimed; tracked constraint subset rechecked UNSAT.')

    def count_full_assignments(self, cap=1000000):
        solver, count = self.solver(), 0
        while True:
            outcome = solver.check()
            if outcome == z3.unsat:
                return count
            require(outcome == z3.sat, 'UNKNOWN_SOLVER during exact path count')
            require(count < cap, 'UNKNOWN_VALIDATOR_CAP during exact path count')
            model = solver.model()
            values = {w: model.eval(v).as_long() for w, v in self.cat.items()}
            count += 1
            # Full category map uniquely determines debt/path. Do not count
            # auxiliary-variable models of the same category map twice.
            solver.add(z3.Or([self.cat[w] != v for w, v in values.items()]))

    def best_prefix(self, name, recurrent=()):
        optimizer = z3.Optimize()
        optimizer.set(timeout=30000)
        optimizer.add(list(self.formulas.values()))
        optimizer.maximize(self.length[name])
        require(optimizer.check() == z3.sat, 'UNKNOWN_SOLVER optimizing prefix')
        end = optimizer.model().eval(self.length[name]).as_long()
        larger = self.solver()
        larger.add(self.length[name] > end)
        require(larger.check() == z3.unsat, 'Prefix optimum not certified')
        solver = self.solver()
        solver.add(self.length[name] == end)
        assignment = {}
        for word in recurrent:
            for value in OPTIONS:
                solver.push(); solver.add(self.cat[word] == value)
                outcome = solver.check(); solver.pop()
                require(outcome != z3.unknown, 'UNKNOWN_SOLVER choosing recurrent tie')
                if outcome == z3.sat:
                    solver.add(self.cat[word] == value)
                    assignment[word] = value
                    break
            else:
                raise ValueError('No recurrent tie witness')
        lengths, position, words = [], 0, self.streams[name]
        while position < end:
            for arity in (0, 1, 2):
                solver.push(); solver.add(self.cat[words[position]] == arity)
                outcome = solver.check(); solver.pop()
                require(outcome != z3.unknown, 'UNKNOWN_SOLVER choosing clause tie')
                if outcome == z3.sat:
                    solver.add(self.cat[words[position]] == arity)
                    lengths.append(arity+1)
                    position += arity+1
                    break
            else:
                raise ValueError('No prefix witness')
        require(position == end and solver.check() == z3.sat, 'Prefix witness incomplete')
        return dict(max_prefix=end, best_recurrent_assignment=assignment, best_prefix_lengths=lengths)


def registration():
    lock, receipt = load(EXP/'PREREG_LOCK.json'), load(ART/'PUBLIC_REGISTRATION.json')
    require(lock['status'] == 'REGISTERED_BEFORE_EXECUTION', 'Registration status')
    require(receipt['registered_before_execution'] is True, 'Public receipt missing')
    require(re.fullmatch('[0-9a-f]{40}', receipt['commit']) is not None, 'Public commit format')
    require(receipt['public_ref'] == 'refs/heads/main', 'Public ref mismatch')
    bound = {}
    for item in lock['files']:
        path = Path(item['path'])
        require(not path.is_absolute() and '..' not in path.parts, 'Nonrelative lock path')
        require(sha(ROOT/path) == item['sha256'], 'Lock hash mismatch: '+str(path))
        bound[str(path)] = item['sha256']
    for path in ['src/validate.py', 'src/run.py', 'src/SOURCE.json', 'src/SPEC.json', 'DECISION.md', 'METHOD.md', 'PREREGISTRATION.md']:
        require((EXP/path).relative_to(ROOT).as_posix() in bound, 'Missing lock member: '+path)
    return receipt['commit']


def source_check(source, spec):
    require(spec['fixed'] == FIXED and spec['unknown_category_options'] == list(OPTIONS), 'Changed categories')
    require(spec['productions'] == ['N -> NOUN', 'CLAUSE -> P0', 'CLAUSE -> P1 N', 'CLAUSE -> P2 N N', 'TEXT -> CLAUSE', 'TEXT -> CLAUSE TEXT'], 'Changed six productions')
    require(spec['same_whole_form_same_category'], 'Changed global category rule')
    require(spec['all_source_groups_required'] and not spec['line_boundaries_are_clause_boundaries'], 'Changed coverage')
    require(set(source['bindings']) == set(EXPECTED_BINDINGS), 'Source binding set')
    inputs = {}
    for key, item in source['bindings'].items():
        require(item['sha256'] == EXPECTED_BINDINGS[key] == sha(ROOT/item['path']), 'Primary hash: '+key)
        if key in ('original', 'offer', 'paragraphs'):
            inputs[key] = load(ROOT/item['path'])
    original, offer = inputs['original']['design'], inputs['offer']['design']
    require(source['frozen_seven_full_values'] == original['shared_whole_word_hypotheses'] == offer['fixed_seven_full_values'], 'Seven meanings changed')
    require(set(source['models']) == set(spec['models']), 'Model population')
    projected = [dict(locus=r['locus'], line_index=r['group'], word=r['raw'], source_id=f"PROJECTED|{r['locus']}|G{r['group']:03d}", original_alignment_status=r['status']) for r in original['all_group_alignment']]
    require(source['models']['PROJECTED_ZL']['groups'] == projected, 'Projection rows changed')
    for reader in ('ZL3b', 'IT2a'):
        name = 'DIPLOMATIC_'+reader
        selected = [p for p in inputs['paragraphs'][reader] if p['id'] == spec['selected_unit']]
        require(len(selected) == 1 and selected[0] == source['models'][name]['unit'], 'Whole native record: '+reader)
        unit = selected[0]
        require(unit['page'] == 'f83r' and unit['lines'][0]['start'] and unit['lines'][-1]['end'], 'Page/boundary')
        rows = [dict(locus=line['locus'], line_index=i, word=w, source_id=sid) for line in unit['lines'] for i, (w, sid) in enumerate(zip(line['words'], line['source_ids']), 1)]
        require(rows == source['models'][name]['groups'], 'Native rows: '+reader)
    sizes = {name: len(model['groups']) for name, model in source['models'].items()}
    require(sizes == {'PROJECTED_ZL': 72, 'DIPLOMATIC_ZL3b': 72, 'DIPLOMATIC_IT2a': 71}, 'Group counts')
    return sizes


def execute():
    commit = registration()  # All target loading/computation is below this gate.
    spec, source = load(EXP/'src/SPEC.json'), load(EXP/'src/SOURCE.json')
    sizes = source_check(source, spec)
    claimed, rows = load(ART/'RESULT.json'), load(ART/'ALL_ASSIGNMENTS.json')
    require(set(rows) == set(source['models']), 'Assignment model population')
    output = dict(status='PASS', public_commit=commit, oracle='Z3 sequential remaining-argument constraints', z3_version=z3.get_version_string(), source_group_counts=sizes, models={}, claim_ceiling='Necessary syntax only; no new meanings or independent confirmation.')
    streams = {}
    for name, model in source['models'].items():
        words = [r['word'] for r in model['groups']]
        streams[name] = words
        counts = Counter(words)
        recurrent = sorted(w for w, n in counts.items() if n > 1 and w not in FIXED)
        expected_keys = set(itertools.product(OPTIONS, repeat=len(recurrent)))
        seen, verified = set(), []
        for row in rows[name]:
            assignment = row['assignment']
            require(set(assignment) == set(recurrent), 'Recurrent assignment keys')
            key = tuple(assignment[w] for w in recurrent)
            require(key in expected_keys and key not in seen, 'Invalid/duplicate assignment')
            seen.add(key)
            paths = DebtOracle({name: words}, FIXED, assignment, full=True).count_full_assignments()
            prefix = DebtOracle({name: words}, FIXED, assignment).best_prefix(name)
            require(row['full_paths'] == paths and row['max_prefix'] == prefix['max_prefix'] and row['best_prefix_lengths'] == prefix['best_prefix_lengths'], 'Candidate mismatch: '+name+' '+str(key))
            verified.append(dict(assignment=assignment, full_paths=paths, **prefix))
        require(seen == expected_keys, 'Missing assignment rows')
        whole = DebtOracle({name: words}, FIXED, full=True).whole_status_and_core()
        require(whole['status'] != 'UNKNOWN_SOLVER', 'Full model unknown')
        best = DebtOracle({name: words}, FIXED).best_prefix(name, recurrent)
        expected = dict(status='FULL_UNSAT' if whole['status'] == 'UNSAT' else 'FULL_SAT', n_groups=len(words), n_types=len(counts), recurrent_unknowns=recurrent, assignments_checked=len(seen), total_full_paths=sum(r['full_paths'] for r in verified), **best)
        for key, value in expected.items():
            require(claimed['models'][name][key] == value, 'RESULT mismatch: '+name+'.'+key)
        for constraint in whole.get('core', []):
            if constraint['kind'] == 'ordered_token':
                constraint['source_id'] = model['groups'][constraint['position']-1]['source_id']
        output['models'][name] = dict(**expected, whole_constraint_result=whole, assignment_rows_verified=len(verified), unparsed_source_ids=[r['source_id'] for r in model['groups'][best['max_prefix']:]])
    joint = DebtOracle(streams, FIXED, full=True).whole_status_and_core()
    require(joint['status'] != 'UNKNOWN_SOLVER', 'Joint unknown')
    for constraint in joint.get('core', []):
        if constraint['kind'] == 'ordered_token':
            constraint['source_id'] = source['models'][constraint['model']]['groups'][constraint['position']-1]['source_id']
    primary_joint = claimed['joint']['status']
    if primary_joint == 'JOINT_REQUIRES_SHARED_SOLVER':
        require(all(row['status'] == 'FULL_SAT' for row in output['models'].values()), 'Premature pending joint status')
    else:
        require(joint['status'] in primary_joint.split('_'), 'Joint mismatch')
    output['joint'] = dict(**joint, primary_status=primary_joint)
    output['validator_sha256'] = sha(Path(__file__))
    (ART/'VALIDATION.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status='PASS', models={k: v['status'] for k, v in output['models'].items()}, joint=joint['status']), sort_keys=True))


def self_test():
    # Invented symbols only. No source/spec/proposal/manuscript stream loaded.
    fixed = {'entity': -1, 'state': 0, 'unary': 1, 'binary': 2}
    cases = [(['state'], True, 1), (['entity'], False, 0), (['unary', 'entity'], True, 2), (['binary', 'entity', 'entity'], True, 3), (['binary', 'entity'], False, 0), (['unary', 'state'], False, 0), (['state', 'unary', 'entity'], True, 3), (['new'], False, 0), (['new', 'entity'], True, 2), (['new', 'entity', 'state', 'new', 'state'], False, 3)]
    for words, sat, endpoint in cases:
        result = DebtOracle({'toy': words}, fixed, full=True).whole_status_and_core()
        require((result['status'] == 'SAT') == sat, 'Synthetic SAT case')
        require(DebtOracle({'toy': words}, fixed).best_prefix('toy')['max_prefix'] == endpoint, 'Synthetic prefix case')
    left, right = ['x', 'entity'], ['x', 'entity', 'entity']
    require(DebtOracle({'left': left}, fixed, full=True).whole_status_and_core()['status'] == 'SAT', 'Left toy')
    require(DebtOracle({'right': right}, fixed, full=True).whole_status_and_core()['status'] == 'SAT', 'Right toy')
    require(DebtOracle({'left': left, 'right': right}, fixed, full=True).whole_status_and_core()['status'] == 'UNSAT', 'Shared toy')
    require(DebtOracle({'toy': ['x', 'y', 'z', 'entity']}, fixed, full=True).count_full_assignments() == 1, 'Toy exact path count')
    print(json.dumps(dict(status='PASS', checks=24, scope='Invented symbols only; no target files or sequences loaded.')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--self-test', action='store_true')
    mode.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    self_test() if args.self_test else execute()
