#!/usr/bin/env python3
"""Evaluate the frozen paired SCG control without changing original spelling."""
from __future__ import annotations
import argparse
import hashlib
import gzip
import importlib.util
import json
import math
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

SRC = Path(__file__).resolve().parent
BASE = SRC.parent
ROOT = BASE.parents[2]
ARMS = ('RELAXED', 'STRICT')
CAPACITIES = {'L':26, 'S':4, 'W':8}


def check(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    path=Path(path)
    if path.suffix=='.gz':
        with gzip.open(path,'rt',encoding='utf-8') as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding='utf-8'))


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


def role_domains(cipher, identifiers):
    domains = {code:set(CAPACITIES) for code in identifiers}
    for p in cipher['paragraphs']:
        for word in p['words']:
            check(bool(word), 'Nonempty code word')
            for position,code in enumerate(word):
                check(code in domains, 'Code must belong to complete public inventory')
                if len(word) != 1:
                    domains[code].discard('W')
                if position != len(word)-1 or len(word)<4:
                    domains[code].discard('S')
    return domains


def identifiability(cipher, true_key, candidates):
    """Same-emission active-role equivalence; unused slot values are free.

    Only the emissions of observed codes enter the constraints. True role
    labels and the outputs of absent codes are deliberately not consulted.
    Counting quotients out every permutation restricted to unused slots.
    """
    pools = {'L':set('abcdefghijklmnopqrstuvwxyz'),'S':set(candidates['suffix_pool']),
             'W':set(candidates['wholeword_pool'])}
    active = {code for p in cipher['paragraphs'] for word in p['words'] for code in word}
    inactive = set(true_key)-active
    check(len(true_key)==sum(CAPACITIES.values()), 'Complete nominal inventory')
    domains = role_domains(cipher,true_key)
    permitted = {code:sorted(role for role in domains[code] if true_key[code]['output'] in pools[role]) for code in active}
    order = sorted(active,key=lambda code:(len(permitted[code]),code))
    possible, assignment, used = {code:set() for code in active},{},{role:set() for role in CAPACITIES}
    counts, solutions = dict.fromkeys(CAPACITIES,0),0
    def visit(index):
        nonlocal solutions
        if index==len(order):
            remaining = {role:CAPACITIES[role]-counts[role] for role in CAPACITIES}
            if sum(remaining.values()) != len(inactive):
                return
            if any(len(pools[role]-used[role])<remaining[role] for role in CAPACITIES):
                return
            solutions += 1
            for code,role in assignment.items():
                possible[code].add(role)
            return
        code = order[index]
        value = true_key[code]['output']
        for role in permitted[code]:
            if counts[role]>=CAPACITIES[role] or value in used[role]:
                continue
            counts[role]+=1; used[role].add(value); assignment[code]=role
            visit(index+1)
            counts[role]-=1; used[role].remove(value); del assignment[code]
    visit(0)
    check(solutions>0, 'Truth emissions have at least one legal role assignment')
    return {'role_options':{code:sorted(possible[code]) for code in sorted(active)},
            'identifiable_ids':sorted(code for code in active if len(possible[code])==1),
            'ambiguous_ids':sorted(code for code in active if len(possible[code])>1),
            'feasible_active_role_assignments':solutions,'inactive_ids':sorted(inactive)}


def legal_key(key, candidates, cipher, arm):
    expected = {f'X{i:02d}' for i in range(38)}
    check(set(key)==expected, 'Complete registered key identifier inventory')
    pools = {'L':set('abcdefghijklmnopqrstuvwxyz'),'S':set(candidates['suffix_pool']),'W':set(candidates['wholeword_pool'])}
    check(Counter(row['role'] for row in key.values())==Counter(CAPACITIES), 'Exact nominal role capacities')
    domains = role_domains(cipher,key)
    for role in CAPACITIES:
        values = [row['output'] for row in key.values() if row['role']==role]
        check(len(values)==len(set(values)) and set(values)<=pools[role], 'Per-role injective candidate assignment')
    for code,row in key.items():
        check(row['role'] in domains[code], 'Public discovery positional grammar')


def discovery_score(cipher, key, model):
    return sum(model.paragraph_score([''.join(key[c]['output'] for c in word) for word in p['words']]) for p in cipher['paragraphs'])


