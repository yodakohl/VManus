#!/usr/bin/env python3
"""Independent phoneme roundtrip validator. No primary-program imports."""
import argparse
import gzip
import hashlib
import itertools
import math
import json
from collections import Counter
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
SIGNS = tuple(sorted(('a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh')))
FOLLOWERS = {'cfh': ('a','d','e','o','s','y'), 'cph': ('a','d','e','k','o','y')}
SOURCE = 'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'


def make_codec(signs, head, followers, vowels):
    followers = tuple(sorted(followers))
    vowels = tuple(sorted(vowels))
    assert len(followers) == 6 and len(vowels) == 3
    assert len(set(signs)) == 22
    assert head not in followers and head not in vowels
    assert not set(followers).intersection(vowels)
    remaining = sorted(set(signs) - {head} - set(followers) - set(vowels))
    assert len(remaining) == 12
    values = {s: (c, 6) for c, s in enumerate(followers)}
    values.update({s: (6+v,) for v, s in enumerate(vowels)})
    values.update({s: pair for s, pair in zip(remaining, itertools.product(range(6), (7,8)))})
    bare = {s: c for c,s in enumerate(followers)}
    inverse = {value: s for s,value in values.items()}
    return values, bare, inverse, followers


def decode(word, head, codec):
    values, bare, _, _ = codec
    phonemes = []
    cursor = iter(word)
    for sign in cursor:
        if sign == head:
            follower = next(cursor, None)
            if follower not in bare:
                return None
            phonemes.append(bare[follower])
        else:
            if sign not in values:
                return None
            phonemes.extend(values[sign])
    return tuple(phonemes)


def encode(phonemes, head, codec):
    _, _, inverse, followers = codec
    written = []
    position = 0
    while position < len(phonemes):
        first = phonemes[position]
        if first >= 6:
            written.append(inverse[(first,)])
            position += 1
        elif position+1 < len(phonemes) and phonemes[position+1] >= 6:
            written.append(inverse[(first, phonemes[position+1])])
            position += 2
        else:
            written.extend((head, followers[first]))
            position += 1
    return tuple(written)


def canonical(word, head, codec):
    phonemes = decode(word, head, codec)
    return phonemes is not None and encode(phonemes, head, codec) == word


