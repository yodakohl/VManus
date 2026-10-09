"""Verify retained construction evidence after the root's manual reading.

This checks bytes, tables, physical counts and the qok impossibility.
It is not a semantic decoder or a validator of the manual meaning judgment.
"""
from pathlib import Path
import copy
import hashlib
import json

HERE = Path(__file__).parent


def read(name):
    return json.loads((HERE / name).read_text())


def main():
    report = read('HUMAN_SYLLABARY954_ROOT_REVIEW.json')
    for name, digest in report['input_hashes'].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
    raw = read('HUMAN_SPOKEN_SYLLABARY_WRITER_RAW_20261006.json')['design']
    rules = read('HUMAN_SYLLABARY954_READER_RULES.json')['rules']
    for key, value in rules.items():
        original = copy.deepcopy(raw[key])
        if key == 'literal_names':
            original.pop('examples')
        assert original == value, key
    glyphs = rules['phonology_and_glyphs']['G_in_order']
    assert len(glyphs) == len(set(glyphs)) == 21 and 'q' not in glyphs
    columns = rules['literal_names']['column_labels']
    assert columns == glyphs
    chars = [c for row in rules['literal_names']['rows']
             for c in row['characters'] if c is not None]
    assert len(chars) == len(set(chars)) == 83
    assert all(len(row['characters']) == 21 for row in rules['literal_names']['rows'])
    controls = [tuple(e['glyphs']) for e in rules['control_table']['entries']]
    assert len(controls) == len(set(controls)) == 8
    assert all(len(c) == 3 and c[:2] == ('q', 'o') for c in controls)
    assert ('q', 'o', 'k') not in controls
    assert all(e['glyphs'] and set(e['glyphs']) <= set(glyphs)
               for e in rules['teaching_lexicon'])

    challenge = (HERE / 'HUMAN_SYLLABARY954_MANUAL_CHALLENGE.txt').read_text()
    lines = challenge.rstrip().split('\n')[-4:]
    valid = set(glyphs) | {'q'}
    physical_counts, cells = [], []
    for line in lines:
        groups = line.split('   ')
        tokens = [x for g in groups for x in g.split(' ')]
        assert tokens and all(x in valid for x in tokens)
        physical_counts.append(len(tokens))
        cells.append(len(tokens) + len(groups) - 1)
    frozen = read('HUMAN_SYLLABARY954_ROOT_READBACK_FROZEN.json')
    counts = frozen['physical_hand_count']
    assert cells == counts['physical_lines_used_cells_including_visible_blanks']
    assert max(cells) <= 24
    assert sum(physical_counts) == counts['physical_signs'] == 69
    assert counts['logical_signs_excluding_continuation'] == 66
    assert lines[1].endswith('q o s')

    profiles = read('HUMAN_SYLLABARY954_KNOWN_FORM_PROFILES.json')['profiles']
    selected = report['native_form_countercase']['counterexample_forms']
    assert [p['form'] for p in profiles] == selected
    assert all(form.startswith('qok') for form in selected)
    for reader, row in report['native_form_countercase']['existing_frequency_profiles'].items():
        counts = {p['form']: p['editions'][reader]['count'] for p in profiles}
        totals = {p['editions'][reader]['total_groups'] for p in profiles}
        assert len(totals) == 1
        total = totals.pop()
        assert counts == row['selected_whole_form_counts']
        assert sum(counts.values()) == row['sum_of_these_disjoint_exact_forms']
        assert total == row['existing_profile_total_groups']
        assert sum(counts.values()) / total == row['fraction_of_profile_groups']
    note = read('HUMAN_SYLLABARY954_SELECTOR_PERMUTATION_NOTE.json')
    root = Path(__file__).resolve().parents[3]
    old_hits = root / note['source']['path']
    assert hashlib.sha256(old_hits.read_bytes()).hexdigest() == note['source']['sha256']
    selected_hits = [r for r in json.loads(old_hits.read_text())
                     if r['locus'] == 'f79v.19' and r['raw'] == 'qokedy']
    assert selected_hits == note['source']['witnesses']
    assert {r['edition'] for r in selected_hits} == {'IT2a', 'RF1b', 'ZL3b'}
    assert {c['candidate_function_of_qok'] for c in note['function_cases']} == {
        c['function'] for c in rules['control_table']['entries']}
    for hit in selected_hits:
        assert len(hit['groups']) == 3
        for group in hit['groups']:
            assert group['ivtff_group_raw'] == 'qokedy'
            assert group['left_separator'] == group['right_separator'] == 'DEFINITE_SPACE'
    print('PASS: hashes, frozen rule copy, tables, physical hand counts, '
          'unlicensed qok control, separate counts, old triples and eight case labels')
    print('Manual semantic equivalence remains an informed review judgment.')


if __name__ == '__main__':
    main()
