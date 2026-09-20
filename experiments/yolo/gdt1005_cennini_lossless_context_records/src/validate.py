#!/usr/bin/env python3
"""Independent complete census, reverse packing/capacity and code-string inverse."""
import collections,concurrent.futures,csv,hashlib,itertools,json,re
from pathlib import Path
from independent import FIELDS,bound_check,decode
from run import isolated
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(n,x):(A/n).write_text(json.dumps(x,separators=(',',':'))+'\n')
def main():
    lock=read(E/'PREREG_LOCK.json')
    for path,h in lock['files'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
    s=read(E/'src/SPEC.json');source=read(R/s['source_facts']);records=[{k:r[k] for k in FIELDS} for r in source['records']]
    ps=read(R/s['input']);bundles=read(A/'BUNDLES.json');cases=read(A/'CASES.json');result=read(A/'RESULT.json');pred=read(A/'PREDICTIONS.json')
    # Reconstruct each registered full atom prediction directly from field differences.
    for writer,v in pred.items():
        assert len(v['streams'])==120
        for oi,order in enumerate(itertools.permutations(FIELDS)):
            tokens=[];ends=[];previous={}
            for r in records:
                flags={k:(writer=='FULL' or r[k]!=previous.get(k)) for k in FIELDS}
                if writer=='DELTA':tokens+=['M:'+''.join('1' if flags[k] else '0' for k in FIELDS)]
                tokens+=['V:'+r[k] for k in order if flags[k]];ends.append(len(tokens));previous=dict(r)
            row=v['streams'][oi];assert row['fields']==list(order) and row['order']==oi
            assert [v['dictionary'][i] for i in row['atoms']]==tokens and v['record_ends']==ends
    expected=[]
    for ed,parts in ps.items():
        pages=sorted(set(p['page'] for p in parts))
        for page in pages:
            pageparts=sorted([p for p in parts if p['page']==page],key=lambda p:p['lines'][0]['row'])
            for size in (1,2,3,4):
                expected.extend((ed,pageparts[i:i+size]) for i in range(len(pageparts)-size+1))
    assert len(expected)==len(bundles)==result['bundles'] and len(cases)==2*len(bundles)==result['cases']
    pending=[];witnesses=[];bounds=collections.Counter();nextcase=0
    for bi,((ed,parts),b) in enumerate(zip(expected,bundles)):
        assert b['bundle']==bi and b['edition']==ed and b['paragraphs']==[p['id'] for p in parts]
        assert b['page']==parts[0]['page'] and b['leaf']==parts[0]['leaf'] and not b['page'].startswith('f84') and b['page']!='f116v'
        words=sum([line['words'] for p in parts for line in p['lines']],[])
        assert words==b['words'] and len(words)==b['groups'] and sum(map(len,words))==b['characters']
        assert [p['groups'] for p in parts]==b['paragraph_groups']
        gaps=[j for j in range(len(parts)-1) if int(parts[j]['lines'][-1]['locus'].split('.')[-1])+1!=int(parts[j+1]['lines'][0]['locus'].split('.')[-1])]
        literal=all(l['anchor_eligible'] for p in parts for l in p['lines']) and all(re.fullmatch('[a-z]+',w) for w in words)
        assert b['literal']==literal and b['gaps']==gaps
        for writer in ('FULL','DELTA'):
            c=cases[nextcase];assert c['case']==nextcase and c['bundle']==bi and c['writer']==writer and c['edition']==ed;nextcase+=1
            for k in ('page','leaf','groups','characters'):assert c[k]==b[k]
            status='UNKNOWN_GAP' if gaps else 'UNKNOWN_SOURCE' if not literal else bound_check(records,writer,words)
            if status!='EXACT_SEARCH_REQUIRED':assert c['status']==status;bounds[status]+=1;continue
            key=hashlib.sha256(json.dumps([ed,b['page'],b['paragraphs'],writer],separators=(',',':')).encode()).hexdigest();assert key==c['job_hash']
            pending.append((key,c['case'],dict(spec=s,records=source['records'],words=words,writer=writer)))
            for witness in c.get('codes',[]):
                decoded,owners=decode(words,writer,witness['fields'],witness['code']);assert decoded==records
                assert tuple(witness['fields'])==list(itertools.permutations(FIELDS))[witness['order']]
                witnesses.append(dict(case=c['case'],order=witness['order'],word_records=owners,code=witness['code']))
    pending.sort();selected=pending[:s['max_exact_jobs']]
    for _,i,_ in pending[s['max_exact_jobs']:]:assert cases[i]['status']=='UNKNOWN_JOB_CAP'
    independent=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:
        fs={pool.submit(isolated,j,True):i for _,i,j in selected}
        for f in concurrent.futures.as_completed(fs):
            i=fs[f];r=f.result();c=cases[i]
            if c['status']=='UNSAT_EXACT':assert r['status']!='SAT'
            if c['status']=='SAT':assert r['status']!='UNSAT_EXACT'
            for w in r.get('codes',[]):
                got,_=decode(bundles[c['bundle']]['words'],c['writer'],w['fields'],w['code']);assert got==records
            independent.append(dict(case=i,**r))
    counts=dict(collections.Counter(c['status'] for c in cases));assert counts==result['status_counts'] and len(witnesses)==result['saved_codes']
    assert len(pending)==result['exact_candidates'] and len(selected)==result['selected_exact_jobs']
    assert result['paragraph_counts']=={ed:len(rows) for ed,rows in ps.items()}
    assert result['source_records']==len(records) and result['source_value_types']==len({v for r in records for v in r.values()})
    for ed in ps:
        for writer in s['writers']:assert result['panels'][ed][writer]==dict(collections.Counter(c['status'] for c in cases if c['edition']==ed and c['writer']==writer))
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==len(cases)
    for t,c in zip(table,cases):
        for k in ('case','bundle','edition','page','leaf','writer','groups','characters','status'):assert t[k]==str(c[k])
        assert t['paragraphs']==';'.join(bundles[c['bundle']]['paragraphs']) and int(t['codes'])==len(c.get('codes',[])) and t['independent_meaning_capacity']=='0'
    independent.sort(key=lambda r:r['case']);put('INDEPENDENT_REPLAYS.json',independent);put('INVERSE_READINGS.json',witnesses)
    out=dict(status='PASS',bundles=len(bundles),cases_checked=len(cases),complete_predictions_checked=240,independently_checked_bound_or_source_statuses=dict(bounds),codes_decoded_from_actual_strings=len(witnesses),reverse_cases=len(independent),reverse_status_counts=dict(collections.Counter(r['status'] for r in independent)),unresolved_reverse_cases=sum(r['status'].startswith(('UNKNOWN','ERROR')) for r in independent),confirmed_words=0,independent_meaning_capacity=0,scope='Complete registered source record/code consequences, not an independent identification of source content or source interpretation.')
    put('VALIDATION.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
