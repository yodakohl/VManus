"""Finite necessary projection; first witness is a certificate, not a reading rank."""
import collections,csv,functools,gzip,hashlib,json,multiprocessing as mp,os,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
OLD=R/'experiments/yolo/gdt976_dioscorides_shared_referent_projection'
def save(name,data):
 blob=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode();path=E/'artifacts'/name
 if name.endswith('.gz'):
  with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:f.write(blob)
 else:path.write_bytes(blob)
def project(p,text,codes):
 cursor=0;positions=[]
 for gap,atom in zip(p['gaps_before'],p['events']):
  value=codes[atom]
  start=(cursor if text.startswith(value,cursor) else -1) if gap==0 else text.find(value,cursor+gap)
  if start<0:return None
  positions.append(start);cursor=start+len(value)
 return positions if len(text)-cursor>=p['tail'] else None
def setup(domains,spec):
 global D,P,S,PAGE
 D,S,P=domains,spec,spec['projections']
 PAGE={ed:{rid:{x['page']:x for x in xs} for rid,xs in ds.items()} for ed,ds in domains.items()}
@functools.lru_cache(maxsize=512)
def support(ed,rid,v,leaf,broad):
 codes={'IRIS':v,'LEAF':leaf,'BROAD':broad};out=[]
 for z in D[ed][rid]:
  pos=project(P[rid],z['text'],codes)
  if pos is not None:out.append(dict(page=z['page'],physical_leaf=z['physical_leaf'],positions=pos))
 return out
def joint_support(ed,v,leaf,broad,excluded):
 ac=[z for z in support(ed,'I.2',v,leaf,broad) if z['physical_leaf'] not in excluded]
 me=[z for z in support(ed,'I.3','',leaf,'') if z['physical_leaf'] not in excluded]
 ac=[z for z in ac if any(m['physical_leaf']!=z['physical_leaf'] for m in me)]
 me=[m for m in me if any(z['physical_leaf']!=m['physical_leaf'] for z in ac)]
 return ac,me,sum(z['physical_leaf']!=m['physical_leaf'] for z in ac for m in me)
def next_chars(text,prefix):
 out=set();start=text.find(prefix)
 while start>=0:
  end=start+len(prefix)
  if end<len(text):out.add(text[end])
  start=text.find(prefix,start+1)
 return out
def solve(item):
 number,c=item;started=time.process_time();ed,v,w=c['edition'],c['iris_code'],c['xiphion_code']
 a,x=PAGE[ed]['I.1'][c['iris_page']],PAGE[ed]['IV.20'][c['xiphion_page']]
 ta,tx=a['text'],x['text'];fixed=(v,w);excluded={a['physical_leaf'],x['physical_leaf']}
 assert len(excluded)==2 and not v.startswith(w) and not w.startswith(v)
 alphabet=sorted(set(ta)&set(tx));queue=collections.deque((l,b) for l in alphabet for b in alphabet)
 proof=[];checked=0
 while queue:
  if time.process_time()-started>=S['case_cpu_seconds']:return dict(id=number,status='UNKNOWN_CASE_CPU',nodes=checked,cpu_seconds=time.process_time()-started)
  leaf,broad=queue.popleft();checked+=1
  if any(z.startswith(f) for z in (leaf,broad) for f in fixed):proof.append([leaf,broad,'FIXED_PREFIX','']);continue
  codes={'IRIS':v,'XIPHION':w,'LEAF':leaf,'BROAD':broad}
  pa,px=project(P['I.1'],ta,codes),project(P['IV.20'],tx,codes)
  if pa is None or px is None:proof.append([leaf,broad,'NO_LOCAL_FIT','']);continue
  ac,me,n=joint_support(ed,v,leaf,broad,excluded)
  if not n:proof.append([leaf,broad,'NO_FOUR_LEAF_SUPPORT','']);continue
  if any(f.startswith(leaf) for f in fixed):which='L'
  elif any(f.startswith(broad) for f in fixed):which='B'
  elif broad.startswith(leaf):which='L'
  elif leaf.startswith(broad):which='B'
  else:
   witness=dict(leaf_code=leaf,broad_code=broad,iris_positions=pa,xiphion_positions=px,acorus=ac,meum=me,four_page_assignments=n)
   return dict(id=number,status='PARTIAL_FOUR_ATOM_WITNESS',nodes=checked,cpu_seconds=time.process_time()-started,witness=witness)
  prefix=leaf if which=='L' else broad;children=''.join(sorted(next_chars(ta,prefix)&next_chars(tx,prefix)))
  proof.append([leaf,broad,'BRANCH_'+which,children])
  for ch in children:queue.append((leaf+ch,broad) if which=='L' else (leaf,broad+ch))
 return dict(id=number,status='FOUR_ATOM_PROJECTION_CONTRADICTED',nodes=checked,cpu_seconds=time.process_time()-started,proof=proof)
