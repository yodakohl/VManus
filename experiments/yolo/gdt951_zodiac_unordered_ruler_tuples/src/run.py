"""Exact source-tuple/whole-label feasibility; no learned decoder or score."""
import argparse
from collections import Counter, defaultdict, deque
import csv
import hashlib
import io
import json
from pathlib import Path
import re

E = Path(__file__).resolve().parents[1]
R = E.parents[2]


def dump(path, obj, frozen=False):
    txt = json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n'
    if frozen and path.exists():
        assert path.read_text() == txt, 'frozen artifact changed: ' + path.name
    else:
        path.write_text(txt)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lockcheck():
    lock = json.loads((E / 'PREREG_LOCK.json').read_text())
    for rel, h in lock['files'].items():
        assert sha(E / rel) == h, rel
    for rel, h in lock['source_files'].items():
        assert sha(R / rel) == h, rel


def inscriptions(rows, spec, phase):
    by = defaultdict(list)
    for r in rows:
        assert r['page'] in spec['intake_phases'][phase]
        assert not r['page'].startswith('f84') and r['kind'] == 'L'
        by[(r['edition'], r['page'], r['locus'])].append(r)
    out = []
    for (edition, page, locus), gs in sorted(by.items()):
        gs.sort(key=lambda r: int(r['source_group_index']))
        raw = [g['ivtff_group_raw'] for g in gs]
        reasons = []
        if not all(re.fullmatch(spec['literal_regex'], w) for w in raw):
            reasons.append('NONLITERAL_GROUP')
        if not all(int(g['source_group_count']) == len(gs) for g in gs):
            reasons.append('GROUP_COUNT_MISMATCH')
        if not all(int(b['source_group_index']) == int(a['source_group_index']) + 1
                   for a, b in zip(gs, gs[1:])):
            reasons.append('NONCONSECUTIVE_INDICES')
        if not all(a['right_separator'] == b['left_separator'] ==
                   spec['definite_interior_separator'] for a, b in zip(gs, gs[1:])):
            reasons.append('UNCERTAIN_INTERIOR_SEAM')
        out.append({'edition': edition, 'page': page, 'locus': locus,
                    'sign': spec['page_sign'][page], 'phase': phase,
                    'physical_leaf': re.match(r'f\d+', page)[0],
                    'groups': raw, 'definite': not reasons, 'unknown_reasons': reasons})
    if spec['unlabeled_slot']['page'] in spec['intake_phases'][phase]:
        for edition in spec['editions']:
            out.append({'edition': edition, 'page': 'f72r2',
                        'locus': 'UNLABELED_CATALOGUE_SLOT', 'sign': 'GEMINI',
                        'phase': phase, 'physical_leaf': 'f72', 'groups': [],
                        'definite': False, 'unknown_reasons': ['SOURCE_UNLABELED_SLOT']})
    return out


def maximum_matching(domains, forced=None):
    """Augmenting paths with an optional immutable edge."""
    right = {}
    fixed_left = None
    if forced is not None:
        fixed_left, fixed_right = forced
        if fixed_right not in domains[fixed_left]:
            return {}
        right[fixed_right] = fixed_left

    def augment(u, seen):
        for v in domains[u]:
            if v in seen:
                continue
            seen.add(v)
            owner = right.get(v)
            if owner == fixed_left and forced is not None:
                continue
            if owner is None or augment(owner, seen):
                right[v] = u
                return True
        return False

    for u in sorted(domains, key=lambda u: (len(domains[u]), u)):
        if u != fixed_left:
            augment(u, set())
    return {u: v for v, u in right.items()}


def hall_certificate(domains, matching):
    owners = {v: u for u, v in matching.items()}
    left = set(domains) - set(matching)
    queue = deque(sorted(left))
    neighbours = set()
    while queue:
        u = queue.popleft()
        for v in domains[u]:
            if v not in neighbours:
                neighbours.add(v)
                if v in owners and owners[v] not in left:
                    left.add(owners[v])
                    queue.append(owners[v])
    assert len(left) > len(neighbours)
    assert neighbours == {v for u in left for v in domains[u]}
    return {'label_ids': sorted(left), 'tuple_ids': sorted(neighbours),
            'deficiency': len(left) - len(neighbours)}


