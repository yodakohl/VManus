#!/usr/bin/env python3
"""Independent fixed-source capacity STOP and engineering artifact audit.

This experiment stops before historical keys, ciphertext or fits are generated.
Engineering tests do not establish fresh historical recovery.
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
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

SRC = Path(__file__).resolve().parent
BASE = SRC.parent
ROOT = BASE.parents[2]
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


def conllu(path, work=None):
    comments, rows = {}, []
    with Path(path).open(encoding='utf-8') as stream:
        for raw in itertools.chain(stream, ['\n']):
            line = raw.rstrip('\r\n')
            if not line:
                if (comments or rows) and (work is None or comments.get('sent_id','').startswith(work+'-')):
                    yield comments, rows
                comments, rows = {}, []
            elif line.startswith('#'):
                if work is not None:
                    identity_prefix='# sent_id = '
                    if line.startswith(identity_prefix):
                        comments['sent_id']=line[len(identity_prefix):]
                        continue
                    if not comments.get('sent_id','').startswith(work+'-'):
                        continue
                match = re.fullmatch(r'# ([^=]+) = (.*)', line)
                if match:
                    comments[match[1].strip()] = match[2]
            else:
                if work is not None and not comments.get('sent_id','').startswith(work+'-'):
                    continue
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


def logical_atoms(word,spec):
    if word in spec['wholeword_values']:
        return [('W',word)]
    for suffix in spec['suffix_values']:
        if word.endswith(suffix) and len(word)-len(suffix)>=spec['suffix_minimum_stem_characters']:
            return [('L',c) for c in word[:-len(suffix)]]+[('S',suffix)]
    return [('L',c) for c in word]


def source_replay(data,source_dir):
    spec=obj(SRC/'ENCODER_SPEC.json'); cap=obj(data/'prepared/CAPACITY.json'); manifest=obj(data/'sources/MANIFEST.json')
    original=data/'prepared/INITIAL_CAPACITY.json'
    check(sha(original)=='f92960e81c7d00df316ad55c2f8c27c9579e88f8d79e556924a5e4d4da61f213','Immutable initial source STOP snapshot')
    raw=source_dir/manifest['control_source']['file']
    check(sha(raw)==manifest['control_source']['sha256'],'Pinned raw source')
    for section in ('helpers_sha256','frozen_reference_and_encoder_sha256'):
        for relative,digest in manifest[section].items():
            check(sha(ROOT/relative)==digest,'Unchanged inherited input')
    for filename,digest in manifest['raw_documentation'].items():
        check(sha(source_dir/filename)==digest==sha(data/'sources'/filename),'Pinned source documentation')
    compare({'original_initial_snapshot_sha256':sha(original),'encoder_spec_sha256':sha(SRC/'ENCODER_SPEC.json'),
             'source_manifest_sha256':sha(data/'sources/MANIFEST.json'),'paragraph_metadata_sha256':sha(data/'prepared/PARAGRAPHS.json')},cap,'Source artifact bindings')
    old=BASE.parent/'gdt834_role_blind_mixed_control'
    inherited=obj(old/'src/ENCODER_SPEC.json')
    for name in ('letter_alphabet','suffix_values','suffix_minimum_stem_characters','wholeword_values','precedence',
                 'minimum_discovery_paragraphs','minimum_held_paragraphs','minimum_discovery_occurrences_active_suffix_or_wholeword',
                 'minimum_discovery_occurrences_held_active_literal','minimum_held_novel_composed_form_occurrences',
                 'minimum_held_unambiguous_novel_composed_lemma_occurrences','deduplication_audit_words'):
        check(spec[name]==inherited[name],'Unchanged encoder or capacity threshold')
    check(spec['discovery_citation_numbers']==[1,44] and spec['held_citation_numbers']==[45,88],'Fixed mechanical midpoint')
    check(spec['source_work']=='Que','Fixed source work')
    rebuilt=[]; occurrences=Counter(); previous=None
    for comments,fields in conllu(raw,work='Que'):
        citation=comments['citation_hierarchy']; parts=citation.split(',')
        check(len(parts)==2 and parts[0]==spec['source_heading'],'Exact source heading')
        match=re.fullmatch(r'Paragraphus_([1-9][0-9]*)',parts[1]); check(match is not None,'Literal citation label')
        n=int(match[1]); check(1<=n<=88,'Fixed entire citation range')
        if citation!=previous:
            occurrences[citation]+=1
            rebuilt.append({'citation':citation,'occurrence':occurrences[citation],'split':'discovery' if n<=44 else 'held',
                            'words':[],'analyses':[],'statuses':[],'source_sentence_ids':[]})
            previous=citation
        words,analyses,statuses=source_sentence(comments,fields)
        p=rebuilt[-1]; p['words'].extend(words); p['analyses'].extend(analyses); p['statuses'].extend(statuses)
        p['source_sentence_ids'].append(comments['sent_id'])
    excluded=[p for p in rebuilt if any(re.fullmatch('[a-z]+',w) is None for w in p['words'])]
    kept=[p for p in rebuilt if p not in excluded]
    forms={w for p in kept if p['split']=='discovery' for w in p['words']}
    lemmas={a for p in kept if p['split']=='discovery' for aa in p['analyses'] if aa for a in aa}
    support={split:Counter() for split in ('discovery','held')}; partitions={}
    for split in support:
        pp=[p for p in kept if p['split']==split]
        flat=[w for p in pp for w in p['words']]
        for w in flat:
            support[split].update(logical_atoms(w,spec))
        partitions[split]={'paragraphs':len(pp),'sentences':sum(len(p['source_sentence_ids']) for p in pp),
            'words':len(flat),'types':len(set(flat)),
            'novel_composed_forms':sum(w not in forms and w not in spec['wholeword_values'] for w in flat),
            'unambiguous_novel_composed_lemmas':sum(w not in spec['wholeword_values'] and aa is not None and len(aa)==1 and aa[0] not in lemmas for p in pp for w,aa in zip(p['words'],p['analyses'])),
            'annotation_status_counts':dict(Counter(s for p in pp for s in p['statuses']))}
    active=set(support['discovery'])|set(support['held']); rules={}
    for role,nominal in CAPACITIES.items():
        all_rules={a for a in active if a[0]==role}; held_rules={a for a in support['held'] if a[0]==role}
        rules[role]={'nominal':nominal,'active':len(all_rules),'inactive':nominal-len(all_rules),
            'minimum_D_active_occurrences':min((support['discovery'][a] for a in all_rules),default=0),
            'minimum_D_held_active_occurrences':min((support['discovery'][a] for a in held_rules),default=0),
            'held_only_rules':sum(support['discovery'][a]==0 for a in held_rules),
            'active_rules_below_8_D':sum(support['discovery'][a]<8 for a in all_rules)}
    reference=[json.loads(line) for line in (old/'prepared/reference.jsonl').read_text().splitlines()]
    candidates=obj(old/'prepared/candidates.json')
    width=spec['deduplication_audit_words']
    windows={tuple(p['words'][i:i+width]) for p in kept for i in range(len(p['words'])-width+1)}
    overlap=sum(any(tuple(sentence[i:i+width]) in windows for i in range(len(sentence)-width+1)) for sentence in reference)
    missing=set(spec['wholeword_values'])-set(candidates['wholeword_pool'])
    gates={'D_runs':partitions['discovery']['paragraphs']>=spec['minimum_discovery_paragraphs'],
        'H_runs':partitions['held']['paragraphs']>=spec['minimum_held_paragraphs'],
        'active_S_8D':rules['S']['minimum_D_active_occurrences']>=spec['minimum_discovery_occurrences_active_suffix_or_wholeword'],
        'active_W_8D':rules['W']['minimum_D_active_occurrences']>=spec['minimum_discovery_occurrences_active_suffix_or_wholeword'],
        'held_active_L_1D':rules['L']['minimum_D_held_active_occurrences']>=spec['minimum_discovery_occurrences_held_active_literal'],
        'H_new_composed_forms_100':partitions['held']['novel_composed_forms']>=spec['minimum_held_novel_composed_form_occurrences'],
        'H_new_unambiguous_composed_lemmas_30':partitions['held']['unambiguous_novel_composed_lemmas']>=spec['minimum_held_unambiguous_novel_composed_lemma_occurrences'],
        'all_true_W_in_frozen_candidates':not missing,'reference_exact20_overlap_zero':overlap==0}
    initial={'status':'SOURCE_CAPACITY_PASS' if all(gates.values()) else 'SOURCE_CAPACITY_STOP',
        'gates':gates,'failed_gates':[k for k,v in gates.items() if not v],
        'split':'Que citation1-44 discovery/45-88 held, fixed before word/rule counts',
        'partitions':partitions,'rules':rules,'reference_exact20_overlap_sentences':overlap,
        'excluded_whole_paragraphs':[{'split':p['split'],'citation_id':p['citation']+':occurrence_'+str(p['occurrence']),'word_count':len(p['words'])} for p in excluded],
        'reused_citation_events':sum(n-1 for n in occurrences.values()),'missing_W_candidate_count':len(missing),'keys_generated':False}
    encoded=(json.dumps(initial,indent=2,sort_keys=True)+'\n').encode()
    check(encoded==original.read_bytes(),'Independent byte-exact first capacity snapshot reconstruction')
    compare(initial,cap,'Independent final capacity audit')
    metadata={'schema':'GDT836_PARAGRAPH_METADATA_V1','plaintext_included':False,'paragraphs':[
        {'paragraph_id':'Que:'+p['citation'].replace(',',':')+((':occurrence_'+str(p['occurrence'])) if p['occurrence']>1 else ''),
         'citation_hierarchy':p['citation'],'citation_occurrence':p['occurrence'],'split':p['split'],
         'source_sentence_ids':p['source_sentence_ids'],'word_count':len(p['words']),
         'annotation_status_counts':dict(Counter(p['statuses']))} for p in kept]}
    check(metadata==obj(data/'prepared/PARAGRAPHS.json'),'Independent paragraph metadata reconstruction')
    check(initial['status']=='SOURCE_CAPACITY_STOP' and cap['historical_fit_allowed'] is False,'Historical source stop must remain in force')
    return {'scientific_status':initial['status'],'failed_gates':initial['failed_gates'],
            'source_paragraphs_reconstructed':len(kept),'source_words_reconstructed':sum(len(p['words']) for p in kept),
            'source_sentences_reconstructed':sum(len(p['source_sentence_ids']) for p in kept),
            'held_only_literal_rules':rules['L']['held_only_rules'],'initial_snapshot_byte_exact':True,
            'initial_capacity_sha256':sha(original),'capacity_sha256':sha(data/'prepared/CAPACITY.json')}


def no_historical_artifacts(data):
    forbidden=['prepared/GENERATION.json','artifacts/FIT_LOCK.json','artifacts/FIT_INPUTS.json','sealed/source_truth.json']
    check(not any((data/path).exists() for path in forbidden),'No historical key/cipher/fit stage artifacts')
    patterns=['prepared/world_*','sealed/world_*','runtime/world_*','artifacts/fits/*']
    check(not any(list(data.glob(pattern)) for pattern in patterns),'No historical generated worlds or fits')
    return {'historical_cipher_key_fit_artifacts_present':False,'historical_fit_allowed':False}


def engineering_bindings(data):
    report=obj(data/'artifacts/ENGINEERING_TESTS.json')
    check(report['status']=='PASS' and type(report['tests']) is int and report['tests']>0,'Recorded synthetic engineering suite')
    required={'src/decoder.cpp','src/build_engine.py','src/test_constraint.py'}
    check(required<=set(report['sha256']),'Engineering suite bound to implementation and tests')
    for name,digest in report['sha256'].items():
        path=(data/name).resolve()
        check(path.is_relative_to(data.resolve()) and sha(path)==digest,'Current tested code bytes')
    completed=subprocess.run([sys.executable,str(data/'src/run.py'),'--fit'],capture_output=True,text=True)
    check(completed.returncode==2,'Source stop rejects historical fitting before initialization')
    response=json.loads(completed.stdout)
    compare({'status':'SOURCE_CAPACITY_STOP','historical_fits':0,'keys_generated':0},response,'Runtime source-stop guard')
    no_historical_artifacts(data)
    return {'engineering_test_report_status':report['status'],'recorded_synthetic_tests':report['tests'],
            'engineering_report_sha256':sha(data/'artifacts/ENGINEERING_TESTS.json'),
            'tested_source_sha256':report['sha256'],'source_stop_guard_exit_status':completed.returncode,
            'fresh_historical_recovery_tested':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=BASE)
    parser.add_argument('--source-dir',type=Path,default=BASE/'runtime/udante_source')
    parser.add_argument('--source-only',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result={'schema':'GDT836_VALIDATION_V1','status':'VALIDATION_PASS',
            **source_replay(args.data_dir,args.source_dir),**no_historical_artifacts(args.data_dir),
            'mode':'SOURCE_ONLY' if args.source_only else 'SOURCE_AND_ENGINEERING_BINDINGS',
            'voynich_data_accessed':False}
    if not args.source_only:
        result.update(engineering_bindings(args.data_dir))
    target=args.data_dir/'artifacts'/('SOURCE_VALIDATION.json' if args.source_only else 'VALIDATION.json')
    encoded=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    if args.check:
        check(target.read_bytes()==encoded,'Independent validation artifact replay')
    else:
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(encoded)
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
