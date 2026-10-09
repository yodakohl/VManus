"""Separately reconstruct source differences and all five decisions; no writer import."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
import statistics

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
A = D/'artifacts'


def hash_value(value):
    payload = json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()
    return hashlib.sha256(payload).hexdigest()


def main():
    lock = json.loads((A/'REGISTRATION_LOCK.json').read_text())
    for name, sha in lock['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == sha, name
    proposal = json.loads((ROOT/'research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_CIRCULAR_LETTER_DIFFERENCE_RAW_20261005.json').read_text())
    rare = proposal['design']['plain_unit_ring']['escape_characters_in_order']
    code = {chr(97+i): (i,) for i in range(21)}
    code.update({c: (21,)+divmod(j,21) for j,c in enumerate(rare)})
    inv = {v:k for k,v in code.items()}
    assert len(code) == len(inv) == 82

    def produce(words, initial=0):
        all_units = [list(itertools.chain.from_iterable(code[c] for c in w)) for w in words]
        flat = list(itertools.chain.from_iterable(all_units))
        encoded = [(curr-prev+22)%22 for prev,curr in zip([initial]+flat,flat)]
        out, i = [], 0
        for units in all_units:
            out.append(encoded[i:i+len(units)])
            i += len(units)
        return out

    def read_back(groups, initial=0):
        state = initial
        out = []
        for group in groups:
            assert group
            units = []
            for d in group:
                assert isinstance(d,int) and 0 <= d <= 21
                state = (state+d)%22
                units.append(state)
            result = []
            i = 0
            while i < len(units):
                size = 3 if units[i] == 21 else 1
                piece = tuple(units[i:i+size])
                assert len(piece) == size and piece in inv
                result.append(inv[piece])
                i += size
            out.append(''.join(result))
        return out

    for ch in code:
        for start in range(21):
            assert read_back(produce([ch], start), start) == [ch]
    ex = proposal['design']['complete_invented_example']
    alphabet = proposal['design']['output_glyphs_by_distance_0_to_21']
    assert [[alphabet[d] for d in g] for g in produce(ex['source'].split())] == ex['output_working_glyph_words']
    trace = ex['trace']
    p = 0
    for word,char,old,u,d,sign,new in trace:
        assert old == p and new == u and d == (u-old)%22 and alphabet[d] == sign
        p = u

    source = json.loads((ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text())
    targets = json.loads((ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json').read_text())['targets']
    result = json.loads((A/'RESULT.json').read_text())
    saved_receipts = json.loads((A/'RECIPE_RECEIPTS.json').read_text())
    all_receipts, outcomes = [], []
    conditions = 0
    for book in ('b4','w1','bs1','gr1'):
        sample = []
        used = 0
        for recipe in source[book]:
            rendered = produce(recipe['words'])
            assert read_back(rendered) == recipe['words']
            all_receipts.append(dict(book=book,id=recipe['id'],words=len(rendered),
                source_characters=sum(len(w) for w in recipe['words']),
                written_signs=sum(len(w) for w in rendered),encoded_sha256=hash_value(rendered)))
            take = rendered[:max(0,8000-used)]
            if take:
                sample.append(take)
                used += len(take)
        assert used == 8000
        words = [tuple(w) for part in sample for w in part]
        lengths = [len(w) for w in words]
        counts = Counter(words)
        m = result['books'][book]['metrics']
        pairs = [(a,b) for part in sample for a,b in zip(part,part[1:])]
        top = sum(n for _,n in counts.most_common(10))
        eq = sum(a==b for a,b in pairs)
        checks = dict(tokens=8000,types=len(counts),type_ratio=len(counts)/8000,
            top10_count=top,top10_share=top/8000,adjacent_pairs=len(pairs),
            exact_repeat_count=eq,exact_repeat=eq/len(pairs),
            mean_length=statistics.mean(lengths),sd_length=statistics.pstdev(lengths),
            length_counts={str(k):v for k,v in Counter(lengths).items()},
            frequency_counts={str(k):v for k,v in Counter(counts.values()).items()},
            sample_sequence_hash=hash_value(sample))
        assert set(checks) == set(m)
        for name,value in checks.items():
            if isinstance(value,float):
                assert abs(value-m[name]) < 1e-11, (book,name)
            else:
                assert value == m[name], (book,name)
        mm = Fraction(sum(lengths),8000)
        mv = sum((Fraction(n)-mm)**2 for n in lengths)/8000
        book_pass = True
        for ed,t in targets.items():
            tm = sum(Fraction(int(k)*v,8000) for k,v in t['length_counts'].items())
            tv = sum(v*(Fraction(int(k))-tm)**2 for k,v in t['length_counts'].items())/8000
            flags = dict(type_ratio=abs(len(counts)-t['types'])<=400,
                top10_share=abs(top-round(t['top10_share']*8000))<=400,
                exact_repeat=abs(Fraction(eq,len(pairs))-Fraction(round(t['exact_repeat']*t['adjacent_pairs']),t['adjacent_pairs']))<=Fraction(1,100),
                mean_length=4*tm <= 5*mm <= 6*tm,
                sd_length=9*tv <= 16*mv <= 25*tv)
            expected = result['books'][book]['reader_conditions'][ed]
            assert expected == dict(checks=flags,passed=all(flags.values()))
            conditions += len(flags)
            outcomes.append(all(flags.values()))
            book_pass = book_pass and all(flags.values())
        assert result['books'][book]['passed'] == book_pass
    assert all_receipts == saved_receipts
    assert result['complete_recipe_roundtrips'] == len(all_receipts) == 1054
    for key,field in [('complete_source_words','words'),('source_characters','source_characters'),('emitted_working_signs','written_signs')]:
        assert result[key] == sum(r[field] for r in all_receipts)
    expected_status = 'FIXED_RING_NECESSARY_SCREEN_'+('PASS' if all(outcomes) else 'FAIL')
    assert result['status'] == expected_status and result['all_books_pass'] == all(outcomes)
    validation = dict(status='PASS',scientific_result=expected_status,
        recipes_checked=len(all_receipts),words_checked=result['complete_source_words'],conditions_checked=conditions,
        entry_character_cases=82*21,hand_trace_rows=len(trace),same_author=True,
        runner_imported=False,writer_imported=False,native_meanings_validated=0)
    (A/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(validation,indent=2))


if __name__ == '__main__':
    main()
