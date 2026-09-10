#!/usr/bin/env python3
"""Independent Z3 lexical projection domains; never imports the primary search.
Only the frozen SOURCE/TARGET/RESULT JSON inputs are read.
"""
import collections
import hashlib
import itertools
import json
from pathlib import Path
import time
import z3

EXP = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def brute(source, target):
    atoms = sorted(set(source))
    words = sorted(set(target))
    for values in itertools.permutations(words, len(atoms)):
        mapping = dict(zip(atoms, values))
        inverse = {v:k for k,v in mapping.items()}
        if [inverse[x] for x in target if x in inverse] == source:
            return True
    return False


def feasible(source, target, timeout_ms=10000):
    """Exact type assignment with ordinal occurrence position constraints."""
    multiplicity = collections.Counter(source)
    positions = collections.defaultdict(list)
    for pos, word in enumerate(target):
        positions[word].append(pos)
    atoms, words = sorted(multiplicity), sorted(positions)
    word_ids = {w:i for i,w in enumerate(words)}
    candidates = {a:[w for w in words if len(positions[w]) == multiplicity[a]] for a in atoms}
    source_counts = collections.Counter(multiplicity.values())
    target_counts = collections.Counter(map(len, positions.values()))
    # Necessary Hall condition within the disjoint exact-count candidate classes.
    if any(target_counts[k] < n for k,n in source_counts.items()):
        return {'status':'UNSAT','proof':'EXACT_MULTIPLICITY_CLASS_CAPACITY'}
    solver = z3.Solver()
    solver.set(timeout=timeout_ms, random_seed=0)
    variables = {a:z3.Int('type_'+str(i)) for i,a in enumerate(atoms)}
    solver.add(z3.Distinct(list(variables.values())))
    for a in atoms:
        solver.add(z3.Or([variables[a] == word_ids[w] for w in candidates[a]]))
    occurrences = collections.Counter()
    stream_positions = []
    for i,a in enumerate(source):
        ordinal = occurrences[a]
        occurrences[a] += 1
        p = z3.Int('position_'+str(i))
        solver.add(z3.Or([z3.And(variables[a] == word_ids[w], p == positions[w][ordinal]) for w in candidates[a]]))
        if stream_positions:
            solver.add(stream_positions[-1] < p)
        stream_positions.append(p)
    answer = solver.check()
    if answer == z3.unsat:
        return {'status':'UNSAT','proof':'Z3_EXACT_COUNT_ORDINAL_POSITION_CONSTRAINTS'}
    if answer == z3.unknown:
        return {'status':'UNKNOWN','reason':solver.reason_unknown()}
    model = solver.model()
    mapping = {a:words[model.eval(variables[a]).as_long()] for a in atoms}
    reverse = {v:k for k,v in mapping.items()}
    assert len(reverse) == len(mapping)
    assert [reverse[w] for w in target if w in reverse] == source
    return {'status':'SAT','mapping':mapping}


def self_test():
    tests = []
    # Exhaust every binary source length1..3 against every ternary target
    # length0..4; brute oracle enumerates whole injective type maps.
    count = positives = 0
    for ns in range(1,4):
        for source in itertools.product('ab', repeat=ns):
            for nt in range(5):
                for target in itertools.product('xyz', repeat=nt):
                    expected = brute(list(source), list(target))
                    result = feasible(list(source), list(target))
                    assert result['status'] != 'UNKNOWN'
                    assert (result['status']=='SAT') == expected, (source,target,result,expected)
                    count += 1
                    positives += expected
    tests.append({'name':'exhaustive_binary_source_ternary_target','pairs':count,'satisfiable':positives,'unsatisfiable':count-positives,'oracle':'brute injective type maps and total projection'})
    return tests


def run():
    tests = self_test()
    source_path = EXP/'artifacts/SOURCE.json'
    target_path = EXP/'artifacts/TARGET.json'
    result_path = EXP/'artifacts/RESULT.json'
    if not target_path.exists() or not result_path.exists():
        print(json.dumps({'synthetic_tests':'PASS','details':tests,'waiting_for_frozen_inputs':True}))
        return
    source = json.loads(source_path.read_text())
    target = json.loads(target_path.read_text())
    primary = json.loads(result_path.read_text())
    sources = {r['id']:r['lexical'] for r in source['records']}
    assert len(sources) == primary['source_records'] == 38
    panels = {}
    all_unsat = True
    started = time.monotonic()
    for name, reported in primary['panels'].items():
        paragraphs = target['panels'][name]
        assert len(paragraphs) == reported['target_records']
        assert len({p['paragraph_id'] for p in paragraphs}) == len(paragraphs)
        assert len({p['physical_folio'] for p in paragraphs}) == reported['target_leaves']
        for p in paragraphs:
            assert len(p['words']) == len(p['loci']) == len(p['source_group_ids'])
            assert int(p['physical_folio'][1:]) % 2 == 1
            assert not p['page'].startswith('f84')
        zero = reported['zero_domain_sources']
        selected = ['P02','R02'] if name == 'IT2a' else [zero[0]]
        if 'R24' in zero and 'R24' not in selected:
            selected.append('R24')
        panel_results = {}
        for sid in selected:
            assert sid in zero and sid not in reported['sources_with_unknown']
            assert sum(reported['local_counts'][sid].values()) == len(paragraphs)
            assert not any(k.startswith(('SAT','UNKNOWN')) for k in reported['local_counts'][sid])
            checks = []
            for p in paragraphs:
                r = feasible(sources[sid],p['words'])
                if r['status'] != 'UNSAT':
                    all_unsat = False
                checks.append(dict(paragraph_id=p['paragraph_id'],source_length=len(sources[sid]),target_length=len(p['words']),source_distinct=len(set(sources[sid])),target_distinct=len(set(p['words'])),**r))
            counts = dict(collections.Counter(r['status'] for r in checks))
            panel_results[sid] = {'counts':counts,'proof_counts':dict(collections.Counter(r.get('proof',r['status']) for r in checks)),'all_target_pairs_checked':len(checks)==len(paragraphs),'pairs':checks}
            print(json.dumps({'panel':name,'source':sid,'counts':counts}),flush=True)
        panels[name] = {'candidate_paragraphs':len(paragraphs),'mandatory38_record_capacity':len(paragraphs)>=38,'selected_zero_witnesses':panel_results}
    output = {
        'schema':'GDT904_INDEPENDENT_Z3_DOMAIN_VALIDATION_V1','status':'PASS' if all_unsat else 'NOT_CONFIRMED',
        'source_sha256':sha(source_path),'target_sha256':sha(target_path),'primary_result_sha256':sha(result_path),'validator_sha256':sha(Path(__file__)),
        'engine':'Z3 '+z3.get_version_string(),'algorithm':'Exact-multiplicity type variables, injective AllDifferent, ordinal occurrence position tables and strict order; separate from primary occurrence DFS.',
        'synthetic_tests':tests,'panels':panels,'seconds':time.monotonic()-started,
        'claim_ceiling':'Independent exclusion proof for the selected mandatory zero-domain source records across every eligible candidate in each panel. Does not resolve other primary UNKNOWN pairs, find meanings, or establish relaxed-fit full-model compatibility.'
    }
    (EXP/'artifacts/DOMAIN_VALIDATION.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    assert all_unsat, 'Independent proof did not confirm every selected zero domain'
    print(json.dumps({'status':'PASS','seconds':output['seconds']}))


if __name__ == '__main__':
    run()
