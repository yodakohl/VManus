#!/usr/bin/env python3
"""Independent GDT892 full-source control eligibility audit.

No solver, encoder, preparation or grammar implementation is imported. This
validator reads only the historical source, frozen reference and public control.
It never creates or reads a cipher key or truth file. Public output is aggregate.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import pickle
import re
import unicodedata

VOWELS = 'aeiouy'
CONSONANTS = ''.join(x for x in 'abcdefghijklmnopqrstuvwxyz' if x not in VOWELS)
SOURCE_SHA256 = '7308e1b9145bc5c4e6febc1149722a8fed89b2cf5a59a9a83ec53744de57744f'

def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def inventory(vowel):
    require(vowel in VOWELS and len(vowel) == 1, 'invalid inherent vowel')
    return ['C:' + c for c in CONSONANTS] + [
        'V:' + v for v in VOWELS if v != vowel] + ['CARRIER', 'VIRAMA']


def encode_parts(word, vowel):
    """Tokenize maximal CV or single-letter chunks, then emit channel symbols."""
    inventory(vowel)
    require(isinstance(word, str) and re.fullmatch('[a-z]+', word),
            'plaintext is not a complete normalized word')
    chunks = re.findall('[' + CONSONANTS + '][' + VOWELS + ']|[a-z]', word)
    result = []
    for chunk in chunks:
        if chunk[0] in VOWELS:
            result.append('CARRIER')
            if chunk != vowel:
                result.append('V:' + chunk)
        else:
            result.append('C:' + chunk[0])
            if len(chunk) == 1:
                result.append('VIRAMA')
            elif chunk[1] != vowel:
                result.append('V:' + chunk[1])
    return result


def accepts_reference(grammar, tag_options):
    """Independent Earley recognizer, reading productions rather than by_lhs."""
    tags = {tuple(tag): n for n, tag in enumerate(grammar['tags'])}
    lattice = [{tags[tuple(t)] for t in options if tuple(t) in tags} for options in tag_options]
    if not lattice or any(not options for options in lattice):
        return False
    rules = [(row['lhs'], tuple(tuple(x) for x in row['rhs'])) for row in grammar['productions']]
    start_rule = len(rules)
    rules.append((-1, (('N', grammar['start']),)))
    by_lhs = {}
    for i, (lhs, _) in enumerate(rules):
        by_lhs.setdefault(lhs, []).append(i)
    chart = [set() for _ in range(len(lattice) + 1)]
    waiting = [defaultdict(set) for _ in chart]
    predicted = [set() for _ in chart]
    chart[0].add((start_rule, 0, 0))
    for position in range(len(chart)):
        agenda = list(chart[position])
        while agenda:
            rule, dot, origin = agenda.pop()
            lhs, rhs = rules[rule]
            additions = []
            if dot == len(rhs):
                for parent, pdot, porigin in waiting[origin].get(lhs, ()):
                    additions.append((parent, pdot + 1, porigin))
            elif rhs[dot][0] == 'N':
                symbol = rhs[dot][1]
                waiting[position][symbol].add((rule, dot, origin))
                if symbol not in predicted[position]:
                    predicted[position].add(symbol)
                    additions = [(child, 0, position) for child in by_lhs.get(symbol, ())]
            elif position < len(lattice) and rhs[dot][1] in lattice[position]:
                chart[position + 1].add((rule, dot + 1, origin))
            for state in additions:
                if state not in chart[position]:
                    chart[position].add(state)
                    agenda.append(state)
    return (start_rule, 1, 0) in chart[-1]



def normalized(word):
    expanded = word.casefold().replace('æ', 'ae').replace('œ', 'oe')
    return ''.join(c for c in unicodedata.normalize('NFD', expanded)
                   if not unicodedata.combining(c))


def parse_source(raw):
    """Inspect every source sentence; yield only full admissible lexical rows.

    Multiword-token headers exclude their entire sentence, while empty nodes
    have no surface token. Punctuation is the only discarded integer token.
    """
    blocks = re.split(r'\n\s*\n', raw.decode('utf8').strip())
    stats = Counter()
    eligible = []
    for block in blocks:
        if not block.strip():
            continue
        stats['source_blocks_examined'] += 1
        sid = None
        words = []
        malformed = False
        mwt = False
        for line in block.splitlines():
            if line.startswith('#'):
                if line.startswith('# sent_id = '):
                    sid = line[len('# sent_id = '):]
                continue
            fields = line.split('\t')
            if len(fields) != 10:
                malformed = True
                continue
            token = fields[0]
            if re.fullmatch(r'\d+-\d+', token):
                mwt = True
                continue
            if re.fullmatch(r'\d+\.\d+', token):
                continue
            if not re.fullmatch(r'\d+', token):
                malformed = True
                continue
            if fields[3] == 'PUNCT':
                continue
            word = normalized(fields[1])
            if re.fullmatch('[a-z]+', word) is None:
                malformed = True
            words.append(word)
        if mwt:
            stats['excluded_mwt_sentences'] += 1
            continue
        if malformed or not sid:
            stats['excluded_invalid_sentences'] += 1
            continue
        if not 6 <= len(words) <= 16:
            stats['excluded_length_sentences'] += 1
            continue
        eligible.append((sid, words))
        stats['complete_length_eligible'] += 1
    return eligible, dict(stats)


def select_all(eligible, cache):
    """Exhaust fixed source once; never repair a rejected sentence or its words."""
    counts = dict.fromkeys(('complete_length_eligible', 'lexicon_covered',
                           'grammar_admitted', 'held_component_coverage_declines',
                           'discovery_selected', 'held_selected'), 0)
    forms = set(cache['forms'])
    discovery = {v: set() for v in VOWELS}
    admitted_examined = 0
    for _, words in eligible:
        counts['complete_length_eligible'] += 1
        if any(w not in forms or not cache['analyses'].get(w) for w in words):
            continue
        counts['lexicon_covered'] += 1
        if not accepts_reference(cache['grammar'], [cache['analyses'][w] for w in words]):
            continue
        counts['grammar_admitted'] += 1
        usage = {v: {part for w in words for part in encode_parts(w, v)} for v in VOWELS}
        admitted_examined += 1
        if counts['discovery_selected'] < 12:
            counts['discovery_selected'] += 1
            for v in VOWELS:
                discovery[v].update(usage[v])
        elif counts['held_selected'] < 12:
            if any(not usage[v] <= discovery[v] for v in VOWELS):
                counts['held_component_coverage_declines'] += 1
            else:
                counts['held_selected'] += 1
        # Keep scanning even if capacity fills. For the insufficient-control
        # audit this branch is unreachable; flag any disagreement below.
    return counts, {'eligible_sentences_examined': len(eligible),
                    'grammar_admitted_sentences_examined': admitted_examined,
                    'discovery_component_counts': {v: len(discovery[v]) for v in VOWELS},
                    'full_source_exhausted': True}


def audit(control, cache, source_bytes):
    require(hashlib.sha256(source_bytes).hexdigest() == SOURCE_SHA256,
            'historical source hash mismatch')
    require(control.get('source_sha256') == SOURCE_SHA256,
            'public control source commitment mismatch')
    require(control.get('status') == 'INSUFFICIENT_ELIGIBLE_SENTENCES',
            'audit is restricted to an insufficient public control')
    eligible, parser_counts = parse_source(source_bytes)
    counts, traversal = select_all(eligible, cache)
    require(counts == control['selection_counts'], 'independent selection counts differ')
    require(counts['discovery_selected'] < 12 or counts['held_selected'] < 12,
            'insufficient-control claim contradicted by capacity')
    return {'status': 'PASS', 'control_status': 'INSUFFICIENT_ELIGIBLE_SENTENCES',
            'selection_counts': counts, 'parser_counts': parser_counts,
            'traversal': traversal, 'source_sha256': SOURCE_SHA256,
            'interpretation': 'Fixed source exhausted below the registered 12 discovery plus 12 held requirement; no cipher/key generated or evaluated.',
            'independence': 'Independent source parser, regex-based CV encoder and grammar recognizer; no generator/solver/grammar-code imports.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('control', 'reference-cache', 'source', 'output'):
        parser.add_argument('--' + flag, type=Path, required=True)
    args = parser.parse_args()
    try:
        control_bytes = args.control.read_bytes()
        control = json.loads(control_bytes)
        reference_bytes = args.reference_cache.read_bytes()
        reference_sha = hashlib.sha256(reference_bytes).hexdigest()
        metadata_path = Path(__file__).resolve().parents[1] / 'artifacts' / 'REFERENCE.json'
        metadata = json.loads(metadata_path.read_text())
        expected = metadata['cache_files']['reference.pkl']['sha256']
        require(reference_sha == expected, 'frozen reference cache hash mismatch')
        cache = pickle.loads(reference_bytes)
        result = audit(control, cache, args.source.read_bytes())
        result['reference_cache_sha256'] = reference_sha
        result['control_sha256'] = hashlib.sha256(control_bytes).hexdigest()
        result['validator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        result['spec_sha256'] = hashlib.sha256(Path(__file__).with_name('SPEC.json').read_bytes()).hexdigest()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        result = {'status': 'VALIDATION_ERROR', 'reason': type(exc).__name__ + ': ' + str(exc)}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'selection_counts': result.get('selection_counts')}))
    if result['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
