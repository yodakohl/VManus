#!/usr/bin/env python3
"""Evaluate frozen opaque-role mixed controls against original held spelling."""
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
ARMS = ('BLIND', 'TYPED')
CAPACITIES = {'L':26, 'S':4, 'W':8}


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
    expected = {f'X{i:02d}' for i in range(38)} if arm=='BLIND' else {f'{role}{i:02d}' for role,n in CAPACITIES.items() for i in range(n)}
    check(set(key)==expected, 'Complete registered key identifier inventory')
    pools = {'L':set('abcdefghijklmnopqrstuvwxyz'),'S':set(candidates['suffix_pool']),'W':set(candidates['wholeword_pool'])}
    check(Counter(row['role'] for row in key.values())==Counter(CAPACITIES), 'Exact nominal role capacities')
    domains = role_domains(cipher,key)
    for role in CAPACITIES:
        values = [row['output'] for row in key.values() if row['role']==role]
        check(len(values)==len(set(values)) and set(values)<=pools[role], 'Per-role injective candidate assignment')
    for code,row in key.items():
        check(row['role'] in domains[code], 'Public discovery positional grammar')
        if arm=='TYPED':
            check(row['role']==code[0], 'Typed baseline receives fixed supplied roles')


def discovery_score(cipher, key, model):
    return sum(model.paragraph_score([''.join(key[c]['output'] for c in word) for word in p['words']]) for p in cipher['paragraphs'])


def ciphertext_path(data, world, arm, split):
    return data/f'prepared/world_{world}_{"typed_" if arm=="TYPED" else ""}{split}.json'


def lock_audit(data, spec):
    registration, lock = read_json(SRC/'PREREG_LOCK.json'),read_json(data/'artifacts/FIT_LOCK.json')
    for section,folder in [('sha256',BASE),('upstream_sha256',ROOT)]:
        for name,digest in registration[section].items():
            path=(folder/name).resolve()
            check(path.is_relative_to(folder) and sha(path)==digest,'Registered implementation/input hash')
    expected_restarts={f'artifacts/fits/world_{w}_{a}_start{s}.json' for w in spec['world_ids'] for a in ARMS for s in spec['starts']}
    expected_selected={f'artifacts/fits/world_{w}_{a}_selected.json' for w in spec['world_ids'] for a in ARMS}
    check(set(lock['restarts'])==expected_restarts and len(lock['restarts'])==48,'Complete restart freeze')
    check(set(lock['selected'])==expected_selected and len(lock['selected'])==6,'Complete selection freeze')
    check(set(lock['sha256'])==expected_restarts|expected_selected,'Exact fit commitment inventory')
    check(lock['spec_sha256']==sha(SRC/'SPEC.json'),'Frozen protocol')
    for name,digest in lock['sha256'].items():
        check(sha(data/name)==digest,'Frozen fit bytes')
    restarts=[read_json(data/p) for p in sorted(expected_restarts)]
    selected=[read_json(data/p) for p in sorted(expected_selected)]
    candidates=read_json(data/'prepared/candidates.json')
    for fit in restarts:
        check(fit['schema']=='GDT834_FIT_V1' and fit['world_id'] in spec['world_ids'] and fit['arm'] in ARMS,'Fixed fit identity')
        check(fit['seed']==83400000+100*fit['world_id']+fit['start'],'Fixed paired seed')
        discovery=read_json(ciphertext_path(data,fit['world_id'],fit['arm'],'discovery'))
        legal_key(fit['key'],candidates,discovery,fit['arm'])
    for fit in selected:
        group=[r for r in restarts if (r['world_id'],r['arm'])==(fit['world_id'],fit['arm'])]
        check(len(group)==8 and {r['start'] for r in group}==set(spec['starts']),'Eight starts per arm/world')
        check(fit==min(group,key=lambda r:(-r['discovery_objective']['total_nats'],r['start'])),'Discovery selection with fixed tie break')
    # Validate all held/key commitments only after the complete fit freeze.
    held={ciphertext_path(data,w,a,'held').relative_to(data).as_posix() for w in spec['world_ids'] for a in ARMS}
    sealed={'sealed/source_truth.json'}|{f'sealed/world_{w}_truth.json' for w in spec['world_ids']}
    check(held<=set(registration['held_commitments']) and sealed<=set(registration['sealed_commitments']),'Complete held and source/key commitments')
    for section in ('held_commitments','sealed_commitments'):
        for name,digest in registration[section].items():
            path=(data/name).resolve()
            check(path.is_relative_to(data.resolve()) and sha(path)==digest,'Post-freeze held/key commitment')
    return selected


def true_key_for_arm(truth, arm):
    if arm=='BLIND':
        return truth['decode_map']
    return {code:{'role':code[0],'output':value} for code,value in truth['typed_decode_map'].items()}


