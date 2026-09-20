from common import *
from worker import bounded
import collections,concurrent.futures,csv,subprocess

def extension(job):
    panel=read(A/'PANEL.json');candidate=job['original'];p=panel[job['context_index']]
    r=bounded('primary',dict(paragraphs=[p],lexicon=candidate['code']));r.setdefault('witnesses',[])
    for witness in r['witnesses']:
        witness['aliases']={**candidate['code'],**witness['aliases']}
        witness['parses']=[candidate['parse'],*witness['parses']]
        witness['meaning_check']=bounded('meaning',dict(witness=witness))
    return dict(id=job['id'],original_id=candidate['id'],context=p['id'],context_index=job['context_index'],original_valid_variants=candidate['valid_variants'],**r)

def main():
    checklock();s,g=inputs();receipt=read(A/'PUBLIC_REGISTRATION.json');subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],check=True,cwd=R)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();originals={r['id']:r for r in read(A/'ORIGINAL_CANDIDATES.json')}
    jobs=[dict(id=p['id'],original=originals[p['original_id']],context_index=p['context_index']) for p in read(A/'PREDICTIONS.json')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:rows=list(pool.map(extension,jobs))
    put('ROWS.json',rows)
    result=dict(experiment='GDT1012',status='NECESSARY_BANK_SEQUENCE_CHECKED',cases=len(rows),counts=dict(collections.Counter(r['status'] for r in rows)),sampled_extension_maps=sum(len(r['witnesses']) for r in rows),coherent_common_witness_settings=sum(v['status']=='COHERENT_COMMON_READING' for r in rows for w in r['witnesses'] for v in w['meaning_check'].get('variants',[])),meaning_unknowns=sum(w['meaning_check']['status']!='COMPLETE' for r in rows for w in r['witnesses']),confirmed_words=0,independent_meaning_capacity=0,significance=False)
    put('RESULT.json',result);put('EXECUTION_RECEIPT.json',dict(started_utc=started,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registration_commit=receipt['commit']))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['candidate','original_id','context','bank_grammar','saved_maps','coherent_common_settings','remaining_meaning_alternatives','independent_meaning_capacity'])
        for r in rows:w.writerow([r['id'],r['original_id'],r['context'],r['status'],len(r['witnesses']),sum(v['status']=='COHERENT_COMMON_READING' for x in r['witnesses'] for v in x['meaning_check'].get('variants',[])),'NONE_IF_VERIFIED' if r['status']=='UNSAT' else 'UNRESOLVED',0])
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
