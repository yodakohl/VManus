#!/usr/bin/env python3
"""Independent source, paired-reference, locked-fit and original-spelling audit.

Capacity-only mode is authorized source accounting and never opens world keys.
Full mode verifies every locked fit before reading held data or key truth.
No fitter, generator or evaluator is imported for independent arithmetic.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

SRC = Path(__file__).resolve().parent
BASE = SRC.parent
ROOT = BASE.parents[2]
CONDITIONS = ('NATIVE', 'COLLAPSED')


def check(ok, message):
    if not ok:
        raise ValueError(message)


def obj(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(expected, actual, where='artifact', tolerance=1e-8):
    if isinstance(expected, dict):
        check(isinstance(actual, dict), where + ': object required')
        for key, value in expected.items():
            check(key in actual, where + ': missing field ' + key)
            compare(value, actual[key], where + '.' + key, tolerance)
    elif isinstance(expected, list):
        check(isinstance(actual, list) and len(expected) == len(actual), where + ': list length')
        for i, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, where + '[' + str(i) + ']', tolerance)
    elif isinstance(expected, bool) or expected is None:
        check(actual is expected, where + ': boolean/null')
    elif isinstance(expected, (int, float)):
        check(isinstance(actual, (int, float)) and math.isfinite(actual)
              and abs(expected-actual) <= tolerance, where + ': number')
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


def logical_atoms(word, encoder):
    if word in encoder['wholeword_values']:
        return [('W', word)]
    for ending in encoder['suffix_values']:
        if word.endswith(ending) and len(word)-len(ending) >= encoder['suffix_minimum_stem_characters']:
            return [('L', char) for char in word[:-len(ending)]] + [('S', ending)]
    return [('L', char) for char in word]


def capacity_audit(data, source_dir):
    encoder, spec = obj(SRC/'ENCODER_SPEC.json'), obj(SRC/'SPEC.json')
    cap, manifest = obj(data/'prepared/CAPACITY.json'), obj(data/'sources/MANIFEST.json')
    for name, info in manifest['files'].items():
        check((source_dir/name).stat().st_size == info['bytes'] and sha(source_dir/name) == info['sha256'], 'Pinned source bytes')
    check(sha(ROOT/manifest['frozen_helper']['path']) == manifest['frozen_helper']['sha256'], 'Unchanged upstream source helper')
    check(sha(SRC/'ENCODER_SPEC.json') == cap['encoder_spec_sha256'] and
          sha(data/'sources/MANIFEST.json') == cap['sources_manifest_sha256'], 'Capacity source bindings')
    for name, digest in cap['prepared_input_sha256'].items():
        check(sha(data/'prepared'/name) == digest, 'Capacity prepared binding')
    check(sha(data/'sealed/source_truth.json') == cap['source_truth_sha256'], 'Original source commitment')
    source = obj(data/'sealed/source_truth.json')
    rebuilt, occurrences, previous = [], Counter(), None
    for comments, fields in conllu(source_dir/'la_udante-ud-test.conllu'):
        check(comments['sent_id'].startswith(encoder['control_work']+'-'), 'Fixed DVE source scope')
        citation = comments['citation_hierarchy']
        pieces = citation.split(',')
        check(len(pieces) == 3 and pieces[2].startswith('Paragraphus_'), 'Original citation shape')
        check(pieces[0] == encoder['discovery_book'] or pieces[0] in encoder['held_books'], 'Control book scope')
        if citation != previous:
            occurrences[citation] += 1
            pid = encoder['control_work']+':'+':'.join(pieces)
            if occurrences[citation] > 1:
                pid += ':occurrence_'+str(occurrences[citation])
            rebuilt.append({'paragraph_id':pid, 'book':pieces[0], 'chapter':pieces[1],
                            'citation_hierarchy':citation, 'citation_occurrence':occurrences[citation],
                            'split':'discovery' if pieces[0] == encoder['discovery_book'] else 'held',
                            'words':[], 'lemma_sets':[], 'annotation_status':[],
                            'source_sentence_ids':[], 'sentence_word_spans':[]})
            previous = citation
        words, analyses, statuses = source_sentence(comments, fields)
        row = rebuilt[-1]
        row['sentence_word_spans'].append([len(row['words']),len(row['words'])+len(words)])
        row['words'].extend(words); row['lemma_sets'].extend(analyses)
        row['annotation_status'].extend(statuses); row['source_sentence_ids'].append(comments['sent_id'])
    excluded = [p for p in rebuilt if any(re.fullmatch('[a-z]+',w) is None for w in p['words'])]
    kept = [p for p in rebuilt if p not in excluded]
    compare(kept, source['paragraphs'], 'Independent original paragraph/annotation reconstruction')
    compare([{'paragraph_id':p['paragraph_id'],'split':p['split'],
              'reason':'UNREPRESENTABLE_ALPHABETIC_WORD','word_count':len(p['words'])} for p in excluded], cap['excluded_control_paragraphs'])
    compare(sum(len(p['source_sentence_ids']) for p in rebuilt), cap['control_sentences_before_exclusion'])
    compare(sum(n-1 for n in occurrences.values()), cap['control_noncontiguous_citation_reuse_events'])
    compare(sum(n>1 for n in occurrences.values()), cap['control_distinct_reused_citation_labels'])
    seen = {w for p in kept if p['split'] == 'discovery' for w in p['words']}
    lemmas = {a for p in kept if p['split'] == 'discovery' for aa in p['lemma_sets'] if aa for a in aa}
    width = encoder['deduplication_ngram_words']
    grams = {tuple(p['words'][i:i+width]) for p in kept for i in range(len(p['words'])-width+1)}
    native, ids, removed, unsupported = [], [], [], []
    for comments, fields in conllu(source_dir/'la_udante-ud-train.conllu'):
        if not comments['sent_id'].startswith(encoder['reference_work']+'-'):
            continue
        words = canonical_words(comments['text'])
        if any(re.fullmatch('[a-z]+',w) is None for w in words):
            unsupported.append(comments['sent_id']); continue
        if any(tuple(words[i:i+width]) in grams for i in range(len(words)-width+1)):
            removed.append(comments['sent_id']); continue
        native.append(words); ids.append(comments['sent_id'])
    collapsed = [[w.replace('v','u') for w in sentence] for sentence in native]
    for condition, expected in [('native',native),('collapsed',collapsed)]:
        actual = [json.loads(line) for line in (data/f'prepared/reference_{condition}.jsonl').read_text().splitlines()]
        check(expected == actual, 'Independent paired reference reconstruction: '+condition)
    compare(ids, obj(data/'prepared/reference_ids.json'), 'Reference sentence identities')
    compare(removed, source['reference_removed_overlap_sentence_ids'])
    compare(unsupported, source['reference_unsupported_sentence_ids'])
    check(obj(data/'prepared/families.json') == {}, 'Both reference conditions have no family factors')
    counts = Counter(w for sentence in native for w in sentence)
    pool = sorted((w for w in counts if encoder['wholeword_candidate_minimum_characters'] <= len(w) <= encoder['wholeword_candidate_maximum_characters']), key=lambda w:(-counts[w],w))[:encoder['wholeword_candidate_pool_size']]
    compare({'suffix_pool':encoder['suffix_candidate_pool'],'wholeword_pool':pool}, obj(data/'prepared/candidates.json'))
    support = {s:Counter() for s in ('discovery','held')}
    partitions = {}
    for split in support:
        pp = [p for p in kept if p['split'] == split]
        for p in pp:
            flags = {'novel_form':[w not in seen for w in p['words']],
                     'novel_lemma':[None if aa is None or len(aa)!=1 else aa[0] not in lemmas for aa in p['lemma_sets']],
                     'composed':[w not in encoder['wholeword_values'] for w in p['words']],
                     'contains_v':['v' in w for w in p['words']]}
            original = next(q for q in source['paragraphs'] if q['paragraph_id'] == p['paragraph_id'])
            compare(flags, original, 'Independent novelty and spelling flags')
            for w in p['words']:
                support[split].update(logical_atoms(w,encoder))
        flat = [w for p in pp for w in p['words']]
        partitions[split] = {'paragraphs':len(pp),'sentences':sum(len(p['source_sentence_ids']) for p in pp),
            'words':len(flat),'types':len(set(flat)),'v_containing_words':sum('v' in w for w in flat),
            'literal_v_occurrences':sum(w.count('v') for w in flat),
            'novel_composed_form_occurrences':sum(w not in seen and w not in encoder['wholeword_values'] for w in flat),
            'known_novel_lemma_occurrences':sum(aa is not None and len(aa)==1 and aa[0] not in lemmas for p in pp for aa in p['lemma_sets']),
            'unknown_lemma_occurrences':sum(aa is None or len(aa)!=1 for p in pp for aa in p['lemma_sets']),
            'annotation_status_counts':dict(Counter(s for p in pp for s in p['annotation_status']))}
    compare(partitions, cap['partitions'], 'Independent capacity partition accounting')
    compare({s:[{'kind':k,'value':v,'count':n} for (k,v),n in sorted(c.items())] for s,c in support.items()}, source['logical_rule_support'])
    stats = {}
    active = set(support['discovery']) | set(support['held'])
    for kind, nominal in [('L',len(encoder['letter_alphabet'])),('S',len(encoder['suffix_values'])),('W',len(encoder['wholeword_values']))]:
        aa, hh = {a for a in active if a[0]==kind}, {a for a in support['held'] if a[0]==kind}
        stats[kind] = {'nominal_rules':nominal,'active_rules':len(aa),'unobserved_unscored_rules':nominal-len(aa),
                      'minimum_discovery_occurrences_active_rules':min((support['discovery'][a] for a in aa),default=0),
                      'minimum_discovery_occurrences_held_active_rules':min((support['discovery'][a] for a in hh),default=0),
                      'held_only_rules':sum(support['discovery'][a]==0 for a in hh)}
    compare(stats, cap['rule_support'], 'Active parameter domain')
    v = sum(w.count('v') for sentence in native for w in sentence)
    c = spec['capacity']
    gates = {'discovery_paragraphs':partitions['discovery']['paragraphs']>=c['minimum_discovery_paragraphs'],
             'held_paragraphs':partitions['held']['paragraphs']>=c['minimum_held_paragraphs'],
             'active_suffix_discovery_coverage':stats['S']['minimum_discovery_occurrences_active_rules']>=c['minimum_discovery_occurrences_active_macro'],
             'active_wholeword_discovery_coverage':stats['W']['minimum_discovery_occurrences_active_rules']>=c['minimum_discovery_occurrences_active_macro'],
             'held_active_letter_discovery_coverage':stats['L']['minimum_discovery_occurrences_held_active_rules']>=c['minimum_discovery_occurrences_held_active_letter'],
             'wholeword_truth_in_native_candidate_pool':set(encoder['wholeword_values'])<=set(pool),
             'suffix_truth_in_frozen_candidate_pool':set(encoder['suffix_values'])<=set(encoder['suffix_candidate_pool']),
             'discovery_v_containing_words':partitions['discovery']['v_containing_words']>=c['minimum_discovery_v_word_tokens'],
             'held_v_containing_words':partitions['held']['v_containing_words']>=c['minimum_held_v_word_tokens'],
             'reference_literal_v':v>=c['minimum_reference_v_characters'],
             'held_novel_composed_forms':partitions['held']['novel_composed_form_occurrences']>=c['minimum_held_novel_composed_form_occurrences'],
             'held_known_novel_lemmas':partitions['held']['known_novel_lemma_occurrences']>=c['minimum_held_novel_composed_lemma_occurrences'],
             'exact_paired_reference_intervention':True}
    compare(gates, cap['gates'], 'SPEC-defined source capacity gates')
    compare(sorted(k for k,vv in gates.items() if not vv), cap['failed_gates'])
    compare('SOURCE_CAPACITY_PASS' if all(gates.values()) else 'SOURCE_CAPACITY_STOP', cap['status'])
    compare({'reference_sentences':len(native),'reference_words':sum(map(len,native)),
             'reference_native_v_occurrences':v,'reference_collapsed_v_occurrences':0,
             'reference_overlap_removed_sentences':len(removed),'reference_unsupported_removed_sentences':len(unsupported)}, cap)
    return {'capacity_status':cap['status'],'source_paragraphs_reconstructed':len(kept),
            'source_words_reconstructed':sum(len(p['words']) for p in kept),
            'source_sentences_reconstructed':sum(len(p['source_sentence_ids']) for p in kept),
            'reference_sentences_reconstructed':len(native),'reference_words_reconstructed':sum(map(len,native)),
            'reference_native_v_characters':v,'reference_collapsed_v_characters':0,
            'citation_reuse_events_verified':sum(n-1 for n in occurrences.values()),
            'distinct_reused_citation_labels_verified':sum(n>1 for n in occurrences.values()),
            'source_capacity_sha256':sha(data/'prepared/CAPACITY.json')}


def freeze_audit(data, spec):
    reg, lock = obj(SRC/'PREREG_LOCK.json'), obj(data/'artifacts/FIT_LOCK.json')
    for section, folder in [('sha256',BASE),('upstream_sha256',ROOT)]:
        for name, digest in reg[section].items():
            path = (folder/name).resolve()
            check(path.is_relative_to(folder) and sha(path)==digest, 'Registered implementation/input hash')
    check(lock['spec_sha256']==sha(SRC/'SPEC.json'), 'Frozen numerical protocol')
    expected_restarts = {f'artifacts/fits/world_{w}_{c}_start{s}.json' for w in spec['world_ids'] for c in CONDITIONS for s in spec['starts']}
    expected_selected = {f'artifacts/fits/world_{w}_{c}_selected.json' for w in spec['world_ids'] for c in CONDITIONS}
    check(set(lock['restarts'])==expected_restarts and len(lock['restarts'])==48, 'All 48 unique restart paths')
    check(set(lock['selected'])==expected_selected and len(lock['selected'])==6, 'All six unique selected paths')
    check(set(lock['sha256'])==expected_restarts|expected_selected, 'Exact complete fit commitment inventory')
    for name, digest in lock['sha256'].items():
        check(sha(data/name)==digest, 'Frozen fit bytes')
    candidates = obj(data/'prepared/candidates.json')
    fits, selected = [obj(data/p) for p in sorted(expected_restarts)], [obj(data/p) for p in sorted(expected_selected)]
    for fit in fits+selected:
        check(fit['schema']=='GDT833_FIT_V1' and fit['engine_arm']=='OFF', 'Frozen fit method')
        check(fit['seed']==83300000+100*fit['world_id']+fit['start'], 'Paired seed')
        legal_key(fit['key'], candidates)
        check(fit['input_hashes']['discovery_input_sha256']==sha(data/f"prepared/world_{fit['world_id']}_discovery.json"), 'Only discovery ciphertext bound to fitting')
        check(fit['input_hashes']['spec_sha256']==sha(SRC/'SPEC.json'), 'Fit specification binding')
        check(fit['input_hashes']['decoder_source_sha256']==sha(ROOT/'experiments/yolo/gdt832_joint_family_context_control/src/decoder.cpp'), 'Unchanged decoder binding')
    for selected_fit in selected:
        group = [f for f in fits if (f['world_id'],f['reference_condition'])==(selected_fit['world_id'],selected_fit['reference_condition'])]
        check(len(group)==8 and {f['start'] for f in group}==set(spec['starts']), 'Complete paired starts')
        check(selected_fit==sorted(group,key=lambda f:(-f['discovery_objective']['total_nats'],f['start']))[0], 'Independent discovery-only fit selection')
    # No held payload or world truth is opened until all preceding fit checks pass.
    check({f'prepared/world_{w}_held.json' for w in spec['world_ids']}<=set(reg['held_commitments']), 'Held commitments complete')
    check({'sealed/source_truth.json'}|{f'sealed/world_{w}_truth.json' for w in spec['world_ids']}<=set(reg['sealed_commitments']), 'Source/key commitments complete')
    for section in ('held_commitments','sealed_commitments'):
        for name,digest in reg[section].items():
            path = (data/name).resolve()
            check(path.is_relative_to(data.resolve()) and sha(path)==digest, 'Post-lock held/truth commitment verification')
    return fits, selected


def legal_key(key, candidates):
    check(set(key)=={f'{kind}{i:02d}' for kind,n in [('L',26),('S',4),('W',8)] for i in range(n)}, 'Complete key identifier set')
    for kind, pool in [('L',set('abcdefghijklmnopqrstuvwxyz')),('S',set(candidates['suffix_pool'])),('W',set(candidates['wholeword_pool']))]:
        values = [v for k,v in key.items() if k[0]==kind]
        check(len(set(values))==len(values) and set(values)<=pool, 'Independent injective candidate-space audit')


def levenshtein(left, right):
    matrix = [list(range(len(right)+1))]
    for i,a in enumerate(left):
        row = [i+1]
        for j,b in enumerate(right):
            row.append(min(matrix[-1][j+1]+1,row[-1]+1,matrix[-1][j]+(a!=b)))
        matrix.append(row)
    return matrix[-1][-1]


def metrics(pairs):
    good = sum(a==b for a,b in pairs)
    error = sum(levenshtein(a,b) for a,b in pairs)
    chars = sum(max(len(a),len(b)) for a,b in pairs)
    forms = {a for a,b in pairs}
    badforms = {a for a,b in pairs if a!=b}
    return {'words':len(pairs),'exact_words':good,'word_accuracy':good/len(pairs) if pairs else None,
            'edit_distance':error,'character_denominator':chars,'character_accuracy':1-error/chars if chars else None,
            'truth_types':len(forms),'fully_correct_truth_types':len(forms-badforms),
            'truth_type_accuracy':len(forms-badforms)/len(forms) if forms else None}


def objective(cipher,key,model):
    score = 0.0
    for paragraph in cipher['paragraphs']:
        previous = None
        for codes in paragraph['words']:
            word = ''.join(key[code] for code in codes)
            score += model.log_conditional(previous,word)
            previous = word
    return score


def world_audit(data, world, encoder, source):
    truth = obj(data/f'sealed/world_{world}_truth.json')
    check(truth['world_id']==world and truth['paragraphs']==source['paragraphs'], 'Shared original gold for both reference conditions')
    check(truth['source_truth_sha256']==sha(data/'sealed/source_truth.json') and truth['encoder_spec_sha256']==sha(SRC/'ENCODER_SPEC.json'), 'Generated truth source binding')
    # Reconstruct source-independent random IDs without calling the generator.
    rng, key = random.Random(world), {}
    for kind, values in [('L',list(encoder['letter_alphabet'])),('S',encoder['suffix_values']),('W',encoder['wholeword_values'])]:
        cards = [f'{kind}{i:02d}' for i in range(len(values))]
        rng.shuffle(cards)
        key.update(zip(cards,values))
    check(key==truth['decode_map'], 'Independent exact seeded generator key')
    inverse = {(k[0],v):k for k,v in key.items()}
    payloads = {}
    for split in ('discovery','held'):
        path = data/f'prepared/world_{world}_{split}.json'
        check(sha(path)==truth['ciphertext_sha256'][split], 'Single shared ciphertext binding')
        cipher = obj(path)
        expected = [{'paragraph_id':p['paragraph_id'],'words':[[inverse[a] for a in logical_atoms(w,encoder)] for w in p['words']]} for p in source['paragraphs'] if p['split']==split]
        check(cipher['schema']=='GDT833_CIPHERTEXT_V1' and cipher['world_id']==world and cipher['split']==split and cipher['paragraphs']==expected, 'Independent exact original-spelling ciphertext generation')
        payloads[split] = cipher
    return key,payloads


def held_audit(fit, key, cipher, source, model):
    d,h = cipher['discovery'],cipher['held']
    previous = [p for p in source['paragraphs'] if p['split']=='discovery']
    forms = {w for p in previous for w in p['words']}
    lemmas = {a for p in previous for aa in p['lemma_sets'] if aa for a in aa}
    gold = {p['paragraph_id']:p for p in source['paragraphs'] if p['split']=='held'}
    buckets = {name:[] for name in ('all','v_words','non_v_words','novel_forms','novel_lemmas')}
    paragraphs_correct = 0
    for p in h['paragraphs']:
        original = gold[p['paragraph_id']]
        correctness = []
        for codes,word,analysis in zip(p['words'],original['words'],original['lemma_sets']):
            predicted = ''.join(fit['key'][c] for c in codes)
            pair = (word,predicted)
            correctness.append(word==predicted)
            buckets['all'].append(pair)
            buckets['v_words' if 'v' in word else 'non_v_words'].append(pair)
            composed = all(c[0]!='W' for c in codes)
            if composed and word not in forms:
                buckets['novel_forms'].append(pair)
            if composed and analysis is not None and len(analysis)==1 and analysis[0] not in lemmas:
                buckets['novel_lemmas'].append(pair)
        paragraphs_correct += all(correctness)
    support = Counter(c for p in d['paragraphs'] for word in p['words'] for c in word)
    check({c for p in h['paragraphs'] for word in p['words'] for c in word}<=set(support), 'Identifiable held-active key domain')
    active = []
    for kind in 'LSW':
        codes = {c for c in support if c[0]==kind}
        correct = {c for c in codes if fit['key'][c]==key[c]}
        active.append({'kind':kind,'supported_rules':len(codes),'exact_supported_rules':len(correct),
                       'supported_rule_accuracy':len(correct)/len(codes) if codes else None,
                       'discovery_mass_accuracy':sum(support[c] for c in correct)/sum(support[c] for c in codes) if codes else None})
    v = next(c for c,value in key.items() if c[0]=='L' and value=='v')
    # Swap output symbols globally: this remains a permutation even if z is unseen.
    mutant = {c:('z' if value=='v' else 'v' if value=='z' else value) if c[0]=='L' else value for c,value in key.items()}
    check(len({value for c,value in mutant.items() if c[0]=='L'})==26, 'Oracle mutation is legal bijection')
    oracle, swapped, fitted = objective(d,key,model), objective(d,mutant,model), objective(d,fit['key'],model)
    return {'world_id':fit['world_id'],'reference_condition':fit['reference_condition'],
            'selected_start':fit['start'],'selected_seed':fit['seed'],
            'recovery':{name:metrics(pairs) for name,pairs in buckets.items()},
            'held_paragraphs':len(gold),'exact_held_paragraphs':paragraphs_correct,
            'active_key_accuracy':active,'v_key_output':fit['key'][v],'v_key_correct':fit['key'][v]=='v',
            'oracle_true_nats':oracle,'oracle_vz_swap_nats':swapped,'oracle_margin':oracle-swapped,
            'selected_objective_nats':fitted,'selected_minus_oracle':fitted-oracle}


def decision_audit(rows, spec):
    s,r = spec['specific_effect'],spec['overall_recovery']
    lookup = {(x['world_id'],x['reference_condition']):x for x in rows}
    gains,secondary,primary,overall = [],[],[],[]
    for w in spec['world_ids']:
        n,c = lookup[w,'NATIVE'],lookup[w,'COLLAPSED']
        gains.append(n['recovery']['v_words']['word_accuracy']-c['recovery']['v_words']['word_accuracy'])
        secondary.append(n['recovery']['non_v_words']['word_accuracy']-c['recovery']['non_v_words']['word_accuracy'])
        primary.extend([n['recovery']['v_words']['word_accuracy']>=s['minimum_native_v_word_accuracy_each_key'],n['v_key_correct'],n['oracle_margin']>0,c['oracle_margin']<0])
        for subset, metric, floor in [('all','word_accuracy','minimum_word_accuracy_each_native_key'),('all','character_accuracy','minimum_character_accuracy_each_native_key'),('novel_forms','word_accuracy','minimum_novel_form_accuracy_each_native_key'),('novel_lemmas','word_accuracy','minimum_novel_lemma_accuracy_each_native_key')]:
            value = n['recovery'][subset][metric]
            overall.append(value is not None and value>=r[floor])
    mean = sum(gains)/len(gains)
    primary.extend([mean>=s['minimum_mean_v_word_gain']-1e-12,min(gains)>=s['minimum_each_key_v_word_gain']-1e-12])
    status = spec['decision_order'][1 if not all(primary) else 2 if not all(overall) else 3]
    return {'status':status,'specific_effect_pass':all(primary),'overall_recovery_pass':all(overall),
            'v_word_gain_per_world':gains,'mean_v_word_gain':mean,'non_v_word_gain_per_world':secondary,
            'three_keys_are_robustness_replicates_not_independent_texts':True,
            'gold_spelling_normalized_for_uv':False,'voynich_data_accessed':False}


def full_audit(data, model_root, fits, selected):
    source, spec, encoder = obj(data/'sealed/source_truth.json'),obj(SRC/'SPEC.json'),obj(SRC/'ENCODER_SPEC.json')
    path = ROOT/'experiments/yolo/gdt832_joint_family_context_control/src/reference_model.py'
    module_spec = importlib.util.spec_from_file_location('gdt833_validation_frozen_reference',path)
    module = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
    models = {c:module.load_model(model_root/('reference_'+c.lower())) for c in CONDITIONS}
    for condition,model in models.items():
        check(model.metadata['input_hashes']['reference_jsonl_sha256']==sha(data/('prepared/reference_'+condition.lower()+'.jsonl')) and model.metadata['input_hashes']['families_json_sha256']==sha(data/'prepared/families.json'), 'Respective paired model source binding')
    worlds = {w:world_audit(data,w,encoder,source) for w in spec['world_ids']}
    for fit in fits:
        key,payloads = worlds[fit['world_id']]
        condition = fit['reference_condition']
        check(fit['input_hashes']['projection_sha256']==sha(model_root/f"world_{fit['world_id']}_discovery.txt"), 'Frozen runtime discovery projection')
        pp = payloads['discovery']['paragraphs']
        compare({'paragraphs':len(pp),'word_occurrences':sum(len(p['words']) for p in pp),
                 'word_types':len({tuple(w) for p in pp for w in p['words']})},fit['input_hashes'],'Independent fit input accounting')
        check(fit['input_hashes']['model_meta_sha256']==sha(model_root/('reference_'+condition.lower())/'model_meta.json'), 'Frozen fit respective reference model')
        score = objective(payloads['discovery'],fit['key'],models[condition])
        compare({'language_nats':score,'family_nats':0,'total_nats':score},fit['discovery_objective'],'Independent restart objective',1e-4)
    rows = [held_audit(fit,*worlds[fit['world_id']],source,models[fit['reference_condition']]) for fit in selected]
    result = obj(data/'artifacts/RESULT.json')
    compare(rows,result['condition_results'],'Independent selected prediction and oracle replay',1e-7)
    compare(decision_audit(rows,spec),result,'Independent scientific decision')
    check(result['fit_lock_sha256']==sha(data/'artifacts/FIT_LOCK.json'), 'Result freeze binding')
    return {'restart_objectives_replayed':len(fits),'selected_fits_replayed':len(rows),
            'held_word_predictions_replayed':sum(row['recovery']['all']['words'] for row in rows),
            'oracle_truth_and_legal_mutant_scores_replayed':2*len(rows),
            'scientific_status':result['status'],'specific_effect_pass':result['specific_effect_pass'],
            'overall_recovery_pass':result['overall_recovery_pass'],
            'fit_lock_sha256':sha(data/'artifacts/FIT_LOCK.json'), 'result_sha256':sha(data/'artifacts/RESULT.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=BASE)
    parser.add_argument('--source-dir',type=Path,default=ROOT/'.gdt833/repos/latin_udante')
    parser.add_argument('--model-root',type=Path,default=BASE/'runtime')
    parser.add_argument('--capacity-only',action='store_true')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    fits = selected = None
    if not args.capacity_only:
        fits, selected = freeze_audit(args.data_dir,obj(SRC/'SPEC.json'))
    result = {'schema':'GDT833_VALIDATION_V1','status':'VALIDATION_PASS',
              'mode':'SOURCE_CAPACITY_ONLY' if args.capacity_only else 'SOURCE_AND_LOCKED_FIT_REPLAY',
              **capacity_audit(args.data_dir,args.source_dir),
              'world_key_truth_opened':not args.capacity_only,'voynich_data_accessed':False}
    if not args.capacity_only:
        result.update(full_audit(args.data_dir,args.model_root,fits,selected))
    target = args.data_dir/'artifacts'/('SOURCE_VALIDATION.json' if args.capacity_only else 'VALIDATION.json')
    encoded = (json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    if args.check:
        check(target.read_bytes()==encoded, 'Independent validation artifact replay')
    else:
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(encoded)
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
