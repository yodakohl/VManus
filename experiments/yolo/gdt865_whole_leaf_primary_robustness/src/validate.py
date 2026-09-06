#!/usr/bin/env python3
"""Independent GDT865 membership, metric and four-deck fitting validation.

Does not import the experiment runner or the inherited scorer. Target access is
only in main validation; --controls executes synthetic, corpus-free fixtures.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.git').exists())
EXP = Path(__file__).resolve().parents[1]
MODELS = {'M01_L_TO_L': 'L', 'M02_DY_TO_DY': 'DY'}
CHANNELS = {'TOPIC': 'topic_score', 'TEMPLATE': 'template_score',
            'FORM_REGIME': 'form_score', 'SLOT_HOLE': 'slot_score',
            'NUISANCE': 'nuisance_score', 'AUGMENTED': 'augmented_score',
            'UNION_NUISANCE': 'union_nuisance_score', 'UNION_AUGMENTED': 'union_augmented_score'}
DECKS = {'topic': 'TOPIC', 'template': 'TEMPLATE', 'form': 'FORM_REGIME', 'slot': 'SLOT_HOLE'}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    return json.loads(path.read_text())


def leaf(page):
    require(isinstance(page, str) and not page.startswith('f84'), 'sealed/invalid page')
    m = re.fullmatch(r'(f[0-9]+)[rv][0-9]*', page)
    require(m is not None, 'unrecognized page selector')
    return m[1]


def face(page):
    leaf(page)
    return re.match(r'f[0-9]+[rv]', page)[0]


def auc(rows, field):
    """Tie-aware rank sum, independent of the runner pairwise implementation."""
    ordered = sorted((float(r[field]), int(r['true_label'])) for r in rows)
    require(all(y in (0, 1) and math.isfinite(s) for s, y in ordered), 'invalid label/score')
    n1 = sum(y for _, y in ordered)
    n0 = len(ordered) - n1
    if not n1 or not n0:
        return None
    ranks, i = 0.0, 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][0] == ordered[i][0]:
            j += 1
        ranks += ((i + 1 + j) / 2) * sum(y for _, y in ordered[i:j])
        i = j
    return (ranks - n1 * (n1 + 1) / 2) / (n1 * n0)


def metrics(rows, field):
    groups = defaultdict(list)
    for row in rows:
        groups[row['carrier']].append(row)
    per = {k: auc(v, field) for k, v in sorted(groups.items())}
    per = {k: v for k, v in per.items() if v is not None}
    positive = [r for r in rows if int(r['true_label']) == 1]
    negative = [r for r in rows if int(r['true_label']) == 0]
    ba = None
    if positive and negative:
        ba = (sum(1 if float(r[field]) > 0 else .5 if float(r[field]) == 0 else 0 for r in positive) / len(positive)
              + sum(1 if float(r[field]) < 0 else .5 if float(r[field]) == 0 else 0 for r in negative) / len(negative)) / 2
    cells = Counter((r['carrier'], int(r['true_label'])) for r in rows)
    losses, weights = [], []
    for r in rows:
        y = int(r['true_label']); s = min(35.0, max(-35.0, float(r[field])))
        p = 1 / (1 + math.exp(-s)); w = 1 / cells[(r['carrier'], y)]
        losses.append(w * (-y * math.log(max(p, 1e-15)) - (1-y) * math.log(max(1-p, 1e-15))))
        weights.append(w)
    return {'micro_auc': auc(rows, field),
            'carrier_macro_auc': math.fsum(per.values()) / len(per) if per else None,
            'balanced_accuracy': ba,
            'balanced_log_loss': math.fsum(losses) / math.fsum(weights) if weights else None,
            'carriers_scored': len(per),
            'carriers_auc_above_half': sum(v > .5 for v in per.values()),
            'carriers_auc_below_half': sum(v < .5 for v in per.values()),
            'per_carrier': per, 'events': len(rows),
            'positive_events': len(positive), 'negative_events': len(negative)}


def close(actual, expected, name='value'):
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and set(actual) == set(expected), name + ' keys')
        for k in expected:
            close(actual[k], expected[k], name + '/' + k)
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), name + ' list size')
        for i, v in enumerate(expected):
            close(actual[i], v, name + '/' + str(i))
    elif isinstance(expected, float):
        require(isinstance(actual, (float, int)) and math.isfinite(actual)
                and math.isclose(actual, expected, abs_tol=2e-11, rel_tol=2e-11), name + ' numeric mismatch')
    else:
        require(actual == expected, name + ' mismatch')


def fit_predict(training, testing):
    """Fresh four-deck MNB; face support is deliberately unchanged."""
    cells = Counter((e['carrier'], int(e['label'])) for e in training)
    result = {e['event_id']: {} for e in testing}
    for channel, deck in DECKS.items():
        support_c, support_f = defaultdict(set), defaultdict(set)
        for e in training:
            for f in e['features'][deck]:
                support_c[f].add(e['carrier']); support_f[f].add(e['folio'])
        vocab = {f for f in support_c if len(support_c[f]) >= 2 and len(support_f[f]) >= 2}
        counts = [defaultdict(float), defaultdict(float)]
        for e in training:
            y = int(e['label']); w = 1 / cells[(e['carrier'], y)]
            for f in set(e['features'][deck]) & vocab:
                counts[y][f] += w
        mass = [math.fsum(counts[y].values()) + .5 * len(vocab) for y in (0, 1)]
        llr = {f: math.log((counts[1][f] + .5) / mass[1])
                  - math.log((counts[0][f] + .5) / mass[0]) for f in vocab}
        for e in testing:
            known = set(e['features'][deck]) & vocab
            result[e['event_id']][channel + '_score'] = math.fsum(llr[f] for f in known) / len(known) if known else 0.0
            result[e['event_id']][channel + '_known'] = len(known)
    for values in result.values():
        values['nuisance_score'] = values['topic_score'] + values['template_score'] + values['form_score']
        values['augmented_score'] = values['nuisance_score'] + values['slot_score']
    return result


def controls():
    def r(label, score, carrier='a'):
        return {'true_label': label, 'score': score, 'carrier': carrier}
    require(auc([r(0, 0), r(1, 0)], 'score') == .5, 'tie control')
    require(auc([r(0, 0), r(1, 1)], 'score') == 1, 'ordered control')
    require(auc([r(0, 1), r(1, 0)], 'score') == 0, 'reversed control')
    require(auc([r(1, 0)], 'score') is None, 'one class control')
    require(metrics([r(0, 0), r(1, 0)], 'score')['carriers_auc_above_half'] == 0, 'tie is not direction')
    require(leaf('f102v1') == leaf('f102r1') == 'f102', 'leaf panels')
    try:
        leaf('f84r')
    except AssertionError:
        pass
    else:
        raise AssertionError('sealed prefix control')
    events = []
    for c, p in [('a', 'f1r'), ('b', 'f2r')]:
        for y in (0, 1):
            events.append({'event_id': c + str(y), 'carrier': c, 'folio': p, 'label': y,
                           'features': {deck: ['common', 'positive' if y else 'negative'] for deck in DECKS.values()}})
    scored = fit_predict(events, events)
    require(scored['a1']['nuisance_score'] > 0 > scored['a0']['nuisance_score'], 'independent NB direction')
    require(all(v['topic_known'] == 2 for v in scored.values()), 'NB vocabulary support')
    print('GDT865 independent synthetic controls PASS')


def repeat_guards(requests):
    dumped = {}
    allowed = read(ROOT / 'experiments/yolo/gdt851_primitive_tandem_raw_group_discovery/src/SPEC.json')['allowed_selectors']
    expected_sources = {
        'predictions': 'experiments/yolo/gdt808_exact_relation_slot_residual_bridge/artifacts/GDT808_HELD_PREDICTIONS.tsv',
        'atlas': 'experiments/yolo/gdt808_exact_relation_slot_residual_bridge/artifacts/GDT808_1777_CORE_EVENT_ATLAS.tsv'}
    require(len(requests) == 2 and {q['artifact_key'] for q in requests} == set(expected_sources), 'guard requests')
    for q in requests:
        key = q['artifact_key']
        require(q['source'] == expected_sources[key], 'fixed guard source')
        require(len(q['selectors']) == 179 and set(q['selectors']) == set(allowed), 'fixed guard allowance')
        require(not any(p.startswith('f84') for p in q['selectors']), 'sealed allowance')
        cmd = [str(ROOT / 'vmanus-exp'), 'query-tsv', q['source'], '--selector', 'page']
        for p in q['selectors']:
            cmd += ['--allow', p]
        cmd += ['--columns', ','.join(q['columns']), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
        done = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
        require(sum(s.startswith('GUARD_STATS ') for s in done.stderr.splitlines()) == 1, 'guard stats')
        rows = list(csv.DictReader(io.StringIO(done.stdout), delimiter='\t'))
        require(all(not r['page'].startswith('f84') for r in rows), 'sealed projection')
        if key == 'predictions':
            rows = [r for r in rows if r['model_id'] in MODELS and r['population'] == 'CORE13' and r['variant'] == 'EXACT']
        dumped[key] = rows
    return dumped


def check_features(events, atlas):
    require(len(events) == len(atlas) == 1777, '1777 source events')
    indexed = {e['event_id']: e for e in events}
    originals = {e['event_id']: e for e in atlas}
    require(len(indexed) == len(originals) == 1777 and set(indexed) == set(originals), 'unique event coverage')
    mapped = {'expanded_label': 'label', 'physical_folio': 'folio'}
    named = {'topic': 'TOPIC', 'template': 'TEMPLATE', 'form_regime': 'FORM_REGIME',
             'slot_hole': 'SLOT_HOLE', 'mask_status_audit': 'MASK_STATUS', 'raw_slot_sensitivity': 'RAW_SLOT'}
    paragraph_pages = defaultdict(set)
    for eid, e in indexed.items():
        require(e['folio'] == e['face'] == face(e['page']) and e['leaf'] == leaf(e['page']), 'leaf/face reconstruction')
        require(int(e['label']) in (0, 1), 'event label')
        paragraph_pages[e['paragraph_id']].add(e['page'])
        original = originals[eid]
        for k, v in original.items():
            if '_feature_' not in k:
                require(str(e[mapped.get(k, k)]) == v, 'old event metadata ' + eid + '/' + k)
        for prefix, deck in named.items():
            if 'features' in e:
                values = e['features'][deck]
                require(values == sorted(set(values)), 'canonical feature set')
                digest = hashlib.sha256('\n'.join(values).encode()).hexdigest()
                count = len(values)
            else:
                digest = e['feature_hashes'][prefix]
                count = e['feature_counts'][prefix]
            require(str(count) == original[prefix + '_feature_count'], 'feature count')
            require(digest == original[prefix + '_feature_sha256'], 'feature hash')
    require(all(len(pages) == 1 for pages in paragraph_pages.values()), 'event paragraph page confinement')
    require(Counter(e['axis'] for e in events) == {'L': 914, 'DY': 863}, 'axis event counts')
    return indexed


def recompute_summaries(old, new):
    output, ranges, decisions = {}, {}, {}
    for model in MODELS:
        a = [r for r in old if r['model_id'] == model]
        b = [r for r in new if r['model_id'] == model]
        lookup = {r['event_id']: r for r in a}
        output[model], ranges[model] = {}, {}
        for channel, field in CHANNELS.items():
            am, bm = metrics(a, field), metrics(b, field)
            per = {}
            for c in sorted(am['per_carrier']):
                changes = [float(r[field]) - float(lookup[r['event_id']][field]) for r in b if r['carrier'] == c]
                per[c] = {'baseline_auc': am['per_carrier'][c], 'leaf_auc': bm['per_carrier'][c],
                          'auc_delta': bm['per_carrier'][c] - am['per_carrier'][c],
                          'mean_score_change': math.fsum(changes) / len(changes),
                          'mean_absolute_score_change': math.fsum(abs(v) for v in changes) / len(changes)}
            output[model][channel] = {'baseline': am, 'leaf': bm,
                                     'delta_macro_auc': bm['carrier_macro_auc'] - am['carrier_macro_auc'],
                                     'paired_per_carrier': per}
        m = output[model]['NUISANCE']['leaf']
        require(m['carriers_scored'] == 13, 'all thirteen primary carriers scoreable')
        decisions[model] = ('PRIMARY_THRESHOLD_SURVIVES_WHOLE_LEAF_EXCLUSION'
                            if m['carrier_macro_auc'] >= .60 and m['carriers_auc_above_half'] >= 9
                            else 'PRIMARY_THRESHOLD_NOT_RETAINED')
        for channel in ('NUISANCE', 'AUGMENTED', 'SLOT_HOLE'):
            field = CHANNELS[channel]
            deletions = []
            for held in sorted({leaf(r['page']) for r in a}):
                ms = []
                for rows in (a, b):
                    m = metrics([r for r in rows if leaf(r['page']) != held], field)
                    ms.append({k: m[k] for k in ('carrier_macro_auc', 'carriers_scored', 'carriers_auc_above_half', 'per_carrier')})
                require(all(m['carrier_macro_auc'] is not None for m in ms), 'scoreable leaf deletion')
                deletions.append({'deleted_test_leaf': held, 'baseline': ms[0], 'leaf': ms[1],
                                  'delta_macro_auc': ms[1]['carrier_macro_auc'] - ms[0]['carrier_macro_auc']})
            ranges[model][channel] = {'deletions': deletions,
                'baseline_range': [min(d['baseline']['carrier_macro_auc'] for d in deletions), max(d['baseline']['carrier_macro_auc'] for d in deletions)],
                'leaf_range': [min(d['leaf']['carrier_macro_auc'] for d in deletions), max(d['leaf']['carrier_macro_auc'] for d in deletions)],
                'delta_range': [min(d['delta_macro_auc'] for d in deletions), max(d['delta_macro_auc'] for d in deletions)]}
    return output, ranges, decisions


REFIT_EVENTS = None


def refit_fold(f):
    training = [REFIT_EVENTS[eid] for eid in f['leaf_train_ids']]
    testing = [REFIT_EVENTS[eid] for eid in f['test_ids']]
    return f['model_id'], fit_predict(training, testing)


def validate(refit=False, workers=8):
    global REFIT_EVENTS
    artifacts, runtime = EXP / 'artifacts', EXP / 'runtime'
    hashes = read(artifacts / 'SOURCE_HASHES.json')
    legacy = ROOT / 'experiments/yolo/gdt808_exact_relation_slot_residual_bridge/src/run.py'
    require(hashlib.sha256(legacy.read_bytes()).hexdigest() == hashes['legacy_code_sha256'], 'legacy scorer bytes')
    dumped = repeat_guards(read(artifacts / 'GUARD_REQUESTS.json'))
    for key, name in [('predictions', 'published_predictions'), ('atlas', 'event_atlas')]:
        payload = json.dumps(dumped[key], sort_keys=True, separators=(',', ':')) + '\n'
        require(hashlib.sha256(payload.encode()).hexdigest() == hashes['guarded_projection_sha256'][name], 'fresh guarded digest')
    events = read(artifacts / 'EVENT_METADATA.json')
    indexed = check_features(events, dumped['atlas'])
    old, new = (read(artifacts / name) for name in ('BASELINE_PREDICTIONS.json', 'LEAF_PREDICTIONS.json'))
    op, np = ({r['prediction_id']: r for r in rows} for rows in (old, new))
    originals = {r['prediction_id']: r for r in dumped['predictions']}
    require(len(old) == len(new) == len(op) == len(np) == len(originals) == 1777, 'paired prediction cardinality')
    require(set(op) == set(np) == set(originals), 'paired prediction coverage')
    score_fields = [k for k in next(iter(originals.values())) if k.endswith(('_score', '_known'))]
    require(len(score_fields) == 25, 'all old score and known fields projected')
    for pid, row in op.items():
        require({k: str(v) for k, v in row.items()} == originals[pid], 'published serialized full-row parity ' + pid)
        require(set(row) == set(np[pid]), 'prediction schema parity')
        require(all(row[k] == np[pid][k] for k in row if k not in score_fields), 'paired metadata parity')
        e = indexed[row['event_id']]
        require(row['model_id'] in MODELS and MODELS[row['model_id']] == e['axis'], 'model event axis')
        require(int(row['true_label']) == int(e['label']) and row['carrier'] == e['carrier'], 'prediction event label/carrier')
        require(row['page'] == e['page'] and row['physical_folio'] == e['folio'], 'prediction event page')
    folds = read(artifacts / 'FOLDS.json')
    require(len(folds) == 963, '963 folds')
    expected_keys = {(model, e['carrier'], e['folio']) for model, axis in MODELS.items() for e in events if e['axis'] == axis}
    require(len(expected_keys) == len(folds) and {(f['model_id'], f['held_carrier'], f['held_face']) for f in folds} == expected_keys, 'fold coverage')
    require(Counter(f['model_id'] for f in folds) == {'M01_L_TO_L': 569, 'M02_DY_TO_DY': 394}, 'model fold counts')
    seen, unchanged = Counter(), 0
    for f in folds:
        axis = MODELS[f['model_id']]; c, facekey = f['held_carrier'], f['held_face']
        require(f['held_leaf'] == leaf(facekey), 'held leaf key')
        source = [e for e in events if e['axis'] == axis]
        baseline = [e for e in source if e['carrier'] != c and e['folio'] != facekey]
        whole = [e for e in source if e['carrier'] != c and leaf(e['page']) != leaf(facekey)]
        test = [e for e in source if e['carrier'] == c and e['folio'] == facekey]
        for key, values in (('baseline_train', baseline), ('leaf_train', whole), ('test', test)):
            ids = [e['event_id'] for e in values]
            if key == 'test':
                require(len(f['test_ids']) == len(ids) and set(f['test_ids']) == set(ids), 'test exact membership')
            else:
                payload = json.dumps(ids, sort_keys=True, separators=(',', ':')) + '\n'
                require(f[key + '_ids_sha256'] == hashlib.sha256(payload.encode()).hexdigest(), key + ' membership digest')
                f[key + '_ids'] = ids
            require(f[key + '_count'] == len(values), key + ' count')
        require({int(e['label']) for e in whole} == {0, 1} and len({e['carrier'] for e in whole}) == 12, 'whole-leaf fold capacity')
        require(f['leaf_train_carriers'] == 12 and f['leaf_train_classes'] == [0, 1], 'capacity audit parity')
        require(f['carrier_excluded'] is True and f['whole_leaf_excluded'] is True, 'exclusion audit flags')
        same = len(whole) == len(baseline)
        require(f['unchanged'] == same, 'unchanged membership flag')
        unchanged += same
        for e in test:
            pid = f['model_id'] + ':' + e['event_id']; seen[pid] += 1
            if same:
                require(op[pid] == np[pid], 'unchanged fold exact all-field parity')
    require(unchanged == 108 and set(seen) == set(op) and set(seen.values()) == {1}, '108 unchanged / test once coverage')
    expected_metrics, expected_ranges, decisions = recompute_summaries(old, new)
    close(read(artifacts / 'METRICS.json'), expected_metrics, 'metrics')
    close(read(artifacts / 'LEAF_DELETE_RANGES.json'), expected_ranges, 'leaf deletion ranges')
    result = read(artifacts / 'RESULT.json')
    require(result['status'] == 'COMPLETE_PRIMARY_WHOLE_LEAF_ROBUSTNESS_AUDIT', 'complete status')
    require(result['axis_decisions'] == decisions, 'independent decisions')
    require(result['events'] == 1777 and result['folds'] == 963 and result['unchanged_folds'] == 108 and result['baseline_serialized_parity'] is True, 'result counts')
    require(read(artifacts / 'BASELINE_CHECK.json')['status'] == 'PASS', 'baseline status')
    if refit:
        import concurrent.futures
        import multiprocessing
        feature_events = read(runtime / 'EVENT_FEATURES.json')
        REFIT_EVENTS = check_features(feature_events, dumped['atlas'])
        require([e['event_id'] for e in feature_events] == [e['event_id'] for e in events], 'runtime event order parity')
        with concurrent.futures.ProcessPoolExecutor(max_workers=max(1, min(32, workers)), mp_context=multiprocessing.get_context('fork')) as pool:
            for model, values in pool.map(refit_fold, folds, chunksize=1):
                for eid, scores in values.items():
                    row = np[model + ':' + eid]
                    for field, value in scores.items():
                        if field.endswith('_known'):
                            require(row[field] == value, 'independent refit known features')
                        else:
                            close(float(row[field]), value, 'independent refit ' + model + ':' + eid + '/' + field)
    print(json.dumps({'status': 'PASS', 'events': 1777, 'folds': 963, 'unchanged_folds': 108,
                      'independent_four_deck_refit': refit, 'axis_decisions': decisions,
                      'claim': 'RETROSPECTIVE_PRIMARY_THRESHOLDS_ONLY_NO_NULL_OR_SEMANTIC_CREDIT'}, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--controls', action='store_true')
    ap.add_argument('--refit', action='store_true', help='Independently refit four primary decks for all 963 leaf folds.')
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--no-write', action='store_true', help='Compatibility flag; this validator always writes only stdout.')
    args = ap.parse_args()
    if args.controls:
        controls()
    else:
        validate(args.refit, args.workers)


if __name__ == '__main__':
    main()
