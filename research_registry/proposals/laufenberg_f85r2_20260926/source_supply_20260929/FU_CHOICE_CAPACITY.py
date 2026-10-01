#!/usr/bin/env python3
"""Exact navigation on the pinned already-admitted source-only projection."""
import csv
import gzip
import hashlib
import json
from pathlib import Path

source = Path('experiments/yolo/gdt1106_frozen_domain_transfer/artifacts/SOURCE.tsv.gz')
expected = 'e7476ce8ed73861d730c30abb257cbb4a000c379ba662509bf3efa217047f183'
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
allowed_source = Path('experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv')
with allowed_source.open() as f:
    allowed_rows = list(csv.DictReader(f, delimiter='\t'))
page_key = 'page' if 'page' in allowed_rows[0] else 'selector'
allowed = {row[page_key] for row in allowed_rows}
assert len(allowed) == 179 and not any(p.startswith('f84') for p in allowed)
previous = None
matches = []
groups = 0
with gzip.open(source, 'rt', newline='') as f:
    for row in csv.DictReader(f, delimiter='\t'):
        # The entire compressed input is a pinned, validated admitted-only
        # derivative, not a mixed raw TSV. No further target body is displayed.
        assert row['page'] in allowed and not row['page'].startswith('f84')
        assert row['kind'] == 'P'
        groups += 1
        key = (row['edition'], row['page'], row['locus'])
        if previous is not None:
            old_key = (previous['edition'], previous['page'], previous['locus'])
            if (key == old_key
                and int(row['source_group_index']) == int(previous['source_group_index']) + 1
                and previous['ivtff_group_raw'] == 'chey'
                and row['ivtff_group_raw'] == 'tal'):
                matches.append({k:row[k] for k in ('edition','page','locus')} | {
                    'first_index':int(previous['source_group_index']),
                    'second_index':int(row['source_group_index']),
                    'first_source_id':previous['source_group_id'],
                    'second_source_id':row['source_group_id']})
        previous = row
assert groups == 94855
result = {
    'status':'EXACT_WITHIN_LINE_CAPACITY_ONLY_NO_MEANING_TEST',
    'source_path':source.as_posix(),'source_sha256':expected,
    'groups_examined':groups,'admitted_selectors':179,
    'match_rule':'exact chey then tal, consecutive source indices, same edition/page/locus',
    'matches':matches,
    'reader_matches':len(matches),
    'physical_loci':len({(r['page'],r['locus']) for r in matches}),
    'additional_physical_loci':[list(v) for v in sorted({(r['page'],r['locus']) for r in matches if r['locus']!='f83r.15'})],
    'new_context_bodies_printed':0,'approximate_or_cross_line_matches':False,
    'meaning_binding':False,'confirmed_words':0,'independent_confirmation_capacity':0}
print(json.dumps(result,ensure_ascii=False,indent=2))
