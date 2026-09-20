#!/usr/bin/env python3
"""Check source identity/complete line coverage; does not validate meanings."""
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def main():
    packet = json.loads((BASE / 'BALNEIS_COMPLETE_CONTENT_20260920.json').read_text())
    source = ROOT / packet['source_path']
    note = ROOT / packet['interpretation_path']
    expected = [n for lo, hi in [(74,85),(123,134),(219,230),(393,404)]
                for n in range(lo, hi+1)]
    source_lines = source.read_text().splitlines()
    table = []
    for line in note.read_text().splitlines():
        if re.match(r'^\|\d+\|', line):
            fields = line.strip('|').split('|')
            assert len(fields) == 3
            table.append((int(fields[0]), fields[1], fields[2]))
    checks = {
        'unchanged_source_identity': hashlib.sha256(source.read_bytes()).hexdigest()
            == packet['source_sha256']
            == '397968f02fc5faf54161f2c0df9e7557f96d36e649a27a140e64c2cfe0c69ecd',
        'interpretation_identity': hashlib.sha256(note.read_bytes()).hexdigest()
            == packet['interpretation_sha256'],
        'all_48_source_lines_in_order': [r['source_line'] for r in packet['rows']]
            == expected == [r[0] for r in table],
        'all_original_lines_preserved': all(r['source_exact']
            == source_lines[r['source_line']-1] for r in packet['rows']),
        'all_content_and_scope_fields_replay': all(
            (r['source_line'],r['content_obligation'],r['representation_scope']) == t
            for r,t in zip(packet['rows'],table)),
        'unresolved_relations_not_called_complete':
            packet['semantic_resolution_complete'] is False
            and packet['unresolved_main_relation_lines'] == [85,397],
        'no_target_or_word_claim': packet['target_accesses'] == 0
            and packet['confirmed_voynich_words'] == 0,
    }
    receipt = json.loads((BASE / 'BALNEIS_BODMER_RECEIPT_20260920.json').read_text())
    checks['four_distinct_native_pages'] = [x['folio'] for x in receipt['images']] == ['7v','11v','26v','35v']
    checks['public_urls_and_sha256_identities'] = all(
        x['url'].startswith('https://media.e-codices.ch/iip/fmb/fmb-cb-0135/')
        and re.fullmatch('[0-9a-f]{64}', x['sha256']) and x['bytes'] > 0
        for x in receipt['images'])
    result = {'status':'PASS' if all(checks.values()) else 'FAIL',
              'scope':'Source identity and coverage only; same-author checker; no semantic certification',
              'checks':checks,'covered_source_lines':len(expected)}
    (BASE / 'BALNEIS_COMPLETE_CONTENT_VALIDATION_20260920.json').write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2))
    assert all(checks.values())


if __name__ == '__main__':
    main()
