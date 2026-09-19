"""All fixed name-code classes, entire non-name remainder, all source pages."""
import collections,concurrent.futures,csv,gzip,hashlib,json,multiprocessing,time
from pathlib import Path
from model import segment
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
RECORDS=None;DOMAINS=None

def load(path):
    if str(path).endswith('.gz'):
        with gzip.open(path,'rt') as f:return json.load(f)
    return json.loads(Path(path).read_text())

def save(n,obj):
    b=(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    if n.endswith('.gz'):
        with gzip.GzipFile(filename=str(A/n),mode='wb',mtime=0) as f:f.write(b)
    else:(A/n).write_bytes(b)

def table(n,rows,fields):
    with (A/n).open('w') as f:
        w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def initialize(records,domains):
    global RECORDS,DOMAINS
    RECORDS=records;DOMAINS=domains

def work(job):
    cid,ed,iris,xiphion=job;codes={'IRIS':iris,'XIPHION':xiphion};out={}
    for rid,atoms in RECORDS.items():
        out[rid]=[]
        for page in DOMAINS[ed][rid]:
            answer=segment(atoms,page['text'],codes)
            out[rid].append(dict(page=page['page'],physical_leaf=page['physical_leaf'],**answer))
    return dict(id=cid,status='COMPLETE',edition=ed,iris_code=iris,xiphion_code=xiphion,roles=out)

def main():
    for n,h in load(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    assert (A/'EXECUTION_RECEIPT.json').exists()
    spec=load(E/'src/SPEC.json');src=load(R/spec['source']);records={r['id']:r['atoms'] for r in src['records']};domains=load(R/spec['domains']);base=load(R/spec['candidates']);old=load(R/spec['previous'])
    assert len(base)==len(old)==spec['expected_candidates']
    assert all(not p['page'].startswith('f84') and p['page']!='f116v' for d in domains.values() for pp in d.values() for p in pp)
    keys=sorted({(b['edition'],b['iris_code'],b['xiphion_code']) for b in base});classid={k:i for i,k in enumerate(keys)}
    active=collections.defaultdict(list);inherited=[]
    for i,(b,previous) in enumerate(zip(base,old)):
        assert previous['id']==i
        if previous['status']=='FOUR_ATOM_PROJECTION_CONTRADICTED':inherited.append(i)
        else:
            assert previous['status']=='PARTIAL_FOUR_ATOM_WITNESS'
            active[classid[b['edition'],b['iris_code'],b['xiphion_code']]].append(i)
    assert len(inherited)==spec['expected_inherited_failures'] and len(active)==spec['expected_active_classes']
    predictions=[dict(id=i,class_id=classid[b['edition'],b['iris_code'],b['xiphion_code']],edition=b['edition'],iris_code=b['iris_code'],xiphion_code=b['xiphion_code'],iris_page=b['iris_page'],xiphion_page=b['xiphion_page'],prior_status=old[i]['status']) for i,b in enumerate(base)]
    table('CASE_PREDICTIONS.tsv',predictions,list(predictions[0]))
    source_predictions=[dict(record=rid,index=i,atom=a,obligation='EXACT_NAME_CODE' if a in ['IRIS','XIPHION'] else 'NONEMPTY_PREFIX_INCOMPARABLE_TO_BOTH_NAMES') for rid,atoms in records.items() for i,a in enumerate(atoms)]
    save('SOURCE_PREDICTIONS.json',source_predictions)
    started=time.monotonic();results={};pool=concurrent.futures.ProcessPoolExecutor(max_workers=spec['workers'],initializer=initialize,initargs=(records,domains))
    futures={pool.submit(work,(cid,*keys[cid])):cid for cid in active}
    expired=False
    try:
        for future in concurrent.futures.as_completed(futures,timeout=spec['execution_wall_seconds']):
            cid=futures[future]
            try:results[cid]=future.result()
            except Exception as e:results[cid]=dict(id=cid,status='ERROR',error_type=type(e).__name__)
            if len(results)%100==0:print('Completed classes',len(results),'of',len(active),flush=True)
    except concurrent.futures.TimeoutError:expired=True
    finally:
        if expired:
            for p in multiprocessing.active_children():p.terminate()
        pool.shutdown(wait=True,cancel_futures=True)
    for cid in active:
        if cid not in results:results[cid]=dict(id=cid,status='UNKNOWN_EXECUTION_WALL')
    allclasses=[];cases=[];witnesses=[];localcounts=collections.Counter()
    lookup={ed:{rid:{p['page']:p for p in pp} for rid,pp in d.items()} for ed,d in domains.items()}
    for cid,key in enumerate(keys):
        ed,ic,xc=key
        if cid not in active:
            allclasses.append(dict(id=cid,edition=ed,iris_code=ic,xiphion_code=xc,status='INHERITED_CLASS_EXCLUDED',active_rows=0,surviving_rows=0));continue
        result=results[cid];supports={};statuses={}
        if result['status']=='COMPLETE':
            for rid,rr in result['roles'].items():
                localcounts.update(r['status'] for r in rr)
                supports[rid]=[r['page'] for r in rr if r['status']=='PARTIAL_PREFIX_PARTITION']
                statuses[rid]={r['page']:r for r in rr}
        surviving=0;example=None
        for i in active[cid]:
            b=base[i];status='UNKNOWN_'+result['status'];count=0;sample=None
            if result['status']=='COMPLETE':
                first=b['iris_page'];fourth=b['xiphion_page']
                if first not in supports['I.1']:status='CONTRADICTED_I_1_PREFIX_PARTITION'
                elif fourth not in supports['IV.20']:status='CONTRADICTED_IV_20_PREFIX_PARTITION'
                else:
                    used={lookup[ed]['I.1'][first]['physical_leaf'],lookup[ed]['IV.20'][fourth]['physical_leaf']};assert len(used)==2
                    for second in supports['I.2']:
                        lf=lookup[ed]['I.2'][second]['physical_leaf']
                        if lf in used:continue
                        for third in supports['I.3']:
                            lf3=lookup[ed]['I.3'][third]['physical_leaf']
                            if lf3 in used or lf3==lf:continue
                            count+=1
                            if sample is None:sample={'I.1':first,'I.2':second,'I.3':third,'IV.20':fourth}
                    assert count<=b['four_page_assignments']
                    status='PARTIAL_PREFIX_COMPATIBLE' if count else 'CONTRADICTED_NO_FOUR_LEAF_COMPLETION'
                    if count:
                        surviving+=1
                        if example is None:example=(i,sample)
            cases.append(dict(id=i,class_id=cid,edition=ed,iris_page=b['iris_page'],xiphion_page=b['xiphion_page'],iris_code=ic,xiphion_code=xc,status=status,four_leaf_completions=count))
        allclasses.append(dict(id=cid,edition=ed,iris_code=ic,xiphion_code=xc,status=result['status'],active_rows=len(active[cid]),surviving_rows=surviving,supports=supports))
        if example:
            i,assignment=example;codes={'IRIS':ic,'XIPHION':xc};ww={}
            for rid,page in assignment.items():
                p=lookup[ed][rid][page];answer=segment(records[rid],p['text'],codes,witness=True);assert answer['status']=='PARTIAL_PREFIX_PARTITION'
                ww[rid]=dict(page=page,physical_leaf=p['physical_leaf'],boundaries=answer['boundaries'])
            witnesses.append(dict(class_id=cid,base_id=i,edition=ed,codes=codes,records=ww,non_name_codes_not_shared=True))
    for i in inherited:
        b=base[i];cases.append(dict(id=i,class_id=classid[b['edition'],b['iris_code'],b['xiphion_code']],edition=b['edition'],iris_page=b['iris_page'],xiphion_page=b['xiphion_page'],iris_code=b['iris_code'],xiphion_code=b['xiphion_code'],status='INHERITED_GDT977_CONTRADICTION',four_leaf_completions=0))
    cases.sort(key=lambda r:r['id']);counts=collections.Counter(c['status'] for c in cases);survivors=counts['PARTIAL_PREFIX_COMPATIBLE'];unknown=sum(v for k,v in counts.items() if k.startswith('UNKNOWN_'))
    fraction=survivors/(len(base)-len(inherited));status='INCOMPLETE_COMPUTATION' if unknown else 'NO_LITERAL_FULL_CODE_POSSIBLE' if not survivors else 'PREFIX_PROJECTION_WEAK' if fraction>=spec['stop_retention_fraction'] else 'PREFIX_COMPATIBLE_PARTIAL_CANDIDATES'
    save('LOCAL_RESULTS.json.gz',[results[cid] for cid in sorted(results)]);save('CLASS_RESULTS.json.gz',allclasses);save('BOUNDARY_WITNESSES.json.gz',witnesses)
    table('CANDIDATE_TABLE.tsv',cases,list(cases[0]))
    class_table=[{k:c[k] for k in ['id','edition','iris_code','xiphion_code','status','active_rows','surviving_rows']} for c in allclasses]
    table('NAME_CLASS_TABLE.tsv',class_table,list(class_table[0]))
    out=dict(status=status,original_candidates=len(base),active_candidates=len(base)-len(inherited),inherited_exclusions=len(inherited),candidate_counts=dict(counts),class_counts=dict(collections.Counter(c['status'] for c in allclasses)),local_counts=dict(localcounts),surviving_rows=survivors,surviving_classes=sum(c['surviving_rows']>0 for c in allclasses),retention_fraction=fraction,source_occurrences=len(source_predictions),non_name_occurrences=sum(x['obligation'].startswith('NONEMPTY') for x in source_predictions),elapsed_seconds=time.monotonic()-started,full_code_found=False,confirmed_words=0,independent_confirmation=0)
    save('RESULT.json',out);print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':main()
