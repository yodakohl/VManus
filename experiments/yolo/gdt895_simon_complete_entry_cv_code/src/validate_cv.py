#!/usr/bin/env python3
"""Independent CV panel replay: complete local tables, then exhaustive joins."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import time

import validate_entry_domains as domain_validator
import validate_cv_equations as local_kernel

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
VOWELS = 'aeiouy'
EXPECTED_LOCAL_KERNEL_SHA256 = 'b63aca4ef25033c894634d9fe64f29d3e2f218cd45e2154764b8202112e9fd49'
EXPECTED_DOMAIN_VALIDATOR_SHA256 = 'ab768e967b75a573704be1448e831c18a8b480eda326714a661234e2f533caa8'


class Stopped(Exception):
    pass


def extendible(mapping):
    """Independent global injectivity, prefix, and 27-leaf completion check."""
    values = list(mapping.values())
    if len(values) > 27 or len(set(values)) != len(values):
        return False
    if any(not isinstance(v, str) or len(v) not in (1, 2)
           or any(c not in ALPHABET for c in v) for v in values):
        return False
    if any(a != b and b.startswith(a) for a in values for b in values):
        return False
    singletons = sum(len(v) == 1 for v in values)
    return singletons + 26 * (26 - singletons) >= 27


def join_key(left, right):
    if any(k in left and left[k] != v for k, v in right.items()):
        return None
    combined = dict(left)
    combined.update(right)
    return combined if extendible(combined) else None


def canonical_model(model):
    return (model['inherent'], tuple(sorted(tuple(p) for p in model['assignments'])),
            tuple(sorted(model['observed_component_codes'].items())))


def join_tables(tables, inherent, deadline, solution_limit, models, seen, stats):
    """Join fully materialized local relations, including entry allDifferent."""
    order = sorted(tables, key=lambda p: (len(tables[p]), p))

    def visit(i, mapping, used, choices):
        if time.monotonic() >= deadline:
            raise Stopped('UNKNOWN_BUDGET')
        stats['join_nodes'] += 1
        if i == len(order):
            model = {'inherent': inherent, 'assignments': sorted(choices),
                     'observed_component_codes': dict(sorted(mapping.items()))}
            key = canonical_model(model)
            if key not in seen:
                if len(models) >= solution_limit:
                    raise Stopped('UNKNOWN_OUTPUT_LIMIT')
                seen.add(key); models.append(model)
            return
        paragraph = order[i]
        for candidate in tables[paragraph]:
            if time.monotonic() >= deadline:
                raise Stopped('UNKNOWN_BUDGET')
            if candidate['source'] in used:
                continue
            combined = join_key(mapping, candidate['mapping'])
            if combined is not None:
                visit(i + 1, combined, used | {candidate['source']},
                      choices + [[paragraph, candidate['source']]])
    visit(0, {}, set(), [])


def panel_models(targets, entries, domain_rows, deadline, solution_limit):
    """Materialize every local kernel before doing any global key join."""
    sources = {e['id']: e for e in entries}
    target_by_id = {p['id']: p for p in targets}
    stats = {'local_calls': 0, 'local_maps': 0, 'join_nodes': 0}
    tables_by_vowel, models, seen = {}, [], set()
    try:
        for inherent in VOWELS:
            tables = {}
            for row in domain_rows:
                paragraph = row['paragraph']; options = []
                for ident in row['candidate_source_ids']:
                    if time.monotonic() >= deadline:
                        raise Stopped('UNKNOWN_BUDGET')
                    local = local_kernel.fixed_entry_solutions(sources[ident]['words'],
                        target_by_id[paragraph]['words'], inherent, deadline)
                    stats['local_calls'] += 1
                    if local['status'] != 'COMPLETE':
                        raise Stopped('UNKNOWN_LOCAL_KERNEL')
                    for mapping in local['solutions']:
                        options.append({'source': ident, 'mapping': mapping})
                    stats['local_maps'] += len(local['solutions'])
                tables[paragraph] = options
            tables_by_vowel[inherent] = tables
        for inherent in VOWELS:
            join_tables(tables_by_vowel[inherent], inherent, deadline, solution_limit,
                        models, seen, stats)
    except Stopped as exc:
        return {'status': str(exc), 'enumeration_complete': False, 'models': models, 'stats': stats}
    except (MemoryError, RecursionError) as exc:
        return {'status': 'UNKNOWN_' + type(exc).__name__.upper(),
                'enumeration_complete': False, 'models': models, 'stats': stats}
    return {'status': 'SAT_COMPLETE_OBSERVED_MODELS' if models else 'UNSAT_COMPLETE_CV_ENUMERATION',
            'enumeration_complete': True, 'models': models, 'stats': stats}


def valid_witness(model, targets, entries):
    sources = {e['id']: e for e in entries}; target = {t['id']: t for t in targets}
    inherent = model.get('inherent')
    if not isinstance(inherent, str) or len(inherent) != 1 or inherent not in VOWELS:
        return False
    assignments = model.get('assignments', [])
    if (len(assignments) != len(target) or any(not isinstance(p, list) or len(p) != 2 for p in assignments)
            or len({p[0] for p in assignments}) != len(target)
            or {p[0] for p in assignments} != set(target)
            or len({p[1] for p in assignments}) != len(assignments)
            or any(p[1] not in sources for p in assignments)):
        return False
    mapping = model.get('observed_component_codes', {})
    if not isinstance(mapping, dict) or not extendible(mapping):
        return False
    observed = set()
    for p, e in assignments:
        source_words, cipher_words = sources[e]['words'], target[p]['words']
        if len(source_words) != len(cipher_words):
            return False
        for word, cipher in zip(source_words, cipher_words):
            components = local_kernel.components(word, inherent)
            observed.update(components)
            if any(c not in mapping for c in components):
                return False
            if ''.join(mapping[c] for c in components) != cipher:
                return False
    return observed == set(mapping)


def replay(args):
    sha = domain_validator.digest
    if (sha(Path(local_kernel.__file__).read_bytes()) != EXPECTED_LOCAL_KERNEL_SHA256
            or sha(Path(domain_validator.__file__).read_bytes()) != EXPECTED_DOMAIN_VALIDATOR_SHA256):
        raise ValueError('FROZEN_INDEPENDENT_DEPENDENCY_HASH_MISMATCH')
    source_raw, lock_raw, audit_raw = [p.read_bytes() for p in
        (args.source_pool, args.source_lock, args.source_audit)]
    pool = domain_validator.source_gate(source_raw, lock_raw, audit_raw)
    packet_raw = args.target_packet.read_bytes()
    if sha(packet_raw) != domain_validator.PACKET_SHA256:
        raise ValueError('TARGET_PACKET_HASH_MISMATCH_REFUSING_PARSE')
    packet = json.loads(gzip.decompress(packet_raw))
    expected_domains = domain_validator.reconstruct(pool, packet)
    domain_raw = args.domains.read_bytes(); primary_domains = json.loads(domain_raw)
    expected_domains.update(source_pool_sha256=sha(source_raw), source_lock_sha256=sha(lock_raw),
        source_audit_sha256=sha(audit_raw), target_packet_sha256=sha(packet_raw),
        implementation_sha256=sha(Path(__file__).with_name('check_entry_domains.py').read_bytes()))
    if domain_validator.differing_paths(expected_domains, primary_domains):
        raise ValueError('INDEPENDENT_COMPLETE_DOMAIN_REPLAY_DISAGREES')
    primary_raw = args.result.read_bytes(); primary = json.loads(primary_raw)
    issues = []
    if primary.get('schema') != 'GDT895_COMPLETE_CV_PANEL_RESULT_V1':
        issues.append('PRIMARY_SCHEMA')
    if set(primary.get('panels', {})) != set(domain_validator.PANEL_COUNTS):
        raise ValueError('PRIMARY_PANEL_SCOPE_CHANGED')
    for field, raw in (('source_pool_sha256', source_raw), ('source_lock_sha256', lock_raw),
                       ('source_audit_sha256', audit_raw), ('target_packet_sha256', packet_raw),
                       ('domain_certificate_sha256', domain_raw)):
        if primary.get(field) != sha(raw): issues.append('INPUT_HASH:' + field)
    for name in ('fit_cv.py', 'cv_equations.py', 'check_entry_domains.py'):
        if primary.get('source_hashes', {}).get(name) != sha(Path(__file__).with_name(name).read_bytes()):
            issues.append('PRIMARY_IMPLEMENTATION_HASH:' + name)
    if primary.get('held_access') is not False: issues.append('HELD_ACCESS_FLAG')
    if primary.get('all_panels_complete') != all(p['enumeration_complete'] for p in primary['panels'].values()):
        issues.append('PRIMARY_COMPLETENESS_AGGREGATE')
    start = time.monotonic(); deadline = start + args.budget_seconds; panels = {}
    sources = {e['id']: e for e in pool['entries']}
    for edition in domain_validator.PANEL_COUNTS:
        domain = expected_domains['panels'][edition]; claim = primary['panels'][edition]
        if domain['empty_domains']:
            expected = {'status': 'UNSAT_EMPTY_COMPLETE_ENTRY_DOMAIN', 'enumeration_complete': True,
                        'key_search_performed': False, 'empty_domain_count': domain['empty_domains']}
            mismatch = domain_validator.differing_paths(expected, claim)
            if mismatch: issues.append('EMPTY_DOMAIN_PANEL:' + edition)
            panels[edition] = {'status': 'PASS_COMPLETE' if not mismatch else 'FAIL',
                'enumeration_complete': True, 'empty_domain_count': domain['empty_domains'],
                'key_search_performed': False}
            continue
        targets = packet['panels'][edition]
        claimed_models = claim.get('models', [])
        expected_status = 'SAT_COMPLETE_OBSERVED_MODELS' if claimed_models else 'UNSAT_COMPLETE_CV_ENUMERATION'
        if ((claim['enumeration_complete'] and claim['status'] != expected_status)
                or (not claim['enumeration_complete'] and not claim['status'].startswith('UNKNOWN_'))):
            issues.append('PRIMARY_STATUS_CONTRADICTION:' + edition)
        if any(not valid_witness(m, targets, pool['entries']) for m in claimed_models):
            issues.append('INVALID_PRIMARY_WITNESS:' + edition)
        claimed_set = {canonical_model(m) for m in claimed_models}
        if len(claimed_set) != len(claimed_models): issues.append('DUPLICATE_PRIMARY_MODELS:' + edition)
        assignments = {tuple(sorted(tuple(p) for p in m['assignments'])) for m in claimed_models}
        plaintexts = {tuple(sorted((p, tuple(sources[e]['words'])) for p, e in m['assignments'])) for m in claimed_models}
        if (claim.get('model_count') != len(claimed_models)
                or claim.get('distinct_entry_assignments') != len(assignments)
                or claim.get('distinct_plaintext_projections') != len(plaintexts)):
            issues.append('PRIMARY_PROJECTION_COUNTS:' + edition)
        if claim.get('unused_component_values_identified') is not False or claim.get('key_search_performed') is not True:
            issues.append('PRIMARY_SCOPE_FLAGS:' + edition)
        independent = panel_models(targets, pool['entries'], domain['records'], deadline, args.solution_limit)
        independent_set = {canonical_model(m) for m in independent['models']}
        complete = independent['enumeration_complete'] and claim['enumeration_complete']
        same = independent_set == claimed_set if complete else None
        if complete and (not same or independent['status'] != claim['status']):
            issues.append('COMPLETE_MODEL_FAMILY_DISAGREEMENT:' + edition)
        panels[edition] = {'status': 'PASS_COMPLETE' if complete and same else 'FAIL' if complete else 'UNKNOWN',
            'enumeration_complete': complete, 'independent_status': independent['status'],
            'primary_status': claim['status'], 'independent_model_count': len(independent_set),
            'primary_model_count': len(claimed_set), 'complete_model_families_equal': same,
            'primary_witnesses_checked': len(claimed_models), 'stats': independent['stats'],
            'independent_models': independent['models']}
    return {'schema': 'GDT895_INDEPENDENT_GLOBAL_CV_VALIDATION_V1',
            'status': 'FAIL' if issues else 'PASS' if all(p['enumeration_complete'] for p in panels.values()) else 'UNKNOWN',
            'panels': panels, 'issues': issues,
            'source_pool_sha256': sha(source_raw), 'source_lock_sha256': sha(lock_raw),
            'source_audit_sha256': sha(audit_raw), 'target_packet_sha256': sha(packet_raw),
            'domain_certificate_sha256': sha(domain_raw), 'primary_result_sha256': sha(primary_raw),
            'validator_sha256': sha(Path(__file__).read_bytes()),
            'local_kernel_sha256': sha(Path(local_kernel.__file__).read_bytes()),
            'domain_validator_sha256': sha(Path(domain_validator.__file__).read_bytes()),
            'budget_seconds': args.budget_seconds, 'solution_limit': args.solution_limit,
            'elapsed_seconds': time.monotonic() - start,
            'claim_ceiling': 'Full agreement requires complete local kernels, complete joins and equality of every observed model; no unused-key identification or meaning.'}


def self_test():
    def joined(tables):
        models, seen = [], set()
        join_tables(tables, 'a', time.monotonic() + 5, 100, models, seen, {'join_nodes': 0})
        return models
    def option(source, **mapping): return {'source': source, 'mapping': mapping}
    assert not joined({'p': [option('s1', c='x')], 'q': [option('s2', c='y')]})
    assert not joined({'p': [option('s1', c='x')], 'q': [option('s1', c='x')]})
    assert not joined({'p': [option('s1', c='x')], 'q': [option('s2', d='xy')]})
    assert not joined({'p': [option('s1', c='x')], 'q': [option('s2', d='x')]})
    assert len(joined({'p': [option('s1', c='x'), option('s2', c='x')],
                       'q': [option('s2', d='yz'), option('s1', d='yz')]})) == 2
    assert not extendible({str(i): c for i, c in enumerate(ALPHABET)})
    assert extendible({str(i): c for i, c in enumerate(ALPHABET[:-1])})
    entries = [{'id': 's1', 'words': ['ba']}, {'id': 's2', 'words': ['ba']}]
    targets = [{'id': 'p', 'words': ['x']}, {'id': 'q', 'words': ['x']}]
    domains = [{'paragraph': p['id'], 'candidate_source_ids': ['s1', 's2']} for p in targets]
    result = panel_models(targets, entries, domains, time.monotonic() + 5, 100)
    assert result['enumeration_complete'] and len(result['models']) == 2, result
    assert all(valid_witness(m, targets, entries) for m in result['models'])
    assert {m['inherent'] for m in result['models']} == {'a'}
    assert panel_models(targets, entries, domains, 0, 100)['enumeration_complete'] is False
    capped = panel_models(targets, entries, domains, time.monotonic() + 5, 1)
    assert capped['status'] == 'UNKNOWN_OUTPUT_LIMIT' and not capped['enumeration_complete']
    targets[1]['words'] = ['y']
    bad = panel_models(targets, entries, domains, time.monotonic() + 5, 100)
    assert bad['enumeration_complete'] and not bad['models']
    return {'status': 'PASS', 'synthetic_join_cases': 7, 'synthetic_full_panel_cases': 4,
            'real_target_opened': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source-pool', 'source-lock', 'source-audit', 'target-packet', 'domains', 'result', 'output'):
        p.add_argument('--' + name, type=Path)
    p.add_argument('--budget-seconds', type=float)
    p.add_argument('--solution-limit', type=int)
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True)); return 0
    if (any(getattr(args, n.replace('-', '_')) is None for n in
            ('source-pool', 'source-lock', 'source-audit', 'target-packet', 'domains', 'result', 'output'))
            or args.budget_seconds is None or args.budget_seconds <= 0
            or args.solution_limit is None or args.solution_limit <= 0):
        p.error('all paths and positive budget/solution limits required')
    result = replay(args)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': result['status'], 'issues': result['issues'],
        'panels': {e: {k: v for k, v in row.items() if k != 'independent_models'}
                   for e, row in result['panels'].items()}}))
    return 1 if result['status'] == 'FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())
