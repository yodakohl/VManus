from pathlib import Path
from collections import Counter
from fractions import Fraction
import hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def excess(word,V):
    bits=[a in V for a in word];n=len(word);v=sum(bits)
    return Fraction(sum(a!=b for a,b in zip(bits,bits[1:])))-Fraction(2*v*(n-v),n)
def main():
    for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    source=json.loads((R/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());account=json.loads((B/'artifacts/SOURCE_ACCOUNT.json').read_text());actual_accounts=[];checks=0
    for book,rs in source.items():
        words=Counter();totals=Counter()
        for r in rs:
            stats=Counter()
            for w in r['words']:
                stats['original_words']+=1
                if not w or any(c<'a' or c>'z' for c in w):stats['non_ascii_or_nonletter_words']+=1
                elif len(w)<=4:stats['too_short_words']+=1
                else:stats['eligible_words']+=1;words[w[1:-1]]+=1
            actual_accounts.append({'collection':book,'recipe':r['id'],'counts':dict(stats)});totals.update(stats)
        got=result[book];assert got['counts']==dict(totals) and got['recipes']==len(rs) and got['interior_types']==len(words)
        letters=sorted(set().union(*(set(w) for w in words)));assert letters==got['letters']
        assert got['interior_units']==sum(f*len(w) for w,f in words.items())
        edge_weights={}
        for entry in got['weights']:
            a,b=entry['pair'];obs=sum(f*sum({u,v}=={a,b} for u,v in zip(w,w[1:])) for w,f in words.items());exp=sum((Fraction(2*f*w.count(a)*w.count(b),len(w)) for w,f in words.items()),Fraction(0));weight=Fraction(obs)-exp
            assert entry['observed']==obs and Fraction(*entry['expected'])==exp and Fraction(*entry['exact'])==weight and entry['quantized']==round(weight*1000000)
            edge_weights[a,b]=entry['quantized']
        assert len(edge_weights)==len(letters)*(len(letters)-1)//2
        for trial in got['comparisons']:
            ref=set(trial['reference'])&set(letters);assert trial['active_reference']==sorted(ref)
            base=sum((f*excess(w,ref) for w,f in words.items()),Fraction(0));assert Fraction(*trial['baseline_exact'])==base
            qbase=sum(v for (a,b),v in edge_weights.items() if (a in ref)!=(b in ref));assert trial['baseline_quantized']==qbase
            expected_flips=[u for u in letters if ref^{u} and ref^{u}!=set(letters)]
            assert [x['letter'] for x in trial['flips']]==expected_flips
            for flip in trial['flips']:
                u=flip['letter'];changed=ref^{u};delta=sum((f*(excess(w,changed)-excess(w,ref)) for w,f in words.items()),Fraction(0))
                # Only edges incident to the flipped vertex can change.
                qdelta=sum(v*(1 if (a in ref)==(b in ref) else -1) for (a,b),v in edge_weights.items() if u in (a,b))
                assert delta==Fraction(*flip['delta_exact']) and qdelta==flip['delta_quantized']
                assert flip['interior_occurrences']==sum(f*w.count(u) for w,f in words.items())
                assert flip['interior_groups_touched']==sum(f for w,f in words.items() if u in w)
                checks+=1
            improving=[f['letter'] for f in trial['flips'] if f['delta_quantized']>0];assert improving==trial['improving_letters']
            assert trial['decision']==('REFERENCE_NOT_GLOBAL_MAXIMUM' if improving else 'NO_SINGLE_FLIP_WITNESS_LOCAL_ONLY')
    assert sorted(account,key=lambda r:(r['collection'],r['recipe']))==sorted(actual_accounts,key=lambda r:(r['collection'],r['recipe']))
    fixtures=0
    for n in range(2,7):
        for ones in range(n+1):
            permutations=set(itertools.permutations('a'*ones+'b'*(n-ones)))
            assert sum((excess(w,{'a'}) for w in permutations),Fraction(0))==0;fixtures+=1
    assert [round(Fraction(x,2)) for x in [1,3,5,-1,-3,-5]]==[0,2,2,0,-2,-2]
    out={'status':'PASS','source_collections':len(result),'source_recipes':len(account),'checked_flips':checks,'exact_bag_fixtures':fixtures,'scope':'Independent per-word score, source eligibility and all quantized/rational flips; no native or phonetic validation.'}
    (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
