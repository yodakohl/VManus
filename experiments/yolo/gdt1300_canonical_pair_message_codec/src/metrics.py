"""Transparent descriptive metrics, no fitted target model."""
from collections import Counter,defaultdict
import math
from codec import SIGNS

ORDER=sorted(SIGNS,key=lambda x:(-len(x),x))
def glyphs(word):
    out=[];i=0
    while i<len(word):
        sign=next((s for s in ORDER if word.startswith(s,i)),None)
        if sign is None:return None
        out.append(sign);i+=len(sign)
    return out

def entropy(counts):
    n=sum(counts.values())
    return -sum(c/n*math.log2(c/n) for c in counts.values()) if n else 0

def js(a,b):
    sa=sum(a.values());sb=sum(b.values());result=0
    for k in a.keys()|b.keys():
        p=a.get(k,0)/sa;q=b.get(k,0)/sb;m=(p+q)/2
        if p:result+=.5*p*math.log2(p/m)
        if q:result+=.5*q*math.log2(q/m)
    return result

def edit_one(a,b):
    if abs(len(a)-len(b))>1 or a==b:return False
    if len(a)==len(b):return sum(x!=y for x,y in zip(a,b))==1
    if len(a)>len(b):a,b=b,a
    i=j=0;removed=0
    while i<len(a) and j<len(b):
        if a[i]==b[j]:i+=1;j+=1
        else:j+=1;removed+=1
        if removed>1:return False
    return True

def measure(segments,n=8000):
    # Truncate a single explicitly documented token stream, preserving all
    # definite-neighbour and physical-line boundaries. Never join over holes.
    pieces=[];left=n
    for seg in segments:
        if not left:break
        s=seg[:left]
        if s:pieces.append(s);left-=len(s)
    assert left==0,('insufficient sample',n-left)
    words=[w for s in pieces for w in s];parsed=[glyphs(w) for w in words]
    assert all(parsed)
    wc=Counter(words);gc=Counter(g for w in parsed for g in w)
    lc=Counter(map(len,parsed));first=Counter(w[0] for w in parsed);last=Counter(w[-1] for w in parsed)
    bc=Counter((a,b) for w in parsed for a,b in zip(w,w[1:]));prev=Counter()
    for (a,b),c in bc.items():prev[a]+=c
    cond=sum(-c*math.log2(c/prev[a]) for (a,b),c in bc.items())/sum(bc.values())
    pairs=[(a,b) for seg in pieces for a,b in zip(seg,seg[1:])]
    mean=sum(k*v for k,v in lc.items())/n
    return dict(tokens=n,types=len(wc),type_ratio=len(wc)/n,mean_length=mean,
                sd_length=math.sqrt(sum((k-mean)**2*v for k,v in lc.items())/n),
                top10_share=sum(v for _,v in wc.most_common(10))/n,
                word_entropy=entropy(wc),glyph_entropy=entropy(gc),conditional_entropy=cond,
                first_last_js=js(first,last),adjacent_pairs=len(pairs),
                exact_repeat=sum(a==b for a,b in pairs)/len(pairs),
                edit1_repeat=sum(edit_one(glyphs(a),glyphs(b)) for a,b in pairs)/len(pairs),
                glyph_counts=dict(gc),length_counts={str(k):v for k,v in sorted(lc.items())},
                q_followed_o=(bc['q','o']/prev['q'] if prev['q'] else None),
                q_count=gc['q'],y_final=sum(w[-1]=='y' for w in parsed)/n)

TOLERANCES={'mean_length':('relative',.20),'sd_length':('relative',.25),
            'top10_share':('absolute',.05),'type_ratio':('absolute',.05),
            'conditional_entropy':('absolute',.30),'exact_repeat':('absolute',.01),
            'edit1_repeat':('absolute',.03),'first_last_js':('absolute',.12)}
def compare(model,target):
    rows={}
    for key,(kind,tol) in TOLERANCES.items():
        d=abs(model[key]-target[key]);limit=tol*target[key] if kind=='relative' else tol
        rows[key]={'model':model[key],'target':target[key],'difference':d,'limit':limit,'within':d<=limit}
    tv=.5*sum(abs(model['length_counts'].get(k,0)/model['tokens']-target['length_counts'].get(k,0)/target['tokens']) for k in model['length_counts'].keys()|target['length_counts'].keys())
    dist=js(model['glyph_counts'],target['glyph_counts'])
    rows['length_tv']={'difference':tv,'limit':.20,'within':tv<=.20}
    rows['glyph_js']={'difference':dist,'limit':.10,'within':dist<=.10}
    return {'diagnostics':rows,'passed':sum(r['within'] for r in rows.values()),
            'total':len(rows),'joint_screen':all(r['within'] for r in rows.values())}
