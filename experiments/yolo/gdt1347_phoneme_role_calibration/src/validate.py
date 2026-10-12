from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
import gzip,hashlib,itertools,json,random,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];N=8192

def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def read(name):
    data=(B/'artifacts'/name).read_bytes();return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)
def switch(word,labels):
    values=[labels[u] for u in word];n=len(values);a=sum(values)
    return Fraction(sum(x!=y for x,y in zip(values,values[1:])))-Fraction(2*a*(n-a),n)
def cut(mask,active,weights):return sum(v for (a,b),v in weights.items() if ((mask>>active.index(a))^(mask>>active.index(b)))&1)
def main():
    for path,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
    packet=read('PACKET.json.gz');results=read('RESULT.json');events=read('TEST_EVENTS.json.gz')
    meta={a:b for a,b in (line.split() for line in (B/'source/cmudict.phones').read_text().splitlines())};order=sorted(meta,key=lambda p:sha('1347opaque|'+p));idx={p:i for i,p in enumerate(order)}
    variants=defaultdict(set);account=Counter()
    for line in (B/'source/cmudict.dict').read_text().splitlines():
        line=line.partition('#')[0].strip()
        if not line or line.startswith(';;;'):continue
        fields=line.split();base=fields[0];account['dictionary_entries']+=1
        if base.endswith(')') and '(' in base:
            stem,number=base.rsplit('(',1)
            if number[:-1].isdigit():base=stem
        if not base or not all('a'<=c<='z' for c in base):account['nonletter_entries']+=1;continue
        seq=[]
        for token in fields[1:]:
            core=token[:-1] if token[-1] in '012' else token;assert core in meta
            if core!=token:assert meta[core]=='vowel'
            seq.append(core)
        variants[base].add(tuple(seq))
    grouped=defaultdict(list)
    for base,forms in variants.items():
        if len(forms)>1:account['ambiguous_bases']+=1
        elif len(next(iter(forms)))<5:account['short_unambiguous_bases']+=1
        else:grouped[next(iter(forms))].append(base)
    buckets={'train':[],'test':[]}
    for seq,bases in grouped.items():
        h=sha('1347split|'+' '.join(seq));side='train' if int(h[0:2],16)<128 else 'test';buckets[side].append({'key':h,'seq':[idx[p] for p in seq],'bases':sorted(bases)})
    for side in buckets:
        buckets[side].sort(key=lambda r:r['key']);account[side+'_available_sequences']=len(buckets[side]);assert packet['CMU']['splits'][side]==buckets[side][:N]
    account['eligible_unique_sequences']=len(grouped);account['dictionary_letter_bases']=len(variants);assert dict(account)==read('SOURCE_ACCOUNT.json')
    assert packet['CMU']['symbols']==order and packet['CMU']['truth']=={str(i):int(meta[p]=='vowel') for i,p in enumerate(order)}
    trainkeys={tuple(r['seq']) for r in packet['CMU']['splits']['train']};testkeys={tuple(r['seq']) for r in packet['CMU']['splits']['test']};assert not trainkeys&testkeys
    bases=[{b for r in packet['CMU']['splits'][side] for b in r['bases']} for side in ['train','test']];assert not bases[0]&bases[1]
    controls=0
    for name in ['PROCEDURAL_STRICT','PROCEDURAL_VARIABLE']:
        corpus=packet[name];symbols=corpus['symbols'];assert symbols==sorted(range(39),key=lambda i:sha('1347procopaque|'+str(i)))
        assert corpus['truth']=={str(i):int(u>=24) for i,u in enumerate(symbols)}
        seqs=set()
        for side in ['train','test']:
            assert len(corpus['splits'][side])==N
            for row in corpus['splits'][side]:
                seq=row['seq'];assert tuple(seq) not in seqs;seqs.add(tuple(seq));original=[symbols[u] for u in seq]
                runs=[]
                for role,g in itertools.groupby(original,key=lambda i:int(i>=24)):runs.append((role,list(g)))
                assert [role for role,_ in runs]==[0,1]*3 and [xs for _,xs in runs]==row['fields']
                assert all(len(xs)==1 if name.endswith('STRICT') else len(xs) in (1,2) for _,xs in runs)
                assert row['key']==sha('1347proc|'+','.join(map(str,original)))
                if name.endswith('STRICT'):assert switch(seq[1:-1],{int(k):v for k,v in corpus['truth'].items()})==1
                controls+=1
    assert packet['SHUFFLED']['symbols']==order and packet['SHUFFLED']['truth']==packet['CMU']['truth']
    for side in ['train','test']:
        for original,mixed in zip(packet['CMU']['splits'][side],packet['SHUFFLED']['splits'][side]):
            seq=original['seq'][:];random.Random(int(sha('1347shuffle|'+' '.join(order[i] for i in seq)),16)).shuffle(seq)
            assert mixed=={'key':original['key'],'seq':seq}
    scorechecks=0;eventchecks=0
    for name,corpus in packet.items():
        r=results[name];active=r['active_ids'];assert active==sorted({u for row in corpus['splits']['train'] for u in row['seq'][1:-1]})
        words=Counter(tuple(row['seq'][1:-1]) for row in corpus['splits']['train']);observed=Counter();denoms=defaultdict(Counter)
        for word,f in words.items():
            for i in range(1,len(word)):
                a,b=sorted([word[i-1],word[i]])
                if a!=b:observed[a,b]+=f
            counts=Counter(word)
            for a,b in itertools.combinations(sorted(counts),2):denoms[a,b][len(word)]+=2*f*counts[a]*counts[b]
        weights={}
        for entry in r['weights']:
            pair=(entry['a'],entry['b']);expected=sum((Fraction(v,n) for n,v in denoms[pair].items()),Fraction(0));exact=observed[pair]-expected
            assert entry['observed']==observed[pair] and Fraction(*entry['expected'])==expected and Fraction(*entry['exact'])==exact and entry['quantized']==round(exact*1000000)
            weights[pair]=entry['quantized']
        assert len(weights)==len(active)*(len(active)-1)//2
        opt=r['optimizer'];assert len(opt['starts'])==64
        for start in opt['starts']:
            mask=start['mask'];assert 0<mask<2**len(active) and mask&1==0
            score=cut(mask,active,weights);assert score==start['score']
            assert 0<=start['steps']<=500 and start['limit']==(start['steps']==500)
            if not start['limit']:
                for j in range(1,len(active)):
                    altered=mask^(1<<j)
                    if altered:assert cut(altered,active,weights)<=score
            scorechecks+=1
        best=min(opt['starts'],key=lambda x:(-x['score'],x['mask']));assert (best['score'],best['mask'],best['start'])==(opt['best_score'],opt['best_mask'],opt['best_start']);assert opt['any_limit']==any(s['limit'] for s in opt['starts'])
        labels={u:(best['mask']>>i)&1 for i,u in enumerate(active)};assert r['labels']==[labels[u] for u in active]
        truth={int(k):v for k,v in corpus['truth'].items()};rawacc=sum((Fraction(sum(labels[u]==c for u in active if truth[u]==c),sum(truth[u]==c for u in active)) for c in (0,1)),Fraction(0))/2
        flip=rawacc<Fraction(1,2);pred={u:v^int(flip) for u,v in labels.items()};ev=r['evaluation'];assert ev['training_orientation_inverted']==flip and ev['oriented_prediction']=={str(k):v for k,v in pred.items()}
        bal=max(rawacc,1-rawacc);assert Fraction(*ev['balanced_type_accuracy'])==bal
        totals=Counter();blocks=[];expected_events=[]
        for block in range(32):
            excess=Fraction(0);edges=valid=missing_inner=0
            for row in corpus['splits']['test'][block*256:(block+1)*256]:
                seq=row['seq'];missing=sum(u not in labels for u in seq);gold=sum(truth[u] for u in seq);guess=None if missing else sum(pred[u] for u in seq)
                totals['tokens']+=len(seq);totals['correct']+=sum(u in pred and pred[u]==truth[u] for u in seq);totals['unknown']+=missing;totals['unknown_records']+=bool(missing);totals['counts']+=guess is not None and guess==gold;totals['exact']+=not missing and all(pred[u]==truth[u] for u in seq)
                inner=seq[1:-1]
                if not all(u in labels for u in inner):missing_inner+=1;continue
                x=switch(inner,labels);excess+=x;edges+=len(inner)-1;valid+=1
                expected_events.append({'key':row['key'],'block':block,'gold_count':gold,'predicted_count':guess,'inner_excess':[x.numerator,x.denominator],'inner_edges':len(inner)-1});eventchecks+=1
            effect=excess/edges if edges else Fraction(0);blocks.append({'block':block,'valid':valid,'unscorable':missing_inner,'excess':[excess.numerator,excess.denominator],'edges':edges,'effect':[effect.numerator,effect.denominator]})
        assert blocks==ev['blocks'] and expected_events==events[name]
        assert (totals['tokens'],totals['correct'],totals['counts'],totals['unknown'],totals['unknown_records'],totals['exact'])==(ev['test_tokens'],ev['test_correct_tokens'],ev['test_correct_counts'],ev['unknown_test_tokens'],ev['unknown_test_records'],ev['test_exact_profiles'])
        ta=Fraction(totals['correct'],totals['tokens']);ca=Fraction(totals['counts'],N);assert Fraction(*ev['token_accuracy'])==ta and Fraction(*ev['count_accuracy'])==ca
        mean=sum((Fraction(*b['effect']) for b in blocks),Fraction(0))/32;positive=sum(Fraction(*b['effect'])>0 for b in blocks)
        assert Fraction(*ev['mean_excess'])==mean and ev['positive_blocks']==positive
        assert ev['structural_transfer_gate']==(mean>=Fraction(3,100) and positive>=22 and all(b['valid']==256 for b in blocks) and totals['unknown']==0)
        assert ev['class_recovery_gate']==(bal>=Fraction(9,10) and ta>=Fraction(95,100) and ca>=Fraction(85,100) and not opt['any_limit'] and totals['unknown']==0)
        goldscore=sum(v for (a,b),v in weights.items() if truth[a]!=truth[b]);assert ev['known_label_training_score']==goldscore and ev['learned_minus_known_label_score']==opt['best_score']-goldscore
    fixtures=0
    for n in range(2,7):
        for count in range(n+1):
            perms=set(itertools.permutations([0]*count+[1]*(n-count)));assert sum((switch(w,{0:0,1:1}) for w in perms),Fraction(0))==0;fixtures+=1
    out={'status':'PASS','cmu_train_sequences':N,'cmu_test_sequences':N,'procedural_roundtrips':controls,'checked_optimizer_final_states':scorechecks,'test_event_checks':eventchecks,'bag_fixtures':fixtures,'scope':'Source reconstruction, fixed splits, control inverse, integer final scores/local optima and all held metrics; no global optimization, syllable boundaries or Voynich sound evidence.'}
    (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
