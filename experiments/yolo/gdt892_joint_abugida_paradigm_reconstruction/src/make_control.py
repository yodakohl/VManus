#!/usr/bin/env python3
"""Independent GDT892 encoder and blinded control builder.

No decoder/core imports. Run --self-test before generating any control.
Generation requires an explicit --start authorization marker.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import pickle
import random
import secrets
import unicodedata

VOWELS = 'aeiouy'
CONSONANTS = ''.join(c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in VOWELS)
SOURCE_SHA256 = '7308e1b9145bc5c4e6febc1149722a8fed89b2cf5a59a9a83ec53744de57744f'


def normalize(word):
    word = word.lower().replace('æ', 'ae').replace('œ', 'oe')
    return ''.join(c for c in unicodedata.normalize('NFD', word)
                   if not unicodedata.combining(c))


def components(word, inherent):
    """Greedy orthographic CV scan, implemented without decoder helpers."""
    if inherent not in VOWELS or not word or any(c not in CONSONANTS + VOWELS for c in word):
        raise ValueError('Invalid normalized word or inherent vowel')
    result = []
    i = 0
    while i < len(word):
        letter = word[i]
        if letter in VOWELS:
            result.append('CARRIER')
            if letter != inherent:
                result.append('V:' + letter)
            i += 1
        else:
            result.append('C:' + letter)
            i += 1
            if i < len(word) and word[i] in VOWELS:
                if word[i] != inherent:
                    result.append('V:' + word[i])
                i += 1
            else:
                result.append('VIRAMA')
    return result


def validate_key(key, inherent):
    expected = {'C:' + c for c in CONSONANTS} | {'V:' + v for v in VOWELS if v != inherent} | {'CARRIER', 'VIRAMA'}
    if set(key) != expected or len(key) != 27:
        raise ValueError('Key does not cover exactly 27 components')
    values = list(key.values())
    if any(len(v) not in (1, 2) for v in values):
        raise ValueError('Bad codeword length')
    if any(a.startswith(b) for i, a in enumerate(values) for j, b in enumerate(values) if i != j):
        raise ValueError('Key is not injective prefix-free')


def encode(word, inherent, key):
    return ''.join(key[c] for c in components(word, inherent))


def self_test():
    # Explicit fixtures written independently before implementation integration.
    fixtures = [
        ('a', 'a', ['CARRIER']),
        ('ae', 'a', ['CARRIER', 'CARRIER', 'V:e']),
        ('ba', 'a', ['C:b']),
        ('be', 'a', ['C:b', 'V:e']),
        ('b', 'a', ['C:b', 'VIRAMA']),
        ('bra', 'a', ['C:b', 'VIRAMA', 'C:r']),
        ('aba', 'a', ['CARRIER', 'C:b']),
        ('bai', 'a', ['C:b', 'CARRIER', 'V:i']),
        ('yy', 'y', ['CARRIER', 'CARRIER']),
        ('qu', 'a', ['C:q', 'V:u']),
        ('juv', 'u', ['C:j', 'C:v', 'VIRAMA']),
        ('a', 'e', ['CARRIER', 'V:a']),
    ]
    for word, vowel, expected in fixtures:
        assert components(word, vowel) == expected, (word, vowel)
    assert normalize('ĀVĒ') == 'ave'
    assert normalize('ÆŒJUV') == 'aeoejuv'
    k = dict(zip(['C:' + c for c in CONSONANTS] + ['V:' + v for v in VOWELS if v != 'a'] + ['CARRIER', 'VIRAMA'],
                 [chr(65 + i // 10) + str(i % 10) for i in range(27)]))
    validate_key(k, 'a')
    assert encode('bra', 'a', k) == k['C:b'] + k['VIRAMA'] + k['C:r']
    bad = dict(k)
    bad['C:b'] = bad['C:c']
    try:
        validate_key(bad, 'a')
    except ValueError:
        pass
    else:
        raise AssertionError('Duplicate code accepted')
    return {'status': 'PASS', 'explicit_component_fixtures': len(fixtures)}


def source_sentences(path):
    """Drop only rows explicitly tagged PUNCT; reject remaining nonletters."""
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('UDante source hash mismatch')
    for block in raw.decode('utf8').split('\n\n'):
        rows, sid, valid = [], None, True
        for line in block.splitlines():
            if line.startswith('# sent_id = '):
                sid = line.partition(' = ')[2]
            if not line or line.startswith('#'):
                continue
            fields = line.split('\t')
            if len(fields) != 10:
                valid = False
                continue
            if not fields[0].isdigit():
                # Range rows duplicate surface tokens; decimal rows are empty nodes.
                # Every ordinary integer-ID lexical token remains mandatory.
                if '-' not in fields[0] and '.' not in fields[0]:
                    valid = False
                continue
            if fields[3] == 'PUNCT':
                continue
            word = normalize(fields[1])
            if not word or any(c not in 'abcdefghijklmnopqrstuvwxyz' for c in word):
                valid = False
            rows.append(word)
        if sid and valid and 6 <= len(rows) <= 16:
            yield sid, rows


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf8')


def build(args):
    # The independent encoder above was completed and fixture-tested before this
    # grammar adapter was added. Admission delegates to the frozen reference only.
    from grammar import accepts
    spec = json.loads(Path(__file__).with_name('SPEC.json').read_text())
    if any(x is None for x in (args.reference_cache, args.source, args.output_dir, args.secret_dir)):
        raise ValueError('Reference cache, source, output directory and secret directory required')
    secret_dir = args.secret_dir.resolve()
    output_dir = args.output_dir.resolve()
    if secret_dir == output_dir:
        raise ValueError('Public and secret directories must differ')
    if (secret_dir / 'truth.json').exists() or (output_dir / 'CONTROL.json').exists():
        raise ValueError('Refusing to replace existing control')
    with args.reference_cache.open('rb') as handle:
        cache = pickle.load(handle)
    forms = set(cache['forms'])
    selected = []
    counts = {'complete_length_eligible': 0, 'lexicon_covered': 0, 'grammar_admitted': 0}
    for sid, words in source_sentences(args.source):
        counts['complete_length_eligible'] += 1
        if any(w not in forms or not cache['analyses'].get(w) for w in words):
            continue
        counts['lexicon_covered'] += 1
        if not accepts(cache['grammar'], [set(tuple(t) for t in cache['analyses'][w]) for w in words]):
            continue
        counts['grammar_admitted'] += 1
        selected.append((sid, words))
        if len(selected) == 24:
            break
    if len(selected) < 24:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / 'CONTROL.json').write_bytes(packed({'status': 'INSUFFICIENT_ELIGIBLE_SENTENCES', 'selection_counts': counts, 'source_sha256': SOURCE_SHA256}))
        return {'status': 'INSUFFICIENT_ELIGIBLE_SENTENCES', 'selection_counts': counts}
    seed = secrets.token_bytes(32)
    rng = random.Random(int.from_bytes(seed, 'big'))
    inherent = rng.choice(VOWELS)
    alphabet = list(spec['control']['cipher_alphabet'])
    assert len(alphabet) == len(set(alphabet)) == 20
    rng.shuffle(alphabet)
    codewords = alphabet[:12] + rng.sample([a + b for a in alphabet[12:] for b in alphabet], 15)
    rng.shuffle(codewords)
    labels = ['C:' + c for c in CONSONANTS] + ['V:' + v for v in VOWELS if v != inherent] + ['CARRIER', 'VIRAMA']
    key = dict(zip(labels, codewords))
    validate_key(key, inherent)
    observed = set()
    truth_rows, public_rows = [], []
    for n, (sid, words) in enumerate(selected):
        row_id = 'D%02d' % (n + 1) if n < 12 else 'H%02d' % (n - 11)
        ciphertext = [encode(w, inherent, key) for w in words]
        for w in words:
            observed.update(components(w, inherent))
        truth_rows.append({'id': row_id, 'source_sent_id': sid, 'words': words})
        public_rows.append({'id': row_id, 'split': 'discovery' if n < 12 else 'held', 'ciphertext': ciphertext})
    truth = {'seed_hex': seed.hex(), 'inherent_vowel': inherent, 'key': key, 'rows': truth_rows, 'observed_components': sorted(observed), 'unobserved_components': sorted(set(key) - observed)}
    public = {'status': 'CONTROL_READY', 'schema': 'GDT892_BLINDED_CONTROL_V1', 'source_sha256': SOURCE_SHA256, 'reference_cache_sha256': hashlib.sha256(args.reference_cache.read_bytes()).hexdigest(), 'spec_sha256': hashlib.sha256(Path(__file__).with_name('SPEC.json').read_bytes()).hexdigest(), 'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'seed_commitment_sha256': hashlib.sha256(seed).hexdigest(), 'truth_commitment_sha256': hashlib.sha256(packed(truth)).hexdigest(), 'selection_counts': counts, 'rows': public_rows, 'unused_rule_policy': 'No identification credit; compare complete plaintext projections, not unused parameter values.'}
    secret_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(secret_dir, 0o700)
    fd = os.open(secret_dir / 'truth.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(packed(truth))
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'CONTROL.json').write_bytes(packed(public))
    return {'status': public['status'], 'selection_counts': counts, 'public_file': str(output_dir / 'CONTROL.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--reference-cache', type=Path)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--secret-dir', type=Path)
    parser.add_argument('--start', action='store_true')
    args = parser.parse_args()
    result = self_test()
    if args.self_test:
        print(json.dumps(result))
        return
    if not args.start:
        parser.error('Generation requires explicit START authorization and --start')
    print(json.dumps(build(args)))


if __name__ == '__main__':
    main()
