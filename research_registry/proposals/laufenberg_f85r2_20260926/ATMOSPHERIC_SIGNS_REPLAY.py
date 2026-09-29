#!/usr/bin/env python3
"""Source-byte, complete-chapter and bounded-inventory check; no meaning test."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import urllib.request

BASE = Path('research_registry/proposals/laufenberg_f85r2_20260926')

def extract(blob):
    source = blob.decode('utf-8')
    start = source.index('<H2><A NAME="13"></A>')
    end = source.index('<HR CLASS="endnotes">', start)
    part = source[start:end]
    part = re.sub(r'<SPAN CLASS="(?:Camerarius|pagenum)">.*?</SPAN>', '', part, flags=re.S)
    part = re.sub(r'<A CLASS="ref".*?</A>', '', part, flags=re.S)
    return [' '.join(html.unescape(re.sub('<[^>]*>', ' ', x)).split())
            for x in re.split(r'<P CLASS="justify">', part)]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--fetch', action='store_true'); args = ap.parse_args()
    receipt = json.loads((BASE/'ATMOSPHERIC_SIGNS_RECEIPTS_20260929.json').read_text())
    for row in receipt['sources']:
        path = Path(row['cache_path'])
        if not path.exists() and args.fetch:
            path.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(row['url'], timeout=30) as response:
                blob = response.read()
            assert hashlib.sha256(blob).hexdigest() == row['sha256'], row['id']
            path.write_bytes(blob)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], row['id']
    raw = Path(receipt['sources'][0]['cache_path']).read_bytes()
    complete = json.loads((BASE/'ATMOSPHERIC_SIGNS_COMPLETE_SOURCE_20260929.json').read_text())
    assert complete['source_sha256'] == hashlib.sha256(raw).hexdigest()
    actual = extract(raw)
    assert actual == [row['text'] for row in complete['paragraphs']]
    assert len(actual) == 9 and actual[1].startswith('Observations of the signs')
    assert actual[-1].startswith('Let us, then, consider')
    assert len(receipt['sources']) == 6
    assert receipt['new_candidate_witnesses_examined'] == 2 <= receipt['preregistered_max_new_illustrated_candidates']
    result = {'status':'PASS_SOURCE_ACCOUNTING_ONLY', 'cached_source_hashes_checked':6,
              'complete_chapter_body_paragraphs':8, 'complete_chapter_body_words':sum(len(x.split()) for x in actual[1:]),
              'new_candidate_witnesses':2, 'new_voynich_data':False,
              'native_observations_automatically_verified':False, 'semantic_validation':False}
    (BASE/'ATMOSPHERIC_SIGNS_VALIDATION_20260929.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))
if __name__ == '__main__': main()
