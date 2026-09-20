import collections,concurrent.futures,csv,datetime,hashlib,json,time
from pathlib import Path
import z3
from grammar import build
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def put(n,x):(A/n).write_text(json.dumps(x,separators=(',',':'))+'\n')
def task(job):
 pred,cfg,g,lex=job;start=time.monotonic();b=build(pred['paragraphs'],lex,g,cfg['query_milliseconds']);s=b['solver'];answers=[];tuples=[]
 def check():
  left=cfg['worker_seconds']-(time.monotonic()-start)
  if left<=0:return 'unknown_batch_limit'
  s.set(timeout=max(1,min(cfg['query_milliseconds'],int(left*1000))));return str(s.check())
 def witness():
  m=s.model();aliases={w:b['terminals'][m.eval(x,model_completion=True).as_long()] for w,x in b['xs'].items()};full={**lex,**aliases};parses=[]
  for p,es,bs in zip(pred['paragraphs'],b['edges'],b['flags']):
   chosen=sorted(e for e,v in zip(es,bs) if z3.is_true(m.eval(v,model_completion=True)));parses.append([dict(start=lo,end=hi,kind=k,symbols=[full[w] for w in p['words'][lo:hi]]) for lo,hi,k in chosen])
  return dict(aliases=aliases,parses=parses)
 for q in pred['queries']:
  s.push()
  if 'word' in q:s.add(b['xs'][q['word']]==b['num'][q['value']])
  status=check();row=dict(**q,status=status)
  if status=='sat':row['witness']=witness()
  answers.append(row);s.pop()
 for _ in range(cfg['tuple_limit']):
  status=check()
  if status!='sat':projection=dict(exhaustive=status=='unsat',status=status);break
  w=witness();values={k:w['aliases'][k] for k in pred['shared_words']};tuples.append(dict(values=values,witness=w));s.add(z3.Or([b['xs'][k]!=b['num'][v] for k,v in values.items()]))
 else:projection=dict(exhaustive=False,status='TUPLE_LIMIT')
 return dict(id=pred['id'],answers=answers,tuples=tuples,projection=projection,wall_seconds=time.monotonic()-start)
def main():
 for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 cfg=read(E/'src/SPEC.json');pred=read(A/'PREDICTIONS.json');g=read(R/cfg['grammar']);lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']};old=read(R/cfg['source_world_rows']);start=datetime.datetime.now(datetime.timezone.utc).isoformat();tm=time.monotonic()
 with concurrent.futures.ProcessPoolExecutor(max_workers=cfg['workers']) as pool:rows=list(pool.map(task,[(p,cfg,g,lex) for p in pred]))
 put('ROWS.json',rows);comp=[]
 for r,o,p in zip(rows,old,pred):
  key=lambda x:json.dumps(x['values'],sort_keys=True);ws={key(t) for t in o['tuples']};ss={key(t) for t in r['tuples']};assert r['id']==o['id']==p['id']
  domains=[]
  for word in p['shared_words']:
   sv=[q['value'] for q in r['answers'] if q.get('word')==word and q['status']=='sat'];wv=o['domains'][word]['sat'];domains.append(dict(word=word,syntax_values=sv,world_values=wv,syntax_only=sorted(set(sv)-set(wv))))
  comp.append(dict(id=r['id'],query_counts=dict(collections.Counter(q['status'] for q in r['answers'])),syntax_tuples=len(ss),world_tuples=len(ws),syntax_projection=r['projection'],world_missing_in_syntax=sorted(ws-ss),syntax_only_tuples=[json.loads(x) for x in sorted(ss-ws)],domains=domains))
 result=dict(status='CONTENT_ADDED_RELATIONS_AUDITED',systems=comp,queries=sum(len(r['answers']) for r in rows),confirmed_words=0,independent_meaning_capacity=0,significance=False);put('RESULT.json',result)
 with (A/'CANDIDATES.tsv').open('w',newline='') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['system','query','grammar_status','world_status'])
  for r,o in zip(rows,old):
   for q,z in zip(r['answers'],o['answers']):w.writerow([r['id'],q['id'],q['status'],z['status']])
 put('EXECUTION_RECEIPT.json',dict(started_utc=start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=time.monotonic()-tm,z3_version=z3.get_version_string()));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
