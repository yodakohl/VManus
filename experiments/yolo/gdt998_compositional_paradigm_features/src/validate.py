#!/usr/bin/env python3
"""Independent length-vector extraction; no runner/core import."""
import csv,gzip,hashlib,json
from collections import Counter
from datetime import datetime,timezone
from itertools import permutations,combinations
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def canon(xs):return sorted(json.dumps(x,sort_keys=True) for x in xs)
def independently_factor(m,order):
 n=len(m[0][0]);out=[]
 for r0 in range(1,n+1):
  for p0 in range(n-r0+1):
   t=n-r0-p0
   rl=[len(m[0][c])-p0-t for c in range(len(m[0]))]
   pl=[len(m[r][0])-r0-t for r in range(len(m))]
   if min(rl)<1 or min(pl)<0:continue
   assignments={};good=True
   for r,row in enumerate(m):
    for c,word in enumerate(row):
     lengths=dict(R=rl[c],P=pl[r],T=t);offset=0
     for k in order:
      key=(k,c if k=='R' else r if k=='P' else 0)
      value=word[offset:offset+lengths[k]];offset+=lengths[k]
      if len(value)!=lengths[k] or key in assignments and assignments[key]!=value:good=False
      assignments[key]=value
     if offset!=len(word):good=False
   roots=[assignments.get(('R',c)) for c in range(len(m[0]))];persons=[assignments.get(('P',r)) for r in range(len(m))]
   if good and len(set(roots))==len(roots) and len(set(persons))==len(persons):out.append(dict(order=order,roots=roots,persons=persons,tense=assignments[('T',0)]))
 return out

def main():
 spec=json.loads((E/'src/SPEC.json').read_text());lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 packet=json.loads((R/spec['target']).read_text());source=json.loads((R/spec['source']).read_text());cases=json.loads(gzip.decompress((E/'artifacts/CASES.json.gz').read_bytes()));res=json.loads((E/'artifacts/RESULT.json').read_text())
 assert {k:len(v) for k,v in packet['panels'].items()}==spec['counts']
 assert [t['id'] for t in source['tables']]==['PRESENT','IMPERFECT']
 assert all(len(t['rows'])==6 and all(len(r)==3 for r in t['rows']) for t in source['tables'])
 predicted=json.loads((E/'artifacts/PREDICTIONS.json').read_text())['cells']
 expected_cells=[dict(table=t['id'],person=spec['persons'][r],channel=spec['channels'][c],cell_id=x['id'],prediction='HEAR(channel,person,tense)') for t in source['tables'] for r,row in enumerate(t['rows']) for c,x in enumerate(row)]
 assert predicted==expected_cells
 records={(x['panel'],x['window_id'],x['layout']):x for x in cases['rows']};assert len(records)==len(cases['rows'])
 orders=[''.join(o) for o in permutations('RPT')];checked=0;unresolved=0;expected_witnesses=[];win={}
 for panel,ws in packet['panels'].items():
  for w in ws:
   assert not w['page'].startswith('f84') and w['page']!='f116v'
   assert int(w['physical_folio'][1:])%2==1
   assert len(w['words'])==len(w['source_group_ids'])==18
   win[(panel,w['id'])]=w
   for layout in ['ROW_MAJOR','COLUMN_MAJOR']:
    rec=records[(panel,w['id'],layout)];checked+=1
    if rec['status']=='UNKNOWN_REMAINDER':unresolved+=1;continue
    m=[[w['words'][r*3+c if layout=='ROW_MAJOR' else c*6+r] for c in range(3)] for r in range(6)]
    if rec['status']=='CONTRADICTED_LENGTH_RECTANGLE':
     b=rec['certificate'];r,c=b['row'],b['column'];actual=len(m[r][c]);expected=len(m[r][0])+len(m[0][c])-len(m[0][0]);assert actual==b['observed'] and expected==b['expected'] and actual!=expected
     assert rec['factorizations']==0
    else:
     by_order={};local=[]
     for o in orders:
      fs=independently_factor(m,o);by_order[o]=len(fs);local+=fs
      for f in fs:expected_witnesses.append(dict(f,panel=panel,window_id=w['id'],layout=layout))
     assert by_order==rec['by_order'];assert len(local)==rec['factorizations']
     assert rec['status']==('LOCAL_FACTORIZATION' if local else 'CONTRADICTED_SHARED_FIELDS')
 assert checked==len(records)==sum(spec['counts'].values())*2
 actual_witnesses=[{k:v for k,v in x.items() if k!='id'} for x in cases['witnesses']];assert canon(expected_witnesses)==canon(actual_witnesses)
 ids={w['id']:w for w in cases['witnesses']};assert set(ids)==set(range(len(ids)))
 expected_pairs=[]
 for a,b in combinations(cases['witnesses'],2):
  if any(a[k]!=b[k] for k in ('panel','layout','order','roots','persons')) or a['tense']==b['tense']:continue
  aa=win[(a['panel'],a['window_id'])];bb=win[(b['panel'],b['window_id'])]
  if set(aa['source_group_ids']).isdisjoint(bb['source_group_ids']):expected_pairs.append((a['id'],b['id']))
 pairs=[(p['a'],p['b']) for p in cases['pairs']]
 if res['joins_complete']:assert sorted(pairs)==sorted(expected_pairs)
 else:assert set(pairs)<=set(expected_pairs)
 for p in cases['pairs']:
  assert p['temporal_assignments']==2 and p['channel_assignments']==6 and p['independent_meaning_capacity']==0
 assert res['counts']==dict(Counter(x['status'] for x in cases['rows']))
 assert res['local_factorizations']==len(ids) and res['paired_factorizations']==len(pairs)
 expected_status='RETAIN_COMPOSITIONAL_TABLE_CANDIDATES' if pairs else ('UNKNOWN_BOUNDED_SEARCH' if unresolved or not res['joins_complete'] else 'CONTRADICTED_COMPLETE_FEATURE_TABLES')
 assert res['status']==expected_status
 with (E/'artifacts/CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
 assert len(table)==len(records)
 for row in table:
  rec=records[(row['panel'],row['window_id'],row['layout'])];assert row['status']==rec['status'] and int(row['factorizations'])==rec['factorizations']
 out=dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),window_traversal_cases=checked,unknown_cases=unresolved,independent_factorizations=len(expected_witnesses),independent_pairs=len(expected_pairs),source_cells=36,validation='Independent integer-length extraction, all negative certificates, population and pair replay',scientific_meaning_confirmation=False)
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
