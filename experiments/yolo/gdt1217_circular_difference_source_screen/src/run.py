"""Five necessary fixed-ring source metrics, all full-source inverse receipts."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from datetime import datetime, timezone
import hashlib
import json
import math
import string
from writer import encode, decode

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D / 'artifacts'
SOURCE = 'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET = 'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
RAW = 'research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_CIRCULAR_LETTER_DIFFERENCE_RAW_20261005.json'
BOOKS = ('b4', 'w1', 'bs1', 'gr1')
N = 8000


def canon(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canon(value)).hexdigest()


def dump(name, value):
    (A/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def moments(hist):
    count = sum(hist.values())
    mu = F(sum(int(k)*v for k, v in hist.items()), count)
    var = F(sum(int(k)**2*v for k, v in hist.items()), count) - mu**2
    return mu, var


def measure(segments):
    left = N
    sample = []
    for segment in segments:
        if left == 0:
            break
        part = segment[:left]
        if part:
            sample.append(part)
            left -= len(part)
    assert left == 0
    counts = Counter(tuple(g) for seg in sample for g in seg)
    hist = Counter(len(g) for seg in sample for g in seg)
    mu, var = moments(hist)
    pairs = sum(len(seg)-1 for seg in sample)
    repeats = sum(a == b for seg in sample for a, b in zip(seg, seg[1:]))
    top = sum(sorted(counts.values(), reverse=True)[:10])
    return dict(tokens=N, types=len(counts), type_ratio=len(counts)/N,
        top10_count=top, top10_share=top/N, adjacent_pairs=pairs,
        exact_repeat_count=repeats, exact_repeat=repeats/pairs,
        mean_length=float(mu), sd_length=math.sqrt(var),
        length_counts={str(k): v for k, v in sorted(hist.items())},
        frequency_counts={str(k): v for k, v in sorted(Counter(counts.values()).items())},
        sample_sequence_hash=digest(sample))


def compare(model, target):
    mt, tt = model['tokens'], target['tokens']
    assert mt == tt == N
    tc = round(target['top10_share']*tt)
    tr = round(target['exact_repeat']*target['adjacent_pairs'])
    assert abs(tc/tt-target['top10_share']) < 1e-12
    assert abs(tr/target['adjacent_pairs']-target['exact_repeat']) < 1e-12
    mm, mv = moments(model['length_counts'])
    tm, tv = moments(target['length_counts'])
    assert abs(float(tm)-target['mean_length']) < 1e-10
    assert abs(math.sqrt(tv)-target['sd_length']) < 1e-10
    checks = dict(type_ratio=abs(F(model['types'], mt)-F(target['types'], tt)) <= F(1,20),
        top10_share=abs(F(model['top10_count'], mt)-F(tc, tt)) <= F(1,20),
        exact_repeat=abs(F(model['exact_repeat_count'], model['adjacent_pairs'])-
                         F(tr, target['adjacent_pairs'])) <= F(1,100),
        mean_length=F(4,5)*tm <= mm <= F(6,5)*tm,
        sd_length=F(9,16)*tv <= mv <= F(25,16)*tv)
    return dict(checks=checks, passed=all(checks.values()))


def fixtures(raw, escapes):
    ex = raw['design']['complete_invented_example']
    glyphs = raw['design']['output_glyphs_by_distance_0_to_21']
    words = ex['source'].split(' ')
    encoded = encode(words, escapes)
    assert [[glyphs[d] for d in g] for g in encoded] == ex['output_working_glyph_words']
    assert decode(encoded, escapes) == words
    alphabet = list(string.ascii_lowercase[:21])+escapes
    for start in range(21):
        for c in alphabet:
            assert decode(encode([c], escapes, start), escapes, start) == [c]
    for word in ['a', 'aa', 'abb', 'xylophon', 'Ä', 'a7a']:
        groups = encode([word]*3, escapes)
        assert groups[1] == groups[2]
    bad_units = [[21], [21,0], [21,21,0], [21,0,21], [21,2,19]]
    for units in bad_units:
        last = 0
        distances = []
        for u in units:
            distances.append((u-last)%22)
            last = u
        try:
            decode([distances], escapes)
        except ValueError:
            pass
        else:
            raise AssertionError('malformed escape accepted')
    return dict(character_entries=21*len(alphabet), malformed_escape_cases=len(bad_units),
                hand_example=encoded, repeated_word_fixtures=6)


def main():
    lock = json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for path, expected in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
    raw = json.loads((ROOT/RAW).read_text())
    escapes = raw['design']['plain_unit_ring']['escape_characters_in_order']
    assert len(escapes) == len(set(escapes)) == 61
    source = json.loads((ROOT/SOURCE).read_text())
    targets = json.loads((ROOT/TARGET).read_text())['targets']
    allowed = set(string.ascii_lowercase[:21]) | set(escapes)
    missing = Counter(c for b in BOOKS for r in source[b] for w in r['words'] for c in w if c not in allowed)
    if missing:
        dump('RESULT.json', dict(experiment='GDT1217', status='COVERAGE_FAILURE', unsupported=dict(missing)))
        print('COVERAGE_FAILURE')
        return
    fixture_receipt = fixtures(raw, escapes)
    books = {}
    receipts = []
    for b in BOOKS:
        segments = []
        for recipe in source[b]:
            encoded = encode(recipe['words'], escapes)
            assert decode(encoded, escapes) == recipe['words']
            segments.append(encoded)
            receipts.append(dict(book=b, id=recipe['id'], words=len(encoded),
                source_characters=sum(map(len, recipe['words'])),
                written_signs=sum(map(len, encoded)), encoded_sha256=digest(encoded)))
        metrics = measure(segments)
        comparisons = {ed: compare(metrics, target) for ed, target in targets.items()}
        books[b] = dict(metrics=metrics, reader_conditions=comparisons,
                        passed=all(c['passed'] for c in comparisons.values()))
    total_words = sum(r['words'] for r in receipts)
    assert len(receipts) == 1054 and total_words == 80931
    passed = all(b['passed'] for b in books.values())
    result = dict(experiment='GDT1217', status='FIXED_RING_NECESSARY_SCREEN_PASS' if passed else
                  'FIXED_RING_NECESSARY_SCREEN_FAIL', books=books, all_books_pass=passed,
        complete_recipe_roundtrips=len(receipts), complete_source_words=total_words,
        source_characters=sum(r['source_characters'] for r in receipts),
        emitted_working_signs=sum(r['written_signs'] for r in receipts),
        native_word_meanings=0, independent_confirmation=0,
        scope='Fixed source/ring/reset and five necessary metrics only; not a native inverse or general language exclusion.')
    dump('RESULT.json', result)
    dump('RECIPE_RECEIPTS.json', receipts)
    dump('RUN_RECEIPT.json', dict(completed_utc=datetime.now(timezone.utc).isoformat(), fixtures=fixture_receipt))
    print(json.dumps(dict(status=result['status'], recipes=len(receipts), words=total_words,
        books={b:{k:v for k,v in r['metrics'].items() if k not in ('length_counts','frequency_counts','sample_sequence_hash')}
               for b,r in books.items()}, failures={b:{ed:[k for k,v in c['checks'].items() if not v]
               for ed,c in r['reader_conditions'].items()} for b,r in books.items()}), indent=2))


if __name__ == '__main__':
    main()
