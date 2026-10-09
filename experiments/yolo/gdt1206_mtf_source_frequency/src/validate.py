"""Independent timestamp MTF source/recovery/count verification; no runner import."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import string

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D/'artifacts'
SOURCE = ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET = ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
PROPOSAL = ROOT/'research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_MOVABLE_LETTER_RANK_RAW_20261005.json'


def independent_encode(words, extra):
    seen = {c: -1 for c in string.ascii_lowercase}
    time = 0
    groups = []
    for word in words:
        group = []
        for char in word:
            if char in seen:
                rank = sum(seen[c] > seen[char] or (seen[c] == seen[char] and c < char) for c in seen)
                group.append(rank)
                seen[char] = time
                time += 1
            else:
                group.append(26+extra.index(char))
        groups.append(group)
    return groups


def independent_decode(groups, extra):
    seen = {c: -1 for c in string.ascii_lowercase}
    time = 0
    recovered = []
    for group in groups:
        letters = []
        for unit in group:
            assert type(unit) is int and 0 <= unit < 26+len(extra)
            if unit >= 26:
                char = extra[unit-26]
            else:
                order = sorted(seen, key=lambda c: (-seen[c], c))
                char = order[unit]
                seen[char] = time
                time += 1
            letters.append(char)
        recovered.append(''.join(letters))
    return recovered


def statistics(records, key):
    histogram = Counter()
    remaining = 8000
    pairs = repeats = 0
    for record in records:
        words = record[key][:remaining]
        if key == 'groups':
            words = [tuple(g) for g in words]
        histogram.update(words)
        remaining -= len(words)
        if words:
            pairs += len(words)-1
            repeats += sum(words[i] == words[i-1] for i in range(1,len(words)))
        if remaining == 0:
            break
    assert remaining == 0
    top = sum(v for _,v in histogram.most_common(10))
    return dict(tokens=8000,types=len(histogram),type_ratio=len(histogram)/8000,
                top10_count=top,top10_share=top/8000,adjacent_pairs=pairs,
                exact_repeat_count=repeats,exact_repeat=repeats/pairs),histogram


def main():
    lock = json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for path, digest in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest,path
    receipt = json.loads((A/'RUN_RECEIPT.json').read_text())
    assert datetime.fromisoformat(lock['registered_utc']) < datetime.fromisoformat(receipt['completed_utc'])
    assert receipt['runner_sha256'] == hashlib.sha256((D/'src/run.py').read_bytes()).hexdigest()
    assert receipt['writer_sha256'] == hashlib.sha256((D/'src/writer.py').read_bytes()).hexdigest()
    assert receipt['source_sha256'] == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    source = json.loads(SOURCE.read_text())
    target = json.loads(TARGET.read_text())['targets']
    extra = json.loads(PROPOSAL.read_text())['input_contract']['additional_characters_in_order']
    assert len(extra) == len(set(extra)) == 56
    result = json.loads((A/'RESULT.json').read_text())
    if result['status'] == 'COVERAGE_FAILURE':
        raise AssertionError('Coverage failure requires separate source review; no frequency validation')
    fixtures = [['a'],['aa'],['abb']*3,['neu']+['xylophon']*3,['Ä','7',',','a','a']]
    for words in fixtures:
        groups = independent_encode(words, extra)
        assert independent_decode(groups, extra) == words
        for word, group in zip(words, groups):
            for i in range(1,len(word)):
                if word[i] == word[i-1] and word[i] in string.ascii_lowercase:
                    assert group[i] == 0
    for word in ['a','aa','abb','xylophon','Ä','a7a']:
        triple = independent_encode([word]*3, extra)
        assert triple[1] == triple[2]
    recipes = words_count = units = conditions = 0
    all_passed = True
    for book in ('b4','w1','bs1','gr1'):
        encoded = json.loads((A/('ENCODED_'+book+'.json')).read_text())
        assert len(encoded) == len(source[book])
        for native, written in zip(source[book], encoded):
            assert native['id'] == written['id']
            assert independent_decode(written['groups'], extra) == native['words']
            assert independent_encode(native['words'], extra) == written['groups']
            assert len(native['words']) == len(written['groups'])
            recipes += 1
            words_count += len(native['words'])
            units += sum(len(g) for g in written['groups'])
        observed,histogram = statistics(encoded,'groups')
        baseline,_ = statistics(source[book],'words')
        book_result = result['books'][book]
        assert book_result['metrics'] == observed
        assert book_result['source_baseline'] == baseline
        freq = json.loads((A/('FREQUENCIES_'+book+'.json')).read_text())
        assert len(freq) == len(histogram)
        assert {tuple(row['units']):row['count'] for row in freq} == histogram
        expected_receipts = dict(recipes=len(source[book]),source_words=sum(len(r['words']) for r in source[book]),
            source_characters=sum(len(w) for r in source[book] for w in r['words']),
            emitted_units=sum(len(g) for r in encoded for g in r['groups']))
        assert expected_receipts == book_result['receipts']
        assert expected_receipts['source_characters'] == expected_receipts['emitted_units']
        book_pass = True
        for reader,t in target.items():
            expected = {}
            for metric,model_count,model_den,target_count,target_den,tol in [
                ('type_ratio',observed['types'],8000,t['types'],8000,20),
                ('top10_share',observed['top10_count'],8000,round(t['top10_share']*8000),8000,20),
                ('exact_repeat',observed['exact_repeat_count'],observed['adjacent_pairs'],
                 round(t['exact_repeat']*t['adjacent_pairs']),t['adjacent_pairs'],100)]:
                assert abs(target_count/target_den-t[metric])<1e-12
                # Integer cross-product rather than the runner's Fraction comparison.
                passed = abs(model_count*target_den-target_count*model_den)*tol <= model_den*target_den
                expected[metric] = dict(model_count=model_count,model_denominator=model_den,
                    target_count=target_count,target_denominator=target_den,
                    tolerance_numerator=1,tolerance_denominator=tol,passed=passed)
                conditions += 1
            expected['passed'] = all(v['passed'] for v in expected.values())
            assert book_result['reader_conditions'][reader] == expected
            book_pass &= expected['passed']
        assert book_result['passed'] == book_pass
        all_passed &= book_pass
    assert result['all_books_pass'] == all_passed
    assert result['status'] == ('MTF_FREQUENCY_SCREEN_PASS' if all_passed else 'MTF_FREQUENCY_SCREEN_FAIL')
    assert result['complete_recipe_roundtrips'] == recipes
    assert result['complete_source_words'] == words_count
    assert result['ordinary_rank_units'] == 26 and result['auxiliary_units'] == 56
    assert result['native_word_meanings'] == result['independent_confirmation'] == 0
    validation = dict(status='PASS',complete_recipes=recipes,complete_words=words_count,
        complete_units=units,metric_conditions=conditions,scientific_status=result['status'],
        source_and_inverse='Independent timestamp forward/reverse without runner import; inverse state from recovered output only',
        same_author=True,native_semantics_validated=False,human_practicality_validated=False,
        validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (A/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(validation,indent=2))


if __name__ == '__main__':
    main()
