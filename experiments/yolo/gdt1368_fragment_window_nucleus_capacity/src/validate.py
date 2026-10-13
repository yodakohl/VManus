"""Independent true-consecutive window reconstruction and bitset hitting proof."""
from pathlib import Path
from itertools import combinations,product
import gzip,json,re,hashlib
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
OLD=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'

def windows_from_rows(rows):
    lines={}
    for row in rows:
        key=(row['page'],row['locus']);i=int(row['source_group_index'])
        line=lines.setdefault(key,{})
        assert i not in line;line[i]=row
    windows=[]
    for key in sorted(lines):
        line=lines[key]
        for start in sorted(line):
            if all(start+j in line for j in range(3)):
                source=[line[start+j] for j in range(3)]
                windows.append({'sources':source,'support':sorted(set(''.join(r['ivtff_group_raw'] for r in source)))})
    return windows

def solve(supports,alphabet):
    full=(1<<len(supports))-1;bits={c:0 for c in alphabet}
    for i,support in enumerate(supports):
        for c in support:bits[c]|=1<<i
    def mask(chars):
        value=0
        for c in chars:value|=bits[c]
        return value
    tau=None;best=None;number=0
    for k in range(6):
        for chars in combinations(alphabet,k):
            if mask(chars)==full:
                number+=1
                if best is None:best=list(chars)
        if number:tau=k;break
    lower_k=5 if tau is None else tau-1
    certificate=[]
    if lower_k>=0:
        for chars in combinations(alphabet,lower_k):
            missing=full&~mask(chars);assert missing
            certificate.append({'set':list(chars),'first_missed_window':(missing&-missing).bit_length()-1})
    return {'tau_or_null':tau,'lower_bound':6 if tau is None else tau,'minimum_sets':number,'canonical_hitset':best,'decision':'K5_EXCLUDED_BY_RETAINED_WINDOWS' if tau is None else 'K5_NOT_EXCLUDED_BY_RETAINED_WINDOWS','lower_certificate':certificate}

def controls():
    def row(i,locus='f2r.1',word='a'):
        return {'page':'f2r','locus':locus,'source_group_index':str(i),'ivtff_group_raw':word}
    assert not windows_from_rows([row(1),row(3),row(4)])
    assert not windows_from_rows([row(1),row(2,'f2r.2'),row(3)])
    assert len(windows_from_rows([row(i) for i in range(1,5)]))==2
    split=windows_from_rows([row(1,word='c'),row(2,word='h'),row(3,word='a')])[0]
    assert split['support']==['a','c','h']
    s=solve([set('ab'),set('bc')],list('abc'));assert s['tau_or_null']==1 and s['canonical_hitset']==['b'] and s['minimum_sets']==1
    s=solve([set(c) for c in 'abcdef'],list('abcdef'));assert s['tau_or_null'] is None and s['lower_bound']==6 and len(s['lower_certificate'])==6
    flags=[0,1,0,0,1,0];assert all(any(flags[i:i+3]) for i in range(4))
    dp=[True]+[False]*len(flags)
    for end in range(1,len(flags)+1):dp[end]=any(dp[start] and any(flags[start:end]) for start in range(max(0,end-2),end))
    assert not dp[-1]
    theorem=0
    for n in range(1,7):
        for lengths in product((1,2),repeat=n):
            boundaries=[0]
            for length in lengths:boundaries.append(boundaries[-1]+length)
            for start in range(boundaries[-1]-2):
                assert any(start<=a and b<=start+3 for a,b in zip(boundaries,boundaries[1:]));theorem+=1
    return {'missing_index':True,'wrong_locus':True,'overlapping_windows':True,'split_working_unit_RAW_support':True,'hitting_not_sufficient_for_framed_partition':True,'B2_containment_cases':theorem,'upper_and_lower_hitting_controls':True}

def parse(raw,signs):
    ways={0:[()]}
    for i in range(len(raw)):
        for before in ways.get(i,[]):
            for sign in signs:
                if raw.startswith(sign,i):ways.setdefault(i+len(sign),[]).append(before+(sign,))
    assert len(ways.get(len(raw),[]))==1
    return ways[len(raw)][0]

def compute():
    spec=json.loads((OLD/'src/SPEC.json').read_text());signs=spec['signs']
    allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed'];assert len(allowed)==179
    data=json.loads(gzip.decompress((OLD/'artifacts/GROUPS.json.gz').read_bytes()));panels={};allwindows={}
    for edition,rows in data.items():
        seen=set();parsed={}
        for r in rows:
            assert r['edition']==edition and r['page'] in allowed and r['kind']=='P'
            assert not r['page'].startswith('f84') and r['page'] not in ('f116v','f1r')
            assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
            assert r['locus'].split('.')[0]==r['page']
            identifier=f"{edition}|{r['locus']}|G{int(r['source_group_index']):03d}"
            assert identifier==r['id'] and identifier not in seen;seen.add(identifier)
            raw=r['ivtff_group_raw'];assert raw and all('a'<=c<='z' for c in raw)
            if raw not in parsed:parsed[raw]=parse(raw,signs)
            assert list(parsed[raw])==r['units']
        windows=windows_from_rows(rows)
        if not windows:raise AssertionError('UNAPPLICABLE: zero eligible windows')
        alphabet=sorted(set(''.join(r['ivtff_group_raw'] for r in rows)))
        solved=solve([w['support'] for w in windows],alphabet)
        loci={(w['sources'][0]['page'],w['sources'][0]['locus']) for w in windows}
        leaves={int(re.fullmatch(r'f(\d+)[rv]\d*',w['sources'][0]['page']).group(1)) for w in windows}
        panels[edition]={'groups':len(rows),'windows':len(windows),'loci':len(loci),'leaves':len(leaves),'alphabet':alphabet,**solved};allwindows[edition]=windows
    return panels,allwindows

def main():
    lock=json.loads((D/'src/REGISTRATION_LOCK.json').read_text())
    for path,digest in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    fixture=controls();expected,windows=compute()
    stored=json.loads((D/'artifacts/RESULT.json').read_text());packet=json.loads(gzip.decompress((D/'artifacts/WINDOWS.json.gz').read_bytes()))
    assert stored['status']=='FRAGMENT_WINDOW_NUCLEUS_CAPACITY' and stored['panels']==expected
    assert packet==windows
    report={'status':'PASS','controls':fixture,'panels':len(expected),'independence':'Own sourcewindow reconstruction and direct percharacter bitsets/combinations; no primary imports or subsettransform. Every inputrow, orderedwindow, support, minimum tiecount, canonicaltuple, lowercertificate and firstmiss index compared.','limits':'Only retained trueconsecutive windows; a cover establishes neither fullmanuscriptcapacity nor consistent partition/carrier/nucleus/sourceinterpretation.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
