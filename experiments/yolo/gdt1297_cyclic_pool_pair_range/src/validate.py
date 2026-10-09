#!/usr/bin/env python3
"""Independent SQL run boundaries and interval-imbalance certificate replay."""
from pathlib import Path
import collections,gzip,hashlib,itertools,json,sqlite3
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
def load(name):return json.loads(gzip.decompress((B/'artifacts'/name).read_bytes()) if name.endswith('.gz') else (B/'artifacts'/name).read_bytes())
def main():
 spec=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 for inp in spec['inputs']:assert hashlib.sha256((ROOT/inp['path']).read_bytes()).hexdigest()==inp['sha256']
 source=json.loads(gzip.decompress((ROOT/spec['inputs'][0]['path']).read_bytes()));old=json.loads((ROOT/spec['inputs'][1]['path']).read_text());result=load('RESULT.json');saved=load('RUNS.json.gz');proofs=load('PROOFS.json.gz');total=anchors=checks=0
 for reader,rows in source.items():
  con=sqlite3.connect(':memory:');con.execute('CREATE TABLE g(page TEXT,locus TEXT,idx INTEGER,payload TEXT,UNIQUE(page,locus,idx))')
  for q in rows:
   assert q['edition']==reader and q['kind']=='P' and q['left_separator']==q['right_separator']=='DEFINITE_SPACE'
   assert not q['page'].startswith('f84') and q['page']!='f116v'
   con.execute('INSERT INTO g VALUES(?,?,?,?)',(q['page'],q['locus'],int(q['source_group_index']),json.dumps(q)));total+=1
  sql='''WITH prior AS(SELECT *,LAG(idx) OVER(PARTITION BY page,locus ORDER BY idx) AS p FROM g),
         flagged AS(SELECT *,CASE WHEN p IS NULL OR idx<>p+1 THEN 1 ELSE 0 END AS start FROM prior),
         numbered AS(SELECT *,SUM(start) OVER(PARTITION BY page,locus ORDER BY idx) AS block FROM flagged)
         SELECT page,locus,block,idx,payload FROM numbered ORDER BY page,locus,block,idx'''
  runs=[]
  for (page,locus,block),group in itertools.groupby(con.execute(sql),key=lambda q:q[:3]):
   items=list(group);qs=[json.loads(x[4]) for x in items];runs.append({'id':f'{reader}|{locus}|{items[0][3]:03}-{items[-1][3]:03}','page':page,'locus':locus,'groups':qs})
  con.close();runs.sort(key=lambda q:q['id']);assert runs==saved[reader]
  streams={q['id']:[g['ivtff_group_raw'] for g in q['groups']] for q in runs};run_by={q['id']:q for q in runs};seeds={};direct=set()
  for run in runs:
   fs=streams[run['id']]
   for i in range(len(fs)-2):
    if len(set(fs[i:i+3]))==1:direct.add(fs[i])
   for a,count in collections.Counter(fs).items():
    if count<3:continue
    # Independent interval enumeration, rather than consecutive-occurrence triples.
    for lo in range(len(fs)):
     if fs[lo]!=a:continue
     for hi in range(lo+2,len(fs)):
      if fs[hi]!=a or fs[lo:hi+1].count(a)!=3:continue
      ids=tuple(g['id'] for g in run['groups'][lo:hi+1]);key=(hi-lo+1,ids)
      if a not in seeds or key<seeds[a][0]:seeds[a]=(key,run['id'],lo,hi)
  assert [x['form'] for x in proofs[reader]]==sorted(seeds)
  forced=[];checkcount=0
  for item in proofs[reader]:
   a=item['form'];_,rid,lo,hi=seeds[a];rs=run_by[rid];span=rs['groups'][lo:hi+1];partners=sorted(set(streams[rid][lo:hi+1])-{a})
   expected={'run_id':rid,'start_offset':lo,'end_offset':hi,'source_ids':[q['id'] for q in span],'forms':[q['ivtff_group_raw'] for q in span],'candidate_partners':partners};assert item['seed']==expected and expected['forms'].count(a)==3
   cs=[]
   for b in partners:
    witness=None
    for run in runs:
     fs=streams[run['id']]
     if max(fs.count(a),fs.count(b))<3:continue
     deltas=[int(w==a)-int(w==b) for w in fs];bad=False
     for first in range(len(deltas)):
      subtotal=0
      for step in deltas[first:]:
       subtotal+=step
       if abs(subtotal)>2:bad=True;break
      if bad:break
     if bad:
      d=[0]+list(itertools.accumulate(deltas));witness={'run_id':run['id'],'prefix_difference':d,'range':max(d)-min(d),'source_ids':[q['id'] for q in run['groups']]};break
    cs.append({'partner':b,'excluded':witness is not None,'witness':witness});checkcount+=1
   assert cs==item['partner_checks'];survivors=[c['partner'] for c in cs if not c['excluded']]
   assert survivors==item['surviving_partners'] and item['forced_singleton']==(not survivors)
   if not survivors:forced.append(a)
  oldset={q['raw'] for q in old if q['edition']==reader};types={q['ivtff_group_raw'] for q in rows}
  expected={'groups':len(rows),'runs':len(runs),'forms':len(types),'repeat_anchors':len(seeds),'seed_partner_checks':checkcount,'forced_singletons':forced,'current_direct_AAA':sorted(direct),'old857_AAA':sorted(oldset),'additional_nonlocal_forced':sorted(set(forced)-oldset-direct),'minimum_distinct_pools':len(forced)+int(bool(types-set(forced))),'unexcluded_anchor_forms':[x['form'] for x in proofs[reader] if not x['forced_singleton']]}
  assert result['readers'][reader]==expected;anchors+=len(seeds);checks+=checkcount
 status='ADDITIONAL_SINGLETON_CONSEQUENCES' if any(x['additional_nonlocal_forced'] for x in result['readers'].values()) else 'NO_ADDITIONAL_SINGLETON_CONSEQUENCE';assert result['status']==status
 f=load('FIXTURES.json');assert f['status']=='PASS' and f['valid_cycle_windows']==9888
 out={'status':'PASS','source_groups':total,'anchor_proofs':anchors,'partner_checks':checks,'scope':'IndependentSQLrunandintervalimbalanceverification;notmeaning,nativeinkorglobalpoolpartition'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
