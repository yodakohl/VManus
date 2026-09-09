#!/usr/bin/env python3
"""Independent GDT893 odd-packet window, global-optimum and projection audit.

No imports from fitter, matcher or optimizer. Source ingestion and excluded
mixed-cache completeness are upstream checks, not claimed by this validator.
"""
import argparse
from collections import defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time

EDITIONS = ('ZL3b', 'IT2a', 'RF1b', 'CONSENSUS')


class BudgetExpired(Exception):
    pass


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    hasher = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            hasher.update(block)
    return hasher.hexdigest()


def read_gzip(path):
    with gzip.open(path, 'rt') as handle:
        return json.load(handle)


def checkpoint(deadline):
    if time.monotonic() > deadline:
        raise BudgetExpired()


def direct_map(target, plain):
    require(len(target) == len(plain), 'incomplete word window')
    forward, reverse = {}, {}
    for cipher, source in zip(target, plain):
        require(cipher not in forward or forward[cipher] == source, 'forward word-map conflict')
        require(source not in reverse or reverse[source] == cipher, 'reverse word-map conflict')
        forward[cipher], reverse[source] = source, cipher
    return forward


def canonical_mapping(mapping):
    converted = {int(k): v for k, v in mapping.items()}
    require(len(converted) == len(mapping), 'duplicate canonical map key')
    require(all(type(k) is int and k >= 0 and type(v) is int and v >= 0
                for k, v in converted.items()), 'invalid map ID')
    return tuple(sorted(converted.items()))


def validate_packet(packet):
    require(packet['schema'] == 'GDT893_ODD_ONLY_FIT_PACKET_V1', 'packet schema mismatch')
    require(set(packet['panels']) == set(EDITIONS), 'edition panel mismatch')
    for key in ('source_words', 'cipher_words'):
        require(len(packet[key]) == len(set(packet[key])), 'duplicate vocabulary entry')
        require(all(isinstance(w, str) and w for w in packet[key]), 'invalid vocabulary')
    ids = [u['id'] for u in packet['source_units']]
    require(len(ids) == len(set(ids)), 'duplicate source unit ID')
    for unit in packet['source_units']:
        require(all(type(x) is int and 0 <= x < len(packet['source_words']) for x in unit['word_ids']),
                'source vocabulary index out of bounds')
    ci = {w: n for n, w in enumerate(packet['cipher_words'])}
    for edition, targets in packet['panels'].items():
        seen = set()
        for target in targets:
            require(not target['page'].startswith('f84'), 'sealed page in packet')
            folio = target['physical_folio']
            require(re.fullmatch('f[0-9]+', folio) and int(folio[1:]) % 2 == 1,
                    'non-odd physical folio in fit packet')
            require(target['id'] not in seen, 'duplicate paragraph ID in edition')
            seen.add(target['id'])
            require(target['words'] and all(w in ci for w in target['words']), 'invalid complete target')
            require(len(target['source_group_ids']) == len(target['words']), 'target group count mismatch')
    return ci


def read_matches(path, targets, units):
    matches = set()
    with Path(path).open(newline='') as handle:
        reader = csv.reader(handle)
        require(next(reader, None) == ['target_index', 'source_index', 'start', 'length'], 'match CSV header')
        for row in reader:
            require(len(row) == 4, 'match row field count')
            t, s, start, length = map(int, row)
            require(0 <= t < len(targets) and 0 <= s < len(units), 'match record index bounds')
            require(length == len(targets[t]['words']) and length > 0, 'partial target window')
            require(start >= 0 and start + length <= len(units[s]['word_ids']), 'source window bounds')
            value = (t, s, start, length)
            require(value not in matches, 'duplicate raw window match')
            matches.add(value)
    return matches


