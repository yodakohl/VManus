import json,hashlib,itertools,datetime,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
LABELS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
SOURCE='ABCDEFGHIJKLMNOPQRSTUV #'
MESSAGES=['HEAT OIL#','HEAT GIN#']
def digitize(values):return [d for v in values for d in (v//4,v%4)]
def options(w,p,width):
    seen=set();out=[]
    for distance in range(len(w)):
        j=(p+distance)%len(w)
        if w[j] not in seen:seen.add(w[j]);out.append(j)
        if len(out)==width:return out
    raise ValueError('insufficient labels')
def encode(w,values):
    p=0;out=[];trace=[]
    for i,d in enumerate(digitize(values)):
        width=6 if i%2==0 else 4;start=p;p=options(w,p,width)[d];out.append(w[p]);trace.append(dict(step=i,width=width,rank=d,start=start,destination=p,label=w[p]))
    return out,trace

def decode(w,cipher):
    assert len(cipher)%2==0;p=0;digits=[]
    for i,g in enumerate(cipher):
        candidates=options(w,p,6 if i%2==0 else 4);labels=[w[q] for q in candidates];rank=labels.index(g);digits.append(rank);p=candidates[rank]
    return [4*digits[i]+digits[i+1] for i in range(0,len(digits),2)]
def desired(digits,initial,cycle):
    out=[];g=initial;k=0
    for d in digits:
        if d:
            while cycle[k%len(cycle)]==g:k+=1
            g=cycle[k%len(cycle)];k+=1
        out.append(g)
    return out

def construct(digits,cipher,alphabet,initial):
    w=[initial];g=initial
    for d,h in zip(digits,cipher):
        assert (d==0)==(h==g)
        if d:
            fillers=[c for c in alphabet if c not in (g,h)][:d-1];assert len(fillers)==d-1
            w.extend(fillers);w.append(h)
        g=h
    used_end=len(w)-1
    w.extend(c for c in alphabet if c not in w)
    assert len(w)<=1+sum(digits)+len(alphabet)
    return w,used_end

def controls():
    n=0;alphabet=list('abcdef')
    for length in range(1,4):
        for vals in itertools.product(range(24),repeat=length):
            ds=digitize(vals);c=desired(ds,'a',alphabet[1:]);w,_=construct(ds,c,alphabet,'a')
            assert encode(w,vals)[0]==c and decode(w,c)==list(vals)
            assert [a==b for a,b in zip(['a']+c,c)]==[d==0 for d in ds];n+=1
    return dict(status='PASS',source_sequences=n,source_lengths=[1,2,3],output_alphabet_size=6)

def main():
    for path,h in json.loads((P/'src/REGISTRATION_LOCK.json').read_text())['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
    assert len(SOURCE)==24 and len(set(SOURCE))==24
    vals=[[SOURCE.index(c) for c in message] for message in MESSAGES];ds=[digitize(v) for v in vals]
    assert [d==0 for d in ds[0]]==[d==0 for d in ds[1]]
    cipher=desired(ds[0],'o',['e','d','y','a','l','ch','i','n']);built=[construct(d,cipher,LABELS,'o') for d in ds]
    common_size=max(len(w) for w,end in built);records=[]
    for message,vs,d,(w,last) in zip(MESSAGES,vals,ds,built):
        unpadded=len(w);w=w+['o']*(common_size-len(w));c,trace=encode(w,vs);assert c==cipher
        decoded=''.join(SOURCE[v] for v in decode(w,c));assert decoded==message and message.count('#')==1 and message.endswith('#')
        records.append(dict(source=message,source_values=vs,digits=d,chart=w,unpadded_positions=unpadded,positions=len(w),last_used_constructed_position=last,trace=trace,decoded=decoded))
    classes={}
    for v in range(24):
        key=('zero' if v//4==0 else 'nonzero')+'_'+('zero' if v%4==0 else 'nonzero');classes.setdefault(key,[]).append(v)
    result=dict(status='ZERO_MASK_INVARIANT_AND_DIFFERENT_CHART_AMBIGUITY',artificial_only=True,native_data_read=False,source_alphabet=list(SOURCE),initial_label='o',cipher=cipher,equality_mask=[int(d==0) for d in ds[0]],source_classes=classes,equal_chart_positions=common_size,records=records,scope='Two different charts, not two readings under one fixed chart; neither chart is fitted to native data or offered as a manuscript decoder.')
    (P/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    (P/'artifacts/RUN_RECEIPT.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),lock_sha256=hashlib.sha256((P/'src/REGISTRATION_LOCK.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps({'status':result['status'],'positions':common_size,'cipher':cipher,'messages':MESSAGES,'class_sizes':{k:len(v) for k,v in classes.items()}}))
if __name__=='__main__':
    if '--controls' in sys.argv:
        out=controls();(P/'artifacts/CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
    else:main()
