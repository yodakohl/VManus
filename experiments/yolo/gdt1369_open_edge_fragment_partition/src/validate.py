"""Independent unmatched-zero/adjacent-hit matching and exact witness replay."""
from pathlib import Path
from itertools import combinations,product
from functools import lru_cache
import gzip,json,re,hashlib
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
PREV=ROOT/'experiments/yolo/gdt1368_fragment_window_nucleus_capacity/artifacts'
OLD=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'

@lru_cache(None)
def feasible(hit):
    n=len(hit);assigned={}
    def augment(z,seen):
        options=[]
        if z==0:options.append(-1)
        if z==n-1:options.append(n)
        options.extend(j for j in (z-1,z+1) if 0<=j<n and hit[j])
        for h in options:
            if h in seen:continue
            seen.add(h)
            if h not in assigned or augment(assigned[h],seen):assigned[h]=z;return True
        return False
    return all(augment(i,set()) for i,v in enumerate(hit) if not v)

def canonical(hit):
    n=len(hit)
    for leading,trailing in ((0,0),(0,1),(1,0),(1,1)):
        start=leading;stop=n-trailing
        @lru_cache(None)
        def reconstruct(end):
            if end==start:return ()
            if end<start:return None
            if hit[end-1]:
                prefix=reconstruct(end-1)
                if prefix is not None:return prefix+((end-1,end),)
            if end-start>=2 and (hit[end-1] or hit[end-2]):
                prefix=reconstruct(end-2)
                if prefix is not None:return prefix+((end-2,end),)
            return None
        blocks=reconstruct(stop)
        if blocks is not None:return {'leading_external':leading,'trailing_external':trailing,'blocks':[list(b) for b in blocks]}
    return None

@lru_cache(None)
def compositions(n):
    if n==0:return ((),)
    return tuple((k,)+tail for k in (1,2) if k<=n for tail in compositions(n-k))

def exhaustive(hit):
    for a,b in ((0,0),(0,1),(1,0),(1,1)):
        for comp in compositions(len(hit)-a-b):
            pos=a;ok=True
            for k in comp:
                if not any(hit[pos:pos+k]):ok=False;break
                pos+=k
            if ok:return True
    return False

def controls():
    count=0
    for n in range(3,13):
        for h in product((False,True),repeat=n):
            a=feasible(h);assert a==exhaustive(h)==(canonical(h) is not None)
            if a:assert all(any(h[i:i+3]) for i in range(n-2))
            count+=1
    bad=(False,False,True,False,False)
    assert all(any(bad[i:i+3]) for i in range(3)) and not feasible(bad)
    return {'binary_patterns_lengths_3_to_12':count,'matching_equals_exhaustive_blocks_and_canonical':True,'counterexample':[0,0,1,0,0],'partition_implies_triple_hits':True}

def parse(raw,signs):
    paths={0:[()]}
    for i in range(len(raw)):
        for before in paths.get(i,[]):
            for s in signs:
                if raw.startswith(s,i):paths.setdefault(i+len(s),[]).append(before+(s,))
    assert len(paths.get(len(raw),[]))==1
    return paths[len(raw)][0]

