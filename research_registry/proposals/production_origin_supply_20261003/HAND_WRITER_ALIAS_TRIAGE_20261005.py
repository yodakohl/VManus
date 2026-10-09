#!/usr/bin/env python3
"""Fixed existing-packet census, not a test of synonymy or native identity."""
import hashlib
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def main():
    contract_path = BASE / 'HAND_WRITER_ALIAS_TRIAGE_CONTRACT_20261005.json'
    contract = json.loads(contract_path.read_text())
    source = ROOT / contract['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == contract['source_sha256']
    data = json.loads(source.read_text())
    out = []
    validation_cases = 0
    for orientation, fused, separate in contract['pairs']:
        for reader in contract['readers']:
            all_rows, eligible, buckets = {}, {}, {}
            for form in (fused, separate):
                all_rows[form] = [r for r in data['occurrences'][form]
                                  if r['edition'] == reader]
                assert all(r['ivtff_group_raw'] == form for r in all_rows[form])
                assert all(not r['page'].startswith('f84') for r in all_rows[form])
                eligible[form] = [r for r in all_rows[form]
                                  if r['kind'] == 'P'
                                  and r['left_separator'] == 'DEFINITE_SPACE'
                                  and r['right_separator'] == 'DEFINITE_SPACE'
                                  and re.fullmatch('[a-z]+', r['previous_literal'] or '')
                                  and re.fullmatch('[a-z]+', r['next_literal'] or '')]
                buckets[form] = defaultdict(list)
                for row in eligible[form]:
                    buckets[form][(row['previous_literal'], row['next_literal'])].append(row)
            hits = []
            for flank in sorted(buckets[fused].keys() & buckets[separate].keys()):
                for a, b in itertools.product(buckets[fused][flank], buckets[separate][flank]):
                    if a['locus'] == b['locus']:
                        continue
                    leaf_a = re.fullmatch(r'f(\d+)[rv]\d*', a['page']).group(1)
                    leaf_b = re.fullmatch(r'f(\d+)[rv]\d*', b['page']).group(1)
                    hits.append({'flanks': list(flank), 'fused': a, 'separate': b,
                                 'different_physical_leaf': leaf_a != leaf_b})
            # Cross-check by direct enumeration from all source rows, without buckets.
            brute = set()
            for a, b in itertools.product(all_rows[fused], all_rows[separate]):
                validation_cases += 1
                if a['locus'] == b['locus']:
                    continue
                if any(r['kind'] != 'P' or r['left_separator'] != 'DEFINITE_SPACE'
                       or r['right_separator'] != 'DEFINITE_SPACE' for r in (a, b)):
                    continue
                flanks_a = (a['previous_literal'], a['next_literal'])
                flanks_b = (b['previous_literal'], b['next_literal'])
                if flanks_a != flanks_b or any(not re.fullmatch('[a-z]+', x or '') for x in flanks_a):
                    continue
                brute.add((a['source_group_id'], b['source_group_id']))
            assert brute == {(h['fused']['source_group_id'], h['separate']['source_group_id']) for h in hits}
            item = {'orientation': orientation, 'forms': [fused, separate], 'reader': reader,
                    'all_exact_counts': {f: len(all_rows[f]) for f in all_rows},
                    'eligible_counts': {f: len(eligible[f]) for f in eligible},
                    'distinct_flank_counts': {f: len(buckets[f]) for f in buckets},
                    'pair_count': len(hits),
                    'cross_leaf_pair_count': sum(h['different_physical_leaf'] for h in hits),
                    'hits': hits}
            out.append(item)
            print(reader, fused, separate, item['eligible_counts'], 'pairs', len(hits))
    result = {'status': 'MATCHES_REQUIRE_PROVENANCE_REVIEW' if any(r['hits'] for r in out)
              else 'NO_FIXED_PAIR_SHARED_LITERAL_FLANKS',
              'source': contract['source'], 'source_sha256': contract['source_sha256'],
              'contract_sha256': hashlib.sha256(contract_path.read_bytes()).hexdigest(),
              'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'results': out,
              'validation': {'direct_product_crosscheck': 'PASS', 'candidate_pairs_checked': validation_cases},
              'limits': contract['limits'] + ['No matched flanks would not refute the aliases or G2.']}
    (BASE / 'HAND_WRITER_ALIAS_TRIAGE_RESULT_20261005.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
