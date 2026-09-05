#!/usr/bin/env python3
"""Independent GDT832 source/capacity and frozen-fit audit.

Capacity-only source access is explicitly authorized before keys exist. It
never prints historical plaintext and never opens world-key truth files.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parent
BASE = SRC.parent


def check(ok, message):
    if not ok:
        raise ValueError(message)


def obj(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(expected, actual, where='artifact'):
    if isinstance(expected, dict):
        check(isinstance(actual, dict), where + ': object required')
        for key, value in expected.items():
            check(key in actual, where + ': missing field ' + key)
            compare(value, actual[key], where + '.' + key)
    elif isinstance(expected, list):
        check(isinstance(actual, list) and len(expected) == len(actual), where + ': list length')
        for i, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, where + '[' + str(i) + ']')
    elif isinstance(expected, bool) or expected is None:
        check(actual is expected, where + ': boolean/null')
    elif isinstance(expected, (int, float)):
        check(isinstance(actual, (int, float)) and math.isfinite(actual)
              and abs(expected-actual) <= 1e-8, where + ': number')
    else:
        check(expected == actual, where + ': value')


def canonical_words(text):
    folded = text.casefold().replace('æ', 'ae').replace('œ', 'oe')
    folded = ''.join(c for c in unicodedata.normalize('NFKD', folded)
                     if not unicodedata.combining(c))
    return re.findall(r'[^\W\d_]+', folded, flags=re.UNICODE)


def conllu(path):
    comments, rows = {}, []
    with Path(path).open(encoding='utf-8') as stream:
        for raw in itertools.chain(stream, ['\n']):
            line = raw.rstrip('\r\n')
            if not line:
                if comments or rows:
                    yield comments, rows
                comments, rows = {}, []
            elif line.startswith('#'):
                match = re.fullmatch(r'# ([^=]+) = (.*)', line)
                if match:
                    comments[match[1].strip()] = match[2]
            else:
                fields = line.split('\t')
                check(len(fields) == 10, 'CoNLL-U field count')
                rows.append(fields)


def source_sentence(comments, fields):
    words = canonical_words(comments['text'])
    surface, analyses, statuses, covered = [], [], [], set()
    for row in fields:
        if re.fullmatch(r'\d+-\d+', row[0]):
            low, high = map(int, row[0].split('-'))
            covered.update(range(low, high+1))
            forms = canonical_words(row[1])
            surface.extend(forms)
            analyses.extend([None]*len(forms))
            statuses.extend(['UNKNOWN_MULTIWORD_TOKEN']*len(forms))
        elif row[0].isdigit() and int(row[0]) not in covered:
            forms = canonical_words(row[1])
            surface.extend(forms)
            valid = (len(forms) == 1 and re.fullmatch('[a-z]+', forms[0])
                     and row[2] != '_' and row[3] not in ('PUNCT', 'SYM', 'X', '_'))
            if valid:
                lemma = row[2].casefold().replace('æ', 'ae').replace('œ', 'oe')
                lemma = ''.join(c for c in unicodedata.normalize('NFKD', lemma)
                                if not unicodedata.combining(c))
                analyses.append([lemma+'|'+row[3]])
                statuses.append('EXACT_SINGLE_TOKEN_JOIN')
            else:
                analyses.extend([None]*len(forms))
                statuses.extend(['UNKNOWN_NONUNIQUE_OR_MISSING_ANNOTATION']*len(forms))
    if words != surface:
        analyses, statuses = [None]*len(words), ['UNKNOWN_SENTENCE_SURFACE_ALIGNMENT']*len(words)
    check(len(words) == len(analyses) == len(statuses), 'Independent annotation shape')
    return words, analyses, statuses


def source_hashes(data, source_dirs):
    manifest = obj(data / 'sources/MANIFEST.json')
    for kind, source in manifest['sources'].items():
        folder = data / 'sources' / kind
        source_path = source_dirs.get(kind, folder) / source['input_file']
        check(source_path.stat().st_size == source['bytes'] and sha(source_path) == source['sha256'],
              'Pinned source corpus bytes: ' + kind)
        for filename, field in [('README.md', 'README_sha256'), ('LICENSE.txt', 'LICENSE_sha256')]:
            check(sha(folder / filename) == source[field], 'Pinned source metadata: ' + kind)
    return manifest


def capacity_audit(data, source_dirs=None):
    source_dirs = source_dirs or {}
    spec = obj(SRC / 'ENCODER_SPEC.json')
    old = obj(data / 'prepared/CAPACITY.json')
    manifest = source_hashes(data, source_dirs)
    truth = obj(data / 'sealed/source_truth.json')
    paragraphs = truth['paragraphs']
    # Independent source paragraph and annotation reconstruction, with no
    # generator import and no plaintext in diagnostics/output artifacts.
    reconstructed, citation_count, last = [], Counter(), None
    for comments, fields in conllu(source_dirs.get('udante', data / 'sources/udante') / manifest['sources']['udante']['input_file']):
        if not comments.get('sent_id', '').startswith('Mon-'):
            last = None
            continue
        citation = comments['citation_hierarchy']
        if citation != last:
            citation_count[citation] += 1
            parts = citation.split(',')
            pid = 'Mon:' + ':'.join(parts)
            if citation_count[citation] > 1:
                pid += ':occurrence_' + str(citation_count[citation])
            split = 'discovery' if parts[0] == spec['discovery_book'] else 'held'
            check(parts[0] == spec['discovery_book'] or parts[0] in spec['held_books'], 'Registered book scope')
            reconstructed.append(dict(paragraph_id=pid, split=split, words=[], lemma_sets=[],
                                      annotation_status=[], source_sentence_ids=[]))
            last = citation
        words, analyses, statuses = source_sentence(comments, fields)
        p = reconstructed[-1]
        p['words'].extend(words)
        p['lemma_sets'].extend(analyses)
        p['annotation_status'].extend(statuses)
        p['source_sentence_ids'].append(comments['sent_id'])
    excluded = [p for p in reconstructed if any(re.fullmatch('[a-z]+', w) is None for w in p['words'])]
    kept = [p for p in reconstructed if p not in excluded]
    compare(kept, paragraphs, 'original paragraph/annotation reconstruction')
    compare(len(reconstructed), old['paragraphs_before_exclusion'], 'source paragraphs')
    compare(sum(len(p['source_sentence_ids']) for p in reconstructed), old['monarchia_sentences_before_exclusion'], 'source sentences')
    compare(sum(n-1 for n in citation_count.values()), old['noncontiguous_reused_citation_labels'], 'reused citations')
    compare(len(excluded), len(old['excluded_control_paragraphs']), 'whole-paragraph exclusion count')
    forms = {w for p in kept if p['split'] == 'discovery' for w in p['words']}
    lemmas = {a for p in kept if p['split'] == 'discovery' for row in p['lemma_sets'] if row for a in row}
    all_control_grams = {tuple(p['words'][i:i+20]) for p in kept for i in range(len(p['words'])-19)}
    reference, family = [], defaultdict(set)
    reference_status = Counter()
    removed = unsupported = 0
    for comments, fields in conllu(source_dirs.get('ittb', data / 'sources/ittb') / manifest['sources']['ittb']['input_file']):
        words, analyses, statuses = source_sentence(comments, fields)
        if any(re.fullmatch('[a-z]+', w) is None for w in words):
            unsupported += 1
            continue
        if any(tuple(words[i:i+20]) in all_control_grams for i in range(len(words)-19)):
            removed += 1
            continue
        reference.append(words)
        reference_status.update(statuses)
        for word, readings in zip(words, analyses):
            family[word].update(readings or [])
    prepared_reference = [json.loads(line) for line in (data / 'prepared/reference.jsonl').read_text().splitlines()]
    compare(reference, prepared_reference, 'reference source preservation')
    family = {w: sorted(a) for w, a in family.items() if a}
    compare(family, obj(data / 'prepared/families.json'), 'reference family annotations')
    counts = Counter(w for sentence in reference for w in sentence)
    compare({'reference_sentences': len(reference), 'reference_words': sum(counts.values()),
             'reference_types': len(counts), 'reference_family_forms': len(family),
             'reference_annotation_status_counts': dict(reference_status),
             'reference_sentences_removed_for_20word_overlap': removed,
             'reference_sentences_removed_for_unsupported_script': unsupported}, old, 'reference capacity')
    candidates = sorted((w for w in counts if 2 <= len(w) <= 10), key=lambda w: (-counts[w], w))[:128]
    compare({'suffix_pool': spec['suffix_candidate_pool'], 'wholeword_pool': candidates},
            obj(data / 'prepared/candidates.json'), 'candidate inventory')
    def encode(word):
        if word in spec['wholeword_values']:
            return (('W', word),)
        ending = next((s for s in spec['suffix_values'] if word.endswith(s) and
                       len(word)-len(s) >= spec['suffix_minimum_stem_characters']), None)
        if ending:
            return tuple(('L', c) for c in word[:-len(ending)]) + (('S', ending),)
        return tuple(('L', c) for c in word)
    support = {s: Counter() for s in ('discovery', 'held')}
    partitions = {}
    for split in support:
        pp = [p for p in kept if p['split'] == split]
        flat = [w for p in pp for w in p['words']]
        for w in flat:
            support[split].update(encode(w))
        new = [w for w in flat if w not in forms]
        newlemma = sum(a is not None and len(a) == 1 and a[0] not in lemmas for p in pp for a in p['lemma_sets'])
        partitions[split] = {'paragraphs': len(pp), 'sentences': sum(len(p['source_sentence_ids']) for p in pp),
                             'words': len(flat), 'types': len(set(flat)),
                             'novel_form_tokens': len(new), 'novel_form_types': len(set(new)),
                             'known_novel_lemma_tokens': newlemma,
                             'novel_composed_form_tokens': sum(w not in spec['wholeword_values'] for w in new),
                             'unknown_lemma_tokens': sum(a is None or len(a) != 1 for p in pp for a in p['lemma_sets']),
                             'annotation_status_counts': dict(Counter(s for p in pp for s in p['annotation_status']))}
    compare(partitions, old['partitions'], 'independent partition counts')
    decks = {'L': list(spec['letter_alphabet']), 'S': spec['suffix_values'], 'W': spec['wholeword_values']}
    rule_stats = {}
    for kind, values in decks.items():
        active = [n for (k, _), n in support['discovery'].items() if k == kind]
        held_rules = {r for r in support['held'] if r[0] == kind}
        rule_stats[kind] = {'discovery_active_rules': len(active), 'held_active_rules': len(held_rules),
                            'held_only_rules': len(held_rules-set(support['discovery'])),
                            'minimum_active_discovery_count': min(active, default=0),
                            'minimum_discovery_count_all_declared_rules': min(support['discovery'][(kind,v)] for v in values),
                            'minimum_discovery_count_among_held_active': min((support['discovery'][r] for r in held_rules), default=0)}
    compare(rule_stats, old['rule_support'], 'independent rule coverage')
    groups = defaultdict(list)
    for word in sorted(forms):
        encoded = encode(word)
        if len(encoded) >= 4:
            groups[encoded[:-1]].append(word)
    edges = [(u,v) for group in groups.values() for u,v in itertools.combinations(group,2)]
    coherent = sum(bool(set(family.get(u,[])) & set(family.get(v,[]))) for u,v in edges)
    compare(len(edges), old['observed_discovery_source_family_edges'], 'source family edges')
    compare(coherent, old['reference_lemma_supported_source_family_edges'], 'reference-supported source edges')
    macro_min = spec['minimum_discovery_occurrences_each_suffix_or_wholeword']
    gates = {'minimum_discovery_paragraphs': partitions['discovery']['paragraphs'] >= spec['minimum_discovery_paragraphs'],
             'minimum_held_paragraphs': partitions['held']['paragraphs'] >= spec['minimum_held_paragraphs'],
             'wholeword_truth_in_reference_pool': set(spec['wholeword_values']) <= set(candidates),
             'suffix_truth_in_frozen_pool': set(spec['suffix_values']) <= set(spec['suffix_candidate_pool']),
             'suffix_discovery_coverage': rule_stats['S']['minimum_discovery_count_all_declared_rules'] >= macro_min,
             'wholeword_discovery_coverage': rule_stats['W']['minimum_discovery_count_all_declared_rules'] >= macro_min,
             'held_active_letter_discovery_coverage': rule_stats['L']['minimum_discovery_count_among_held_active'] >= spec['minimum_discovery_occurrences_each_held_active_letter'],
             'minimum_observed_source_family_edges': len(edges) >= spec['minimum_source_family_edges'],
             'minimum_held_novel_composed_form_occurrences': partitions['held']['novel_composed_form_tokens'] >= spec['minimum_held_novel_composed_form_occurrences'],
             'minimum_held_known_novel_lemma_occurrences': partitions['held']['known_novel_lemma_tokens'] >= spec['minimum_held_known_novel_lemma_occurrences'],
             'minimum_reference_lemma_supported_source_family_edges': coherent >= spec['minimum_reference_lemma_supported_source_family_edges']}
    compare(gates, old['gates'], 'initial fixed gates')
    compare(sorted(k for k,v in gates.items() if not v), old['failed_gates'], 'initial failures')
    check(old['status'] == ('SOURCE_CAPACITY_PASS' if all(gates.values()) else 'SOURCE_CAPACITY_STOP'), 'Initial capacity decision')
    active_suffixes = {r for s in support.values() for r in s if r[0] == 'S'}
    active_min = min((support['discovery'][r] for r in active_suffixes), default=0)
    active_gates = dict(gates, suffix_discovery_coverage=active_min >= macro_min)
    active_path = data / 'prepared/ACTIVE_RULE_CAPACITY.json'
    if active_path.exists():
        active = obj(active_path)
        compare({'initial_capacity_sha256': sha(data/'prepared/CAPACITY.json'),
                 'source_truth_sha256': sha(data/'sealed/source_truth.json'),
                 'sources_manifest_sha256': sha(data/'sources/MANIFEST.json'),
                 'initial_status': old['status'], 'initial_failed_gates': old['failed_gates'],
                 'changed_gate': 'suffix_discovery_coverage', 'gates': active_gates,
                 'active_suffix_rule_count': len(active_suffixes),
                 'inactive_suffix_rule_count': len(spec['suffix_values'])-len(active_suffixes),
                 'minimum_discovery_count_active_suffix_rules': active_min,
                 'failed_gates': sorted(k for k,v in active_gates.items() if not v)}, active, 'active-rule correction')
        check(active['status'] == ('ACTIVE_RULE_SOURCE_CAPACITY_PASS' if all(active_gates.values()) else 'ACTIVE_RULE_SOURCE_CAPACITY_STOP'), 'Active rule capacity decision')
        for name, digest in active['prepared_input_sha256'].items():
            check(Path(name).name == name and sha(data/'prepared'/name) == digest, 'Corrected capacity input binding')
    return {'status': 'PASS_INDEPENDENT_SOURCE_CAPACITY_RECONSTRUCTION',
            'initial_decision': old['status'], 'active_rule_decision': 'ACTIVE_RULE_SOURCE_CAPACITY_PASS' if all(active_gates.values()) else 'ACTIVE_RULE_SOURCE_CAPACITY_STOP',
            'control_paragraphs_reconstructed': len(kept),
            'control_words_reconstructed': sum(len(p['words']) for p in kept),
            'reference_words_reconstructed': sum(counts.values()),
            'source_family_edges_reconstructed': len(edges),
            'reference_supported_source_edges_reconstructed': coherent,
            'active_suffix_rules': len(active_suffixes),
            'inactive_suffix_rules': len(spec['suffix_values'])-len(active_suffixes),
            'initial_failed_gates': sorted(k for k,v in gates.items() if not v),
            'active_failed_gates': sorted(k for k,v in active_gates.items() if not v),
            'source_plaintext_printed': False, 'world_key_truth_opened': False,
            'control_recovery_tested': False, 'voynich_data_accessed': False}


def distance(a, b):
    row = list(range(len(b)+1))
    for i, left in enumerate(a, 1):
        previous, row = row, [i]
        for j, right in enumerate(b, 1):
            row.append(min(previous[j]+1, row[j-1]+1, previous[j-1]+int(left != right)))
    return row[-1]


def word_statistics(pairs):
    types = defaultdict(list)
    edits = denominator = correct = 0
    for gold, prediction in pairs:
        same = gold == prediction
        correct += same
        edits += 0 if same else distance(gold, prediction)
        denominator += max(len(gold), len(prediction))
        types[gold].append(same)
    return dict(words=len(pairs), exact_words=correct,
                word_accuracy=correct/len(pairs) if pairs else None,
                edit_distance=edits, character_denominator=denominator,
                character_accuracy=1-edits/denominator if denominator else None,
                truth_types=len(types), fully_correct_truth_types=sum(all(v) for v in types.values()),
                truth_type_accuracy=sum(all(v) for v in types.values())/len(types) if types else None)


def objective(discovery, key, model, memberships, arm, spec):
    language = 0.0
    buckets = defaultdict(set)
    for p in discovery['paragraphs']:
        last_word, last_macro = None, False
        for word in p['words']:
            plain = ''.join(key[c] for c in word)
            macro = any(c[0] == 'W' for c in word)
            previous = None if arm == 'CUT' and (macro or last_macro) else last_word
            language += model.log_conditional(previous, plain)
            last_word, last_macro = plain, macro
            if len(word) > spec['source_family']['minimum_shared_prefix_atoms']:
                buckets[tuple(word[:-1])].add(tuple(word))
    edges = [(u,v) for group in buckets.values() for u,v in itertools.combinations(sorted(group),2)]
    degree = Counter(node for edge in edges for node in edge)
    relational = 0.0
    if arm != 'OFF':
        graph = memberships['REWIRED' if arm == 'REWIRED' else 'FULL']
        for u,v in edges:
            a, b = ''.join(key[c] for c in u), ''.join(key[c] for c in v)
            if a != b and graph.get(a, set()) & graph.get(b, set()):
                relational += 1/max(degree[u], degree[v])
    relational *= spec['source_family']['lambda_nats']
    return dict(language_nats=language, family_nats=relational, total_nats=language+relational)


def fit_audit(data, model_dir):
    from reference_model import load_model
    spec = obj(SRC / 'SPEC.json')
    registration = obj(SRC / 'PREREG_LOCK.json')['sha256']
    for relative, expected in registration.items():
        path = (BASE / relative).resolve()
        check(path.is_relative_to(BASE) and sha(path) == expected, 'Preregistration binding')
    lock = obj(BASE / 'artifacts/FIT_LOCK.json')
    check(lock['spec_sha256'] == sha(SRC/'SPEC.json'), 'Frozen specification')
    check(len(lock['selected']) == 15 and len(lock['restarts']) == 120, 'Complete fit panel before truth')
    check(set(lock['selected']+lock['restarts']) <= set(lock['sha256']), 'All fit files bound')
    for relative, expected in lock['sha256'].items():
        path = (BASE / relative).resolve()
        check(path.is_relative_to(BASE) and sha(path) == expected, 'Frozen fit file')
    selected = [obj(BASE/p) for p in lock['selected']]
    restarts = [obj(BASE/p) for p in lock['restarts']]
    expected_panel = {(w,'real',a) for w in spec['world_ids'] for a in spec['real_arms']} | {(w,'pseudo','FULL') for w in spec['world_ids']}
    signature = lambda r: (r['world_id'], r['condition'], r['arm'])
    check({signature(r) for r in selected} == expected_panel, 'Selected panel identities')
    pools = obj(data/'prepared/candidates.json')
    expected_codes = {f'{k}{i:02d}' for k,n in [('L',26),('S',4),('W',8)] for i in range(n)}
    for fit in restarts+selected:
        check(signature(fit) in expected_panel, 'Fit scope')
        check(fit['start'] in spec['starts'] and fit['seed'] == 83200000+100*fit['world_id']+fit['start'], 'Frozen restart seed')
        check(set(fit['key']) == expected_codes, 'Key inventory')
        for kind,pool in [('L',set(spec['letter_alphabet'])),('S',set(pools['suffix_pool'])),('W',set(pools['wholeword_pool']))]:
            values = [v for c,v in fit['key'].items() if c[0] == kind]
            check(set(values) <= pool and len(set(values)) == len(values), 'Legal injective role outputs')
        suffix = '_pseudo' if fit['condition'] == 'pseudo' else ''
        discovery_path = data/f'prepared/world_{fit["world_id"]}{suffix}_discovery.json'
        check(fit['input_hashes']['discovery_input_sha256'] == sha(discovery_path), 'Discovery-only input binding')
        check(fit['input_hashes']['model_meta_sha256'] == sha(model_dir/'model_meta.json'), 'Reference model binding')
        check(fit['input_hashes']['decoder_source_sha256'] == sha(SRC/'decoder.cpp'), 'Fitter code binding')
        check(fit['input_hashes']['spec_sha256'] == sha(SRC/'SPEC.json'), 'Fitter spec binding')
    for fit in selected:
        group = [r for r in restarts if signature(r) == signature(fit)]
        check(len(group) == 8 and {r['start'] for r in group} == set(spec['starts']), 'Eight complete starts per arm')
        winner = min(group, key=lambda r: (-r['discovery_objective']['total_nats'],r['start']))
        check(fit == winner, 'Discovery-only selected fit, exact tie handling')
    # Complete protocol check above precedes every world-truth access below.
    for relative, digest in obj(SRC / 'PREREG_LOCK.json')['held_commitments'].items():
        check(sha(data/relative) == digest, 'Held ciphertext commitment after fit freeze')
    commitments = obj(SRC / 'PREREG_LOCK.json')['sealed_commitments']
    check(set(commitments) == {'sealed/source_truth.json'} | {f'sealed/world_{w}_truth.json' for w in spec['world_ids']}, 'Complete truth commitments')
    for relative,digest in commitments.items():
        check(sha(data/relative) == digest, 'Prior sealed truth commitment verified after fit freeze')
    model = load_model(model_dir)
    memberships = {}
    for arm,name in [('FULL','family_real.tsv'),('REWIRED','family_rewired.tsv')]:
        with (model_dir/name).open(newline='') as stream:
            memberships[arm] = {model.words[int(r['word_id'])]:set(r['lemma_ids'].split(','))-{''}
                                for r in csv.DictReader(stream,delimiter='\t')}
    check(Counter({w:len(a) for w,a in memberships['FULL'].items()}) ==
          Counter({w:len(a) for w,a in memberships['REWIRED'].items()}), 'Rewired form degrees')
    check(Counter(a for values in memberships['FULL'].values() for a in values) ==
          Counter(a for values in memberships['REWIRED'].values() for a in values), 'Rewired lemma degrees')
    discovery_cache = {}
    for world,condition,_ in expected_panel:
        suffix = '_pseudo' if condition == 'pseudo' else ''
        discovery_cache[(world,condition)] = obj(data/f'prepared/world_{world}{suffix}_discovery.json')
    objective_count = 0
    for fit in restarts:
        expected = objective(discovery_cache[(fit['world_id'],fit['condition'])],fit['key'],model,memberships,fit['arm'],spec)
        for key,value in expected.items():
            check(abs(value-fit['discovery_objective'][key]) <= 1e-4, 'Independent C++ objective reconstruction')
        objective_count += 1
    evaluation = obj(BASE/'artifacts/EVALUATION.json')
    check(evaluation['fit_lock_sha256'] == sha(BASE/'artifacts/FIT_LOCK.json'), 'Evaluation uses frozen fit lock')
    reports = {(r['world_id'],r['condition'],r['arm']):r for r in evaluation['results']}
    check(set(reports) == expected_panel, 'Evaluation panel')
    source = obj(data/'sealed/source_truth.json')['paragraphs']
    check(sha(data/'sealed/source_truth.json') == obj(data/'prepared/ACTIVE_RULE_CAPACITY.json')['source_truth_sha256'], 'Original source truth commitment')
    seen_forms = {w for p in source if p['split']=='discovery' for w in p['words']}
    seen_lemmas = {a for p in source if p['split']=='discovery' for row in p['lemma_sets'] if row for a in row}
    metrics_by_fit = {}
    held_words_checked = 0
    null_scores_checked = 0
    for fit in selected:
        ident = signature(fit)
        world,condition,arm = ident
        report = reports[ident]
        truth = obj(data/f'sealed/world_{world}_truth.json')
        check(truth['paragraphs'] == source, 'World original truth/source equality')
        original_by_id = {p['paragraph_id']:p for p in source}
        check(len(truth['pseudo_paragraphs']) == len(source), 'Pseudo source inventory')
        for pseudo in truth['pseudo_paragraphs']:
            original = original_by_id[pseudo['paragraph_id']]
            order = pseudo['source_order_indices']
            check(sorted(order) == list(range(len(original['words']))), 'Pseudo source-order permutation')
            for field in ['words','lemma_sets','annotation_status','novel_form','novel_lemma','composed']:
                check(pseudo[field] == [original[field][i] for i in order], 'Pseudo source annotation binding')
        rng = random.Random(world)
        expected_truth_key = {}
        encoder_spec = obj(SRC/'ENCODER_SPEC.json')
        for kind,values in [('L',list(encoder_spec['letter_alphabet'])),('S',encoder_spec['suffix_values']),('W',encoder_spec['wholeword_values'])]:
            ids=[f'{kind}{i:02d}' for i in range(len(values))];rng.shuffle(ids)
            expected_truth_key.update(zip(ids,values))
        check(truth['decode_map'] == expected_truth_key, 'Independent generator key reconstruction after fit lock')
        suffix = '_pseudo' if condition=='pseudo' else ''
        held = obj(data/f'prepared/world_{world}{suffix}_held.json')
        pp = truth['pseudo_paragraphs'] if condition=='pseudo' else truth['paragraphs']
        truth_by_id = {p['paragraph_id']:p for p in pp if p['split']=='held'}
        lists = {k:[] for k in ['all_words','novel_composed_forms','novel_composed_lemmas','macro_or_novel_composed','macro_words']}
        exact_paragraphs = 0
        decoded_paragraphs = []
        for p in held['paragraphs']:
            actual = truth_by_id[p['paragraph_id']]
            check(len(p['words']) == len(actual['words']) == len(actual['lemma_sets']), 'Held source alignment')
            pairs, decoded = [], []
            for encoded,gold,lemmas in zip(p['words'],actual['words'],actual['lemma_sets']):
                check(''.join(truth['decode_map'][c] for c in encoded)==gold, 'Independent encoder roundtrip')
                prediction=''.join(fit['key'][c] for c in encoded)
                pair=(gold,prediction)
                pairs.append(pair);decoded.append(prediction);lists['all_words'].append(pair)
                composed=not any(c[0]=='W' for c in encoded)
                new=composed and gold not in seen_forms
                newlemma=composed and lemmas is not None and len(lemmas)==1 and lemmas[0] not in seen_lemmas
                macro=any(c[0] in 'SW' for c in encoded)
                if new: lists['novel_composed_forms'].append(pair)
                if newlemma: lists['novel_composed_lemmas'].append(pair)
                if macro or new: lists['macro_or_novel_composed'].append(pair)
                if macro: lists['macro_words'].append(pair)
                held_words_checked += 1
            exact=all(a==b for a,b in pairs)
            exact_paragraphs += exact
            recorded=next(r for r in report['recovery']['paragraphs'] if r['paragraph_id']==p['paragraph_id'])
            compare(dict(paragraph_id=p['paragraph_id'],exact_paragraph=exact,**word_statistics(pairs)),recorded,'paragraph recovery')
            decoded_paragraphs.append((p['paragraph_id'],decoded))
        stats={name:word_statistics(pairs) for name,pairs in lists.items()}
        compare(stats,report['recovery'],'independent held metrics')
        compare(exact_paragraphs,report['recovery']['exact_paragraphs'],'exact held paragraphs')
        metrics_by_fit[ident]=stats
        discovery=discovery_cache[(world,condition)]
        supported=Counter(c for p in discovery['paragraphs'] for word in p['words'] for c in word)
        for row in report['recovery']['key']:
            codes=[c for c in supported if c[0]==row['kind']]
            correct=sum(fit['key'][c]==truth['decode_map'][c] for c in codes)
            mass=sum(supported[c] for c in codes)
            compare(dict(discovery_supported_rules=len(codes),exact_supported_rules=correct,
                         supported_rule_accuracy=correct/len(codes),
                         discovery_mass_accuracy=sum(supported[c] for c in codes if fit['key'][c]==truth['decode_map'][c])/mass),row,'supported key accuracy')
        oracle=objective(discovery,truth['decode_map'],model,memberships,arm,spec)
        compare(oracle,report['oracle_objective'],'oracle objective')
        fitted=objective(discovery,fit['key'],model,memberships,arm,spec)
        compare(fitted,report['selected_discovery_objective_replayed'],'selected objective replay')
        compare(fitted['total_nats']-oracle['total_nats'],report['selected_minus_oracle'],'oracle margin')
        if arm=='FULL':
            observed=0.0
            null=np.zeros(spec['order_control']['shuffles'],dtype=np.float64)
            for pid,words in decoded_paragraphs:
                words_unique=sorted(set(words)); ix={w:i for i,w in enumerate(words_unique)}
                initial=np.asarray([model.log_unigram(w) for w in words_unique])
                transitions=np.asarray([[model.log_conditional(a,b) for b in words_unique] for a in words_unique])
                ids=np.asarray([ix[w] for w in words],dtype=np.int64)
                observed+=float(initial[ids[0]]+transitions[ids[:-1],ids[1:]].sum())
                seed=int.from_bytes(hashlib.sha256((str(spec['order_control']['seed'])+'|'+pid).encode()).digest()[:8],'big')
                rng=random.Random(seed)
                for j in range(len(null)):
                    positions=list(range(len(words)));rng.shuffle(positions)
                    shuffled=ids[positions]
                    null[j]+=float(initial[shuffled[0]]+transitions[shuffled[:-1],shuffled[1:]].sum())
            test=report['context_test']
            check(np.max(np.abs(null-np.asarray(test['null_scores_nats'])))<1e-7,'Independent held permutation scores')
            compare(observed,test['observed_nats'],'held order score')
            n=int(np.count_nonzero(null>=observed))
            compare(dict(shuffle_count=len(null),null_greater_equal=n,upper_p=(n+1)/(len(null)+1),null_mean_nats=float(null.mean())),test,'order test arithmetic')
            null_scores_checked+=len(null)
    recovered=True
    ordered=True
    for world in spec['world_ids']:
        full=metrics_by_fit[(world,'real','FULL')];r=spec['recovery']
        recovered &= (full['all_words']['word_accuracy']>=r['minimum_full_word_accuracy_each_key'] and
                      full['all_words']['character_accuracy']>=r['minimum_full_character_accuracy_each_key'] and
                      full['novel_composed_forms']['word_accuracy']>=r['minimum_full_novel_composed_form_accuracy_each_key'] and
                      full['novel_composed_lemmas']['word_accuracy']>=r['minimum_full_novel_composed_lemma_accuracy_each_key'])
        ordered &= (reports[(world,'real','FULL')]['context_test']['upper_p']<=spec['order_control']['real_p_max'] and
                    reports[(world,'pseudo','FULL')]['context_test']['upper_p']>spec['order_control']['pseudo_p_must_exceed'])
    gain=True
    for arm in ('CUT','OFF'):
        ds=[metrics_by_fit[(w,'real','FULL')]['macro_or_novel_composed']['word_accuracy']-
            metrics_by_fit[(w,'real',arm)]['macro_or_novel_composed']['word_accuracy'] for w in spec['world_ids']]
        ok=min(ds)>=spec['incremental_information']['minimum_each_key_gain']-1e-12 and sum(ds)/3>=spec['incremental_information']['minimum_mean_full_minus_'+arm.lower()]-1e-12
        compare(sum(ds)/3,evaluation['gains'][arm]['mean'],'ablation gain')
        compare(ds,evaluation['gains'][arm]['per_world'],'key-level ablation gains')
        compare(bool(ok),evaluation['gains'][arm]['pass'],'ablation gate')
        gain &= ok
    status=('CONTROL_RECOVERY_FAIL' if not recovered else 'CONTROL_RECOVERED_NO_JOINT_GAIN' if not gain else
            'JOINT_GAIN_WITH_ORDER_CONTROL_FAIL' if not ordered else 'JOINT_CONTROL_RECOVERY_AND_GAIN_PASS')
    compare(dict(status=status,recovery_pass=bool(recovered),context_discrimination_pass=bool(ordered),joint_gain_pass=bool(gain)),evaluation,'final decision')
    return {'status':'PASS_INDEPENDENT_FROZEN_FIT_AND_RECOVERY_RECONSTRUCTION',
            'scientific_status':status,'restart_objectives_replayed':objective_count,
            'selected_fits_verified':len(selected),'held_word_predictions_checked':held_words_checked,
            'held_null_scores_reconstructed':null_scores_checked,'world_key_truth_opened':True,
            'voynich_data_accessed':False,'translation_established':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=BASE)
    parser.add_argument('--model-dir', type=Path)
    parser.add_argument('--reference-dir', type=Path)
    parser.add_argument('--control-dir', type=Path)
    parser.add_argument('--capacity-only', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    source_dirs = {kind: value for kind, value in [('ittb', args.reference_dir), ('udante', args.control_dir)] if value is not None}
    if args.capacity_only:
        result = capacity_audit(args.data_dir, source_dirs)
        path = BASE / 'artifacts/CAPACITY_VALIDATION.json'
    else:
        check(args.model_dir is not None, '--model-dir required for frozen fit/evaluation audit')
        result = fit_audit(args.data_dir,args.model_dir)
        path = BASE / 'artifacts/VALIDATION.json'
    if args.check:
        compare(result, obj(path), 'capacity validation replay')
    else:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
