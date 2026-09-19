"""Independent finite-frontier/ground and complete candidate-account validation."""
import collections,concurrent.futures,csv,gzip,hashlib,json,time
from pathlib import Path
from check_model import decide,ground
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
RECORDS=None;PAGES=None

def read(path):
    if str(path).endswith('.gz'):
        with gzip.open(path,'rt') as f:return json.load(f)
    return json.loads(Path(path).read_text())

def init(records,pages):
    global RECORDS,PAGES
    RECORDS=records;PAGES=pages

def check_local(row):
    if row['status']!='COMPLETE':return dict(id=row['id'],status='UNRESOLVED',counts={})
    ed=row['edition'];codes={'IRIS':row['iris_code'],'XIPHION':row['xiphion_code']};counts=collections.Counter()
    assert set(row['roles'])==set(RECORDS)
    for rid,rows in row['roles'].items():
        assert [x['page'] for x in rows]==list(PAGES[ed][rid])
        for answer in rows:
            p=PAGES[ed][rid][answer['page']];assert answer['physical_leaf']==p['physical_leaf']
            v=decide(RECORDS[rid],p['text'],codes,bounds=True)
            expected='PARTIAL_PREFIX_PARTITION' if v[0] else 'CONTRADICTED_PREFIX_PARTITION'
            assert (answer['status'],answer['failed_atom'],answer['reason'])==(expected,v[1],v[2]),(row['id'],rid,answer['page'])
            if v[0]:ground(RECORDS[rid],p['text'],codes,v[3])
            counts[expected]+=1
    return dict(id=row['id'],status='PASS',counts=dict(counts))

