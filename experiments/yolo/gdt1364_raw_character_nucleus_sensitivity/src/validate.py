"""Independent exact combination/bitset validator, no subset zeta or runner import."""
from pathlib import Path
from itertools import combinations
import gzip,json,re,hashlib
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
OLD=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion'
KS=(3,5,7,8)

def optimize(supports, weights, alphabet_size, sizes):
    group_bits=[0]*alphabet_size;type_bits=[0]*alphabet_size;offset=0
    for j,(support,weight) in enumerate(zip(supports,weights)):
        block=((1<<weight)-1)<<offset;offset+=weight
        for i in range(alphabet_size):
            if support>>i&1:group_bits[i]|=block;type_bits[i]|=1<<j
    totals=(sum(weights),len(supports));best={k:{'groups':None,'types':None} for k in sizes}
    def visit(start,depth,mask,gb,tb):
        if depth in best:
            missed=(totals[0]-gb.bit_count(),totals[1]-tb.bit_count())
            for obj,index in [('groups',0),('types',1)]:
                proposal=(missed[index],mask,missed[1-index])
                if best[depth][obj] is None or proposal[:2]<best[depth][obj][:2]:best[depth][obj]=proposal
        if depth==max(sizes):return
        for i in range(start,alphabet_size):
            visit(i+1,depth+1,mask|(1<<i),gb|group_bits[i],tb|type_bits[i])
    visit(0,0,0,0,0)
    return best

def fixtures():
    cases=0
    for family in range(1,1<<7):
        supports=[s for s in range(1,8) if family>>(s-1)&1]
        for variant in range(3):
            weights=[1+(s+variant)%3 for s in supports]
            result=optimize(supports,weights,3,(0,1,2,3))
            for k in range(4):
                direct=[]
                for chosen in combinations(range(3),k):
                    mask=sum(1<<i for i in chosen)
                    miss=[i for i,s in enumerate(supports) if s&mask==0]
                    direct.append((sum(weights[i] for i in miss),len(miss),mask))
                group=min(direct,key=lambda x:(x[0],x[2]));typ=min(direct,key=lambda x:(x[1],x[2]))
                assert result[k]['groups']==(group[0],group[2],group[1])
                assert result[k]['types']==(typ[1],typ[2],typ[0])
            cases+=1
    # A shared raw component can reduce hitting cardinality: atomic bc,bd.
    oldopt=optimize([1,2],[2,3],2,(0,1,2))
    rawopt=optimize([3,5],[2,3],3,(0,1,2,3))
    assert min(k for k,v in oldopt.items() if v['groups'][0]==0)==2
    assert min(k for k,v in rawopt.items() if v['groups'][0]==0)==1
    for encodings in [('ab','ac','d'),('a','b','c'),('aa','a','ba')]:
        rawalphabet=sorted(set(''.join(encodings)))
        oldsupports=[1,2,4,3,5,6,7]; weights=[1,2,3,4,5,6,7]
        rawsupports=[sum(1<<rawalphabet.index(c) for c in set(''.join(encodings[i] for i in range(3) if support>>i&1))) for support in oldsupports]
        before=optimize(oldsupports,weights,3,(0,1,2,3))
        after=optimize(rawsupports,weights,len(rawalphabet),tuple(range(len(rawalphabet)+1)))
        for k in range(min(3,len(rawalphabet))+1):
            assert after[k]['groups'][0]<=before[k]['groups'][0]
            assert after[k]['types'][0]<=before[k]['types'][0]
    return {'weighted_support_families':cases,'sizes_checked':[0,1,2,3],'bitsets_vs_direct_subset_membership':'PASS','shared_component_hitting_tau':[2,1],'additional_refinement_controls':3}

def parse(raw,signs):
    ways={0:[()]}
    for i in range(len(raw)):
        for before in ways.get(i,[]):
            for s in signs:
                if raw.startswith(s,i):ways.setdefault(i+len(s),[]).append(before+(s,))
    assert len(ways.get(len(raw),[]))==1
    return ways[len(raw)][0]

def input_panels():
    spec=json.loads((OLD/'src/SPEC.json').read_text());signs=sorted(spec['signs']);assert len(signs)==22
    allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed'];assert len(allowed)==179
    data=json.loads(gzip.decompress((OLD/'artifacts/GROUPS.json.gz').read_bytes()));panels={};alphabets={}
    for ed,rows in data.items():
        alphabet=sorted(set(''.join(row['ivtff_group_raw'] for row in rows)))
        assert alphabet and all('a'<=x<='z' for x in alphabet)
        alphabets[ed]=alphabet
        forms={};seen=set()
        for row in rows:
            assert row['edition']==ed and row['page'] in allowed and row['kind']=='P'
            assert row['page'] not in ('f1r','f116v') and not row['page'].startswith('f84')
            assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            assert row['locus'].split('.')[0]==row['page']
            ident=f"{ed}|{row['locus']}|G{int(row['source_group_index']):03d}"
            assert ident==row['id'] and ident not in seen;seen.add(ident)
            m=re.fullmatch(r'f(\d+)[rv]\d*',row['page']);assert m;leaf='f'+m.group(1)
            raw=row['ivtff_group_raw'];assert raw and all('a'<=x<='z' for x in raw)
            if raw not in forms:
                units=parse(raw,signs);assert list(units)==row['units']
                forms[raw]={'form':raw,'count':0,'first_id':ident,'leaves':set(),'support':sum(1<<alphabet.index(x) for x in set(raw)),'units':list(units)}
            f=forms[raw];assert f['units']==row['units'];f['count']+=1;f['leaves'].add(leaf)
        for panel in ('FULL','GE2'):
            selected=[forms[f] for f in sorted(forms) if panel=='FULL' or len(forms[f]['leaves'])>=2]
            assert set(signs)=={u for f in forms.values() for u in f['units']}
            panels[ed,panel]=selected
    return alphabets,panels