def validate_candidates(packet, edition, fit, matches):
    ci = {w: n for n, w in enumerate(packet['cipher_words'])}
    targets, units = packet['panels'][edition], packet['source_units']
    expected = {}
    for t, s, start, length in matches:
        target, unit = targets[t], units[s]
        plain = unit['word_ids'][start:start + length]
        mapping = direct_map([ci[w] for w in target['words']], plain)
        key = (target['id'], canonical_mapping(mapping))
        prov = (unit['id'], unit['source'], start, length)
        if key not in expected:
            expected[key] = {'target_index': t, 'plain': plain, 'provenance': set()}
        expected[key]['provenance'].add(prov)
    actual_keys = set()
    for candidate in fit['candidates']:
        key = (candidate['paragraph'], canonical_mapping(candidate['mapping']))
        require(key in expected and key not in actual_keys, 'missing or duplicate candidate mapping')
        actual_keys.add(key)
        want = expected[key]
        require(candidate['target_index'] == want['target_index'], 'candidate target index mismatch')
        require(candidate['plain_word_ids'] == want['plain'], 'candidate full plaintext mismatch')
        require(candidate['weight'] == len(want['plain']), 'candidate objective weight mismatch')
        provenance = [(p['unit'], p['source'], p['start'], p['length']) for p in candidate['provenance']]
        require(len(provenance) == len(set(provenance)), 'duplicate candidate provenance')
        require(set(provenance) == want['provenance'], 'candidate provenance aliases incomplete')
    require(actual_keys == set(expected), 'candidate pool incomplete')
    require(fit.get('raw_matches') == len(matches), 'raw match counter mismatch')
    require(fit.get('candidate_materialization_complete') is True, 'candidate materialization incomplete')
    return {'status': 'PASS', 'raw_matches': len(matches), 'deduplicated_candidates': len(expected)}


def exhaustive_optima(candidates, deadline):
    """Enumerate paragraph choices (including omission), using direct map joins.

    Branch-and-bound only skips branches strictly below a safe weight bound;
    ties remain, so every maximum set is retained. No shared conflict graph.
    """
    domains = defaultdict(list)
    maps = []
    for index, candidate in enumerate(candidates):
        domains[candidate['paragraph']].append(index)
        maps.append(dict(canonical_mapping(candidate['mapping'])))
    groups = sorted(domains.values(), key=lambda indices: (len(indices), indices[0]))
    suffix = [0] * (len(groups) + 1)
    for n in range(len(groups) - 1, -1, -1):
        suffix[n] = suffix[n + 1] + max(candidates[i]['weight'] for i in groups[n])
    best, optima, nodes = -1, set(), 0

    def visit(depth, chosen, forward, reverse, weight):
        nonlocal best, optima, nodes
        nodes += 1
        if nodes % 256 == 0:
            checkpoint(deadline)
        if weight + suffix[depth] < best:
            return
        if depth == len(groups):
            if weight > best:
                best, optima = weight, set()
            if weight == best:
                optima.add(tuple(sorted(chosen)))
            return
        for index in groups[depth]:
            mapping = maps[index]
            if any((c in forward and forward[c] != p) or (p in reverse and reverse[p] != c)
                   for c, p in mapping.items()):
                continue
            new_forward, new_reverse = dict(forward), dict(reverse)
            new_forward.update(mapping)
            new_reverse.update({p: c for c, p in mapping.items()})
            visit(depth + 1, chosen + [index], new_forward, new_reverse,
                  weight + candidates[index]['weight'])
        visit(depth + 1, chosen, forward, reverse, weight)

    checkpoint(deadline)
    visit(0, [], {}, {}, 0)
    checkpoint(deadline)
    return best, optima, nodes


def project(candidates, solutions):
    common_paragraphs, common_words = None, None
    for solution in solutions:
        paragraphs, words = {}, {}
        for index in solution:
            candidate = candidates[index]
            paragraphs[candidate['paragraph']] = tuple(candidate['plain_word_ids'])
            words.update(dict(canonical_mapping(candidate['mapping'])))
        if common_paragraphs is None:
            common_paragraphs, common_words = paragraphs, words
        else:
            common_paragraphs = {k: v for k, v in common_paragraphs.items() if paragraphs.get(k) == v}
            common_words = {k: v for k, v in common_words.items() if words.get(k) == v}
    return {'forced_paragraphs': sorted((k, v) for k, v in (common_paragraphs or {}).items()),
            'forced_word_values': sorted((common_words or {}).items())}


