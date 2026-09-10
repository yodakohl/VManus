#!/usr/bin/env python3
"""Build the declared source-exposed pair certificate; never search target data."""
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]

def canonical(words):
    key = {}
    encoded = []
    for word in words:
        row = []
        for syllable in word:
            if syllable not in key:
                key[syllable] = f'C{len(key)+1:02d}'
            row.append(key[syllable])
        encoded.append(row)
    return encoded, {v:k for k,v in key.items()}

def main():
    spec = json.loads((E/'src/SPEC.json').read_text())
    a, b, scans, ends = [], [], [], []
    for verse in spec['verses']:
        words = [w.split('-') for w in verse['syllabified'].split()]
        other = [spec['alternative']['to'] if w == spec['alternative']['from'] else w for w in words]
        a.extend(words); b.extend(other); ends.append(len(a))
        types = list(verse['first_five_feet']) + ['X']
        lengths = [3 if f == 'D' else 2 for f in types]
        flat = [s for w in words for s in w]
        flat_b = [s for w in other for s in w]
        assert len(flat) == sum(lengths)
        pos, feet_a, feet_b = 0, [], []
        for kind, n in zip(types, lengths):
            weight = {'D':'LSS','S':'LL','X':'LX'}[kind]
            feet_a.append({'syllables':flat[pos:pos+n], 'weights':weight})
            feet_b.append({'syllables':flat_b[pos:pos+n], 'weights':weight})
            pos += n
        scans.append({'verse':verse['verse'],'A':feet_a,'B':feet_b,'quantity_notes':verse['quantity_notes']})
    ca, ka = canonical(a); cb, kb = canonical(b)
    assert ca == cb and ka != kb
    assert len(ka) == len(set(ka.values())) <= spec['channel']['max_symbols']
    assert len(kb) == len(set(kb.values())) <= spec['channel']['max_symbols']
    for key, truth in [(ka,a),(kb,b)]:
        assert [[key[c] for c in w] for w in ca] == truth
    result = {
      'status':'EXPOSED_SIX_VERSE_COLLISION_CONFIRMED',
      'evidence_kind':'constructed historical-text control; no manuscript experiment',
      'words':len(a),'syllables':sum(map(len,a)), 'symbol_types':len(ka),
      'ciphertext_words':ca, 'key_A':ka, 'key_B':kb,
      'plaintext_A':' '.join(''.join(w) for w in a),
      'plaintext_B':' '.join(''.join(w) for w in b),
      'changed_entries':{c:{'A':ka[c],'B':kb[c]} for c in ka if ka[c]!=kb[c]},
      'verse_end_word_offsets':ends,
      'same_ciphertext':True, 'injective_A':True, 'injective_B':True,
      'distinct_readings_proved_at_least':2,
      'all_possible_readings_enumerated':False,
      'grammatical_quantity_basis':'manual source/dictionary analyses and independent audit, not a grammar solver',
      'scans':scans,
      'blind_recovery_test_performed':False,
      'general_verse_boundary_inference_performed':False,
      'voynich_access':False, 'new_voynich_lexemes':0,
      'complete_historical_prescription':False,
      'binding_spec_sha256':hashlib.sha256((E/'src/SPEC.json').read_bytes()).hexdigest(),
    }
    (E/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    lines=['# Complete explicit certificate','',
      'A is the printed historical excerpt; B is a constructed alternative, not an attested text.',
      'The source and proposed contrast were exposed before computation.','',
      '## Ciphertext with word boundaries and no verse boundaries','',
      ' '.join('.'.join(w) for w in ca),'',
      '## Readings and scans','']
    for scan in scans:
        for k in ['A','B']:
            lines.append(f"{scan['verse']} {k}: "+' | '.join('-'.join(f['syllables']) for f in scan[k]))
        lines.append('Weights: '+' | '.join(f['weights'] for f in scan['A']))
        lines.append('')
    lines += ['## Full keys','','| Symbol | A | B |','|---|---|---|']
    lines += [f'| {c} | {ka[c]} | {kb[c]} |' for c in ka]
    (E/'artifacts/CERTIFICATE.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:result[k] for k in ['status','words','syllables','symbol_types','changed_entries']}))

if __name__ == '__main__': main()
