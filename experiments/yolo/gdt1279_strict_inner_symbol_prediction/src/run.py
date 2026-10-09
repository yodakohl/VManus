import collections,gzip,hashlib,json,math,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
LABELFILE='experiments/yolo/gdt1264_interior_binary_alternation/artifacts/TRAIN.json'
SIGNS=['a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh']
MODELS=['POS','BIT','EXACT'];COHORTS=['ALL','UNSEEN_INTERIOR'];CONTRASTS=[('EXACT','POS'),('EXACT','BIT'),('BIT','POS')]
def save(n,x):(B/('artifacts/'+n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def leaf(r):return int(re.match(r'f(\d+)',r['page'])[1])
def key(m,c,prev,labels):return c+(('ANY' if m=='POS' else str(labels[prev]) if m=='BIT' else prev),)
def logp(counter,symbol):return math.log((counter[symbol]+.5)/(sum(counter.values())+11))
def controls():
 for c in [collections.Counter(),collections.Counter({'a':7,'o':1}),collections.Counter({'m':4})]:
  assert abs(sum(math.exp(logp(c,s)) for s in SIGNS)-1)<1e-12
 assert abs(logp(collections.Counter(),'a')+math.log(22))<1e-12
 assert abs(math.exp(logp(collections.Counter({'a':7,'o':1}),'a'))-7.5/19)<1e-12
 return 5

def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/SOURCE).read_bytes()));labels=json.loads((R/LABELFILE).read_text())['labels'];metas={};validated=0
 for reader,rows in data.items():
  lines={}
  for phase in ['DISCOVERY','EVALUATION']:
   src=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json').read_text())
   for line in src['lines']:lines[line['metadata']['locus']]=line
  for row in rows:
   assert not row['page'].startswith('f84') and row['page']!='f116v';line=lines[row['locus']];meta=line['metadata'];g=next(g for g in line['groups'] if g[0]==row['id']);assert g[2]==row['ivtff_group_raw'] and row['kind']==meta['kind']=='P' and row['page']==meta['page'] and reader==meta['edition'];assert set(row['units'])<=set(SIGNS)
   metas[(reader,row['id'])]=meta['currier'];validated+=1
 models={};fit_info={}
 for reader,rows in data.items():
  tables={m:collections.defaultdict(collections.Counter) for m in MODELS};info=collections.Counter()
  for row in rows:
   if not leaf(row)%2 or len(row['units'])<4:continue
   info['groups']+=1;u=row['units'];n=len(u)
   for i in range(1,n):
    info['opportunities']+=1
    if u[i-1] not in labels:info['excluded_unknown_previous']+=1;continue
    c=(metas[(reader,row['id'])],n,i);info['scored_transitions']+=1
    for m in MODELS:tables[m][key(m,c,u[i-1],labels)][u[i]]+=1
  models[reader]=tables;fit_info[reader]=dict(info)
 serialized={r:{m:[{'context':list(k),'counts':dict(sorted(v.items()))} for k,v in sorted(t.items())] for m,t in ts.items()} for r,ts in models.items()}
 save('MODEL',{'alphabet':SIGNS,'alpha':.5,'train_counts':fit_info,'tables':serialized,'source_groups_validated':validated,'controls':controls()});save('MODEL_LOCK',{'sha256':hashlib.sha256((B/'artifacts/MODEL.json').read_bytes()).hexdigest()})
 all_events=[];summaries={}
 for reader,rows in data.items():
  known={tuple(r['units'][1:-1]) for r in rows if leaf(r)%2 and len(r['units'])>=4};census=collections.Counter();buckets=collections.defaultdict(lambda:collections.defaultdict(list))
  for row in rows:
   if leaf(row)%2:continue
   census['all_groups']+=1;u=row['units'];n=len(u)
   if n<4:census['too_short_groups']+=1;continue
   census['eligible_groups']+=1;novel=tuple(u[1:-1]) not in known
   for i in range(1,n):
    region='EDGE' if i in [1,n-1] else 'INNER';census['opportunities']+=1
    if u[i-1] not in labels:
     census['excluded_unknown_previous']+=1;all_events.append({'reader':reader,'id':row['id'],'i':i,'status':'UNKNOWN_PREVIOUS_CLASS','region':region});continue
    census['scored_transitions']+=1;c=(metas[(reader,row['id'])],n,i);logs={m:logp(models[reader][m].get(key(m,c,u[i-1],labels),collections.Counter()),u[i]) for m in MODELS};event={'reader':reader,'id':row['id'],'i':i,'leaf':leaf(row),'n':n,'currier':c[0],'previous':u[i-1],'next':u[i],'region':region,'unseen_interior':novel,'logs':logs};all_events.append(event)
    for cohort in COHORTS:
     if cohort=='UNSEEN_INTERIOR' and not novel:continue
     for a,b in CONTRASTS:buckets[(cohort,region,a+'-'+b)][leaf(row)].append(logs[a]-logs[b])
  comp={}
  for cohort in COHORTS:
   comp[cohort]={}
   for region in ['EDGE','INNER']:
    comp[cohort][region]={}
    for a,b in CONTRASTS:
     vals=buckets[(cohort,region,a+'-'+b)];means={str(k):sum(v)/len(v) for k,v in sorted(vals.items())};N=sum(map(len,vals.values()));L=len(means);avg=sum(means.values())/L if L else 0;pos=sum(x>0 for x in means.values());capacity=N>=100 and L>=10
     status='PASS' if capacity and avg>=.01 and pos*3>=2*L else ('NONCONFIRMING' if capacity else 'CAPACITY_STOP')
     comp[cohort][region][a+'-'+b]={'transitions':N,'leaves':L,'positive_leaves':pos,'equal_leaf_gain':avg,'event_mean_gain':sum(sum(v) for v in vals.values())/N if N else 0,'per_leaf':means,'status':status}
  summaries[reader]={'census':dict(census),'comparisons':comp}
 primary=[summaries['ZL3b']['comparisons'][c]['INNER']['EXACT-POS']['status'] for c in COHORTS];status='INNER_EXACT_TRANSFER' if primary==['PASS','PASS'] else ('CAPACITY_STOP' if 'CAPACITY_STOP' in primary else 'NO_JOINT_INNER_TRANSFER');extra=[summaries['ZL3b']['comparisons'][c]['INNER']['EXACT-BIT']['status'] for c in COHORTS]
 result={'status':status,'identity_increment':'EXACT_IDENTITY_ADDS_PREDICTIVE_VALUE' if status=='INNER_EXACT_TRANSFER' and extra==['PASS','PASS'] else 'NOT_ESTABLISHED','readers':summaries,'claim_ceiling':'Fixed count-model nextunitprediction onsharedsupport;notcause,meaning,fullwriterorindependentconfirmation.'};save('RESULT',result);(B/'artifacts/EVENTS.json.gz').write_bytes(gzip.compress(json.dumps(all_events,separators=(',',':')).encode(),mtime=0))
 print(json.dumps({'status':status,'identity_increment':result['identity_increment'],'ZL3b':{c:{r:{k:{x:y for x,y in v.items() if x!='per_leaf'} for k,v in z.items()} for r,z in cs.items()} for c,cs in summaries['ZL3b']['comparisons'].items()}},indent=2))
if __name__=='__main__':main()
