"""Independent inverse cardinality DP; no primary runner imports."""
from pathlib import Path
from itertools import product
from collections import Counter
import gzip,json,hashlib
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
OLD=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'
CAP=ROOT/'experiments/yolo/gdt1361_nasal_assimilation_capacity/artifacts/RESULT.json'

def encode(word,n,t):
    return tuple(t if x==n and i+1<len(word) and word[i+1]==t else x for i,x in enumerate(word))

def inverse_count(word,n,t):
    # State stores the ORIGINAL next source symbol, not emitted neighbor.
    states={None:1}
    for emitted in reversed(word):
        updated=Counter()
        for original in ((t,n) if emitted==t else (emitted,)):
            for following,ways in states.items():
                observed=t if original==n and following==t else original
                if observed==emitted:updated[original]+=ways
        states=updated
    return sum(states.values())

def run_formula(word,n,t):
    fib=[0,1]
    for _ in range(len(word)+2):fib.append(fib[-1]+fib[-2])
    cardinality=1;i=0
    while i<len(word):
        if word[i]!=t:i+=1;continue
        j=i
        while j<len(word) and word[j]==t:j+=1
        r=j-i
        if i>0 and word[i-1]==n:
            if r<2:return 0
            cardinality*=fib[r-1]
        else:cardinality*=fib[r+1]
        i=j
    return cardinality

def fixtures():
    total=0;outputs=0
    for length in range(9):
        words=list(product('NTX',repeat=length))
        forward=Counter(encode(w,'N','T') for w in words)
        for w in words:
            count=inverse_count(w,'N','T')
            assert count==forward[w]==run_formula(w,'N','T')
            total+=1;outputs+=bool(count)
    assert inverse_count(tuple('NTT'),'N','T')==1
    assert encode(tuple('NTT'),'N','T')!=tuple('NTT')
    assert inverse_count(tuple('NTTT'),'N','T')==1
    assert inverse_count(tuple('NTTTT'),'N','T')==2
    return {'ternary_words_length_0_through_8':total,'valid_output_words':outputs,'direct_forward_multiplicity_DP_formula_agree':True}

def unique_parse(raw,signs):
    paths={0:[()]}
    for i in range(len(raw)):
        for before in paths.get(i,[]):
            for s in signs:
                if raw.startswith(s,i):paths.setdefault(i+len(s),[]).append(before+(s,))
    assert len(paths.get(len(raw),[]))==1
    return paths[len(raw)][0]

