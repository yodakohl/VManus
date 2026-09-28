#!/usr/bin/env python3
"""Validate the pinned public quote and the complete result matrix."""
import csv
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

HERE = Path(__file__).resolve().parents[1]
URL = ('https://raw.githubusercontent.com/denoflore/ZFD/'
       '3f030a9293b8db15dc2c7b0d0e7c703e71711f62/'
       '05_Case_Studies/CASE_STUDIES.md')
SHA = '234c7689f9d1ee4cb3592009b8c468151399fff55015c971b633dfff45a75fb3'


def main():
    raw = urlopen(URL, timeout=20).read()
    assert hashlib.sha256(raw).hexdigest() == SHA
    source = raw.decode('utf-8')
    claims = list(csv.DictReader((HERE / 'src/claims.tsv').open(), delimiter='\t'))
    assert len(claims) == 6 and len({c['id'] for c in claims}) == 6
    assert all(c['quoted_raw_eva'] in source for c in claims)
    rows = list(csv.DictReader((HERE / 'artifacts/CASE_RESULTS.tsv').open(),
                               delimiter='\t'))
    assert len(rows) == 18
    assert {(r['id'], r['reader']) for r in rows} == {
        (c['id'], x) for c in claims for x in ('zl3b', 'it2a', 'rf1b')}
    assert all(r['page'] == next(c['page'] for c in claims if c['id'] == r['id'])
               for r in rows)
    assert all(int(r['groups']) == 6 and int(r['prose_loci']) > 0 for r in rows)
    fields = ('whole_line', 'same_line_span', 'adjacent_line_span', 'any_kind_span')
    assert all(not r[f] for r in rows for f in fields)
    result = json.loads((HERE / 'artifacts/RESULT.json').read_text())
    assert result['source_sha256'] == SHA
    assert result['tested_claims'] == 6 and result['tested_reader_pairs'] == 18
    assert all(result[f] == 0 for f in ('whole_line_matches',
               'same_line_span_matches', 'adjacent_line_span_matches',
               'all_kind_span_matches'))
    assert all(not loci for readers in result['kostain_exact_group_loci'].values()
               for loci in readers.values())
    print('PASS: pinned source quote, six-by-three matrix and zero-match counts')


if __name__ == '__main__':
    main()
