#!/usr/bin/env python3
"""Independent Alberti replay: complete local relative keys, then offset joins."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re
import time
import independent_runs as reference

LETTERS = 'abcdefgilmnopqrstuxz'
OUTER = LETTERS + '1234'
LETTER_INDEX = {c: i for i, c in enumerate(LETTERS)}
PACKET_SHA256 = '1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed'
CAPTURE_SHA256 = '033800bc117abe9031364800c703d4b061299d47a642b53398bd478429f9d322'
SOURCE_VALIDATOR_SHA256 = 'd13a09a6cae513f526d137d3f50a1d8bddfe049ec56b731869e566cae7e6ace2'
REFERENCE_SHA256 = 'e11aca901982ac63dbff44c90a7ca176f3ccf99d702e8b1f0e57290dbe759c79'
SOURCE_POOL_SHA256 = '440476367567addf11406cbc62d8d22f3c1fa42be1701190866903a101dfa28d'
SOURCE_LOCK_SHA256 = 'ec35b637bd891edc833648f61b57ef182802b6148b9979c1856d56a6f1fcc169'
SOURCE_AUDIT_SHA256 = 'aaa365203d5ce33f679496388ad3e37e5446a7b70c610eff6dfcde34cedb9250'
PANEL_COUNTS = {'ZL3b': 14, 'IT2a': 259, 'RF1b': 11, 'CONSENSUS': 1}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Interrupted(Exception):
    pass


def check_time(deadline):
    if time.monotonic() >= deadline:
        raise Interrupted('BUDGET')


def decode(cipher, positions, index):
    """Direct state machine, independent of source matching and key search."""
    if not cipher or type(index) is not int or not 0 <= index < 20:
        raise ValueError('INVALID_MESSAGE_OR_INDEX')
    values = list(positions.values())
    if (any(type(v) is not int or not 0 <= v < 24 for v in values)
            or len(set(values)) != len(values) or any(c not in positions for c in cipher)):
        raise ValueError('INVALID_POSITION_INJECTION')
    anchor = positions[cipher[0]]
    output = []
    for glyph in cipher[1:]:
        offset = (positions[glyph] - anchor + index) % 24
        if offset < 20:
            output.append(OUTER[offset])
        else:
            anchor = positions[glyph]
    return ''.join(output)


def local_models(cipher, plain, index, deadline):
    """All relative keys, first indicator at zero; recursion only on new glyphs."""
    if not cipher or type(index) is not int or not 0 <= index < 20 or any(c not in LETTERS for c in plain):
        raise ValueError('INVALID_LOCAL_INPUT')
    maps, positions = [], {cipher[0]: 0}
    stats = {'branches': 0, 'deterministic_steps': 0}

    def visit(offset, cursor, anchor, occupied):
        while offset < len(cipher):
            check_time(deadline)
            glyph = cipher[offset]
            if glyph not in positions:
                candidates = ([LETTER_INDEX[plain[cursor]]] if cursor < len(plain) else []) + [20, 21, 22, 23]
                for decoded in candidates:
                    position = (positions[anchor] + decoded - index) % 24
                    if position in occupied:
                        continue
                    stats['branches'] += 1
                    positions[glyph] = position
                    visit(offset, cursor, anchor, occupied | {position})
                    del positions[glyph]
                return
            decoded = (positions[glyph] - positions[anchor] + index) % 24
            stats['deterministic_steps'] += 1
            if decoded >= 20:
                anchor = glyph
            else:
                if cursor >= len(plain) or LETTERS[decoded] != plain[cursor]:
                    return
                cursor += 1
            offset += 1
        if cursor == len(plain):
            maps.append(dict(sorted(positions.items())))

    try:
        check_time(deadline)
        if len(set(cipher)) <= 24:
            visit(1, 0, cipher[0], {0})
    except Interrupted:
        return {'status': 'UNKNOWN_BUDGET', 'maps': maps, 'stats': stats}
    except MemoryError:
        return {'status': 'UNKNOWN_MEMORY', 'maps': maps, 'stats': stats}
    return {'status': 'COMPLETE', 'maps': maps, 'stats': stats}


def aligned_extensions(global_positions, relative):
    overlap = set(global_positions) & set(relative)
    if overlap:
        shifts = {(global_positions[g] - relative[g]) % 24 for g in overlap}
        if len(shifts) != 1:
            return
    else:
        shifts = range(24)
    for shift in shifts:
        merged = dict(global_positions)
        occupied = {v: k for k, v in merged.items()}
        valid = True
        for glyph, relative_position in relative.items():
            position = (relative_position + shift) % 24
            if ((glyph in merged and merged[glyph] != position)
                    or (position in occupied and occupied[position] != glyph)):
                valid = False
                break
            merged[glyph] = position
            occupied[position] = glyph
        if valid:
            yield merged


def model_key(model):
    return (model['index'], tuple(sorted(tuple(p) for p in model['assignments'])),
            tuple(sorted(model['positions'].items())))


def join_relatives(tables, index, gauge, deadline, limit, models, seen, stats):
    order = sorted(tables, key=lambda p: (len(tables[p]), p))

    def visit(i, positions, entries_used, assignments):
        check_time(deadline)
        stats['join_nodes'] += 1
        if i == len(order):
            model = {'index': index, 'assignments': sorted(assignments), 'positions': dict(sorted(positions.items()))}
            key = model_key(model)
            if key not in seen:
                if len(models) >= limit:
                    raise Interrupted('OUTPUT_LIMIT')
                models.append(model)
                seen.add(key)
                if len(models) >= limit:
                    raise Interrupted('OUTPUT_LIMIT')
            return
        paragraph = order[i]
        for candidate in tables[paragraph]:
            check_time(deadline)
            ident = candidate['entry']
            if ident in entries_used:
                continue
            for merged in aligned_extensions(positions, candidate['relative']):
                visit(i + 1, merged, entries_used | {ident}, assignments + [[paragraph, ident]])
    visit(0, {gauge: 0}, set(), [])


def panel_models(targets, entries, deadline, limit=100):
    if len({p['id'] for p in targets}) != len(targets) or len({e['id'] for e in entries}) != len(entries):
        raise ValueError('DUPLICATE_IDS')
    if any(not p['cipher'] for p in targets):
        raise ValueError('EMPTY_TARGET_MESSAGE')
    glyphs = sorted({c for p in targets for c in p['cipher']})
    if not glyphs:
        raise ValueError('EMPTY_PANEL')
    stats = {'run_calls': 0, 'local_calls': 0, 'relative_maps': 0, 'join_nodes': 0}
    models, seen, certificates, completed_indices = [], set(), [], []
    if len(glyphs) > 24:
        return {'status': 'COMPLETE_UNSAT', 'enumeration_complete': True, 'models': [],
                'completed_indices': list(range(20)),
                'certificates': [{'reason': 'ALPHABET_CAPACITY', 'glyphs': len(glyphs)}], 'stats': stats}
    try:
        for index in range(20):
            check_time(deadline)
            domains = {}
            for target in targets:
                options = []
                for entry in entries:
                    check_time(deadline)
                    stats['run_calls'] += 1
                    if reference.run_accepts(target['cipher'], entry['plain'], index):
                        options.append(entry)
                domains[target['id']] = options
                if not options:
                    certificates.append({'index': index, 'reason': 'EMPTY_RUN_DOMAIN', 'paragraph': target['id']})
                    break
            if any(not options for options in domains.values()):
                completed_indices.append(index)
                continue
            target_lookup = {t['id']: t for t in targets}
            tables = {}
            failed = None
            for paragraph in sorted(domains, key=lambda p: (len(domains[p]), p)):
                options, cache = [], {}
                for entry in domains[paragraph]:
                    check_time(deadline)
                    plain = entry['plain']
                    if plain not in cache:
                        local = local_models(target_lookup[paragraph]['cipher'], plain, index, deadline)
                        stats['local_calls'] += 1
                        if local['status'] != 'COMPLETE':
                            raise Interrupted(local['status'])
                        cache[plain] = local['maps']
                    for positions in cache[plain]:
                        options.append({'entry': entry['id'], 'relative': positions})
                    stats['relative_maps'] += len(cache[plain])
                tables[paragraph] = options
                if not options:
                    failed = paragraph
                    certificates.append({'index': index, 'reason': 'EMPTY_LOCAL_DOMAIN', 'paragraph': paragraph,
                                         'complete_entry_ids': [e['id'] for e in domains[paragraph]]})
                    break
            if failed is None:
                before = len(models)
                join_relatives(tables, index, glyphs[0], deadline, limit, models, seen, stats)
                certificates.append({'index': index, 'reason': 'COMPLETE_OFFSET_JOIN', 'new_models': len(models) - before})
            completed_indices.append(index)
    except (Interrupted, MemoryError, RecursionError) as exc:
        return {'status': 'UNKNOWN_WITH_WITNESS' if models else 'UNKNOWN_NO_WITNESS',
                'enumeration_complete': False, 'models': models, 'interruption': str(exc) or type(exc).__name__,
                'completed_indices': completed_indices, 'certificates': certificates, 'stats': stats}
    return {'status': 'COMPLETE_SAT' if models else 'COMPLETE_UNSAT', 'enumeration_complete': True,
            'models': models, 'completed_indices': completed_indices, 'certificates': certificates, 'stats': stats}


def witness_valid(model, targets, entries):
    try:
        source = {e['id']: e['plain'] for e in entries}
        target = {p['id']: p['cipher'] for p in targets}
        assignments = model['assignments']
        positions = model['positions']
        glyphs = {c for cipher in target.values() for c in cipher}
        if (len(assignments) != len(target) or len({p for p, e in assignments}) != len(target)
                or {p for p, e in assignments} != set(target)
                or len({e for p, e in assignments}) != len(assignments)
                or set(positions) != glyphs or positions[min(glyphs)] != 0):
            return False
        return all(decode(target[p], positions, model['index']) == source[e] for p, e in assignments)
    except (ValueError, KeyError, TypeError):
        return False


def source_gate(source_raw, lock_raw, audit_raw):
    if tuple(map(sha, (source_raw, lock_raw, audit_raw))) != (SOURCE_POOL_SHA256, SOURCE_LOCK_SHA256, SOURCE_AUDIT_SHA256):
        raise ValueError('EXACT_SOURCE_BYTES_CHANGED_BEFORE_PARSE')
    pool, lock, audit = map(json.loads, (source_raw, lock_raw, audit_raw))
    if (lock.get('status') != 'FROZEN' or lock.get('source_pool_sha256') != sha(source_raw)
            or lock.get('source_audit_sha256') != sha(audit_raw) or audit.get('status') != 'PASS'
            or audit.get('source_pool_sha256') != sha(source_raw)
            or audit.get('capture_sha256') != CAPTURE_SHA256 or pool.get('capture_sha256') != CAPTURE_SHA256
            or audit.get('validator_sha256') != SOURCE_VALIDATOR_SHA256 or pool.get('pending') != []
            or len(pool.get('entries', [])) != 1016):
        raise ValueError('SOURCE_NOT_FROZEN_OR_BOUND')
    return pool


def read_inputs(args):
    if sha(Path(reference.__file__).read_bytes()) != REFERENCE_SHA256:
        raise ValueError('INDEPENDENT_REFERENCE_HASH_CHANGED')
    source_raw, lock_raw, audit_raw = [p.read_bytes() for p in (args.source_pool, args.source_lock, args.source_audit)]
    pool = source_gate(source_raw, lock_raw, audit_raw)
    projection = reference.source_projection(pool['entries'])
    packet_raw = args.target_packet.read_bytes()
    if sha(packet_raw) != PACKET_SHA256:
        raise ValueError('TARGET_PACKET_HASH_MISMATCH_REFUSING_PARSE')
    packet = json.loads(gzip.decompress(packet_raw))
    if packet.get('schema') != 'GDT893_ODD_ONLY_FIT_PACKET_V1' or set(packet.get('panels', {})) != set(PANEL_COUNTS):
        raise ValueError('TARGET_PACKET_SCHEMA_CHANGED')
    targets = {}
    for edition, paragraphs in packet['panels'].items():
        if len(paragraphs) != PANEL_COUNTS[edition] or len({p['id'] for p in paragraphs}) != len(paragraphs):
            raise ValueError('MANDATORY_PARAGRAPH_SCOPE_CHANGED')
        targets[edition] = []
        for p in paragraphs:
            folio = p['physical_folio']
            words = p['words']
            if (not re.fullmatch(r'f[0-9]+', folio) or int(folio[1:]) % 2 != 1
                    or p['page'].startswith(('f84', 'f116')) or not words
                    or len(words) != len(p['source_group_ids'])
                    or any(not re.fullmatch(r'[a-z]+', w) for w in words)):
                raise ValueError('INVALID_COMPLETE_TARGET_MESSAGE')
            targets[edition].append({'id': p['id'], 'cipher': ''.join(words)})
    bindings = {'source_pool_sha256': sha(source_raw), 'source_lock_sha256': sha(lock_raw),
                'source_audit_sha256': sha(audit_raw), 'target_packet_sha256': sha(packet_raw)}
    return projection, targets, bindings


def timed_panel(payload):
    targets, entries, budget, limit = payload
    started = time.monotonic()
    result = panel_models(targets, entries, started + budget, limit)
    result['elapsed_seconds'] = time.monotonic() - started
    return result


def replay(args):
    projection, targets, bindings = read_inputs(args)
    result_raw = args.result.read_bytes()
    primary = json.loads(result_raw)
    issues = []
    if primary.get('schema') != 'GDT896_COMPLETE_ENTRY_ROTOR_V1':
        issues.append('PRIMARY_SCHEMA')
    if set(primary.get('panels', {})) != set(PANEL_COUNTS):
        raise ValueError('PRIMARY_PANEL_SCOPE_CHANGED')
    for field, value in bindings.items():
        if primary.get(field) != value:
            issues.append('INPUT_BINDING:' + field)
    if primary.get('implementation_sha256') != sha(Path(__file__).with_name('run.py').read_bytes()):
        issues.append('PRIMARY_IMPLEMENTATION_HASH')
    if primary.get('held_access') is not False:
        issues.append('HELD_ACCESS_FLAG')
    reported_projection = primary.get('source_projection', {})
    expected_profiles = [{'id': e['id'], 'length': len(e['plain']), 'plain_sha256': sha(e['plain'].encode('ascii'))}
                         for e in projection['entries']]
    if (reported_projection.get('entries') != expected_profiles
            or reported_projection.get('accepted') != len(projection['entries'])
            or reported_projection.get('excluded') != len(projection['exclusions'])
            or {e['id'] for e in reported_projection.get('exclusions', [])} != {e['id'] for e in projection['exclusions']}
            or reported_projection.get('source_pool_sha256') != SOURCE_POOL_SHA256):
        issues.append('SOURCE_PROJECTION_DISAGREEMENT')
    payloads = [(targets[e], projection['entries'], args.budget_seconds, args.solution_limit) for e in PANEL_COUNTS]
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=min(4, args.workers)) as executor:
            independent = list(executor.map(timed_panel, payloads))
    else:
        independent = [timed_panel(p) for p in payloads]
    panels = {}
    for edition, actual in zip(PANEL_COUNTS, independent):
        claimed = primary['panels'][edition]
        primary_models = claimed.get('models', [])
        if any(not witness_valid(m, targets[edition], projection['entries']) for m in primary_models):
            issues.append('INVALID_PRIMARY_WITNESS:' + edition)
        if any(not witness_valid(m, targets[edition], projection['entries']) for m in actual['models']):
            issues.append('INVALID_INDEPENDENT_WITNESS:' + edition)
        primary_set = {model_key(m) for m in primary_models}
        actual_set = {model_key(m) for m in actual['models']}
        if len(primary_set) != len(primary_models):
            issues.append('DUPLICATE_PRIMARY_MODELS:' + edition)
        expected_status = ('COMPLETE_SAT' if primary_models else 'COMPLETE_UNSAT') if claimed['enumeration_complete'] else (
            'UNKNOWN_WITH_WITNESS' if primary_models else 'UNKNOWN_NO_WITNESS')
        if claimed['status'] != expected_status:
            issues.append('PRIMARY_STATUS_CONTRADICTION:' + edition)
        complete = actual['enumeration_complete'] and claimed['enumeration_complete']
        equal = primary_set == actual_set if complete else None
        if complete and (not equal or actual['status'] != claimed['status']):
            issues.append('COMPLETE_MODEL_FAMILY_DISAGREEMENT:' + edition)
        panels[edition] = {'status': 'PASS_COMPLETE' if complete and equal else 'FAIL' if complete else 'UNKNOWN',
            'enumeration_complete': complete, 'primary_status': claimed['status'],
            'independent_status': actual['status'], 'primary_model_count': len(primary_set),
            'independent_model_count': len(actual_set), 'complete_model_families_equal': equal,
            'independent': actual}
    return {'schema': 'GDT896_INDEPENDENT_COMPLETE_ROTOR_VALIDATION_V1',
            'status': 'FAIL' if issues else 'PASS' if all(p['enumeration_complete'] for p in panels.values()) else 'UNKNOWN',
            **bindings, 'primary_result_sha256': sha(result_raw), 'validator_sha256': sha(Path(__file__).read_bytes()),
            'independent_reference_sha256': REFERENCE_SHA256,
            'projected_source_entries': len(projection['entries']), 'source_exclusions': projection['exclusions'],
            'source_projection_sha256': sha(json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()),
            'panels': panels, 'issues': issues, 'budget_seconds_per_panel': args.budget_seconds,
            'solution_limit': args.solution_limit,
            'claim_ceiling': 'Exact partial-source mechanical supersystem only; no missing-source rejection or semantic claim.'}


def self_test():
    assert len(LETTERS) == 20 and len(OUTER) == 24 and len(set(OUTER)) == 24
    cases = 0
    for cipher in ('a', 'aa', 'ab', 'aba', 'abb', 'abca', 'abcb'):
        glyphs = sorted(set(cipher))
        first = cipher[0]
        others = [g for g in glyphs if g != first]
        for index in range(20):
            by_plain = {}
            for chosen in itertools.permutations(range(1, 24), len(others)):
                key = {first: 0, **dict(zip(others, chosen))}
                plain = decode(cipher, key, index)
                by_plain.setdefault(plain, set()).add(tuple(sorted(key.items())))
            for plain, expected in by_plain.items():
                result = local_models(cipher, plain, index, time.monotonic() + 5)
                assert result['status'] == 'COMPLETE'
                assert {tuple(sorted(m.items())) for m in result['maps']} == expected, (cipher, plain, index)
                cases += 1
    assert local_models('ab', 'a', 0, 0)['status'] == 'UNKNOWN_BUDGET'
    for cipher, plain in (('a', 'a'), ('aaa', 'a'), ('ab', 'ab')):
        assert not local_models(cipher, plain, 0, time.monotonic() + 5)['maps']
    assert len(list(aligned_extensions({'a': 0}, {'b': 0}))) == 23
    assert not list(aligned_extensions({'a': 0, 'b': 1}, {'a': 0, 'b': 2}))
    assert not list(aligned_extensions({'a': 0, 'b': 1}, {'a': 0, 'c': 1}))
    tables = {'p': [{'entry': 's1', 'relative': {'a': 0, 'b': 1}}],
              'q': [{'entry': 's2', 'relative': {'b': 0, 'a': 23}}]}
    models, seen = [], set()
    join_relatives(tables, 0, 'a', time.monotonic() + 5, 100, models, seen, {'join_nodes': 0})
    assert len(models) == 1 and models[0]['positions'] == {'a': 0, 'b': 1}
    tables['q'][0]['entry'] = 's1'
    models = []
    join_relatives(tables, 0, 'a', time.monotonic() + 5, 100, models, set(), {'join_nodes': 0})
    assert not models
    entries = [{'id': 's1', 'plain': 'a'}, {'id': 's2', 'plain': 'a'}]
    targets = [{'id': 'p', 'cipher': 'aa'}, {'id': 'q', 'cipher': 'aa'}]
    result = panel_models(targets, entries, time.monotonic() + 10, 100)
    assert result['status'] == 'COMPLETE_SAT' and len(result['models']) == 2
    assert all(witness_valid(m, targets, entries) for m in result['models'])
    reused = panel_models(targets, entries[:1], time.monotonic() + 10, 100)
    assert reused['status'] == 'COMPLETE_UNSAT'
    cap = panel_models(targets, entries, time.monotonic() + 10, 1)
    assert not cap['enumeration_complete'] and len(cap['models']) == 1
    exact_cap = panel_models(targets, entries, time.monotonic() + 10, 2)
    assert not exact_cap['enumeration_complete'] and len(exact_cap['models']) == 2
    targets[1]['cipher'] = 'bb'
    disconnected = panel_models(targets, entries, time.monotonic() + 10, 100)
    assert disconnected['enumeration_complete'] and len(disconnected['models']) == 46
    assert all(witness_valid(m, targets, entries) for m in disconnected['models'])
    class InventedBytes:
        def read_bytes(self): return b'not valid JSON or the frozen source'
    class ForbiddenTarget:
        def read_bytes(self): raise AssertionError('target was read before exact source byte gate')
    class Inputs:
        source_pool = source_lock = source_audit = InventedBytes()
        target_packet = ForbiddenTarget()
    try:
        read_inputs(Inputs())
    except ValueError as exc:
        assert str(exc) == 'EXACT_SOURCE_BYTES_CHANGED_BEFORE_PARSE'
    else:
        raise AssertionError('unbound source accepted')
    return {'status': 'PASS', 'exhaustive_local_output_cases': cases,
            'global_offset_and_assignment_cases': 10, 'source_before_target_barrier_cases': 1,
            'real_target_opened': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source-pool', 'source-lock', 'source-audit', 'target-packet', 'result', 'output'):
        p.add_argument('--' + name, type=Path)
    p.add_argument('--budget-seconds', type=float, default=300)
    p.add_argument('--solution-limit', type=int, default=100)
    p.add_argument('--workers', type=int, default=1)
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return 0
    if (any(getattr(args, n.replace('-', '_')) is None for n in
            ('source-pool', 'source-lock', 'source-audit', 'target-packet', 'result', 'output'))
            or not 0 < args.budget_seconds <= 300 or not 0 < args.solution_limit <= 100 or not 1 <= args.workers <= 4):
        p.error('all paths required; budget 0..300 seconds, positive limit, workers 1..4')
    result = replay(args)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': result['status'], 'issues': result['issues'],
        'panels': {e: {k: v for k, v in row.items() if k != 'independent'} for e, row in result['panels'].items()}}))
    return 1 if result['status'] == 'FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())
