#!/usr/bin/env python3
"""Independent source, opaque-role, locked-fit and original-spelling audit.

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
ARMS = ('BLIND', 'TYPED')
CAPACITIES = {'L':26, 'S':4, 'W':8}


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


def positional_domains(cipher, ids):
    observed = defaultdict(list)
    for p in cipher['paragraphs']:
        for word in p['words']:
            check(bool(word), 'No empty ciphertext word')
            for i,code in enumerate(word):
                check(code in ids, 'Complete anonymous code inventory')
                observed[code].append((i,len(word)))
    return {code:({'L'} | ({'W'} if all(n==1 for i,n in observed[code]) else set()) |
                  ({'S'} if all(n>=4 and i==n-1 for i,n in observed[code]) else set())) for code in ids}


def active_role_equivalence(cipher, truth_key, candidates):
    """Independent capacitated matching audit of same-emission role options.

    Unlike evaluator enumeration, each proposed role is tested by a max-flow
    network. Code→(role, output)→role edges enforce candidate membership,
    same-role injection and the complete nominal role capacities.
    """
    active = sorted({c for p in cipher['paragraphs'] for word in p['words'] for c in word})
    inactive = sorted(set(truth_key)-set(active))
    check(len(truth_key)==38, 'Full nominal inventory remains in the inverse problem')
    pools = {'L':set('abcdefghijklmnopqrstuvwxyz'),'S':set(candidates['suffix_pool']),'W':set(candidates['wholeword_pool'])}
    check(all(len(pools[r])>=CAPACITIES[r] for r in CAPACITIES), 'Unused slots can fill residual candidate capacity')
    geometry = positional_domains(cipher,truth_key)
    allowed = {code:sorted(r for r in geometry[code] if truth_key[code]['output'] in pools[r]) for code in active}
    def feasible(forced=None):
        residual = defaultdict(dict)
        def edge(a,b,n):
            residual[a][b]=n; residual[b].setdefault(a,0)
        source, sink = ('source',),('sink',)
        for code in active:
            node = ('code',code)
            edge(source,node,1)
            for role in allowed[code]:
                if forced is not None and code==forced[0] and role!=forced[1]:
                    continue
                value = truth_key[code]['output']
                edge(node,('value',role,value),1)
                edge(('value',role,value),('role',role),1)
        for role,n in CAPACITIES.items():
            edge(('role',role),sink,n)
        total=0
        while True:
            parents={source:None}; queue=[source]
            for a in queue:
                for b,n in residual[a].items():
                    if n>0 and b not in parents:
                        parents[b]=a; queue.append(b)
                if sink in parents:
                    break
            if sink not in parents:
                return total==len(active)
            node=sink
            while parents[node] is not None:
                parent=parents[node]
                residual[parent][node]-=1; residual[node][parent]+=1; node=parent
            total+=1
    check(feasible(), 'Independent same-emission feasibility')
    possible={code:[r for r in allowed[code] if feasible((code,r))] for code in active}
    return {'role_options':possible,'identifiable_ids':[c for c in active if len(possible[c])==1],
            'ambiguous_ids':[c for c in active if len(possible[c])>1], 'inactive_ids':inactive}


def levenshtein(left, right):
    row = list(range(len(right)+1))
    for i,a in enumerate(left,1):
        previous,row=row,[i]
        for j,b in enumerate(right,1):
            row.append(min(previous[j]+1,row[-1]+1,previous[j-1]+(a!=b)))
    return row[-1]


def metrics(pairs):
    good=sum(a==b for a,b in pairs)
    errors=sum(levenshtein(a,b) for a,b in pairs)
    chars=sum(max(len(a),len(b)) for a,b in pairs)
    types={a for a,b in pairs}; bad={a for a,b in pairs if a!=b}
    return {'words':len(pairs),'exact_words':good,'word_accuracy':good/len(pairs) if pairs else None,
            'edit_distance':errors,'character_denominator':chars,'character_accuracy':1-errors/chars if chars else None,
            'truth_types':len(types),'fully_correct_truth_types':len(types-bad),
            'truth_type_accuracy':len(types-bad)/len(types) if types else None}


def objective(cipher,key,model):
    total=0.0
    for p in cipher['paragraphs']:
        previous=None
        for word in p['words']:
            decoded=''.join(key[c]['output'] for c in word)
            total+=model.log_conditional(previous,decoded)
            previous=decoded
    return total


def cipher_path(data,world,arm,split):
    return data/f'prepared/world_{world}_{"typed_" if arm=="TYPED" else ""}{split}.json'


def key_check(key,cipher,candidates,arm):
    required={f'X{i:02d}' for i in range(38)} if arm=='BLIND' else {f'{r}{i:02d}' for r,n in CAPACITIES.items() for i in range(n)}
    check(set(key)==required,'Complete nominal ID inventory')
    compare(dict(Counter(row['role'] for row in key.values())),CAPACITIES,'Exact role counts')
    pools={'L':set('abcdefghijklmnopqrstuvwxyz'),'S':set(candidates['suffix_pool']),'W':set(candidates['wholeword_pool'])}
    geometry=positional_domains(cipher,key)
    for code,row in key.items():
        check(row['role'] in geometry[code] and row['output'] in pools[row['role']],'Candidate and public position legality')
        if arm=='TYPED':
            check(row['role']==code[0],'Typed side information honored')
    for role,n in CAPACITIES.items():
        check(len({row['output'] for row in key.values() if row['role']==role})==n,'Per-role output injection')


def frozen_fits(data,spec):
    reg,lock=obj(SRC/'PREREG_LOCK.json'),obj(data/'artifacts/FIT_LOCK.json')
    for section,folder in [('sha256',BASE),('upstream_sha256',ROOT)]:
        for name,digest in reg[section].items():
            path=(folder/name).resolve()
            check(path.is_relative_to(folder) and sha(path)==digest,'Registered implementation and input hashes')
    restarts={f'artifacts/fits/world_{w}_{a}_start{s}.json' for w in spec['world_ids'] for a in ARMS for s in spec['starts']}
    selected={f'artifacts/fits/world_{w}_{a}_selected.json' for w in spec['world_ids'] for a in ARMS}
    check(set(lock['restarts'])==restarts and len(lock['restarts'])==48,'Exact 48 restart commitments')
    check(set(lock['selected'])==selected and len(lock['selected'])==6,'Exact six selected commitments')
    check(set(lock['sha256'])==restarts|selected and lock['spec_sha256']==sha(SRC/'SPEC.json'),'Exact freeze inventory and numerical protocol')
    for name,digest in lock['sha256'].items():
        check(sha(data/name)==digest,'Frozen fit content')
    fits=[obj(data/name) for name in sorted(restarts)]
    chosen=[obj(data/name) for name in sorted(selected)]
    candidates=obj(data/'prepared/candidates.json')
    for fit in fits:
        check(fit['schema']=='GDT834_FIT_V1' and fit['world_id'] in spec['world_ids'] and fit['arm'] in ARMS,'Fit schema and identity')
        check(fit['seed']==83400000+100*fit['world_id']+fit['start'],'Paired fixed seed')
        discovery=cipher_path(data,fit['world_id'],fit['arm'],'discovery')
        key_check(fit['key'],obj(discovery),candidates,fit['arm'])
        compare({'cipher_sha256':sha(discovery),'decoder_sha256':sha(SRC/'decoder.cpp'),'spec_sha256':sha(SRC/'SPEC.json')},fit['input_hashes'],'Fit source bindings')
    for fit in chosen:
        group=[r for r in fits if (r['world_id'],r['arm'])==(fit['world_id'],fit['arm'])]
        check(len(group)==8 and {r['start'] for r in group}==set(spec['starts']),'All starts per condition')
        check(fit==sorted(group,key=lambda r:(-r['discovery_objective']['total_nats'],r['start']))[0],'Independent discovery-only selection')
    # Every fit and selection has passed before any held/key commitment is read.
    expected_h={cipher_path(data,w,a,'held').relative_to(data).as_posix() for w in spec['world_ids'] for a in ARMS}
    expected_s={'sealed/source_truth.json'}|{f'sealed/world_{w}_truth.json' for w in spec['world_ids']}
    check(expected_h<=set(reg['held_commitments']) and expected_s<=set(reg['sealed_commitments']),'Complete held and source/key commitments')
    for section in ('held_commitments','sealed_commitments'):
        for name,digest in reg[section].items():
            path=(data/name).resolve()
            check(path.is_relative_to(data.resolve()) and sha(path)==digest,'Post-freeze held/key commitments')
    return fits,chosen


def held_metrics(fit,key,discovery,held,source,candidates,model):
    d=[p for p in source['paragraphs'] if p['split']=='discovery']
    h=[p for p in source['paragraphs'] if p['split']=='held']
    compare([p['paragraph_id'] for p in h],[p['paragraph_id'] for p in held['paragraphs']],'Held source identity and ordering')
    forms={w for p in d for w in p['words']}
    lemmas={a for p in d for aa in p['lemma_sets'] if aa for a in aa}
    pairs={name:[] for name in ('all','novel_forms','novel_lemmas')}
    whole_paragraphs=0
    for cp,gp in zip(held['paragraphs'],h):
        check(len(cp['words'])==len(gp['words'])==len(gp['lemma_sets']),'Held word alignment')
        correct=[]
        for codes,gold,aa in zip(cp['words'],gp['words'],gp['lemma_sets']):
            check(''.join(key[c]['output'] for c in codes)==gold,'Original orthography roundtrip')
            predicted=''.join(fit['key'][c]['output'] for c in codes)
            pair=(gold,predicted); pairs['all'].append(pair); correct.append(gold==predicted)
            composed=not any(key[c]['role']=='W' for c in codes)
            if composed and gold not in forms:
                pairs['novel_forms'].append(pair)
            if composed and aa is not None and len(aa)==1 and aa[0] not in lemmas:
                pairs['novel_lemmas'].append(pair)
        whole_paragraphs+=all(correct)
    supported=Counter(c for p in discovery['paragraphs'] for word in p['words'] for c in word)
    check({c for p in held['paragraphs'] for word in p['words'] for c in word}<=set(supported),'No held-only active parameter')
    eq=active_role_equivalence(discovery,key,candidates)
    confusion=Counter((key[c]['role'],fit['key'][c]['role']) for c in supported)
    active=[]
    for role in CAPACITIES:
        codes={c for c in supported if key[c]['role']==role}
        rc={c for c in codes if fit['key'][c]['role']==role}
        oc={c for c in codes if fit['key'][c]['output']==key[c]['output']}
        both=rc&oc
        active.append({'role':role,'supported_rules':len(codes),'exact_roles':len(rc),'exact_outputs':len(oc),
                       'exact_role_and_outputs':len(both),'role_accuracy':len(rc)/len(codes) if codes else None,
                       'output_accuracy':len(oc)/len(codes) if codes else None,
                       'role_output_accuracy':len(both)/len(codes) if codes else None,
                       'discovery_mass_role_output_accuracy':sum(supported[c] for c in both)/sum(supported[c] for c in codes) if codes else None})
    correct_ids=sum(fit['key'][c]==key[c] for c in eq['identifiable_ids'])
    n=len(eq['identifiable_ids']); oracle=objective(discovery,key,model); fitted=objective(discovery,fit['key'],model)
    return {'world_id':fit['world_id'],'arm':fit['arm'],'selected_start':fit['start'],'selected_seed':fit['seed'],
            'recovery':{name:metrics(rows) for name,rows in pairs.items()},
            'held_paragraphs':len(h),'exact_held_paragraphs':whole_paragraphs,
            'active_key_accuracy':active,'role_confusion':[{'true_role':a,'predicted_role':b,'codes':n} for (a,b),n in sorted(confusion.items())],
            'same_emission_role_equivalence':eq,'identifiable_active_rules':n,
            'exact_identifiable_role_outputs':correct_ids,'identifiable_role_output_accuracy':correct_ids/n if n else None,
            'all_identifiable_role_outputs_correct':n>0 and correct_ids==n,
            'oracle_true_nats':oracle,'selected_objective_nats':fitted,'selected_minus_oracle':fitted-oracle}


def scientific_decision(rows,spec):
    limits=spec['overall_recovery']; tests={a:[] for a in ARMS}; roles=[]
    for row in rows:
        for subset,metric,limit in [('all','word_accuracy','minimum_word_accuracy_each_key'),('all','character_accuracy','minimum_character_accuracy_each_key'),('novel_forms','word_accuracy','minimum_novel_form_accuracy_each_key'),('novel_lemmas','word_accuracy','minimum_novel_lemma_accuracy_each_key')]:
            value=row['recovery'][subset][metric]
            tests[row['arm']].append(value is not None and value>=limits[limit])
        if row['arm']=='BLIND':
            roles.append(row['all_identifiable_role_outputs_correct'])
    typed,blind=all(tests['TYPED']),all(tests['BLIND'])
    status=spec['decision_order'][2 if not typed else 3 if not(blind and all(roles)) else 4]
    return {'status':status,'typed_recovery_pass':typed,'blind_recovery_pass':blind,
            'blind_identifiable_role_output_pass':all(roles),'known_boundaries_and_nominal_role_counts_supplied':True,
            'three_keys_share_one_source_split':True,'gold_spelling_normalized_for_uv':False,'voynich_data_accessed':False}


def logical_word(word, encoder):
    if word in encoder['wholeword_values']:
        return [('W',word)]
    for suffix in encoder['suffix_values']:
        if word.endswith(suffix) and len(word)-len(suffix)>=encoder['suffix_minimum_stem_characters']:
            return [('L',c) for c in word[:-len(suffix)]]+[('S',suffix)]
    return [('L',c) for c in word]


def source_capacity(data,source_dir):
    encoder,cap,manifest=obj(SRC/'ENCODER_SPEC.json'),obj(data/'prepared/CAPACITY.json'),obj(data/'sources/MANIFEST.json')
    for name,info in manifest['files'].items():
        check(sha(source_dir/name)==info['sha256'] and (source_dir/name).stat().st_size==info['bytes'],'Pinned historical source bytes')
    for field in ('source_helper','transitive_GDT832_helper'):
        check(sha(ROOT/manifest[field]['path'])==manifest[field]['sha256'],'Frozen source helper')
    for name,binding in manifest['reference_bindings'].items():
        check(sha(ROOT/binding['source'])==binding['sha256']==sha(data/'prepared'/name),'Unchanged previous native reference/candidates')
    check(sha(data/'sealed/source_truth.json')==cap['source_truth_sha256'] and sha(data/'sources/MANIFEST.json')==cap['sources_manifest_sha256'] and sha(SRC/'ENCODER_SPEC.json')==cap['encoder_spec_sha256'],'Capacity source commitments')
    for name,digest in cap['prepared_input_sha256'].items():
        check(sha(data/'prepared'/name)==digest,'Prepared source commitments')
    source=obj(data/'sealed/source_truth.json')
    rebuilt=[]; last=None; reuse=Counter()
    for comments,tokens in conllu(source_dir/manifest['source_file']):
        check(comments['sent_id'].startswith(encoder['source_work']+'-'),'Fixed Epistolae source work')
        citation=comments['citation_hierarchy']; parts=citation.split(',')
        check(len(parts)==2 and parts[1].startswith('Paragraphus_'),'Original two-part citation')
        check(parts[0] in encoder['discovery_letters']+encoder['held_letters'],'Fixed whole-letter source split')
        if citation!=last:
            reuse[citation]+=1
            pid='Epi:'+':'.join(parts)+((':occurrence_'+str(reuse[citation])) if reuse[citation]>1 else '')
            rebuilt.append({'paragraph_id':pid,'letter':parts[0],'citation_hierarchy':citation,'citation_occurrence':reuse[citation],
                            'split':'discovery' if parts[0] in encoder['discovery_letters'] else 'held',
                            'words':[],'lemma_sets':[],'annotation_status':[],'source_sentence_ids':[],'sentence_word_spans':[]})
            last=citation
        words,analyses,statuses=source_sentence(comments,tokens); p=rebuilt[-1]
        p['sentence_word_spans'].append([len(p['words']),len(p['words'])+len(words)])
        p['words'].extend(words); p['lemma_sets'].extend(analyses); p['annotation_status'].extend(statuses)
        p['source_sentence_ids'].append(comments['sent_id'])
    excluded=[p for p in rebuilt if any(re.fullmatch('[a-z]+',w) is None for w in p['words'])]
    kept=[p for p in rebuilt if p not in excluded]
    compare(kept,source['paragraphs'],'Independent original citation-run/annotation reconstruction')
    compare([{'paragraph_id':p['paragraph_id'],'split':p['split'],'reason':'UNREPRESENTABLE_ALPHABETIC_WORD','words':len(p['words'])} for p in excluded],cap['excluded_control_paragraphs'])
    compare(sum(len(p['source_sentence_ids']) for p in rebuilt),cap['control_sentences_before_exclusion'])
    compare(sum(n-1 for n in reuse.values()),cap['control_noncontiguous_citation_reuse_events'])
    compare(sum(n>1 for n in reuse.values()),cap['control_distinct_reused_citation_labels'])
    forms={w for p in kept if p['split']=='discovery' for w in p['words']}
    lemmas={a for p in kept if p['split']=='discovery' for aa in p['lemma_sets'] if aa for a in aa}
    support={s:Counter() for s in ('discovery','held')}; partitions={}
    for split in support:
        pp=[p for p in kept if p['split']==split]
        for p in pp:
            flags={'novel_form':[w not in forms for w in p['words']],
                   'novel_lemma':[None if aa is None or len(aa)!=1 else aa[0] not in lemmas for aa in p['lemma_sets']],
                   'composed':[w not in encoder['wholeword_values'] for w in p['words']]}
            compare(flags,next(q for q in source['paragraphs'] if q['paragraph_id']==p['paragraph_id']),'Independent novelty and composition tags')
            for w in p['words']:
                support[split].update(logical_word(w,encoder))
        flat=[w for p in pp for w in p['words']]
        partitions[split]={'paragraphs':len(pp),'sentences':sum(len(p['source_sentence_ids']) for p in pp),'words':len(flat),'types':len(set(flat)),
            'novel_composed_form_occurrences':sum(w not in forms and w not in encoder['wholeword_values'] for w in flat),
            'known_novel_lemma_occurrences':sum(aa is not None and len(aa)==1 and aa[0] not in lemmas for p in pp for aa in p['lemma_sets']),
            'novel_composed_lemma_occurrences':sum(w not in encoder['wholeword_values'] and aa is not None and len(aa)==1 and aa[0] not in lemmas for p in pp for w,aa in zip(p['words'],p['lemma_sets'])),
            'unknown_lemma_occurrences':sum(aa is None or len(aa)!=1 for p in pp for aa in p['lemma_sets']),
            'annotation_status_counts':dict(Counter(s for p in pp for s in p['annotation_status']))}
    compare(partitions,cap['partitions'],'Independent partition capacity counts')
    compare({s:[{'role':r,'output':v,'occurrences':n} for (r,v),n in sorted(c.items())] for s,c in support.items()},source['logical_rule_support'],'Independent logical generator support')
    stats={}; active=set(support['discovery'])|set(support['held'])
    for role,total in CAPACITIES.items():
        aa={c for c in active if c[0]==role}; hh={c for c in support['held'] if c[0]==role}
        stats[role]={'nominal_rules':total,'active_rules':len(aa),'inactive_unscored_rules':total-len(aa),
                     'minimum_discovery_occurrences_active_rules':min((support['discovery'][c] for c in aa),default=0),
                     'minimum_discovery_occurrences_held_active_rules':min((support['discovery'][c] for c in hh),default=0),
                     'held_only_rules':sum(support['discovery'][c]==0 for c in hh)}
    compare(stats,cap['rule_support'],'Independent supported role accounting')
    reference=[json.loads(line) for line in (data/'prepared/reference.jsonl').read_text().splitlines()]
    candidates=obj(data/'prepared/candidates.json')
    check(obj(data/'prepared/families.json')=={},'Family factor remains absent')
    width=encoder['deduplication_audit_words']
    grams={tuple(p['words'][i:i+width]) for p in kept for i in range(len(p['words'])-width+1)}
    overlap=sum(any(tuple(sentence[i:i+width]) in grams for i in range(len(sentence)-width+1)) for sentence in reference)
    compare({'reference_sentences':len(reference),'reference_words':sum(map(len,reference)),'reference_sentences_with_exact20word_control_overlap':overlap},cap,'Frozen-reference overlap accounting')
    missing=set(encoder['wholeword_values'])-set(candidates['wholeword_pool'])
    compare(sorted(missing),source['missing_wholeword_candidates'])
    gates={'discovery_citation_runs':partitions['discovery']['paragraphs']>=encoder['minimum_discovery_paragraphs'],
           'held_citation_runs':partitions['held']['paragraphs']>=encoder['minimum_held_paragraphs'],
           'active_suffix_discovery_coverage':stats['S']['minimum_discovery_occurrences_active_rules']>=encoder['minimum_discovery_occurrences_active_suffix_or_wholeword'],
           'active_wholeword_discovery_coverage':stats['W']['minimum_discovery_occurrences_active_rules']>=encoder['minimum_discovery_occurrences_active_suffix_or_wholeword'],
           'held_active_literal_discovery_coverage':stats['L']['minimum_discovery_occurrences_held_active_rules']>=encoder['minimum_discovery_occurrences_held_active_literal'],
           'held_novel_composed_forms':partitions['held']['novel_composed_form_occurrences']>=encoder['minimum_held_novel_composed_form_occurrences'],
           'held_unambiguous_novel_composed_lemmas':partitions['held']['novel_composed_lemma_occurrences']>=encoder['minimum_held_unambiguous_novel_composed_lemma_occurrences'],
           'wholeword_truth_in_frozen_candidate_pool':not missing}
    compare(gates,cap['gates'],'Fixed source gates')
    compare(sorted(k for k,v in gates.items() if not v),cap['failed_gates'])
    check(cap['status']==('SOURCE_CAPACITY_PASS' if all(gates.values()) else 'SOURCE_CAPACITY_STOP'),'Source capacity decision')
    compare({'primitive_ids':[f'X{i:02d}' for i in range(38)]},obj(data/'prepared/inventory.json'),'Role-free full inventory')
    return {'source_capacity_status':cap['status'],'source_paragraphs_reconstructed':len(kept),
            'source_words_reconstructed':sum(len(p['words']) for p in kept),
            'source_sentences_reconstructed':sum(len(p['source_sentence_ids']) for p in kept),
            'reference_words_verified':sum(map(len,reference)),'exact20word_reference_overlap_sentences':overlap,
            'citation_reuse_events_verified':sum(n-1 for n in reuse.values()),
            'source_capacity_sha256':sha(data/'prepared/CAPACITY.json')}


def world_replay(data, world, source, encoder, candidates):
    truth=obj(data/f'sealed/world_{world}_truth.json')
    check(truth['world_id']==world and truth['paragraphs']==source['paragraphs'],'Original source gold shared between arms')
    typed={code:{'role':code[0],'output':value} for code,value in truth['typed_decode_map'].items()}
    opaque=truth['decode_map']; aliases=truth['opaque_to_typed']
    check(truth['source_truth_sha256']==sha(data/'sealed/source_truth.json') and truth['encoder_spec_sha256']==sha(SRC/'ENCODER_SPEC.json'),'Generated truth source binding')
    rng=random.Random(world); seeded={}
    for role,values in [('L',list(encoder['letter_alphabet'])),('S',encoder['suffix_values']),('W',encoder['wholeword_values'])]:
        ids=[f'{role}{i:02d}' for i in range(len(values))]; rng.shuffle(ids)
        seeded.update(zip(ids,values))
    check(seeded==truth['typed_decode_map'],'Independent source-free planted value randomization')
    shuffled=[f'X{i:02d}' for i in range(38)]
    random.Random(world+encoder['opaque_shuffle_seed_offset']).shuffle(shuffled)
    check(dict(zip(shuffled,sorted(seeded)))==aliases,'Independent full-inventory opaque randomization')
    check(set(aliases)==set(opaque) and set(aliases.values())==set(typed) and len(aliases)==38,'Global opaque alias bijection covers every nominal code')
    check(all(opaque[code]==typed[target] for code,target in aliases.items()),'Opaque and typed exact role/output identity')
    for role,values in [('L',list(encoder['letter_alphabet'])),('S',encoder['suffix_values']),('W',encoder['wholeword_values'])]:
        check({row['output'] for row in typed.values() if row['role']==role}==set(values),'Declared planted output decks')
    inverse={(row['role'],row['output']):code for code,row in typed.items()}
    to_opaque={v:k for k,v in aliases.items()}
    result={}
    for arm,key in [('TYPED',typed),('BLIND',opaque)]:
        payloads={}
        for split in ('discovery','held'):
            path=cipher_path(data,world,arm,split)
            packet=('typed_' if arm=='TYPED' else '')+split
            check(truth['ciphertext_sha256'][packet]==sha(path),'Truth-to-ciphertext commitments')
            cipher=obj(path)
            expected=[]
            for p in source['paragraphs']:
                if p['split']!=split:
                    continue
                encoded=[[inverse[a] for a in logical_word(word,encoder)] for word in p['words']]
                if arm=='BLIND':
                    encoded=[[to_opaque[a] for a in word] for word in encoded]
                expected.append({'paragraph_id':p['paragraph_id'],'words':encoded})
            check(cipher['world_id']==world and cipher['split']==split and cipher['paragraphs']==expected,'Independent exact source→typed/opaque generation')
            payloads[split]=cipher
        key_check(key,payloads['discovery'],candidates,arm)
        result[arm]=(key,payloads)
    return result


def full_replay(data,model_root,fits,selected):
    source,spec,encoder=obj(data/'sealed/source_truth.json'),obj(SRC/'SPEC.json'),obj(SRC/'ENCODER_SPEC.json')
    candidates=obj(data/'prepared/candidates.json')
    path=ROOT/'experiments/yolo/gdt832_joint_family_context_control/src/reference_model.py'
    module_spec=importlib.util.spec_from_file_location('gdt834_independent_reference_model',path)
    module=importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
    model=module.load_model(model_root/'reference')
    compare({'reference_jsonl_sha256':sha(data/'prepared/reference.jsonl'),'families_json_sha256':sha(data/'prepared/families.json')},model.metadata['input_hashes'],'Shared frozen reference')
    worlds={world:world_replay(data,world,source,encoder,candidates) for world in spec['world_ids']}
    for fit in fits:
        key,payloads=worlds[fit['world_id']][fit['arm']]
        discovery=payloads['discovery']; pp=discovery['paragraphs']
        compare({'model_meta_sha256':sha(model_root/'reference/model_meta.json'),
                 'projection_sha256':sha(model_root/f"world_{fit['world_id']}_{fit['arm']}.txt"),
                 'word_tokens':sum(len(p['words']) for p in pp),'word_types':len({tuple(w) for p in pp for w in p['words']})},fit['input_hashes'],'Frozen discovery runtime accounting')
        score=objective(discovery,fit['key'],model)
        compare({'total_nats':score,'language_nats':score,'family_nats':0},fit['discovery_objective'],'Independent restart objective',1e-4)
    rows=[]
    for fit in selected:
        key,pp=worlds[fit['world_id']][fit['arm']]
        rows.append(held_metrics(fit,key,pp['discovery'],pp['held'],source,candidates,model))
    result=obj(data/'artifacts/RESULT.json')
    compare(rows,result['condition_results'],'Independent held/oracle and max-flow role equivalence',1e-7)
    compare(scientific_decision(rows,spec),result,'Independent scientific decision')
    check(result['fit_lock_sha256']==sha(data/'artifacts/FIT_LOCK.json'),'Result freeze binding')
    return {'restart_objectives_replayed':len(fits),'selected_fits_replayed':len(selected),
            'held_word_predictions_replayed':sum(r['recovery']['all']['words'] for r in rows),
            'true_key_oracle_scores_replayed':len(rows),
            'identifiable_role_domains_checked_by_independent_max_flow':sum(len(r['same_emission_role_equivalence']['role_options']) for r in rows),
            'scientific_status':result['status'],'typed_recovery_pass':result['typed_recovery_pass'],
            'blind_recovery_pass':result['blind_recovery_pass'],
            'blind_identifiable_role_output_pass':result['blind_identifiable_role_output_pass'],
            'fit_lock_sha256':sha(data/'artifacts/FIT_LOCK.json'),'result_sha256':sha(data/'artifacts/RESULT.json')}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=BASE)
    parser.add_argument('--source-dir',type=Path,default=BASE/'runtime/udante_source')
    parser.add_argument('--model-root',type=Path,default=BASE/'runtime')
    parser.add_argument('--capacity-only',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args(); fits=selected=None
    if not args.capacity_only:
        fits,selected=frozen_fits(args.data_dir,obj(SRC/'SPEC.json'))
    result={'schema':'GDT834_VALIDATION_V1','status':'VALIDATION_PASS',
            'mode':'SOURCE_CAPACITY_ONLY' if args.capacity_only else 'SOURCE_AND_LOCKED_FIT_REPLAY',
            **source_capacity(args.data_dir,args.source_dir),
            'world_key_truth_opened':not args.capacity_only,'voynich_data_accessed':False}
    if not args.capacity_only:
        result.update(full_replay(args.data_dir,args.model_root,fits,selected))
    target=args.data_dir/'artifacts'/('SOURCE_VALIDATION.json' if args.capacity_only else 'VALIDATION.json')
    raw=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    if args.check:
        check(target.read_bytes()==raw,'Independent validation artifact replay')
    else:
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(raw)
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
