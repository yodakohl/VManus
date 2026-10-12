from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
import gzip,hashlib,json,math,random,itertools
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def metrics(table,links):
    groups=defaultdict(list)
    for u,c in table.items():groups[c].append(u)
    balanced=sum((Fraction(sum(table[u]==table[links[u]] for u in us),len(us)) for us in groups.values()),Fraction(0))/len(groups)
    acc=Fraction(sum(table[u]==table[v] for u,v in links.items()),len(links));return balanced,acc

def main():
    for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    packet=read(R/'experiments/yolo/gdt1347_phoneme_role_calibration/artifacts/PACKET.json.gz');typ=dict(x.split() for x in (R/'experiments/yolo/gdt1347_phoneme_role_calibration/source/cmudict.phones').read_text().splitlines() if x.strip());result=read(B/'artifacts/RESULT.json');scores={};events=0;distance_checks=0
    for name,corpus in packet.items():
        obs=result['corpora'][name];target=sorted(int(u) for u,c in corpus['truth'].items() if c==0);assert len(target)==24
        if name in ['CMU','SHUFFLED']:labels={u:typ[corpus['symbols'][u]] for u in target}
        else:
            order=sorted(target,key=lambda u:hashlib.sha256(('1350procedural|'+str(u)).encode()).hexdigest());cats=[typ[k] for k in sorted(typ) if typ[k]!='vowel'];labels=dict(zip(order,cats))
        assert sorted(Counter(labels.values()).values())==[1,2,2,2,3,6,8]
        profiles={};mass={}
        for side in ['train','test']:
            count=defaultdict(Counter)
            for row in corpus['splits'][side]:
                seq=row['seq']
                for prev,cur,nxt in zip(seq,seq[1:],seq[2:]):count[cur,0][prev]+=1;count[cur,1][nxt]+=1;events+=1
            mass[side]={u:sum(count[u,0].values()) for u in target};profiles[side]={}
            for u in range(39):
                profiles[side][u]=[]
                for d in range(2):
                    raw=[count[u,d][v] for v in range(39)];assert raw==obs['counts'][side][u][d]
                    den=2*sum(raw)+39;values=[(2*n+1)/den for n in raw];assert abs(sum(values)-1)<1e-12
                    assert all(abs(a-b)<1e-14 for a,b in zip(values,obs['profiles'][side][u][d]));profiles[side][u].append(values)
        links={};details={r['target']:r for r in obs['targets']};assert set(details)==set(target)
        for u in target:
            candidates=[]
            for v in target:
                if v==u:continue
                distance=math.fsum((math.sqrt(a)-math.sqrt(b))**2 for x,y in zip(profiles['test'][u],profiles['train'][v]) for a,b in zip(x,y));assert abs(distance-obs['distances'][str(u)][str(v)])<1e-12;candidates.append((distance,v));distance_checks+=1
            _,v=min(candidates);links[u]=v;r=details[u];assert r['neighbor']==v and r['true_category']==labels[u] and r['predicted_category']==labels[v];assert r['train_occurrences']==mass['train'][u] and r['test_occurrences']==mass['test'][u];assert r['symbol']==corpus['symbols'][u] and r['neighbor_symbol']==corpus['symbols'][v]
        macro,acc=metrics(labels,links);assert macro==Fraction(*obs['macro_accuracy']) and acc==Fraction(*obs['type_accuracy'])
        for c,n in Counter(labels.values()).items():assert obs['by_category'][c]=={'correct':sum(labels[u]==c and labels[v]==c for u,v in links.items()),'total':n}
        extreme=1
        for i,reported in enumerate(obs['permutation_macros']):
            cats=[labels[u] for u in target];seed=int(hashlib.sha256(f'1350perm|{name}|{i}'.encode()).hexdigest(),16);random.Random(seed).shuffle(cats);m,_=metrics(dict(zip(target,cats)),links);assert m==Fraction(*reported);extreme+=m>=macro
        assert len(obs['permutation_macros'])==4096 and Fraction(extreme,4097)==Fraction(*obs['permutation_tail'])
        capacity=all(mass[s][u]>=20 for s in mass for u in target);assert capacity==obs['capacity'];scores[name]=(macro,acc,Fraction(extreme,4097),capacity)
        if name=='CMU':hh=next(u for u in target if corpus['symbols'][u]=='HH');assert labels[links[hh]]!='aspirate' and obs['by_category']['aspirate']['correct']==0
    m,a,p,_=scores['CMU'];checks={'capacity':all(v[3] for v in scores.values()),'macro_at_least_point4':m>=Fraction(2,5),'type_at_least_half':a>=Fraction(1,2),'permutation_at_most_point01':p<=Fraction(1,100),'all_control_gaps_at_least_point15':all(m-v[0]>=Fraction(3,20) for k,v in scores.items() if k!='CMU')};assert checks==result['gate_checks'];assert result['status']==('MANNER_TRANSFER_FIXED_CONTROL_PASS' if all(checks.values()) else 'MANNER_TRANSFER_JOINT_GATE_FAIL')
    assert metrics({0:'a',1:'a',2:'a'},{0:1,1:2,2:0})==(1,1)
    assert metrics({0:'a',1:'a',2:'b'},{0:1,1:2,2:0})==(Fraction(1,4),Fraction(1,3))
    assert min((0.0,v) for v in [0,1,2] if v!=0)==(0.0,1)
    assert sum(Fraction(1,39) for _ in range(39))==1
    cycle=[metrics(dict(enumerate(t)),{0:1,1:2,2:0})[0] for t in itertools.permutations(['a','a','b'])]
    assert len(cycle)==6 and all(v==Fraction(1,4) for v in cycle)
    out={'status':'PASS','independent_count_events':events,'distance_checks':distance_checks,'permutation_checks':4*4096,'toy_checks':5,'scope':'Source/count/math verification only; no Voynich access, linguistic unit confirmation or independent general phonetic-origin test.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