def priority_audit(cipher,key):
    whole={row['output']:code for code,row in key.items() if row['role']=='W'}
    check(len(whole)==sum(row['role']=='W' for row in key.values()),'Wholeword injection')
    words=Counter(tuple(word) for p in cipher['paragraphs'] for word in p['words'])
    check(bool(words),'Nonempty source required')
    violations=[]
    for codes,count in words.items():
        text=''.join(key[c]['output'] for c in codes)
        owner=whole.get(text)
        if owner is not None and codes!=(owner,):
            violations.append(count)
    return {'words':sum(words.values()),'word_types':len(words),
            'violating_words':sum(violations),'violating_types':len(violations),
            'passes_W_precedence':not violations}


def check_paired_initializations(fits,spec):
    groups=defaultdict(dict)
    for fit in fits:
        identity=(fit['world_id'],fit['start'])
        check(fit['arm'] in ARMS and fit['arm'] not in groups[identity],'One restart per paired arm')
        check(fit['search_seed']==837000000+100*fit['world_id']+fit['start'],'Fixed optimization seed')
        check(fit['initialization_seed']==837500000+100*fit['world_id']+fit['start'],'Fixed separate initialization seed')
        check(type(fit['initialization_attempts']) is int and 1<=fit['initialization_attempts']<=1000,'Fixed initialization cap')
        groups[identity][fit['arm']]=fit
    check(set(groups)=={(w,s) for w in spec['world_ids'] for s in spec['starts']},'Complete paired initialization panel')
    for pair in groups.values():
        check(set(pair)==set(ARMS),'Both arms present for every initialization')
        left,right=pair['RELAXED'],pair['STRICT']
        for field in ('initial_key','initialization_attempts','initialization_seed','search_seed'):
            check(left[field]==right[field],'Paired common initialization: '+field)
    return len(groups)


def decide(rows,spec):
    thresholds=spec['overall_recovery']; passed={a:True for a in ARMS}
    panel={(row['world_id'],row['arm']):row for row in rows}
    check(len(rows)==len(panel)==2*len(spec['world_ids']) and set(panel)=={(w,a) for w in spec['world_ids'] for a in ARMS},'Complete selected evaluation panel')
    for row in rows:
        for subset,metric,field in [('all','word_accuracy','minimum_word_accuracy_each_key'),('all','character_accuracy','minimum_character_accuracy_each_key'),('novel_forms','word_accuracy','minimum_novel_form_accuracy_each_key'),('novel_lemmas','word_accuracy','minimum_novel_lemma_accuracy_each_key')]:
            value=row['recovery'][subset][metric]
            passed[row['arm']] &= value is not None and value>=thresholds[field]
        passed[row['arm']] &= row['all_identifiable_role_outputs_correct']
    strict=passed['STRICT'] and all(panel[w,'STRICT']['priority'][s]['passes_W_precedence'] for w in spec['world_ids'] for s in ('discovery','held'))
    gains=[panel[w,'STRICT']['recovery']['all']['word_accuracy']-panel[w,'RELAXED']['recovery']['all']['word_accuracy'] for w in spec['world_ids']]
    mean=sum(gains)/len(gains); rule=spec['constraint_gain']
    gain=bool(strict and mean>=rule['minimum_mean_held_word_gain']-1e-12 and min(gains)>=rule['minimum_each_key_held_word_gain']-1e-12)
    status='STRICT_RECOVERY_FAIL' if not strict else 'FRESH_RECOVERY_PASS_WITH_CONSTRAINT_GAIN' if gain else 'FRESH_RECOVERY_PASS_NO_DEMONSTRATED_CONSTRAINT_GAIN'
    return {'status':status,'strict_recovery_pass':bool(strict),'relaxed_recovery_pass':bool(passed['RELAXED']),
            'constraint_gain_demonstrated':gain,'held_word_gain_per_world':gains,'mean_held_word_gain':mean,
            'three_keys_share_one_source_split':True,'source_units_are_supplied_sentences':True,
            'gold_spelling_normalized_for_uv':False,'voynich_data_accessed':False}


