from pathlib import Path
from collections import Counter
from fractions import Fraction
import gzip,hashlib,json,random
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2]
P='experiments/yolo/gdt1347_phoneme_role_calibration/artifacts/PACKET.json.gz'
T='experiments/yolo/gdt1347_phoneme_role_calibration/source/cmudict.phones'
def h(s):return hashlib.sha256(s.encode()).hexdigest()
def frac(x):return [x.numerator,x.denominator]
def score(labels,neighbors):
    sizes=Counter(labels.values());correct=Counter(labels[u] for u,v in neighbors.items() if labels[u]==labels[v])
    macro=sum((Fraction(correct[c],sizes[c]) for c in sizes),Fraction(0))/len(sizes)
    return macro,Fraction(sum(correct.values()),len(labels)),{c:{'correct':correct[c],'total':sizes[c]} for c in sorted(sizes)}
def main():
    for p,d in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==d,p
    corpora=json.loads(gzip.decompress((R/P).read_bytes()));types=dict(line.split() for line in (R/T).read_text().splitlines() if line.strip());taxonomy=[types[p] for p in sorted(types) if types[p]!='vowel'];assert len(taxonomy)==24
    results={}
    for name,c in corpora.items():
        targets=sorted(int(k) for k,v in c['truth'].items() if v==0);assert len(targets)==24
        if name in ('CMU','SHUFFLED'):labels={u:types[c['symbols'][u]] for u in targets}
        else:labels=dict(zip(sorted(targets,key=lambda u:h('1350procedural|'+str(u))),taxonomy))
        counts={};profiles={}
        for side,rows in c['splits'].items():
            a=np.zeros((39,2,39),dtype=np.int64)
            for row in rows:
                w=row['seq']
                for i in range(1,len(w)-1):a[w[i],0,w[i-1]]+=1;a[w[i],1,w[i+1]]+=1
            counts[side]=a;sm=a.astype(float)+.5;profiles[side]=sm/sm.sum(axis=2,keepdims=True)
        distances={};neighbors={};details=[]
        for u in targets:
            dd={v:float(np.square(np.sqrt(profiles['test'][u])-np.sqrt(profiles['train'][v])).sum()) for v in targets if v!=u}
            v=min(dd,key=lambda v:(dd[v],v));neighbors[u]=v;distances[str(u)]={str(k):val for k,val in dd.items()}
            details.append({'target':u,'symbol':c['symbols'][u],'true_category':labels[u],'neighbor':v,'neighbor_symbol':c['symbols'][v],'predicted_category':labels[v],'train_occurrences':int(counts['train'][u,0].sum()),'test_occurrences':int(counts['test'][u,0].sum())})
        macro,accuracy,byclass=score(labels,neighbors);permuted=[]
        for i in range(4096):
            ll=[labels[u] for u in targets];random.Random(int(h('1350perm|'+name+'|'+str(i)),16)).shuffle(ll);m,a,_=score(dict(zip(targets,ll)),neighbors);permuted.append(frac(m))
        tail=Fraction(1+sum(Fraction(*p)>=macro for p in permuted),4097)
        results[name]={'capacity':all(d['train_occurrences']>=20 and d['test_occurrences']>=20 for d in details),'macro_accuracy':frac(macro),'type_accuracy':frac(accuracy),'by_category':byclass,'permutation_tail':frac(tail),'permutation_macros':permuted,'targets':details,'distances':distances,'counts':{s:a.tolist() for s,a in counts.items()},'profiles':{s:a.tolist() for s,a in profiles.items()}}
    cmu=results['CMU'];m=Fraction(*cmu['macro_accuracy']);checks={'capacity':all(r['capacity'] for r in results.values()),'macro_at_least_point4':m>=Fraction(2,5),'type_at_least_half':Fraction(*cmu['type_accuracy'])>=Fraction(1,2),'permutation_at_most_point01':Fraction(*cmu['permutation_tail'])<=Fraction(1,100),'all_control_gaps_at_least_point15':all(m-Fraction(*r['macro_accuracy'])>=Fraction(3,20) for name,r in results.items() if name!='CMU')}
    out={'status':'MANNER_TRANSFER_FIXED_CONTROL_PASS' if all(checks.values()) else 'MANNER_TRANSFER_JOINT_GATE_FAIL','gate_checks':checks,'corpora':results,'scope':'Known phone context-to-category transfer with supplied prototype labels; no native units, sounds, meaning or general phonetic-origin proof.'}
    (B/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'gate_checks':checks,'scores':{k:{f:v[f] for f in ['macro_accuracy','type_accuracy','permutation_tail','capacity']} for k,v in results.items()}},indent=2))
if __name__=='__main__':main()
