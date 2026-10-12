from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
import gzip,hashlib,itertools,json,random,re
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2];N=8192

def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def frac(x):return [x.numerator,x.denominator]
def save(name,obj):
    payload=json.dumps(obj,indent=2,sort_keys=True).encode()+b'\n'
    (B/'artifacts'/name).write_bytes(gzip.compress(payload,mtime=0) if name.endswith('.gz') else payload)
def load_sources():
    types=dict(line.split() for line in (B/'source/cmudict.phones').read_text().splitlines() if line.strip())
    assert len(types)==39 and sum(v=='vowel' for v in types.values())==15
    order=sorted(types,key=lambda p:digest('1347opaque|'+p));index={p:i for i,p in enumerate(order)}
    raw=defaultdict(set);counts=Counter()
    for line in (B/'source/cmudict.dict').read_text().splitlines():
        line=line.split('#',1)[0].strip()
        if not line or line.startswith(';;;'):continue
        fields=line.split();base=re.sub(r'\(\d+\)$','',fields[0]);counts['dictionary_entries']+=1
        if not re.fullmatch('[a-z]+',base):counts['nonletter_entries']+=1;continue
        phones=[]
        for token in fields[1:]:
            phone=re.sub('[012]$','',token);assert phone in types,(base,token)
            if token!=phone:assert types[phone]=='vowel'
            phones.append(phone)
        assert phones;raw[base].add(tuple(phones))
    groups=defaultdict(list)
    for base,forms in raw.items():
        if len(forms)!=1:counts['ambiguous_bases']+=1;continue
        seq=next(iter(forms))
        if len(seq)<5:counts['short_unambiguous_bases']+=1;continue
        groups[seq].append(base)
    candidates={'train':[],'test':[]}
    for seq,bases in groups.items():
        h=digest('1347split|'+' '.join(seq));side='train' if int(h[:2],16)<128 else 'test'
        candidates[side].append({'key':h,'seq':[index[p] for p in seq],'bases':sorted(bases)})
    for side in candidates:
        candidates[side].sort(key=lambda r:r['key']);counts[side+'_available_sequences']=len(candidates[side]);assert len(candidates[side])>=N,'STOP_NO_CAPACITY'
        candidates[side]=candidates[side][:N]
    counts['eligible_unique_sequences']=len(groups);counts['dictionary_letter_bases']=len(raw)
    return {'splits':candidates,'truth':{str(index[p]):int(types[p]=='vowel') for p in types},'symbols':order,'scope':'dictionary pronunciation, equal unique-sequence weights'},dict(counts)
def procedural(mode):
    rng=random.Random(1347001 if mode=='STRICT' else 1347002)
    order=sorted(range(39),key=lambda i:digest('1347procopaque|'+str(i)));index={p:i for i,p in enumerate(order)}
    rows=[];seen=set()
    while len(rows)<2*N:
        fields=[]
        for _ in range(3):
            for role in (0,1):
                length=1 if mode=='STRICT' else rng.randint(1,2)
                fields.append([rng.randrange(24) if role==0 else 24+rng.randrange(15) for j in range(length)])
        flat=sum(fields,[]);key=tuple(flat)
        if key in seen:continue
        seen.add(key);rows.append({'key':digest('1347proc|'+','.join(map(str,flat))),'seq':[index[i] for i in flat],'fields':fields})
    return {'splits':{'train':rows[:N],'test':rows[N:]},'truth':{str(index[i]):int(i>=24) for i in order},'symbols':order,'scope':'three reversible address/value assignments, no pronunciation'}
def shuffled(cmu):
    splits={}
    for side,rows in cmu['splits'].items():
        out=[]
        for r in rows:
            seed=int(digest('1347shuffle|'+' '.join(cmu['symbols'][i] for i in r['seq'])),16)
            seq=r['seq'][:];random.Random(seed).shuffle(seq);out.append({'key':r['key'],'seq':seq})
        splits[side]=out
    return {'splits':splits,'truth':cmu['truth'],'symbols':cmu['symbols'],'scope':'CMU word bags with destroyed within-record order'}
