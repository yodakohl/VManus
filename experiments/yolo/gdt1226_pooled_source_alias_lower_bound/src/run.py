"""All-mixture lower bound, with exact independently checkable certificates."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime, timezone
import hashlib,json
import numpy as np
import scipy
from scipy.optimize import linprog
D=Path(__file__).resolve().parents[1]; R=D.parents[2]; A=D/'artifacts'
BOOKS=('b4','w1','bs1','gr1')
B=R/'experiments/yolo/gdt1202_whole_word_two_alias_capacity/artifacts'
def save(n,x): (A/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def fractions(v):
    a=[F(float(max(0,x))).limit_denominator(10**9) for x in v]
    assert sum(a)>0
    return [x/sum(a) for x in a]
def main():
    assert not (A/'RESULT.json').exists(),'Use a fresh reproduction directory'
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    assert scipy.__version__=='1.14.1'
    raw=json.loads((B/'FREQUENCIES.json').read_text())
    counts={b:{x['word']:x['count'] for x in raw[b]} for b in BOOKS}
    assert all(sum(c.values())==8000 for c in counts.values())
    words=sorted(set().union(*(set(c) for c in counts.values())))
    M=np.array([[counts[b].get(w,0) for b in BOOKS] for w in words],dtype=float)
    def top(v):return tuple(sorted(sorted(range(len(words)),key=lambda i:(-v[i],words[i]))[:5]))
    cuts=[]
    for j in range(4):
        c=top(M[:,j])
        if c not in cuts:cuts.append(c)
    trace=[];candidate=None;termination='ITERATION_CAP'
    for step in range(100):
        rows=np.array([M[list(c)].sum(axis=0) for c in cuts])
        res=linprog([0,0,0,0,1],A_ub=np.column_stack([rows,-np.ones(len(rows))]),
          b_ub=np.zeros(len(rows)),A_eq=[[1,1,1,1,0]],b_eq=[1],bounds=[(0,None)]*5,method='highs')
        if not res.success:termination='SOLVER_NO_CANDIDATE';break
        v=M@res.x[:4];worst=top(v);actual=float(v[list(worst)].sum())
        candidate=(list(cuts),res.x[:4],-res.ineqlin.marginals)
        trace.append({'iteration':step,'cuts':len(cuts),'lp_objective':float(res.fun),
          'actual_top5':actual,'worst_words':[words[i] for i in worst]})
        if actual-res.fun<=1e-7:termination='NUMERIC_CUTS_CLOSED';break
        if worst in cuts:termination='NUMERIC_REPEAT';break
        cuts.append(worst)
    assert candidate is not None,'No certificate available'
    used,p,d=candidate;pw=fractions(p);dw=fractions(d)
    masses={w:sum(pw[j]*counts[b].get(w,0) for j,b in enumerate(BOOKS)) for w in words}
    topwords=sorted(words,key=lambda w:(-masses[w],w))[:5]
    upper=sum(masses[w] for w in topwords);cert=[];bvals=[F(0)]*4
    for c,weight in zip(used,dw):
        ws=[words[i] for i in c];vals=[sum(counts[b].get(w,0) for w in ws) for b in BOOKS]
        cert.append({'words':ws,'weight':str(weight),'book_counts':dict(zip(BOOKS,vals))})
        for j,n in enumerate(vals):bvals[j]+=weight*n
    lower=min(bvals);assert 0<=lower<=upper<=8000
    old=json.loads((B/'RESULT.json').read_text());conditions={}
    for ed,row in old['native_limits'].items():
        cap=row['top10_upper_count']
        dec='EXCLUDED' if lower>cap else 'CONTINUOUS_NOT_EXCLUDED' if upper<=cap else 'UNKNOWN'
        conditions[ed]={'ceiling':cap,'decision':dec}
    values={x['decision'] for x in conditions.values()}
    status=('EVERY_MIXTURE_TWO_ALIAS_CONCENTRATION_EXCLUDED' if values=={'EXCLUDED'} else
      'CONCENTRATION_RELAXATION_FEASIBLE' if values=={'CONTINUOUS_NOT_EXCLUDED'} else
      'UNRESOLVED_BOUND' if 'UNKNOWN' in values else 'READER_SPECIFIC_MIXTURE_CAPACITY')
    out={'experiment':'GDT1226','status':status,'sample_mass':8000,'books':list(BOOKS),
      'source_union_types':len(words),'lower_bound':str(lower),'upper_bound':str(upper),
      'exact_gap':str(upper-lower),'lower_count_decimal':float(lower),'upper_count_decimal':float(upper),
      'lower_share':float(lower/8000),'upper_share':float(upper/8000),
      'primal_weights':dict(zip(BOOKS,map(str,pw))),
      'primal_top5':[{'word':w,'mass':str(masses[w])} for w in topwords],
      'dual_book_bounds':dict(zip(BOOKS,map(str,bvals))),'dual_cuts':cert,
      'reader_conditions':conditions,'termination':termination,'trace':trace,
      'scope':'Continuous mixtures of four fixed source profiles; globally at most two forms per exact word. No integer text, type test, physical writer, native meaning or general language claim.'}
    save('RESULT.json',out)
    save('RUN_RECEIPT.json',{'completed_utc':datetime.now(timezone.utc).isoformat(),
      'scipy_version':scipy.__version__,'numpy_version':np.__version__,
      'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    print(json.dumps({k:out[k] for k in ('status','lower_bound','upper_bound','primal_weights','reader_conditions','termination')},indent=2))
if __name__=='__main__':main()