def main():
 for name,digest in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
 assert (E/'artifacts/EXECUTION_RECEIPT.json').exists(),'Publish registration and record receipt first'
 spec=json.loads((E/'src/SPEC.json').read_text());domains=json.loads((OLD/'artifacts/DOMAINS.json').read_text())
 with gzip.open(OLD/'artifacts/CANDIDATES.json.gz','rt') as f:candidates=json.load(f)
 assert len(candidates)==spec['expected_cases']
 assert all(not x['page'].startswith('f84') and x['page']!='f116v' for ds in domains.values() for xs in ds.values() for x in xs)
 started=time.monotonic();workers=min(spec['workers'],os.cpu_count() or 1);results={}
 pool=mp.get_context('fork').Pool(workers,initializer=setup,initargs=(domains,spec));it=pool.imap_unordered(solve,enumerate(candidates),chunksize=1)
 try:
  while len(results)<len(candidates):
   remaining=spec['execution_wall_seconds']-(time.monotonic()-started)
   if remaining<=0:break
   try:row=it.next(timeout=remaining)
   except mp.TimeoutError:break
   results[row['id']]=row
   if len(results)%1000==0:print('Completed',len(results),dict(collections.Counter(z['status'] for z in results.values())),flush=True)
 finally:pool.terminate();pool.join()
 for number in range(len(candidates)):
  if number not in results:results[number]=dict(id=number,status='UNKNOWN_GLOBAL_WALL',nodes=None,cpu_seconds=None)
 rows=[results[i] for i in range(len(candidates))];save('CASES.json.gz',rows)
 columns=['id','edition','iris_page','xiphion_page','iris_code','xiphion_code','status','leaf_witness','broad_witness','acorus_pages','meum_pages','four_page_assignments','nodes']
 with (E/'artifacts/CANDIDATE_RESULTS.tsv').open('w') as f:
  writer=csv.writer(f,delimiter='\t',lineterminator='\n');writer.writerow(columns)
  for row,c in zip(rows,candidates):
   w=row.get('witness',{});writer.writerow([row['id'],*[c[k] for k in columns[1:6]],row['status'],w.get('leaf_code',''),w.get('broad_code',''),','.join(z['page'] for z in w.get('acorus',[])),','.join(z['page'] for z in w.get('meum',[])),w.get('four_page_assignments',''),row['nodes']])
 counts=dict(collections.Counter(z['status'] for z in rows));good=[(c,z) for c,z in zip(candidates,rows) if 'witness' in z]
 classes={(c['edition'],c['iris_code'],c['xiphion_code']) for c,z in good}
 status='PARTIAL_FOUR_ATOM_BINDINGS_REMAIN' if good else 'UNRESOLVED_PROJECTION' if any(x.startswith('UNKNOWN') for x in counts) else 'ALL_LITERAL_BASE_ROWS_CONTRADICTED'
 result=dict(status=status,cases=len(rows),counts=counts,surviving_name_classes=len(classes),witnessed_iris_values=len({c['iris_code'] for c,z in good}),witnessed_xiphion_values=len({c['xiphion_code'] for c,z in good}),saved_leaf_witness_values=len({z['witness']['leaf_code'] for c,z in good}),saved_broad_witness_values=len({z['witness']['broad_code'] for c,z in good}),enumerated_all_leaf_broad_codes=False,constrained_source_occurrences=13,source_occurrences=613,confirmed_words=0,independent_confirmation_leaves=0,reserve_access=False,full_code_tested=False,workers=workers,elapsed_seconds=time.monotonic()-started)
 save('RESULT.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':main()
