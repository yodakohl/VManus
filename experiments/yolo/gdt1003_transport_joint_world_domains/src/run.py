import argparse,collections,concurrent.futures,csv,datetime,hashlib,importlib.util,json,time
from pathlib import Path
import z3
from world import build,witness,vals
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def prepare(cfg):
    panel=read(R/cfg['source_panel']);systems=read(R/cfg['source_systems']);lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']};g=read(R/cfg['grammar']);symbols=sorted(set(lex.values())|{v for pat in g['patterns'].values() for t in pat for v in vals(g,t)})
    out=[]
    for old in systems:
        if old['id'] not in cfg['systems']:continue
        ps=[panel[i] for i in old['indices']];counts=collections.Counter(w for p in ps for w in set(p['words'])-lex.keys());shared=sorted(w for w,n in counts.items() if n>1);assert shared==old['shared_unknown_words']
        queries=[dict(id='EXISTS')]+[dict(id=w+'='+v,word=w,value=v) for w in shared for v in symbols]
        out.append(dict(id=old['id'],paragraphs=ps,shared_words=shared,queries=queries,prediction='EXISTING_SEMANTICS_AND_ONE_CODE_MUST_HOLD_FOR_BOTH_COMPLETE_PARAGRAPHS',independent_meaning_capacity=0))
    assert [x['id'] for x in out]==cfg['systems'];put('PREDICTIONS.json',out);print(json.dumps(dict(systems=len(out),terminals=len(symbols),queries=sum(len(x['queries']) for x in out))))

def task(job):
    pred,cfg,g,lex=job;started=time.monotonic();deadline=started+cfg['worker_seconds'];b=build(pred['paragraphs'],lex,g,cfg['query_milliseconds']);model=load(R/cfg['model'],'frozen993');answers=[];tuples=[];projection=dict(exhaustive=False,status='NOT_STARTED')
    def query():
        remaining=deadline-time.monotonic()
        if remaining<=0:return 'unknown_batch_limit'
        b['solver'].set(timeout=max(1,min(cfg['query_milliseconds'],int(remaining*1000))));return str(b['solver'].check())
    def save_witness(all_variants=False):
        w=witness(b);replays=[]
        for p,parsed in zip(pred['paragraphs'],w['parses']):
            program=model.compile_reading(parsed,w['variant']);paths=model.execute(program,w['variant']);assert any(t['consistent'] for t in paths),(p['id'],w)
            replays.append(dict(id=p['id'],program=program,paths=paths))
        w['replays']=replays
        if all_variants:
            w['variant_checks']=[]
            old=read(R/cfg['old_cases'])
            for v in [x for x in old if x['id'] in cfg['retained_variants']]:
                cases=[]
                for p,parsed in zip(pred['paragraphs'],w['parses']):
                    try:
                        program=model.compile_reading(parsed,v['variant']);paths=model.execute(program,v['variant']);cases.append(dict(id=p['id'],program=program,paths=paths,status='COHERENT' if any(t['consistent'] for t in paths) else 'CONTRADICTED'))
                    except ValueError as ex:cases.append(dict(id=p['id'],status='BINDING_CONTRADICTION',error=str(ex),paths=[]))
                w['variant_checks'].append(dict(variant_id=v['id'],variant=v['variant'],paragraphs=cases,joint_coherent=all(c['status']=='COHERENT' for c in cases)))
        return w
    for q in pred['queries']:
        b['solver'].push()
        if 'word' in q:b['solver'].add(b['xs'][q['word']]==b['num'][q['value']])
        status=query();row=dict(**q,status=status)
        if status=='sat':row['witness']=save_witness()
        answers.append(row);b['solver'].pop()
    for _ in range(cfg['tuple_limit']):
        status=query()
        if status!='sat':projection=dict(exhaustive=status=='unsat',status=status);break
        w=save_witness(True);values={word:w['aliases'][word] for word in pred['shared_words']};tuples.append(dict(values=values,witness=w));b['solver'].add(z3.Or([b['xs'][word]!=b['num'][val] for word,val in values.items()]))
    else:projection=dict(exhaustive=False,status='TUPLE_LIMIT')
    domains={word:{status:[q['value'] for q in answers if q.get('word')==word and q['status']==status] for status in sorted(set(q['status'] for q in answers if q.get('word')==word))} for word in pred['shared_words']}
    return dict(id=pred['id'],answers=answers,domains=domains,tuples=tuples,projection=projection,wall_seconds=time.monotonic()-started,confirmed_words=0,full_dictionary_uniqueness='NOT_EXHAUSTED')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');args=ap.parse_args();cfg=read(E/'src/SPEC.json')
    if args.prepare:prepare(cfg);return
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    predictions=read(A/'PREDICTIONS.json');g=read(R/cfg['grammar']);lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']};started=datetime.datetime.now(datetime.timezone.utc).isoformat();tm=time.monotonic()
    with concurrent.futures.ProcessPoolExecutor(max_workers=cfg['workers']) as pool:rows=list(pool.map(task,[(p,cfg,g,lex) for p in predictions]))
    put('ROWS.json',rows)
    result=dict(status='JOINT_WORLD_DOMAINS_AUDITED',systems=[dict(id=r['id'],existence=r['answers'][0]['status'],query_counts=dict(collections.Counter(q['status'] for q in r['answers'])),domains=r['domains'],projected_tuples=len(r['tuples']),projection=r['projection']) for r in rows],queries=sum(len(r['answers']) for r in rows),confirmed_words=0,independent_meaning_capacity=0,significance=False,reserve_accesses=0)
    put('RESULT.json',result);put('EXECUTION_RECEIPT.json',dict(started_utc=started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=time.monotonic()-tm,z3_version=z3.get_version_string()))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['system','query','word','value','status','complete_witness','independent_meaning_capacity'])
        for r in rows:
            for q in r['answers']:w.writerow([r['id'],q['id'],q.get('word',''),q.get('value',''),q['status'],'witness' in q,0])
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
