"""Finite conditional scope models on retained source; no text decoder."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
INPUT = ROOT / 'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/CF_FULL_LEAVES.json'

def runs(source, spec):
    vocab = set(spec['nominals']) | set(spec['fields']) | set(spec['compound'])
    output = []
    for line in source['lines']:
        pending = []
        for row in line['groups'] + [None]:
            if row is not None and row['ivtff_group_raw'] in vocab:
                pending.append(row)
            elif pending:
                output.append({'edition': line['edition'], 'page': line['page'],
                    'locus': line['locus'], 'groups': pending})
                pending = []
    return output

def owners(run, spec, policy):
    rows = run['groups']
    heads = [i for i, row in enumerate(rows) if row['ivtff_group_raw'] in spec['nominals']]
    mapping = {}
    for i, row in enumerate(rows):
        if i in heads:
            continue
        previous = [head for head in heads if head < i]
        mapping[i] = previous[-1] if previous else heads[0] if heads else None
    if policy == 'PAIR_SPLIT':
        for left, right in zip(heads, heads[1:]):
            if right - left == 3:
                mapping[left + 1] = left
                mapping[left + 2] = right
    return mapping

def family(mask):
    domains = [(mask >> i) & 1 for i in range(4)]
    uses_frame = domains[0] != domains[2] or domains[1] != domains[3]
    uses_tail = domains[0] != domains[1] or domains[2] != domains[3]
    return 'interaction' if uses_frame and uses_tail else 'frame_only' if uses_frame else 'tail_only' if uses_tail else 'constant'

def evaluate(retained, spec, mask, polarity, policy):
    claims, unbound = [], []
    for run in retained:
        rows = run['groups']
        mapping = owners(run, spec, policy)
        for i, row in enumerate(rows):
            raw = row['ivtff_group_raw']
            if raw in spec['nominals']:
                natural = spec['nominals'][raw]['natural']
                if natural:
                    claims.append({'edition': row['edition'], 'owner': row['source_group_id'],
                        'source': row['source_group_id'], 'raw': raw, 'domain': 'natural',
                        'thermal': natural, 'kind': 'inherited_nominal_C0'})
                continue
            owner_index = mapping[i]
            if raw in spec['compound']:
                field = spec['compound'][raw]
                domain = field['domain']
            else:
                field = spec['fields'][raw]
                cell = 2 * field['wrapped'] + field['tail_value']
                domain = 'natural' if (mask >> cell) & 1 else 'physical'
            thermal = 'hot' if (field['polarity'] == 'k') == (polarity == 'k_hot') else 'cold'
            claim = {'edition': row['edition'], 'owner': rows[owner_index]['source_group_id'] if owner_index is not None else None,
                'source': row['source_group_id'], 'raw': raw, 'domain': domain,
                'thermal': thermal, 'kind': 'whole_field_C0'}
            (claims if owner_index is not None else unbound).append(claim)
    grouped = defaultdict(list)
    for claim in claims:
        grouped[(claim['edition'], claim['owner'], claim['domain'])].append(claim)
    contradictions = [{'edition': key[0], 'owner': key[1], 'domain': key[2], 'claims': entries}
        for key, entries in sorted(grouped.items()) if {c['thermal'] for c in entries} == {'hot', 'cold'}]
    return {'id': f'{policy}:{polarity}:D{mask:02d}', 'ownership': policy,
        'polarity': polarity, 'mask': mask, 'feature_family': family(mask),
        'domains': ['natural' if (mask >> i) & 1 else 'physical' for i in range(4)],
        'survives_all_readers_conditionally': not contradictions,
        'contradictions': contradictions, 'bound_claims': claims, 'unbound_fields': unbound,
        'reader_contradictions': dict(Counter(c['edition'] for c in contradictions)),
        'claim_ceiling': 'Internal consistency under stipulated thermal/nominal/scope assumptions; no meaning confirmation'}

def main():
    spec = json.loads((BASE / 'src/MODEL.json').read_text())
    source = json.loads(INPUT.read_text())
    retained = runs(source, spec)
    models = [evaluate(retained, spec, mask, polarity, policy)
        for policy in spec['ownership_models'] for polarity in spec['polarity_orders'] for mask in spec['domain_masks']]
    packet = {'input_path': str(INPUT.relative_to(ROOT)),
        'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        'source_group_count': len(source['rows']), 'full_line_count': len(source['lines']),
        'scope': 'Whole previously exposed f9 and f50 text leaves; all reader alternatives',
        'runs': retained, 'nominal_roles_confirmed': False}
    (BASE / 'artifacts/RUNS.json').write_text(json.dumps(packet, ensure_ascii=False, indent=2) + '\n')
    result = {'status': 'CONDITIONAL_SCOPE_FAMILY_DIAGNOSTIC', 'models': models,
        'survivors': [m['id'] for m in models if m['survives_all_readers_conditionally']],
        'confirmed_words': 0, 'independent_meaning_confirmation_leaves': 0,
        'semantic_score': None, 'significance': None,
        'reserved_pages_opened': [], 'input_hashes': {str(INPUT.relative_to(ROOT)): packet['input_sha256'],
            str((BASE / 'src/MODEL.json').relative_to(ROOT)): hashlib.sha256((BASE / 'src/MODEL.json').read_bytes()).hexdigest()}}
    equivalent = defaultdict(list)
    for model in models:
        if model['survives_all_readers_conditionally']:
            signature = json.dumps(model['bound_claims'] + model['unbound_fields'], sort_keys=True)
            equivalent[signature].append(model['id'])
    result['surviving_prediction_groups'] = list(equivalent.values())
    result['observed_feature_cells'] = sorted({2 * spec['fields'][r['ivtff_group_raw']]['wrapped'] + spec['fields'][r['ivtff_group_raw']]['tail_value']
        for run in retained for r in run['groups'] if r['ivtff_group_raw'] in spec['fields']})
    (BASE / 'artifacts/RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    table = ['# All64 registered conditional models',
        'Domains in order: bare-y, bare-aiin, wrapped-y, wrapped-aiin. Survivors are compatible with stipulated meanings and ownership, not confirmed readings.', '',
        '| Model | Family | Domains | Contradictory owners | Unbound fields | Outcome |',
        '|---|---|---|---:|---:|---|']
    for model in models:
        table.append('| ' + ' | '.join((model['id'], model['feature_family'], ', '.join(model['domains']),
            str(len(model['contradictions'])), str(len(model['unbound_fields'])),
            'conditional survivor' if model['survives_all_readers_conditionally'] else 'contradicted under fixed package')) + ' |')
    (BASE / 'artifacts/MODEL_TABLE.md').write_text('\n'.join(table) + '\n')
    print(json.dumps({'models': len(models), 'runs': len(retained), 'survivors': result['survivors'],
        'field_counts': dict(Counter(r['ivtff_group_raw'] for run in retained for r in run['groups'] if r['ivtff_group_raw'] not in spec['nominals']))}, indent=2))