def validate_optimum(fit, deadline, independent=None):
    if fit['optimization']['status'] != 'COMPLETE':
        raise BudgetExpired()
    if independent is None:
        best, optima, nodes = exhaustive_optima(fit['candidates'], deadline)
    else:
        if independent['status'] != 'COMPLETE':
            raise BudgetExpired()
        best = independent['best_weight']
        optima = {tuple(sorted(s)) for s in independent['optimal_solutions']}
        require(len(optima) == len(independent['optimal_solutions']), 'duplicate independent optimum')
        nodes = independent['stats']['nodes']
    reported = fit['optimization']['optimal_solutions']
    for solution in reported:
        require(isinstance(solution, list) and len(solution) == len(set(solution)), 'duplicate solution candidate')
        require(all(type(i) is int and 0 <= i < len(fit['candidates']) for i in solution), 'solution candidate index bounds')
    reported_sets = {tuple(sorted(s)) for s in reported}
    require(len(reported_sets) == len(reported), 'duplicate optimum set')
    require(best == fit['optimization']['best_weight'], 'global optimum weight mismatch')
    require(reported_sets == optima, 'complete optimum-set family mismatch')
    expected = project(fit['candidates'], optima)
    observed = fit['projection']
    normalized = {'forced_paragraphs': sorted((p['paragraph'], tuple(p['plain_word_ids'])) for p in observed['forced_paragraphs']),
                  'forced_word_values': sorted((p['cipher_word_id'], p['source_word_id']) for p in observed['forced_word_values'])}
    require(normalized == expected, 'forced projection mismatch, including omission')
    return {'status': 'PASS', 'best_weight': best, 'optimal_sets': len(optima),
            'independent_search_nodes': nodes, 'forced_paragraphs': len(expected['forced_paragraphs']),
            'forced_word_values': len(expected['forced_word_values'])}


def write_records(path, sequences):
    with Path(path).open('w') as handle:
        handle.write(str(len(sequences)) + '\n')
        for index, words in enumerate(sequences):
            handle.write(str(index) + ' ' + str(len(words)) + ' ' + ' '.join(map(str, words)) + '\n')


def write_optimum_records(path, candidates):
    groups = {}
    with Path(path).open('w') as handle:
        handle.write(str(len(candidates)) + '\n')
        for candidate in candidates:
            group = groups.setdefault(candidate['paragraph'], len(groups))
            pairs = canonical_mapping(candidate['mapping'])
            values = [group, candidate['weight'], len(pairs)]
            values += [value for pair in pairs for value in pair]
            handle.write(' '.join(map(str, values)) + '\n')


def verify_commitments(fit_dir, result, packet, base):
    require(sha(fit_dir / 'FIT_PACKET.json.gz') == result['fit_packet_sha256'], 'fit packet byte hash mismatch')
    published = json.loads((base / 'artifacts' / 'INPUT_LOCK.json').read_text())
    require(result['input_lock'] == packet['input_lock'] == published, 'input commitments differ')
    root = base.parents[2]
    require(result['source_hashes'], 'source hash inventory missing')
    for name, expected in result['source_hashes'].items():
        p = Path(name)
        require(not p.is_absolute() and '..' not in p.parts, 'invalid committed source path')
        require(sha(root / p) == expected, 'committed source file hash mismatch: ' + name)
    return {'status': 'PASS', 'source_files': len(result['source_hashes']),
            'input_lock_equality': True, 'fit_packet_bytes': True,
            'upstream_mixed_target_cache': 'Not opened; preparation audit owns raw cache integrity and intake completeness.'}


