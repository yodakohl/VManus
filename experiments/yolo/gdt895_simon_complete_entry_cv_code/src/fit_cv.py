#!/usr/bin/env python3
"""Complete panel equations with one CV key and distinct complete source entries."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import time

import check_entry_domains as domains
import cv_equations as cv


class OutputLimit(Exception):
    pass


def panel_solutions(targets, entries, domain_rows, deadline, solution_limit):
    source = {row['id']: row for row in entries}
    target = {row['id']: row for row in targets}
    order = sorted(domain_rows, key=lambda r: (len(r['candidate_source_ids']), r['paragraph']))
    models, used, choices = [], set(), []
    stats = {'nodes': 0}

    def visit(index, mapping, inherent):
        if time.monotonic() >= deadline:
            raise cv.BudgetExpired()
        if index == len(order):
            if len(models) >= solution_limit:
                raise OutputLimit()
            models.append({'inherent': inherent, 'assignments': list(choices),
                           'observed_component_codes': dict(sorted(mapping.items()))})
            return
        row = order[index]
        paragraph = row['paragraph']
        for ident in row['candidate_source_ids']:
            if ident in used:
                continue
            for extension in cv.entry_extensions(source[ident]['words'], target[paragraph]['words'],
                    inherent, initial=mapping, deadline=deadline, stats=stats):
                used.add(ident); choices.append([paragraph, ident])
                try:
                    visit(index + 1, extension, inherent)
                finally:
                    choices.pop(); used.remove(ident)

    status = 'COMPLETE'
    try:
        for inherent in cv._core.VOWELS:
            visit(0, {}, inherent)
    except cv.BudgetExpired:
        status = 'UNKNOWN_BUDGET'
    except OutputLimit:
        status = 'UNKNOWN_OUTPUT_LIMIT'
    except RecursionError:
        status = 'UNKNOWN_RECURSION_LIMIT'
    assignments = {tuple(tuple(p) for p in m['assignments']) for m in models}
    plaintexts = {tuple((p, tuple(source[e]['words'])) for p, e in m['assignments']) for m in models}
    return {'status': ('UNSAT_COMPLETE_CV_ENUMERATION' if not models else 'SAT_COMPLETE_OBSERVED_MODELS')
                     if status == 'COMPLETE' else status,
            'enumeration_complete': status == 'COMPLETE', 'model_count': len(models),
            'distinct_entry_assignments': len(assignments), 'distinct_plaintext_projections': len(plaintexts),
            'unused_component_values_identified': False, 'models': models, 'stats': stats}


def main():
    parser = argparse.ArgumentParser()
    for name in ('source-pool', 'source-lock', 'source-audit', 'target-packet', 'domains', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--budget-seconds', type=float, required=True, help='One total budget shared by all unresolved panels')
    parser.add_argument('--solution-limit', type=int, required=True, help='Exceeding the preregistered cap returns UNKNOWN')
    args = parser.parse_args()
    if args.budget_seconds <= 0 or args.solution_limit <= 0:
        parser.error('positive registered resource limits required')
    paths = (args.source_pool, args.source_lock, args.source_audit)
    source_raw, lock_raw, audit_raw = (p.read_bytes() for p in paths)
    pool, lock, audit = (json.loads(raw) for raw in (source_raw, lock_raw, audit_raw))
    sha = domains.sha
    if (lock['status'] != 'FROZEN' or lock['source_pool_sha256'] != sha(source_raw)
            or lock['source_audit_sha256'] != sha(audit_raw) or audit['status'] != 'PASS'
            or audit['source_pool_sha256'] != sha(source_raw) or pool['pending']
            or audit['capture_sha256'] != pool['capture_sha256']):
        raise ValueError('source freeze and independent audit required before target access')
    domain_raw = args.domains.read_bytes()
    previous = json.loads(domain_raw)
    target_raw = args.target_packet.read_bytes()
    if sha(target_raw) != domains.PACKET_SHA256:
        raise ValueError('target packet byte binding mismatch; refusing to parse')
    packet = json.loads(gzip.decompress(target_raw))
    expected = domains.check(pool, packet)
    for key in ('source_profiles', 'panels', 'status', 'source_entry_count'):
        if previous[key] != expected[key]:
            raise ValueError('complete source domains changed: ' + key)
    for key, raw in (('source_pool_sha256', source_raw), ('source_lock_sha256', lock_raw),
                     ('source_audit_sha256', audit_raw), ('target_packet_sha256', target_raw)):
        if previous[key] != sha(raw):
            raise ValueError('domain certificate input binding mismatch')
    started = time.monotonic(); deadline = started + args.budget_seconds
    results = {}
    for edition in domains.PANELS:
        domain = previous['panels'][edition]
        if domain['empty_domains']:
            results[edition] = {'status': 'UNSAT_EMPTY_COMPLETE_ENTRY_DOMAIN',
                                'enumeration_complete': True, 'key_search_performed': False,
                                'empty_domain_count': domain['empty_domains']}
        else:
            results[edition] = panel_solutions(packet['panels'][edition], pool['entries'],
                domain['records'], deadline, args.solution_limit)
            results[edition]['key_search_performed'] = True
    result = {'schema': 'GDT895_COMPLETE_CV_PANEL_RESULT_V1', 'panels': results,
              'all_panels_complete': all(r['enumeration_complete'] for r in results.values()),
              'source_pool_sha256': sha(source_raw), 'source_lock_sha256': sha(lock_raw),
              'source_audit_sha256': sha(audit_raw), 'target_packet_sha256': sha(target_raw),
              'domain_certificate_sha256': sha(domain_raw),
              'source_hashes': {name: sha(Path(__file__).with_name(name).read_bytes())
                  for name in ('fit_cv.py', 'cv_equations.py', 'check_entry_domains.py')},
              'elapsed_seconds': time.monotonic() - started, 'budget_seconds': args.budget_seconds,
              'solution_limit': args.solution_limit, 'held_access': False,
              'claim_ceiling': 'Conditional complete-source-entry equations only; missing sources, language and meaning untested.'}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({e: {k: v for k, v in row.items() if k != 'models'} for e, row in results.items()}))


if __name__ == '__main__':
    main()
