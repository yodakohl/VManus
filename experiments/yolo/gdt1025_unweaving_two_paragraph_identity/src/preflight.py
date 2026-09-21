from common import *
import model
from independent import facts,verify_joint
import copy

s=source();sp=spec();oldsp=read(OLD/'src/SPEC.json');oldsrc=read(OLD/'src/SOURCE.json')
parser=module('old_forward_synthetic',OLD/'src/model.py');ind=module('old_reverse_synthetic',OLD/'src/independent.py')
rename={w:'invented_'+str(i) for i,w in enumerate(sp['lexicon'])}
synthetic=copy.deepcopy(sp);synthetic['lexicon']={rename[w]:list(v) for w,v in sp['lexicon'].items()}
synthetic_old=copy.deepcopy(oldsp);synthetic_old['lexicon']={rename[w]:list(v) for w,v in oldsp['lexicon'].items()}
newwords=[rename[w] for c in s['new_complete_clauses'] for w in c['raw'].split()]
oldwords=[rename[w] for l in oldsrc['projected_lines'] for w in l['raw'].split()]
checks=[]
for suffix in ('A','B'):
    replacements={'CURRENT_CLOTH':'TOY_C_'+suffix,'WOMAN':'TOY_W_'+suffix,'WOOERS':'TOY_O_'+suffix}
    for d in (synthetic,synthetic_old):
        for v in d['lexicon'].values():
            for old,new in replacements.items():
                if v[1]==old or v[1].startswith('TOY_'+old[0]):v[1]=new
    # Rebuild from the immutable declared values for each independently named case.
    for d,original in [(synthetic,sp),(synthetic_old,oldsp)]:
        d['lexicon']={rename[w]:[v[0],replacements.get(v[1],v[1])] for w,v in original['lexicon'].items()}
    ps,unknown=parser.parse_all(newwords,synthetic);po,_=parser.parse_all(oldwords,synthetic_old)
    assert not unknown and len(ps)==len(po)==1 and ind.parses(newwords,synthetic)==ps
    g=model.construct(ps[0]);assert g==facts(ps[0])
    for pairing in ('direct','reversed'):
        old=parser.construct(po[0],pairing);ind.validate_graph(po[0],old,pairing)
        for mode in ('SHARED_FRAME','SEPARATE_V_DIAGNOSTIC'):
            result=model.join(g,old,mode);issues=verify_joint(g,old,mode,result)
            assert issues==(['SHARED_V_SOLE_PHASE'] if pairing=='reversed' and mode=='SHARED_FRAME' else [])
            checks.append(dict(case=suffix,pairing=pairing,mode=mode,errors=issues))
    for kind in ('N4','N5','N8','N10'):
        incomplete=[c for c in ps[0] if c['kind']!=kind]
        try:model.construct(incomplete)
        except (ValueError,KeyError):pass
        else:raise AssertionError('missing binding accepted:'+kind)
    old=parser.construct(po[0],'direct')
    for mutation in ('early_completion','asserted_requirement','late_ignorance','wrong_first','wrong_recurrence'):
        bad=copy.deepcopy(g)
        if mutation=='early_completion':bad['states'].append(dict(clause='synthetic',predicate='FINISHED',cloth=bad['cloth'],at='PRIOR',truth=True))
        elif mutation=='asserted_requirement':bad['requirements'][0]['asserted_truth']=True
        elif mutation=='late_ignorance':bad['knowledge'][0]['period']='AFTER_DISCOVERY'
        elif mutation=='wrong_first':bad['habits'][0]['action']='WOMAN'
        else:bad['recurrence'][0]['referent']='UNWRITTEN_G'
        result=model.join(bad,old,'SHARED_FRAME');assert result['errors'];verify_joint(bad,old,'SHARED_FRAME',result)
for i in range(11):
    start=sum(len(c['raw'].split()) for c in s['new_complete_clauses'][:i]);bad=newwords[:start]+newwords[start+1:]
    p,u=parser.parse_all(bad,synthetic);assert not p and not u and not ind.parses(bad,synthetic)
assert model.condition('TIME_PHASE','DAY')==dict(kind='REGION_MEMBERSHIP',region='DAY')
assert model.condition('FINISH_PREDICATE','FINISHED','C')==dict(kind='STATE_TRUTH',predicate='FINISHED',cloth='C')
write(A/'PREFLIGHT.json',dict(status='PASS',executed_utc=now(),renamed_program_cases=checks,missing_binding_cases=8,semantic_countercases=10,omitted_terminal_cases=11,new_target_compilation=False))
print('PASS: 8 renamed programs, 8 missing bindings, 10 semantic countercases, 11 omitted terminals')
