import collections,gzip,hashlib,json,math,re
from pathlib import Path
B=Path(__file__).resolve().parents[1]; R=B.parents[2]
SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
SIGNS=['a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh']
def save(name,obj): (B/('artifacts/'+name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
def leaf(row): return int(re.match(r'f(\d+)',row['page'])[1])
def p(c,x): return (c[x]+.5)/(sum(c.values())+11)
def fixture():
 for c in [collections.Counter(),collections.Counter({'a':8,'e':8}),collections.Counter({'a':8})]: assert abs(sum(p(c,s) for s in SIGNS)-1)<1e-12
 assert p(collections.Counter(),'m')==1/22
 c1=collections.Counter({'a':8,'e':8}); c2=collections.Counter({'a':8})
 assert abs(p(c1,'a')-8.5/27)<1e-12 and abs(p(c2,'a')-8.5/19)<1e-12
 assert math.log(p(c2,'a')/p(c1,'a'))>0
 return 7

def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for path,h in lock['hashes'].items(): assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
 data=json.loads(gzip.decompress((R/SOURCE).read_bytes())); metas={}; joined=0
 for reader,rows in data.items():
  groups={}
  for phase in ['DISCOVERY','EVALUATION']:
   src=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json').read_text())
   for line in src['lines']:
    for g in line['groups']:
     assert g[0] not in groups;groups[g[0]]=(g,line['metadata'])
  for row in rows:
   assert not row['page'].startswith('f84') and row['page']!='f116v'
   g,m=groups[row['id']]
   assert row['ivtff_group_raw']==g[2]==''.join(row['units'])
   assert row['page']==m['page'] and row['locus']==m['locus'] and row['kind']==m['kind']=='P' and reader==m['edition']
   assert set(row['units'])<=set(SIGNS)
   metas[(reader,row['id'])]=m['currier'];joined+=1
 tables={}; known={}; fit={}
 for reader,rows in data.items():
  one=collections.defaultdict(collections.Counter);two=collections.defaultdict(collections.Counter);known[reader]=set();count=0
  for row in rows:
   u=row['units'];n=len(u)
   if not leaf(row)%2 or n<5:continue
   known[reader].add(tuple(u[1:-1]))
   for i in range(3,n-1):
    c=(metas[(reader,row['id'])],n,i);one[c+(u[i-1],)][u[i]]+=1;two[c+(u[i-2],u[i-1])][u[i]]+=1;count+=1
  tables[reader]=(one,two);fit[reader]={'events':count,'M1_contexts':len(one),'M2_contexts':len(two),'known_interiors':len(known[reader])}
 serial={r:{m:[{'context':list(k),'counts':dict(sorted(v.items()))} for k,v in sorted(t.items())] for m,t in zip(['M1','M2'],ts)} for r,ts in tables.items()}
 save('MODEL',{'alphabet':SIGNS,'alpha':.5,'fit':fit,'tables':serial,'source_groups_joined':joined,'fixture_assertions':fixture()})
 save('MODEL_LOCK',{'sha256':hashlib.sha256((B/'artifacts/MODEL.json').read_bytes()).hexdigest()})
 events=[]; results={}
 for reader,rows in data.items():
  by=collections.defaultdict(lambda:collections.defaultdict(list));supports=collections.defaultdict(collections.Counter)
  for row in rows:
   u=row['units'];n=len(u)
   if leaf(row)%2 or n<5:continue
   novel=tuple(u[1:-1]) not in known[reader]
   for i in range(3,n-1):
    c=(metas[(reader,row['id'])],n,i); c1=tables[reader][0].get(c+(u[i-1],),collections.Counter());c2=tables[reader][1].get(c+(u[i-2],u[i-1]),collections.Counter())
    logs=[math.log(p(t,u[i])) for t in [c1,c2]]; totals=[sum(t.values()) for t in [c1,c2]];delta=logs[1]-logs[0]
    events.append({'reader':reader,'id':row['id'],'i':i,'leaf':leaf(row),'currier':c[0],'n':n,'second_previous':u[i-2],'previous':u[i-1],'target':u[i],'unseen_interior':novel,'logs':logs,'train_support':totals})
    for cohort in ['ALL','UNSEEN_INTERIOR']:
     if cohort=='UNSEEN_INTERIOR' and not novel:continue
     by[cohort][leaf(row)].append(delta)
     for j in [0,1]:
      supports[cohort]['M'+str(j+1)+'_zero_support']+=int(totals[j]==0)
      supports[cohort]['M'+str(j+1)+'_under5_support']+=int(totals[j]<5)
  result={}
  for cohort in ['ALL','UNSEEN_INTERIOR']:
   buckets=by[cohort];means={str(k):sum(v)/len(v) for k,v in sorted(buckets.items())};N=sum(map(len,buckets.values()));L=len(means);mean=sum(means.values())/L if L else 0;pos=sum(v>0 for v in means.values());capacity=N>=100 and L>=10
   result[cohort]={'events':N,'leaves':L,'positive_leaves':pos,'equal_leaf_gain':mean,'event_mean_gain':sum(sum(v) for v in buckets.values())/N if N else 0,'per_leaf':means,'support':dict(supports[cohort]),'status':'PASS' if capacity and mean>=.01 and 3*pos>=2*L else ('NONCONFIRMING' if capacity else 'CAPACITY_STOP')}
  results[reader]=result
 statuses=[v['status'] for v in results['ZL3b'].values()]; status='TWO_UNIT_PREDICTIVE_INCREMENT' if statuses==['PASS','PASS'] else ('CAPACITY_STOP' if 'CAPACITY_STOP' in statuses else 'NO_JOINT_TWO_UNIT_INCREMENT')
 save('RESULT',{'status':status,'readers':results,'ceiling':'Fixed predictive models only; not minimal memory, primitive chunks, meaning, significance or first-order process rejection.'})
 (B/'artifacts/EVENTS.json.gz').write_bytes(gzip.compress(json.dumps(events,separators=(',',':')).encode(),mtime=0))
 print(json.dumps({'status':status,'readers':{r:{c:{k:v for k,v in x.items() if k!='per_leaf'} for c,x in cs.items()} for r,cs in results.items()}},indent=2))
if __name__=='__main__':main()
