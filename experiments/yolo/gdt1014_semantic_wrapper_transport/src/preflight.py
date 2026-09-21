from common import *
from wrappers import relations,contradictions,impose_z3
from wrapper_independent import relations_independent,constrain
from worker import bounded
import itertools,concurrent.futures,collections,z3
from cvc5 import pythonic as c

def job(j):
    expected=j.pop('expected');one=bounded('primary',j);two=bounded('independent',j)
    assert one['status']==two['status']==expected,(j['id'],expected,one,two)
    return dict(id=j['id'],expected=expected,primary=one['status'],independent=two['status'])

def main():
    s,g=inputs();cases=read(A/'PREDICTIONS.json');panel=read(A/'PANEL.json');scope=[]
    for case in cases:
        gs=relations_independent(set(case['canonical_lexicon'])|set(panel[case['context_index']]['words']));assert gs==case['groups']
        scope.append(dict(id=case['id'],groups=len(gs),pairs=sum(len(x['pairs']) for x in gs)))
    # Complete 3^4 assignment truth table: equal inputs require equal outputs.
    fixtures=[];words=['a','b','qa','qb'];groups=relations(words)
    for values in itertools.product(range(3),repeat=4):
        code=dict(zip(words,map(str,values)));expected='unsat' if values[0]==values[1] and values[2]!=values[3] else 'sat'
        zb=dict(solver=z3.Solver(),num={str(i):i for i in range(3)},lexicon=code,xs={});impose_z3(zb,groups)
        cs=c.Solver();constrain(cs,words,code,{},zb['num']);assert str(zb['solver'].check())==str(cs.check())==expected
        assert bool(contradictions(code,groups))==(expected=='unsat')
        fixtures.append(dict(values=values,expected=expected))
    # Previously saved fixed witnesses only; no new unconstrained target fitting.
    oldcases=read(R/'experiments/yolo/gdt1013_transport_complete_long_worlds/artifacts/PREDICTIONS.json')
    oldprimary=read(R/'experiments/yolo/gdt1013_transport_complete_long_worlds/artifacts/ROWS.json')
    oldindependent=read(R/'experiments/yolo/gdt1013_transport_complete_long_worlds/artifacts/INDEPENDENT.json')
    originals={x['id']:x for x in read(A/'ORIGINAL_CANDIDATES.json')};jobs=[];details=[]
    for case,p,x in zip(oldcases,oldprimary,oldindependent):
        for engine,r in [('primary',p),('independent',x['independent'])]:
            if r['status']!='sat':continue
            member=case['members'][0];rename=member['original_to_canonical'][0];old=originals[member['original_id']]
            lex={w:rename.get(v,v) for w,v in old['code'].items()};lex.update(r['witness']['aliases']);bad=contradictions(lex,relations(lex));expected='unsat' if bad else 'sat'
            jobs.append(dict(id=case['id']+'_'+engine,paragraph=panel[case['context_index']],lexicon=lex,variant=case['variant'],fixed_layout=r['witness']['parse'],expected=expected))
            details.append(dict(id=case['id']+'_'+engine,expected=expected,contradictions=bad))
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:rows=list(pool.map(job,jobs))
    # Verify that the two full models differ from1013 only by the displayed hook.
    old=read(E/'src/SPEC.json');orig=(R/old['source_world']).read_text();current=(E/'src/world.py').read_text()
    marker="built=build(p,lex,g,variant,timeout,fixed_layout);s=built['solver'];answer=str(s.check());out=dict(status=answer)"
    hook="built=build(p,lex,g,variant,timeout,fixed_layout)\n    from wrappers import relations,impose_z3\n    impose_z3(built,relations(set(lex)|set(p['words'])))\n    s=built['solver'];answer=str(s.check());out=dict(status=answer)"
    assert orig.count(marker)==1 and current==orig.replace(marker,hook)
    orig=(R/old['source_independent']).read_text();marker="    answer=str(solver.check());out=dict(status=answer,solver='cvc5',version=cvc5.__version__)"
    hook="    from wrapper_independent import constrain\n    constrain(solver,raw,lex,xs,code)\n"+marker
    assert orig.count(marker)==1 and (E/'src/independent.py').read_text()==orig.replace(marker,hook)
    out=dict(status='PASS',scope_checks=scope,truth_table=fixtures,fixed_witnesses=rows,fixed_contradictions=details,full_model_hook_diff_only=True,inherited_full_model_preflight='GDT1013:1152fixedcases234SAT918UNSAT',counts=dict(collections.Counter(x['expected'] for x in rows)),new_unconstrained_queries=0,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    put('PREFLIGHT.json',out);print(json.dumps({k:v for k,v in out.items() if k not in ('scope_checks','truth_table','fixed_witnesses','fixed_contradictions')},indent=2))
if __name__=='__main__':main()