def certificate(forms,mask,signs):
    missed=[f for f in forms if not f['support']&mask]
    leaves=set().union(*(f['leaves'] for f in missed)) if missed else set()
    return {'mask':mask,'representatives':[s for i,s in enumerate(signs) if mask>>i&1],'uncovered_groups':sum(f['count'] for f in missed),'uncovered_types':len(missed),'physical_leaves':len(leaves),'leaf_ids':sorted(leaves),'forms':[{'form':f['form'],'count':f['count'],'first_id':f['first_id'],'physical_leaves':len(f['leaves']),'leaf_ids':sorted(f['leaves'])} for f in missed]}

def compute():
    alphabets,panels=input_panels();result={}
    previous=json.loads((ROOT/'experiments/yolo/gdt1363_nucleus_omission_envelope/artifacts/RESULT.json').read_text())
    for (ed,panel),forms in panels.items():
        signs=alphabets[ed];n=len(signs);assert n>=max(KS)
        optimum=optimize([f['support'] for f in forms],[f['count'] for f in forms],n,tuple(range(n+1)))
        tau=min(k for k,v in optimum.items() if v['groups'][0]==0)
        old_tau={'IT2a':13,'RF1b':14,'ZL3b':11}[ed] if panel=='FULL' else 9
        assert tau<=old_tau
        assert optimum[tau]['groups'][1]==optimum[tau]['types'][1]
        witnesses={k:{obj:certificate(forms,entry[1],signs) for obj,entry in optimum[k].items()} for k in KS}
        result[ed,panel]={'alphabet':signs,'groups':sum(f['count'] for f in forms),'types':len(forms),'tau':tau,'tau_certificate':certificate(forms,optimum[tau]['groups'][1],signs),'results':witnesses}
        old=previous['panels'][ed+'_'+panel]
        assert old['groups']==result[ed,panel]['groups'] and old['types']==len(forms)
        for k in KS:
            for obj,oldname in [('groups','occurrences'),('types','types')]:
                assert witnesses[k][obj]['uncovered_'+obj]<=old['K'][str(k)][oldname]['minimum_uncovered']
    return alphabets,result

def compare(primary,alphabets,expected):
    assert primary['status']=='RAW_CHARACTER_NUCLEUS_SENSITIVITY'
    assert set(primary['panels'])=={ed+'_'+panel for ed,panel in expected}
    for (ed,panel),mine in expected.items():
        theirs=primary['panels'][ed+'_'+panel]
        assert theirs['alphabet']==alphabets[ed]
        assert theirs['min_hitting_size']==mine['tau']
        assert theirs['hitting_witness_mask']==mine['tau_certificate']['mask']
        assert theirs['hitting_witness_representatives']==mine['tau_certificate']['representatives']
        assert theirs['groups']==mine['groups'] and theirs['types']==mine['types']
        assert set(theirs['K'])=={str(k) for k in KS}
        for k,outcomes in mine['results'].items():
            for objective,m in outcomes.items():
                q=theirs['K'][str(k)]['occurrences' if objective=='groups' else 'types']
                assert q['minimum_uncovered']==m['uncovered_'+objective],(ed,panel,k,objective)
                assert q['representative_mask']==m['mask']
                assert q['representatives']==m['representatives']
                assert q['uncovered_groups']==m['uncovered_groups']
                assert q['uncovered_types']==m['uncovered_types']
                assert q['uncovered_physical_leaves']==m['physical_leaves']
                normalized=[{'form':f['form'],'count':f['count'],'first_id':f['first_id'],'physical_leaves':sorted(int(x[1:]) for x in f['leaf_ids'])} for f in m['forms']]
                assert q['uncovered_forms']==normalized

def main():
    controls=fixtures();signs,expected=compute()
    primary=json.loads((D/'artifacts/RESULT.json').read_text());compare(primary,signs,expected)
    report={'status':'PASS','controls':controls,'independence':'Copied/adapted independent1363recursive bitset engine for RAW_CHAR; no primary runner read/imported and no zeta transform or NumPy.','panels':len(expected),'objective_witnesses':len(expected)*len(KS)*2,'limits':'Checks combinatorics/source-cache accounting, not true phonology, nuclei, physical word boundaries or omitted vowels.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
