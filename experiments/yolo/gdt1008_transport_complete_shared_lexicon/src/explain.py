"""Post-result short certificates; frozen six joint decisions are not changed."""
from common import *
import itertools
checklock();s,g=inputs();panel=read(A/'PANEL.json');validation=read(A/'VALIDATION.json');assert validation['unverified_negatives']==0
paths=dict(primary='experiments/yolo/gdt1006_transport_unfixed_original_lexicon/src/grammar.py',independent='experiments/yolo/gdt1006_transport_unfixed_original_lexicon/src/independent.py')
gp=load(paths['primary'],'grammar1006');gi=load(paths['independent'],'ind1006');checks=[]
for family in s['families']:
    for word,role in [('chedain','NEXT'),('lkedy','PAIRED_WITH')]:
        b=gp.build(panel[0]['words'],g,family,timeout=10000);b['solver'].add(b['xs'][word]!=b['num'][role]);primary=str(b['solver'].check())
        d=gi.build(panel[0]['words'],g,family,timeout=10000);d['solver'].add(d['xs'][word]!=d['num'][role]);other=str(d['solver'].check())
        assert not ({primary,other}=={'sat','unsat'})
        checks.append(dict(family=family,word=word,role=role,alternative_primary=primary,alternative_independent=other,witness=gp.extract(b) if primary=='sat' else None))
put('POST_RESULT_ROLE_CHECKS.json',dict(status='COMPLETE',checks=checks,source_files={p:sha(R/p) for p in paths.values()},scope='Four post-result conditional syntax-role necessity probes; no meanings exported.'))
old=panel[0]['words'];second=panel[2]['words']
proof=dict(f107r=read(A/'KNOWN_COUNTERCASE.json'),f108r=dict(status='UNRESOLVED_SHORT_CERTIFICATE'))
if all(q['alternative_primary']==q['alternative_independent']=='unsat' for q in checks):
    # Only NEXT occurs in CONVEY at slot2; only PAIRED_WITH occurs in PAIR slot2.
    for role,expected in [('NEXT',[('CONVEY',1)]),('PAIRED_WITH',[('PAIR',1)])]:
        locations=[(k,i) for k,pat in g['patterns'].items() for i,t in enumerate(pat) if role in (g['types'][t[1:]] if t.startswith('@') else [t])]
        assert locations==expected
    assert second[13]=='chedain' and second[16]=='lkedy' and len(second)==35
    mandatory=['INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'];base=sum(len(g['patterns'][k]) for k in mandatory);extras=len(g['patterns']['CONVEY'])+len(g['patterns']['PAIR']);assert base==26 and extras==9
    lengths=[len(g['patterns'][k]) for k in ['GOAL','SAFETY','CAPACITY']]
    possible=sorted({5+sum(lengths[i] for i in range(3) if mask&(1<<i)) for mask in range(8)})
    assert 12 not in possible
    proof['f108r']=dict(status='VERIFIED_COMPLETE_PACKING_CONTRADICTION',forced_chedain_role='NEXT',forced_lkedy_role='PAIRED_WITH',required_convey_span=[13,15],required_pair_span=[16,21],mandatory_groups=base,forced_extra_groups=extras,total_groups=35,required_groups_before_convey=12,possible_mandatory_prefix_sizes=possible,reason='The forced two clauses use all nine nonmandatory groups; no other optional clause can fill the missing prefix. INITIAL plus any subset of the other interior mandatory clauses cannot occupy12groups.')
bijective=all(q['primary']=='UNSAT' and q['independent']=='unsat' for q in validation['checks'] if q['id'] in ['BIJECTIVE_0-1','BIJECTIVE_0-2'])
prior=read(R/s['source_original_candidates']);pval=read(R/s['source_original_validation']);cval=read(R/s['source_context_validation']);cr=read(R/s['source_context_results'])
assert prior['exhaustive_projection'] and next(x for x in pval['families'] if x['family']=='BIJECTIVE')['final_blocked_cvc5']=='unsat' and cval['unverified_primary_negatives']==0
covered=[]
for r in cr:
    candidates=[q for q in r['rows'] if q['candidate']!='UNPINNED'];assert len(candidates)==36
    if all(q['status']=='unsat' for q in candidates):covered.append(dict(paragraph=r['paragraph'],certificate='GDT1007_ALL_36_PROJECTIONS_EXCLUDED'))
    else:
        assert r['paragraph'] in [p['id'] for p in panel[1:]] and bijective
        covered.append(dict(paragraph=r['paragraph'],certificate='GDT1008_COMPLETE_SHARED_GRAMMAR_EXCLUDED'))
assert len(covered)==120
proof['bounded_bijective_closure']=dict(status='VERIFIED_DEPENDENCY_COMPOSITION',paragraphs=120,by_projection=118,by_complete_joint_grammar=2,certificates=covered,scope='Every exposed other-leaf26–37group whole paragraph with exact chedy in the fixed census; conditional source readings and original inventory retained.',functional_global_closure=False,confirmed_words=0,independent_meaning_capacity=0)
put('EXPLANATIONS.json',proof);print(json.dumps(dict(role_checks=checks,f108r=proof['f108r'],bounded_bijective_closure=120),indent=2))
