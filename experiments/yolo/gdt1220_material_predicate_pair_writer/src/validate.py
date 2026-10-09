"""Standalone reconstruction; same author, no imports from legacy/new runner."""
from pathlib import Path
from collections import Counter
import hashlib,itertools,json,math,re
D=Path(__file__).resolve().parents[1];R=D.parents[2];A=D/'artifacts'
BASE=R/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts'
PREFIX=['','o','qo','ok','ot','ol','or','al','ar','ya','ye','yo','da','de','do','sa','se','so','ra','re','ro','la','le','lo','ka','ke','ko','ta','te','to','sha','she']
HEAD=['d','ch','k','t','sh','s','r','l'];MID=['a','e','o','ee'];END=['y','in','l','r']
ROOTS=[''.join(p) for p in itertools.product(PREFIX,HEAD,MID,END)]
REVERSE={s:i for i,s in enumerate(ROOTS)}
GLYPH=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')


def digest(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def parse(w):
    g=GLYPH.findall(w);assert ''.join(g)==w;return g

def encode_record(r):
    left=0
    for i,base in [(1,64),(2,8),(3,8)]: left=left*base+r[i]
    right=0
    for i,base in [(0,8),(4,8),(5,4),(6,4)]: right=right*base+r[i]
    return left,right

def decode_record(left,right):
    vals={}
    for i,base in [(3,8),(2,8),(1,64)]: left,vals[i]=divmod(left,base)
    for i,base in [(6,4),(5,4),(4,8),(0,8)]: right,vals[i]=divmod(right,base)
    assert left==right==0
    return [vals[i] for i in range(7)]

def lines(words):
    out=[];current=[]
    for w in words:
        if current and sum(len(parse(x)) for x in current)+len(current)+len(parse(w))>48:
            out.append(current);current=[]
        current.append(w)
    if current: out.append(current)
    return out

def h(c):
    n=sum(c.values())
    return math.log2(n)-sum(v*math.log2(v) for v in c.values())/n if n else 0.

def js(a,b):
    u=sum(a.values());v=sum(b.values());z=0.
    for k in set(a)|set(b):
        p=a[k]/u;q=b[k]/v
        if p:z+=p/2*math.log2(2*p/(p+q))
        if q:z+=q/2*math.log2(2*q/(p+q))
    return z

def edit1(a,b):
    if len(a)==len(b): return sum(x!=y for x,y in zip(a,b))==1
    if len(a)>len(b): a,b=b,a
    return len(b)==len(a)+1 and any(b[:i]+b[i+1:]==a for i in range(len(b)))

def measure(all_lines):
    remain=8000;sample=[]
    for line in all_lines:
        if not remain:break
        here=line[:remain];sample.append(here);remain-=len(here)
    assert remain==0
    words=[w for ln in sample for w in ln];gs=[parse(w) for w in words]
    wc=Counter(words);gc=Counter(itertools.chain.from_iterable(gs));lc=Counter(map(len,gs))
    initial=Counter(x[0] for x in gs);final=Counter(x[-1] for x in gs)
    bc=Counter((w[i-1],w[i]) for w in gs for i in range(1,len(w)))
    prev=Counter()
    for (a,b),n in bc.items():prev[a]+=n
    pairs=[(parse(ln[i-1]),parse(ln[i])) for ln in sample for i in range(1,len(ln))]
    mu=sum(k*n for k,n in lc.items())/8000
    return dict(tokens=8000,types=len(wc),type_ratio=len(wc)/8000,mean_length=mu,
        sd_length=math.sqrt(sum(n*(k-mu)**2 for k,n in lc.items())/8000),
        top10_share=sum(sorted(wc.values(),reverse=True)[:10])/8000,
        word_entropy=h(wc),glyph_entropy=h(gc),conditional_entropy=h(bc)-h(prev),
        first_last_js=js(initial,final),adjacent_pairs=len(pairs),
        exact_repeat=sum(a==b for a,b in pairs)/len(pairs),
        edit1_repeat=sum(edit1(a,b) for a,b in pairs)/len(pairs),
        glyph_counts=dict(gc),length_counts={str(k):v for k,v in sorted(lc.items())},
        q_followed_o=bc['q','o']/prev['q'] if prev['q'] else None,
        q_count=gc['q'],y_final=final['y']/8000)

def nested_equal(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a:nested_equal(a[k],b[k])
    elif type(a)==float: assert abs(a-b)<1e-11,(a,b)
    else:assert a==b,(a,b)

def full_checks(m,t):
    rel={'mean_length':.20,'sd_length':.25}
    absolute={'top10_share':.05,'type_ratio':.05,'conditional_entropy':.30,
              'exact_repeat':.01,'edit1_repeat':.03,'first_last_js':.12}
    rows={}
    for k,lim in {**{k:v*t[k] for k,v in rel.items()},**absolute}.items():
        delta=abs(m[k]-t[k]);rows[k]=dict(model=m[k],target=t[k],difference=delta,limit=lim,within=delta<=lim)
    tv=sum(abs(m['length_counts'].get(k,0)-t['length_counts'].get(k,0)) for k in set(m['length_counts'])|set(t['length_counts']))/16000
    dist=js(Counter(m['glyph_counts']),Counter(t['glyph_counts']))
    rows['length_tv']=dict(difference=tv,limit=.20,within=tv<=.20)
    rows['glyph_js']=dict(difference=dist,limit=.10,within=dist<=.10)
    base=dict(diagnostics=rows,passed=sum(v['within'] for v in rows.values()),total=10,joint_screen=all(v['within'] for v in rows.values()))
    limits={'edit1_repeat':.01,'q_followed_o':.03,'q_count':.25*t['q_count'],'y_final':.05,'glyph_entropy':.15,'word_entropy':.30}
    extra={k:dict(model=m[k],target=t[k],limit=v,within=m[k] is not None and t[k] is not None and abs(m[k]-t[k])<=v) for k,v in limits.items()}
    return base,extra

def main():
    for p,v in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((R/p).read_bytes()).hexdigest()==v,p
    source=json.loads((BASE/'SOURCE_MESSAGES.json').read_text());targets=json.loads((BASE/'RESULT.json').read_text())['targets']
    result=json.loads((A/'RESULT.json').read_text());stored=json.loads((A/'PARAGRAPH_RECEIPTS.json').read_text())
    assert len(ROOTS)==len(REVERSE)==4096
    for n in range(4096): assert encode_record(decode_record(n,0))[0]==n
    for n in range(1024): assert encode_record(decode_record(0,n))[1]==n
    teaching=[[3,0,0,1,1,0,2],[3,0,0,1,1,1,2],[3,1,0,1,1,1,2],[3,1,0,1,1,1,2]]
    manual=[list(encode_record(r)) for r in teaching]
    assert manual==[[1,402],[1,406],[65,406],[65,406]]
    sample=[];all_lines=[];receipts=[]
    assert len(source)==256
    for p,page in enumerate(source):
        assert len(page)==20
        nums=list(itertools.chain.from_iterable(encode_record(r) for r in page))
        words=[ROOTS[n] for n in nums];wrapped=lines(words);all_lines+=wrapped
        got=[REVERSE[w] for line in wrapped for w in line]
        assert [decode_record(*got[i:i+2]) for i in range(0,len(got),2)]==page
        if p<200: sample+=nums
        receipts.append(dict(paragraph=p,records=len(page),groups=len(nums),lines=len(wrapped),
            address_hash=digest(nums),surface_hash=digest(words),line_hash=digest(wrapped)))
    assert receipts==stored and len(sample)==8000
    ct=Counter(sample);assert {str(k):v for k,v in ct.items()}==json.loads((A/'FREQUENCIES.json').read_text())
    v=len(ct);top=sum(sorted(ct.values(),reverse=True)[:10])
    assert (v,top)==(result['types'],result['top10_count'])
    necessary={ed:dict(types=abs(v-t['types'])<=400,top10=abs(top-round(t['top10_share']*8000))<=400) for ed,t in targets.items()}
    assert necessary==result['necessary_checks'];passed=all(all(x.values()) for x in necessary.values())
    assert passed==result['stage1_pass'];full_checks_count=0
    if passed:
        assert result['full_stage']=='EXECUTED'
        met=measure(all_lines);nested_equal(met,result['metrics']);full=True
        for ed,t in targets.items():
            base,extra=full_checks(met,t)
            nested_equal(base,result['base_checks'][ed]);nested_equal(extra,result['strengthened_checks'][ed])
            full &= base['joint_screen'] and all(c['within'] for c in extra.values());full_checks_count+=16
        assert full==result['full_pass']
        assert result['status']==('MATERIAL_PREDICATE_FULL_SCREEN_PASS' if full else 'MATERIAL_PREDICATE_FULL_SCREEN_FAIL')
    else:
        assert result['full_stage']=='NOT_RUN_NECESSARY_FAILURE' and 'metrics' not in result
        assert result['status']=='MATERIAL_PREDICATE_FREQUENCY_FAIL'
    assert [result[k] for k in ['full_source_records','full_source_paragraphs','full_output_groups','sample_groups','sample_paragraphs']]==[5120,256,10240,8000,200]
    run=json.loads((A/'RUN_RECEIPT.json').read_text())
    assert run['manual_addresses']==manual and run['sample_address_hash']==digest(sample)
    assert run['material_inverse_values']==4096 and run['predicate_inverse_values']==1024
    checked=dict(status='PASS',experiment='GDT1220',scientific_status=result['status'],source_record_inverses=5120,
        material_values=4096,predicate_values=1024,necessary_conditions=6,conditional_full_conditions=full_checks_count,
        source_paragraphs=256,independent_implementation_same_author=True,imports_legacy_or_runner=False,
        native_meanings=0,independent_holdout=False)
    (A/'VALIDATION.json').write_text(json.dumps(checked,indent=2)+'\n');print(json.dumps(checked,indent=2))

if __name__=='__main__':main()
