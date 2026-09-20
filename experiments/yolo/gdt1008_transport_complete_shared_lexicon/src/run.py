from common import *
import collections,concurrent.futures,csv,itertools,subprocess
import solver

def meanings(witness,s,g,independent=False):
    out=[]
    for vi,values in enumerate(itertools.product(*g['variants'].values())):
        variant=dict(zip(g['variants'],values));details=[replay(p,variant,s,independent) for p in witness['parses']]
        original=details[0]
        content=original.get('status')=='COHERENT' and len(original['cargo'])==3 and len(original['hazards'])==2 and any(p['consistent'] and len(p['trace'])==8 for p in original['paths'])
        coherent=content and all(p['status']=='COHERENT' for p in details[1:])
        out.append(dict(variant_index=vi,variant=variant,status='COHERENT_COMMON_READING' if coherent else 'SAMPLE_CONTRADICTION',original_full_content=bool(content),paragraphs=details))
    return out

def task(job):
    s,g=inputs();panel=read(A/'PANEL.json');ps=[panel[i] for i in job['system']];start=time.monotonic()
    result=solver.solve(ps,{},g,timeout=s['query_milliseconds'],witness_limit=s['witness_limit'],family=job['family'])
    for w in result['witnesses']:w['meaning_variants']=meanings(w,s,g)
    return dict(**job,**result,wall_seconds=time.monotonic()-start)

def main():
    checklock();s,g=inputs();receipt=read(A/'PUBLIC_REGISTRATION.json');subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],check=True,cwd=R)
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();jobs=read(A/'PREDICTIONS.json')
    with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:rows=list(pool.map(task,jobs))
    put('ROWS.json',rows)
    result=dict(experiment='GDT1008',status='COMPLETE_SHARED_GRAMMAR_AUDIT',systems=len(rows),counts=dict(collections.Counter(r['status'] for r in rows)),sampled_maps=sum(len(r['witnesses']) for r in rows),coherent_common_witness_variants=sum(v['status']=='COHERENT_COMMON_READING' for r in rows for w in r['witnesses'] for v in w['meaning_variants']),semantic_map_space_exhausted=False,confirmed_words=0,independent_meaning_capacity=0,significance=False)
    put('RESULT.json',result);put('EXECUTION_RECEIPT.json',dict(started_utc=start,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registration_commit=receipt['commit']))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['system','family','complete_paragraphs','shared_words','status','sampled_maps','common_coherent_variants','remaining_semantic_alternatives','independent_meaning_capacity'])
        for r in rows:w.writerow([r['id'],r['family'],';'.join(r['paragraph_ids']),','.join(r['all_shared_words']),r['status'],len(r['witnesses']),sum(v['status']=='COHERENT_COMMON_READING' for x in r['witnesses'] for v in x['meaning_variants']),'NONE_BY_GRAMMAR' if r['status']=='UNSAT' else 'UNRESOLVED',0])
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
