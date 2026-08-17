#!/usr/bin/env python3
"""Validate GDT277 without importing its producer."""
from __future__ import annotations
import csv, hashlib, json, statistics
from collections import defaultdict
from pathlib import Path
import run_gdt276_residual_channel_world_comparison as frozen

R = Path(__file__).resolve().parent
MODELS = tuple(frozen.MODELS)
IDS = (
    'ORDINARY_NATURAL_LANGUAGE', 'ABBREVIATION_HEAVY_MEDIEVAL',
    'ARBITRARY_LOCAL_CODEBOOK', 'COMPOSITIONAL_TECHNICAL_NOTATION',
    'HYBRID_SHORTHAND', 'VOYNICH_MATCHED_REFERENCE')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def csha(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True,
                     separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()

def rows(path):
    with Path(path).open(encoding='utf8', newline='') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))

checks = []
def ck(name, value, detail=''):
    checks.append({'check': name, 'pass': bool(value), 'detail': str(detail)})
    assert value, (name, detail)

design = json.loads((R / 'gdt277_design.json').read_text())
base = json.loads((R / 'gdt276_design.json').read_text())
result = json.loads((R / 'gdt277_result.json').read_text())
inv = rows(R / 'gdt277_matched_event_inventory.tsv')
world = rows(R / 'gdt277_world_scores.tsv')
null = rows(R / 'gdt277_null_results.tsv')
leak = rows(R / 'gdt277_representation_leakage.tsv')
leak_folds = rows(R / 'gdt277_representation_fold_scores.tsv')
sig = rows(R / 'gdt277_signature_summary.tsv')
cap = rows(R / 'gdt277_capacity_audit.tsv')
freeze = rows(R / 'gdt277_gdt276_freeze_manifest.tsv')
controls = rows(R / 'gdt277_control_manifest.tsv')

ck('design_frozen', design['status'] == 'FROZEN_BEFORE_GDT277_SCORING')
ck('gdt276_immutable', all(sha(R / x['artifact']) == x['frozen_sha256'] for x in freeze), len(freeze))
ck('control_sources_current', all(
    sha(R / x['observation_input']) == x['observation_sha256'] and
    sha(R / x['oracle_or_pair_input']) == x['oracle_or_pair_sha256']
    for x in controls))
ck('oracles_not_scored', all(x['oracle_used_for_scoring'] == '0' for x in controls))
ck('inventory_rows', len(inv) == 6 * 4476, len(inv))
ck('six_panels', {x['control_id'] for x in inv} == set(IDS))
ck('zero_f84', not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in inv))
ck('semantic_assignment_absent', result['semantic_assignments'] == 0)
ck('alphabet_capacity', all(set(x['page_host']).issubset(set(base['alphabet']) - {'<EOS>'}) for x in inv))

by = defaultdict(list)
for row in inv:
    by[row['control_id']].append(row)
quota = {int(k): int(v) for k, v in design['matched_view']['length_quotas'].items()}
for cid in IDS:
    ck('panel_count_' + cid, len(by[cid]) == 4476)
    got = defaultdict(int)
    for row in by[cid]:
        got[len(row['page_host'])] += 1
    ck('length_quota_' + cid, dict(got) == quota, dict(got))

slot_fields = ('page', 'physical_folio', 'locus', 'group_index', 'group_count',
               'record_ordinal', 'field_ordinal', 'within_field_position',
               'line_close', 'paragraph_close')
base_slots = None
for cid in IDS:
    current = {x['observation_id']: tuple(x[k] for k in slot_fields) for x in by[cid]}
    ck('unique_slots_' + cid, len(current) == 4476)
    if base_slots is None:
        base_slots = current
    else:
        ck('same_scaffold_' + cid, current == base_slots)

ck('capacity_rows', len(cap) == 6 and all(
    int(x['matched_events']) == 4476 and int(x['matched_folios']) == 91 for x in cap))
ck('world_rows', len(world) == 6 * 5)
ck('null_rows', len(null) == 6 * 4 * 64)
ck('folio_rows', len(rows(R / 'gdt277_folio_scores.tsv')) == 6 * 5 * 91)
ck('leak_rows', len(leak) == 6 * 5)
ck('leak_fold_rows', len(leak_folds) == 6 * 5 * 91)
ck('signature_rows', len(sig) == 6)

# Replay every observed score from the serialized event panel.
wmap = {(x['control_id'], x['model']): x for x in world}
for cid in IDS:
    observed = frozen.score_models(by[cid], base)
    rank = sorted(MODELS, key=lambda m: observed[m]['bits'])
    for model in MODELS:
        delta = observed[model]['bits'] - float(wmap[cid, model]['held_bits'])
        ck('score_' + cid + '_' + model, abs(delta) < 1e-8, delta)
        ck('rank_' + cid + '_' + model,
           int(wmap[cid, model]['rank']) == rank.index(model) + 1)

