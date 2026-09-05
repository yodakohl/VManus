#!/usr/bin/env python3
"""Frozen paired-reference evaluation; preserve original u/v gold distinctions."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

SRC = Path(__file__).resolve().parent
BASE = SRC.parent
ROOT = BASE.parents[2]
CONDITIONS = ('NATIVE', 'COLLAPSED')


def check(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, value, checking=False):
    raw = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)+'\n').encode()
    if checking:
        check(Path(path).read_bytes() == raw, 'Result artifact replay')
    else:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(raw)


def reference_module():
    path = ROOT/'experiments/yolo/gdt832_joint_family_context_control/src/reference_model.py'
    spec = importlib.util.spec_from_file_location('gdt832_frozen_reference_model', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=100000)
def edit_distance(a, b):
    if a == b:
        return 0
    row = list(range(len(b)+1))
    for i, left in enumerate(a, 1):
        previous, row = row, [i]
        for j, right in enumerate(b, 1):
            row.append(min(previous[j]+1, row[-1]+1, previous[j-1]+int(left != right)))
    return row[-1]


def word_metrics(pairs):
    matches = sum(gold == pred for gold,pred in pairs)
    edits = sum(edit_distance(gold,pred) for gold,pred in pairs)
    denominator = sum(max(len(gold),len(pred)) for gold,pred in pairs)
    types = defaultdict(list)
    for gold,pred in pairs:
        types[gold].append(gold == pred)
    return {'words':len(pairs), 'exact_words':matches,
            'word_accuracy':matches/len(pairs) if pairs else None,
            'edit_distance':edits, 'character_denominator':denominator,
            'character_accuracy':1-edits/denominator if denominator else None,
            'truth_types':len(types), 'fully_correct_truth_types':sum(all(v) for v in types.values()),
            'truth_type_accuracy':sum(all(v) for v in types.values())/len(types) if types else None}


def swap_vz(key):
    v = [code for code,value in key.items() if code.startswith('L') and value == 'v']
    z = [code for code,value in key.items() if code.startswith('L') and value == 'z']
    check(len(v) == len(z) == 1, 'Unique literal v and z outputs required for legal mutant')
    changed = dict(key)
    changed[v[0]],changed[z[0]] = changed[z[0]],changed[v[0]]
    check(len({value for code,value in changed.items() if code.startswith('L')}) ==
          len({value for code,value in key.items() if code.startswith('L')}), 'Mutant preserves literal bijection')
    return changed


def reference_pair_check(data):
    native = [json.loads(line) for line in (data/'prepared/reference_native.jsonl').read_text().splitlines()]
    collapsed = [json.loads(line) for line in (data/'prepared/reference_collapsed.jsonl').read_text().splitlines()]
    check(len(native) == len(collapsed), 'Same reference sentence inventory')
    check([[word.replace('v','u') for word in row] for row in native] == collapsed,
          'Only reference v-to-u transformation allowed')
    n = sum(len(row) for row in native)
    v = sum(word.count('v') for row in native for word in row)
    check(v > 0, 'Native reference needs observed v support')
    check(not any('v' in word for row in collapsed for word in row), 'Collapsed reference has no v')
    frequencies = Counter(word for row in native for word in row)
    candidates = read_json(data/'prepared/candidates.json')
    pool = sorted((w for w in frequencies if 2 <= len(w) <= 10), key=lambda w:(-frequencies[w],w))[:128]
    check(candidates['wholeword_pool'] == pool, 'Shared wholeword candidates derive from native reference only')
    return {'reference_sentences':len(native), 'reference_words':n,
            'native_v_characters':v, 'collapsed_v_characters':0,
            'only_reference_spelling_changed':True}


def legal_key(key, candidates):
    expected = {f'{kind}{i:02d}' for kind,n in [('L',26),('S',4),('W',8)] for i in range(n)}
    check(set(key) == expected, 'Complete typed key')
    for kind,pool in [('L',set('abcdefghijklmnopqrstuvwxyz')),('S',set(candidates['suffix_pool'])),('W',set(candidates['wholeword_pool']))]:
        values = [value for code,value in key.items() if code.startswith(kind)]
        check(set(values) <= pool and len(set(values)) == len(values), 'Same legal injective key space')


def locked_fits(data, spec):
    registration = read_json(SRC/'PREREG_LOCK.json')
    for relative,digest in registration['sha256'].items():
        path = (BASE/relative).resolve()
        check(path.is_relative_to(BASE) and sha(path) == digest, 'Registered local input')
    for relative,digest in registration['upstream_sha256'].items():
        path = (ROOT/relative).resolve()
        check(path.is_relative_to(ROOT) and sha(path) == digest, 'Frozen upstream implementation')
    lock = read_json(BASE/'artifacts/FIT_LOCK.json')
    check(lock['spec_sha256'] == sha(SRC/'SPEC.json'), 'Frozen specification')
    check(len(lock['restarts']) == 48 and len(lock['selected']) == 6, 'Complete 48+6 fit freeze before truth')
    check(set(lock['restarts']+lock['selected']) <= set(lock['sha256']), 'All fit files hash-bound')
    for relative,digest in lock['sha256'].items():
        path = (BASE/relative).resolve()
        check(path.is_relative_to(BASE) and sha(path) == digest, 'Frozen fit bytes')
    selected = [read_json(BASE/p) for p in lock['selected']]
    restarts = [read_json(BASE/p) for p in lock['restarts']]
    signature = lambda f:(f['world_id'],f['reference_condition'])
    panel = {(w,c) for w in spec['world_ids'] for c in CONDITIONS}
    check({signature(f) for f in selected} == panel, 'Six selected world/reference cells')
    candidates = read_json(data/'prepared/candidates.json')
    for fit in selected+restarts:
        check(signature(fit) in panel and fit['engine_arm'] == 'OFF', 'Fixed engine/reference condition')
        check(fit['seed'] == 83300000+100*fit['world_id']+fit['start'], 'Matched fixed optimizer seed')
        legal_key(fit['key'],candidates)
    for fit in selected:
        group = [r for r in restarts if signature(r) == signature(fit)]
        check(len(group) == 8 and {r['start'] for r in group} == set(range(8)), 'Eight complete starts per cell')
        winner = min(group,key=lambda f:(-f['discovery_objective']['total_nats'],f['start']))
        check(fit == winner, 'Discovery-objective selection and fixed tie breaking')
    # Only after every fit and selection is frozen may held/key commitments be opened.
    check({f'prepared/world_{w}_held.json' for w in spec['world_ids']} <= set(registration['held_commitments']), 'Complete held commitments')
    check({'sealed/source_truth.json'} | {f'sealed/world_{w}_truth.json' for w in spec['world_ids']} <= set(registration['sealed_commitments']), 'Complete source/key commitments')
    for section in ('held_commitments','sealed_commitments'):
        for relative,digest in registration[section].items():
            path = (data/relative).resolve()
            check(path.is_relative_to(data.resolve()) and sha(path) == digest, 'Held/truth commitment')
    return selected,lock


def discovery_score(cipher,key,model):
    return sum(model.paragraph_score([''.join(key[c] for c in word) for word in p['words']])
               for p in cipher['paragraphs'])


def score_condition(fit, truth, source, discovery, held, model):
    check(truth['paragraphs'] == source['paragraphs'], 'World original truth is source-exact')
    earlier = [p for p in source['paragraphs'] if p['split'] == 'discovery']
    seen_forms = {w for p in earlier for w in p['words']}
    seen_lemmas = {a for p in earlier for aa in p['lemma_sets'] if aa for a in aa}
    gold = {p['paragraph_id']:p for p in source['paragraphs'] if p['split'] == 'held'}
    buckets = {name:[] for name in ('all','v_words','non_v_words','novel_forms','novel_lemmas')}
    paragraph_exact = 0
    check(len(held['paragraphs']) == len(gold), 'Complete held paragraph panel')
    check(len({p['paragraph_id'] for p in held['paragraphs']}) == len(gold), 'No duplicate held paragraph')
    for p in held['paragraphs']:
        original = gold[p['paragraph_id']]
        check(len(p['words']) == len(original['words']) == len(original['lemma_sets']), 'Held word alignment')
        local = []
        for codes,word,analyses in zip(p['words'],original['words'],original['lemma_sets']):
            check(''.join(truth['decode_map'][c] for c in codes) == word, 'Exact original-spelling generator roundtrip')
            predicted = ''.join(fit['key'][c] for c in codes)
            pair = (word,predicted)
            buckets['all'].append(pair); local.append(pair)
            buckets['v_words' if 'v' in word else 'non_v_words'].append(pair)
            composed = not any(c.startswith('W') for c in codes)
            if composed and word not in seen_forms:
                buckets['novel_forms'].append(pair)
            if composed and analyses is not None and len(analyses) == 1 and analyses[0] not in seen_lemmas:
                buckets['novel_lemmas'].append(pair)
        paragraph_exact += all(a == b for a,b in local)
    support = Counter(c for p in discovery['paragraphs'] for word in p['words'] for c in word)
    held_support = {c for p in held['paragraphs'] for word in p['words'] for c in word}
    check(held_support <= set(support), 'No held-only key rule')
    key_metrics = []
    for kind in 'LSW':
        codes = [c for c in support if c.startswith(kind)]
        mass = sum(support[c] for c in codes)
        exact = sum(fit['key'][c] == truth['decode_map'][c] for c in codes)
        key_metrics.append({'kind':kind,'supported_rules':len(codes),'exact_supported_rules':exact,
                            'supported_rule_accuracy':exact/len(codes) if codes else None,
                            'discovery_mass_accuracy':sum(support[c] for c in codes if fit['key'][c] == truth['decode_map'][c])/mass if mass else None})
    v_code = next(c for c,value in truth['decode_map'].items() if c.startswith('L') and value == 'v')
    check(v_code in support and v_code in held_support, 'Observable v key in both partitions')
    fitted = discovery_score(discovery,fit['key'],model)
    recorded = fit['discovery_objective']
    check(abs(fitted-recorded['language_nats']) < 1e-4 and abs(fitted-recorded['total_nats']) < 1e-4
          and recorded['family_nats'] == 0, 'Frozen OFF objective replay')
    oracle = discovery_score(discovery,truth['decode_map'],model)
    mutant = discovery_score(discovery,swap_vz(truth['decode_map']),model)
    return {'world_id':fit['world_id'],'reference_condition':fit['reference_condition'],
            'selected_start':fit['start'],'selected_seed':fit['seed'],
            'recovery':{name:word_metrics(pairs) for name,pairs in buckets.items()},
            'held_paragraphs':len(gold),'exact_held_paragraphs':paragraph_exact,
            'active_key_accuracy':key_metrics,'v_key_output':fit['key'][v_code],
            'v_key_correct':fit['key'][v_code] == 'v',
            'oracle_true_nats':oracle,'oracle_vz_swap_nats':mutant,'oracle_margin':oracle-mutant,
            'selected_objective_nats':fitted,'selected_minus_oracle':fitted-oracle}


def decide(rows,spec):
    by = {(r['world_id'],r['reference_condition']):r for r in rows}
    primary = spec['specific_effect']
    recovery = spec['overall_recovery']
    specific = overall = True
    gains, non_v_gains = [], []
    for world in spec['world_ids']:
        native,collapsed = by[(world,'NATIVE')],by[(world,'COLLAPSED')]
        nm,cm = native['recovery'],collapsed['recovery']
        check(nm['v_words']['words'] == cm['v_words']['words'], 'Matched original-spelling v subset')
        gains.append(nm['v_words']['word_accuracy']-cm['v_words']['word_accuracy'])
        non_v_gains.append(nm['non_v_words']['word_accuracy']-cm['non_v_words']['word_accuracy'])
        specific &= (nm['v_words']['word_accuracy'] >= primary['minimum_native_v_word_accuracy_each_key']
                     and native['v_key_correct'] and native['oracle_margin'] > 0 and collapsed['oracle_margin'] < 0)
        overall &= (nm['all']['word_accuracy'] >= recovery['minimum_word_accuracy_each_native_key']
                    and nm['all']['character_accuracy'] >= recovery['minimum_character_accuracy_each_native_key']
                    and nm['novel_forms']['word_accuracy'] is not None
                    and nm['novel_forms']['word_accuracy'] >= recovery['minimum_novel_form_accuracy_each_native_key']
                    and nm['novel_lemmas']['word_accuracy'] is not None
                    and nm['novel_lemmas']['word_accuracy'] >= recovery['minimum_novel_lemma_accuracy_each_native_key'])
    mean = sum(gains)/len(gains)
    specific &= mean >= primary['minimum_mean_v_word_gain']-1e-12
    specific &= min(gains) >= primary['minimum_each_key_v_word_gain']-1e-12
    status = ('ORTHOGRAPHY_EFFECT_NOT_CONFIRMED' if not specific else
              'ORTHOGRAPHY_EFFECT_CONFIRMED_RECOVERY_FAIL' if not overall else
              'ORTHOGRAPHY_EFFECT_AND_RECOVERY_PASS')
    return {'status':status,'specific_effect_pass':bool(specific),'overall_recovery_pass':bool(overall),
            'v_word_gain_per_world':gains,'mean_v_word_gain':mean,
            'non_v_word_gain_per_world':non_v_gains,
            'three_keys_are_robustness_replicates_not_independent_texts':True,
            'gold_spelling_normalized_for_uv':False,'voynich_data_accessed':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=BASE)
    parser.add_argument('--model-root','--runtime-dir',dest='runtime_dir',type=Path,default=BASE/'runtime')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    spec = read_json(SRC/'SPEC.json')
    reference_check = reference_pair_check(args.data_dir)
    fits,lock = locked_fits(args.data_dir,spec)
    source = read_json(args.data_dir/'sealed/source_truth.json')
    module = reference_module()
    models = {c:module.load_model(args.runtime_dir/('reference_'+c.lower())) for c in CONDITIONS}
    for condition,model in models.items():
        check(model.metadata['input_hashes']['reference_jsonl_sha256'] ==
              sha(args.data_dir/('prepared/reference_'+condition.lower()+'.jsonl')) and
              model.metadata['input_hashes']['families_json_sha256'] == sha(args.data_dir/'prepared/families.json'),
              'Reference model is bound to the respective paired reference')
    rows = []
    for fit in sorted(fits,key=lambda f:(f['world_id'],f['reference_condition'])):
        w=fit['world_id']
        truth=read_json(args.data_dir/f'sealed/world_{w}_truth.json')
        discovery=read_json(args.data_dir/f'prepared/world_{w}_discovery.json')
        held=read_json(args.data_dir/f'prepared/world_{w}_held.json')
        rows.append(score_condition(fit,truth,source,discovery,held,models[fit['reference_condition']]))
    result={'schema':'GDT833_RESULT_V1',**decide(rows,spec),'reference_intervention':reference_check,
            'condition_results':rows,'fit_lock_sha256':sha(BASE/'artifacts/FIT_LOCK.json')}
    emit(BASE/'artifacts/RESULT.json',result,args.check)
    print(json.dumps({k:v for k,v in result.items() if k!='condition_results'},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
