#!/usr/bin/env python3
"""Independent conditional impossibility proof; no cyclic order or decoder fit.
Supply the original CHD HTML cache explicitly. Target rows are obtained only
through the workspace guarded selector, never by parsing mixed raw TSV rows.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from html.parser import HTMLParser


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)


def plain(fragment):
    p = Text()
    p.feed(fragment)
    return ''.join(p.parts)


def normalize(raw):
    s = raw.strip().lower().replace('*', '').replace('-', '')
    if s.endswith('.'):
        s = s[:-1]
    if not re.fullmatch('[a-z]+', s):
        raise ValueError('Unexpected source character or empty cell')
    return s


def extract(raw):
    # Bind the month header and only its own following table rows. Modern
    # explanatory names are the third/sixth cells and never enter extraction.
    text = raw.decode('latin-1')
    assert text.count('<b>FEBRUARIUS</b>') == 1
    section = text.split('<b>FEBRUARIUS</b>', 1)[1].split('<b>MARTIUS</b>', 1)[0]
    found = {}
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', section, re.I | re.S):
        cells = re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.I | re.S)
        for i in (0, 3):
            if len(cells) <= i + 1:
                continue
            number = plain(cells[i]).strip()
            if not re.fullmatch(r'\d+\.', number):
                continue
            day = int(number[:-1])
            assert day not in found
            raw_cell = plain(cells[i + 1])
            found[day] = {'day': day, 'raw_text': raw_cell,
                          'written_atoms': normalize(raw_cell)}
    assert sorted(found) == list(range(1, 29))
    return [found[d] for d in range(1, 29)]


def self_test():
    assert normalize(' *Bri- \n') == 'bri'
    assert normalize(' de.') == 'de'
    for bad in ('a b', 'á', '.', 'a..', 'a/b', ''):
        try:
            normalize(bad)
        except ValueError:
            continue
        raise AssertionError(bad)
    # Illustration, not the proof: nonempty distinct prefix code on two atoms.
    from itertools import product
    words = [''.join(w) for n in range(7) for w in product('ab', repeat=n)]
    code = {'a': '0', 'b': '10'}
    assert len({''.join(code[c] for c in w) for w in words}) == len(words)
    # Merely distinct non-prefix codewords do NOT imply string injectivity.
    assert '0' + '00' == '00' + '0'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-html', required=True)
    p.add_argument('--artifacts', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    self_test()
    source_path = a.artifacts / 'SOURCE_INPUT.json'
    target_path = a.artifacts / 'TARGET_INPUT.json'
    s = json.loads(source_path.read_text())
    t = json.loads(target_path.read_text())
    assert sha(a.source_html) == s['source_html_sha256']
    cells = extract(Path(a.source_html).read_bytes())
    for fresh, frozen in zip(cells, s['cells'], strict=True):
        assert all(fresh[k] == frozen[k] for k in fresh)
    assert len({x['written_atoms'] for x in cells}) == 28
    loci = [f'f69v.{i}' for i in range(4, 32)]
    assert t['scope']['loci'] == loci
    assert len(t['entries']) == 28
    provenance = t['source_provenance']
    assert sha(provenance['path']) == provenance['sha256']
    cmd = ['./vmanus-exp', 'query-tsv', provenance['path'], '--selector', 'locus',
           '--columns', 'edition,locus,source_group_index,source_group_count,ivtff_group_raw',
           '--forbid-prefix', 'f84']
    for locus in loci:
        cmd.extend(['--allow', locus])
    proc = subprocess.run(cmd, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(proc.stdout), delimiter='\t'))
    assert len(rows) == 100
    panels = ('ZL3b', 'IT2a', 'RF1b')
    recovered = {}
    for entry in t['entries']:
        locus = entry['locus']
        assert locus in loci and locus not in recovered
        recovered[locus] = {}
        for panel in panels:
            rr = sorted((r for r in rows if r['locus'] == locus and r['edition'] == panel),
                        key=lambda r: int(r['source_group_index']))
            assert rr and [int(r['source_group_index']) for r in rr] == list(range(1, len(rr)+1))
            assert all(int(r['source_group_count']) == len(rr) for r in rr)
            groups = [r['ivtff_group_raw'] for r in rr]
            assert groups == entry['raw_groups'][panel]
            recovered[locus][panel] = groups
    witnesses = []
    for panel in panels:
        assert recovered['f69v.14'][panel] == recovered['f69v.18'][panel] == ['okeod']
        witnesses.append({'panel': panel, 'loci': ['f69v.14', 'f69v.18'],
                          'complete_raw_groups_each': ['okeod']})
    result = {
        'schema': 'GDT898_INDEPENDENT_INJECTIVITY_VALIDATION_V1',
        'status': 'PASS_CONDITIONAL_MODEL_IMPOSSIBLE',
        'source_input_sha256': sha(source_path), 'target_input_sha256': sha(target_path),
        'source_html_sha256': sha(a.source_html), 'source_url': s['source_url'],
        'target_source_sha256': provenance['sha256'],
        'source_cells_independently_extracted': cells, 'distinct_source_strings': 28,
        'target_entries_replayed': 28, 'target_group_rows_replayed': len(rows),
        'guard_receipt': proc.stderr.strip(), 'duplicate_witnesses': witnesses,
        'proof': [
            'Assume distinct source atoms have distinct nonempty prefix-free codewords.',
            'For equal encoded strings, their first codewords are comparable by prefix. Prefix-freeness forces equality; atom injectivity forces equal first atoms.',
            'Cancel that common codeword and induct. Nonemptiness prevents a nonempty remainder encoding the empty string. Thus the induced morphism is injective on every finite source string.',
            'All 28 source strings are distinct; every bijection to 28 complete target entries must therefore yield distinct outputs.',
            'The two distinct entries f69v.14 and f69v.18 instead have the same complete single-group literal output in each panel. This contradicts every bijection, including every cyclic phase and direction.'
        ],
        'scope': 'Conditional on the fixed CHD letters-only February edition and literal target panels; not a refutation of every historical Cisiojanus variant.',
        'limitations': [
            'Exact diplomatic native source collation remains unresolved; editorial reading is an explicit condition.',
            'Panels are alternate readings of one manuscript, not three independent manuscript observations.',
            'The equality obstruction was noticed after raw target exposure, not preregistered blind.',
            'No native cyclic-order certification, continuous fit, decoder, calendar meaning or plaintext claim is required or supplied.',
            'Executable synthetic checks illustrate implementation behavior; the general result follows from the stated proof.'
        ],
        'synthetic_checks': 'PASS normalization/rejection and prefix-code illustration/non-prefix counterexample'
    }
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
