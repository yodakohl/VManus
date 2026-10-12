from pathlib import Path
from collections import defaultdict
from fractions import Fraction
import gzip,hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
    v=p.read_bytes();return json.loads(gzip.decompress(v) if p.suffix=='.gz' else v)
def q(bits):
    observed=sum(bits[i]!=bits[i+1] for i in range(len(bits)-1));expected=Fraction(sum(a!=b for a in bits for b in bits),len(bits));return Fraction(observed)-expected

def main():
    for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    corpus=read(R/'experiments/yolo/gdt1347_phoneme_role_calibration/artifacts/PACKET.json.gz')['CMU'];result=read(B/'artifacts/RESULT.json');events=read(B/'artifacts/EVENTS.json.gz');expected_order=sorted(itertools.product(range(39),range(2)),key=lambda x:hashlib.sha256(('1351opaque|%d|%d'%x).encode()).hexdigest());code={t:i for i,t in enumerate(expected_order)};book=result['codebook'];truth={int(k):v for k,v in corpus['truth'].items()};assert len(book)==78
    for i,(u,p) in enumerate(expected_order):assert book[i]=={'code':i,'phone_id':u,'phase':p,'inherited_class':truth[u]}
    pos=0;score_checks=0;graph_checks=0
    for split,rows in corpus['splits'].items():
        tables=defaultdict(lambda:defaultdict(list));edgecounts=defaultdict(list);graphs=defaultdict(lambda:defaultdict(set))
        for row in rows:
            w=row['seq'];assert len(w)>=5;event=events[pos];pos+=1;assert event['key']==row['key'] and event['split']==split and event['source_phone_length']==len(w)
            rendered=[code[u,p] for u in w for p in (0,1)];assert [book[rendered[i]]['phone_id'] for i in range(0,len(rendered),2)]==w
            for i in range(0,len(rendered),2):assert book[rendered[i]]['phase']==0 and book[rendered[i+1]]['phase']==1 and book[rendered[i]]['phone_id']==book[rendered[i+1]]['phone_id']
            arms={'ATOMIC':w[1:-1],'RENDER_THEN_TRIM':rendered[1:-1],'TRIM_THEN_RENDER':rendered[2:-2]}
            for arm,seq in arms.items():
                bits=[truth[u] for u in seq] if arm=='ATOMIC' else [book[u]['inherited_class'] for u in seq];channels={'inherited':bits}
                if arm!='ATOMIC':channels['phase']=[book[u]['phase'] for u in seq]
                edgecounts[arm].append(len(seq)-1)
                for channel,bb in channels.items():
                    r=event['arms'][arm][channel];value=q(bb);assert r=={'length':len(bb),'ones':sum(bb),'switches':sum(a!=b for a,b in zip(bb,bb[1:])),'score':[value.numerator,value.denominator]};score_checks+=1;tables[arm][channel].append(value)
                if arm!='ATOMIC':
                    assert tables[arm]['inherited'][-1]<=0 and tables[arm]['phase'][-1]==Fraction(len(seq),2)-1>0
                    margin=tables[arm]['phase'][-1]-tables[arm]['inherited'][-1];assert margin==Fraction(*event['arms'][arm]['margin'])
                    for a,b in zip(seq,seq[1:]):graphs[arm][a].add(b);graphs[arm][b].add(a);assert book[a]['phase']!=book[b]['phase']
        for arm,channels in tables.items():
            r=result['panels'][split][arm];assert r['records']==len(rows)==8192
            for channel,values in channels.items():
                blocks=[sum(values[i:i+256],Fraction(0))/sum(edgecounts[arm][i:i+256]) for i in range(0,8192,256)];stored=r[channel]
                for field,value in [('sum',sum(values,Fraction(0))),('min',min(values)),('max',max(values)),('mean_block_per_edge',sum(blocks,Fraction(0))/32)]:assert Fraction(*stored[field])==value
                assert [Fraction(*x) for x in stored['block_per_edge']]==blocks and stored['positive_blocks']==sum(v>0 for v in blocks)
            if arm!='ATOMIC':
                margins=[a-b for a,b in zip(channels['phase'],channels['inherited'])];assert Fraction(*r['minimum_margin'])==min(margins) and Fraction(*r['total_margin'])==sum(margins,Fraction(0))
                graph=graphs[arm];seen=set();cc=[]
                for start in sorted(graph):
                    if start in seen:continue
                    group={start};front=[start]
                    while front:
                        u=front.pop()
                        for v in graph[u]:
                            if v not in group:group.add(v);front.append(v)
                    seen|=group;cc.append(sorted(group))
                assert cc==r['components'] and len(seen)==r['active_units'];assert len(cc)==r['component_count'] and r['unique_up_to_swap']==(len(cc)==1) and r['optimal_assignments_on_active_units']==2**len(cc)
                gap=min(1-Fraction(2,e+1) for e in edgecounts[arm]);bound=Fraction(len(seen)*(len(seen)-1),4000000);assert gap==Fraction(*r['exact_nonoptimal_cut_gap_lower_bound']) and bound==Fraction(*r['aggregate_pair_rounding_difference_bound']) and gap>bound and r['rounding_cannot_change_optimum'];graph_checks+=1
    assert pos==len(events)==result['complete_word_inverse_checks']==16384
    fixtures=0
    for n in range(2,15,2):
        upper=Fraction(n,2)-1
        for bits in itertools.product([0,1],repeat=n):
            value=q(bits);assert value<=upper;alternating=all(a!=b for a,b in zip(bits,bits[1:]))
            if n>2:
                assert (value==upper)==alternating
                if not alternating:assert upper-value>=1-Fraction(2,n)
            fixtures+=1
    inherited_fixtures=0
    for n in range(3,9):
        for bits in itertools.product([0,1],repeat=n):
            rendered=[b for b in bits for _ in range(2)]
            for seq in [rendered[1:-1],rendered[2:-2]]:
                assert q(seq)<=0;inherited_fixtures+=1
    reference=read(R/'experiments/yolo/gdt1347_phoneme_role_calibration/artifacts/RESULT.json')['CMU']['evaluation']['mean_excess'];assert result['panels']['test']['ATOMIC']['inherited']['mean_block_per_edge']==reference
    assert result['status']=='PAIRED_PHONE_CLASSES_STRICTLY_SUBOPTIMAL__PHASE_GLOBAL_OPTIMUM'
    out={'status':'PASS','word_inverses':pos,'source_score_checks':score_checks,'graph_checks':graph_checks,'exhaustive_binary_words':fixtures,'inherited_rendering_fixtures':inherited_fixtures,'scope':'Exact paired control identity, arithmetic and extremal fixtures; no native glyph or phonetic binding.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
