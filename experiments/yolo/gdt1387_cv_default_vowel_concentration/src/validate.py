#!/usr/bin/env python3
"""Independent aggregate-code decoding; no primary imports or raw source reads."""
import hashlib
import itertools
import json
import math
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
SIGNS = set(('a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh'))
FOLLOWERS = {'cfh': ['a','d','e','o','s','y'], 'cph': ['a','d','e','k','o','y']}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def codec(head, followers, isolated_order):
    table = {}
    for c, sign in enumerate(sorted(followers)):
        table[(sign,)] = (c, 6)
        table[(head, sign)] = (c,)
    for v, sign in enumerate(isolated_order):
        table[(sign,)] = (6 + v,)
    remaining = sorted(SIGNS - {head} - set(followers) - set(isolated_order))
    assert len(remaining) == 12
    for sign, pair in zip(remaining, itertools.product(range(6), (7, 8))):
        table[(sign,)] = pair
    assert len(table) == 27
    assert len(set(table.values())) == 27
    assert all(6 not in table[(s,)] for s in remaining)
    return table


def check_bound(actual, numerator, denominator, signs, triples):
    frac = Fraction(numerator, denominator)
    witness_sign = min(signs)
    witness_triple = min(tuple(t) for t in triples if witness_sign in t)
    assert actual['numerator'] == numerator
    assert actual['denominator'] == denominator
    assert actual['reduced_numerator'] == frac.numerator
    assert actual['reduced_denominator'] == frac.denominator
    assert math.isclose(actual['percent'], float(frac * 100), rel_tol=1e-12, abs_tol=1e-12)
    assert actual['attaining_signs'] == sorted(signs)
    assert actual['witness'] == {'isolated_V0': witness_sign, 'vowel_triple': list(witness_triple)}


