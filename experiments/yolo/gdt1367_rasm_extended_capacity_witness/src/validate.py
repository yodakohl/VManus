"""Independent arbitrary constructive witness validator. No primary imports."""
from pathlib import Path
from itertools import product
import hashlib,importlib,io,json,sys
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/rasm_arch_source_20261013'
HASHES={'__init__.py':'29d23d75612198ff1206aaba0105c61c5d72aa61848a840764e9a3936343c623','rasm_arch.py':'dcbeeb69253c6a467276c267e3f26871cc427f5e9c1698ae573bf876a6c416cd','util.py':'befeced908b7e7d9fb3c9a6c5add3dd5b72aecf48ddf9fd5facdf2c042f177a0'}
REP={'A':'ا','B':'ب','C':'ص','D':'د','E':'ع','F':'ف','G':'ج','H':'ه','K':'ك','L':'ل','M':'م','O':'ھ','R':'ر','S':'س','T':'ط','W':'و','Q':'ق','N':'ن'}
ORDINARY=tuple(sorted(set(REP)-{'Q','N'}))

def compute():
    old=json.loads((ROOT/'experiments/yolo/gdt1365_rasm_nonfinal_capacity/artifacts/RESULT.json').read_text())
    premises={}
    for reader in ('IT2a','RF1b','ZL3b'):
        p=old['panels'][reader+'_GE2']
        nonfinal=sorted(r['char'] for r in p['characters'] if r['nonfinal_count'])
        alphabet=p['alphabet'];terminal=sorted(set(alphabet)-set(nonfinal))
        assert len(alphabet)==18 and len(nonfinal)==16 and terminal==['m','n']
        premises[reader]={'groups':p['groups'],'types':p['types'],'alphabet':alphabet,'nonfinal':nonfinal,'terminal_only':terminal}
    assert all(p['nonfinal']==premises['IT2a']['nonfinal'] and p['alphabet']==premises['IT2a']['alphabet'] for p in premises.values())
    targets=premises['IT2a']['nonfinal'];alphabet=premises['IT2a']['alphabet']
    mapping=dict(zip(ORDINARY,targets));mapping.update({'Q':'m','N':'n','Y':'n','J':targets[0]})
    inverse={target:REP[cl] for cl,target in mapping.items() if cl in ORDINARY}
    inverse.update({'m':REP['Q'],'n':REP['N']})
    for name,digest in HASHES.items():assert hashlib.sha256((CACHE/'rasm_arch'/name).read_bytes()).hexdigest()==digest
    sys.path.insert(0,str(CACHE));module=importlib.import_module('rasm_arch.rasm_arch')
    assert Path(module.__file__).resolve()==(CACHE/'rasm_arch/rasm_arch.py').resolve()
    def forbidden(*a,**k):raise AssertionError('Corpus/resource access forbidden')
    module.files=forbidden
    def rasm(source):
        rows=list(module.rasm_arch(io.StringIO(source)))
        assert len(rows)==1 and rows[0][0]==source
        return rows[0][1]
    controls=[]
    for cl in ORDINARY:
        rep=REP[cl]
        for source,expected in ((rep,cl),(rep+'ب',cl+'B'),('ب'+rep,'B'+cl)):
            got=rasm(source);assert got==expected
            controls.append({'class':cl,'source':source,'rasm':got})
    digest=hashlib.sha256();count=0;used=set()
    for n in (1,2,3):
        for prefix in product(targets,repeat=n-1):
            for last in alphabet:
                target=''.join(prefix)+last
                source=''.join(inverse[c] for c in target)
                output=rasm(source)
                assert ''.join(mapping[c] for c in output)==target
                assert len(output)==len(source)==len(target)
                used.update(output)
                digest.update((json.dumps([target,source,output],ensure_ascii=False,separators=(',',':'))+'\n').encode())
                count+=1
    assert count==4914 and len(used)==18 and not used&set('JY')
    return {'status':'EXTENDED_RASM_CONSTRUCTIVE_CAPACITY','mapping':mapping,'representatives':REP,'premises':premises,'synthetic_cases':count,'roundtrip_sha256':digest.hexdigest(),'representative_controls':controls,'effective_used_classes':18,'retained_extension_classes':19,'declared_full_classes':20}

def main():
    lock=json.loads((D/'src/REGISTRATION_LOCK.json').read_text())
    for path,digest in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    expected=compute();observed=json.loads((D/'artifacts/RESULT.json').read_text())
    for key,value in expected.items():assert observed[key]==value,key
    result={'status':'PASS','synthetic_cases':expected['synthetic_cases'],'representative_controls':len(expected['representative_controls']),'roundtrip_sha256':expected['roundtrip_sha256'],'independence':'No primary runner imported/read before validator freeze. Independently reconstructed lexicographic witness, saved1365premises, Unicode representative controls and exact digest using pinned converter.','scope':'Source-free technical capacity only; arbitrary witness is not a native lexicon, phonetic key, natural-language text or FULLfit. No native cache or source-corpus query.'}
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
