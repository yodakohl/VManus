from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
import hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SOURCE='experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
def rat(x):return [x.numerator,x.denominator]
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
    for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    source=json.loads((R/SOURCE).read_text());result={};counts=[]
    assert set(source)=={'b4','w1','bs1','gr1'}
    for book in ['b4','w1','bs1','gr1']:
        words=Counter();totals=Counter()
        for row in source[book]:
            c=Counter()
            for word in row['words']:
                c['original_words']+=1
                if not re.fullmatch('[a-z]+',word):c['non_ascii_or_nonletter_words']+=1
                elif len(word)<5:c['too_short_words']+=1
                else:c['eligible_words']+=1;words[word[1:-1]]+=1
            counts.append({'collection':book,'recipe':row['id'],'counts':dict(c)});totals.update(c)
        letters=sorted(set(''.join(words)));observed=Counter();expected=defaultdict(Fraction);mass=Counter();touch=Counter()
        for w,f in words.items():
            cc=Counter(w);n=len(w)
            for a,b in zip(w,w[1:]):
                if a!=b:observed[tuple(sorted([a,b]))]+=f
            for a,b in itertools.combinations(sorted(cc),2):expected[a,b]+=Fraction(2*f*cc[a]*cc[b],n)
            mass.update({a:f*v for a,v in cc.items()});touch.update({a:f for a in cc})
        weights={pair:Fraction(observed[pair])-expected[pair] for pair in itertools.combinations(letters,2)}
        qweights={p:round(v*1000000) for p,v in weights.items()};trials=[]
        for name in ['aeiou','aeiouy']:
            ref=set(name)&set(letters);assert ref and ref!=set(letters)
            exact=sum((v for (a,b),v in weights.items() if (a in ref)!=(b in ref)),Fraction(0));quant=sum(v for (a,b),v in qweights.items() if (a in ref)!=(b in ref));flips=[]
            for u in letters:
                changed=ref^{u}
                if not changed or changed==set(letters):continue
                score=sum((v for (a,b),v in weights.items() if (a in changed)!=(b in changed)),Fraction(0));qscore=sum(v for (a,b),v in qweights.items() if (a in changed)!=(b in changed))
                flips.append({'letter':u,'direction':'remove_from_reference' if u in ref else 'add_to_reference','delta_exact':rat(score-exact),'delta_quantized':qscore-quant,'interior_occurrences':mass[u],'interior_groups_touched':touch[u]})
            trials.append({'reference':name,'active_reference':sorted(ref),'duplicate_without_y':name=='aeiouy' and 'y' not in letters,'baseline_exact':rat(exact),'baseline_quantized':quant,'flips':flips,'improving_letters':[f['letter'] for f in flips if f['delta_quantized']>0],'decision':'REFERENCE_NOT_GLOBAL_MAXIMUM' if any(f['delta_quantized']>0 for f in flips) else 'NO_SINGLE_FLIP_WITNESS_LOCAL_ONLY'})
        result[book]={'recipes':len(source[book]),'counts':dict(totals),'interior_types':len(words),'interior_units':sum(mass.values()),'letters':letters,'weights':[{'pair':list(p),'observed':observed[p],'expected':rat(expected[p]),'exact':rat(v),'quantized':qweights[p]} for p,v in weights.items()],'comparisons':trials}
    save('RESULT.json',result);save('SOURCE_ACCOUNT.json',counts)
    print(json.dumps({b:{'counts':r['counts'],'letters':r['letters'],'comparisons':[{'reference':x['reference'],'decision':x['decision'],'improving':[(f['letter'],float(Fraction(*f['delta_exact'])),f['delta_quantized'],f['interior_occurrences']) for f in x['flips'] if f['delta_quantized']>0]} for x in r['comparisons']]} for b,r in result.items()},indent=2))
if __name__=='__main__':main()