def main():
    start=time.monotonic();spec=read(E/'src/SPEC.json')
    for n,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
    source=read(R/spec['source']);records={r['id']:r['atoms'] for r in source['records']};domains=read(R/spec['domains']);base=read(R/spec['candidates']);previous=read(R/spec['previous'])
    pages={ed:{rid:{p['page']:p for p in pp} for rid,pp in d.items()} for ed,d in domains.items()}
    assert all(not p['page'].startswith('f84') and p['page']!='f116v' for d in domains.values() for pp in d.values() for p in pp)
    keys=sorted({(b['edition'],b['iris_code'],b['xiphion_code']) for b in base});ids={k:i for i,k in enumerate(keys)}
    inherited={i for i,p in enumerate(previous) if p['status']=='FOUR_ATOM_PROJECTION_CONTRADICTED'}
    active=collections.defaultdict(list)
    for i,b in enumerate(base):
        assert previous[i]['id']==i
        if i not in inherited:active[ids[b['edition'],b['iris_code'],b['xiphion_code']]].append(i)
    assert len(inherited)==4 and len(active)==1318 and len(base)==8990
    pred=list(csv.DictReader((A/'CASE_PREDICTIONS.tsv').open(),delimiter='\t'));assert len(pred)==8990
    for i,(p,b) in enumerate(zip(pred,base)):
        assert int(p['id'])==i and int(p['class_id'])==ids[b['edition'],b['iris_code'],b['xiphion_code']]
        for k in ['edition','iris_code','xiphion_code','iris_page','xiphion_page']:assert p[k]==b[k]
        assert p['prior_status']==previous[i]['status']
    sp=read(A/'SOURCE_PREDICTIONS.json')
    assert sp==[dict(record=rid,index=i,atom=a,obligation='EXACT_NAME_CODE' if a in ['IRIS','XIPHION'] else 'NONEMPTY_PREFIX_INCOMPARABLE_TO_BOTH_NAMES') for rid,atoms in records.items() for i,a in enumerate(atoms)]
    local=read(A/'LOCAL_RESULTS.json.gz');assert [r['id'] for r in local]==sorted(active)
    for row in local:
        if row['status']=='COMPLETE':assert (row['edition'],row['iris_code'],row['xiphion_code'])==keys[row['id']]
    with concurrent.futures.ProcessPoolExecutor(max_workers=spec['workers'],initializer=init,initargs=(records,pages)) as pool:checks=list(pool.map(check_local,local,chunksize=4))
    lc=collections.Counter()
    for c in checks:lc.update(c['counts'])
    classes=read(A/'CLASS_RESULTS.json.gz');assert len(classes)==len(keys)
    bylocal={r['id']:r for r in local};table=list(csv.DictReader((A/'CANDIDATE_TABLE.tsv').open(),delimiter='\t'));assert len(table)==8990
    cc=collections.Counter();surv=collections.Counter()
    for cid,c in enumerate(classes):
        assert c['id']==cid and (c['edition'],c['iris_code'],c['xiphion_code'])==keys[cid]
        assert c['active_rows']==len(active[cid])
        if cid not in bylocal:
            assert c['status']=='INHERITED_CLASS_EXCLUDED' and c['surviving_rows']==0;continue
        result=bylocal[cid];assert c['status']==result['status']
        expected={rid:[p['page'] for p in rr if p['status']=='PARTIAL_PREFIX_PARTITION'] for rid,rr in result['roles'].items()} if result['status']=='COMPLETE' else {}
        assert c['supports']==expected
    for i,(row,b) in enumerate(zip(table,base)):
        cid=ids[b['edition'],b['iris_code'],b['xiphion_code']];assert int(row['id'])==i and int(row['class_id'])==cid
        for k in ['edition','iris_code','xiphion_code','iris_page','xiphion_page']:assert row[k]==b[k]
        c=classes[cid];count=0
        if i in inherited:status='INHERITED_GDT977_CONTRADICTION'
        elif c['status']!='COMPLETE':status='UNKNOWN_'+c['status']
        else:
            sup=c['supports'];ed=b['edition']
            if b['iris_page'] not in sup['I.1']:status='CONTRADICTED_I_1_PREFIX_PARTITION'
            elif b['xiphion_page'] not in sup['IV.20']:status='CONTRADICTED_IV_20_PREFIX_PARTITION'
            else:
                used={pages[ed]['I.1'][b['iris_page']]['physical_leaf'],pages[ed]['IV.20'][b['xiphion_page']]['physical_leaf']}
                counts3=collections.Counter(pages[ed]['I.3'][p]['physical_leaf'] for p in sup['I.3'] if pages[ed]['I.3'][p]['physical_leaf'] not in used)
                total3=sum(counts3.values())
                for p in sup['I.2']:
                    leaf=pages[ed]['I.2'][p]['physical_leaf']
                    if leaf not in used:count+=total3-counts3[leaf]
                status='PARTIAL_PREFIX_COMPATIBLE' if count else 'CONTRADICTED_NO_FOUR_LEAF_COMPLETION'
        assert row['status']==status and int(row['four_leaf_completions'])==count,(i,row,status,count)
        cc[status]+=1
        if count:surv[cid]+=1
    for c in classes:assert c['surviving_rows']==surv[c['id']]
    class_table=list(csv.DictReader((A/'NAME_CLASS_TABLE.tsv').open(),delimiter='\t'));assert len(class_table)==len(classes)
    for row,c in zip(class_table,classes):assert all(row[k]==str(c[k]) for k in row)
    ws=read(A/'BOUNDARY_WITNESSES.json.gz');assert {w['class_id'] for w in ws}==set(surv) and len(ws)==len(surv)
    for w in ws:
        c=classes[w['class_id']];b=base[w['base_id']];ed=w['edition'];assert w['non_name_codes_not_shared'] is True
        assert w['codes']=={'IRIS':c['iris_code'],'XIPHION':c['xiphion_code']}
        assert table[w['base_id']]['status']=='PARTIAL_PREFIX_COMPATIBLE'
        assert w['records']['I.1']['page']==b['iris_page'] and w['records']['IV.20']['page']==b['xiphion_page']
        assert len({r['physical_leaf'] for r in w['records'].values()})==4
        for rid,part in w['records'].items():
            assert part['page'] in c['supports'][rid];p=pages[ed][rid][part['page']];assert p['physical_leaf']==part['physical_leaf']
            ground(records[rid],p['text'],w['codes'],part['boundaries'])
    out=read(A/'RESULT.json');assert out['candidate_counts']==dict(cc) and out['local_counts']==dict(lc)
    assert out['class_counts']==dict(collections.Counter(c['status'] for c in classes))
    assert out['surviving_rows']==cc['PARTIAL_PREFIX_COMPATIBLE'] and out['surviving_classes']==len(surv)
    fraction=out['surviving_rows']/8986;assert out['retention_fraction']==fraction
    unknown=sum(v for k,v in cc.items() if k.startswith('UNKNOWN_'))
    expected='INCOMPLETE_COMPUTATION' if unknown else 'NO_LITERAL_FULL_CODE_POSSIBLE' if not out['surviving_rows'] else 'PREFIX_PROJECTION_WEAK' if fraction>=0.9 else 'PREFIX_COMPATIBLE_PARTIAL_CANDIDATES'
    assert out['status']==expected and out['original_candidates']==8990 and out['active_candidates']==8986 and out['inherited_exclusions']==4
    assert out['source_occurrences']==613 and out['non_name_occurrences']==607 and out['full_code_found'] is False
    assert out['confirmed_words']==out['independent_confirmation']==0
    result=dict(status='PASS',local_cases_checked=sum(lc.values()),local_counts=dict(lc),candidate_rows=8990,class_rows=len(classes),complete_boundary_examples=len(ws),unresolved_classes=sum(c['status']=='UNRESOLVED' for c in checks),elapsed_seconds=time.monotonic()-start,scope='Independent finite-frontier calculation and ground partitions, same author; no semantic confirmation.')
    (A/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