def evaluate_condition(fit, truth, source, discovery, held, candidates, model):
    check(truth['paragraphs']==source['paragraphs'],'World and source gold coincide')
    true_key=true_key_for_arm(truth,fit['arm'])
    legal_key(true_key,candidates,discovery,fit['arm'])
    support=Counter(c for p in discovery['paragraphs'] for word in p['words'] for c in word)
    held_ids={c for p in held['paragraphs'] for word in p['words'] for c in word}
    check(held_ids<=set(support),'Every held-active rule has discovery support')
    prior=[p for p in source['paragraphs'] if p['split']=='discovery']
    forms={w for p in prior for w in p['words']}
    lemmas={a for p in prior for aa in p['lemma_sets'] if aa for a in aa}
    expected=[p for p in source['paragraphs'] if p['split']=='held']
    check([p['paragraph_id'] for p in held['paragraphs']]==[p['paragraph_id'] for p in expected],'Exact held paragraph order and inventory')
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
    return {'world_id':fit['world_id'],'arm':fit['arm'],'selected_start':fit['start'],'selected_seed':fit['seed'],
            'recovery':{name:word_metrics(pairs) for name,pairs in buckets.items()},
            'held_paragraphs':len(expected),'exact_held_paragraphs':correct_paragraphs,
            'active_key_accuracy':active,'role_confusion':[{'true_role':a,'predicted_role':b,'codes':n} for (a,b),n in sorted(confusion.items())],
            'same_emission_role_equivalence':equivalence,'identifiable_active_rules':len(identifiable),
            'exact_identifiable_role_outputs':correct_identifiable,
            'identifiable_role_output_accuracy':correct_identifiable/len(identifiable) if identifiable else None,
            'all_identifiable_role_outputs_correct':bool(identifiable) and correct_identifiable==len(identifiable),
            'oracle_true_nats':oracle,'selected_objective_nats':fitted,'selected_minus_oracle':fitted-oracle}


def decide(rows, spec):
    limits=spec['overall_recovery']
    passed={arm:True for arm in ARMS}
    role=True
    for row in rows:
        for subset,metric,limit in [('all','word_accuracy','minimum_word_accuracy_each_key'),('all','character_accuracy','minimum_character_accuracy_each_key'),('novel_forms','word_accuracy','minimum_novel_form_accuracy_each_key'),('novel_lemmas','word_accuracy','minimum_novel_lemma_accuracy_each_key')]:
            value=row['recovery'][subset][metric]
            passed[row['arm']] &= value is not None and value>=limits[limit]
        if row['arm']=='BLIND':
            role &= row['all_identifiable_role_outputs_correct']
    status='BASELINE_RECOVERY_FAIL' if not passed['TYPED'] else 'ROLE_BLIND_RECOVERY_FAIL' if not(passed['BLIND'] and role) else 'ROLE_BLIND_RECOVERY_PASS'
    return {'status':status,'typed_recovery_pass':bool(passed['TYPED']),
            'blind_recovery_pass':bool(passed['BLIND']),'blind_identifiable_role_output_pass':bool(role),
            'known_boundaries_and_nominal_role_counts_supplied':True,'three_keys_share_one_source_split':True,
            'gold_spelling_normalized_for_uv':False,'voynich_data_accessed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=BASE)
    parser.add_argument('--model-root',type=Path,default=BASE/'runtime')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args(); spec=read_json(SRC/'SPEC.json')
    fits=lock_audit(args.data_dir,spec)
    source=read_json(args.data_dir/'sealed/source_truth.json')
    candidates=read_json(args.data_dir/'prepared/candidates.json')
    model=reference_module().load_model(args.model_root/'reference')
    check(model.metadata['input_hashes']['reference_jsonl_sha256']==sha(args.data_dir/'prepared/reference.jsonl') and model.metadata['input_hashes']['families_json_sha256']==sha(args.data_dir/'prepared/families.json'),'Frozen reference model source')
    rows=[]
    for fit in fits:
        world,arm=fit['world_id'],fit['arm']
        rows.append(evaluate_condition(fit,read_json(args.data_dir/f'sealed/world_{world}_truth.json'),source,
                    read_json(ciphertext_path(args.data_dir,world,arm,'discovery')),
                    read_json(ciphertext_path(args.data_dir,world,arm,'held')),candidates,model))
    result={'schema':'GDT834_RESULT_V1',**decide(rows,spec),'condition_results':rows,
            'fit_lock_sha256':sha(args.data_dir/'artifacts/FIT_LOCK.json')}
    emit(args.data_dir/'artifacts/RESULT.json',result,args.check)
    print(json.dumps({k:v for k,v in result.items() if k!='condition_results'},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
