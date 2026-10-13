"""Independent RAW_CHAR position census, no primary imports."""
from pathlib import Path
from collections import Counter
import gzip,json,re
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
OLD=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'

def parse(raw,signs):
    ways={0:[()]}
    for i in range(len(raw)):
        for before in ways.get(i,[]):
            for s in signs:
                if raw.startswith(s,i):ways.setdefault(i+len(s),[]).append(before+(s,))
    assert len(ways.get(len(raw),[]))==1
    return ways[len(raw)][0]

def census(rows,alphabet=None):
    if alphabet is None:alphabet=sorted(set(''.join(row['ivtff_group_raw'] for row in rows)))
    modes=('nonfinal','noninitial','middle')
    chars={c:{**{m+'_count':0 for m in modes},**{m+'_first':None for m in modes},'char':c} for c in alphabet}
    active=set()
    for row in rows:
        raw=row['ivtff_group_raw'];active.update(raw)
        for i,c in enumerate(raw):
            qualifies={'nonfinal':i<len(raw)-1,'noninitial':i>0,'middle':0<i<len(raw)-1}
            for mode,condition in qualifies.items():
                if condition:
                    chars[c][mode+'_count']+=1
                    if chars[c][mode+'_first'] is None:chars[c][mode+'_first']={'source':row,'offset_zero_based':i}
    counts={'all':len(active),**{m:sum(bool(v[m+'_count']) for v in chars.values()) for m in modes}}
    models={}
    for name,total,internal in [('restricted18',18,15),('full20',20,17)]:
        models[name]={direction:('EXCLUDED' if counts['all']>total or counts[mode]>internal else 'CAPACITY_ONLY') for direction,mode in [('forward','nonfinal'),('reverse','noninitial'),('mixed_direction','middle')]}
    return {'groups':len(rows),'types':len({r['ivtff_group_raw'] for r in rows}),'alphabet':alphabet,'characters':[chars[c] for c in alphabet],'counts':counts,'models':models}

def controls():
    rows=[{'ivtff_group_raw':raw,'page':'f2r','id':str(i)} for i,raw in enumerate(('a','ab','baa','ccc'))]
    r=census(rows);by={e['char']:e for e in r['characters']}
    assert by['a']['nonfinal_count']==2 and by['a']['noninitial_count']==2 and by['a']['middle_count']==1
    assert by['b']['nonfinal_count']==1 and by['b']['noninitial_count']==1 and by['b']['middle_count']==0
    assert by['c']['nonfinal_count']==2 and by['c']['noninitial_count']==2 and by['c']['middle_count']==1
    assert by['c']['middle_first']['offset_zero_based']==1
    assert r['counts']=={'all':3,'nonfinal':3,'noninitial':3,'middle':2}
    return {'synthetic_position_cases':4,'singleton_has_no_nonfinal_noninitial_middle':True,'strict_middle_excludes_both_ends':True,'multiple_events_pergroup':True}

def compute():
    spec=json.loads((OLD/'src/SPEC.json').read_text());signs=spec['signs']
    allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed'];assert len(allowed)==179
    packet=json.loads(gzip.decompress((OLD/'artifacts/GROUPS.json.gz').read_bytes()));panels={}
    for ed,rows in packet.items():
        parsed={};leaves={};seen=set()
        for row in rows:
            assert row['edition']==ed and row['page'] in allowed and row['kind']=='P'
            assert row['page'] not in ('f1r','f116v') and not row['page'].startswith('f84')
            assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            assert row['locus'].split('.')[0]==row['page']
            ident=f"{ed}|{row['locus']}|G{int(row['source_group_index']):03d}";assert ident==row['id'] and ident not in seen;seen.add(ident)
            raw=row['ivtff_group_raw'];assert raw and all('a'<=c<='z' for c in raw)
            if raw not in parsed:parsed[raw]=parse(raw,signs)
            assert list(parsed[raw])==row['units']
            leaf=int(re.match(r'f(\d+)[rv]\d*$',row['page']).group(1));leaves.setdefault(raw,set()).add(leaf)
        for panel in ('FULL','GE2'):
            selected=[r for r in rows if panel=='FULL' or len(leaves[r['ivtff_group_raw']])>=2]
            panels[ed+'_'+panel]=census(selected,sorted(set(''.join(r['ivtff_group_raw'] for r in rows))))
    return panels

def compare(primary,expected):
    assert primary['status']=='RASM_RENDERING_CAPACITY_ENUMERATED'
    assert set(primary['panels'])==set(expected)
    for key,wanted in expected.items():
        observed=primary['panels'][key]
        for field in ('groups','types','alphabet','counts','models'):
            assert observed[field]==wanted[field],(key,field)
        assert observed['characters']==wanted['characters'],key

def main():
    fixture=controls();expected=compute();primary=json.loads((D/'artifacts/RESULT.json').read_text());compare(primary,expected)
    out={'status':'PASS','independence':'Direct position-event census, source reparse, no primary imports.','controls':fixture,'panels':len(expected),'limits':'No source letter values, historical orthography, actual rasm identity or native phonology validated.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
