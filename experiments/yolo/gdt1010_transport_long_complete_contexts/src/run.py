from common import *
from worker import bounded
import collections,concurrent.futures,csv,subprocess

def task(job):
    panel=read(A/'PANEL.json');ps=[panel[i] for i in job['system']]
    result=bounded('primary',dict(paragraphs=ps));result.setdefault('witnesses',[])
    for witness in result['witnesses']:witness['meaning_check']=bounded('meaning',dict(witness=witness))
    return dict(**job,**result)

def main():
    checklock();s,g=inputs();receipt=read(A/'PUBLIC_REGISTRATION.json')
    subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],check=True,cwd=R)
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();jobs=read(A/'PREDICTIONS.json');rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:
        futures={pool.submit(task,j):j['id'] for j in jobs}
        for f in concurrent.futures.as_completed(futures):
            rows.append(f.result())
            if len(rows)%32==0 or len(rows)==len(jobs):print(json.dumps(dict(done=len(rows),total=len(jobs),last=rows[-1]['status'])),flush=True)
    rows.sort(key=lambda x:x['id']);put('ROWS.json',rows)
    result=dict(experiment='GDT1010',status='COMPLETE_LONG_SHARED_GRAMMAR_AUDIT',systems=len(rows),counts=dict(collections.Counter(r['status'] for r in rows)),sampled_maps=sum(len(r['witnesses']) for r in rows),coherent_common_witness_variants=sum(v['status']=='COHERENT_COMMON_READING' for r in rows for w in r['witnesses'] for v in w['meaning_check'].get('variants',[])),meaning_unknowns=sum(w['meaning_check']['status']!='COMPLETE' for r in rows for w in r['witnesses']),semantic_map_space_exhausted=False,confirmed_words=0,independent_meaning_capacity=0,significance=False)
    put('RESULT.json',result);put('EXECUTION_RECEIPT.json',dict(started_utc=start,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registration_commit=receipt['commit']))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['system','family','complete_paragraphs','shared_words','status','sampled_maps','common_coherent_variants','meaning_unknowns','remaining_semantic_alternatives','independent_meaning_capacity'])
        for r in rows:w.writerow([r['id'],r['family'],';'.join(r['paragraph_ids']),','.join(r['all_shared_words']),r['status'],len(r['witnesses']),sum(v['status']=='COHERENT_COMMON_READING' for x in r['witnesses'] for v in x['meaning_check'].get('variants',[])),sum(x['meaning_check']['status']!='COMPLETE' for x in r['witnesses']),'NONE_IF_INDEPENDENTLY_VERIFIED' if r['status']=='UNSAT' else 'UNRESOLVED',0])
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
