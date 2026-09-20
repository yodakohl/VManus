from common import *
from evaluate import maps,evaluate
from worker import bounded
import collections,concurrent.futures,csv,subprocess
import layout_solver,layout_independent

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
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();p=read(A/'PANEL.json')[0];layouts=[x['layout'] for x in read(A/'LAYOUTS.json')]
    one=layout_solver.solve([p],{},g,timeout=s['layout_proof_milliseconds'],witness_limit=1,blocked_layouts=layouts)
    two=layout_independent.check([p],{},g,timeout=s['layout_proof_milliseconds'],blocked_layouts=layouts)
    coverage=dict(primary=one,independent=two,complete=one['status']=='UNSAT' and two['status']=='unsat');put('COVERAGE.json',coverage)
    if not coverage['complete']:
        put('RESULT.json',dict(status='STOP_LAYOUT_COVERAGE_UNPROVED',coverage=False,confirmed_words=0));return
    candidates=list(maps());assert len(candidates)==1800
    with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:originals=list(pool.map(evaluate,candidates,chunksize=10))
    put('ORIGINAL_ROWS.json',originals);valid=[r for r in originals if r['valid_variants']]
    print(json.dumps(dict(original_maps=len(originals),valid_maps=len(valid),valid_map_settings=sum(len(r['valid_variants']) for r in valid))),flush=True)
    jobs=[]
    for candidate in valid:
        for context in range(1,5):jobs.append(dict(id=candidate['id']+'_P'+str(context),original=candidate,context_index=context))
    put('EXTENSION_PREDICTIONS.json',[dict(id=j['id'],original_id=j['original']['id'],context_index=j['context_index'],valid_variants=j['original']['valid_variants']) for j in jobs])
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:rows=list(pool.map(extension,jobs))
    put('ROWS.json',rows)
    result=dict(experiment='GDT1011',status='COMPLETE_FACTORED_CONTENT_AUDIT',coverage=True,original_maps=len(originals),original_unique_codes=len({json.dumps(r['code'],sort_keys=True) for r in originals}),original_setting_checks=1800*32,source_valid_maps=len(valid),source_valid_map_settings=sum(len(r['valid_variants']) for r in valid),source_valid_bijective_maps=sum(r['bijective'] for r in valid),source_valid_layouts=sorted({r['layout'] for r in valid}),extension_cases=len(rows),extension_counts=dict(collections.Counter(r['status'] for r in rows)),sampled_extension_maps=sum(len(r['witnesses']) for r in rows),coherent_common_witness_settings=sum(v['status']=='COHERENT_COMMON_READING' for r in rows for w in r['witnesses'] for v in w['meaning_check'].get('variants',[])),meaning_unknowns=sum(w['meaning_check']['status']!='COMPLETE' for r in rows for w in r['witnesses']),confirmed_words=0,independent_meaning_capacity=0,significance=False)
    put('RESULT.json',result);put('EXECUTION_RECEIPT.json',dict(started_utc=started,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registration_commit=receipt['commit']))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['candidate','layout','bijective','valid_variants','source_status','independent_meaning_capacity'])
        for r in originals:w.writerow([r['id'],r['layout'],r['bijective'],','.join(map(str,r['valid_variants'])),'SOURCE_VALID' if r['valid_variants'] else 'CONTRADICTED',0])
    with (A/'EXTENSIONS.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['candidate','original_id','context','grammar','saved_maps','coherent_common_settings','remaining_meaning_alternatives','independent_meaning_capacity'])
        for r in rows:w.writerow([r['id'],r['original_id'],r['context'],r['status'],len(r['witnesses']),sum(v['status']=='COHERENT_COMMON_READING' for x in r['witnesses'] for v in x['meaning_check'].get('variants',[])),'NONE_IF_VERIFIED' if r['status']=='UNSAT' else 'UNRESOLVED',0])
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