def run(fit_dir, deadline):
    base = Path(__file__).resolve().parents[1]
    result = json.loads((fit_dir / 'RESULT.json').read_text())
    if result['status'] != 'COMPLETE':
        raise BudgetExpired()
    packet = read_gzip(fit_dir / 'FIT_PACKET.json.gz')
    ci = validate_packet(packet)
    commitments = verify_commitments(fit_dir, result, packet, base)
    summaries = {}
    with tempfile.TemporaryDirectory(prefix='gdt893_validator_') as folder:
        work = Path(folder)
        binary = work / 'windows'
        subprocess.run(['g++', '-O3', '-std=c++17', str(base / 'src' / 'validate_windows.cpp'), '-o', str(binary)],
                       check=True, capture_output=True, timeout=max(1, deadline - time.monotonic()))
        optimizer = work / 'optima'
        subprocess.run(['g++', '-O3', '-std=c++17', str(base / 'src' / 'validate_optima.cpp'), '-o', str(optimizer)],
                       check=True, capture_output=True, timeout=max(1, deadline - time.monotonic()))
        write_records(work / 'source.txt', [u['word_ids'] for u in packet['source_units']])
        for edition in EDITIONS:
            checkpoint(deadline)
            targets = packet['panels'][edition]
            write_records(work / 'target.txt', [[ci[w] for w in t['words']] for t in targets])
            completed = subprocess.run([str(binary), str(work / 'target.txt'), str(work / 'source.txt'), str(work / 'matches.csv')],
                                       check=True, capture_output=True, text=True,
                                       timeout=max(1, deadline - time.monotonic()))
            stats = json.loads(completed.stdout)
            oracle = read_matches(work / 'matches.csv', targets, packet['source_units'])
            actual = read_matches(fit_dir / (edition + '_MATCHES.csv'), targets, packet['source_units'])
            require(actual == oracle, 'complete source-window match set differs: ' + edition)
            expected_windows = sum(max(0, len(u['word_ids']) - len(t['words']) + 1)
                                   for t in targets for u in packet['source_units'])
            require(stats['windows'] == expected_windows and stats['matches'] == len(oracle), 'independent enumeration counters')
            fit = read_gzip(fit_dir / (edition + '_FIT.json.gz'))
            require(fit['enumeration']['matches'] == len(oracle), 'root match counter mismatch')
            candidate_check = validate_candidates(packet, edition, fit, oracle)
            write_optimum_records(work / 'candidates.txt', fit['candidates'])
            subprocess.run([str(optimizer), str(work / 'candidates.txt'), str(work / 'optima.json'),
                            str(max(0, deadline - time.monotonic()))], check=True, capture_output=True,
                           timeout=max(1, deadline - time.monotonic() + 1))
            independent_optima = json.loads((work / 'optima.json').read_text())
            optimum_check = validate_optimum(fit, deadline, independent_optima)
            summaries[edition] = {'windows': stats['windows'], 'candidate_check': candidate_check,
                                  'optimum_check': optimum_check}
    require(result['status'] == 'COMPLETE', 'root result incomplete')
    return {'status': 'PASS', 'commitments': commitments, 'panels': summaries,
            'independence': 'Explicit forward/reverse window maps; independent paragraph-domain exhaustive optimum search; omission-aware projection intersection.',
            'held_folio_fit': False, 'claim_ceiling': 'Computational replay only; no meaning, null score, or GDT388 promotion.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fit-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--budget-seconds', type=float, default=600)
    args = parser.parse_args()
    start = time.monotonic()
    try:
        result = run(args.fit_dir, start + args.budget_seconds)
    except (BudgetExpired, subprocess.TimeoutExpired, MemoryError, RecursionError):
        result = {'status': 'UNKNOWN_BUDGET', 'reason': 'Independent enumeration or optimization did not exhaust.'}
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as exc:
        result = {'status': 'VALIDATION_ERROR', 'reason': str(exc)}
    result['elapsed_seconds'] = time.monotonic() - start
    result['validator_sha256'] = sha(__file__)
    result['window_validator_sha256'] = sha(Path(__file__).with_name('validate_windows.cpp'))
    result['optimum_validator_sha256'] = sha(Path(__file__).with_name('validate_optima.cpp'))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds']}))
    if result['status'] == 'VALIDATION_ERROR':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