def registered_inputs(data):
    reg=read_json(data/'src/PREREG_LOCK.json')
    for section,base in [('sha256',data),('upstream_sha256',ROOT)]:
        check(bool(reg[section]),'Nonempty registered input inventory')
        for relative,digest in reg[section].items():
            path=(base/relative).resolve()
            check(path.is_relative_to(base.resolve()),'Registered path containment')
            if section=='sha256':
                check('confirmation' not in Path(relative).parts and not relative.endswith('_held.json.gz'),'Discovery registry excludes confirmation payloads')
            check(sha(path)==digest,'Registered immutable input: '+relative)
    return reg


def verify_fit_lock(data,spec):
    """No held/confirmation file is opened anywhere in this gate."""
    data=Path(data); reg=registered_inputs(data)
    check(read_json(data/'prepared/CAPACITY.json')['status']=='SOURCE_CAPACITY_PASS','Source capacity precedes recovery')
    check(not (data/'artifacts/RUN_STOP.json').exists(),'Initialization stop forbids confirmation')
    lock=read_json(data/'artifacts/FIT_LOCK.json')
    restart_names=sorted(f'artifacts/fits/world_{w}_{a}_start{s}.json' for w in spec['world_ids'] for a in ARMS for s in spec['starts'])
    selected_names=sorted(f'artifacts/fits/world_{w}_{a}_selected.json' for w in spec['world_ids'] for a in ARMS)
    check(lock['restarts']==restart_names and lock['selected']==selected_names,'Exact complete restart and selected path inventories')
    check(set(lock['sha256'])==set(restart_names+selected_names),'Exactly all fit hashes, without omissions or extras')
    check(lock['schema']=='GDT837_FIT_LOCK_V1' and lock['spec_sha256']==sha(data/'src/SPEC.json') and lock['paired_initializations_identical'] is True,'Fit lock policy binding')
    for relative,digest in lock['sha256'].items():
        check(sha(data/relative)==digest,'Frozen fit bytes: '+relative)
    fits=[read_json(data/name) for name in restart_names]
    candidates=read_json(data/'prepared/candidates.json')
    discovery={w:read_json(data/f'prepared/world_{w}_discovery.json.gz') for w in spec['world_ids']}
    for w,cipher in discovery.items():
        check(cipher['world_id']==w and cipher['split']=='discovery' and cipher['unit_type']=='source_sentence','Discovery-only packet identity')
    for relative,fit in zip(restart_names,fits):
        w,a,s=fit['world_id'],fit['arm'],fit['start']
        check(relative==f'artifacts/fits/world_{w}_{a}_start{s}.json','Filename and restart identity agree')
        check(fit['schema']=='GDT837_FIT_V1' and fit['status']=='FIT_COMPLETE','Every scheduled restart completed')
        values=fit['discovery_objective']
        check(all(type(values[k]) in (int,float) and math.isfinite(values[k]) for k in ('total_nats','language_nats','family_nats')),'Finite discovery objective before ranking')
        check(values['family_nats']==0 and abs(values['total_nats']-values['language_nats'])<1e-8,'OFF language-only objective')
        for field in ('proposals','priority_rejections'):
            check(type(fit[field]) is int and fit[field]>=0,'Nonnegative engine proposal accounting')
        check(fit['priority_rejections']<=fit['proposals'],'Rejected proposals bounded by proposals')
        legal_key(fit['initial_key'],candidates,discovery[w],a)
        legal_key(fit['key'],candidates,discovery[w],a)
        check(priority_audit(discovery[w],fit['initial_key'])['passes_W_precedence'],'Every saved common initialization satisfies mandatory W')
        if a=='STRICT':
            check(priority_audit(discovery[w],fit['key'])['passes_W_precedence'],'Every STRICT final key satisfies discovery W')
        check(fit['input_hashes']['cipher_sha256']==sha(data/f'prepared/world_{w}_discovery.json.gz') and fit['input_hashes']['spec_sha256']==sha(data/'src/SPEC.json'),'Fit discovery and policy binding')
    check_paired_initializations(fits,spec)
    selected=[]
    for name in selected_names:
        saved=read_json(data/name)
        w,a=saved['world_id'],saved['arm']
        check(name==f'artifacts/fits/world_{w}_{a}_selected.json','Selected filename identity')
        winner=min((f for f in fits if (f['world_id'],f['arm'])==(w,a)),key=lambda f:(-f['discovery_objective']['total_nats'],f['start']))
        check(saved==winner,'Discovery-only maximum, tie lowest restart, exact saved object')
        selected.append(saved)
    return {'lock':lock,'restarts':fits,'selected':selected,'discovery':discovery,'candidates':candidates,'prereg':reg}


