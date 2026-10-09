import collections,gzip,hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
def close(a,b): assert math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-11),(a,b)
def main():
 lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
 for f,h in lock['hashes'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h
 model=json.loads((P/'artifacts/MODEL.json').read_text()); assert hashlib.sha256((P/'artifacts/MODEL.json').read_bytes()).hexdigest()==json.loads((P/'artifacts/MODEL_LOCK.json').read_text())['sha256']
 symbols=['a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh'];assert model['alphabet']==symbols and model['alpha']==.5
 sources={}
 for f in lock['hashes']:
  if '/SOURCE_' not in f:continue
  for line in json.loads((ROOT/f).read_text())['lines']:
   for g in line['groups']:
    assert g[0] not in sources;sources[g[0]]=(g,line['metadata'])
 data=json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()))
 train={}; rawtest=[]; known=collections.defaultdict(set);joined=0;fitcount=collections.Counter()
 for reader,rows in data.items():
  counts=[collections.defaultdict(lambda:[0]*22),collections.defaultdict(lambda:[0]*22)];train[reader]=counts
  for r in rows:
   g,m=sources[r['id']];assert r['ivtff_group_raw']==g[2]==''.join(r['units'])
   assert r['page']==m['page'] and r['locus']==m['locus'] and r['kind']==m['kind']=='P' and m['edition']==reader
   assert r['left_separator']==g[3] and r['right_separator']==g[4]
   assert not r['page'].startswith('f84') and r['page']!='f116v'; joined+=1
   digits=''
   for ch in r['page'][1:]:
    if not ch.isdigit():break
    digits+=ch
   leaf=int(digits);u=r['units'];n=len(u)
   if n<5:continue
   if leaf%2:known[reader].add(tuple(u[1:-1]))
   for i in range(n):
    if i<3 or i>n-2:continue
    c=(m['currier'],n,i);keys=[c+(u[i-1],),c+tuple(u[i-2:i])]
    if leaf%2:
     for j,key in enumerate(keys): counts[j][key][symbols.index(u[i])]+=1
     fitcount[reader]+=1
    else:rawtest.append((reader,r['id'],leaf,m['currier'],u,i,keys))
 assert joined==model['source_groups_joined']
 for reader,tables in train.items():
  assert model['fit'][reader]['events']==fitcount[reader] and model['fit'][reader]['known_interiors']==len(known[reader])
  for j,t in enumerate(tables):
   actual={tuple(v['context']):[v['counts'].get(s,0) for s in symbols] for v in model['tables'][reader]['M'+str(j+1)]}
   assert actual==dict(t)
 events=json.loads(gzip.decompress((P/'artifacts/EVENTS.json.gz').read_bytes()));assert len(events)==len(rawtest)
 actual={(e['reader'],e['id'],e['i']):e for e in events};assert len(actual)==len(events)
 buckets=collections.defaultdict(lambda:collections.defaultdict(list)); support=collections.defaultdict(collections.Counter)
 for reader,rid,leaf,currier,u,i,keys in rawtest:
  e=actual[reader,rid,i];novel=tuple(u[1:-1]) not in known[reader];logs=[];totals=[]
  assert (e['leaf'],e['currier'],e['n'],e['second_previous'],e['previous'],e['target'],e['unseen_interior'])==(leaf,currier,len(u),u[i-2],u[i-1],u[i],novel)
  for j,key in enumerate(keys):
   t=train[reader][j].get(key,[0]*22); denom=2*sum(t)+22;prob=[(2*n+1)/denom for n in t];close(sum(prob),1)
   logs.append(math.log(prob[symbols.index(u[i])])) ;totals.append(sum(t));close(logs[-1],e['logs'][j])
  assert totals==e['train_support']
  for c in ['ALL','UNSEEN_INTERIOR']:
   if c=='UNSEEN_INTERIOR' and not novel:continue
   buckets[reader,c][leaf].append(logs[1]-logs[0])
   for j,n in enumerate(totals):support[reader,c]['M'+str(j+1)+'_zero_support']+=n==0;support[reader,c]['M'+str(j+1)+'_under5_support']+=n<5
 result=json.loads((P/'artifacts/RESULT.json').read_text());statuses=[]
 for reader,cohorts in result['readers'].items():
  for c,v in cohorts.items():
   bs=buckets[reader,c];means={str(k):math.fsum(vals)/len(vals) for k,vals in bs.items()};N=sum(map(len,bs.values()));L=len(means);avg=math.fsum(means.values())/L if L else 0;positive=sum(x>0 for x in means.values())
   assert (N,L,positive)==(v['events'],v['leaves'],v['positive_leaves']);assert dict(support[reader,c])==v['support']
   close(avg,v['equal_leaf_gain']);close(math.fsum(math.fsum(a) for a in bs.values())/N if N else 0,v['event_mean_gain'])
   assert set(means)==set(v['per_leaf'])
   for k,x in means.items():close(x,v['per_leaf'][k])
   status='CAPACITY_STOP' if N<100 or L<10 else ('PASS' if avg>=.01 and positive*3>=L*2 else 'NONCONFIRMING');assert v['status']==status
   if reader=='ZL3b':statuses.append(status)
 expected='TWO_UNIT_PREDICTIVE_INCREMENT' if statuses==['PASS','PASS'] else ('CAPACITY_STOP' if 'CAPACITY_STOP' in statuses else 'NO_JOINT_TWO_UNIT_INCREMENT');assert result['status']==expected
 out={'status':'PASS','source_joins':joined,'independently_reconstructed_events':len(events),'scope':'Independent source joins, training tables, exact probabilities, cohort/leaf arithmetic and frozen decisions; no scientific independence or semantic confirmation.'}
 (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out))
if __name__=='__main__':main()