def compute():
    spec=json.loads((OLD/'src/SPEC.json').read_text());signs=spec['signs']
    allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed']
    assert len(signs)==22 and len(allowed)==179
    data=json.loads(gzip.decompress((OLD/'artifacts/GROUPS.json.gz').read_bytes()))
    cap=json.loads(CAP.read_text());out={}
    for ed,rows in data.items():
        forms={};ids=set()
        for row in rows:
            assert row['edition']==ed and row['page'] in allowed and row['kind']=='P'
            assert not row['page'].startswith('f84') and row['page'] not in ('f116v','f1r')
            assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            assert row['locus'].split('.')[0]==row['page']
            assert row['id']==f"{ed}|{row['locus']}|G{int(row['source_group_index']):03d}" and row['id'] not in ids
            ids.add(row['id']);raw=row['ivtff_group_raw']
            if raw not in forms:
                units=unique_parse(raw,signs);assert list(units)==row['units']
                forms[raw]={'units':units,'frequency':0,'source':row}
            assert list(forms[raw]['units'])==row['units'];forms[raw]['frequency']+=1
        pairs=[tuple(p) for p in cap['readers'][ed]['survivors']]
        assert len(pairs)==len(set(pairs))
        active_targets={t for n,t in cap['readers'][ed]['active_survivors']}
        pair_results=[]
        rigid_by_dp=set(forms)
        for n,t in pairs:
            categories={k:{'groups':0,'types':0} for k in ('unique_literal','unique_changed','ambiguous')}
            maximum=0;example=None;literal_groups=0
            for raw in sorted(forms):
                entry=forms[raw]
                w=entry['units'];count=inverse_count(w,n,t);assert count>0
                literal=encode(w,n,t)==w
                if literal:literal_groups+=entry['frequency']
                if count==1:
                    category='unique_literal' if literal else 'unique_changed'
                else:category='ambiguous'
                has_tt=any(a==b==t for a,b in zip(w,w[1:]))
                has_nt=any(a==n and b==t for a,b in zip(w,w[1:]))
                assert (category=='unique_literal') == (not has_tt)
                assert (category=='unique_changed') == (count==1 and has_nt)
                categories[category]['groups']+=entry['frequency'];categories[category]['types']+=1
                if category!='unique_literal':rigid_by_dp.discard(raw)
                if count>maximum:maximum=count;example=entry['source']
            pair_results.append({'N':n,'T':t,'categories':categories,'maximum':maximum,'example':example,'literal_preimage_groups':literal_groups})
        rigid_by_doubles={raw for raw,e in forms.items() if not any(a==b and a in active_targets for a,b in zip(e['units'],e['units'][1:]))}
        assert rigid_by_dp==rigid_by_doubles
        out[ed]={'groups':len(rows),'types':len(forms),'pairs':pair_results,'rigid_groups':sum(forms[r]['frequency'] for r in rigid_by_dp),'rigid_types':len(rigid_by_dp),'active_targets':sorted(active_targets),'rigid_forms':[{'form':r,'count':forms[r]['frequency'],'first_id':forms[r]['source']['id']} for r in sorted(rigid_by_dp)],'examples':{r:{'count':forms[r]['frequency'],'first_id':forms[r]['source']['id'],'globally_rigid':r in rigid_by_dp,'pair_counts':[{'N':n,'T':t,'preimages':inverse_count(forms[r]['units'],n,t)} for n,t in pairs]} for r in ('daldy','qokeedy','qokedy','daiin','keeees') if r in forms}}
    return out

def compare(primary, expected):
    assert primary['status']=='EXACT_INVERSE_ACCOUNTED'
    assert set(primary['readers'])==set(expected)
    for ed,mine in expected.items():
        theirs=primary['readers'][ed]
        for k in ('groups','types','rigid_groups','rigid_types','rigid_forms'):
            assert theirs[k]==mine[k],(ed,k)
        assert theirs['active_T']==mine['active_targets']
        assert set(theirs['examples'])==set(mine['examples'])
        for form,x in mine['examples'].items():
            y=theirs['examples'][form]
            for k in ('count','first_id','globally_rigid'):assert x[k]==y[k],(ed,form,k)
            assert {(p['N'],p['T']):p['preimages'] for p in x['pair_counts']}=={(p['N'],p['T']):p['preimages'] for p in y['pair_counts']}
        lookup={(p['N'],p['T']):p for p in theirs['pairs']}
        assert len(lookup)==len(theirs['pairs'])==len(mine['pairs'])
        for p in mine['pairs']:
            q=lookup[p['N'],p['T']]
            for cat,counts in p['categories'].items():
                for unit,value in counts.items():assert q[cat+'_'+unit]==value,(ed,p['N'],p['T'],cat,unit)
            assert q['literal_preimage_groups']==p['literal_preimage_groups']
            assert q['max_preimages']==p['maximum']
            assert q['max_form']==p['example']['ivtff_group_raw']
            assert q['max_first_id']==p['example']['id']

def main():
    controls=fixtures();expected=compute()
    primary=json.loads((D/'artifacts/RESULT.json').read_text())
    compare(primary,expected)
    report={'status':'PASS','controls':controls,'readers':{e:{k:v for k,v in r.items() if k not in ('pairs','rigid_forms','examples')} for e,r in expected.items()},'independence':'Direct original-next-symbol inverse DP, independent raw parser; no primary imports.','limits':'No actual source choice, sounds, meanings, original boundary verification or held confirmation.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
