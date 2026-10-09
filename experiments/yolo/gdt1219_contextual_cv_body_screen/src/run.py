"""Fixed contextual CV source screen; inherited five-metric arithmetic."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from datetime import datetime, timezone
import hashlib
import json
import math
import string
from writer import encode, decode, train, VOWELS, ROWS

D=Path(__file__).resolve().parents[1]
ROOT=D.parents[2]
A=D/'artifacts'
SOURCE='experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET='experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
CONTRACT='research_registry/proposals/production_origin_supply_20261003/HAND_WRITER_CONTEXT_CV_CONTRACT_20261006.json'
BOOKS=('b4','w1','bs1','gr1')
N=8000

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


def fixtures(extras, table):
    fallback={s:{b: ('a' if b=='@' else '') for b in ROWS} for s in VOWELS}
    words=['lege','lege','salz.']
    expected=[[7,20,20,4,20,20],[7,20,20,4,20,20],[13,20,7,17,19,1,3,0,14]]
    assert encode(words,extras,fallback)==expected
    assert decode(expected,extras,fallback)==words
    cases=[*string.ascii_lowercase,*extras,'nara','aei','aa','bb','jawa','a7a','xylophon',
        'bcdfghjklmnpqrstvwxz','überÄ.','abcdefghijklmnopqrstuvwxyz'*4]
    for tab in [fallback,table]:
        for start in VOWELS:
            for word in cases:
                groups=encode([word]*3,extras,tab,start)
                assert decode(groups,extras,tab,start)==[word]*3
                assert groups[1]==groups[2]
    bad=[[],[19],[19,0],[19,1],[19,1,5],[19,1,3,18,18],[0,20,21],
         [0,20,20,20,20],[18,20],[18,20,20],[19,1,3,0],[22]]
    # [18,20] selects NONE for the fallback carrier; [18,20,20]
    # is a noncanonical explicit initial carrier for the nondefault vowel e.
    for group in bad:
        try:
            decode([group],extras,fallback)
        except ValueError:
            pass
        else:
            raise AssertionError('accepted bad group '+str(group))
    return dict(roundtrip_fixtures=2*6*len(cases),bad_groups=len(bad),manual_example=expected)


def main():
    for path,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    contract=json.loads((ROOT/CONTRACT).read_text())
    extras=contract['input']['additional_characters']
    source=json.loads((ROOT/SOURCE).read_text())
    allowed=set(string.ascii_lowercase)|set(extras)
    missing=Counter(c for b in BOOKS for r in source[b] for w in r['words'] for c in w if c not in allowed)
    if missing:
        dump('RESULT.json',dict(experiment='GDT1219',status='COVERAGE_FAILURE',unsupported=dict(missing)))
        print('COVERAGE_FAILURE');return
    table,event_counts=train(source,extras)
    dump('DEFAULT_TABLE.json',dict(table=table,event_counts=event_counts,rows=126,trained_books=['b4','w1']))
    fixture_receipt=fixtures(extras,table)
    targets=json.loads((ROOT/TARGET).read_text())['targets']
    books={};receipts=[]
    for book in BOOKS:
        segments=[]
        for recipe in source[book]:
            groups=encode(recipe['words'],extras,table)
            assert decode(groups,extras,table)==recipe['words']
            segments.append(groups)
            receipts.append(dict(book=book,id=recipe['id'],words=len(groups),
                source_characters=sum(map(len,recipe['words'])),written_signs=sum(map(len,groups)),
                encoded_sha256=digest(groups)))
        metrics=measure(segments)
        comparisons={ed:compare(metrics,t) for ed,t in targets.items()}
        books[book]=dict(metrics=metrics,reader_conditions=comparisons,
            passed=all(c['passed'] for c in comparisons.values()))
    assert len(receipts)==1054 and sum(r['words'] for r in receipts)==80931
    passed=all(b['passed'] for b in books.values())
    result=dict(experiment='GDT1219',status='CONTEXT_CV_NECESSARY_SCREEN_PASS' if passed else
        'CONTEXT_CV_NECESSARY_SCREEN_FAIL',books=books,all_books_pass=passed,
        complete_recipe_roundtrips=len(receipts),complete_source_words=80931,
        source_characters=sum(r['source_characters'] for r in receipts),
        emitted_working_signs=sum(r['written_signs'] for r in receipts),
        native_word_meanings=0,independent_confirmation=0,
        scope='Fixed contextual CV writer, source and five necessary metrics; no native reading or full structural pass.')
    dump('RESULT.json',result);dump('RECIPE_RECEIPTS.json',receipts)
    dump('RUN_RECEIPT.json',dict(completed_utc=datetime.now(timezone.utc).isoformat(),fixtures=fixture_receipt))
    print(json.dumps(dict(status=result['status'],books={b:{k:v for k,v in x['metrics'].items()
        if k not in ('length_counts','frequency_counts','sample_sequence_hash')} for b,x in books.items()},
        failures={b:{ed:[k for k,v in c['checks'].items() if not v] for ed,c in x['reader_conditions'].items()}
                  for b,x in books.items()}),indent=2))

if __name__=='__main__':
    main()
