#!/usr/bin/env python3
"""Replay three C0 local constructions, preserving every exposed source group.

No corpus acquisition, decoder, semantic score or unobserved word completion.
"""
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
LOCK = BASE / 'INFLUENCE_CONSTRUCTION_LOCK_20260929.json'
TABLE = BASE / 'source_supply_20260929/E_WHOLE_CONTEXT_TABLE.tsv'
GRAMMAR = ROOT / 'experiments/yolo/gdt1051_frozen_grammar_local_application/artifacts/RESULT.json'
MODELS = ('A_ACTIVE_ADJACENT', 'H_HEAD_PRESERVING_MODIFIER', 'P_PASSIVE_SWITCH')


def key(row):
    return row['edition'], row['locus'], int(row['group_index'])


def replay():
    lock = json.loads(LOCK.read_text())
    for path, expected in lock['inputs'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    rows = list(csv.DictReader(io.StringIO(TABLE.read_text()), delimiter='\t'))
    assert len(rows) == 288 and len({key(row) for row in rows}) == 288
    units = defaultdict(list)
    grammar = json.loads(GRAMMAR.read_text())
    old = {(r['edition'], r['locus'], r['index']): r for r in grammar['groups']}
    assert set(old) == {key(row) for row in rows}
    output = []
    by_key = {}
    for row in rows:
        k = key(row)
        assert old[k]['raw'] == row['raw_group']
        unit = row['locus'] if row['locus'].startswith('f68r2.') else 'f89v1.13-20'
        assert row['locus'] in {'f68r2.6', 'f68r2.31'} or row['locus'] in {
            f'f89v1.{i}' for i in range(13, 21)
        }
        out = {name: row[name] for name in ('edition', 'locus', 'group_index', 'raw_group')}
        out['unit'] = unit
        out['left_separator'] = old[k]['left_separator']
        out['right_separator'] = old[k]['right_separator']
        out['formal_parse_status'] = old[k]['parse_status']
        out['frozen_wrapper_host'] = json.dumps(old[k].get('wrapper_host'), sort_keys=True)
        out['shared_okol_class_hypothesis'] = 'UNNAMED_CLASS_ONLY' if row['raw_group'] == 'okol' else 'NONE'
        for model in MODELS:
            out[model] = 'UNRESOLVED'
        by_key[k] = out
        output.append(out)
        units[row['edition'], unit].append(row)

    clauses = []
    for (edition, unit), items in units.items():
        for pos, row in enumerate(items):
            if row['raw_group'] != 'okoaiin':
                continue
            assert 0 < pos < len(items) - 1
            for model in MODELS:
                clause = {'model': model, 'edition': edition, 'unit': unit,
                          'predicate_key': list(key(row)), 'predicate_guess': 'INFLUENCE',
                          'status': 'C0_LOCAL_DERIVATION_ONLY',
                          'source_head': None, 'recipient_head': None, 'modifier': None,
                          'boundary_assumptions': []}
                by_key[key(row)][model] = 'GUESSED_RELATION'
                before, after = items[pos - 1], items[pos + 1]
                if model != MODELS[0] and before['raw_group'] == 'cho@152;y':
                    clause['status'] = 'UNRESOLVED_RF_MARKER_NO_EMENDATION'
                    clause['reason'] = 'Cannot determine whether the distinct written marker licenses H or P.'
                    clauses.append(clause)
                    continue
                left = before
                if model != MODELS[0] and before['raw_group'] == 'chody':
                    assert pos >= 2
                    left = items[pos - 2]
                    clause['modifier'] = {'key': list(key(before)), 'raw': before['raw_group']}
                    by_key[key(before)][model] = (
                        'GUESSED_HEAD_PRESERVING_MODIFIER' if model == MODELS[1]
                        else 'GUESSED_PASSIVE_SWITCH'
                    )
                source, recipient = left, after
                if model == MODELS[2] and clause['modifier'] is not None:
                    source, recipient = after, left
                for role, item in (('source_head', source), ('recipient_head', recipient)):
                    clause[role] = {'key': list(key(item)), 'raw': item['raw_group'],
                                    'meaning': 'UNNAMED_PARTICIPANT_CLASS'}
                    by_key[key(item)][model] = 'GUESSED_' + role.upper()
                for item, edge in ((left, 'left_separator'), (after, 'right_separator')):
                    value = by_key[key(item)][edge]
                    if value.startswith('UNCERTAIN'):
                        clause['boundary_assumptions'].append({
                            'key': list(key(item)), 'edge': edge, 'raw_flag': value,
                            'choice_needed': 'Treat this uncertain gap as the chosen NP boundary.'
                        })
                if clause['boundary_assumptions']:
                    clause['status'] = 'C0_LOCAL_DERIVATION_REQUIRES_UNCERTAIN_BOUNDARY'
                clauses.append(clause)

    # This is form-class recurrence, not identity of a drug across two leaves.
    links = []
    for edition in ('ZL3b', 'IT2a', 'RF1b'):
        for model in MODELS:
            local = [c for c in clauses if c['edition'] == edition and c['model'] == model]
            ring = next(c for c in local if c['unit'] == 'f68r2.31')
            prose = next(c for c in local if c['unit'] == 'f89v1.13-20')
            known = prose['status'].startswith('C0_LOCAL_DERIVATION')
            links.append({
                'edition': edition, 'model': model,
                'ring_recipient_form': ring['recipient_head']['raw'],
                'prose_source_form': prose['source_head']['raw'] if known else None,
                'prose_recipient_form': prose['recipient_head']['raw'] if known else None,
                'same_recipient_to_source_class': known and ring['recipient_head']['raw'] == prose['source_head']['raw'],
                'same_recipient_class': known and ring['recipient_head']['raw'] == prose['recipient_head']['raw'],
                'physical_referent_identity': 'NOT_DERIVED',
                'additional_boundary_assumptions': prose['boundary_assumptions'],
            })

    result = {
        'status': 'PARTIAL_C0_CONSTRUCTOR_NO_MEANING_SELECTION',
        'input_hashes': lock['inputs'], 'rows': len(rows),
        'counts_by_reader_unit': [dict(edition=e, unit=u, groups=len(v)) for (e, u), v in units.items()],
        'clauses': clauses, 'class_links': links,
        'exact_okol_occurrences': [dict(edition=r['edition'], locus=r['locus'], index=int(r['group_index'])) for r in rows if r['raw_group'] == 'okol'],
        'coverage': {m: dict(Counter(r[m] for r in output)) for m in MODELS},
        'complete_readings': 0, 'new_unselected_relations_derived': 0,
        'included_body_region_bound': False, 'excluded_body_region_bound': False,
        'draw_away_relation_bound': False, 'upper_ring_relation_derived': False,
        'physical_confirmation_leaves': 0, 'confirmed_word_meanings': 0,
        'reader_policy': 'alternate readings of one manuscript; not three confirmations',
        'source_limit': 'INFLUENCE and DRAW_AWAY remain distinct source relations',
    }
    target = BASE / 'INFLUENCE_CONSTRUCTION_TABLE_20260929.tsv'
    with target.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(output)
    (BASE / 'INFLUENCE_CONSTRUCTION_RESULT_20260929.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    r = replay()
    print(json.dumps({k: r[k] for k in ('status', 'rows', 'coverage', 'complete_readings', 'new_unselected_relations_derived')}, indent=2))
