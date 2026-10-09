"""Independent backward positive-weight recursion; no primary imports."""
import collections,functools,gzip,hashlib,json,math,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def near(a,b,tol=1e-9):assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 labels=json.loads((R/'experiments/yolo/gdt1264_interior_binary_alternation/artifacts/TRAIN.json').read_text())['labels'];data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));model=json.loads((B/'artifacts/MODEL.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());events=json.loads(gzip.decompress((B/'artifacts/EVENTS.json.gz').read_bytes()))
 assert hashlib.sha256((B/'artifacts/MODEL.json').read_bytes()).hexdigest()==json.loads((B/'artifacts/MODEL_LOCK.json').read_text())['sha256']
 def leaf(row):return int(re.match(r'f([0-9]+)',row['page']).group(1))
 def bits(row):return tuple(labels[u] for u in row['units'][1:-1])
 train=[r for r in data['ZL3b'] if leaf(r)%2==1 and len(r['units'])>=5 and all(u in labels for u in r['units'][1:-1])];counts=[[0,0] for _ in range(5)]
 for row in train:
  x=bits(row)
  for j,v in enumerate(x):counts[(5*j)//len(x)][v]+=1
 theta=tuple(math.log((v[1]+1)/(v[0]+1)) for v in counts)
 assert counts==model['position_counts_0_1'] and len(train)==model['training_groups'] and len({leaf(r) for r in train})==model['training_leaves']
 for a,b in zip(theta,model['theta']):near(a,b)
 @functools.lru_cache(None)
 def normalizer(n,k,beta):
  @functools.lru_cache(None)
  def remaining(i,ones,last):
   if ones<0 or ones>n-i:return 0.0
   if i==n:return float(ones==0)
   return sum(math.exp(theta[5*i//n]*v+beta*(last!=-1 and last!=v))*remaining(i+1,ones-v,v) for v in (0,1))
  total=remaining(0,k,-1);assert total>0 and math.isfinite(total);return math.log(total)
 def logp(x,beta):
  n=len(x);s=sum(x[j]!=x[j-1] for j in range(1,n));return sum(theta[5*j//n]*v for j,v in enumerate(x))+beta*s-normalizer(n,sum(x),beta)
 grid=[(b,sum(logp(bits(row),b) for row in train)) for b in [0,.25,.5,1,2]]
 for (b,ll),old in zip(grid,model['beta_grid']):assert b==old['beta'];near(ll,old['conditional_loglikelihood'],1e-11)
 best=max(ll for b,ll in grid);beta=min(b for b,ll in grid if best-ll<=1e-10);assert beta==model['selected_beta']==result['selected_beta'];assert model['controls_checked']==390
 keyed={(e['reader'],e['id']):e for e in events};assert len(keyed)==len(events);seen_ids=set();reader_checks={}
 for reader,rows in data.items():
  assert all(not r['page'].startswith('f84') and r['page']!='f116v' for r in rows)
  known_whole={tuple(r['units']) for r in rows if leaf(r)%2};known_inner={tuple(r['units'][1:-1]) for r in rows if leaf(r)%2 and len(r['units'])>=5}
  cohorts={c:collections.defaultdict(list) for c in ['ALL','UNSEEN_INTERIOR','UNSEEN_WHOLE']};census=collections.Counter();checked=0
  for row in rows:
   if leaf(row)%2:continue
   census['all_groups']+=1;inner=row['units'][1:-1]
   if len(inner)<3:census['too_short']+=1;continue
   key=(reader,row['id']);seen_ids.add(key);e=keyed[key]
   if any(u not in labels for u in inner):census['unknown_unit']+=1;assert e['status']=='UNKNOWN_UNIT' and e['units']==inner;continue
   census['scorable']+=1;checked+=1;x=bits(row);p0=logp(x,0);p1=logp(x,beta);gain=(p1-p0)/len(x)
   near(e['logp_base'],p0,1e-11);near(e['logp_switch'],p1,1e-11);near(e['gain_per_unit'],gain,1e-11)
   assert (e['n'],e['k'],e['leaf'],e['switches'])==(len(x),sum(x),leaf(row),sum(x[j]!=x[j-1] for j in range(1,len(x))))
   ui=tuple(inner) not in known_inner;uw=tuple(row['units']) not in known_whole;assert e['unseen_interior']==ui and e['unseen_whole']==uw
   cohorts['ALL'][leaf(row)].append(gain)
   if ui:cohorts['UNSEEN_INTERIOR'][leaf(row)].append(gain)
   if uw:cohorts['UNSEEN_WHOLE'][leaf(row)].append(gain)
  assert dict(census)==result['readers'][reader]['census']
  for cohort,leaves in cohorts.items():
   saved=result['readers'][reader]['cohorts'][cohort];assert set(saved['per_leaf'])=={str(k) for k in leaves}
   means=[sum(v)/len(v) for v in leaves.values()];N=sum(map(len,leaves.values()));avg=sum(means)/len(means);positive=sum(m>0 for m in means)
   for l,v in leaves.items():near(saved['per_leaf'][str(l)],sum(v)/len(v),1e-11)
   near(saved['equal_leaf_gain'],avg,1e-11);near(saved['event_mean_gain'],sum(sum(v) for v in leaves.values())/N,1e-11)
   assert (saved['groups'],saved['leaves'],saved['positive_leaves'])==(N,len(leaves),positive)
   cap=N>=100 and len(leaves)>=10;status='PASS' if cap and avg>=.01 and positive*3>=2*len(leaves) else ('NONCONFIRMING' if cap else 'CAPACITY_STOP');assert saved['status']==status
  reader_checks[reader]={'events':checked,'status':'PASS'}
 assert seen_ids==set(keyed)
 primary=[result['readers']['ZL3b']['cohorts'][c]['status'] for c in ['ALL','UNSEEN_INTERIOR']];status='PASS_BOTH' if primary==['PASS','PASS'] else ('CAPACITY_STOP' if 'CAPACITY_STOP' in primary else 'NO_JOINT_MATERIAL_PREDICTION');assert result['status']==status
 out={'status':'PASS','readers':reader_checks,'validation_method':'Independent backward positive-weight recursion, train/grid/source/event/leaf/gate reconstruction','limits':'Software and source consistency, not independentdata or content/meaning validation.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
