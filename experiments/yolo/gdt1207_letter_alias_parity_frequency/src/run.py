"""Necessary equality-frequency screen for one frozen source ALT writer."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from datetime import datetime, timezone
import hashlib
import json
import string
from writer import encode, decode

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D / 'artifacts'
SOURCE = ROOT / 'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET = ROOT / 'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
PROPOSAL = ROOT / 'research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_PER_LETTER_ALTERNATORS_RAW_20261005.json'
BOOKS = ('b4', 'w1', 'bs1', 'gr1')
N = 8000


def dump(name, value, compact=False):
    (A / name).write_text(json.dumps(value, ensure_ascii=False,
        indent=None if compact else 2, separators=(',', ':') if compact else None) + '\n')


def measure(segments):
    sample = []
    left = N
    for segment in segments:
        part = segment[:left]
        if part:
            sample.append(part)
            left -= len(part)
        if not left:
            break
    assert left == 0
    counts = Counter(w for segment in sample for w in segment)
    pairs = sum(len(segment) - 1 for segment in sample)
    repeats = sum(a == b for segment in sample for a, b in zip(segment, segment[1:]))
    top = sum(sorted(counts.values(), reverse=True)[:10])
    metrics = dict(tokens=N, types=len(counts), type_ratio=len(counts)/N,
        top10_count=top, top10_share=top/N, adjacent_pairs=pairs,
        exact_repeat_count=repeats, exact_repeat=repeats/pairs)
    return metrics, counts


def compare(metrics, target):
    fields = [('type_ratio', metrics['types'], N, target['types'], N, 20),
              ('top10_share', metrics['top10_count'], N,
               round(target['top10_share']*N), N, 20),
              ('exact_repeat', metrics['exact_repeat_count'], metrics['adjacent_pairs'],
               round(target['exact_repeat']*target['adjacent_pairs']), target['adjacent_pairs'], 100)]
    result = {}
    for name, mc, md, tc, td, divisor in fields:
        assert abs(tc/td-target[name]) < 1e-12
        result[name] = dict(model_count=mc, model_denominator=md, target_count=tc,
            target_denominator=td, tolerance_numerator=1, tolerance_denominator=divisor,
            passed=abs(Fraction(mc, md)-Fraction(tc, td)) <= Fraction(1, divisor))
    result['passed'] = all(x['passed'] for x in result.values())
    return result


def main():
    lock = json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for path, expected in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
    source = json.loads(SOURCE.read_text())
    targets = json.loads(TARGET.read_text())['targets']
    extra = json.loads(PROPOSAL.read_text())['input_contract']['additional_characters_in_order']
    assert len(extra) == len(set(extra)) == 56
    assert all(t['tokens'] == N for t in targets.values())
    unseen = Counter(c for b in BOOKS for r in source[b] for w in r['words'] for c in w
                     if c not in string.ascii_lowercase and c not in extra)
    if unseen:
        result = dict(experiment='GDT1207', status='COVERAGE_FAILURE', unlisted_characters=dict(unseen))
        dump('RESULT.json', result)
        print(json.dumps(result, ensure_ascii=False))
        return
    fixtures = [['a'], ['aa'], ['abb']*3, ['abba']*3,
                ['neu']+['xylophon']*3, ['Ä','7',',','a','a'], ['aÄa']*3]
    for words in fixtures:
        assert decode(encode(words, extra), extra) == words
    for word in ['a','aa','abb','abba','xylophon','Ä','aÄa']:
        groups = encode([word]*3, extra)
        assert groups[0] == groups[2]
        even = all(n % 2 == 0 for c,n in Counter(word).items() if c in string.ascii_lowercase)
        assert (groups[0] == groups[1]) == even
    assert encode(['a','a','a'], extra) == [[0],[1],[0]]
    try:
        decode([[0,0]], extra)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid double same alias accepted')
    books = {}
    total_recipes = total_words = 0
    for book in BOOKS:
        encoded = []
        for recipe in source[book]:
            groups = encode(recipe['words'], extra)
            assert decode(groups, extra) == recipe['words']
            encoded.append(dict(id=recipe['id'], groups=groups))
        metrics, counts = measure([[tuple(g) for g in r['groups']] for r in encoded])
        baseline, _ = measure([r['words'] for r in source[book]])
        comparisons = {ed: compare(metrics, t) for ed, t in targets.items()}
        receipts = dict(recipes=len(encoded), source_words=sum(len(r['words']) for r in source[book]),
            source_characters=sum(len(w) for r in source[book] for w in r['words']),
            emitted_units=sum(len(g) for r in encoded for g in r['groups']))
        assert receipts['source_characters'] == receipts['emitted_units']
        books[book] = dict(metrics=metrics, source_baseline=baseline, receipts=receipts,
            reader_conditions=comparisons, passed=all(c['passed'] for c in comparisons.values()))
        total_recipes += receipts['recipes']
        total_words += receipts['source_words']
        dump('ENCODED_'+book+'.json', encoded, compact=True)
        dump('FREQUENCIES_'+book+'.json', [dict(units=list(k), count=v) for k,v in sorted(counts.items())], compact=True)
    passed = all(b['passed'] for b in books.values())
    result = dict(experiment='GDT1207', status='ALT_FREQUENCY_SCREEN_PASS' if passed else 'ALT_FREQUENCY_SCREEN_FAIL',
        books=books, all_books_pass=passed, complete_recipe_roundtrips=total_recipes,
        complete_source_words=total_words, ordinary_alias_units=52, auxiliary_units=56,
        native_word_meanings=0, independent_confirmation=0,
        scope='Known-source fixed-letter ALT and necessary equality-frequency metrics only; no rendered carrier, native morphology, word meaning or historical attestation.')
    dump('RESULT.json', result)
    dump('RUN_RECEIPT.json', dict(completed_utc=datetime.now(timezone.utc).isoformat(),
        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        writer_sha256=hashlib.sha256((D/'src/writer.py').read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(), fixtures=fixtures))
    print(json.dumps(dict(status=result['status'], books={b:r['metrics'] for b,r in books.items()},
                         complete_recipe_roundtrips=total_recipes, complete_source_words=total_words), indent=2))


if __name__ == '__main__':
    main()
