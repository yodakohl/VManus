#!/usr/bin/env python3
import csv,gzip,hashlib,json,time
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import combinations,permutations
from pathlib import Path
from core import ORDERS,LAYOUTS,matrix,length_failure,factor,signature
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=read(E/'src/SPEC.json');receipt=read(E/'artifacts/PUBLIC_REGISTRATION.json')
 assert len(receipt['commit'])==40
 for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/p)==h,p
 start=now();clock=time.monotonic();packet=read(R/s['target']);source=read(R/s['source'])
 assert {k:len(v) for k,v in packet['panels'].items()}==s['counts']
 feature_cells=[dict(table=t['id'],person=s['persons'][r],channel=s['channels'][c],cell_id=x['id'],prediction='HEAR(channel,person,tense)') for t in source['tables'] for r,row in enumerate(t['rows']) for c,x in enumerate(row)]
 assert len(feature_cells)==36
 write(E/'artifacts/PREDICTIONS.json',dict(cells=feature_cells,orders=ORDERS,layouts=LAYOUTS,channel_permutations=list(permutations(s['channels'])),target_sha256=s['target_sha256'],all_pairs_rule='All36cells exact;oneR/P dictionary;differentT;onepanel/layout/order;disjointsourcegroups',equivalent_lexical_predicates='Any predicate with same paradigm, including HEAR/SEE/KNOW',independent_meaning_capacity=0))
 records=[];witnesses=[];index={};deadline=False
 for panel,windows in packet['panels'].items():
  for w in windows:
   assert not w['page'].startswith('f84') and w['page']!='f116v'
   assert len(w['words'])==18 and len(w['source_group_ids'])==18
   index[(panel,w['id'])]=w
   for layout in LAYOUTS:
    row=dict(panel=panel,window_id=w['id'],paragraph_id=w['paragraph_id'],page=w['page'],physical_folio=w['physical_folio'],start=w['start'],layout=layout)
    if time.monotonic()-clock>s['execution_seconds']:
     deadline=True;row.update(status='UNKNOWN_REMAINDER',factorizations=0);records.append(row);continue
    m=matrix(w['words'],layout);bad=length_failure(m)
    if bad:
     row.update(status='CONTRADICTED_LENGTH_RECTANGLE',certificate=bad,factorizations=0)
    else:
     found=[];by_order={}
     for order in ORDERS:
      fs=factor(m,order);by_order[order]=len(fs)
      for f in fs:
       wi=dict(f,panel=panel,window_id=w['id'],layout=layout,id=len(witnesses));witnesses.append(wi);found.append(wi['id'])
     row.update(status='LOCAL_FACTORIZATION' if found else 'CONTRADICTED_SHARED_FIELDS',factorizations=len(found),witness_ids=found,by_order=by_order)
    records.append(row)
 groups=defaultdict(list)
 for w in witnesses:groups[signature(w)].append(w)
 pairs=[];joins_complete=True
 for group in groups.values():
  for a,b in combinations(group,2):
   if time.monotonic()-clock>s['execution_seconds']:
    joins_complete=False;break
   if a['tense']==b['tense']:continue
   aa=index[(a['panel'],a['window_id'])];bb=index[(b['panel'],b['window_id'])]
   if set(aa['source_group_ids']) & set(bb['source_group_ids']):continue
   pairs.append(dict(a=a['id'],b=b['id'],temporal_assignments=2,channel_assignments=6,independent_meaning_capacity=0,distinct_physical_leaves=aa['physical_folio']!=bb['physical_folio']))
  if not joins_complete:break
 (E/'artifacts/CASES.json.gz').write_bytes(gzip.compress(json.dumps(dict(rows=records,witnesses=witnesses,pairs=pairs),sort_keys=True,separators=(',',':')).encode(),mtime=0))
 with (E/'artifacts/CANDIDATES.tsv').open('w') as f:
  fields=['panel','window_id','paragraph_id','page','physical_folio','start','layout','status','factorizations','by_order','certificate']
  out=csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='ignore');out.writeheader()
  for row in records:
   out.writerow({k:json.dumps(row[k],sort_keys=True,separators=(',',':')) if isinstance(row.get(k),(dict,list)) else row.get(k,'') for k in fields})
 counts=dict(Counter(x['status'] for x in records));status='RETAIN_COMPOSITIONAL_TABLE_CANDIDATES' if pairs else ('UNKNOWN_BOUNDED_SEARCH' if deadline or not joins_complete else 'CONTRADICTED_COMPLETE_FEATURE_TABLES')
 result=dict(status=status,start_utc=start,end_utc=now(),elapsed_seconds=time.monotonic()-clock,registered_commit=receipt['commit'],windows=sum(s['counts'].values()),window_traversal_cases=len(records),canonical_field_order_cases=len(records)*6,with_channel_label_permutations=len(records)*36,counts=counts,local_factorizations=len(witnesses),paired_factorizations=len(pairs),labeled_pair_representations=len(pairs)*12,joins_complete=joins_complete,independent_meaning_capacity=0,confirmed_words_added=0,lexical_predicate_unidentified=True)
 write(E/'artifacts/RESULT.json',result);print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
