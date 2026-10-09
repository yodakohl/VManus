"""Check the narrow, already observed literal-carrier contradiction for943."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = json.loads((D / 'HAND_WRITER_IDEA943_LITERAL_RESULT_20261005.json').read_text())
    for rel, digest in result['input_hashes'].items():
        assert sha(ROOT / rel) == digest, rel
    raw = json.loads((D / 'HUMAN_SOURCE_EQUAL_LETTER_SEAM_RAW_20261005.json').read_text())
    table = raw['design']['teaching_carrier']
    ordinary = table['ordinary_signs_in_order']
    assert len(ordinary) == len(set(ordinary)) == 19
    assert set(ordinary).isdisjoint({'q', 'cfh', 'cph'})
    alphabet = tuple(ordinary + ['q', 'cfh', 'cph'])

    @lru_cache(None)
    def segment(s):
        if not s:
            return [()]
        return [(a,) + tail for a in alphabet if s.startswith(a)
                for tail in segment(s[len(a):])]

    parsed = [segment(s) for s in result['forms']]
    assert all(len(p) == 1 for p in parsed)
    left, right = [p[0] for p in parsed]
    assert all(a in ordinary for word in (left, right) for a in word)
    assert left[-1] == right[0] == 'y'
    # Every ordinary code has a distinct lowercase source letter in this table.
    assert ordinary.index(left[-1]) == ordinary.index(right[0])
    packet = json.loads((D / 'HAND_WORD_EXTREMES_PACKET_20261005.json').read_text())
    rows = [line for line in packet['lines'] if line['locus'] == 'f2r.1']
    assert sorted(line['edition'] for line in rows) == ['IT2a', 'RF1b', 'ZL3b']
    witnesses = []
    for line in rows:
        a, b = line['groups'][:2]
        assert [a['ivtff_group_raw'], b['ivtff_group_raw']] == result['forms']
        assert [a['source_group_index'], b['source_group_index']] == [1, 2]
        assert a['right_separator'] == b['left_separator'] == 'DEFINITE_SPACE'
        witnesses.append([a['source_group_id'], b['source_group_id']])
    assert result['status'] == 'LITERAL_TEACHING_CARRIER_CONTRADICTED'
    output = {'status': 'PASS', 'scientific_status': result['status'],
              'witnesses': witnesses, 'working_units': [left, right],
              'reader_independence': False, 'meanings_assigned': 0,
              'all_carrier_bijections_tested': False,
              'validator_sha256': sha(Path(__file__)),
              'result_sha256': sha(D / 'HAND_WRITER_IDEA943_LITERAL_RESULT_20261005.json')}
    (D / 'HAND_WRITER_IDEA943_LITERAL_VALIDATION_20261005.json').write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(output, ensure_ascii=False))


if __name__ == '__main__':
    main()
