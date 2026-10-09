#!/usr/bin/env python3
"""Bounded exploratory source audit; no writer, target query, or refitted gate."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import unicodedata as U
import xml.etree.ElementTree as ET

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
SPECS = ROOT / 'experiments/yolo/gdt1159_corema_unknown_lexical_graph/src/SOURCE.json'
STORED = ROOT / 'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
EXCLUDED = STORED.with_name('EXCLUDED.json')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def local(node):
    return node.tag.rsplit('}', 1)[-1]


def projected_text(node):
    node = deepcopy(node)
    # Remove complete notes, retaining their following text. No production import.
    for parent in node.iter():
        for child in list(parent):
            if local(child) != 'note':
                continue
            siblings = list(parent)
            index = siblings.index(child)
            if index:
                prev = siblings[index - 1]
                prev.tail = (prev.tail or '') + (child.tail or '')
            else:
                parent.text = (parent.text or '') + (child.tail or '')
            parent.remove(child)
    return ' '.join(U.normalize('NFC', ''.join(node.itertext())).lower().split())


def main():
    saved = json.loads(STORED.read_text())
    excluded = json.loads(EXCLUDED.read_text())
    pins = {str(p.relative_to(ROOT)): sha(p) for p in (SPECS, STORED, EXCLUDED)}
    books = {}
    for spec in json.loads(SPECS.read_text())['data']:
        book = spec['collection_id']
        if book not in ('b4', 'w1', 'bs1', 'gr1'):
            continue
        path = ROOT / spec['path']
        assert sha(path) == spec['sha256'], book
        pins[spec['path']] = sha(path)
        recipes = [n for n in ET.parse(path).getroot().iter() if n.get('type') == 'recipe']
        tags = Counter(local(n) for recipe in recipes for n in recipe.iter())
        reconstructed, rejected = [], []
        for i, node in enumerate(recipes, 1):
            text = projected_text(node)
            rid = node.get('{http://www.w3.org/XML/1998/namespace}id', f'{book}.ordinal{i}')
            reasons = sorted({local(n) for n in node.iter() if local(n) in {'gap', 'unclear', 'supplied'}})
            if any(s in text for s in ('[', ']', '…', '...')):
                reasons.append('VISIBLE_EDITORIAL_UNCERTAINTY')
            if not text:
                reasons.append('EMPTY')
            if reasons:
                rejected.append({'id': rid, 'reasons': reasons, 'words': len(text.split())})
            else:
                reconstructed.append({'id': rid, 'text': text, 'words': text.split()})
        assert reconstructed == saved[book], ('projection_difference', book)
        assert rejected == excluded[book], ('exclusion_difference', book)
        flat = [w for r in reconstructed for w in r['words']]
        sample = flat[:8000]
        assert len(sample) == 8000
        counts = Counter(sample)
        top = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:10]
        no_letters = lambda w: not any(ch.isalpha() for ch in w)
        only_punctuation = lambda w: all(U.category(ch).startswith('P') for ch in w)
        books[book] = {
            'projection_equals_stored': True,
            'exclusions_equal_stored': True,
            'retained_recipes': len(reconstructed), 'excluded_recipes': len(rejected),
            'complete_source_words': len(flat),
            'complete_source_characters_without_spaces': sum(map(len, flat)),
            'recipe_tags_before_exclusion': {k: tags[k] for k in ('lb', 'pb', 'w', 'abbr', 'expan', 'note', 'gap', 'unclear', 'supplied', 'del', 'add', 'choice', 'sic', 'corr')},
            'first_8000': {
                'types': len(counts), 'top10': [{'word': w, 'count': n} for w, n in top],
                'top10_count': sum(n for _, n in top),
                'top10_no_letter_count': sum(n for w, n in top if no_letters(w)),
                'no_letter_tokens': sum(no_letters(w) for w in sample),
                'punctuation_only_tokens': sum(only_punctuation(w) for w in sample),
                'punctuation_only_types': sorted(w for w in counts if only_punctuation(w)),
                'any_punctuation_tokens': sum(any(U.category(ch).startswith('P') for ch in w) for w in sample),
            },
        }
    pins[str(Path(__file__).relative_to(ROOT))] = sha(Path(__file__))
    result = {
        'status': 'EXPLORATORY_SOURCE_UNIT_AUDIT', 'input_sha256': pins,
        'books': books,
        'limits': ['Same-author code review/reprojection, not independent manuscript collation.',
                   'No source cleaning, new writer, target access, significance test or replaced gate.',
                   'Tag census was exposed before the bounded audit decision note.',
                   'Exact projection fidelity does not make editorial whitespace native word boundaries.'],
    }
    out = D / 'HAND_WRITER_SOURCE_UNIT_REVIEW_RESULT_20261005.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: {'recipes': v['retained_recipes'], **v['first_8000']} for k, v in books.items()}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