def load_confirmation(data,spec,reg):
    """Called only after verify_fit_lock returns successfully."""
    expected_held={f'prepared/world_{w}_held.json.gz' for w in spec['world_ids']}
    expected_truth={'confirmation/source_truth.json.gz'}|{f'confirmation/world_{w}_truth.json.gz' for w in spec['world_ids']}
    for field,expected in [('held_commitments',expected_held),('confirmation_commitments',expected_truth)]:
        check(set(reg[field])==expected,'Exact post-lock commitment inventory')
        for relative,digest in reg[field].items():
            check(sha(data/relative)==digest,'Preregistered confirmation bytes')
    source=read_json(data/'confirmation/source_truth.json.gz')
    truth={w:read_json(data/f'confirmation/world_{w}_truth.json.gz') for w in spec['world_ids']}
    held={w:read_json(data/f'prepared/world_{w}_held.json.gz') for w in spec['world_ids']}
    for w in spec['world_ids']:
        check(truth[w]['world_id']==held[w]['world_id']==w and held[w]['split']=='held','Confirmation identity')
        check(truth[w]['source_truth_sha256']==sha(data/'confirmation/source_truth.json.gz') and truth[w]['encoder_spec_sha256']==sha(data/'src/ENCODER_SPEC.json'),'Map-to-source binding')
        check(truth[w]['ciphertext_sha256']=={s:sha(data/f'prepared/world_{w}_{s}.json.gz') for s in ('discovery','held')},'Map-to-cipher binding')
    return source,truth,held