def main():
    lock = read(E / 'CODE_LOCK.json')
    datetime.fromisoformat(lock['locked_utc'].replace('Z', '+00:00'))
    locked = {row['path']: row['sha256'] for row in lock['files']}
    assert len(locked) == len(lock['files'])
    for relative, sha in locked.items():
        assert digest(ROOT / relative) == sha, relative
    for relative in ['src/run.py', 'src/validate.py', 'src/SPEC.json', 'METHOD.md']:
        assert str((E / relative).relative_to(ROOT)) in locked
    spec_path = E / 'src/SPEC.json'
    spec = read(spec_path)
    for pin in spec['pins']:
        assert digest(ROOT / pin['path']) == pin['sha256'], pin['path']
    counts = read(ROOT / spec['counts_source'])
    roles = read(ROOT / spec['roles_source'])
    projection_path = E / 'artifacts/INPUT_COUNTS.json'
    projection = read(projection_path)
    result = read(E / 'artifacts/RESULT.json')
    assert projection['experiment_id'] == result['experiment_id'] == 'GDT1387'
    assert projection['spec_sha256'] == result['spec_sha256'] == digest(spec_path)
    assert result['input_counts_sha256'] == digest(projection_path)
    assert result['status'] == 'EXACT_DEFAULT_VOWEL_BOUNDS'
    projection_sources = {s['path']:s['sha256'] for s in projection['sources']}
    for path, sha in projection_sources.items():
        assert digest(ROOT/path) == sha
    for key in ['counts_source','roles_source']:
        assert projection_sources[spec[key]] == digest(ROOT/spec[key])
        assert spec[key] in locked
    order = [(r['reader'],r['head']) for r in roles['cases']]
    assert order == [(reader,head) for reader in spec['readers'] for head in spec['heads']]
    assert [(r['reader'],r['head']) for r in projection['cases']] == order
    assert [(r['reader'],r['head']) for r in result['cases']] == order
    assert len(order) == 6
    receipts = []
    total_assignments = 0
    for role, projected, outcome in zip(roles['cases'],projection['cases'],result['cases']):
        reader, head = role['reader'], role['head']
        candidates = [r for r in counts['cases'] if (r['reader'],r['head']) == (reader,head)]
        assert len(candidates) == 1
        old = candidates[0]
        expected = {k:old[k] for k in ['reader','head','groups','types','active_groups','accepted_groups','failed_groups','failed_types','code_usage']}
        expected.update({k:role[k] for k in ['followers','eligible','vowel_sets']})
        expected['role_set_count'] = role['count']
        assert projected == expected
        assert old['groups'] == role['groups'] and old['types'] == role['types']
        assert old['active_groups'] == role['active_groups']
        assert old['failed_groups'] == old['failed_types'] == 0
        assert old['accepted_groups'] == old['groups']
        assert role['followers'] == FOLLOWERS[head]
        eligible = role['eligible']
        assert len(eligible) == len(set(eligible)) and len(eligible) >= 3
        assert set(eligible) <= SIGNS - {head} - set(role['followers'])
        triples = role['vowel_sets']
        assert triples == [list(t) for t in itertools.combinations(sorted(eligible),3)]
        assert role['count'] == len(triples)
        usages = {}
        singleton = {s:0 for s in sorted(SIGNS-{head})}
        prefix_count = glyph_count = raw_f_count = 0
        for row in old['code_usage']:
            code = tuple(row['units'])
            n = row['occurrences']
            assert isinstance(n,int) and n >= 0
            assert code not in usages
            usages[code] = n
            glyph_count += len(code)*n
            raw_f_count += sum(s in role['followers'] for s in code)*n
            if len(code) == 1:
                assert code[0] in singleton
                singleton[code[0]] += n
            else:
                assert len(code) == 2 and code[0] == head and code[1] in role['followers']
                prefix_count += n
        assert prefix_count >= old['active_groups']
        tallies = []
        values_by_sign = {s:set() for s in eligible}
        for triple in triples:
            for isolated in itertools.permutations(triple):
                table = codec(head, role['followers'], isolated)
                phones = Counter()
                for code,n in usages.items():
                    for phone in table[code]:
                        phones[phone] += n
                vowel_count = sum(phones[v] for v in (6,7,8))
                assert vowel_count == sum(singleton.values()) == glyph_count-2*prefix_count
                default_count = phones[6]
                assert default_count == raw_f_count-prefix_count+singleton[isolated[0]]
                tallies.append((default_count,vowel_count,isolated[0]))
                values_by_sign[isolated[0]].add(default_count)
        assert all(len(v)==1 for v in values_by_sign.values())
        assert len(tallies) == 6*len(triples)
        assert len({t[1] for t in tallies}) == 1
        den = tallies[0][1]
        low, high = min(t[0] for t in tallies), max(t[0] for t in tallies)
        low_signs = {t[2] for t in tallies if t[0] == low}
        high_signs = {t[2] for t in tallies if t[0] == high}
        check_bound(outcome['lower'],low,den,low_signs,triples)
        check_bound(outcome['upper'],high,den,high_signs,triples)
        for key in ['reader','head','groups','types','active_groups']:
            assert outcome[key] == old[key]
        assert outcome['singleton_usage'] == singleton
        assert outcome['glyph_units'] == glyph_count
        assert outcome['prefix_occurrences'] == prefix_count
        assert outcome['total_vowels'] == den
        assert outcome['fixed_V0'] == raw_f_count-prefix_count
        assert outcome['eligible_counts'] == {s:singleton[s] for s in eligible}
        assert outcome['forced_strict_majority'] is (2*low > den)
        total_assignments += len(tallies)
        receipts.append({'reader':reader,'head':head,'decoded_role_assignments':len(tallies),'lower_fraction':str(Fraction(low,den)),'upper_fraction':str(Fraction(high,den)),'forced_strict_majority':2*low>den})
    report = {'experiment_id':'GDT1387','status':'PASS','implementation_lock_utc':lock['locked_utc'],'cases':receipts,'decoded_role_assignments':total_assignments,
              'result_sha256':digest(E/'artifacts/RESULT.json'),'input_counts_sha256':digest(projection_path),'code_lock_sha256':digest(E/'CODE_LOCK.json'),
              'method':'Independent explicit aggregate-code decoding for every retained vowel triple and all six isolated-vowel assignments; no primary import or raw-group traversal.',
              'remaining_label_proof':'Permuting the six consonant labels changes no vowel count. All twelve remaining CV codes emit V1 or V2, never V0; their arbitrary bijection therefore changes neither V0 nor total vowels. Canonicality of role triples is inherited from1383, not re-established from aggregate counts.',
              'scope':'Occurrence-weighted1233eligible groups as counted by1248, not certificate-only types, full manuscript, language distribution, semantic or independent phonetic confirmation.'}
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,sort_keys=True))


if __name__ == '__main__':
    main()
