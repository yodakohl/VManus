from pathlib import Path
from collections import defaultdict,Counter
import csv,gzip,hashlib,itertools,json,re,subprocess
import z3
B=Path(__file__).resolve().parents[1];R=B.parents[2]
PAT=re.compile('ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def cross(word):
    for i,j,k,l in itertools.combinations(range(len(word)),4):
        if word[i]==word[k] and word[j]==word[l] and word[i]!=word[j]:return (i,j,k,l)
    return None
def close(words,alphabet):
    groups=[{a} for a in alphabet]
    while True:
        labels={a:i for i,g in enumerate(groups) for a in g};hit=None
        for word in words:
            values=[labels[a] for a in word];witness=cross(values)
            if witness:
                i,j,_,_=witness;hit=(values[i],values[j]);break
        if hit is None:return sorted(sorted(g) for g in groups)
        a,b=sorted(hit);groups[a]|=groups[b];del groups[b]
def circ(word):
    for c in set(word):
        if sum(word[i]==c and word[(i+1)%len(word)]!=c for i in range(len(word)))>1:return False
    return True
def partitions(n):
    def rec(labels):
        if len(labels)==n:yield tuple(labels);return
        for v in range(max(labels,default=-1)+2):yield from rec(labels+[v])
    yield from rec([0])
def main():
    lock=read(B/'src/REGISTRATION_LOCK.json')
    for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    source=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');results=read(B/'artifacts/RESULT.json')['panels'];allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
    binary=R/'.cache/gdt1349_verify_cuts';subprocess.run(['g++','-O2','-std=c++17',str(B/'src/verify_cuts.cpp'),'-o',str(binary)],check=True,capture_output=True)
    merge_checks=0;parsed_groups=0;panel_receipts={}
    for reader,rr in source.items():
        words={};leaves=defaultdict(set)
        for r in rr:
            assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ['f1r','f116v'];assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE' and r['kind']=='P'
            tokens=PAT.findall(r['ivtff_group_raw']);assert ''.join(tokens)==r['ivtff_group_raw'] and tokens==r['units'];words[r['id']]=tuple(tokens);leaves[tuple(tokens)].add(re.match(r'f\d+',r['page'])[0]);parsed_groups+=1
        for name,rows in [('FULL',rr),('PHYSICAL_LEAVES_GE2',[r for r in rr if len(leaves[words[r['id']]])>=2])]:
            key=reader+'_'+name;result=results[key];n=result['nested'];alphabet=sorted({u for r in rows for u in words[r['id']]});assert len(alphabet)==22
            unique=sorted({words[r['id']] for r in rows});assert result['groups']==len(rows) and result['types']==len(unique)
            independent=close(unique,alphabet);assert independent==n['classes'] and len(independent)==n['maximum_classes']
            # Replay every ORIGINALnecessary merger with its source witness.
            current=[{a} for a in alphabet];panelids={r['id']:r for r in rows}
            for step in n['certificate']:
                row=step['witness'];assert row==panelids[row['id']];labels={a:i for i,cs in enumerate(current) for a in cs};w=words[row['id']];i,j,k,l=step['positions'];assert i<j<k<l<len(w)
                a,b=labels[w[i]],labels[w[j]];assert a!=b and labels[w[k]]==a and labels[w[l]]==b
                assert sorted(step['merged_classes'])==sorted([sorted(current[a]),sorted(current[b])])
                lo,hi=sorted([a,b]);current[lo]|=current[hi];del current[hi];merge_checks+=1
            assert sorted(sorted(g) for g in current)==independent
            label={u:i for i,cs in enumerate(independent) for u in cs};coded={w:tuple(label[u] for u in w) for w in unique};assert all(cross(w) is None for w in coded.values())
            multi=sum(len(set(coded[words[r['id']]]))>1 for r in rows);assert multi==n['multi_class_groups_upper_bound']
            maxused=max(len(set(v)) for v in coded.values());assert maxused==n['max_classes_used_in_word_under_finest']
            nesting=0;depthmax=0
            for r in rows:
                w=coded[words[r['id']]];intervals={a:(w.index(a),len(w)-1-w[::-1].index(a)) for a in set(w)}
                depths=[1+sum(x<i and j<y for other,(x,y) in intervals.items() if other!=a) for a,(i,j) in intervals.items()];depth=max(depths);depthmax=max(depthmax,depth);nesting+=depth>1
            assert nesting==n['groups_nested_under_finest'] and depthmax==n['max_depth_under_finest']
            for entry in n['activity']:
                cs=set(entry['units']);touch=[r for r in rows if cs&set(r['units'])]
                assert entry['unit_tokens']==sum(sum(r['units'].count(a) for a in cs) for r in rows)
                assert entry['groups']==len(touch) and entry['physical_leaves']==len({re.match(r'f\d+',r['page'])[0] for r in touch})
            if name=='PHYSICAL_LEAVES_GE2':
                old={u:({'q':1,'n':2,'m':3}.get(u,0)) for u in alphabet};assert all(circ(tuple(old[u] for u in w)) and cross(tuple(old[u] for u in w)) is None for w in unique)
            circular=result['circular'];receipt={'nested_max':len(independent),'nested_proof':'PASS'}
            if circular['status']=='UNKNOWN_ENUMERATION_TIMEOUT':panel_receipts[key]=receipt;continue
            k=len(independent);ww=sorted(set(coded.values()));payload=f'{k} {len(ww)}\n'+'\n'.join(str(len(w))+' '+' '.join(map(str,w)) for w in ww)+'\n'
            actual=json.loads(subprocess.run([str(binary)],input=payload,text=True,capture_output=True,check=True,timeout=60).stdout);assert actual==circular['valid_cuts'] and circular['checked_cuts']==2**(k-1)-1
            full=2**k-1;allowed=sorted({full,*actual,*(full^m for m in actual)});capacity=circular['capacity'];parts=capacity['partition_masks'];assert all(p in allowed for p in parts)
            union=0
            for p in parts:assert not union&p;union|=p
            assert union==full
            actualclasses=[[u for i,cs in enumerate(independent) if p>>i&1 for u in cs] for p in parts];assert actualclasses==circular['witness_classes']
            mp={u:i for i,cs in enumerate(actualclasses) for u in cs};assert all(circ(tuple(mp[u] for u in w)) for w in unique)
            if capacity['status']=='EXACT':
                maximum=capacity['maximum_classes'];assert maximum==len(parts)
                if maximum==k:proof='atom_count_upper_bound'
                else:
                    sol=z3.Solver();sol.set(timeout=30000);take=[z3.Bool('take_'+str(i)) for i in range(len(allowed))]
                    for i in range(k):sol.add(z3.Sum([z3.If(t,1,0) for t,mask in zip(take,allowed) if mask>>i&1])==1)
                    sol.add(z3.Sum([z3.If(t,1,0) for t in take])>=maximum+1);answer=sol.check();assert answer==z3.unsat,('independent maximum unresolved',key,str(answer));proof='independent_exact_cover_UNSAT_for_one_more_class'
                receipt.update(circular_max=maximum,circular_upper_certificate=proof)
            else:assert capacity['lower']==len(parts)==2 and capacity['upper']==k;receipt.update(circular_bounds=[2,k])
            assert capacity['allowed_subset_count']==len(allowed)
            assert circular['activity_complete']==(len(actual)<=4096)
            if circular['activity_complete']:
                assert [x['mask'] for x in circular['cut_activity']]==actual
                for entry in circular['cut_activity']:
                    mask=entry['mask'];left={u for i,cs in enumerate(independent) if mask>>i&1 for u in cs};counts=Counter()
                    for row in rows:
                        seq=row['units'];a=sum(u in left for u in seq);counts['tokens']+=a;counts['selected']+=a>0;counts['complement']+=a<len(seq);counts['mixed']+=0<a<len(seq)
                    assert (entry['mixed_groups'],entry['selected_unit_tokens'],entry['selected_groups'],entry['complement_groups'])==(counts['mixed'],counts['tokens'],counts['selected'],counts['complement'])
                assert circular['max_binary_mixed_groups']==max((r['mixed_groups'] for r in circular['cut_activity']),default=0)
            receipt['valid_cuts']=len(actual);panel_receipts[key]=receipt
    # Source-free exhaustive class partitions for all3-unit strings throughlength6.
    fixture_count=0;ps=list(partitions(3))
    for length in range(1,7):
        for w in itertools.product(range(3),repeat=length):
            valid=[p for p in ps if cross(tuple(p[a] for a in w)) is None]
            closed=close([w],list(range(3)));assert len(closed)==max(len(set(p)) for p in valid)
            circular=[p for p in ps if circ(tuple(p[a] for a in w))]
            assert all(p in valid for p in circular)
            mapping={u:i for i,cs in enumerate(closed) for u in cs}
            for p in valid:assert all(p[a]==p[b] for cs in closed for a in cs for b in cs)
            fixture_count+=1
    assert cross(tuple('ABA')) is None and cross(tuple('ABACA')) is None and cross(tuple('ABAB')) is not None
    assert not circ(tuple('ABACA')) and circ(tuple('ABA'))
    assert cross(tuple('ABCB')) is None and cross(tuple('ABAB')) is not None
    out={'status':'PASS','source_groups_reparsed':parsed_groups,'necessary_merge_steps':merge_checks,'source_free_word_fixtures':fixture_count,'panels':panel_receipts,'scope':'Exact conditional field capacities; no native alphabet, historical field values, phonetic classes or semantic confirmation.'}
    (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
