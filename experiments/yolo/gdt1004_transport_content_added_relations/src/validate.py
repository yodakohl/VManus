import argparse,collections,concurrent.futures,csv,hashlib,json,subprocess,sys
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cvc5-python',default=sys.executable);args=ap.parse_args()
 for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 cfg=read(E/'src/SPEC.json');pred=read(A/'PREDICTIONS.json');rows=read(A/'ROWS.json');old=read(R/cfg['source_world_rows']);result=read(A/'RESULT.json');g=read(R/cfg['grammar']);lex={x['raw']:x['symbol'] for x in read(R/cfg['source_draft'])['lexicon']};assert pred==read(R/cfg['source_predictions']) and read(R/cfg['source_world_validation'])['status']=='PASS'
 witnesses=0;jobs=[];key=lambda v:json.dumps(v,sort_keys=True)
 def ground(w,ps):
  nonlocal witnesses
  witnesses+=1;assert set(w['aliases'])==set(x for p in ps for x in p['words'])-lex.keys();full={**lex,**w['aliases']};assert len(w['parses'])==len(ps)
  for p,parsed in zip(ps,w['parses']):
   assert not p['page'].startswith('f84') and p['page']!='f116v';cur=0;kinds=[]
   for n in parsed:
    assert n['start']==cur and n['end']==cur+len(g['patterns'][n['kind']]);ss=[full[x] for x in p['words'][cur:n['end']]];assert ss==n['symbols']
    for x,t in zip(ss,g['patterns'][n['kind']]):assert x in (g['types'][t[1:]] if t.startswith('@') else [t])
    cur=n['end'];kinds.append(n['kind'])
   assert cur==len(p['words']) and kinds[0]=='INITIAL' and kinds[-1]=='CONCLUSION'
   assert all(kinds.count(k)==1 for k in ('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'))
 for p,r,o,summary in zip(pred,rows,old,result['systems']):
  assert p['id']==r['id']==o['id']==summary['id'];assert len(r['answers'])==len(p['queries'])==len(o['answers'])
  for q,a in zip(p['queries'],r['answers']):
   assert all(a[k]==v for k,v in q.items());assert a['status'] in ('sat','unsat','unknown','unknown_batch_limit')
   if a['status']=='sat':
    ground(a['witness'],p['paragraphs'])
    if 'word' in q:assert a['witness']['aliases'][q['word']]==q['value']
  ts=[]
  for t in r['tuples']:
   ground(t['witness'],p['paragraphs']);assert t['values']=={w:t['witness']['aliases'][w] for w in p['shared_words']};ts.append(t['values'])
  assert len({key(t) for t in ts})==len(ts)<=cfg['tuple_limit']
  ss={key(t) for t in ts};ws={key(t['values']) for t in o['tuples']};assert o['projection']['exhaustive'];assert summary['syntax_tuples']==len(ss) and summary['world_tuples']==len(ws)
  assert summary['world_missing_in_syntax']==sorted(ws-ss) and summary['syntax_only_tuples']==[json.loads(x) for x in sorted(ss-ws)]
  assert summary['query_counts']==dict(collections.Counter(a['status'] for a in r['answers'])) and summary['syntax_projection']==r['projection']
  for d in summary['domains']:
   sv=[q['value'] for q in r['answers'] if q.get('word')==d['word'] and q['status']=='sat'];wv=o['domains'][d['word']]['sat'];assert d==dict(word=d['word'],syntax_values=sv,world_values=wv,syntax_only=sorted(set(sv)-set(wv)))
  qs=list(p['queries'])+[dict(id='TUPLE'+str(i),values=t) for i,t in enumerate(ts)]
  # World-positive tuples missing from a nonexhaustive sample are tested separately.
  qs += [dict(id='WORLD'+str(i),values=json.loads(t)) for i,t in enumerate(sorted(ws-ss))]
  if r['projection']['exhaustive']:assert r['projection']['status']=='unsat' and not ws-ss;qs.append(dict(id='EXHAUSTION',blocked_tuples=ts))
  jobs.append((p['id'],dict(paragraphs=p['paragraphs'],lexicon=lex,grammar=g,queries=qs,timeout=cfg['query_milliseconds'],worker_seconds=cfg['worker_seconds'])))
 def independent(job):
  ident,data=job
  try:q=subprocess.run([args.cvc5_python,str(E/'src/independent.py')],input=json.dumps(data),text=True,capture_output=True,timeout=cfg['worker_seconds']+30,check=True);return dict(id=ident,**json.loads(q.stdout))
  except subprocess.TimeoutExpired:return dict(id=ident,queries=[dict(id=q['id'],status='unknown_batch_limit') for q in data['queries']])
 with concurrent.futures.ThreadPoolExecutor(max_workers=cfg['workers']) as pool:checks=list(pool.map(independent,jobs))
 unresolved=[]
 for r,c,j in zip(rows,checks,jobs):
  assert [q['id'] for q in c['queries']]==[q['id'] for q in j[1]['queries']]
  for q,v in zip(r['answers'],c['queries']):
   assert (q['status'],v['status']) not in [('sat','unsat'),('unsat','sat')],(r['id'],q['id'])
   if q['status']=='unsat' and v['status']!='unsat':unresolved.append(dict(system=r['id'],query=q['id']))
  for q in c['queries'][len(r['answers']):]:
   expected='unsat' if q['id']=='EXHAUSTION' else 'sat';assert q['status']!=('sat' if expected=='unsat' else 'unsat')
   if q['status']!=expected:unresolved.append(dict(system=r['id'],query=q['id']))
 assert result['queries']==sum(len(r['answers']) for r in rows)==190
 with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
 expected=[dict(system=r['id'],query=q['id'],grammar_status=q['status'],world_status=z['status']) for r,o in zip(rows,old) for q,z in zip(r['answers'],o['answers'])];assert table==expected
 (A/'INDEPENDENT_QUERIES.json').write_text(json.dumps(checks,separators=(',',':'))+'\n')
 out=dict(status='PASS' if not unresolved else 'PASS_WITH_UNRESOLVED_CHECKS',marginal_queries=190,full_syntax_witnesses=witnesses,independent_status_counts=dict(collections.Counter(q['status'] for c in checks for q in c['queries'])),unresolved=unresolved,confirmed_words=0,scope='Finite syntax versus fixed world projection; no independent meaning')
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
