#!/usr/bin/env python3
"""Independent SCG source, paired initialization and strict-control audit."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import re
import unicodedata

SRC=Path(__file__).resolve().parent
BASE=SRC.parent
ROOT=BASE.parents[2]
ARMS=('RELAXED','STRICT')
CAPACITIES={'L':26,'S':4,'W':8}


def check(ok,message):
    if not ok:
        raise ValueError(message)


def obj(path):
    path=Path(path)
    if path.suffix=='.gz':
        with gzip.open(path,'rt',encoding='utf-8') as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(expected,actual,where='artifact',tolerance=1e-8):
    if isinstance(expected,dict):
        check(isinstance(actual,dict),where+': object required')
        for key,value in expected.items():
            check(key in actual,where+': missing '+key)
            compare(value,actual[key],where+'.'+key,tolerance)
    elif isinstance(expected,list):
        check(isinstance(actual,list) and len(expected)==len(actual),where+': list size')
        for i,(left,right) in enumerate(zip(expected,actual)):
            compare(left,right,where+'['+str(i)+']',tolerance)
    elif isinstance(expected,bool) or expected is None:
        check(actual is expected,where+': boolean/null')
    elif isinstance(expected,(int,float)):
        check(isinstance(actual,(int,float)) and math.isfinite(actual) and abs(expected-actual)<=tolerance,where+': number')
    else:
        check(expected==actual,where+': value')


def canonical_words(text):
    folded = text.casefold().replace('æ', 'ae').replace('œ', 'oe')
    folded = ''.join(c for c in unicodedata.normalize('NFKD', folded)
                     if not unicodedata.combining(c))
    return re.findall(r'[^\W\d_]+', folded, flags=re.UNICODE)


def scg_sentences(path):
    """Select by reference metadata before parsing any source text/tokens.

    Reference metadata need not precede the #text line. Scan each block as
    bytes, then revisit and parse only blocks identified as SCG sentences.
    Separate forma concordances never enter the text/annotation parser.
    """
    with Path(path).open('rb') as stream:
        start=stream.tell(); reference=None
        while True:
            raw=stream.readline()
            if raw.startswith(b'# reference = '):
                reference=raw[len(b'# reference = '):].strip().decode('ascii')
            if not raw.strip():
                end=stream.tell()
                match=re.fullmatch(r'ittb-scg-s([1-9][0-9]*)',reference or '')
                if match:
                    stream.seek(start)
                    selected=stream.read(end-start).decode('utf-8')
                    comments,rows={},[]
                    for line in selected.splitlines():
                        if line.startswith('#'):
                            item=re.fullmatch(r'# ([^=]+) = (.*)',line)
                            if item:
                                comments[item[1].strip()]=item[2]
                        elif line:
                            fields=line.split('\t')
                            check(len(fields)==10,'Selected SCG CoNLL-U row shape')
                            rows.append(fields)
                    check(comments['reference']==reference,'Selected canonical source reference')
                    yield int(match[1]),comments,rows
                    stream.seek(end)
                if not raw:
                    break
                start=end; reference=None


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


def gzip_info(path):
    raw=Path(path).read_bytes()
    check(raw[:4]==b'\x1f\x8b\x08\x00' and raw[4:8]==b'\0'*4,'Deterministic gzip header')
    plain=gzip.decompress(raw)
    return {'compressed_sha256':hashlib.sha256(raw).hexdigest(),'compressed_bytes':len(raw),
            'uncompressed_sha256':hashlib.sha256(plain).hexdigest(),'uncompressed_bytes':len(plain)}


def logical_word(word,spec):
    if word in spec['wholeword_values']:
        return [('W',word)]
    for ending in spec['suffix_values']:
        if word.endswith(ending) and len(word)-len(ending)>=spec['suffix_minimum_stem_characters']:
            return [('L',c) for c in word[:-len(ending)]]+[('S',ending)]
    return [('L',c) for c in word]


def source_audit(data,source_dir):
    spec,cap,manifest=obj(SRC/'ENCODER_SPEC.json'),obj(data/'prepared/CAPACITY.json'),obj(data/'sources/MANIFEST.json')
    for name,digest in manifest['raw_source_sha256'].items():
        check(sha(source_dir/name)==digest,'Pinned raw source file')
    for name,digest in manifest['documentation_sha256'].items():
        check(sha(source_dir/name)==digest==sha(data/'sources'/name),'Pinned source documentation')
    for field in ('helpers_sha256','reference_sha256'):
        for name,digest in manifest[field].items():
            check(sha(ROOT/name)==digest,'Frozen inherited source resource')
    check(sha(ROOT/manifest['inherited_gates']['path'])==manifest['inherited_gates']['sha256'],'Unchanged source gate policy')
    inherited=obj(ROOT/manifest['inherited_gates']['path'])
    for field in ('letter_alphabet','suffix_values','suffix_minimum_stem_characters','wholeword_values','precedence',
                  'minimum_discovery_paragraphs','minimum_held_paragraphs','minimum_discovery_occurrences_active_suffix_or_wholeword',
                  'minimum_discovery_occurrences_held_active_literal','minimum_held_novel_composed_form_occurrences',
                  'minimum_held_unambiguous_novel_composed_lemma_occurrences','deduplication_audit_words'):
        check(spec[field]==inherited[field],'Unchanged source rule/threshold')
    check(spec['discovery_reference_range']==[1,9859] and spec['held_reference_range']==[9860,23687],'Fixed complete-book split')
    for name,digest in cap['prepared_input_sha256'].items():
        check(sha(data/'prepared'/name)==digest,'Prepared reference and inventory binding')
    compare({'encoder_spec_sha256':sha(SRC/'ENCODER_SPEC.json'),'source_prepare_sha256':sha(SRC/'prepare.py'),
             'source_manifest_sha256':sha(data/'sources/MANIFEST.json')},cap,'Capacity source bindings')
    check(sha(data/'prepared/INITIAL_CAPACITY.json')=='a2df568ffe0eeecfad8e39e91432ac7a3db5289871ebd61a283d49c84a7cde31','Immutable first source capacity snapshot')
    compare(gzip_info(data/'confirmation/source_truth.json.gz'),cap['shared_source_truth'])
    compare(gzip_info(data/'prepared/UNITS.json.gz'),cap['unit_metadata'])
    units,excluded,identities=[],[],[]
    excluded_forma=0
    for filename in sorted(manifest['raw_source_sha256']):
        # Count excluded identities using metadata bytes alone.
        with (source_dir/filename).open('rb') as stream:
            for line in stream:
                if line.startswith(b'# reference = '):
                    reference=line[len(b'# reference = '):].strip()
                    if re.fullmatch(rb'ittb-forma-s[1-9][0-9]*',reference):
                        excluded_forma+=1
                    else:
                        check(re.fullmatch(rb'ittb-scg-s[1-9][0-9]*',reference) is not None,'Only declared source work identities')
        for number,comments,fields in scg_sentences(source_dir/filename):
            identities.append(number)
            words,analyses,statuses=source_sentence(comments,fields)
            split='discovery' if number<=9859 else 'held'
            if any(re.fullmatch('[a-z]+',word) is None for word in words):
                excluded.append({'source_reference':comments['reference'],'split':split,'words':len(words)})
                continue
            book=next(book for book,(low,high) in spec['book_reference_ranges'].items() if low<=number<=high)
            units.append({'paragraph_id':f'SCG:s{number}','source_reference':comments['reference'],
                          'source_reference_number':number,'source_file':filename,'source_sentence_id':comments['sent_id'],
                          'book':book,'split':split,'words':words,'lemma_sets':analyses,'annotation_status':statuses})
    check(sorted(identities)==list(range(1,23688)),'Complete unique canonical source ordering')
    units.sort(key=lambda p:p['source_reference_number'])
    forms={word for p in units if p['split']=='discovery' for word in p['words']}
    lemmas={a for p in units if p['split']=='discovery' for aa in p['lemma_sets'] if aa for a in aa}
    partitions={};support={split:Counter() for split in ('discovery','held')}
    for split in support:
        selected=[p for p in units if p['split']==split]
        for p in selected:
            p['novel_form']=[word not in forms for word in p['words']]
            p['novel_lemma']=[None if aa is None or len(aa)!=1 else aa[0] not in lemmas for aa in p['lemma_sets']]
            p['composed']=[word not in spec['wholeword_values'] for word in p['words']]
            for word in p['words']:
                support[split].update(logical_word(word,spec))
        partitions[split]={'source_sentence_units':len(selected),'words':sum(len(p['words']) for p in selected),
            'types':len({word for p in selected for word in p['words']}),
            'novel_composed_forms':sum(new and composed for p in selected for new,composed in zip(p['novel_form'],p['composed'])),
            'unambiguous_novel_composed_lemmas':sum(new is True and composed for p in selected for new,composed in zip(p['novel_lemma'],p['composed'])),
            'annotation_status_counts':dict(Counter(s for p in selected for s in p['annotation_status']))}
    source=obj(data/'confirmation/source_truth.json.gz')
    check(source=={'schema':'GDT837_SOURCE_TRUTH_V1','unit_type':'source_sentence','paragraphs':units},'Independent original source and annotation reconstruction')
    meta={'schema':'GDT837_SOURCE_UNIT_METADATA_V1','unit_type':'source_sentence','plaintext_included':False,
          'units':[{**{k:p[k] for k in ('paragraph_id','source_reference','source_reference_number','source_file','source_sentence_id','book','split')},'word_count':len(p['words'])} for p in units]}
    check(meta==obj(data/'prepared/UNITS.json.gz'),'Independent public source metadata')
    active=set(support['discovery'])|set(support['held']);rules={}
    for role,nominal in CAPACITIES.items():
        aa={a for a in active if a[0]==role}; hh={a for a in support['held'] if a[0]==role}
        rules[role]={'nominal':nominal,'active':len(aa),'inactive':nominal-len(aa),
            'minimum_D_active_occurrences':min((support['discovery'][a] for a in aa),default=0),
            'minimum_D_held_active_occurrences':min((support['discovery'][a] for a in hh),default=0),
            'held_only_rules':sum(support['discovery'][a]==0 for a in hh),'active_rules_below_8_D':sum(support['discovery'][a]<8 for a in aa)}
    reference=[json.loads(line) for line in (data/'prepared/reference.jsonl').read_text().splitlines()]
    width=spec['deduplication_audit_words']
    grams={tuple(p['words'][i:i+width]) for p in units for i in range(len(p['words'])-width+1)}
    overlap=sum(any(tuple(sentence[i:i+width]) in grams for i in range(len(sentence)-width+1)) for sentence in reference)
    missing=set(spec['wholeword_values'])-set(obj(data/'prepared/candidates.json')['wholeword_pool'])
    gates={'D_units':partitions['discovery']['source_sentence_units']>=spec['minimum_discovery_paragraphs'],
        'H_units':partitions['held']['source_sentence_units']>=spec['minimum_held_paragraphs'],
        'active_S_8D':rules['S']['minimum_D_active_occurrences']>=spec['minimum_discovery_occurrences_active_suffix_or_wholeword'],
        'active_W_8D':rules['W']['minimum_D_active_occurrences']>=spec['minimum_discovery_occurrences_active_suffix_or_wholeword'],
        'held_active_L_1D':rules['L']['minimum_D_held_active_occurrences']>=spec['minimum_discovery_occurrences_held_active_literal'],
        'H_new_composed_forms_100':partitions['held']['novel_composed_forms']>=spec['minimum_held_novel_composed_form_occurrences'],
        'H_new_unambiguous_composed_lemmas_30':partitions['held']['unambiguous_novel_composed_lemmas']>=spec['minimum_held_unambiguous_novel_composed_lemma_occurrences'],
        'all_true_W_in_frozen_candidates':not missing,'reference_exact20_overlap_zero':overlap==0}
    initial={'status':'SOURCE_CAPACITY_PASS' if all(gates.values()) else 'SOURCE_CAPACITY_STOP','gates':gates,
        'failed_gates':[k for k,v in gates.items() if not v],
        'split':'SCG I-II s1-9859 discovery / III-IV s9860-23687 held; source-sentence units',
        'partitions':partitions,'rules':rules,'reference_exact20_overlap_sentences':overlap,
        'excluded_unrepresentable_units':excluded,'excluded_forma_concordance_units_by_metadata':excluded_forma,
        'canonical_source_ids_before_exclusion':len(identities),'missing_W_candidate_count':len(missing),'keys_generated':False}
    check((json.dumps(initial,indent=2,sort_keys=True)+'\n').encode()==(data/'prepared/INITIAL_CAPACITY.json').read_bytes(),'Independent byte-exact initial capacity reconstruction')
    compare(initial,cap,'Fixed source gates and counts')
    return {'source_capacity_status':initial['status'],'source_units_reconstructed':len(units),
            'source_words_reconstructed':sum(len(p['words']) for p in units),
            'canonical_source_ids_verified':len(identities),'excluded_forma_units':excluded_forma,
            'initial_capacity_byte_exact':True,'source_capacity_sha256':sha(data/'prepared/CAPACITY.json')}


def scientific_decision(rows,spec):
    limits=spec['overall_recovery']; outcomes={arm:[] for arm in ARMS}
    lookup={(row['world_id'],row['arm']):row for row in rows}
    check(len(rows)==len(lookup)==2*len(spec['world_ids']) and set(lookup)=={(w,a) for w in spec['world_ids'] for a in ARMS},'Complete unique evaluation panel')
    for row in rows:
        for subset,metric,field in [('all','word_accuracy','minimum_word_accuracy_each_key'),('all','character_accuracy','minimum_character_accuracy_each_key'),('novel_forms','word_accuracy','minimum_novel_form_accuracy_each_key'),('novel_lemmas','word_accuracy','minimum_novel_lemma_accuracy_each_key')]:
            value=row['recovery'][subset][metric]
            outcomes[row['arm']].append(value is not None and value>=limits[field])
        outcomes[row['arm']].append(row['all_identifiable_role_outputs_correct'])
    relaxed=all(outcomes['RELAXED']); strict=all(outcomes['STRICT'])
    strict=strict and all(lookup[w,'STRICT']['priority'][split]['passes_W_precedence'] for w in spec['world_ids'] for split in ('discovery','held'))
    gains=[lookup[w,'STRICT']['recovery']['all']['word_accuracy']-lookup[w,'RELAXED']['recovery']['all']['word_accuracy'] for w in spec['world_ids']]
    mean=sum(gains)/len(gains)
    gain=strict and mean>=spec['constraint_gain']['minimum_mean_held_word_gain']-1e-12 and all(g>=spec['constraint_gain']['minimum_each_key_held_word_gain']-1e-12 for g in gains)
    status='STRICT_RECOVERY_FAIL' if not strict else 'FRESH_RECOVERY_PASS_WITH_CONSTRAINT_GAIN' if gain else 'FRESH_RECOVERY_PASS_NO_DEMONSTRATED_CONSTRAINT_GAIN'
    return {'status':status,'strict_recovery_pass':bool(strict),'relaxed_recovery_pass':relaxed,
            'constraint_gain_demonstrated':bool(gain),'held_word_gain_per_world':gains,'mean_held_word_gain':mean,
            'three_keys_share_one_source_split':True,'source_units_are_supplied_sentences':True,
            'gold_spelling_normalized_for_uv':False,'voynich_data_accessed':False}



def held_metrics(fit,key,discovery,held,source,candidates,model):
    d=[p for p in source['paragraphs'] if p['split']=='discovery']
    h=[p for p in source['paragraphs'] if p['split']=='held']
    compare([p['paragraph_id'] for p in h],[p['paragraph_id'] for p in held['paragraphs']],'Held source-sentence identity and ordering')
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
    return {'world_id':fit['world_id'],'arm':fit['arm'],'selected_start':fit['start'],'selected_search_seed':fit['search_seed'],
            'selected_initialization_seed':fit['initialization_seed'],'selected_initialization_attempts':fit['initialization_attempts'],
            'priority':{s:mandatory_priority(c,fit['key']) for s,c in [('discovery',discovery),('held',held)]},
            'proposals':fit['proposals'],'priority_rejections':fit['priority_rejections'],
            'recovery':{name:metrics(rows) for name,rows in pairs.items()},
            'held_source_sentences':len(h),'exact_held_source_sentences':whole_paragraphs,
            'active_key_accuracy':active,'role_confusion':[{'true_role':a,'predicted_role':b,'codes':n} for (a,b),n in sorted(confusion.items())],
            'same_emission_role_equivalence':eq,'identifiable_active_rules':n,
            'exact_identifiable_role_outputs':correct_ids,'identifiable_role_output_accuracy':correct_ids/n if n else None,
            'all_identifiable_role_outputs_correct':n>0 and correct_ids==n,
            'oracle_true_nats':oracle,'selected_objective_nats':fitted,'selected_minus_oracle':fitted-oracle}


def key_check(key,cipher,candidates):
    check(set(key)=={f'X{i:02d}' for i in range(38)},'Full opaque key inventory')
    limits={'L':set('abcdefghijklmnopqrstuvwxyz'),'S':set(candidates['suffix_pool']),'W':set(candidates['wholeword_pool'])}
    check(Counter(entry['role'] for entry in key.values())==Counter(CAPACITIES),'Nominal role cardinality')
    domains=positional_domains(cipher,key)
    for role in CAPACITIES:
        outputs=[v['output'] for v in key.values() if v['role']==role]
        check(len(outputs)==len(set(outputs)) and set(outputs)<=limits[role],'Candidate membership and per-role injectivity')
    check(all(v['role'] in domains[c] for c,v in key.items()),'Cipher-position role feasibility')


def mandatory_priority(cipher,key):
    owners={}
    for code,value in key.items():
        if value['role']=='W':
            check(value['output'] not in owners,'No duplicate wholeword owner')
            owners[value['output']]=code
    counts=Counter(tuple(w) for p in cipher['paragraphs'] for w in p['words'])
    check(counts and () not in counts,'Nonempty ciphertext unit words')
    incompatible=set()
    for word in counts:
        emission=''.join(key[c]['output'] for c in word)
        if emission in owners and (len(word)!=1 or word[0]!=owners[emission]):
            incompatible.add(word)
    return {'words':sum(counts.values()),'word_types':len(counts),'violating_words':sum(counts[w] for w in incompatible),
            'violating_types':len(incompatible),'passes_W_precedence':not incompatible}


def frozen_fits(data,spec):
    """Independent exact freeze gate; contains no held or world-truth access."""
    reg=obj(data/'src/PREREG_LOCK.json')
    for field,parent in [('sha256',data),('upstream_sha256',ROOT)]:
        check(bool(reg[field]),'Nonempty source registration')
        for name,digest in reg[field].items():
            path=(parent/name).resolve()
            check(path.is_relative_to(parent.resolve()),'Registered path containment')
            if field=='sha256':
                check('confirmation' not in Path(name).parts and not name.endswith('_held.json.gz'),'Discovery-only prereg input list')
            check(sha(path)==digest,'Registered code and discovery bytes')
    check(obj(data/'prepared/CAPACITY.json')['status']=='SOURCE_CAPACITY_PASS','Fixed source passed')
    check(not (data/'artifacts/RUN_STOP.json').exists(),'No initialization-stop override')
    restart_paths=sorted(f'artifacts/fits/world_{w}_{a}_start{s}.json' for w in spec['world_ids'] for a in ARMS for s in spec['starts'])
    selected_paths=sorted(f'artifacts/fits/world_{w}_{a}_selected.json' for w in spec['world_ids'] for a in ARMS)
    lock=obj(data/'artifacts/FIT_LOCK.json')
    check(lock['schema']=='GDT837_FIT_LOCK_V1' and lock['restarts']==restart_paths and lock['selected']==selected_paths,'Exact fixed path lists')
    check(set(lock['sha256'])==set(restart_paths+selected_paths),'Exact 54-file hash coverage')
    check(lock['spec_sha256']==sha(data/'src/SPEC.json') and lock['paired_initializations_identical'] is True,'Lock policy and paired declaration')
    for name,digest in lock['sha256'].items():
        check(sha(data/name)==digest,'Every fit and selection immutable')
    candidates=obj(data/'prepared/candidates.json')
    discovery={w:obj(data/f'prepared/world_{w}_discovery.json.gz') for w in spec['world_ids']}
    fits=[obj(data/name) for name in restart_paths]
    by_id={}
    for name,fit in zip(restart_paths,fits):
        w,a,s=fit['world_id'],fit['arm'],fit['start']
        check(name==f'artifacts/fits/world_{w}_{a}_start{s}.json','Fit identity matches frozen filename')
        check((w,a,s) not in by_id,'Unique restart identity'); by_id[w,a,s]=fit
        check(fit['status']=='FIT_COMPLETE' and fit['schema']=='GDT837_FIT_V1','Successful complete search outcomes')
        check(fit['search_seed']==837000000+100*w+s and fit['initialization_seed']==837500000+100*w+s,'Registered separate RNG seeds')
        check(type(fit['initialization_attempts']) is int and 0<fit['initialization_attempts']<=spec['optimizer']['initialization_cap'],'Fixed initialization cap')
        score=fit['discovery_objective']
        check(all(type(score[k]) in (int,float) and math.isfinite(score[k]) for k in ('total_nats','language_nats','family_nats')),'Finite scores before ranking')
        check(score['family_nats']==0 and abs(score['total_nats']-score['language_nats'])<1e-8,'OFF score arithmetic')
        check(all(type(fit[k]) is int and fit[k]>=0 for k in ('proposals','priority_rejections')) and fit['priority_rejections']<=fit['proposals'],'Proposal accounting')
        cipher=discovery[w]
        check(cipher['world_id']==w and cipher['split']=='discovery' and cipher['unit_type']=='source_sentence','Discovery packet identity')
        key_check(fit['initial_key'],cipher,candidates); key_check(fit['key'],cipher,candidates)
        check(mandatory_priority(cipher,fit['initial_key'])['passes_W_precedence'],'All 48 saved initializations satisfy W priority')
        if a=='STRICT':
            check(mandatory_priority(cipher,fit['key'])['passes_W_precedence'],'STRICT discovery feasibility invariant')
        compare({'cipher_sha256':sha(data/f'prepared/world_{w}_discovery.json.gz'),'spec_sha256':sha(data/'src/SPEC.json')},fit['input_hashes'],'Discovery-only fit binding')
    check(set(by_id)=={(w,a,s) for w in spec['world_ids'] for a in ARMS for s in spec['starts']},'Every scheduled identity exactly once')
    for w in spec['world_ids']:
        for s in spec['starts']:
            left,right=by_id[w,'RELAXED',s],by_id[w,'STRICT',s]
            for field in ('initial_key','initialization_attempts','initialization_seed','search_seed'):
                check(left[field]==right[field],'Independent paired initial state comparison')
    selected=[]
    for w in spec['world_ids']:
        for a in sorted(ARMS):
            ordered=sorted((by_id[w,a,s] for s in spec['starts']),key=lambda f:(-f['discovery_objective']['total_nats'],f['start']))
            saved=obj(data/f'artifacts/fits/world_{w}_{a}_selected.json')
            check(saved==ordered[0],'Independent discovery winner selection including ties')
            selected.append(saved)
    return fits,selected,discovery,reg


def confirmation_bindings(data,spec,reg):
    expected={'held_commitments':{f'prepared/world_{w}_held.json.gz' for w in spec['world_ids']},
              'confirmation_commitments':{'confirmation/source_truth.json.gz'}|{f'confirmation/world_{w}_truth.json.gz' for w in spec['world_ids']}}
    for field,names in expected.items():
        check(set(reg[field])==names,'Exact post-lock payload commitment set')
        for name in names:
            check(sha(data/name)==reg[field][name],'Previously committed confirmation hash')
    generation=obj(data/'prepared/GENERATION.json')
    names=set.union(*expected.values())|{f'prepared/world_{w}_discovery.json.gz' for w in spec['world_ids']}|{'prepared/UNITS.json.gz'}
    check(set(generation['gzip_files'])==names,'Exact gzip packet inventory')
    for name in sorted(names):
        compare(gzip_info(data/name),generation['gzip_files'][name],'Compressed and decompressed byte commitments')
    compare({'capacity_sha256':sha(data/'prepared/CAPACITY.json'),'encoder_spec_sha256':sha(data/'src/ENCODER_SPEC.json'),
             'shared_source_gold_copies':1,'world_truth_contains_source_words':False,'same_opaque_packet_for_all_fit_conditions':True,
             'condition_or_score_information_in_encoder':False},generation,'Generator source and pairing declarations')
    return generation


def world_replay(data,world,source,encoder,candidates,generation,discovery):
    truth=obj(data/f'confirmation/world_{world}_truth.json.gz')
    check(truth['schema']=='GDT837_WORLD_TRUTH_V1' and truth['world_id']==world and truth['unit_type']=='source_sentence' and 'paragraphs' not in truth,'Map-only world schema')
    check(truth['source_truth_sha256']==sha(data/'confirmation/source_truth.json.gz') and truth['encoder_spec_sha256']==sha(data/'src/ENCODER_SPEC.json'),'Map-to-source commitments')
    rng=random.Random(world); seeded={}
    for role,values in [('L',list(encoder['letter_alphabet'])),('S',encoder['suffix_values']),('W',encoder['wholeword_values'])]:
        ids=[f'{role}{i:02d}' for i in range(len(values))]; rng.shuffle(ids); seeded.update(zip(ids,values))
    check(seeded==truth['typed_decode_map'],'Independent seeded planted values')
    opaque_ids=[f'X{i:02d}' for i in range(38)]; random.Random(world+encoder['opaque_shuffle_seed_offset']).shuffle(opaque_ids)
    aliases=dict(zip(opaque_ids,sorted(seeded)))
    check(aliases==truth['opaque_to_typed'],'Independent full opaque alias permutation')
    key={c:{'role':t[0],'output':seeded[t]} for c,t in aliases.items()}
    check(key==truth['decode_map'],'Role/output map exact reconstruction')
    inverse={(v['role'],v['output']):c for c,v in key.items()}
    payloads={'discovery':discovery,'held':obj(data/f'prepared/world_{world}_held.json.gz')}
    for split,cipher in payloads.items():
        check(cipher['schema']=='GDT837_OPAQUE_CIPHERTEXT_V1' and cipher['world_id']==world and cipher['split']==split and cipher['unit_type']=='source_sentence','Exact cipher identity')
        selected=[p for p in source['paragraphs'] if p['split']==split]
        check(len(selected)==len(cipher['paragraphs']),'Complete source unit count')
        for raw,encoded in zip(selected,cipher['paragraphs']):
            expected={'paragraph_id':raw['paragraph_id'],'words':[[inverse[rule] for rule in logical_word(word,encoder)] for word in raw['words']]}
            check(encoded==expected,'Every original word independently reencoded under fixed W/S/L precedence')
        key_check(key,cipher,candidates)
        check(mandatory_priority(cipher,key)['passes_W_precedence'],'True encoder satisfies necessary priority')
    hashes={s:sha(data/f'prepared/world_{world}_{s}.json.gz') for s in payloads}
    check(truth['ciphertext_sha256']==hashes,'Truth-cipher packet binding')
    entries=[x for x in generation['worlds'] if x['world_id']==world]
    check(len(entries)==1,'One generation entry per world')
    compare({'world_id':world,'ciphertext_sha256':hashes,'map_only_truth_sha256':sha(data/f'confirmation/world_{world}_truth.json.gz'),'original_spelling_roundtrip_pass':True},entries[0])
    return key,payloads


def projection_accounting(data,world,cipher,candidates,model_root):
    counts=Counter(tuple(int(c[1:]) for c in word) for p in cipher['paragraphs'] for word in p['words'])
    types=sorted(counts); type_index={w:i for i,w in enumerate(types)}
    links=Counter()
    for unit in cipher['paragraphs']:
        previous=None
        for word in unit['words']:
            current=type_index[tuple(int(c[1:]) for c in word)]
            if previous is not None:links[previous,current]+=1
            previous=current
    suffix,whole=candidates['suffix_pool'],candidates['wholeword_pool']
    lines=['SUFFIX '+str(len(suffix)),' '.join(suffix),'WHOLE '+str(len(whole)),' '.join(whole),'WORDS '+str(len(types))]
    for word in types:lines.append(' '.join(map(str,[counts[word],len(word),*word])))
    lines.append('TRANSITIONS '+str(len(links)))
    for (a,b),n in sorted(links.items()):lines.append(f'{a} {b} {n}')
    lines.append('FAMILIES 0')
    raw=('\n'.join(lines)+'\n').encode()
    path=model_root/f'world_{world}_discovery.txt'
    check(path.read_bytes()==raw,'Independent complete discovery projection bytes, including source-sentence resets')
    info=gzip_info(data/f'prepared/world_{world}_discovery.json.gz')
    return {'cipher_sha256':info['compressed_sha256'],'cipher_uncompressed_sha256':info['uncompressed_sha256'],
            'compressed_bytes':info['compressed_bytes'],'uncompressed_bytes':info['uncompressed_bytes'],
            'projection_sha256':hashlib.sha256(raw).hexdigest(),'word_types':len(types),'word_tokens':sum(counts.values()),
            'source_sentence_units':len(cipher['paragraphs']),'transition_types':len(links),'atom_incidence_entries':sum(len(set(w)) for w in types),
            'model_meta_sha256':sha(model_root/'reference/model_meta.json'),
            'decoder_source_sha256':sha(ROOT/'experiments/yolo/gdt836_integrated_wholeword_precedence/src/decoder.cpp'),
            'spec_sha256':sha(data/'src/SPEC.json')}


def full_replay(data,model_root,spec,fits,selected,discovery,generation):
    source=obj(data/'confirmation/source_truth.json.gz'); encoder=obj(data/'src/ENCODER_SPEC.json'); candidates=obj(data/'prepared/candidates.json')
    path=ROOT/'experiments/yolo/gdt832_joint_family_context_control/src/reference_model.py'
    module_spec=importlib.util.spec_from_file_location('gdt837_independent_frozen_reference',path)
    module=importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
    model=module.load_model(model_root/'reference')
    compare({'reference_jsonl_sha256':sha(data/'prepared/reference.jsonl'),'families_json_sha256':sha(data/'prepared/families.json')},model.metadata['input_hashes'],'Frozen shared model input')
    worlds={w:world_replay(data,w,source,encoder,candidates,generation,discovery[w]) for w in spec['world_ids']}
    accounting={w:projection_accounting(data,w,discovery[w],candidates,model_root) for w in spec['world_ids']}
    for fit in fits:
        compare(accounting[fit['world_id']],fit['input_hashes'],'Independent exact runtime input accounting')
        score=objective(discovery[fit['world_id']],fit['key'],model)
        compare({'total_nats':score,'language_nats':score,'family_nats':0},fit['discovery_objective'],'Independent restart objective',1e-4)
    rows=[]
    for fit in selected:
        key,packets=worlds[fit['world_id']]
        rows.append(held_metrics(fit,key,packets['discovery'],packets['held'],source,candidates,model))
    result=obj(data/'artifacts/RESULT.json')
    check(len(rows)==len(result['condition_results']),'Complete evaluated row count')
    objective_fields={'oracle_true_nats','selected_objective_nats','selected_minus_oracle'}
    for expected,actual in zip(rows,result['condition_results']):
        compare({k:v for k,v in expected.items() if k not in objective_fields},actual,'Independent held metrics, priority and max-flow identifiability',1e-10)
        compare({k:expected[k] for k in objective_fields},actual,'Independent selected/oracle summation',1e-4)
    compare(scientific_decision(rows,spec),result,'Independent separate recovery and benefit decisions')
    compare({'schema':'GDT837_RESULT_V1','fit_lock_sha256':sha(data/'artifacts/FIT_LOCK.json'),'prereg_lock_sha256':sha(data/'src/PREREG_LOCK.json'),
             'paired_initializations_verified':len(spec['world_ids'])*len(spec['starts']),
             'restart_initial_W_compatibility_verified':len(fits)},result,'Result freeze and pairing bindings')
    return {'restart_objectives_replayed':len(fits),'selected_fits_replayed':len(selected),
            'held_word_predictions_replayed':sum(r['recovery']['all']['words'] for r in rows),
            'true_key_oracle_scores_replayed':len(rows),'paired_initializations_verified':len(spec['world_ids'])*len(spec['starts']),
            'restart_initial_W_compatibility_verified':len(fits),'independent_gzip_bindings_verified':len(generation['gzip_files']),
            'source_words_independently_reencoded':len(spec['world_ids'])*sum(len(p['words']) for p in source['paragraphs']),
            'identifiable_role_domains_checked_by_independent_max_flow':sum(len(r['same_emission_role_equivalence']['role_options']) for r in rows),
            'scientific_status':result['status'],'strict_recovery_pass':result['strict_recovery_pass'],
            'relaxed_recovery_pass':result['relaxed_recovery_pass'],'constraint_gain_demonstrated':result['constraint_gain_demonstrated'],
            'fit_lock_sha256':sha(data/'artifacts/FIT_LOCK.json'),'result_sha256':sha(data/'artifacts/RESULT.json')}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=BASE)
    parser.add_argument('--source-dir',type=Path,default=BASE/'runtime/ittb_source')
    parser.add_argument('--model-root',type=Path,default=BASE/'runtime')
    parser.add_argument('--source-only',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args(); data=args.data_dir; spec=obj(data/'src/SPEC.json')
    if not args.source_only:
        fits,selected,discovery,reg=frozen_fits(data,spec)
        generation=confirmation_bindings(data,spec,reg)
    result={'schema':'GDT837_VALIDATION_V1','status':'VALIDATION_PASS','mode':'SOURCE_CAPACITY_ONLY' if args.source_only else 'SOURCE_AND_LOCKED_FIT_REPLAY',
            **source_audit(data,args.source_dir),'world_key_truth_opened':not args.source_only,'voynich_data_accessed':False}
    if not args.source_only:
        result.update(full_replay(data,args.model_root,spec,fits,selected,discovery,generation))
    target=data/'artifacts'/('SOURCE_VALIDATION.json' if args.source_only else 'VALIDATION.json')
    raw=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    if args.check:
        check(target.read_bytes()==raw,'Independent validation artifact replay')
    else:
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(raw)
    print(json.dumps(result,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
