"""Independent metric formulas retained from GDT1174 validator; no producer import."""
import collections,math,re
SIGNS=['a', 'o', 'e', 'i', 'n', 'd', 'q', 'y', 's', 'r', 'l', 'm', 'k', 't', 'p', 'f', 'ch', 'sh', 'ckh', 'cth', 'cph', 'cfh']
PAT=re.compile('|'.join(sorted(SIGNS,key=lambda v:(-len(v),v))))

def parse(word):
    parts=PAT.findall(word)
    return parts if ''.join(parts)==word else None
def H(c):
    total=sum(c.values())
    return math.log2(total)-sum(n*math.log2(n) for n in c.values())/total
def distance(a,b):
    old=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        new=[i]
        for j,y in enumerate(b,1):new.append(min(new[-1]+1,old[j]+1,old[j-1]+(x!=y)))
        old=new
    return old[-1]
def near(a,b):return abs(a-b)<1e-10

def independent(segments):
    out=[];left=8000
    for seg in segments:
        if left<=0:break
        chosen=seg[:left];left-=len(chosen)
        if chosen:out.append(chosen)
    assert left==0
    words=[w for line in out for w in line];g=[parse(w) for w in words]
    assert all(g)
    lex=collections.Counter(words);letters=collections.Counter(x for w in g for x in w)
    lengths=collections.Counter(map(len,g));pairs=collections.Counter((a,b) for w in g for a,b in zip(w,w[1:]));first=collections.Counter()
    for (a,b),n in pairs.items():first[a]+=n
    mu=sum(map(len,g))/8000
    adjacent=[(a,b) for line in out for a,b in zip(line,line[1:])]
    beginnings=collections.Counter(w[0] for w in g);endings=collections.Counter(w[-1] for w in g)
    mixture={k:(beginnings[k]+endings[k])/16000 for k in beginnings.keys()|endings.keys()}
    edge_js=-sum(v*math.log2(v) for v in mixture.values())-(H(beginnings)+H(endings))/2
    return dict(tokens=8000,types=len(lex),type_ratio=len(lex)/8000,mean_length=mu,
                sd_length=math.sqrt(sum((len(w)-mu)**2 for w in g)/8000),
                top10_share=sum(sorted(lex.values(),reverse=True)[:10])/8000,
                word_entropy=H(lex),glyph_entropy=H(letters),conditional_entropy=H(pairs)-H(first),
                first_last_js=edge_js,
                adjacent_pairs=len(adjacent),exact_repeat=sum(a==b for a,b in adjacent)/len(adjacent),
                edit1_repeat=sum(distance(parse(a),parse(b))==1 for a,b in adjacent)/len(adjacent),
                glyph_counts=dict(letters),length_counts={str(k):v for k,v in lengths.items()})

