"""Independent full query census, cvc5 flow worlds, and frozen bit witnesses."""
import argparse,collections,concurrent.futures,csv,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cvc5-python',default=sys.executable);args=ap.parse_args()
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    cfg=read(E/'src/SPEC.json');pred=read(A/'PREDICTIONS.json');rows=read(A/'ROWS.json');result=read(A/'RESULT.json');lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']};g=read(R/cfg['grammar']);panel=read(R/cfg['source_panel']);oldsystems=read(R/cfg['source_systems'])
    symbols=set(lex.values())
    for pat in g['patterns'].values():
        for t in pat:symbols.update(g['types'][t[1:]] if t.startswith('@') else [t])
    symbols=sorted(symbols);assert len(symbols)==47 and [p['id'] for p in pred]==[r['id'] for r in rows]==cfg['systems']
    bit=load(R/'experiments/yolo/gdt993_complete_transport_consequence_audit/src/validate.py','oldbit');binding=load(R/'experiments/yolo/gdt994_frozen_transport_whole_transfer/src/validate.py','oldbinding');variant_values=[x['variant'] for x in read(R/cfg['old_cases']) if x['id'] in cfg['retained_variants']]
    witnesses=0;semantic=0;jobs=[]
    def ground(w,ps):
        nonlocal witnesses,semantic
        witnesses+=1;assert w['variant'] in variant_values;assert set(w['aliases'])==set(t for p in ps for t in p['words'])-lex.keys();full={**lex,**w['aliases']}
        assert len(w['parses'])==len(ps)==len(w['replays'])
        for p,parsed,rec in zip(ps,w['parses'],w['replays']):
            cursor=0;kinds=[]
            for node in parsed:
                assert node['start']==cursor and node['end']==cursor+len(g['patterns'][node['kind']]);ss=[full[x] for x in p['words'][cursor:node['end']]];assert node['symbols']==ss
                for x,t in zip(ss,g['patterns'][node['kind']]):assert x in (g['types'][t[1:]] if t.startswith('@') else [t])
                cursor=node['end'];kinds.append(node['kind'])
            assert cursor==len(p['words']) and kinds[0]=='INITIAL' and kinds[-1]=='CONCLUSION' and 'PAIR' not in kinds and 'COPY' not in kinds
            assert all(kinds.count(k)==1 for k in ('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'))
            compare(parsed,w['variant'],p,rec,True)
        if 'variant_checks' in w:
            assert [r['variant'] for r in w['variant_checks']]==variant_values
            for vr in w['variant_checks']:
                for p,parsed,rec in zip(ps,w['parses'],vr['paragraphs']):compare(parsed,vr['variant'],p,rec,rec['status']=='COHERENT')
                assert vr['joint_coherent']==all(r['status']=='COHERENT' for r in vr['paragraphs'])
    def compare(parsed,v,p,rec,require):
        nonlocal semantic
        semantic+=1;assert rec['id']==p['id'];error=binding.binding_error(parsed,v)
        if error:assert not require and rec['status']=='BINDING_CONTRADICTION' and rec['error']==error;return
        paths,hazards,refs=bit.replay(parsed,v);named={x for n in parsed for x in n['symbols'] if x in ('W','G','C')}
        for path in paths:
            for st in [path,*path['trace']]:st['positions']={k:x for k,x in st['positions'].items() if k in named|{'M','B'}}
        assert paths==rec['paths'] and hazards==rec['program']['hazards'] and refs==rec['program']['references']
        assert any(t['consistent'] for t in paths)==require
    for p,row in zip(pred,rows):
        old=next(s for s in oldsystems if s['id']==p['id']);assert p['paragraphs']==[panel[i] for i in old['indices']]
        for src in p['paragraphs']:assert not src['page'].startswith('f84') and src['page']!='f116v' and 26<=len(src['words'])<38
        counts=collections.Counter(w for src in p['paragraphs'] for w in set(src['words'])-lex.keys());shared=sorted(w for w,n in counts.items() if n>1);assert shared==p['shared_words']
        queries=[dict(id='EXISTS')]+[dict(id=w+'='+v,word=w,value=v) for w in shared for v in symbols];assert p['queries']==queries and len(row['answers'])==len(queries)
        for q,answer in zip(queries,row['answers']):
            for k in q:assert q[k]==answer[k]
            assert answer['status'] in ('sat','unsat','unknown','unknown_batch_limit')
            if answer['status']=='sat':
                ground(answer['witness'],p['paragraphs'])
                if 'word' in q:assert answer['witness']['aliases'][q['word']]==q['value']
            else:assert 'witness' not in answer
        tuples=[]
        for t in row['tuples']:
            ground(t['witness'],p['paragraphs']);assert t['values']=={w:t['witness']['aliases'][w] for w in shared};tuples.append(t['values'])
        assert len(tuples)<=cfg['tuple_limit'] and len({json.dumps(t,sort_keys=True) for t in tuples})==len(tuples)
        domains={w:{status:[q['value'] for q in row['answers'] if q.get('word')==w and q['status']==status] for status in sorted(set(q['status'] for q in row['answers'] if q.get('word')==w))} for w in shared};assert domains==row['domains']
        qs=list(queries)
        if row['projection']['exhaustive']:assert row['projection']['status']=='unsat';qs.append(dict(id='TUPLE_EXHAUSTION',blocked_tuples=tuples))
        jobs.append((p['id'],dict(paragraphs=p['paragraphs'],lexicon=lex,grammar=g,queries=qs,timeout=cfg['query_milliseconds'],worker_seconds=cfg['worker_seconds'])))
    def independent(job):
        ident,data=job
        try:
            p=subprocess.run([args.cvc5_python,str(E/'src/independent.py')],input=json.dumps(data),text=True,capture_output=True,timeout=cfg['worker_seconds']+30,check=True)
            return dict(id=ident,**json.loads(p.stdout))
        except subprocess.TimeoutExpired:return dict(id=ident,error='EXTERNAL_LIMIT',queries=[dict(id=q['id'],status='unknown_batch_limit') for q in data['queries']])
    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg['workers']) as pool:checks=list(pool.map(independent,jobs))
    unsettled=[]
    for row,check,job in zip(rows,checks,jobs):
        assert [q['id'] for q in check['queries']]==[q['id'] for q in job[1]['queries']]
        for answer,other in zip(row['answers'],check['queries']):
            if answer['status']=='unsat':
                assert other['status']!='sat',(row['id'],answer['id'])
                if other['status']!='unsat':unsettled.append(dict(system=row['id'],query=answer['id'],kind='NEGATIVE_NOT_INDEPENDENTLY_SETTLED'))
            if answer['status']=='sat':assert other['status']!='unsat',(row['id'],answer['id'])
        if row['projection']['exhaustive']:
            other=check['queries'][-1];assert other['id']=='TUPLE_EXHAUSTION' and other['status']!='sat'
            if other['status']!='unsat':unsettled.append(dict(system=row['id'],query=other['id'],kind='PROJECTION_NOT_INDEPENDENTLY_SETTLED'))
    assert result['queries']==sum(len(r['answers']) for r in rows)==190
    for r,summary in zip(rows,result['systems']):
        assert summary==dict(id=r['id'],existence=r['answers'][0]['status'],query_counts=dict(collections.Counter(q['status'] for q in r['answers'])),domains=r['domains'],projected_tuples=len(r['tuples']),projection=r['projection'])
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==190
    for t,(r,q) in zip(table,[(r,q) for r in rows for q in r['answers']]):assert t['system']==r['id'] and t['query']==q['id'] and t['status']==q['status'] and t['complete_witness']==str('witness' in q)
    (A/'INDEPENDENT_QUERIES.json').write_text(json.dumps(checks,separators=(',',':'))+'\n')
    out=dict(status='PASS' if not unsettled else 'PASS_WITH_UNRESOLVED_NEGATIVE_CHECKS',queries_checked=190,witnesses_checked=witnesses,bit_replays_checked=semantic,unsettled=unsettled,independent_status_counts=dict(collections.Counter(q['status'] for c in checks for q in c['queries'])),scope='Independent finite world encoding and direct bit-execution; no source or word meaning confirmation',confirmed_words=0)
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
