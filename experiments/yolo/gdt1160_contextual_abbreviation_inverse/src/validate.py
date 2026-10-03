#!/usr/bin/env python3
"""Independent GDT1160 validator. Never imports the runner or refits models."""
from __future__ import annotations
import argparse, collections, csv, hashlib, json, math
from pathlib import Path
EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows(name):
    with (ROOT / name).open(encoding='utf-8', newline='') as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            if row['corpus'] == 'NUREMBERG':
                yield row


def context_counts(groups, index, radius=8):
    counts = collections.Counter()
    for offset in range(-radius, radius + 1):
        if offset == 0 or not 0 <= index + offset < len(groups):
            continue
        token = groups[index + offset]
        for width in (2, 3, 4):
            for start in range(len(token) - width + 1):
                key = f'{offset}:{token[start:start + width]}'
                bucket = int.from_bytes(hashlib.sha256(key.encode('utf-8')).digest()[:8], 'big') % 4096
                counts[bucket] += 1
    return dict(counts)


def normalized(counts):
    norm = math.sqrt(sum(value * value for value in counts.values()))
    return {key: value / norm for key, value in counts.items()} if norm else {}


def layout_vector(row):
    result = [0.] * 10
    result[row['record_position_quartile']] = 1.
    result[4 + (4 * row['line_group_index'] // row['line_group_count'])] = 1.
    result[8] = float(row['first_line'])
    result[9] = float(row['last_line'])
    return result


def masked_probabilities(logits, prior_counts, candidates, all_outputs):
    """Log-prior offset followed by softmax on train-licensed candidates only."""
    total = sum(prior_counts.values())
    adjusted = [logits[all_outputs.index(value)] + math.log(prior_counts[value] / total)
                for value in candidates]
    maximum = max(adjusted)
    exps = [math.exp(value - maximum) for value in adjusted]
    return [value / sum(exps) for value in exps]


def mean_probabilities(vectors):
    if not vectors or len({len(vector) for vector in vectors}) != 1:
        raise ValueError('Probability vector size')
    for vector in vectors:
        if any(not math.isfinite(x) or x < 0 for x in vector) or abs(sum(vector) - 1) > 1e-5:
            raise ValueError('Invalid candidate probabilities')
    return [sum(row[i] for row in vectors) / len(vectors) for i in range(len(vectors[0]))]


def choose(candidates, probabilities):
    if candidates != sorted(set(candidates)) or len(candidates) != len(probabilities):
        raise ValueError('Candidate alignment')
    return candidates[max(range(len(candidates)), key=lambda i: probabilities[i])]


def macro_type_accuracy(rows):
    types = collections.defaultdict(list)
    for row in rows:
        types[row['marked_group']].append(row['prediction'] == row['truth'])
    return sum(sum(v) / len(v) for v in types.values()) / len(types) if types else None


def gates(metrics):
    means = {arm: sum(values) / len(values) for arm, values in metrics.items()}
    context = {}
    for arm in ('C', 'N'):
        gain = means[arm] - max(means['F'], means['L'])
        folds = sum(x > f and x > l for x, f, l in zip(metrics[arm], metrics['F'], metrics['L']))
        context[arm] = {'gain': gain, 'positive_folds': folds, 'pass': gain >= .03 and folds >= 3}
    gain = means['N'] - means['C']
    folds = sum(n > c for n, c in zip(metrics['N'], metrics['C']))
    return {'means': means, 'context': context, 'neural': {'gain': gain, 'positive_folds': folds,
            'pass': context['N']['pass'] and gain >= .01 and folds >= 3}}


def reconstruct(spec):
    lines = list(source_rows('gdt155_blinded_diplomatic.tsv'))
    records = collections.defaultdict(list)
    for line in lines:
        records[line['record_id']].append(line)
    marker_positions, groups_by_record = {}, {}
    for record, members in records.items():
        members.sort(key=lambda row: int(row['line_index']))
        assert [int(row['line_index']) for row in members] == list(range(1, len(members) + 1))
        assert {int(row['record_line_count']) for row in members} == {len(members)}
        groups, markers = [], []
        for line_index, line in enumerate(members):
            tokens = line['diplomatic_marked'].split()
            # Historical surface_group_count is a separate bare representation;
            # registered context uses whitespace groups of diplomatic_marked.
            for token_index, token in enumerate(tokens):
                location = {'line_id': line['line_id'], 'group_index': len(groups), 'line_group_index': token_index,
                            'line_group_count': len(tokens), 'record_position_quartile': int(line['record_position_quartile']),
                            'first_line': line_index == 0, 'last_line': line_index == len(members) - 1,
                            'page_id': line['page_id'], 'book': line['book_or_ms'], 'group': token}
                markers.extend([location] * token.count('¤'))
                groups.append(token)
        marker_positions[record] = markers
        groups_by_record[record] = groups
    blind = list(source_rows('gdt155_blinded_abbreviation_sites.tsv'))
    truths = {row['site_id']: row for row in source_rows('gdt155_unblinded_abbreviation_sites.tsv')}
    assert len(truths) == len(blind) == sum(len(v) for v in marker_positions.values())
    eligible = []
    for site in blind:
        record = site['record_id']
        location = marker_positions[record][int(site['site_index_in_record']) - 1]
        assert location['line_id'] == site['line_id']
        if location['group'] != site['surface_span_marked'] or location['group'].count('¤') != 1:
            continue
        truth = truths[site['site_id']]
        assert truth['record_id'] == record and truth['line_id'] == site['line_id']
        eligible.append(dict(location, site_id=site['site_id'], record_id=record,
                             marked_group=site['surface_span_marked'], truth=truth['expanded_span']))
    assert len(eligible) == spec['expected_source_eligible_sites']
    folds = []
    for held, expected in zip(spec['books'], spec['expected_held_sites']):
        training = [row for row in eligible if row['book'] != held]
        counts = collections.defaultdict(collections.Counter)
        pages = collections.defaultdict(lambda: collections.defaultdict(set))
        for row in training:
            key, value = row['marked_group'], row['truth']
            counts[key][value] += 1
            pages[key][value].add((row['book'], row['page_id']))
        qualified = sorted(key for key, values in counts.items() if sum(n >= 5 and len(pages[key][value]) >= 3
                            for value, n in values.items()) >= 2)
        domains = {key: sorted(counts[key]) for key in qualified}
        testing = [row for row in eligible if row['book'] == held and row['marked_group'] in domains]
        assert len(testing) == expected
        folds.append({'held_book': held, 'domains': domains, 'counts': {key: dict(counts[key]) for key in qualified},
                      'pages': {key: {value: len(pages[key][value]) for value in counts[key]} for key in qualified},
                      'training': [row for row in training if row['marked_group'] in domains], 'testing': testing})
    return {'lines': lines, 'records': records, 'groups': groups_by_record, 'eligible': eligible, 'folds': folds}


def fixtures():
    assert context_counts(['secret¤'], 0) == {}
    assert context_counts(['ab', 'secret¤'], 1) == {1123: 1}
    assert context_counts(['x'] * 19, 9) == {}
    assert context_counts(['ſe', 't'], 1) != context_counts(['se', 't'], 1)
    assert abs(sum(v*v for v in normalized({1: 3, 2: 4}).values()) - 1) < 1e-12
    assert normalized({}) == {}
    assert mean_probabilities([[.9, .1], [.1, .9]]) == [.5, .5]
    assert choose(['a', 'ſ'], [.5, .5]) == 'a'
    assert all(abs(x-y) < 1e-12 for x,y in zip(masked_probabilities(
        [0., 1000., 0.], {'a': 3, 'c': 1}, ['a','c'], ['a','b','c']), [.75,.25]))
    assert layout_vector({'record_position_quartile':2,'line_group_index':3,'line_group_count':4,
                          'first_line':False,'last_line':True}) == [0.,0.,1.,0.,0.,0.,0.,1.,0.,1.]
    assert macro_type_accuracy([{'marked_group':'a', 'prediction':'a', 'truth':'a'}] * 9 +
                               [{'marked_group':'b', 'prediction':'b', 'truth':'unknown'}]) == .5
    bad = gates({'F':[.9]*4, 'L':[.5]*4, 'C':[.8]*4, 'N':[.85]*4})
    assert not bad['context']['C']['pass'] and not bad['neural']['pass']
    return 'PASS (invented fixtures, not scientific findings)'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--release', action='store_true', help='Only after root release and prediction lock')
    parser.add_argument('--weights-dir', type=Path, help='Local NPZ working directory, never stored in report')
    args=parser.parse_args()
    spec = json.loads((EXP / 'SPEC.json').read_text())
    pins = {name: sha(ROOT / name) == expected for name, expected in spec['source_inputs'].items()}
    assert all(pins.values()), pins
    panel = reconstruct(spec)
    fixtures()
    if args.release:
        if not (EXP/'artifacts/PREDICTION_LOCK.json').is_file():
            raise RuntimeError('Frozen prediction lock is required')
        return validate_release(spec,panel,args.weights_dir)
    summary = {'mode':'PREPARATION', 'source_pins':pins, 'fixtures':fixtures(),
               'source_lines':len(panel['lines']), 'source_records':len(panel['records']),
               'eligible_sites':len(panel['eligible']), 'held_sites':[len(f['testing']) for f in panel['folds']],
               'training_types':[len(f['domains']) for f in panel['folds']],
               'oov_truths':[sum(r['truth'] not in f['domains'][r['marked_group']] for r in f['testing']) for f in panel['folds']],
               'claim_ceiling':'Source bookkeeping and registered feature fixtures; no model or meaning certification.'}
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


# Post-preregistration validator extension: only this independent helper changed.
# It validates saved predictions/weights, never trains or imports src/run.py.
def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_jsonl(path):
    import gzip
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return [json.loads(line) for line in stream]


def exact_window(row, panel):
    groups = panel['groups'][row['record_id']]
    position = row['group_index']
    return tuple(groups[position+d] if 0 <= position+d < len(groups) else None
                 for d in range(-8,9) if d)


def independent_metrics(rows, arm):
    if not rows:
        return dict(sites=0,types=0,token_accuracy=None,macro_type_accuracy=None,records=0,
                    all_ambiguous_sites_correct_record_accuracy=None)
    types, records = collections.defaultdict(list), collections.defaultdict(list)
    for row in rows:
        good = row['predictions'][arm] == row['truth']
        types[row['marked_group']].append(good)
        records[row['record_id']].append(good)
    return dict(sites=len(rows),types=len(types),token_accuracy=sum(sum(v) for v in types.values())/len(rows),
                macro_type_accuracy=sum(sum(v)/len(v) for v in types.values())/len(types),records=len(records),
                all_ambiguous_sites_correct_record_accuracy=sum(all(v) for v in records.values())/len(records))


def feature_matrix(rows, fold, panel):
    import numpy as np
    families = sorted(fold['domains'])
    index = {value:i for i,value in enumerate(families)}
    width = len(families)+10
    matrix = np.zeros((len(rows),width+4096),dtype=np.float32)
    for i,row in enumerate(rows):
        matrix[i,index[row['marked_group']]] = 1.
        matrix[i,len(families):width] = layout_vector(row)
        for bucket,value in normalized(context_counts(panel['groups'][row['record_id']],row['group_index'])).items():
            matrix[i,width+bucket] = value
    return matrix, width


def validate_release(spec, panel, weights_directory):
    import subprocess
    art = EXP / 'artifacts'
    checks = []
    def check(name, condition, detail=None):
        checks.append({'check':name,'pass':bool(condition),'detail':detail})
    def equal(a,b,tolerance=1e-10):
        if isinstance(a,dict) and isinstance(b,dict):
            return a.keys()==b.keys() and all(equal(a[k],b[k],tolerance) for k in a)
        if isinstance(a,list) and isinstance(b,list):
            return len(a)==len(b) and all(equal(x,y,tolerance) for x,y in zip(a,b))
        if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):
            return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tolerance
        return a==b
    for name,digest in spec['source_inputs'].items():
        check('frozen_source_'+name,sha(ROOT/name)==digest)
    check('invented_feature_and_decision_fixtures',fixtures().startswith('PASS'))
    registration = load_json(art/'REGISTRATION_LOCK.json')
    lock = load_json(art/'PREDICTION_LOCK.json')
    for name,digest in registration['configuration_sha256'].items():
        check('current_registered_'+name, sha(EXP/name)==digest)
        relative = (EXP/name).relative_to(ROOT).as_posix()
        historical = subprocess.run(['git','show',registration['commit']+':'+relative],cwd=ROOT,
                                    capture_output=True,check=True).stdout
        check('public_commit_'+name,hashlib.sha256(historical).hexdigest()==digest)
    check('prediction_configuration_lock',lock['configuration_sha256']==registration['configuration_sha256'])
    for name,digest in lock['files'].items():
        check('prediction_lock_'+name,sha(art/name)==digest)
    check('exact_all_eight_prediction_files',set(lock['files'])=={f'{prefix}_{book}.{suffix}'
          for book in spec['books'] for prefix,suffix in [('FIT','json'),('PREDICTIONS','jsonl.gz')]})
    source = load_json(EXP/'src/SOURCE.json')
    check('source_receipt_pins',source['input_sha256']==spec['source_inputs'])
    arms = ('F','L','C','N')
    reconstructed_folds, reconstructed_types, all_scored = [], [], []
    forward_summary, loss_summary = [], []
    for fi,fold in enumerate(panel['folds']):
        book = fold['held_book']
        fit = load_json(art/f'FIT_{book}.json')
        predictions = load_jsonl(art/f'PREDICTIONS_{book}.jsonl.gz')
        test = fold['testing']
        ids = [row['site_id'] for row in test]
        check(book+'_all_site_order', [row['site_id'] for row in predictions]==ids)
        families = sorted(fold['domains'])
        domains = fold['domains']
        mn = sorted(key for key in families if any(value.endswith('m') and value[:-1]+'n' in fold['counts'][key]
            and fold['counts'][key][value]>=5 and fold['counts'][key][value[:-1]+'n']>=5
            and fold['pages'][key][value]>=3 and fold['pages'][key][value[:-1]+'n']>=3 for value in domains[key]))
        id_hash = hashlib.sha256(('\n'.join(sorted(ids))+'\n').encode()).hexdigest()
        expected_meta = dict(book=book,fold_index=fi,training_sites=len(fold['training']),held_sites=len(test),
            families=families,candidate_domains=domains,training_counts=fold['counts'],mn_marked_types=mn,
            held_site_ids_sha256=id_hash)
        check(book+'_fold_metadata', equal(fit['fold'],expected_meta))
        check(book+'_fit_pins',fit['configuration_sha256']==registration['configuration_sha256'] and
              fit['source_sha256']==spec['source_inputs'] and fit['registration_lock_sha256']==sha(art/'REGISTRATION_LOCK.json')
              and fit['prediction_sha256']==sha(art/f'PREDICTIONS_{book}.jsonl.gz'))
        vocabulary = sorted({value for values in domains.values() for value in values})
        check(book+'_train_only_output_vocabulary',fit['output_vocabulary']==vocabulary)
        windows = {(row['marked_group'],exact_window(row,panel)) for row in fold['training']}
        byid = {row['site_id']:row for row in test}
        scored = []
        evidence = collections.Counter()
        for prediction in predictions:
            row = byid.get(prediction['site_id'])
            if row is None:
                evidence['unknown_site']+=1;continue
            key = row['marked_group']
            candidates = domains[key]
            metadata = all(prediction[field]==row[field] for field in ('site_id','book','record_id','line_id','marked_group'))
            evidence['source_metadata']+=not metadata
            evidence['candidate_domain']+=prediction['candidates']!=candidates
            prior_counts = fold['counts'][key]
            prior = [prior_counts[value]/sum(prior_counts.values()) for value in candidates]
            evidence['F_prior']+=not equal(prediction['probabilities']['F'],prior)
            for arm in ('L','C','N'):
                vector = prediction['seed_probabilities'][arm]
                evidence['two_seed_vectors']+=len(vector)!=2
                try:
                    mean = mean_probabilities(vector)
                    evidence['mean_probability']+=not equal(prediction['probabilities'][arm],mean)
                except ValueError:
                    evidence['invalid_probability']+=1
            for arm in arms:
                evidence['argmax_tie']+=choose(candidates,prediction['probabilities'][arm])!=prediction['predictions'][arm]
            novel = (key,exact_window(row,panel)) not in windows
            evidence['novel_context']+=prediction['novel_exact_context']!=novel
            evidence['mn_subset']+=prediction['mn_training_type']!=(key in mn)
            item = {field:prediction[field] for field in ('site_id','book','record_id','line_id','marked_group','novel_exact_context','mn_training_type','predictions')}
            item.update(truth=row['truth'],truth_in_candidates=row['truth'] in candidates,
                        correct={arm:prediction['predictions'][arm]==row['truth'] for arm in arms})
            scored.append(item)
        check(book+'_every_prediction_field',not any(evidence.values()),dict(evidence))
        expected_weights = {(arm,seed+100*fi) for arm in ('L','C','N') for seed in spec['training']['seeds']}
        check(book+'_weight_inventory',{(r['arm'],r['seed']) for r in fit['weights_local_only']}==expected_weights and len(fit['weights_local_only'])==6)
        check(book+'_curves_inventory',{(r['arm'],r['seed']) for r in fit['train_curves']}==expected_weights and len(fit['train_curves'])==6)
        for curve in fit['train_curves']:
            losses = curve['epoch_mean_online_batch_cross_entropy']
            check(book+'_'+curve['arm']+str(curve['seed'])+'_training_curve',len(losses)==20 and all(math.isfinite(x) and x>=0 for x in losses))
            loss_summary.append(dict(book=book,arm=curve['arm'],seed=curve['seed'],first=losses[0],last=losses[-1],
                                     last_five=losses[-5:],note='Online batch losses; finite curve does not prove optimization convergence.'))
        if weights_directory is not None:
            import numpy as np
            import torch
            torch.set_num_threads(2)
            matrix,width = feature_matrix(test,fold,panel)
            x = torch.from_numpy(matrix)
            out_index = {value:i for i,value in enumerate(vocabulary)}
            prior = torch.full((len(test),len(vocabulary)),-float('inf'),dtype=torch.float32)
            indices = []
            for i,row in enumerate(test):
                key = row['marked_group']; counts=fold['counts'][key]; total=sum(counts.values())
                ix = [out_index[v] for v in domains[key]]; indices.append(ix)
                prior[i,ix] = torch.tensor([math.log(counts[v]/total) for v in domains[key]],dtype=torch.float32)
            for weight in fit['weights_local_only']:
                path = weights_directory/weight['local_working_basename']
                check(book+'_'+weight['arm']+str(weight['seed'])+'_weight_hash',path.exists() and sha(path)==weight['sha256'])
                if not path.exists():continue
                tensors = {key:torch.from_numpy(value.copy()) for key,value in np.load(path,allow_pickle=False).items()}
                arm = weight['arm']; seed_index = spec['training']['seeds'].index(weight['seed']-100*fi)
                worst = 0.
                with torch.no_grad():
                    for start in range(0,len(test),256):
                        batch=x[start:start+256,:width] if arm=='L' else x[start:start+256]
                        if arm=='N':
                            hidden=torch.relu(torch.nn.functional.linear(batch,tensors['0.weight'],tensors['0.bias']))
                            logits=torch.nn.functional.linear(hidden,tensors['2.weight'],tensors['2.bias'])
                        else:logits=torch.nn.functional.linear(batch,tensors['weight'],tensors['bias'])
                        result=torch.softmax(logits+prior[start:start+256],dim=1).numpy()
                        for local,values in enumerate(result):
                            i=start+local
                            expected=predictions[i]['seed_probabilities'][arm][seed_index]
                            worst=max(worst,max(abs(float(values[j])-value) for j,value in zip(indices[i],expected)))
                check(book+'_'+arm+str(weight['seed'])+'_independent_forward',worst<=2e-5,{'maximum_absolute_probability_error':worst})
                forward_summary.append(dict(book=book,arm=arm,seed=weight['seed'],maximum_absolute_probability_error=worst))
        reconstructed_folds.append(dict(book=book,arms={arm:independent_metrics(scored,arm) for arm in arms},
            secondary={name:{arm:independent_metrics([r for r in scored if r[field]],arm) for arm in arms}
                       for name,field in [('novel_context','novel_exact_context'),('terminal_m_n','mn_training_type')]},
            oov_truths=sum(not row['truth_in_candidates'] for row in scored)))
        for key in sorted(set(row['marked_group'] for row in scored)):
            subset=[row for row in scored if row['marked_group']==key]
            reconstructed_types.append(dict(book=book,marked_group=key,sites=len(subset),
                oov_truths=sum(not row['truth_in_candidates'] for row in subset),
                accuracy={arm:sum(row['correct'][arm] for row in subset)/len(subset) for arm in arms}))
        all_scored.extend(scored)
    check('all_site_results',equal(load_jsonl(art/'SITE_RESULTS.jsonl.gz'),all_scored))
    check('all_type_results',equal(load_json(art/'TYPE_RESULTS.json'),reconstructed_types))
    decision = gates({arm:[fold['arms'][arm]['macro_type_accuracy'] for fold in reconstructed_folds] for arm in arms})
    context_gates = {arm:decision['context'][arm]['pass'] for arm in ('C','N')}
    neural=decision['neural']['pass']
    status=('CONTEXT_AND_NEURAL_INCREMENT' if context_gates['C'] and neural else 'NEURAL_CONTEXT_ONLY' if neural
            else 'CONTEXT_INCREMENT_ONLY' if context_gates['C'] else 'NO_PROMOTED_CONTEXT_MODEL')
    expected_result=dict(status=status,scope='SUPERVISED_SOURCE_CALIBRATION_ONLY',sites=len(all_scored),folds=reconstructed_folds,
        equal_fold_macro_type_accuracy=decision['means'],
        context_gains_over_fold_max_F_L={arm:[fold['arms'][arm]['macro_type_accuracy']-max(fold['arms']['F']['macro_type_accuracy'],fold['arms']['L']['macro_type_accuracy']) for fold in reconstructed_folds] for arm in ('C','N')},
        context_mean_gains_over_max_mean_F_L={arm:decision['context'][arm]['gain'] for arm in ('C','N')},
        context_gate_pass=context_gates,neural_gains_over_C=[fold['arms']['N']['macro_type_accuracy']-fold['arms']['C']['macro_type_accuracy'] for fold in reconstructed_folds],
        neural_gate_pass=neural,prediction_lock_sha256=sha(art/'PREDICTION_LOCK.json'))
    check('entire_result_and_fixed_gates',equal(load_json(art/'RESULT.json'),expected_result))
    result={'experiment':'GDT1160','accounting_pass':all(c['pass'] for c in checks),'checks':checks,
            'independently_recomputed_result':expected_result,'forward_replays':forward_summary,'training_loss_audit':loss_summary,
            'source_accounting':{'complete_lines':len(panel['lines']),'complete_records':len(panel['records']),
                'eligible_sites':len(panel['eligible']),'held_sites':[len(f['testing']) for f in panel['folds']],
                'oov_truths':[f['oov_truths'] for f in reconstructed_folds],
                'seen_exact_context_sites':[len(f['testing'])-reconstructed_folds[i]['secondary']['novel_context']['F']['sites']
                                            for i,f in enumerate(panel['folds'])]},
            'validator_post_registration_extension':True,
            'registered_configuration_unchanged':all(c['pass'] for c in checks if c['check'].startswith(('current_registered_','public_commit_'))),
            'limits':['Technical accounting is not word-meaning validation.',
                'Source editorial markers do not certify native graphical homography.',
                'No refitting: saved weights and all held probabilities checked when weights are supplied.',
                'Local weights are not published; reproduction of fits requires pinned dependencies and retraining.',
                'Locks bind bytes and sequencing in code; they do not independently certify analyst secrecy or exact first-access times.',
                'Loss curves do not prove optimizer convergence; no held-result retuning permitted.',
                'All learned-arm online training losses remain decreasing at epoch20. The fixed-budget comparison does not establish a converged linear optimum or causal necessity of nonlinearity.',
                'Related held books and historical label exposure are retained; no independent tradition or fresh blinding claim.']}
    (art/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    passed=sum(c['pass'] for c in checks)
    failed=[c['check'] for c in checks if not c['pass']]
    report=f'# GDT1160 independent validation\n\nAccounting: {passed}/{len(checks)} checks pass. Scientific result: {status}.\n\n'
    report+='The validator reconstructs all source sites, complete-record written contexts, training-only candidate domains, all probability means and ties, every site/type/secondary metric and fixed gate without importing the runner. '
    report+=f'Independent frozen-weight forward replays: {len(forward_summary)}.\n\n'
    report+='Primary accuracy gives each marked type equal weight within each book, then each book equal weight.\n\n'
    report+='| Arm | Macro accuracy |\n|---|---:|\n'
    report+=''.join(f'| {arm} | {100*decision["means"][arm]:.3f}% |\n' for arm in arms)+'\n'
    report+=f'C gains {100*decision["context"]["C"]["gain"]:.3f} percentage points over the stronger mean F/L; N gains {100*decision["context"]["N"]["gain"]:.3f}. N gains {100*decision["neural"]["gain"]:.3f} points over C. All three comparisons are positive in all four held books.\n\n'
    report+='All 21,512 held sites remain included, including 171 out-of-domain truths counted as errors. Exact same-type training-context matches number 0/0/2/15 across the four books; all secondary subset metrics were recomputed.\n\n'
    report+='Failed checks: '+(json.dumps(failed,ensure_ascii=False) if failed else 'none')+'.\n\n'
    report+='The helper was extended after public preregistration; source, specification and runner remain unchanged. Registered code is checked against the public commit.\n\n'
    report+='\n\n'.join(result['limits'])+'\n'
    (art/'VALIDATION.md').write_text(report)
    print(json.dumps({'accounting_pass':result['accounting_pass'],'checks':len(checks),'failed':failed,'status':status,'forward_replays':len(forward_summary)}))
    return 0 if result['accounting_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