def cut_weights(records):
    words=Counter(tuple(r['seq'][1:-1]) for r in records);active=sorted(set().union(*(set(w) for w in words)))
    obs=Counter();exp=defaultdict(Fraction)
    for w,f in words.items():
        c=Counter(w)
        for a,b in zip(w,w[1:]):
            if a!=b:obs[tuple(sorted((a,b)))]+=f
        for a,b in itertools.combinations(sorted(c),2):exp[a,b]+=Fraction(2*f*c[a]*c[b],len(w))
    edges=[];mat=np.zeros((len(active),len(active)),dtype=np.int64);ix={v:i for i,v in enumerate(active)}
    for a,b in itertools.combinations(active,2):
        w=Fraction(obs[a,b])-exp[a,b];q=round(w*1000000);mat[ix[a],ix[b]]=mat[ix[b],ix[a]]=q
        edges.append({'a':a,'b':b,'observed':obs[a,b],'expected':frac(exp[a,b]),'exact':frac(w),'quantized':q})
    assert int(np.abs(mat).sum())<2**60
    return active,mat,edges
def optimize(mat):
    n=len(mat);starts=[]
    for start in range(64):
        bits=np.array([0]+[int(digest(f'1347start|{start}|{i}'),16)&1 for i in range(1,n)],dtype=np.int64)
        if not bits.any():bits[1]=1
        steps=0;hit=False
        while steps<500:
            signs=1-2*bits;deltas=signs*(mat@signs);eligible=[i for i in range(1,n) if 0<int(bits.sum())+(1 if bits[i]==0 else -1)<n]
            j=min(eligible,key=lambda i:(-int(deltas[i]),i)) if eligible else None
            if j is None or deltas[j]<=0:break
            bits[j]=1-bits[j];steps+=1
        if steps==500:hit=True
        score=sum(int(mat[i,j]) for i in range(n) for j in range(i+1,n) if bits[i]!=bits[j]);mask=sum(int(v)<<i for i,v in enumerate(bits))
        starts.append({'start':start,'score':score,'mask':mask,'steps':steps,'limit':hit})
    best=min(starts,key=lambda x:(-x['score'],x['mask']));labels=[(best['mask']>>i)&1 for i in range(n)]
    return labels,{'starts':starts,'best_score':best['score'],'best_mask':best['mask'],'best_start':best['start'],'any_limit':any(s['limit'] for s in starts),'global_optimality':'NOT_CLAIMED'}
