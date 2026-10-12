from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,json,re,itertools,sys
import z3
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def cycles(w):
    dp=[()]
    for j in range(1,len(w)):
        choices=[dp[-1]]
        for i in range(j):
            if w[i]==w[j] and len(set(w[i:j+1]))>1:choices.append(dp[i]+((i,j),))
        dp.append(min(choices,key=lambda a:(-len(a),a)))
    return dp[-1]
def passes(w,r):return 1+sum(r[a]>r[b] for a,b in zip(w,w[1:]))
def controls():
    n=0
    for size in range(1,7):
        for w in itertools.product('abc',repeat=size):
            c=cycles(w)
            for order in itertools.permutations('abc'):
                r={a:i for i,a in enumerate(order)};p=passes(w,r)
                # Exhaust all cut subsets to check minimum monotone partition independently.
                good=[]
                for mask in range(1<<(size-1)):
                    starts=[0]+[i+1 for i in range(size-1) if mask>>i&1]+[size]
                    if all(all(r[w[j]]<=r[w[j+1]] for j in range(a,b-1)) for a,b in zip(starts,starts[1:])):good.append(len(starts)-1)
                assert p==min(good) and 1+len(c)<=p
                m=sum(a!=b for a,b in zip(w,w[1:]));assert p+passes(w[::-1],r)==2+m
                n+=1
    # Across arbitrary collections the aggregated pair bound is sound.
    words=list(itertools.product('abc',repeat=3));collections=0
    for ws in itertools.combinations(words,3):
        edges=Counter(e for w in ws for e in zip(w,w[1:]) if e[0]!=e[1]);s=sum(min(edges[a,b],edges[b,a]) for a,b in itertools.combinations('abc',2))
        for order in itertools.permutations('abc'):
            r={a:i for i,a in enumerate(order)};assert 1+(s+2)//3<=max(passes(w,r) for w in ws)
        collections+=1
    out={'status':'PASS','word_order_cases':n,'three_type_collections':collections,'source_free':True};save(B/'artifacts/CONTROLS.json',out);print(out)
def main():
    for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels={}
    for reader,rows in sorted(data.items()):
        original=defaultdict(list)
        for row in rows:
            assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',row['ivtff_group_raw'])==row['units'];assert ''.join(row['units'])==row['ivtff_group_raw'];original[tuple(row['units'])].append(row)
        for panel in ['FULL','GE2']:
            occ={w:rr for w,rr in sorted(original.items()) if panel=='FULL' or len({int(re.match(r'f(\d+)',r['page'])[1]) for r in rr})>=2};alpha=sorted({u for w in occ for u in w});assert len(alpha)==22
            def support(w):
                rr=occ[w];return {'word':list(w),'count':len(rr),'physical_leaves':sorted({int(re.match(r'f(\d+)',r['page'])[1]) for r in rr}),'first_row':rr[0]}
            cw=min(occ,key=lambda w:(-len(cycles(w)),w));cc=cycles(cw);rev=[w for w in occ if w[::-1] in occ];rw=min(rev,key=lambda w:(-(1+(sum(a!=b for a,b in zip(w,w[1:]))+1)//2),w)) if rev else None
            edges=Counter(e for w in occ for e in zip(w,w[1:]) if e[0]!=e[1]);s=sum(min(edges[a,b],edges[b,a]) for a,b in itertools.combinations(alpha,2));T=len(occ)
            bounds={'cycle':{'lower':1+len(cc),'intervals':[list(x) for x in cc],**support(cw)},'reverse':({'lower':1+(sum(a!=b for a,b in zip(rw,rw[1:]))+1)//2,**support(rw),'reverse_support':support(rw[::-1])} if rw else {'lower':1}), 'aggregate':{'lower':1+(s+T-1)//T,'sum_min_edges':s,'type_count':T,'edges':[[a,b,n] for (a,b),n in sorted(edges.items())]}}
            L=max(x['lower'] for x in bounds.values());rank=alpha;rr={a:i for i,a in enumerate(rank)};U=max(passes(w,rr) for w in occ);attempts=[]
            for K in range(L,L+3):
                if K>=U:continue
                solver=z3.Solver();solver.set(timeout=10000,random_seed=0);variables={a:z3.Int('r_'+a) for a in alpha};solver.add(z3.Distinct(list(variables.values())));solver.add(*[z3.And(v>=0,v<22) for v in variables.values()])
                for w in occ:
                    ec=Counter((a,b) for a,b in zip(w,w[1:]) if a!=b)
                    if sum(ec.values())>K-1:solver.add(z3.Sum([n*z3.If(variables[a]>variables[b],1,0) for (a,b),n in ec.items()])<=K-1)
                ans=solver.check();attempts.append({'K':K,'answer':str(ans)})
                if ans==z3.sat:
                    model=solver.model();rank=sorted(alpha,key=lambda a:model[variables[a]].as_long());rr={a:i for i,a in enumerate(rank)};U=max(passes(w,rr) for w in occ);assert U<=K;break
            ht=Counter(passes(w,rr) for w in occ);hn=Counter()
            for w,rs in occ.items():hn[passes(w,rr)]+=len(rs)
            mw=min(w for w in occ if passes(w,rr)==U);starts=[0]+[j+1 for j,(a,b) in enumerate(zip(mw,mw[1:])) if rr[a]>rr[b]]+[len(mw)];segments=[list(mw[a:b]) for a,b in zip(starts,starts[1:])]
            out={'groups':sum(map(len,occ.values())),'types':T,'L':L,'U':U,'exact':L==U,'rank':rank,'bounds':bounds,'attempts':attempts,'hist_type':dict(sorted(ht.items())),'hist_token':dict(sorted(hn.items())),'max_word':{**support(mw),'segments':segments}}
            panels[reader+'_'+panel]=out;print(reader,panel,L,U,rank,'max',mw,flush=True)
    save(B/'artifacts/RESULT.json',{'status':'CERTIFIED_ORDERED_PASS_INTERVALS','panels':panels,'solver_version':z3.get_version_string(),'claim_ceiling':'Strict global rank on supplied working units and wholegroups only; no phonetic values or original pass boundaries.'})
if __name__=='__main__':controls() if '--controls' in sys.argv else main()