# Reconstruct all matched-null summaries from complete null outputs.
nmap = defaultdict(list)
for row in null:
    nmap[row['control_id'], row['model']].append(float(row['held_bits']))
for cid in IDS:
    for model in MODELS:
        observed = wmap[cid, model]
        if model == 'LOCAL_CODEBOOK':
            ck('local_null_' + cid,
               float(observed['matched_savings_bits']) == 0 and
               float(observed['matched_lower_tail_p']) == 1)
            continue
        values = nmap[cid, model]
        ck('null64_' + cid + '_' + model, len(values) == 64)
        mean = statistics.mean(values)
        sd = statistics.pstdev(values)
        p = (1 + sum(v <= float(observed['held_bits']) + 1e-12 for v in values)) / 65
        err = max(
            abs(mean - float(observed['matched_null_mean_bits'])),
            abs(sd - float(observed['matched_null_sd_bits'])),
            abs(mean - float(observed['held_bits']) - float(observed['matched_savings_bits'])),
            abs(p - float(observed['matched_lower_tail_p'])))
        ck('null_summary_' + cid + '_' + model, err < 1e-8, err)

# Rebuild leakage aggregation and the fixed signature decision.
lmap = {(x['control_id'], x['model']): x for x in leak}
smap = {x['control_id']: x for x in sig}
fold_sum = defaultdict(float)
fold_count = defaultdict(int)
for row in leak_folds:
    key = row['control_id'], row['model']
    fold_sum[key] += float(row['held_bits'])
    fold_count[key] += 1
    ck('held_excluded_' + '|'.join(key) + '|' + row['held_folio'],
       row['held_folio_in_training'] == '0')
for cid in IDS:
    for model in MODELS:
        ck('safe_sum_' + cid + '_' + model,
           abs(fold_sum[cid, model] - float(lmap[cid, model]['lofo_safe_bits'])) < 1e-8)
        ck('safe_91_' + cid + '_' + model, fold_count[cid, model] == 91)
    abbreviation = wmap[cid, 'ABBREVIATION_HEAVY_LANGUAGE']
    compressed = wmap[cid, 'COMPRESSED_NATURAL_LANGUAGE']
    expected_signature = int(
        int(abbreviation['rank']) == 1 and
        float(abbreviation['held_bits']) < float(compressed['held_bits']) and
        float(abbreviation['matched_savings_bits']) > 0)
    ck('signature_' + cid,
       int(smap[cid]['signature_all_three']) == expected_signature)

nons = sum(int(smap[x]['signature_all_three']) for x in
           ('ARBITRARY_LOCAL_CODEBOOK', 'COMPOSITIONAL_TECHNICAL_NOTATION', 'HYBRID_SHORTHAND'))
langs = sum(int(smap[x]['signature_all_three']) for x in
            ('ORDINARY_NATURAL_LANGUAGE', 'ABBREVIATION_HEAVY_MEDIEVAL'))
if nons:
    expected_status = 'GDT276_SIGNATURE_NOT_ARCHITECTURE_SPECIFIC'
elif int(smap['VOYNICH_MATCHED_REFERENCE']['signature_all_three']) and langs:
    expected_status = 'GDT276_SIGNATURE_LANGUAGE_ABBREVIATION_SELECTIVE_IN_FROZEN_CONTROLS'
else:
    expected_status = 'GDT276_SIGNATURE_DIAGNOSTICITY_UNRESOLVED'
ck('status', result['status'] == expected_status)
ck('result_counts', result['known_nonlanguage_full_signature_count'] == nons and
   result['known_language_full_signature_count'] == langs)
ck('result_content_hash', csha({k: v for k, v in result.items()
                                if k != 'content_sha256'}) == result['content_sha256'])
for group in ('inputs', 'documents', 'implementation', 'outputs'):
    for path, digest in result[group].items():
        ck('hash_' + group + '_' + path, sha(R / path) == digest)

validation = {
    'schema': 'GDT277_SIGNATURE_CALIBRATION_VALIDATION_V1',
    'status': 'PASS_PRIMARY_INDEPENDENT_SCORE_AND_LEAKAGE_ACCOUNTING',
    'checks_passed': len(checks), 'checks_total': len(checks),
    'scope': ('Independently replays all primary observed scores from exported '
              'matched events with the byte-frozen GDT276 scorer; reconstructs '
              'all null summaries, signatures, leakage fold sums, scaffold and '
              'capacity invariants, bindings, and f84 exclusion. Fold-local '
              'parser learning itself is retained-producer audited, not '
              'independently reimplemented.'),
    'checks': checks, 'result_sha256': sha(R / 'gdt277_result.json'),
    'implementation_sha256': sha(Path(__file__))}
validation['content_sha256'] = csha(validation)
(R / 'gdt277_validation.json').write_text(
    json.dumps(validation, indent=2, sort_keys=True) + '\n')
print(json.dumps({'status': validation['status'], 'checks': len(checks)},
                 sort_keys=True))
