#!/usr/bin/env python3
"""Small independent GDT1136 accounting scaffold, prepared before author release.

Preparation checks only frozen source bookkeeping. Author-schema adapters and
existing-API probes are added after root release; no evolving author is opened.
No parser, fit engine, semantic validator or whole-state solver.
"""
from pathlib import Path
import collections
import csv
import hashlib
import json

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / 'artifacts/NATIVE_GROUPS.tsv'
SOURCE_SHA256 = '0f0533a11773dabf2051d1a8946014f9668475179820cea49c023beb7ac26c09'
COUNTS = {'ZL3b': 227, 'IT2a': 209, 'RF1b': 229}
FIELDS = ['source_group_id', 'edition', 'locus', 'page', 'section', 'currier',
          'hand', 'code', 'kind', 'grammar_scope', 'source_row_index',
          'source_group_index', 'source_group_count', 'paragraph_start',
          'paragraph_end', 'left_separator', 'right_separator', 'ivtff_group_raw']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_source():
    with SOURCE.open() as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        fields = reader.fieldnames
        rows = list(reader)
    return fields, rows

def compare_native_rows(source_rows, reported_native_rows):
    """Compare adapted native dictionaries, never normalize values or meanings.

    The caller must expose the actual source-field container after author
    release. No assumed author schema is certified by this helper.
    """
    expected = {r['source_group_id']: r for r in source_rows}
    counts = collections.Counter(r.get('source_group_id') for r in reported_native_rows)
    reported = {r.get('source_group_id'): r for r in reported_native_rows}
    missing = sorted(set(expected)-set(reported))
    extra = sorted(set(reported)-set(expected), key=str)
    duplicates = sorted((str(k), v) for k,v in counts.items() if v != 1)
    differences = []
    for sid in sorted(expected.keys() & reported.keys()):
        for field in FIELDS:
            if field not in reported[sid] or reported[sid][field] != expected[sid][field]:
                differences.append({'source_group_id': sid, 'field': field,
                                    'expected': expected[sid][field],
                                    'reported': reported[sid].get(field),
                                    'missing_field': field not in reported[sid]})
    order = {edition:
             [r['source_group_id'] for r in reported_native_rows if r.get('edition') == edition]
             == [r['source_group_id'] for r in source_rows if r['edition'] == edition]
             for edition in COUNTS}
    return {'exact_native_fields_and_per_edition_order': not (missing or extra or duplicates or differences) and all(order.values()),
            'reported_rows': len(reported_native_rows), 'missing_IDs': missing,
            'extra_IDs': extra, 'duplicate_IDs': duplicates,
            'field_difference_count': len(differences), 'field_differences_first20': differences[:20],
            'per_edition_order': order,
            'global_presentation_order_same': [r.get('source_group_id') for r in reported_native_rows]
                                             == [r['source_group_id'] for r in source_rows]}

def main():
    fields, rows = read_source()
    checks = {'source_pin': sha(SOURCE) == SOURCE_SHA256,
              'exact_18_fields': fields == FIELDS,
              'rows665_and_unique_IDs': len(rows) == len({r['source_group_id'] for r in rows}) == 665,
              'native_reader_counts': dict(collections.Counter(r['edition'] for r in rows)) == COUNTS,
              'registered_loci': {r['locus'] for r in rows} == {f'f101r.{n}' for n in range(1, 11)},
              'page_scope': {r['page'] for r in rows} == {'f101r'}}
    print(json.dumps({'status': 'PRE_AUTHOR_SOURCE_BOOKKEEPING_ONLY',
                      'checks': checks, 'source_sha256': sha(SOURCE),
                      'rows_by_edition': COUNTS, 'author_review': 'NOT_STARTED',
                      'scientific_validation': False}, indent=2))
    return 0 if all(checks.values()) else 1

if __name__ == '__main__':
    raise SystemExit(main())
