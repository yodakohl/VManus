#!/usr/bin/env python3
"""Independent exact count-vector contradiction and original-profile audit."""
import argparse,collections,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
P=ROOT/'experiments/yolo/gdt1200_stable_part_repetition_capacity/artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prefix(xs,arity):
    slots=1
    for x in xs:
        if slots==0:return False
        slots+=arity[x]-1
    return slots==0
def postfix(xs,arity):
    stack=0
    for x in xs:
        if stack<arity[x]:return False
        stack+=1-arity[x]
    return stack==1
def controls():
    arity={'a':0,'u':1,'b':2}
    assert prefix('baua',arity) and postfix('aaub',arity)
    assert not prefix('bauabaua',arity) and not postfix('aaubaaub',arity)
    assert sum(1-arity[x] for x in 'baua')==1
    assert sum(1-arity[x] for x in 'bauabaua')==2
    assert not prefix('baau',arity) # Balance alone does not certify a parse.
    assert sum(1-arity[x] for x in 'baau')==1
    return {'status':'PASS_SOURCE_FREE_FIXTURES','single_tree_prefix':'baua',
            'single_tree_postfix':'aaub','doubled_trees_rejected':True,
            'balance_not_sufficient_example':'baau','not_a_finite_proof_of_universal_theorem':True}
def proof():
    forms=['ol','oldy','ololdy'];counts=[collections.Counter(w) for w in forms]
    coeff=[-1,-1,1];symbols=sorted(set(''.join(forms)))
    combined={s:sum(c*v[s] for c,v in zip(coeff,counts)) for s in symbols}
    assert all(v==0 for v in combined.values()) and ''.join(forms[:2])==forms[2]
    rhs=sum(coeff);assert rhs==-1
    return {'forms':forms,'units':[list(w) for w in forms],
      'coefficient_vectors':[{s:v[s] for s in symbols} for v in counts],
      'linear_combination':coeff,'combined_lhs_coefficients':combined,'combined_rhs':rhs,
      'universal_argument':'Each finite rooted tree has sum arity = node_count - 1, hence sum(1-arity)=1. Identical-unit concatenation adds these charges. The displayed linear combination gives 0=-1, independent of traversal and of arity bounds. Every working unit is assumed exactly one node with a fixed arity; no implicit nodes or forests.'}
def sources():
    profiles=read(P/'FORM_PROFILES.json');lines=read(P/'REPEAT_SOURCE_LINES.json')
    expected={'ZL3b':[455,25,2],'IT2a':[456,24,2],'RF1b':[469,18,2]};out=[]
    for ed,ns in expected.items():
        selected={}
        for form,n in zip(['ol','oldy','ololdy'],ns):
            entries=[r for r in profiles if r['edition']==ed and r['form']==form]
            assert len(entries)==1;r=entries[0];assert r['n']==n>0
            assert len(r['source_group_ids'])==n==len(set(r['source_group_ids']))
            assert set(r['loci'])=={gid.split('|')[1] for gid in r['source_group_ids']}
            assert all(gid.startswith(ed+'|') for gid in r['source_group_ids'])
            selected[form]=r
        witnesses=[]
        for loc in ['f23r.1','f34r.1']:
            ls=[l for l in lines if l['edition']==ed and l['locus']==loc];assert len(ls)==1
            groups=ls[0]['groups'];assert len(groups)==int(groups[0]['source_group_count'])
            assert [int(g['source_group_index']) for g in groups]==list(range(1,len(groups)+1))
            hits=[g for g in groups if g['ivtff_group_raw']=='ololdy'];assert len(hits)==1
            g=hits[0];assert g['left_separator']==g['right_separator']=='DEFINITE_SPACE'
            assert g['source_group_id'] in selected['ololdy']['source_group_ids']
            witnesses.append(g)
        assert {w['source_group_id'] for w in witnesses}==set(selected['ololdy']['source_group_ids'])
        out.append({'edition':ed,'counts':dict(zip(['ol','oldy','ololdy'],ns)),
                    'profiles':selected,'joined_witnesses':witnesses})
    return out
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps({'controls':controls(),'proof':proof()}));return
    lock=read(E/'LOCK.json')
    pins=lock.get('files',lock.get('sha256'))
    assert isinstance(pins,dict)
    for path,h in pins.items():assert not Path(path).is_absolute() and sha(ROOT/path)==h,path
    spec=read(E/'src/SPEC.json');result=read(A/'RESULT.json');reconstructed=sources();algebra=proof();fixtures=controls()
    assert result['status']=='CLOSED_WORD_FIXED_ARITY_EXCLUDED'
    assert result['claim_ceiling']==spec['claim_ceiling']
    assert result['new_corpus_census'] is False and result['new_meanings']==0 and result['independent_readers'] is False
    assert len(result['cases'])==3
    checked=[]
    for item in reconstructed:
        matches=[c for c in result['cases'] if c['reader']==item['edition']];assert len(matches)==1;c=matches[0]
        assert c['counts']==[item['counts'][form] for form in algebra['forms']]
        assert c['joinedWitnesses']==item['joined_witnesses']
        assert c['profiles']==[{k:item['profiles'][form][k] for k in ['form','n','source_group_ids','loci']} for form in algebra['forms']]
        assert c['vectors']==[dict(collections.Counter(w)) for w in algebra['forms']]
        assert c['certificate']=={'coefficients':[-1,-1,1],'lhs':algebra['combined_lhs_coefficients'],'rhs':-1}
        checked.append({'reader':item['edition'],'counts':item['counts'],
                        'joined_ids':[g['source_group_id'] for g in item['joined_witnesses']]})
    for path,h in result['input_hashes'].items():assert sha(ROOT/path)==h,path
    receipt={'experiment_id':'GDT1422','status':'PASS_INDEPENDENT_PROFILE_WITNESS_AND_LINEAR_CERTIFICATE',
      'readers':checked,'proof':algebra,'controls':fixtures,'validator_sha256':sha(Path(__file__)),
      'lock_sha256':sha(E/'LOCK.json'),'result_sha256':sha(A/'RESULT.json'),
      'scope':'Conditional complete-word/one-node-per-working-unit/fixed-arity/single-tree contradiction. No general grammar exclusion, source meaning, image validation or independent manuscript samples. Profiles are inherited1200evidence, not a new corpus census. Universal proof is the tree-edge identity, not the finite fixtures.'}
    destination=A/'VALIDATION.json'
    if destination.exists():assert read(destination)==receipt
    else:destination.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'readers':len(checked)}))
if __name__=='__main__':main()