def controls():
    signs = tuple('S%02d' % i for i in range(22))
    head = signs[0]
    followers = signs[1:7]
    vowels = signs[7:10]
    codec = make_codec(signs, head, followers, vowels)
    source_count = 0
    for size in range(5):
        for phonemes in itertools.product(range(9), repeat=size):
            written = encode(phonemes, head, codec)
            assert decode(written, head, codec) == phonemes
            assert canonical(written, head, codec)
            source_count += 1
    written_count = 0
    for size in range(4):
        for word in itertools.product(signs, repeat=size):
            local_valid = all(i+1 < len(word) and word[i+1] in followers
                              for i,s in enumerate(word) if s == head)
            local_valid = local_valid and not any(word[i] == head and word[i+1] in followers and word[i+2] in vowels
                                                  for i in range(max(0,len(word)-2)))
            assert canonical(word, head, codec) == local_valid
            written_count += 1
    assert not canonical((head, followers[0], vowels[0]), head, codec)
    assert canonical((head, followers[0]), head, codec)
    assert canonical((vowels[0],), head, codec)
    assert not canonical((head,), head, codec)
    assert not canonical(('OUTSIDE_DOMAIN',), head, codec)
    # Multi-bare chains must remain valid; a forbidden final vowel must not.
    assert canonical((head,followers[0],head,followers[1]),head,codec)
    assert not canonical((head,followers[0],head,followers[1],vowels[1]),head,codec)
    return {'status':'PASS_SOURCE_FREE_ONLY','source_words':source_count,'written_sequences':written_count,
            'method':'Explicit phoneme decode and greedy re-encode versus local criterion; native files unopened.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', '--controls-only', action='store_true')
    args = parser.parse_args()
    if args.controls:
        print(json.dumps(controls(),sort_keys=True))
        return
    lock = json.loads((E/'src/REGISTRATION_LOCK.json').read_text())
    for path, digest in lock['hashes'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
    data = json.loads(gzip.decompress((ROOT/SOURCE).read_bytes()))
    old = json.loads((ROOT/'experiments/yolo/gdt1248_prefix_bound_attainment/artifacts/RESULT.json').read_text())
    prefix = json.loads((ROOT/'experiments/yolo/gdt1234_prefix_quotient_code_capacity/artifacts/RESULT.json').read_text())
    result = json.loads((E/'artifacts/RESULT.json').read_text())
    assert result['experiment'] == 'GDT1383'
    assert result['status'] == 'EXACT_CANONICAL_ROLE_CLASSIFICATION'
    assert result['labelings_per_role_set'] == math.factorial(6)*math.factorial(3)*math.factorial(12)
    case_order = [(reader,head) for reader in ('IT2a','RF1b','ZL3b') for head in ('cfh','cph')]
    assert [(r['reader'],r['head']) for r in result['cases']] == case_order
    checked = []
    total_roundtrips = 0
    for r in result['cases']:
        reader, head = r['reader'], r['head']
        rows = data[reader]
        followers = FOLLOWERS[head]
        words = Counter(tuple(row['units']) for row in rows)
        assert all(w and set(w) <= set(SIGNS) for w in words)
        assert all(not row['page'].startswith('f84') and row['page'] not in ('f116v','f1r') for row in rows)
        assert r['groups'] == len(rows) and r['types'] == len(words)
        prior = next(c for c in old['cases'] if (c['reader'],c['head']) == (reader,head))
        assert prior['groups'] == len(rows) and prior['types'] == len(words)
        assert prior['failed_groups'] == 0 and prior['complete_code_upper_bound'] == 27
        parent = prefix['readers'][reader]
        assert parent['groups'] == len(rows) and parent['types'] == len(words)
        assert parent['closure_status'] == 'COMPLETE'
        assert set(parent['summary']['F']) == set(SIGNS)-{'cfh','cph','q'}
        assert set(parent['summary']['second_signs'][head]) == set(followers)
        assert len(parent['summary']['second_signs']['q']) > 6
        candidates = sorted(set(SIGNS)-{head}-set(followers))
        assert len(candidates) == 15
        allowed = []
        masks_checked = 0
        active = sum(count for word,count in words.items() if head in word)
        assert r['active_groups'] == active == prior['active_groups']
        # Every role mask gets a complete decoded/encoded comparison, including
        # masks already contradicted by another word. No observed-key pruning.
        for vowels in itertools.combinations(candidates,3):
            codec = make_codec(SIGNS,head,followers,vowels)
            failures = 0
            for word,count in words.items():
                if not canonical(word,head,codec):
                    failures += count
                total_roundtrips += 1
            if failures == 0:
                allowed.append(list(vowels))
            masks_checked += 1
        assert masks_checked == 455
        assert allowed == r['vowel_sets']
        assert len(allowed) == r['count']
        expected_status = 'NO_CANONICAL_ROLE_KEY' if not allowed else 'UNIQUE_ROLE_CLASS' if len(allowed)==1 else 'MULTIPLE_ROLE_CLASSES'
        assert r['status'] == expected_status
        # Separate original-row provenance and first-occurrence witness audit.
        witnesses = {}
        seen_followers = set()
        for row in rows:
            word = row['units']
            for position, sign in enumerate(word):
                if sign != head:
                    continue
                assert position+1 < len(word)
                following = word[position+1]
                assert following in followers
                seen_followers.add(following)
                if position+2 < len(word):
                    after = word[position+2]
                    if after not in witnesses:
                        witnesses[after] = dict(next=after,id=row['id'],page=row['page'],locus=row['locus'],
                                                raw=row['ivtff_group_raw'],units=word,index=position)
        assert seen_followers == set(followers)
        assert r['followers'] == sorted(seen_followers)
        assert r['after_pair'] == sorted(witnesses)
        assert r['witnesses'] == [witnesses[s] for s in sorted(witnesses)]
        eligible = sorted(set(candidates)-set(witnesses))
        assert r['eligible'] == eligible
        assert allowed == [list(v) for v in itertools.combinations(eligible,3)]
        checked.append(dict(reader=reader,head=head,role_masks_checked=masks_checked,
                            whole_types=len(words),groups=len(rows),allowed_count=len(allowed),status=expected_status))
    validation = dict(status='PASS',cases=checked,total_whole_type_roundtrips=total_roundtrips,
                      method='All455role sets per head checked by explicit phoneme decoding and greedy re-encoding; separate source witness accounting.',
                      inherited_head_exhaustiveness='Bound to original1234summary and1248results; this validator does not rederive the original quotient closure.',
                      independent_native_meaning_confirmation=False)
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n')
    print(json.dumps(validation,sort_keys=True))


if __name__ == '__main__':
    main()
