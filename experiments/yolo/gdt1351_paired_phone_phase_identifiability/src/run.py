from pathlib import Path
from collections import defaultdict
from fractions import Fraction
import gzip,hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SRC='experiments/yolo/gdt1347_phoneme_role_calibration/artifacts/PACKET.json.gz'
def f(x):return [x.numerator,x.denominator]
def score(bits):
    n=len(bits);ones=sum(bits);s=sum(a!=b for a,b in zip(bits,bits[1:]));return {'length':n,'ones':ones,'switches':s,'score':f(Fraction(s)-Fraction(2*ones*(n-ones),n))}
def stats(rows,field):
    values=[Fraction(*r[field]['score']) for r in rows];blocks=[]
    for i in range(32):
        rr=rows[256*i:256*(i+1)];blocks.append(sum((Fraction(*r[field]['score']) for r in rr),Fraction(0))/sum(r[field]['length']-1 for r in rr))
    return {'sum':f(sum(values,Fraction(0))),'min':f(min(values)),'max':f(max(values)),'mean_block_per_edge':f(sum(blocks,Fraction(0))/32),'positive_blocks':sum(v>0 for v in blocks),'block_per_edge':[f(v) for v in blocks]}
def components(graph):
    pending=set(graph);out=[]
    while pending:
        todo=[min(pending)];seen=set()
        while todo:
            u=todo.pop()
            if u in seen:continue
            seen.add(u);todo.extend(graph[u]-seen)
        pending-=seen;out.append(sorted(seen))
    return out
def main():
    for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    c=json.loads(gzip.decompress((R/SRC).read_bytes()))['CMU'];truth={int(k):v for k,v in c['truth'].items()};pairs=sorted(((u,p) for u in range(39) for p in (0,1)),key=lambda x:hashlib.sha256(f'1351opaque|{x[0]}|{x[1]}'.encode()).hexdigest());codes={pair:i for i,pair in enumerate(pairs)};book=[{'code':i,'phone_id':u,'phase':p,'inherited_class':truth[u]} for i,(u,p) in enumerate(pairs)]
    events=[];panels={};inverse_count=0
    for split,rows in c['splits'].items():
        out=defaultdict(list);graphs={a:defaultdict(set) for a in ['RENDER_THEN_TRIM','TRIM_THEN_RENDER']}
        for row in rows:
            w=row['seq'];n=len(w);assert n>=5;render=[codes[u,p] for u in w for p in (0,1)]
            inverse=[]
            for i in range(0,len(render),2):
                u,p=pairs[render[i]];v,q=pairs[render[i+1]];assert u==v and (p,q)==(0,1);inverse.append(u)
            assert inverse==w;inverse_count+=1
            arms={'ATOMIC':{'inherited':score([truth[u] for u in w[1:-1]])}}
            for arm,seq in [('RENDER_THEN_TRIM',render[1:-1]),('TRIM_THEN_RENDER',[codes[u,p] for u in w[1:-1] for p in (0,1)])]:
                inherited=score([truth[pairs[v][0]] for v in seq]);phase=score([pairs[v][1] for v in seq]);assert Fraction(*inherited['score'])<=0;assert Fraction(*phase['score'])==Fraction(len(seq),2)-1>0
                arms[arm]={'inherited':inherited,'phase':phase,'margin':f(Fraction(*phase['score'])-Fraction(*inherited['score']))}
                for a,b in zip(seq,seq[1:]):graphs[arm][a].add(b);graphs[arm][b].add(a)
            for arm,data in arms.items():out[arm].append(data)
            events.append({'key':row['key'],'split':split,'source_phone_length':n,'arms':arms})
        panels[split]={}
        for arm,rr in out.items():
            result={'records':len(rr),'inherited':stats(rr,'inherited')}
            if arm!='ATOMIC':
                cc=components(graphs[arm]);margins=[Fraction(*r['margin']) for r in rr];active=len(graphs[arm]);gap=min(Fraction(1)-Fraction(2,r['phase']['length']) for r in rr);bound=Fraction(active*(active-1)//2,2000000)
                assert bound<gap
                result.update(phase=stats(rr,'phase'),minimum_margin=f(min(margins)),total_margin=f(sum(margins,Fraction(0))),active_units=active,components=cc,component_count=len(cc),optimal_assignments_on_active_units=2**len(cc),unique_up_to_swap=len(cc)==1,exact_nonoptimal_cut_gap_lower_bound=f(gap),aggregate_pair_rounding_difference_bound=f(bound),rounding_cannot_change_optimum=True)
            panels[split][arm]=result
    parent=json.loads((R/'experiments/yolo/gdt1347_phoneme_role_calibration/artifacts/RESULT.json').read_text());assert panels['test']['ATOMIC']['inherited']['mean_block_per_edge']==parent['CMU']['evaluation']['mean_excess']
    result={'status':'PAIRED_PHONE_CLASSES_STRICTLY_SUBOPTIMAL__PHASE_GLOBAL_OPTIMUM','codebook':book,'panels':panels,'complete_word_inverse_checks':inverse_count,'scope':'Constructed78sign reversible control only; no native units, phonetic origin exclusion, sound key or word meaning.'}
    (B/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');(B/'artifacts/EVENTS.json.gz').write_bytes(gzip.compress((json.dumps(events,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0))
    print(json.dumps({'status':result['status'],'panels':{s:{a:{k:v for k,v in r.items() if k not in ['inherited','phase','components']}|{'inherited_score_sum':r['inherited']['sum'],'phase_score_sum':r.get('phase',{}).get('sum')} for a,r in aa.items()} for s,aa in panels.items()}},indent=2))
if __name__=='__main__':main()
