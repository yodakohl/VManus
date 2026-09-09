#!/usr/bin/env python3
"""Complete global ring/entry DFS; source prose never written to public output."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import gzip
import hashlib
from itertools import groupby
import json
from pathlib import Path
import re
import time

LETTERS = 'abcdefgilmnopqrstuxz'
OUTER = LETTERS + '1234'
SPEC = json.loads(Path(__file__).with_name('SPEC.json').read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def project(entries):
    accepted, exclusions, seen = [], [], set()
    for entry in entries:
        if entry['id'] in seen:
            raise ValueError('duplicate source ID')
        seen.add(entry['id'])
        if (entry.get('status', 'ACCEPTED') != 'ACCEPTED' or not entry['words']
                or any(not re.fullmatch('[a-z]+', w) for w in entry['words'])):
            raise ValueError('invalid original accepted source')
        plain = ''.join(entry['words']).translate(str.maketrans('jv', 'iu'))
        bad = sorted(set(plain) - set(LETTERS))
        if bad:
            exclusions.append({'id': entry['id'], 'reason': 'outer_alphabet_violation',
                               'characters': bad})
        else:
            accepted.append({'id': entry['id'], 'plain': plain})
    return {'entries': accepted, 'exclusions': exclusions}


def run_lengths(cipher):
    return [len(list(g)) for _, g in groupby(cipher)]


class PlainMasks:
    def __init__(self, plain):
        self.plain = plain
        self.blocks = []
        start = 0
        for letter, group in groupby(plain):
            size = len(list(group))
            self.blocks.append((start, size, letter))
            start += size
        self.cache = {}
        self.full = (1 << (len(plain) + 1)) - 1

    def mask(self, width, letter=None):
        if width == 0:
            return self.full
        key = width, letter
        if key not in self.cache:
            result = 0
            for start, size, char in self.blocks:
                if size >= width and (letter is None or char == letter):
                    result |= ((1 << (size - width + 1)) - 1) << start
            self.cache[key] = result
        return self.cache[key]


def runs_accept(runs, source, j):
    """Bitset membership in necessary independent-run language."""
    if not runs:
        return False
    plain, size = source.plain, len(source.plain)
    n = sum(runs)
    if not n - len(runs) <= size <= n - 1:
        return False
    first = runs[0] - 1
    letter = LETTERS[j]
    if plain[:first] != letter * first:
        return False
    bits = 1 << first
    minimum = sum(r - 1 for r in runs[1:])
    maximum = sum(runs[1:])
    for width in runs[1:]:
        minimum -= width - 1
        maximum -= width
        bits = (((bits & source.mask(width)) << width)
                | ((bits & source.mask(width - 1, letter)) << (width - 1)))
        lo, hi = max(0, size - maximum), size - minimum
        if hi < lo:
            return False
        bits &= ((1 << (hi + 1)) - 1) ^ ((1 << lo) - 1)
        if not bits:
            return False
    return bool(bits & (1 << size))


class BudgetStop(Exception):
    pass


def alive(deadline):
    if time.monotonic() >= deadline:
        raise BudgetStop('time budget')


def local_extensions(cipher, plain, j, initial, deadline, stats):
    """All global-key extensions for one whole message, no local regauging."""
    if not cipher or len(set(cipher) | set(initial)) > 24:
        return
    if any(c not in LETTERS for c in plain):
        raise ValueError('invalid projected source')
    if (len(set(initial.values())) != len(initial)
            or any(type(p) is not int or not 0 <= p < 24 for p in initial.values())):
        raise ValueError('invalid initial ring')
    plain_positions = [LETTERS.index(c) for c in plain]
    n, m = len(cipher), len(plain)

    def walk(i, t, anchor, key):
        stats['local_nodes'] += 1
        alive(deadline)
        if n - i < m - t:
            return
        # Consume all already-assigned glyphs without recursive depth growth.
        while i < n and cipher[i] in key:
            value = (key[cipher[i]] - key[anchor] + j) % 24
            if value < 20:
                if t == m or plain_positions[t] != value:
                    return
                t += 1
            else:
                anchor = cipher[i]
            i += 1
            if n - i < m - t:
                return
            alive(deadline)
        if i == n:
            if t == m:
                yield key
            return
        c = cipher[i]
        output_values = list(range(20, 24))
        if t < m:
            output_values.insert(0, plain_positions[t])
        for value in output_values:
            p = (key[anchor] + value - j) % 24
            if p in key.values():
                continue
            extension = dict(key)
            extension[c] = p
            if value < 20:
                yield from walk(i + 1, t + 1, anchor, extension)
            else:
                yield from walk(i + 1, t, c, extension)

    first = cipher[0]
    if first in initial:
        yield from walk(1, 0, first, dict(initial))
    else:
        for p in range(24):
            if p not in initial.values():
                key = dict(initial)
                key[first] = p
                yield from walk(1, 0, first, key)


def perfect_matching(domains):
    """Necessary AllDifferent capacity, ordinary augmenting paths."""
    owners = {}
    def augment(target, visited):
        for entry in domains[target]:
            if entry in visited:
                continue
            visited.add(entry)
            if entry not in owners or augment(owners[entry], visited):
                owners[entry] = target
                return True
        return False
    return all(augment(t, set()) for t in sorted(domains, key=lambda t: len(domains[t])))


def panel_models(targets, entries, seconds=300, limit=100):
    started = time.monotonic()
    deadline = started + seconds
    models, index_records = [], []
    stats = Counter(local_nodes=0, join_nodes=0, run_pairs=0)
    glyphs = set(''.join(t['cipher'] for t in targets))
    if not targets or any(not t['cipher'] for t in targets):
        raise ValueError('complete nonempty messages required')
    if len(glyphs) > 24:
        return {'status': 'COMPLETE_UNSAT', 'enumeration_complete': True,
                'models': [], 'reason': 'GLOBAL_SYMBOL_CAPACITY', 'glyph_count': len(glyphs)}
    if len(entries) < len(targets):
        return {'status': 'COMPLETE_UNSAT', 'enumeration_complete': True,
                'models': [], 'reason': 'GLOBAL_ENTRY_CAPACITY', 'source_count': len(entries)}
    sources = {e['id']: PlainMasks(e['plain']) for e in entries}
    target_by_id = {t['id']: t for t in targets}
    if len(target_by_id) != len(targets) or len(sources) != len(entries):
        raise ValueError('duplicate message/source ID')
    runs = {t['id']: run_lengths(t['cipher']) for t in targets}
    length_domains = {t['id']: [e['id'] for e in entries
        if len(t['cipher']) - len(runs[t['id']]) <= len(e['plain']) <= len(t['cipher']) - 1]
        for t in targets}
    order = sorted(target_by_id, key=lambda p: (len(length_domains[p]), p))
    complete, stopping = True, None
    try:
        for j in range(20):
            alive(deadline)
            domains, records = {}, []
            rec = {'index': j, 'index_letter': LETTERS[j], 'domains': records}
            index_records.append(rec)
            for tid in order:
                domain = []
                for sid in length_domains[tid]:
                    alive(deadline)
                    stats['run_pairs'] += 1
                    if runs_accept(runs[tid], sources[sid], j):
                        domain.append(sid)
                domains[tid] = domain
                records.append({'paragraph': tid, 'length_candidates': len(length_domains[tid]),
                                'candidate_source_ids': domain})
                if not domain:
                    rec.update(status='UNSAT_EMPTY_RUN_DOMAIN', empty_paragraph=tid)
                    break
            if len(domains) != len(targets) or any(not d for d in domains.values()):
                continue
            if not perfect_matching(domains):
                rec['status'] = 'UNSAT_ENTRY_ALLDIFFERENT'
                continue
            rec['status'] = 'EXACT_RING_SEARCH'
            def join(remaining, key, used, assignments):
                stats['join_nodes'] += 1
                alive(deadline)
                if not remaining:
                    models.append({'index': j, 'assignments': sorted(assignments),
                                   'positions': dict(sorted(key.items()))})
                    if len(models) >= limit:
                        raise BudgetStop('model output cap')
                    return
                tid = min(remaining, key=lambda t: (sum(s not in used for s in domains[t]), t))
                rest = [t for t in remaining if t != tid]
                for sid in domains[tid]:
                    if sid in used:
                        continue
                    for extension in local_extensions(target_by_id[tid]['cipher'],
                            sources[sid].plain, j, key, deadline, stats):
                        join(rest, extension, used | {sid}, assignments + [[tid, sid]])
            before = len(models)
            join(list(domains), {min(glyphs): 0}, set(), [])
            rec.update(status='COMPLETE_SAT' if len(models) > before else 'COMPLETE_UNSAT',
                       model_count=len(models) - before)
    except (BudgetStop, RecursionError, MemoryError) as exc:
        complete, stopping = False, type(exc).__name__ + ': ' + str(exc)
    status = ('COMPLETE_SAT' if models else 'COMPLETE_UNSAT') if complete else (
        'UNKNOWN_WITH_WITNESS' if models else 'UNKNOWN_NO_WITNESS')
    return {'status': status, 'enumeration_complete': complete, 'models': models,
            'stop_reason': stopping, 'indices': index_records, 'stats': dict(stats),
            'paragraphs': len(targets), 'glyph_count': len(glyphs),
            'elapsed_seconds': time.monotonic() - started}


def source_intake(pool_path, lock_path, audit_path):
    raw = [p.read_bytes() for p in (pool_path, lock_path, audit_path)]
    for name, data in zip(('source_pool', 'source_lock', 'source_audit'), raw):
        if sha(data) != SPEC[name + '_sha256']:
            raise ValueError(name + ' byte binding mismatch; target unread')
    pool, lock, audit = map(json.loads, raw)
    if (lock['status'] != 'FROZEN' or audit['status'] != 'PASS' or pool['pending']
            or len(pool['entries']) != 1016
            or lock['source_pool_sha256'] != sha(raw[0])
            or audit['source_pool_sha256'] != sha(raw[0])):
        raise ValueError('895 frozen source validation gate failed')
    return pool


def target_intake(path):
    raw = path.read_bytes()
    if sha(raw) != SPEC['target_packet_sha256']:
        raise ValueError('target packet byte mismatch; refusing to decompress/parse')
    packet = json.loads(gzip.decompress(raw))
    if packet['schema'] != 'GDT893_ODD_ONLY_FIT_PACKET_V1' or set(packet['panels']) != set(SPEC['panels']):
        raise ValueError('wrong inherited target schema')
    panels = {}
    for panel, rows in packet['panels'].items():
        if len(rows) != SPEC['panels'][panel] or len({t['id'] for t in rows}) != len(rows):
            raise ValueError('complete target coverage changed')
        result = []
        for t in rows:
            folio = t['physical_folio']
            if (not re.fullmatch('f[0-9]+', folio) or int(folio[1:]) % 2 != 1
                    or t['page'].startswith(('f84', 'f116')) or not t['words']
                    or len(t['words']) != len(t['source_group_ids'])
                    or any(not re.fullmatch('[a-z]+', w) for w in t['words'])):
                raise ValueError('outside unchanged complete odd literal packet')
            result.append({'id': t['id'], 'cipher': ''.join(t['words'])})
        panels[panel] = result
    return panels


def projection_artifact(projection):
    return {'schema': 'GDT896_SOURCE_PROJECTION_V1',
            'source_pool_sha256': SPEC['source_pool_sha256'],
            'accepted': len(projection['entries']), 'excluded': len(projection['exclusions']),
            'entries': [{'id': e['id'], 'length': len(e['plain']),
                         'plain_sha256': sha(e['plain'].encode('ascii'))}
                        for e in projection['entries']],
            'exclusions': projection['exclusions']}


def main():
    parser = argparse.ArgumentParser()
    for name in ('source-pool', 'source-lock', 'source-audit', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--target-packet', type=Path)
    parser.add_argument('--source-only', action='store_true')
    args = parser.parse_args()
    pool = source_intake(args.source_pool, args.source_lock, args.source_audit)
    projection = project(pool['entries'])
    if args.source_only:
        result = projection_artifact(projection)
    else:
        if args.target_packet is None:
            raise ValueError('target packet required')
        panels = target_intake(args.target_packet)
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = {p: executor.submit(panel_models, targets, projection['entries'],
                SPEC['primary_seconds_per_panel'], SPEC['model_cap_per_panel'])
                for p, targets in panels.items()}
            fitted = {p: f.result() for p, f in futures.items()}
        result = {'schema': 'GDT896_COMPLETE_ENTRY_ROTOR_V1', 'panels': fitted,
                  'source_projection': projection_artifact(projection), 'held_access': False,
                  **{k: v for k, v in SPEC.items() if k.endswith('_sha256')},
                  'implementation_sha256': sha(Path(__file__).read_bytes())}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({p: {k: v for k, v in r.items() if k not in ('models', 'indices')}
                      for p, r in result.get('panels', {}).items()} if 'panels' in result else
                     {k: result[k] for k in ('accepted', 'excluded')}))


if __name__ == '__main__':
    main()
