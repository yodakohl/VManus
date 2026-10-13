"""Pinned MIT converter, synthetic source-only checks; no corpus/resource API."""
from pathlib import Path
from itertools import product
import argparse,hashlib,importlib,io,json,sys
HASHES={'__init__.py':'29d23d75612198ff1206aaba0105c61c5d72aa61848a840764e9a3936343c623','rasm_arch.py':'dcbeeb69253c6a467276c267e3f26871cc427f5e9c1698ae573bf876a6c416cd','util.py':'befeced908b7e7d9fb3c9a6c5add3dd5b72aecf48ddf9fd5facdf2c042f177a0'}

def check(directory):
    directory=Path(directory)
    for name,digest in HASHES.items():assert hashlib.sha256((directory/'rasm_arch'/name).read_bytes()).hexdigest()==digest
    sys.path.insert(0,str(directory))
    module=importlib.import_module('rasm_arch.rasm_arch')
    assert Path(module.__file__).resolve()==(directory/'rasm_arch/rasm_arch.py').resolve()
    def forbidden(*a,**k):raise AssertionError('Source corpus/resource access forbidden')
    module.files=forbidden
    letters='ابتثجحخدذرزسشصضطظعغفقكلمنهوي';assert len(set(letters))==28
    mapping={c:key for key,chars in [('A','ا'),('B','بتثني'),('G','جحخ'),('D','دذ'),('R','رز'),('S','سش'),('C','صض'),('T','طظ'),('E','عغ'),('F','فق'),('K','ك'),('L','ل'),('M','م'),('H','ه'),('W','و')] for c in chars}
    terminal={'ق':'Q','ن':'N','ي':'Y'}
    outputs=set();medial=set();checked=0
    for n in (1,2,3):
        for chars in product(letters,repeat=n):
            source=''.join(chars);record=list(module.rasm_arch(io.StringIO(source)))[0];out=record[1]
            expect=''.join(terminal[c] if i==n-1 and c in terminal else mapping[c] for i,c in enumerate(chars))
            assert out==expect and len(out)==n and not(set(out[:-1])&set('QNY'))
            outputs.update(out);medial.update(out[:-1]);checked+=1
    assert len(outputs)==18 and len(medial)==15
    fulloutputs=set();fullmedial=set();fullcases=0
    for c in sorted(set(module.DATA.CHAR)):
        for source in (c,c+'ب','ب'+c):
            out=list(module.rasm_arch(io.StringIO(source)))[0][1]
            assert len(out)==len(source) and not(set(out[:-1])&set('QNY'))
            fulloutputs.update(out);fullmedial.update(out[:-1]);fullcases+=1
    assert len(fulloutputs)==20 and len(fullmedial)==17
    samples={s:[list(r) for r in module.rasm_arch(io.StringIO(s))] for s in ('قاق','نان','ياي','قاب','ناب','ياب','ء','َ','أ','إ','آ','ؤ','ئ','بءن','ب،ن','ب☃ن','ﻻ')}
    clusters={'default':list(module.rasm_arch(io.StringIO('ﻻ'))),'normalized':list(module.rasm_arch(io.StringIO('ﻻ'),norm_clusters=True))}
    blocks={s:list(module.rasm_arch(io.StringIO(s),blocks=True)) for s in ('قاق','نان','ياي')}
    return {'status':'PASS_PINNED_SOURCE_ONLY_RULE','source_hashes':HASHES,'restricted_words':checked,'restricted_output':sorted(outputs),'restricted_nonfinal':sorted(medial),'full_inventory_probe_cases':fullcases,'full_output':sorted(fulloutputs),'full_nonfinal':sorted(fullmedial),'resource_access_disabled':True,'synthetic_samples':samples,'cluster_option':clusters,'block_option':blocks,'limit':'Modern technical converter only; all strings synthetic. No historical witness, source corpus, true glyphs or Voynich language claim.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-dir',default='.cache/rasm_arch_source_20261013');parser.add_argument('--output');a=parser.parse_args();r=check(a.source_dir);text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if a.output:Path(a.output).write_text(text)
    print(text)
if __name__=='__main__':main()
