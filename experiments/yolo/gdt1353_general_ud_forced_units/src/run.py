from pathlib import Path
from collections import defaultdict,Counter
from functools import lru_cache
import csv,gzip,hashlib,json,re,time
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SRC='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(p,o):
    raw=(json.dumps(o,indent=2,sort_keys=True)+'\n').encode();p.write_bytes(gzip.compress(raw,mtime=0) if p.suffix=='.gz' else raw)
def leaf(r):return int(re.match(r'f(\d+)',r['page'])[1])
def closure(occ):
    nodes=[{'units':[],'round':0,'kind':'EMPTY'}];index={():0};start=time.monotonic();rounds=0;complete=False
    for w in sorted(occ):
        index[w]=len(nodes);rr=occ[w];nodes.append({'units':list(w),'round':0,'kind':'WHOLE','source':{'count':len(rr),'physical_leaves':sorted({leaf(r) for r in rr}),'first_row':rr[0]}})
    while True:
        if time.monotonic()-start>30:break
        left={};right={}
        for w in sorted(index):
            for j in range(len(w)+1):
                x,y=w[:j],w[j:]
                if x in index and y:left.setdefault(y,(index[x],index[w]))
                y,z=w[:j],w[j:]
                if z in index and y:right.setdefault(y,(index[w],index[z]))
        add=sorted((left.keys()&right.keys())-index.keys())
        if not add:complete=True;break
        if len(nodes)+len(add)>200000:break
        rounds+=1
        for y in add:index[y]=len(nodes);nodes.append({'units':list(y),'round':rounds,'kind':'QUOTIENT','parents':[*left[y],*right[y]]})
    return nodes,index,rounds,complete

def block_parse(w,h,direction):
    seq=w if direction=='PREFIX' else w[::-1];parts=[];i=0
    while i<len(seq):
        j=i
        while j<len(seq) and seq[j]==h:j+=1
        assert j<len(seq)
        parts.append(seq[i:j+1]);i=j+1
    return parts if direction=='PREFIX' else [p[::-1] for p in parts[::-1]]
def main():
    for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    data=read(R/SRC);allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};result={}
    for reader,rows in sorted(data.items()):
        original=defaultdict(list)
        for row in rows:
            assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert ''.join(row['units'])==row['ivtff_group_raw'];original[tuple(row['units'])].append(row)
        alphabet=sorted({u for w in original for u in w});assert len(alphabet)==22
        for label in ['FULL','GE2']:
            occ={w:rr for w,rr in original.items() if label=='FULL' or len({leaf(r) for r in rr})>=2};nodes,index,rounds,complete=closure(occ);forced=[h for h in alphabet if (h,) in index];counter={};unresolved=[]
            for h in alphabet:
                if h in forced:continue
                if all(w[-1]!=h for w in occ):direction='PREFIX'
                elif all(w[0]!=h for w in occ):direction='SUFFIX'
                else:unresolved.append(h);continue
                uses=Counter();active=0
                for w,rr in occ.items():
                    parts=block_parse(w,h,direction);assert sum(parts,())==w;active+=len(rr)*any(len(p)>1 for p in parts)
                    for p in parts:uses[p]+=len(rr)
                codes=sorted(uses);assert (h,) not in uses and all((u,) in uses for u in forced)
                counter[h]={'direction':direction,'used_codes':[{'units':list(c),'uses':uses[c]} for c in codes],'entry_count':len(codes),'compound_active_groups':active,'omits_singleton':h}
            @lru_cache(None)
            def roots(i):
                n=nodes[i]
                if n['kind']=='EMPTY':return frozenset()
                if n['kind']=='WHOLE':return frozenset([i])
                return frozenset().union(*(roots(j) for j in n['parents']))
            support={h:[{'units':nodes[j]['units'],'count':nodes[j]['source']['count'],'physical_leaves':nodes[j]['source']['physical_leaves'],'first_id':nodes[j]['source']['first_row']['id']} for j in sorted(roots(index[(h,)]))] for h in forced}
            fixed=[w for w in occ if set(w)<=set(forced)];key=reader+'_'+label;certificate={'reader':reader,'panel':label,'nodes':nodes,'countercodes':counter};save(B/f'artifacts/CERTIFICATE_{key}.json.gz',certificate)
            out={'groups':sum(map(len,occ.values())),'types':len(occ),'active_units':sorted({u for w in occ for u in w}),'closure_complete':complete,'closure_nodes':len(nodes),'closure_rounds':rounds,'forced_singletons':forced,'certified_not_forced':sorted(counter),'unresolved':unresolved,'status':'EXACT_SINGLETON_INTERSECTION' if complete and not unresolved else 'PARTIAL_SINGLETON_CLASSIFICATION','fully_forced_groups':sum(len(occ[w]) for w in fixed),'fully_forced_types':len(fixed),'proof_support':support,'countercode_summary':{h:{k:v for k,v in c.items() if k!='used_codes'} for h,c in counter.items()}}
            result[key]=out;print(json.dumps({k:v for k,v in out.items() if k not in ['proof_support','countercode_summary','active_units']}|{'panel':key}),flush=True)
    save(B/'artifacts/RESULT.json',{'status':'CONDITIONAL_FREE_UD_SINGLETON_CLASSIFICATION','panels':result,'scope':'Fixed nonempty freelyUD whole-word code on22working units, no table-size cap. No actual sounds, meanings, alphabet or joint omission claim.'})
if __name__=='__main__':main()
