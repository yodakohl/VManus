#!/usr/bin/env python3
"""Independent full-pair spelling check on the fixed49 public packet cases.

Does not use the author's adaptive pair pruning for its decision. Only own
validation JSON is written. Algorithm fixtures are strings, not new corpus.
"""
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = 'GD_1140_TRANSFER_FEASIBILITY'
EXPECTED = {
 'target': ('experiments/yolo/gdt905_joint_cv_complete_passage_candidates/artifacts/TARGET.json','49fa70f331528ab13dddb7addb56e3bf58fc9afa686b6dea53a70c668ed8adda'),
 'scope': ('experiments/yolo/gdt905_joint_cv_complete_passage_candidates/artifacts/SCOPE.json','7c75205c087bf46bce9e424105fa7f836fb65a73dad6dfaefeccda2c601a4009'),
 'core': ('experiments/yolo/gdt1140_fortune_status_whole_reading/CORE.json','2b1efddd83da54d801c61e0249a373f392480f1f842edd7ce18ed46ca86a43f3'),
 'account': ('experiments/yolo/gdt1140_fortune_status_whole_reading/artifacts/AUTHOR_ACCOUNT.json','9ec0b0890d16eb2617a7657a53025cec0b8d4ad7c97ea87ae9ac90059acc9e3d'),
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def substrings(word):
    return {word[i:j] for i in range(len(word)) for j in range(i+1,len(word)+1)}

def incoming(word, tokens):
    # Bitmask of predecessor cut positions for each possible end position.
    return tuple(sum(1<<start for start in range(end) if word[start:end] in tokens)
                 for end in range(len(word)+1))

def accepts(edges, first=None, second=None):
    reachable = 1
    for end in range(1,len(edges)):
        predecessors = edges[end] | (first[end] if first else 0) | (second[end] if second else 0)
        if predecessors & reachable:
            reachable |= 1 << end
    return bool(reachable & (1 << (len(edges)-1)))

def exhaustive(words, old):
    assert all(words) and all(old), 'Nonempty words/primitives required'
    types = sorted(set(words))
    base = {w:incoming(w,old) for w in types}
    missing = [w for w in types if not accepts(base[w])]
    # Global candidate universe includes all words, including old-covered ones.
    candidates = sorted(set().union(*(substrings(w) for w in types))-old)
    if not missing:
        return {'feasible':True,'witness':[],'candidates':len(candidates),'singles':0,'pairs':0,'missing':[]}
    new_edges = {u:{w:incoming(w,{u}) for w in missing} for u in candidates}
    singles=pairs=0
    for u in candidates:
        singles+=1
        if all(accepts(base[w],new_edges[u][w]) for w in missing):
            return {'feasible':True,'witness':[u],'candidates':len(candidates),'singles':singles,'pairs':pairs,'missing':missing}
    for u,v in itertools.combinations(candidates,2):
        pairs+=1
        if all(accepts(base[w],new_edges[u][w],new_edges[v][w]) for w in missing):
            return {'feasible':True,'witness':[u,v],'candidates':len(candidates),'singles':singles,'pairs':pairs,'missing':missing}
    return {'feasible':False,'witness':None,'candidates':len(candidates),'singles':singles,'pairs':pairs,'missing':missing}

def main():
    checks=[]
    def check(name,value,evidence=None):
        checks.append({'name':name,'pass':bool(value),'evidence':evidence})
    code=HERE/(BASE+'.py'); result_path=HERE/(BASE+'.json')
    frozen=json.loads(result_path.read_text())
    docs={}
    before={str(p.relative_to(ROOT)):sha(p) for p in [code,result_path,*[ROOT/p for p,h in EXPECTED.values()]]}
    check('published_algorithm_hash',sha(code)==frozen['source_sha256'])
    pin_results={}
    for name,(relative,h) in EXPECTED.items():
        pin_results[name]=frozen['inputs'][name]=={'path':relative,'sha256':h} and sha(ROOT/relative)==h
        docs[name]=json.loads((ROOT/relative).read_text())
    check('four_exact_bound_input_pins',all(pin_results.values()),pin_results)
    old=set(docs['core']['lexicon'])|set(docs['account']['extensions']['primitive_entries'])
    check('32_frozen_nonempty_primitives',len(old)==32 and all(old) and sorted(old)==frozen['old_primitive_inventory'])
    packets=[]; scope_counts={}; exclusions=True
    for reader, panel in docs['target']['panels'].items():
        selected=[p for p in panel if 12<=len(p['words'])<=24]
        scope_counts[reader]=len(selected)
        scope=docs['scope'][reader]
        exclusions &= scope['total']==len(panel) and scope['selected']==len(selected) and scope['excluded']==[
            {'paragraph_id':p['paragraph_id'],'reason':'OUTSIDE_REGISTERED_12_24_GROUP_SCOPE','word_count':len(p['words'])}
            for p in panel if not 12<=len(p['words'])<=24]
        packets.extend((reader,p) for p in selected)
    check('all_and_only_original_length_scope_cases',exclusions and scope_counts=={'CONSENSUS':0,'IT2a':41,'RF1b':5,'ZL3b':3} and scope_counts==frozen['selected_by_reader'])
    check('49_cases_41_paragraphs_15_physical_leaves',len(packets)==49 and len({p['paragraph_id'] for r,p in packets})==41 and len({p['physical_folio'] for r,p in packets})==15)
    check('917_literal_groups_with_ids_and_loci',sum(len(p['words']) for r,p in packets)==917 and all(len(p['words'])==len(p['source_group_ids'])==len(p['loci']) for r,p in packets))
    check('unique_reader_cases_no_sealed_or_unadmitted_page',len({(r,p['paragraph_id']) for r,p in packets})==49 and all(not p['page'].startswith('f84') and p['page']!='f116v' for r,p in packets))
    spec=importlib.util.spec_from_file_location('frozen_transfer_algorithm',code)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    fixtures=[('old_only',['ab','abab'],{'a','b'},True),
       ('one_reused_new',['abc','abcabc'],{'a','ab'},True),
       ('two_substrings_cover_three_unknown_types',['axa','aya','axaya'],{'a'},True),
       ('second_token_absent_from_first_word',['xx','yy','xxyy'],set(),True),
       ('three_distinct_required_characters',['x','y','z'],set(),False),
       ('overlap_requires_non_greedy_cut',['abc','abca'],{'a','ab','bc'},True)]
    fixture_results=[]
    for name,words,lex,expected in fixtures:
        own=exhaustive(words,lex); original=module.check(words,frozenset(lex))
        fixture_results.append({'name':name,'expected':expected,'independent':own['feasible'],'published':original['at_most_two_new_substrings_spelling_feasible'],'independent_witness':own['witness']})
    check('six_adversarial_algorithm_fixtures',all(f['expected']==f['independent']==f['published'] for f in fixture_results),fixture_results)
    independent=[]; replay=[]; published_trials=published_distinct=published_repeats=published_self=0
    for reader,p in packets:
        own=exhaustive(p['words'],old)
        independent.append({'reader':reader,'paragraph_id':p['paragraph_id'],'page':p['page'],'word_count':len(p['words']),'type_count':len(set(p['words'])),**own})
        replay.append({'reader':reader,'page':p['page'],'paragraph_id':p['paragraph_id'],'loci':sorted(set(p['loci'])),**module.check(p['words'],frozenset(old))})
        missing=sorted(own['missing'],key=lambda w:(len(w),w)); trials=[]
        for u in module.substrings(missing[0],frozenset(old)):
            remaining=[w for w in missing if not module.reachable(w,frozenset(old)|{u})]
            for v in module.substrings(remaining[0],frozenset(old)): trials.append((u,v))
        distinct=len({tuple(sorted(pair)) for pair in trials})
        published_trials+=len(trials); published_distinct+=distinct
        published_repeats+=len(trials)-distinct; published_self+=sum(u==v for u,v in trials)
    check('49_independent_complete_global_pair_enumerations',len(independent)==49 and not any(r['feasible'] for r in independent),
          {'singles':sum(r['singles'] for r in independent),'unordered_global_pairs':sum(r['pairs'] for r in independent)})
    check('published_case_records_exact_replay',replay==frozen['cases'])
    check('independent_missing_sets_and_word_counts_match',all(sorted(o['missing'])==sorted(r['old_unreachable_types']) and o['word_count']==r['word_count'] and o['type_count']==r['type_count'] for o,r in zip(independent,frozen['cases'])))
    check('minimum6_and_published2738_pairs_and_zero_feasible',min(len(r['missing']) for r in independent)==frozen['min_old_unreachable_types']==6 and sum(r['second_primitive_pairs_tested'] for r in replay)==frozen['pairs_tested']==2738 and frozen['feasible_cases']==0)
    check('fixed_inputs_algorithm_result_unchanged',before=={s:sha(ROOT/s) for s in before})
    result={'status':'INDEPENDENT_BOUNDED_SPELLING_VALIDATION_NOT_MEANING','pass':all(c['pass'] for c in checks),
        'validator_sha256':sha(Path(__file__)),'reviewed_pins':before,'checks':checks,'independent_cases':independent,
        'scope':{'cases':len(packets),'distinct_paragraphs':len({p['paragraph_id'] for r,p in packets}),'physical_leaves':len({p['physical_folio'] for r,p in packets}),'literal_word_positions':sum(len(p['words']) for r,p in packets),'reader_cases':scope_counts,'primary_forms_all_readers':len({w for r,p in packets for w in p['words']}),'actual_group_range':[min(len(p['words']) for r,p in packets),max(len(p['words']) for r,p in packets)]},
        'published_pair_counter_interpretation':{'second_candidate_trials':published_trials,'distinct_unordered_pairs_summed_per_case':published_distinct,'repeated_unordered_trials':published_repeats,'same_token_trials':published_self,'note':'2738 is an execution counter, not a claim of2738 distinct unordered models. Duplicate/self-token trials do not invalidate completeness.'},
        'completeness_proof':'Any useful new token occurs as a nonempty substring of a selected word. The independent implementation tries every singleton and unordered pair from that global per-packet universe. In the published pruning, a successful pair must contribute u to the first old-unreachable word; after u, its second member must contribute v to the first remaining unreachable word. Thus adaptive selection omits no successful set. Removing old-covered words is safe by monotonicity; removing old tokens is redundant. Duplicate tokens add no capacity.',
        'decision':'No selected case is fully spelled by the fixed32 primitive strings plus at most two arbitrary new strings. This is a necessary lexical condition only, under exact concatenation and these inherited strings.',
        'limits':['Not semantic truth, morpheme identification, valid operator arguments, ordinary-language failure or global manuscript coverage.','Other dictionaries/budgets/passages, spelling transformations, richer grammar or nonconcatenative encipherment are not tested.','Missing-type count alone excludes two whole-word exceptions, not two reusable substring additions; exhaustive pair search establishes the stronger bound.','All old-primitive concatenations were admitted, relaxing the frozen finite licenses and ignoring typing; failure in this superset also excludes a stricter unchanged-license model.','Budget two is a root/advisor-proposed exploratory working assumption, not a user-imposed obligation, inferred manuscript law or proof that an eventual reading needs a specific number of meanings.','Alternative readers are one manuscript. This is exposed exploratory feasibility, not independent confirmation.'],
        'confirmed_new_word_meanings':0}
    destination=HERE/(BASE+'_VALIDATION.json');destination.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'pass':result['pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],
                      'cases':49,'feasible':sum(r['feasible'] for r in independent),'global_pairs':sum(r['pairs'] for r in independent)}))
    return 0 if result['pass'] else 1

if __name__=='__main__':
    raise SystemExit(main())
