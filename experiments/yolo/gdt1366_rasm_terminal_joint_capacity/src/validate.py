"""Independent GE2 joint-terminal constraint validator; no primary imports."""
from pathlib import Path
from collections import Counter
import gzip,json,re,hashlib
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
OLD=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'

def offsets(word,candidates):
    return [i for i,ch in enumerate(word) if ch in candidates]

def controls():
    candidates=set('XYZ');checked=0
    for word in ('','A','X','AB','ABX','AABY','CCZ'):
        for ordered in (word,word[::-1]):
            for a in range(len(ordered)+1):
                for b in range(a,len(ordered)+1):
                    assert len(offsets(ordered[a:b],candidates))<=1;checked+=1
    assert offsets('XX',candidates)==[0,1]
    assert offsets('XAY',candidates)==[0,2]
    assert offsets('X',candidates)==[0]
    assert offsets('ABC',candidates)==[]
    return {'split_and_reversal_substrings':checked,'repeated_terminal_counted_twice':True,'distinct_terminals_counted_twice':True,'singleton_not_violation':True}

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
    packet=json.loads(gzip.decompress((OLD/'artifacts/GROUPS.json.gz').read_bytes()));out={}
    for edition,rows in packet.items():
        support={};parsed={};seen=set()
        for row in rows:
            assert row['edition']==edition and row['page'] in allowed and row['kind']=='P'
            assert row['page'] not in ('f116v','f1r') and not row['page'].startswith('f84')
            assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            assert row['locus'].split('.')[0]==row['page']
            ident=f"{edition}|{row['locus']}|G{int(row['source_group_index']):03d}"
            assert row['id']==ident and ident not in seen;seen.add(ident)
            raw=row['ivtff_group_raw'];assert raw and all('a'<=c<='z' for c in raw)
            if raw not in parsed:parsed[raw]=parse(raw,signs)
            assert list(parsed[raw])==row['units']
            m=re.fullmatch(r'f(\d+)[rv]\d*',row['page']);assert m
            support.setdefault(raw,set()).add(int(m.group(1)))
        selected=[row for row in rows if len(support[row['ivtff_group_raw']])>=2]
        allchars=set();middle=set();leaves=set()
        for row in selected:
            word=row['ivtff_group_raw'];allchars.update(word);middle.update(word[1:-1]);leaves.add(int(re.match(r'f(\d+)',row['page']).group(1)))
        if len(allchars)!=18 or len(middle)!=15:
            raise AssertionError('UNAPPLICABLE: fixed18/15premises absent; no replacement terminal set selected')
        candidates=allchars-middle;assert len(candidates)==3
        witnesses=[];patterns=Counter();formcounts=Counter();badleaves=set()
        for row in selected:
            raw=row['ivtff_group_raw'];indices=offsets(raw,candidates)
            if len(indices)>1:
                witnesses.append({'source':row,'offsets':indices,'count':len(indices)})
                patterns[''.join(raw[i] for i in indices)]+=1;formcounts[raw]+=1
                badleaves.add(int(re.match(r'f(\d+)',row['page']).group(1)))
        out[edition]={'groups':len(selected),'types':len({r['ivtff_group_raw'] for r in selected}),'leaves':len(leaves),'alphabet':sorted(allchars),'middle':sorted(middle),'terminal_candidates':sorted(candidates),'violating_groups':len(witnesses),'violating_types':len(formcounts),'violating_leaves':len(badleaves),'violation_rate':len(witnesses)/len(selected),'patterns':dict(sorted(patterns.items())),'top_forms':[{'form':form,'occurrences':count} for form,count in sorted(formcounts.items(),key=lambda p:(-p[1],p[0]))[:10]],'witnesses':witnesses,'decision':'EXCLUDED' if witnesses else 'CAPACITY_ONLY'}
    return out

def main():
    lock=json.loads((D/'src/REGISTRATION_LOCK.json').read_text())
    for path,digest in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    fixtures=controls();expected=compute()
    result=json.loads((D/'artifacts/RESULT.json').read_text())
    assert result['status']=='JOINT_TERMINAL_CAPACITY'
    assert result['panels']==expected
    report={'status':'PASS','controls':fixtures,'panels':len(expected),'comparisons':'Every derived field, all full source rows and raw offsets, descriptive totals/rates/patterns/topforms and decisions match independently.','independence':'No primary imports or output read before source freeze. Source/unit/ID/boundary checks, GE2leaf selection and direct multiplicity census reconstructed.','scope':'Restricted18model only; no20classextension, meanings, trueglyphs, source-language identification or independentholdout.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
