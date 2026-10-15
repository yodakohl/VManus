"""Exact six-case arithmetic from two immutable aggregate artifacts only."""
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())
UNITS = ('a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text())

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def bound(numerator, denominator, signs, triples):
    value = Fraction(numerator, denominator)
    selected = min(signs)
    triple = min(t for t in triples if selected in t)
    return dict(numerator=numerator, denominator=denominator,
                reduced_numerator=value.numerator, reduced_denominator=value.denominator,
                percent=float(100 * value), attaining_signs=sorted(signs),
                witness=dict(isolated_V0=selected, vowel_triple=triple))

def main():
    lock = load(EXP / 'CODE_LOCK.json')
    assert lock['locked_utc']
    locked = {p['path']: p['sha256'] for p in lock['files']}
    for path in [HERE/'run.py', HERE/'validate.py', HERE/'SPEC.json', EXP/'METHOD.md']:
        rel = str(path.relative_to(ROOT))
        assert rel in locked and sha(path) == locked[rel], rel
    for rel, expected in locked.items():
        assert sha(ROOT / rel) == expected, rel
    spec_path = HERE / 'SPEC.json'
    spec = load(spec_path)
    assert spec['experiment_id'] == 'GDT1387'
    for pin in spec['pins']:
        assert sha(ROOT / pin['path']) == pin['sha256'], pin['path']
    counts = load(ROOT / spec['counts_source'])
    roles = load(ROOT / spec['roles_source'])
    assert counts['experiment'] == 'GDT1248' and roles['experiment'] == 'GDT1383'
    expected_keys = {(r,h) for r in spec['readers'] for h in spec['heads']}
    selected_counts = [c for c in counts['cases'] if c['head'] in spec['heads'] and c['reader'] in spec['readers']]
    assert len(selected_counts) == len(roles['cases']) == len(expected_keys) == 6
    old_by_key = {(c['reader'],c['head']):c for c in selected_counts}
    assert set(old_by_key) == {(r['reader'],r['head']) for r in roles['cases']} == expected_keys
    inputs, results = [], []
    for role in roles['cases']:
        old = old_by_key[(role['reader'],role['head'])]
        assert old['decision'] == 'EXACT_MINIMUM_27'
        assert old['failed_groups'] == old['failed_types'] == 0 and not old['failure_ids']
        assert old['accepted_groups'] == old['groups']
        assert all(old[k] == role[k] for k in ['groups','types','active_groups'])
        assert role['status'] == 'MULTIPLE_ROLE_CLASSES'
        head, followers, eligible = role['head'], role['followers'], role['eligible']
        assert len(followers) == 6 and len(set(followers)) == 6
        assert not (set(eligible) & (set(followers) | {head}))
        assert len(eligible) == len(set(eligible)) >= 3
        assert sorted(role['vowel_sets']) == [list(t) for t in itertools.combinations(sorted(eligible),3)]
        assert role['count'] == len(role['vowel_sets'])
        codes = {tuple(c['units']):c['occurrences'] for c in old['code_usage']}
        assert len(codes) == len(old['code_usage'])
        assert all(type(n) is int and n >= 0 for n in codes.values())
        assert set(codes) <= {(u,) for u in UNITS if u != head} | {(head,f) for f in followers}
        assert {code[1] for code in codes if len(code)==2} == set(followers)
        single = {u:codes.get((u,),0) for u in sorted(UNITS) if u != head}
        n = sum(len(code)*v for code,v in codes.items())
        h = sum(v for code,v in codes.items() if len(code)==2)
        vowels = sum(single.values())
        assert vowels == n-2*h and vowels > 0
        fixed = sum(single[f] for f in followers)
        eligible_counts = {s:single[s] for s in sorted(eligible)}
        minimum, maximum = min(eligible_counts.values()), max(eligible_counts.values())
        base_fields = {k:old[k] for k in ['reader','head','groups','types','active_groups']}
        inputs.append(dict(**base_fields, accepted_groups=old['accepted_groups'], failed_groups=old['failed_groups'],
                           failed_types=old['failed_types'], code_usage=old['code_usage'], followers=followers,
                           eligible=eligible, vowel_sets=role['vowel_sets'], role_set_count=role['count']))
        results.append(dict(**base_fields, singleton_usage=single, glyph_units=n, prefix_occurrences=h,
                            total_vowels=vowels, fixed_V0=fixed, eligible_counts=eligible_counts,
                            lower=bound(fixed+minimum,vowels,[s for s,v in eligible_counts.items() if v==minimum],role['vowel_sets']),
                            upper=bound(fixed+maximum,vowels,[s for s,v in eligible_counts.items() if v==maximum],role['vowel_sets']),
                            forced_strict_majority=2*(fixed+minimum)>vowels))
    artifacts = EXP/'artifacts'
    input_path = artifacts/'INPUT_COUNTS.json'
    source_pins = [p for p in spec['pins'] if p['path'] in {spec['counts_source'],spec['roles_source']}]
    write(input_path,dict(experiment_id='GDT1387',spec_sha256=sha(spec_path),sources=source_pins,cases=inputs))
    result = dict(experiment_id='GDT1387',spec_sha256=sha(spec_path),input_counts_sha256=sha(input_path),
                  status='EXACT_DEFAULT_VOWEL_BOUNDS',cases=results,
                  limits=['Exact obligations for source words represented by the GDT1233 selected occurrence population, not 1233 words.',
                          'Anonymous V0 is not a pronunciation or Latin a. Different readers are alternatives of one manuscript.',
                          'Counts are occurrence-weighted; no original groups or new native source were read.',
                          'No Markov assumption, phoneme table enumeration, rhyme, word-final analysis or language fit.',
                          'No extrapolation to the whole manuscript or a complete language. All source/working-unit/word-boundary assumptions remain.',
                          'Extrema are attained; remaining CV-table permutations do not affect V0 count. No key is preferred.'])
    write(artifacts/'RESULT.json',result)
    print(json.dumps(dict(status=result['status'],cases=len(results),
                          forced_majority_cases=sum(c['forced_strict_majority'] for c in results)),sort_keys=True))

if __name__ == '__main__':
    main()
