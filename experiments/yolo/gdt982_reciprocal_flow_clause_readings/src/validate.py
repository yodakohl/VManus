"""Nonimporting algebraic check, exact source reconstruction and regeneration."""
import collections,hashlib,itertools,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(n):return json.loads((E/'artifacts'/n).read_text())
def main():
    models=json.loads((E/'src/CANDIDATES.json').read_text());spec=json.loads((E/'src/SPEC.json').read_text())
    for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    pairs=json.loads((R/spec['families']).read_text());panels=json.loads((R/spec['paragraphs']).read_text())
    expected=[];chey=[]
    for ed,ps in panels.items():
        for p in ps:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            for line in p['lines']:
                for i,w in enumerate(line['words']):
                    if w=='chey':chey.append((ed,p['id'],line['locus'],i))
                if not line['anchor_eligible']:continue
                for i in range(2,len(line['words'])-2):
                    if line['words'][i]!='chey':continue
                    a,b,c,d=line['words'][i-2:i]+line['words'][i+1:i+3]
                    for stem1,stem2 in pairs:
                        if all(x in (s+'r',s+'l') for x,s in zip([a,b,c,d],[stem1,stem2,stem1,stem2])):
                            expected.append((ed,p['id'],line['locus'],i,stem1+'/'+stem2,a[-1]+b[-1]+c[-1]+d[-1]))
    actual=[(f['edition'],f['paragraph'],f['locus'],f['index'],f['family'],f['ends']) for f in read('FRAMES.json')]
    assert sorted(actual)==sorted(expected)
    assert sorted(chey)==sorted((f['edition'],f['paragraph'],f['locus'],f['index']) for f in read('ALL_CHEY.json'))
    fm={f['id']:f for f in read('FRAMES.json')};mm={m['id']:m for m in models}
    def expected_status(ends,m):
        a,b,c,d=ends
        if m['operator']=='DESCRIBE':return 'DESCRIPTIVE_UNSCORED'
        if m['operator']=='THEN':ok=a==d and (m['tail']=='ONCE' or c==b)
        else:ok=(a,b)!=(c,d) and (m['tail']=='ONCE' or a==b)
        return 'COHERENT_UNCONFIRMED' if ok else 'INTERNAL_CONTRADICTION'
    for row in read('PREDICTIONS.json'):assert row['status']==expected_status(fm[row['frame']]['ends'],mm[row['model']])
    for row in read('RESULT.json')['local_outcomes']:assert row['status']==expected_status('lrrl',mm[row['model']])
    # Source/full-context integrity; no cleaned transcription is substituted.
    original={}
    for n in spec['snapshots']:
        data=json.loads((R/n).read_text())
        for row in data['lines']:
            if row['metadata']['locus'] in spec['context_loci']:
                original[(row['metadata']['edition'],row['metadata']['locus'])]=dict(metadata=row['metadata'],groups=[dict(zip(data['group_columns'],g)) for g in row['groups']])
    context=read('COMPLETE_CONTEXT.json')
    assert len(original)==15
    for ed,ls in context.items():
        assert len(ls)==5
        for row in ls:assert row==original[(ed,row['metadata']['locus'])]
    artifacts=[p for p in (E/'artifacts').iterdir() if p.name not in ['VALIDATION.json','EXECUTION_RECEIPT.json','README.md']]
    before={p.name:p.read_bytes() for p in artifacts}
    subprocess.run([sys.executable,str(E/'src/run.py')],check=True,stdout=subprocess.DEVNULL)
    assert all((E/'artifacts'/n).read_bytes()==v for n,v in before.items())
    result=dict(status='PASS',independent_author=False,independent_algebra=True,all_chey_reconstructed=len(chey),frames_reconstructed=len(expected),source_context_lines=15,exact_regeneration=True,semantic_validation=False)
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