def evaluate(model, edition, scope, signs, records, tuples, spec, predict=False):
    selected = [r for r in records if r['edition'] == edition and r['sign'] in signs]
    counts = {s: Counter() for s in signs}
    unknown = Counter()
    loci = defaultdict(list)
    for r in selected:
        if r['definite']:
            w = tuple(r['groups'])
            counts[r['sign']][w] += 1
            loci[w].append(r['locus'])
        else:
            unknown[r['sign']] += 1
    for s in signs:
        assert sum(counts[s].values()) + unknown[s] == 30, (edition, scope, s)
    words = sorted(loci)
    labels = [{'id': f'W{i:04}', 'groups': list(w),
               'counts': {s: counts[s][w] for s in signs}, 'loci': sorted(loci[w])}
              for i, w in enumerate(words)]
    domains = {w['id']: [t['id'] for t in tuples if
                        all(w['counts'][s] <= t['counts'][s] for s in signs)]
               for w in labels}
    matching = maximum_matching(domains)
    feasible = len(matching) == len(labels)
    grouped = defaultdict(list)
    for t in tuples:
        grouped[tuple(t['counts'][s] for s in signs)].append(t['id'])
    groups = [{'count_vector': list(k), 'tuple_ids': v} for k, v in sorted(grouped.items())]
    result = {'model': model, 'edition': edition, 'scope': scope, 'signs': signs,
              'definite_slots': sum(sum(c.values()) for c in counts.values()),
              'unknown_slots': sum(unknown.values()),
              'unknown_by_sign': {s: unknown[s] for s in signs},
              'definite_types': len(labels), 'labels': labels, 'domains': domains,
              'source_tuple_types': len(tuples), 'source_count_equivalence_classes': groups,
              'maximum_matching_size': len(matching), 'matching_witness': matching,
              'feasible': feasible, 'hall_certificate': None if feasible else
              hall_certificate(domains, matching),
              'status': 'CONSISTENT_UNCONFIRMED' if feasible else 'CONTRADICTED',
              'observed_key_count': 'NOT_ENUMERATED',
              'complete_renderer_identified': False, 'confirmed_words': 0}
    if predict:
        supported = {}
        if feasible:
            for u in domains:
                supported[u] = [v for v in domains[u] if
                                len(maximum_matching(domains, (u, v))) == len(labels)]
        by_id = {t['id']: t for t in tuples}
        result['supported_discovery_edges'] = supported
        result['additional_predictions'] = {
            u: [{'tuple_id': v, 'values': by_id[v]['values'],
                 'counts': {s: by_id[v]['counts'][s]
                            for s in spec['scopes']['ADDITIONAL']}}
                for v in vs] for u, vs in supported.items()}
        result['observed_binding_unique'] = bool(labels) and feasible and all(
            len(vs) == 1 for vs in supported.values())
        result['marginal_domains_are_not_independent'] = True
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', choices=['discovery', 'final'], required=True)
    a = ap.parse_args()
    lockcheck()
    spec = json.loads((E / 'src/SPEC.json').read_text())
    source = json.loads((E / 'src/SOURCE_PREDICTIONS.json').read_text())
    phases = ['discovery'] if a.phase == 'discovery' else ['discovery', 'additional', 'taurus']
    records = []
    for phase in phases:
        path = E / 'artifacts' / ('INPUT_' + phase.upper() + '.json')
        receipt = json.loads((E / 'src' / ('INTAKE_' + phase.upper() + '.json')).read_text())
        assert sha(path) == receipt['projection_sha256']
        data = json.loads(path.read_text())
        records.extend(inscriptions(data['rows'], spec, phase))
    scopes = ['DISCOVERY'] if a.phase == 'discovery' else list(spec['scopes'])
    results = [evaluate(model, edition, scope, spec['scopes'][scope], records,
                        source[model], spec, predict=scope == 'DISCOVERY')
               for model in spec['models'] for edition in spec['editions'] for scope in scopes]
    package = {'phase': a.phase, 'results': results, 'inscriptions': records,
               'new_semantic_evidence': False, 'independent_meaning_capacity': 0,
               'reserved_pages_opened': False, 'source_variants_changed': False}
    name = 'DISCOVERY.json' if a.phase == 'discovery' else 'RESULT.json'
    dump(E / 'artifacts' / name, package, frozen=True)
    if a.phase == 'discovery':
        files = ['artifacts/INPUT_DISCOVERY.json', 'src/INTAKE_DISCOVERY.json',
                 'artifacts/DISCOVERY.json', 'PREREG_LOCK.json']
        dump(E / 'DISCOVERY_FREEZE.json', {'files': {p: sha(E / p) for p in files},
             'additional_or_taurus_contents_accessed': False}, frozen=True)
    else:
        frozen = json.loads((E / 'DISCOVERY_FREEZE.json').read_text())
        for p, h in frozen['files'].items():
            assert sha(E / p) == h, 'discovery freeze changed: ' + p
        previous = json.loads((E / 'artifacts/DISCOVERY.json').read_text())['results']
        assert [r for r in results if r['scope'] == 'DISCOVERY'] == previous
        fields = ['model', 'edition', 'scope', 'definite_slots', 'unknown_slots',
                  'definite_types', 'source_tuple_types', 'maximum_matching_size', 'status']
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for r in results:
            writer.writerow({f: r[f] for f in fields})
        (E / 'artifacts/CANDIDATE_TABLE.tsv').write_text(stream.getvalue())
    print(json.dumps([{k: r[k] for k in ['model', 'edition', 'scope', 'definite_slots',
          'unknown_slots', 'definite_types', 'maximum_matching_size', 'status']}
          for r in results]))


if __name__ == '__main__':
    main()
