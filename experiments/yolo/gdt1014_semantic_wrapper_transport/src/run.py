from common import *
from worker import bounded
import concurrent.futures,collections,subprocess

def check_witness(w):
    from wrappers import relations,contradictions
    assert not contradictions(w['aliases'],relations(w['aliases']))
    args=dict(parse=w['parse'],variant=w['variant'])
    one=bounded('replay',args);two=bounded('replay',dict(**args,independent=True))
    if one['status']==two['status']=='COMPLETE':
        assert one['result']==two['result']
        assert one['result']['status']=='COHERENT'
    return dict(primary=one,independent=two,verified=one['status']==two['status']=='COMPLETE')

def job(case):
    panel=read(A/'PANEL.json');payload=dict(paragraph=panel[case['context_index']],lexicon=case['canonical_lexicon'],variant=case['variant'])
    result=bounded('primary',payload)
    if result['status']=='sat':result['witness_check']=check_witness(result['witness'])
    return dict(id=case['id'],**result)

def main():
    checklock();receipt=read(A/'PUBLIC_REGISTRATION.json');subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],check=True,cwd=R)
    s,g=inputs();started=datetime.datetime.now(datetime.timezone.utc).isoformat();cases=read(A/'PREDICTIONS.json')
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:rows=list(pool.map(job,cases))
    put('ROWS.json',rows);put('EXECUTION_RECEIPT.json',dict(started_utc=started,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registration_commit=receipt['commit']))
    result=dict(experiment='GDT1014',status='PRIMARY_COMPLETE_AWAITING_VALIDATION',canonical_cases=len(rows),counts=dict(collections.Counter(r['status'] for r in rows)),verified_primary_witnesses=sum(r.get('witness_check',{}).get('verified',False) for r in rows),confirmed_words=0,independent_meaning_capacity=0,significance=False)
    put('RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
