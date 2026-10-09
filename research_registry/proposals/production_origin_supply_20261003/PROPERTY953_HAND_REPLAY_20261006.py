#!/usr/bin/env python3
"""Check the already exposed, manually reviewed953 lesson; no manuscript input."""
from pathlib import Path
import hashlib
import json
import string

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONTRACT = HERE / "HUMAN_PROPERTY953_PHYSICAL_CONTRACT_20261006.json"
REVIEW = HERE / "HUMAN_PROPERTY953_PHYSICAL_ROOT_REVIEW_20261006.json"


def units(text, alphabet):
    answers = [[]]
    states = {0: answers}
    for i in range(len(text)):
        for parsed in states.get(i, []):
            for glyph in alphabet:
                if text.startswith(glyph, i):
                    states.setdefault(i + len(glyph), []).append(parsed + [glyph])
    answer = states.get(len(text), [])
    assert len(answer) == 1, (text, answer)
    return answer[0]


def main():
    spec = json.loads(CONTRACT.read_text())
    review = json.loads(REVIEW.read_text())
    assert review['contract_sha256'] == hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    alphabet = spec['physical_alphabet']['units']
    assert len(alphabet) == len(set(alphabet)) == 22
    channel = spec['literal_name_channel']
    digits = channel['digit_units_in_order']
    ordinary = channel['ordinary_source_letters_in_order']
    rare = channel['rare_source_characters_in_order']
    assert len(digits) == len(set(digits)) == 21 and 'q' not in digits
    assert ordinary == list(string.ascii_lowercase[:21])
    assert len(rare) == len(set(rare)) == 74
    assert set(ordinary).isdisjoint(rare)
    assert set(ordinary + rare) == {chr(i) for i in range(32, 127)}
    table = {c: [digits[i]] for i, c in enumerate(ordinary)}
    table.update({c: ['q', digits[i // 21], digits[i % 21]] for i, c in enumerate(rare)})
    assert len({tuple(v) for v in table.values()}) == 95

    def literal(payload):
        result = []
        i = 0
        while i < len(payload):
            glyph = payload[i]
            if glyph == 'q':
                assert i + 2 < len(payload)
                j = 21 * digits.index(payload[i+1]) + digits.index(payload[i+2])
                assert j < len(rare)
                result.append(rare[j])
                i += 3
            else:
                result.append(ordinary[digits.index(glyph)])
                i += 1
        return ''.join(result)

    assert all(literal(table[c]) == c for c in table)
    lesson = spec['whole_hand_message_with_answer_exposed']
    sentences, sentence, pending = [], [], False
    cell_counts = []
    for row in lesson['physical_rows']:
        compact = row['body_compact']
        # The fixed example has only the declared ordinary/wide gaps.
        chunks = compact.split('   ')
        assert all('  ' not in c for c in chunks)
        cells = compact.count(' ')
        for j, chunk in enumerate(chunks):
            if j:
                assert sentence and not pending
                sentences.append(sentence)
                sentence = []
            for k, word in enumerate(chunk.split(' ')):
                glyphs = units(word, alphabet)
                cells += len(glyphs)
                if pending:
                    assert j == k == 0 and sentence
                    sentence[-1].extend(glyphs)
                    pending = False
                else:
                    sentence.append(glyphs)
        assert cells == row['occupied_cells_including_gaps'] <= 24
        cell_counts.append(cells)
        if row['margin'] == 'a':
            assert cells == 24
            pending = True
        elif row['margin'] == 'o':
            assert sentence
            sentences.append(sentence)
            sentence = []
        else:
            assert row['margin'] == 'blank'
    assert not pending and not sentence
    assert sentences == [s['groups'] for s in lesson['logical_groups']]
    name = literal(sentences[2][2])
    assert name == review['manual_name_account']['recovered']
    suffixes = spec['word_grammar']['complete_suffix_tails']
    assert len(suffixes) == len({tuple(s) for s in suffixes}) == 9
    entries = {(tuple(e['units']), e['class']): e['meaning'] for e in spec['open_lexicon']['teaching_entries_only']}
    analyses = []
    for groups in sentences:
        terms = []
        i = 0
        while i < len(groups) - 1:
            if groups[i] == ['r', 'y', 'r']:
                assert groups[i+2] == ['r', 'y', 'l']
                terms.append(literal(groups[i+1]))
                i += 3
            else:
                terms.append(entries[(tuple(groups[i]), 'term')])
                i += 1
        assert i == len(groups) - 1
        pred = groups[-1]
        past = pred[:3] == ['r', 'y', 'p']
        if past:
            pred = pred[3:]
        positions = [j for j in range(len(pred)-1) if pred[j:j+2] == ['r', 'y']]
        assert len(positions) <= 1
        if positions:
            j = positions[0]
            root, tail = pred[:j], pred[j+2:]
            assert tail in suffixes
        else:
            root, tail = pred, []
        meaning = entries[(tuple(root), 'property')]
        assert len(terms) == (2 if 'o' in tail else 1)
        analyses.append({'terms': terms, 'property': meaning, 'past': past,
                         'change': 'e' in tail, 'cause': 'o' in tail,
                         'property_complement': 'a' in tail, 'outer_negation': 'n' in tail})
    assert [a['cause'] for a in analyses] == [False, True, True]
    assert [a['outer_negation'] for a in analyses] == [False, True, False]
    assert [a['property_complement'] for a in analyses] == [False, False, True]
    result = {
        'status': 'PASS_EXPOSED_LESSON_RECORD_REPLAY',
        'scope': 'Component table and displayed whole-message consistency only. No native data, historical fit, full-domain proof or independent comprehension.',
        'inputs': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (CONTRACT, REVIEW)},
        'printable_character_table_size': len(table),
        'body_cells': cell_counts, 'recovered_name': name,
        'reconstructed_sentences': sentences, 'analyses': analyses,
        'confirmed_native_meanings': 0,
    }
    target = HERE / 'PROPERTY953_HAND_REPLAY_RESULT_20261006.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'output': str(target.relative_to(ROOT))}))


if __name__ == '__main__':
    main()
