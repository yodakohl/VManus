"""All recurrent content jointly; singleton spans are an explicit relaxation."""
import collections,concurrent.futures,csv,gzip,hashlib,json,subprocess,sys,threading,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
OLD=R/'experiments/yolo/gdt976_dioscorides_shared_referent_projection'
LAST=R/'experiments/yolo/gdt977_dioscorides_leaf_breadth_projection'
ACTIVE={};LOCK=threading.Lock();STOP=threading.Event()
def save(name,data):
 blob=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode();p=E/'artifacts'/name
 if name.endswith('.gz'):
  with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(blob)
 else:p.write_bytes(blob)
def solve_job(job):
 import cvc5
 from cvc5 import Kind as K
 start=time.monotonic();model=job['model'];records=model['records'];domains=job['domains'];atoms=model['recurrent_atoms']
 if any(not domains[r['id']] for r in records):return dict(status='UNSAT_EMPTY_DOMAIN')
 s=cvc5.Solver();s.setLogic('QF_SLIA');s.setOption('produce-models','true');s.setOption('strings-exp','true')
 def ands(xs):return s.mkTerm(K.AND,*xs) if len(xs)>1 else xs[0] if xs else s.mkBoolean(True)
 def ors(xs):return s.mkTerm(K.OR,*xs) if len(xs)>1 else xs[0] if xs else s.mkBoolean(False)
 def eq(a,b):return s.mkTerm(K.EQUAL,a,b)
 def bound(x,lo,hi):
  le=s.mkTerm(K.STRING_LENGTH,x);s.assertFormula(s.mkTerm(K.GEQ,le,s.mkInteger(lo)));s.assertFormula(s.mkTerm(K.LEQ,le,s.mkInteger(hi)))
 code={a:s.mkConst(s.getStringSort(),'a'+str(i)) for i,a in enumerate(atoms)}
 for a,var in code.items():
  maximum=min((max(len(t['text']) for t in domains[r['id']])-r['source_atoms']+r['counts'][a])//r['counts'][a] for r in records if r['counts'].get(a,0))
  if maximum<1:return dict(status='UNSAT_NONEMPTY_LENGTH')
  bound(var,1,maximum)
 for i,a in enumerate(atoms):
  for b in atoms[i+1:]:
   s.assertFormula(s.mkTerm(K.NOT,s.mkTerm(K.STRING_PREFIX,code[a],code[b])))
   s.assertFormula(s.mkTerm(K.NOT,s.mkTerm(K.STRING_PREFIX,code[b],code[a])))
 gaps={};selectors={};leaves={};expr={}
 for ri,r in enumerate(records):
  rid=r['id'];top=max(len(t['text']) for t in domains[rid]);selectors[rid]=s.mkConst(s.getIntegerSort(),'page'+str(ri));leaves[rid]=s.mkConst(s.getStringSort(),'leaf'+str(ri))
  for gi,g in enumerate(r['gaps']):
   var=s.mkConst(s.getStringSort(),'g'+str(ri)+'_'+str(gi));gaps[g['id']]=var;bound(var,g['minimum'],top-r['source_atoms']+g['minimum'])
  terms=[code[t['atom']] if 'atom' in t else gaps[t['gap']] for t in r['terms']]
  expr[rid]=s.mkTerm(K.STRING_CONCAT,*terms) if len(terms)>1 else terms[0]
  choices=[ands([eq(selectors[rid],s.mkInteger(j)),eq(expr[rid],s.mkString(t['text'])),eq(leaves[rid],s.mkString(t['physical_leaf']))]) for j,t in enumerate(domains[rid])]
  s.assertFormula(ors(choices))
 s.assertFormula(s.mkTerm(K.DISTINCT,*leaves.values()))
 xindex={t['page']:j for j,t in enumerate(domains['IV.20'])}
 restrictions=[ands([eq(code['IRIS'],s.mkString(c['iris_code'])),eq(code['XIPHION'],s.mkString(c['xiphion_code'])),eq(selectors['IV.20'],s.mkInteger(xindex[c['xiphion_page']]))]) for c in job['name_cases']]
 s.assertFormula(ors(restrictions));built=time.monotonic()
 s.setOption('tlimit-per',str(int(job['solver_seconds']*1000)));ans=s.checkSat()
 status='SAT_RECURRENT_PROJECTION' if ans.isSat() else 'UNSAT_SOLVER' if ans.isUnsat() else 'UNKNOWN_SOLVER'
 result=dict(status=status,solver='cvc5',version=cvc5.__version__,construction_seconds=built-start,solver_seconds=time.monotonic()-built)
 if ans.isSat():
  result['code']={a:s.getValue(v).getStringValue() for a,v in code.items()};result['gaps']={a:s.getValue(v).getStringValue() for a,v in gaps.items()}
  result['assignments']={rid:{k:domains[rid][int(str(s.getValue(sel)))][k] for k in ['page','physical_leaf']} for rid,sel in selectors.items()}
  matches=[c['id'] for c in job['name_cases'] if c['iris_code']==result['code']['IRIS'] and c['xiphion_code']==result['code']['XIPHION'] and c['xiphion_page']==result['assignments']['IV.20']['page']]
  assert len(matches)==1;result['witnessed_base_id']=matches[0]
 result['elapsed_seconds']=time.monotonic()-start
 return result
def isolated(job):
 if STOP.is_set():return dict(status='UNKNOWN_GLOBAL_WALL')
 p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--solve-job'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 with LOCK:
  if STOP.is_set():p.kill()
  ACTIVE[job['id']]=p
 try:
  out,err=p.communicate(json.dumps(job),timeout=job['process_wall_seconds'])
  if p.returncode:return dict(status='UNKNOWN_GLOBAL_WALL' if STOP.is_set() else 'ERROR_SOLVER_PROCESS',returncode=p.returncode)
  return json.loads(out)
 except subprocess.TimeoutExpired:
  p.kill();p.communicate();return dict(status='UNKNOWN_PROCESS_WALL',wall_ceiling=job['process_wall_seconds'])
 finally:
  with LOCK:ACTIVE.pop(job['id'],None)
def main():
 for name,digest in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
 assert (E/'artifacts/EXECUTION_RECEIPT.json').exists()
 spec=json.loads((E/'src/SPEC.json').read_text());model=json.loads((E/'src/SOURCE_MODEL.json').read_text());pred=json.loads((E/'artifacts/PARTITION_PREDICTIONS.json').read_text());dom=json.loads((OLD/'artifacts/DOMAINS.json').read_text())
 with gzip.open(OLD/'artifacts/CANDIDATES.json.gz','rt') as f:base=json.load(f)
 with gzip.open(LAST/'artifacts/CASES.json.gz','rt') as f:previous=json.load(f)
 assert all(not x['page'].startswith('f84') and x['page']!='f116v' for rs in dom.values() for xs in rs.values() for x in xs)
 jobs=[]
 for part in pred:
  ds={rid:[t for t in ts if rid!='I.1' or t['page']==part['iris_page']] for rid,ts in dom[part['edition']].items()}
  names=[dict(id=i,**{k:base[i][k] for k in ['iris_code','xiphion_code','xiphion_page']}) for i in part['base_ids']]
  jobs.append(dict(id=part['id'],model=model,domains=ds,name_cases=names,solver_seconds=spec['solver_seconds'],process_wall_seconds=spec['process_wall_seconds']))
 started=time.monotonic();results={};pool=concurrent.futures.ThreadPoolExecutor(max_workers=spec['workers']);futures={pool.submit(isolated,j):j['id'] for j in jobs}
 try:
  for f in concurrent.futures.as_completed(futures,timeout=spec['execution_wall_seconds']):
   pid=futures[f]
   try:result=f.result()
   except Exception as e:result=dict(status='ERROR_RUNNER',error_type=type(e).__name__)
   results[pid]=dict(id=pid,**result);print('Partition',pid,result['status'],flush=True)
 except concurrent.futures.TimeoutError:pass
 finally:
  STOP.set()
  with LOCK:
   for p in ACTIVE.values():p.kill()
  pool.shutdown(wait=True,cancel_futures=True)
 for part in pred:
  if part['id'] not in results:results[part['id']]=dict(id=part['id'],status='UNKNOWN_GLOBAL_WALL')
 rows=[results[i] for i in range(len(pred))];save('PARTITION_RESULTS.json.gz',rows)
 partition_of={i:p['id'] for p in pred for i in p['base_ids']};table=[]
 for i,(c,prev) in enumerate(zip(base,previous)):
  pid=partition_of.get(i);row=results.get(pid);status='INHERITED_GDT977_CONTRADICTION'
  if row:
   if row['status'].startswith('UNSAT'):status='EXCLUDED_BY_RECURRENT_PARTITION'
   elif row['status']=='SAT_RECURRENT_PROJECTION':status='WITNESSED_RECURRENT_CODE' if row['witnessed_base_id']==i else 'UNCLASSIFIED_IN_SAT_PARTITION'
   else:status='UNRESOLVED_'+row['status']
  table.append([i,c['edition'],c['iris_page'],c['xiphion_page'],c['iris_code'],c['xiphion_code'],pid if pid is not None else '',status])
 with (E/'artifacts/BASE_CASE_RESULTS.tsv').open('w') as f:
  writer=csv.writer(f,delimiter='\t',lineterminator='\n');writer.writerow(['id','edition','iris_page','xiphion_page','iris_code','xiphion_code','partition','status']);writer.writerows(table)
 counts=dict(collections.Counter(x['status'] for x in rows));status='RECURRENT_PARTIAL_WITNESS_FOUND' if counts.get('SAT_RECURRENT_PROJECTION') else 'ALL_RECURRENT_PARTITIONS_EXCLUDED' if all(x['status'].startswith('UNSAT') for x in rows) else 'BOUNDED_RECURRENT_SEARCH_UNRESOLVED'
 result=dict(status=status,partitions=len(rows),partition_counts=counts,base_counts=dict(collections.Counter(t[-1] for t in table)),tested_base_rows=len(partition_of),original_base_rows=len(base),recurrent_types=78,recurrent_occurrences=358,singleton_occurrences=255,zero_gap_recurrent_seams=208,full_code_tested=False,confirmed_words=0,independent_confirmation_leaves=0,reserve_access=False,elapsed_seconds=time.monotonic()-started)
 save('RESULT.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':
 if '--solve-job' in sys.argv:print(json.dumps(solve_job(json.load(sys.stdin))))
 else:main()