def evaluate_condition(fit, truth, source, discovery, held, candidates, model):
    true_key=truth['decode_map']
    legal_key(true_key,candidates,discovery,fit['arm'])
    support=Counter(c for p in discovery['paragraphs'] for word in p['words'] for c in word)
    held_ids={c for p in held['paragraphs'] for word in p['words'] for c in word}
    check(held_ids<=set(support),'Every held-active rule has discovery support')
    prior=[p for p in source['paragraphs'] if p['split']=='discovery']
    forms={w for p in prior for w in p['words']}
    lemmas={a for p in prior for aa in p['lemma_sets'] if aa for a in aa}
    expected=[p for p in source['paragraphs'] if p['split']=='held']
    check([p['paragraph_id'] for p in held['paragraphs']]==[p['paragraph_id'] for p in expected],'Exact held source-sentence order and inventory')
    buckets={name:[] for name in ('all','novel_forms','novel_lemmas')}
    correct_paragraphs=0
    for cipher,p in zip(held['paragraphs'],expected):
        check(len(cipher['words'])==len(p['words'])==len(p['lemma_sets']),'Exact aligned held word count')
        local=[]
        for codes,word,analysis in zip(cipher['words'],p['words'],p['lemma_sets']):
            check(''.join(true_key[c]['output'] for c in codes)==word,'Unchanged original-spelling generator roundtrip')
            predicted=''.join(fit['key'][c]['output'] for c in codes)
            pair=(word,predicted); buckets['all'].append(pair); local.append(word==predicted)
            composed=all(true_key[c]['role']!='W' for c in codes)
            if composed and word not in forms:
                buckets['novel_forms'].append(pair)
            if composed and analysis is not None and len(analysis)==1 and analysis[0] not in lemmas:
                buckets['novel_lemmas'].append(pair)
        correct_paragraphs+=all(local)
    equivalence=identifiability(discovery,true_key,candidates)
    # Report marginal role identifiability, which the independent max-flow
    # validator checks exactly; the helper's enumeration count is not a gate.
    equivalence.pop('feasible_active_role_assignments')
    active=[]; confusion=Counter()
    for code in support:
        confusion[(true_key[code]['role'],fit['key'][code]['role'])]+=1
    for role in CAPACITIES:
        codes=[c for c in support if true_key[c]['role']==role]
        roles=sum(fit['key'][c]['role']==role for c in codes)
        outputs=sum(fit['key'][c]['output']==true_key[c]['output'] for c in codes)
        both=sum(fit['key'][c]==true_key[c] for c in codes)
        active.append({'role':role,'supported_rules':len(codes),'exact_roles':roles,'exact_outputs':outputs,
                       'exact_role_and_outputs':both,'role_accuracy':roles/len(codes) if codes else None,
                       'output_accuracy':outputs/len(codes) if codes else None,
                       'role_output_accuracy':both/len(codes) if codes else None,
                       'discovery_mass_role_output_accuracy':sum(support[c] for c in codes if fit['key'][c]==true_key[c])/sum(support[c] for c in codes) if codes else None})
    identifiable=equivalence['identifiable_ids']
    correct_identifiable=sum(fit['key'][c]==true_key[c] for c in identifiable)
    fitted=discovery_score(discovery,fit['key'],model)
    check(abs(fitted-fit['discovery_objective']['total_nats'])<1e-4 and
          abs(fitted-fit['discovery_objective']['language_nats'])<1e-4 and fit['discovery_objective']['family_nats']==0,'Independent language objective replay')
    oracle=discovery_score(discovery,true_key,model)
    return {'world_id':fit['world_id'],'arm':fit['arm'],'selected_start':fit['start'],'selected_search_seed':fit['search_seed'],
            'selected_initialization_seed':fit['initialization_seed'],'selected_initialization_attempts':fit['initialization_attempts'],
            'priority':{s:priority_audit(c,fit['key']) for s,c in [('discovery',discovery),('held',held)]},
            'proposals':fit['proposals'],'priority_rejections':fit['priority_rejections'],
            'recovery':{name:word_metrics(pairs) for name,pairs in buckets.items()},
            'held_source_sentences':len(expected),'exact_held_source_sentences':correct_paragraphs,
            'active_key_accuracy':active,'role_confusion':[{'true_role':a,'predicted_role':b,'codes':n} for (a,b),n in sorted(confusion.items())],
            'same_emission_role_equivalence':equivalence,'identifiable_active_rules':len(identifiable),
            'exact_identifiable_role_outputs':correct_identifiable,
            'identifiable_role_output_accuracy':correct_identifiable/len(identifiable) if identifiable else None,
            'all_identifiable_role_outputs_correct':bool(identifiable) and correct_identifiable==len(identifiable),
            'oracle_true_nats':oracle,'selected_objective_nats':fitted,'selected_minus_oracle':fitted-oracle}


def evaluate(data,model_root):
    data,model_root=Path(data),Path(model_root)
    spec=read_json(data/'src/SPEC.json')
    frozen=verify_fit_lock(data,spec)
    # This is deliberately the first confirmation access in evaluation.
    source,truth,held=load_confirmation(data,spec,frozen['prereg'])
    model=reference_module().load_model(model_root/'reference')
    check(model.metadata['input_hashes']['reference_jsonl_sha256']==sha(data/'prepared/reference.jsonl') and model.metadata['input_hashes']['families_json_sha256']==sha(data/'prepared/families.json'),'Shared frozen reference model')
    rows=[evaluate_condition(f,truth[f['world_id']],source,frozen['discovery'][f['world_id']],held[f['world_id']],frozen['candidates'],model) for f in frozen['selected']]
    return {'schema':'GDT837_RESULT_V1',**decide(rows,spec),'condition_results':rows,
            'fit_lock_sha256':sha(data/'artifacts/FIT_LOCK.json'),'prereg_lock_sha256':sha(data/'src/PREREG_LOCK.json'),
            'paired_initializations_verified':len(spec['world_ids'])*len(spec['starts']),
            'restart_initial_W_compatibility_verified':len(frozen['restarts'])}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=BASE)
    parser.add_argument('--model-root',type=Path,default=BASE/'runtime')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=evaluate(args.data_dir,args.model_root)
    emit(args.data_dir/'artifacts/RESULT.json',result,args.check)
    print(json.dumps({k:v for k,v in result.items() if k!='condition_results'},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
