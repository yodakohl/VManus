#!/usr/bin/env python3
"""Small declared lexical/interface certificates, not a source or Voynich fit."""
from pathlib import Path
import hashlib
import importlib.util
import json

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
RAW = D / 'HAND_WRITER_MINIMAL_LEXICON_PREFIX_RAW_20261005.json'
OLD = D / 'B6_7_PRODUCTIVE_STEMS.py'
PAST = ROOT / 'experiments/yolo/gdt1175_fixed_writer_b6_8_transfer/artifacts/RESULT.json'
END = '$'  # Internal source terminator, rendered by the card's existing d.


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_old(name):
    spec = importlib.util.spec_from_file_location(name, OLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PrefixModule:
    def __init__(self, words, carrier):
        self.words = tuple(sorted(words))
        assert self.words and len(set(self.words)) == len(self.words)
        signs = carrier['data_signs_in_order']
        alphabet = carrier['source_characters_in_order']
        assert len(signs) == 6 and len(alphabet) == 27
        self.letter = {c: (signs[j // 6], signs[j % 6]) for j, c in enumerate(alphabet)}
        self.back = {v: k for k, v in self.letter.items()}
        self.end = carrier['end_sign']
        self.literal = carrier['literal_sign']
        assert self.end not in signs and self.literal not in signs
        self.prefix = {}
        for word in self.words:
            assert word and set(word) <= set(alphabet)
            terminated = word + END
            for length in range(1, len(terminated) + 1):
                p = terminated[:length]
                if sum((other + END).startswith(p) for other in self.words) == 1:
                    self.prefix[word] = p
                    break
        self.codes = {w: tuple(s for c in p for s in ((self.end,) if c == END else self.letter[c]))
                      for w, p in self.prefix.items()}
        self.code_back = {code: w for w, code in self.codes.items()}
        assert len(self.code_back) == len(self.words)
        assert all(a == b or b[:len(a)] != a for a in self.code_back for b in self.code_back)
        # Separate longest-common-prefix characterization verifies every choice.
        for word, p in self.prefix.items():
            common = []
            for other in self.words:
                if other == word:
                    continue
                n = 0
                for a, b in zip(word + END, other + END):
                    if a != b:
                        break
                    n += 1
                common.append(n)
            assert p == (word + END)[:1 + max(common, default=0)]

    def encode(self, word):
        if word in self.codes:
            return self.codes[word]
        assert word and all(c in self.letter for c in word)
        return (self.literal,) + tuple(s for c in word for s in self.letter[c]) + (self.end,)

    def read_at(self, glyphs, pos=0):
        start = pos
        if pos >= len(glyphs):
            raise ValueError('Missing lexical code')
        if glyphs[pos] == self.literal:
            pos += 1
            letters = []
            while pos < len(glyphs) and glyphs[pos] != self.end:
                pair = tuple(glyphs[pos:pos + 2])
                if pair not in self.back:
                    raise ValueError('Bad literal pair')
                letters.append(self.back[pair])
                pos += 2
            word = ''.join(letters)
            if pos >= len(glyphs) or not word or word in self.codes:
                raise ValueError('Missing end or noncanonical literal')
            return word, pos + 1
        while pos < len(glyphs):
            pos += 1
            code = tuple(glyphs[start:pos])
            if code in self.code_back:
                return self.code_back[code], pos
            if not any(full[:len(code)] == code for full in self.code_back):
                raise ValueError('Not a known-root prefix')
        raise ValueError('Ambiguous or truncated lexical prefix')

    def decode(self, glyphs):
        word, end = self.read_at(glyphs)
        if end != len(glyphs):
            raise ValueError('Trailing material')
        return word


def main():
    raw = json.loads(RAW.read_text())['design']
    carrier = raw['fully_specified_teaching_carrier']
    lesson = PrefixModule(raw['small_hand_example']['lexicon'], carrier)
    examples = []
    for w in [*lesson.words, 'WURZ', 'A']:
        code = lesson.encode(w)
        assert lesson.decode(code) == w
        examples.append({'word': w, 'prefix': lesson.prefix.get(w, 'LITERAL'), 'written': ''.join(code)})
    expected = {k: v.replace('<END>', END) for k, v in raw['small_hand_example']['prefixes_before_surface_encoding'].items()}
    assert lesson.prefix == expected
    negatives = [lesson.letter['B'], lesson.encode('BILD') + lesson.letter['A'],
                 (lesson.literal,) + lesson.letter['B']]
    for code in negatives:
        try:
            lesson.decode(code)
        except ValueError:
            pass
        else:
            raise AssertionError('Malformed lexical code accepted')
    grown = PrefixModule([*lesson.words, 'BLATT'], carrier)
    try:
        grown.decode(lesson.encode('BLUT'))
    except ValueError:
        growth_rejected = True
    else:
        raise AssertionError('Old BLUT abbreviation silently survives BLATT')

    old = load_old('baseline934')
    roots = PrefixModule([name for name, _, _ in old.ROWS], carrier)
    N = old.N
    first = N('DO', N('SET', N('MEAT'), N('IN', N('POT'))))
    second = N('DO', N('REL', N('APPLY', N('EGG'), N('MEAT')), N('IN', N('POT'))))
    pair = [first, second]
    original = [old.write([tree]) for tree in pair]
    assert original[0] != original[1]
    assert all(old.read(text) == [tree] for text, tree in zip(original, pair))

    bare = load_old('unmarked934')
    for name in bare.LEX:
        bare.LEX[name]['code'] = ''.join(roots.codes[name])
    collision = [bare.write([tree]) for tree in pair]
    assert first != second and collision[0] == collision[1]
    assert roots.prefix['SET'] == 'SE' and roots.prefix['EGG'] == 'E'
    assert roots.codes['SET'] == ('o', 'a') + roots.codes['EGG']

    tagged = load_old('tagged934')
    marker = 't'
    assert marker in tagged.GLYPHS
    assert marker not in tagged.BUILD_BACK and marker not in {'l', 'e', 'i'}
    for name in tagged.LEX:
        tagged.LEX[name]['code'] = marker + ''.join(roots.codes[name])
    original_core_reader = tagged.read_core

    def read_core(gs, pos=0, allow_bare=True):
        if gs[pos] == marker:
            name, end = roots.read_at(gs, pos + 1)
            if name not in tagged.LEX:
                raise ValueError('Unknown learned-root identifier')
            return tagged.N(name, *([None] * tagged.arity(name))), end
        if gs[pos] not in tagged.BUILD_BACK and gs[pos] not in {'l', 'e', 'i'}:
            raise ValueError('Missing declared root-field marker')
        return original_core_reader(gs, pos, allow_bare)

    tagged.read_core = read_core
    separated = [tagged.write([tree]) for tree in pair]
    assert separated[0] != separated[1]
    assert all(tagged.read(text) == [tree] for text, tree in zip(separated, pair))
    assert all(tagged.read(' '.join(text.split())) == [tree] for text, tree in zip(separated, pair))
    assert all(len(code) >= 2 for code in roots.codes.values())
    assert all(len(old.LETTERS[c.lower()]) <= len(lesson.letter[c]) == 2 for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    past = json.loads(PAST.read_text())
    unchanged_literal = past['literal_glyphs']
    old_total = past['glyphs']
    extra_for_half = max(0, 2 * unchanged_literal - old_total)
    result = {
        'status': 'LEXICAL_MODULE_VALID__UNMARKED_COMPOSITION_COLLIDES__NO_FIXED_LEXICON_SHORTENING',
        'input_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (RAW, OLD, PAST, Path(__file__))},
        'lesson': examples,
        'checks': {'eight_declared_spellings_roundtrip': True, 'three_malformed_cases_rejected': True,
                   'fixed_lexicons_prefix_free': True, 'separate_lcp_prefix_derivation': True,
                   'BLATT_invalidates_old_BLUT_code': growth_rejected},
        'root_table': [{'identifier': w, 'prefix': roots.prefix[w], 'code': ''.join(roots.codes[w]),
                        'old_glyphs': 2, 'raw_glyphs': len(roots.codes[w]), 'tagged_glyphs': 1 + len(roots.codes[w])}
                       for w in roots.words],
        'complete_contrast': [{'tree': old.show(tree), 'old_written': a, 'unmarked_written': b,
                               'tagged_written': c, 'tagged_readback': tagged.show(tagged.read(c)[0]),
                               'old_glyphs': sum(len(old.tokenize(w)) for w in a.split()),
                               'tagged_glyphs': sum(len(tagged.tokenize(w)) for w in c.split())}
                              for tree, a, b, c in zip(pair, original, collision, separated)],
        'cost_bound': {'known_root_old': 2, 'known_root_raw_min': 2, 'known_root_tagged_min': 3,
                       'old_unknown_formula': '2+n+count(source letters t-z)',
                       'raw934_unknown_formula': '2+2*n',
                       'claim': 'With the same lexicon and symbolic grouping, the unchanged934carrier cannot shorten any learned-root payload or any old a-z literal payload. Paid delimitation adds cost. This is not a lower bound for other carriers or larger lexicons.'},
        'ratio_warning': {'original1175_literal': unchanged_literal, 'original1175_total': old_total,
                          'pure_nonliteral_padding_to_50percent': extra_for_half,
                          'claim': 'Hypothetical denominator increase only; no padded recipe was written. A falling percentage alone does not show reduced absolute spelling cost. Original1175FAIL retained.'},
        'equality_ceiling': 'If both old and replacement per-group encodings recover the same full symbolic group, a bijective spelling substitution preserves whole-group equality/frequencies. This does not assume a native segmentation or cover changed grammar/grouping.',
        'limits': ['Invented lesson and two artificial complete statements, not translated Voynich or newly scored recipe text.',
                   'The unmarked composition deliberately lacks the delimited root field required by934; it does not refute934proper.',
                   'The tagged comparison was declared before execution; it retains all old literal/grammar branches and changes only learned-root fields.',
                   'English identifier spellings are paid artificial dictionary entries, not identified manuscript language or a natural German lexicon.',
                   'No larger corpus, source rereading, new key, new root, native query, image or reserved data.',
                   'Same-author roundtrips and rule proof, not human usability or independent historical validation.'],
    }
    (D / 'HAND_WRITER_IDEA934_MODULE_RESULT_20261005.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'complete_contrast': result['complete_contrast'],
                      'ratio_warning': result['ratio_warning']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