def rebuild():
    packet=json.loads(gzip.decompress((PREV/'WINDOWS.json.gz').read_bytes()));oldresult=json.loads((PREV/'RESULT.json').read_text())
    spec=json.loads((OLD/'src/SPEC.json').read_text());signs=spec['signs'];allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed'];assert len(allowed)==179
    runs={}
    for ed,windows in packet.items():
        unique={};parsed={};lines={}
        for window in windows:
            sources=window['sources'];assert len(sources)==3
            assert window['support']==sorted(set(''.join(r['ivtff_group_raw'] for r in sources)))
            assert len({(r['page'],r['locus']) for r in sources})==1
            indices=[int(r['source_group_index']) for r in sources];assert indices==list(range(indices[0],indices[0]+3))
            for r in sources:
                assert r['edition']==ed and r['page'] in allowed and r['kind']=='P'
                assert not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v')
                assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
                assert r['locus'].split('.')[0]==r['page']
                identifier=f"{ed}|{r['locus']}|G{int(r['source_group_index']):03d}";assert identifier==r['id']
                raw=r['ivtff_group_raw'];assert raw and all('a'<=c<='z' for c in raw)
                if raw not in parsed:parsed[raw]=parse(raw,signs)
                assert list(parsed[raw])==r['units']
                if identifier in unique:assert unique[identifier]==r
                else:
                    unique[identifier]=r;key=(r['page'],r['locus']);idx=int(r['source_group_index']);line=lines.setdefault(key,{})
                    assert idx not in line;line[idx]=r
        reader=[]
        for key in sorted(lines):
            line=lines[key];current=[];previous=None
            for i in sorted(line):
                if previous is not None and i!=previous+1:
                    assert len(current)>=3;reader.append({'sources':current});current=[]
                current.append(line[i]);previous=i
            if current:assert len(current)>=3;reader.append({'sources':current})
        triples=[]
        for run in reader:
            for i in range(len(run['sources'])-2):
                rr=run['sources'][i:i+3];triples.append({'sources':rr,'support':sorted(set(''.join(r['ivtff_group_raw'] for r in rr)))})
        assert triples==windows
        runs[ed]=reader
    return packet,oldresult,runs

def compute():
    windows,old,runs=rebuild();panels={}
    for ed,reader_runs in runs.items():
        alphabet=old['panels'][ed]['alphabet'];full=(1<<len(windows[ed]))-1;bits={c:0 for c in alphabet}
        for i,w in enumerate(windows[ed]):
            for c in w['support']:bits[c]|=1<<i
        supports=[tuple(frozenset(r['ivtff_group_raw']) for r in run['sources']) for run in reader_runs]
        byk={};firstset=None;minimum=None;partitions=None
        for k in (4,5):
            candidates=[];survivors=0
            for choice in combinations(alphabet,k):
                cover=0
                for c in choice:cover|=bits[c]
                if cover!=full:continue
                chosen=frozenset(choice);failed=None
                for i,support in enumerate(supports):
                    h=tuple(bool(s&chosen) for s in support)
                    if not feasible(h):failed=i;break
                candidates.append({'set':list(choice),'first_failed_run':failed})
                if failed is None:
                    survivors+=1
                    if firstset is None:
                        firstset=list(choice);minimum=k
                        partitions=[canonical(tuple(bool(s&chosen) for s in sup)) for sup in supports]
                        assert all(p is not None for p in partitions)
            byk[str(k)]={'window_survivors':len(candidates),'partition_survivors':survivors,'candidates':candidates}
        panels[ed]={'runs':len(reader_runs),'groups':sum(len(r['sources']) for r in reader_runs),'windows':len(windows[ed]),'alphabet':alphabet,'by_k':byk,'minimum_or_null':minimum,'canonical_hitset':firstset,'canonical_partitions':partitions}
    return panels,runs

def main():
    lock=json.loads((D/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    fixtures=controls();expected,runs=compute();result=json.loads((D/'artifacts/RESULT.json').read_text())
    assert result['status']=='OPEN_EDGE_FRAGMENT_PARTITION' and result['panels']==expected
    assert json.loads(gzip.decompress((D/'artifacts/RUNS.json.gz').read_bytes()))==runs
    receipt={'status':'PASS','controls':fixtures,'panels':len(expected),'independence':'Unhit-to-neighbor-hit bipartite matching (external endhits allowed), exhaustive compositions on controls; no primary imports. All oldwindows/runs, candidates/firstfailures and deterministic edge/block witnesses reconstructed.','limits':'Only local representative-hit partitions of retainedruns; no actualcarriers, compatibleglobaloutsideassignments, realwordboundaries or language.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
