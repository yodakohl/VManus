"""Independent rational-certificate check; no numerical solver or runner import."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from datetime import datetime,timezone
import hashlib,json
D=Path(__file__).resolve().parents[1];R=D.parents[2];A=D/'artifacts'
B=R/'experiments/yolo/gdt1202_whole_word_two_alias_capacity/artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def main():
    for p,h in load(A/'REGISTRATION_LOCK.json')['files'].items():assert sha(R/p)==h,p
    result=load(A/'RESULT.json');books=('b4','w1','bs1','gr1')
    assert result['books']==list(books) and result['sample_mass']==8000
    source=R/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
    recipes=load(source);old=load(B/'FREQUENCIES.json');receipt=load(B/'SOURCE_RECEIPT.json')
    assert sha(source)==receipt['source_sha256']
    counts={}
    for b in books:
        sample=[]
        for rec in recipes[b]:
            for word in rec['words']:
                if len(sample)<8000:sample.append(word)
        assert len(sample)==8000
        h=hashlib.sha256(json.dumps(sample,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        assert h==receipt['books'][b]['ordered_sample_sha256']
        c=Counter(sample);counts[b]=c
        assert c=={x['word']:x['count'] for x in old[b]}
        assert len(old[b])==len(c)
        assert all(x['balanced_two_counts']==[(x['count']+1)//2,x['count']//2] for x in old[b])
    words=set().union(*(set(c) for c in counts.values()))
    assert len(words)==result['source_union_types']
    p={b:F(result['primal_weights'][b]) for b in books}
    assert sum(p.values())==1 and min(p.values())>=0
    masses={w:sum(p[b]*counts[b][w] for b in books) for w in words}
    names=sorted(words,key=lambda w:(-masses[w],w))[:5]
    upper=sum(masses[w] for w in names);assert sum(masses.values())==8000
    assert [{'word':w,'mass':str(masses[w])} for w in names]==result['primal_top5']
    dsum=F(0);bounds={b:F(0) for b in books}
    for cut in result['dual_cuts']:
        s=set(cut['words']);assert len(s)==5 and len(cut['words'])==5 and s<=words
        d=F(cut['weight']);assert d>=0;dsum+=d
        for b in books:
            n=sum(counts[b][w] for w in s)
            assert n==cut['book_counts'][b];bounds[b]+=d*n
    assert dsum==1
    lower=min(bounds.values());assert 0<=lower<=upper<=8000
    assert result['lower_bound']==str(lower) and result['upper_bound']==str(upper)
    assert result['exact_gap']==str(upper-lower)
    assert {b:str(v) for b,v in bounds.items()}==result['dual_book_bounds']
    target=R/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
    assert sha(target)==receipt['target_summary_sha256']
    conditions={}
    for ed,t in load(target)['targets'].items():
        assert t['tokens']==8000
        n=round(8000*t['top10_share']);assert abs(n/8000-t['top10_share'])<1e-12
        cap=n+400
        dec='EXCLUDED' if lower>cap else 'CONTINUOUS_NOT_EXCLUDED' if upper<=cap else 'UNKNOWN'
        conditions[ed]={'ceiling':cap,'decision':dec}
    assert conditions==result['reader_conditions']
    values={x['decision'] for x in conditions.values()}
    status=('EVERY_MIXTURE_TWO_ALIAS_CONCENTRATION_EXCLUDED' if values=={'EXCLUDED'} else
      'CONCENTRATION_RELAXATION_FEASIBLE' if values=={'CONTINUOUS_NOT_EXCLUDED'} else
      'UNRESOLVED_BOUND' if 'UNKNOWN' in values else 'READER_SPECIFIC_MIXTURE_CAPACITY')
    assert status==result['status']
    out={'status':'PASS','completed_utc':datetime.now(timezone.utc).isoformat(),
      'source_sample_positions_checked':32000,'all_source_profiles_reconstructed':True,
      'exact_primal_and_dual_certificates_checked':True,'optimizer_used':False,
      'runner_imported':False,'research_independence':False,'lower_bound':str(lower),
      'upper_bound':str(upper),'decision':status,'result_sha256':sha(A/'RESULT.json')}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
