import collections,concurrent.futures,csv,datetime,hashlib,importlib.util,json,subprocess,time
from pathlib import Path
from core import endpoints,relaxed_path,shared_path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def task(args):
    row,words,lex,grammar,spec,variants=args
    row['endpoints']=endpoints(words,lex,grammar)
    if not row['endpoints']['pass_']:row['status']='CONTRADICTED_ENDPOINT_SCOPE';return row
    relaxed,_=relaxed_path(words,lex,grammar);row['relaxed']=relaxed
    if not relaxed['feasible']:row['status']='CONTRADICTED_RELAXED_FULL_GRAMMAR';return row
    shared=shared_path(words,lex,grammar,spec['shared_search_state_limit'],spec['shared_search_seconds']);row['shared']=shared
    if shared['status']!='SHARED_SAT':row['status']='CONTRADICTED_SHARED_ALIAS' if shared['status']=='SHARED_UNSAT' else shared['status'];return row
    model=load(R/spec['model'],'fixed993');cases=[]
    for old in variants:
        case=dict(variant_id=old['id'],variant=old['variant'])
        try:
            program=model.compile_reading(shared['parse'],old['variant']);paths=model.execute(program,old['variant']);case.update(program=program,paths=paths,status='COHERENT_WITNESS' if any(p['consistent'] for p in paths) else 'WITNESS_SEMANTIC_CONTRADICTION')
        except ValueError as ex:case.update(status='WITNESS_BINDING_CONTRADICTION',error=str(ex),paths=[])
        cases.append(case)
    row['cases']=cases;row['status']='COHERENT_LOCAL_EXTENSION' if any(c['status']=='COHERENT_WITNESS' for c in cases) else 'SYNTACTIC_EXTENSION_SEMANTICS_UNRESOLVED'
    return row

def main():
    for n,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    receipt=read(A/'PUBLIC_REGISTRATION.json');assert subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],cwd=R).returncode==0
    spec=read(E/'src/SPEC.json');grammar=read(R/spec['grammar']);lex={r['raw']:r['symbol'] for r in read(R/spec['source_draft'])['lexicon']};src=read(R/spec['source_paragraphs'])
    variants=[c for c in read(R/spec['old_cases']) if c['id'] in spec['retained_variants']];assert [c['id'] for c in variants]==spec['retained_variants']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();jobs=[];pred=[]
    for ed,ps in src.items():
        for p in ps:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            words=[w for l in p['lines'] for w in l['words']];ids=[x for l in p['lines'] for x in l['source_ids']];assert len(words)==len(ids)==p['groups']
            part='ORIGINAL_PARAGRAPH' if p['id']=='f83r|f83r.18-f83r.24' else 'OTHER_SAME_LEAF' if p['leaf']==83 else 'OTHER_EXPOSED_LEAF'
            row=dict(id=ed+'|'+p['id'],edition=ed,paragraph=p['id'],page=p['page'],leaf=p['leaf'],partition=part,groups=len(words),known_groups=sum(w in lex for w in words),unknown_types=sorted(set(words)-lex.keys()),strict_anchor_eligible=all(l['anchor_eligible'] for l in p['lines']),source_ids=ids,independent_meaning_capacity=0)
            pred.append(dict(id=row['id'],partition=part,groups=len(words),required_first=grammar['patterns']['INITIAL'],required_last=grammar['patterns']['CONCLUSION'],required_once=spec['required'],known_values=[dict(position=i+1,raw=w,symbol=lex[w]) for i,w in enumerate(words) if w in lex],unknown_types=row['unknown_types'],prediction='FULL_COVERAGE_SHARED_ALIAS_WITH_FIXED_GRAMMAR'))
            jobs.append((row,words,lex,grammar,spec,variants))
    assert len(jobs)==1349
    write(A/'PREDICTIONS.json',pred)
    with concurrent.futures.ProcessPoolExecutor(max_workers=spec['worker_count']) as pool:
        rows=list(pool.map(task,jobs,timeout=spec['whole_run_seconds']))
    write(A/'ROWS.json',rows)
    additional=[r['id'] for r in rows if r['partition']!='ORIGINAL_PARAGRAPH' and r['status']=='COHERENT_LOCAL_EXTENSION']
    syntactic=[r['id'] for r in rows if r['partition']!='ORIGINAL_PARAGRAPH' and r['status']=='SYNTACTIC_EXTENSION_SEMANTICS_UNRESOLVED']
    unresolved=[r['id'] for r in rows if r['status'].startswith('UNKNOWN')]
    result=dict(status='COMPLETE_FINITE_CAPACITY_RUN',started_utc=started,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registration_commit=receipt['commit'],paragraphs=len(rows),status_counts=dict(collections.Counter(r['status'] for r in rows)),readers={},partitions={},additional_coherent_witnesses=additional,additional_syntactic_only=syntactic,unresolved=unresolved,claims=spec['claims'])
    for ed,ps in src.items():
        rs=[r for r in rows if r['edition']==ed];result['readers'][ed]=dict(paragraphs=len(ps),physical_leaves=len({r['leaf'] for r in rs}),counts=dict(collections.Counter(r['status'] for r in rs)))
    for part in ('ORIGINAL_PARAGRAPH','OTHER_SAME_LEAF','OTHER_EXPOSED_LEAF'):
        rs=[r for r in rows if r['partition']==part];result['partitions'][part]=dict(paragraphs=len(rs),physical_leaves=len({r['leaf'] for r in rs}),counts=dict(collections.Counter(r['status'] for r in rs)))
    result['decision']='RETAIN_COMPLETE_EXPOSED_EXTENSION' if additional else 'RETAIN_UNRESOLVED_COMPLETION_CAPACITY' if syntactic or unresolved else 'NO_ADDITIONAL_FINITE_ALIAS_EXTENSION'
    write(A/'RESULT.json',result)
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        fields=['id','partition','groups','known_groups','unknown_types','strict_anchor_eligible','status','endpoint_conflicts','new_aliases','coherent_variants','independent_meaning_capacity'];w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader()
        for r in rows:
            w.writerow({**{k:r[k] for k in fields if k in r},'unknown_types':len(r['unknown_types']),'endpoint_conflicts':len(r['endpoints']['conflicts']),'new_aliases':len(r.get('shared',{}).get('aliases',{})),'coherent_variants':sum(c['status']=='COHERENT_WITNESS' for c in r.get('cases',[]))})
    print(json.dumps(result))
if __name__=='__main__':main()