def evaluate(corpus,active,labels,opt,mat):
    label=dict(zip(active,labels));truth={int(k):v for k,v in corpus['truth'].items()}
    bytruth={c:[u for u in active if truth[u]==c] for c in (0,1)};assert all(bytruth.values())
    bal=sum((Fraction(sum(label[u]==c for u in us),len(us)) for c,us in bytruth.items()),Fraction(0))/2
    invert=bal<Fraction(1,2);balanced=1-bal if invert else bal;pred={u:v^int(invert) for u,v in label.items()}
    token_total=token_correct=record_count_correct=unknown=unknown_records=exact_profile=0;blocks=[]
    test=corpus['splits']['test'];events=[]
    for b in range(32):
        excess=Fraction(0);edges=valid=unscorable=0
        for r in test[b*256:(b+1)*256]:
            seq=r['seq'];token_total+=len(seq);token_correct+=sum(u in pred and pred[u]==truth[u] for u in seq)
            missing=sum(u not in pred for u in seq);unknown+=missing;unknown_records+=bool(missing)
            gold=sum(truth[u] for u in seq);estimate=None if missing else sum(pred[u] for u in seq)
            record_count_correct+=estimate is not None and estimate==gold;exact_profile+=not missing and all(pred[u]==truth[u] for u in seq)
            inner=seq[1:-1]
            if any(u not in label for u in inner):unscorable+=1;continue
            bits=[label[u] for u in inner];n=len(bits);ones=sum(bits);cross=sum(a!=b for a,b in zip(bits,bits[1:]));ex=Fraction(cross)-Fraction(2*ones*(n-ones),n)
            excess+=ex;edges+=n-1;valid+=1
            events.append({'key':r['key'],'block':b,'gold_count':gold,'predicted_count':estimate,'inner_excess':frac(ex),'inner_edges':n-1})
        effect=excess/edges if edges else Fraction(0);blocks.append({'block':b,'valid':valid,'unscorable':unscorable,'excess':frac(excess),'edges':edges,'effect':frac(effect)})
    mean=sum((Fraction(*b['effect']) for b in blocks),Fraction(0))/32;positive=sum(Fraction(*b['effect'])>0 for b in blocks)
    tok=Fraction(token_correct,token_total);count=Fraction(record_count_correct,N)
    transfer=mean>=Fraction(3,100) and positive>=22 and all(b['valid']==256 for b in blocks) and unknown==0
    sensitivity=balanced>=Fraction(9,10) and tok>=Fraction(95,100) and count>=Fraction(85,100) and not opt['any_limit'] and unknown==0
    goldscore=sum(int(mat[i,j]) for i in range(len(active)) for j in range(i+1,len(active)) if truth[active[i]]!=truth[active[j]])
    return {'oriented_prediction':{str(k):v for k,v in pred.items()},'training_orientation_inverted':bool(invert),'balanced_type_accuracy':frac(balanced),'test_tokens':token_total,'test_correct_tokens':token_correct,'token_accuracy':frac(tok),'test_correct_counts':record_count_correct,'count_accuracy':frac(count),'test_exact_profiles':exact_profile,'unknown_test_tokens':unknown,'unknown_test_records':unknown_records,'class_recovery_gate':bool(sensitivity),'known_label_training_score':goldscore,'learned_minus_known_label_score':opt['best_score']-goldscore,'blocks':blocks,'mean_excess':frac(mean),'positive_blocks':positive,'structural_transfer_gate':bool(transfer)},events
def main():
    for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    cmu,account=load_sources();packet={'CMU':cmu,'PROCEDURAL_STRICT':procedural('STRICT'),'PROCEDURAL_VARIABLE':procedural('VARIABLE'),'SHUFFLED':shuffled(cmu)}
    save('PACKET.json.gz',packet);save('SOURCE_ACCOUNT.json',account);results={};events={}
    for name,corpus in packet.items():
        active,mat,edges=cut_weights(corpus['splits']['train']);labels,opt=optimize(mat);evaluation,ev=evaluate(corpus,active,labels,opt,mat)
        results[name]={'active_ids':active,'labels':labels,'weights':edges,'optimizer':opt,'evaluation':evaluation};events[name]=ev
    save('RESULT.json',results);save('TEST_EVENTS.json.gz',events)
    print(json.dumps({name:{'active_units':len(r['active_ids']),'balanced_type_accuracy':float(Fraction(*r['evaluation']['balanced_type_accuracy'])),'token_accuracy':float(Fraction(*r['evaluation']['token_accuracy'])),'count_accuracy':float(Fraction(*r['evaluation']['count_accuracy'])),'class_recovery_gate':r['evaluation']['class_recovery_gate'],'mean_excess':float(Fraction(*r['evaluation']['mean_excess'])),'positive_blocks':r['evaluation']['positive_blocks'],'structural_gate':r['evaluation']['structural_transfer_gate'],'learned_minus_known_score':r['evaluation']['learned_minus_known_label_score'],'optimizer_limit':r['optimizer']['any_limit']} for name,r in results.items()},indent=2))
if __name__=='__main__':main()
