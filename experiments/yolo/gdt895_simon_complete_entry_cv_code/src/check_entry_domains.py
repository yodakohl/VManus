#!/usr/bin/env python3
"""Exact complete-entry necessary condition, before any component-key search.

Only the previously published odd-only GDT893 packet is an admitted target.
Full modern source text stays in the caller's cache. The public certificate
contains equality partitions, source IDs and byte bindings, never source prose.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re

PACKET_SHA256 = '1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed'
PANELS = {'ZL3b': 14, 'IT2a': 259, 'RF1b': 11, 'CONSENSUS': 1}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def partition(words):
    first = {}
    return tuple(first.setdefault(word, len(first)) for word in words)


def source_profiles(pool):
    rows = []
    for entry in pool['entries']:
        words = entry['words']
        if (entry['status'] != 'ACCEPTED' or not words
                or any(not re.fullmatch('[a-z]+', w) for w in words)):
            raise ValueError('invalid admitted source entry')
        rows.append({'id': entry['id'], 'word_count': len(words),
                     'equality_partition': list(partition(words)),
                     'word_sequence_sha256': sha(json.dumps(words, ensure_ascii=False,
                         separators=(',', ':')).encode('utf-8')),
                     'html_sha256': entry['html_sha256']})
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('duplicate source ID')
    return rows


def check(pool, packet):
    if packet['schema'] != 'GDT893_ODD_ONLY_FIT_PACKET_V1' or set(packet['panels']) != set(PANELS):
        raise ValueError('wrong inherited target packet schema')
    sources = source_profiles(pool)
    by_pattern, by_length = defaultdict(list), Counter()
    for row in sources:
        by_pattern[tuple(row['equality_partition'])].append(row['id'])
        by_length[row['word_count']] += 1
    panels = {}
    for edition, targets in packet['panels'].items():
        if len(targets) != PANELS[edition] or len({t['id'] for t in targets}) != len(targets):
            raise ValueError('inherited complete paragraph scope changed')
        records = []
        for target in targets:
            folio = target['physical_folio']
            if (not re.fullmatch('f[0-9]+', folio) or int(folio[1:]) % 2 != 1
                    or target['page'].startswith('f84') or target['page'].startswith('f116')):
                raise ValueError('outside admitted odd paragraph scope')
            words = target['words']
            if not words or len(words) != len(target['source_group_ids']):
                raise ValueError('incomplete target group sequence')
            if any(not re.fullmatch('[a-z]+', w) for w in words):
                raise ValueError('inherited target outside declared literal code alphabet')
            pattern = partition(words)
            candidates = by_pattern.get(pattern, [])
            records.append({'paragraph': target['id'], 'page': target['page'],
                            'word_count': len(words), 'equality_partition': list(pattern),
                            'same_length_source_entries': by_length[len(words)],
                            'candidate_source_ids': list(candidates)})
        empty = [r['paragraph'] for r in records if not r['candidate_source_ids']]
        panels[edition] = {
            'status': 'UNSAT_EMPTY_COMPLETE_ENTRY_DOMAIN' if empty else 'NECESSARY_CONDITION_ONLY',
            'paragraphs': len(records), 'target_words': sum(r['word_count'] for r in records),
            'empty_domains': len(empty), 'empty_domain_paragraphs': empty,
            'length_only_empty_domains': sum(r['same_length_source_entries'] == 0 for r in records),
            'candidate_pairs': sum(len(r['candidate_source_ids']) for r in records),
            'records': records}
    return {'schema': 'GDT895_COMPLETE_ENTRY_DOMAINS_V1',
            'status': 'ALL_PANELS_UNSAT' if all(p['empty_domains'] for p in panels.values()) else 'SOME_PANELS_NOT_EXCLUDED',
            'source_entry_count': len(sources), 'source_profiles': sources, 'panels': panels,
            'key_search_performed': False, 'held_access': False,
            'claim_ceiling': 'Necessary-condition rejection of total complete-entry copying on this frozen partial edited pool only.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-pool', type=Path, required=True)
    parser.add_argument('--source-lock', type=Path, required=True)
    parser.add_argument('--source-audit', type=Path, required=True)
    parser.add_argument('--target-packet', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source_raw, lock_raw, audit_raw = (p.read_bytes() for p in
        (args.source_pool, args.source_lock, args.source_audit))
    pool, lock, audit = (json.loads(raw) for raw in (source_raw, lock_raw, audit_raw))
    if (lock['status'] != 'FROZEN' or lock['source_pool_sha256'] != sha(source_raw)
            or lock['source_audit_sha256'] != sha(audit_raw) or audit['status'] != 'PASS'
            or audit['source_pool_sha256'] != sha(source_raw)
            or audit['capture_sha256'] != pool['capture_sha256']
            or pool['pending']):
        raise ValueError('source acquisition and independent validation must be frozen before target access')
    target_raw = args.target_packet.read_bytes()
    if sha(target_raw) != PACKET_SHA256:
        raise ValueError('target packet byte hash mismatch; refusing to parse')
    result = check(pool, json.loads(gzip.decompress(target_raw)))
    result.update(source_pool_sha256=sha(source_raw), source_lock_sha256=sha(lock_raw),
                  source_audit_sha256=sha(audit_raw), target_packet_sha256=sha(target_raw),
                  implementation_sha256=sha(Path(__file__).read_bytes()))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'source_entry_count': result['source_entry_count'],
        'panels': {e: {k: v for k, v in p.items() if k not in ('records', 'empty_domain_paragraphs')}
                   for e, p in result['panels'].items()}}))


if __name__ == '__main__':
    main()
