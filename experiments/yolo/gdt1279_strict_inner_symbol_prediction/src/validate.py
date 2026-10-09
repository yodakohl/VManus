"""Independent flat-cell reconstruction of matched transition predictions."""
import collections,gzip,hashlib,json,math,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def near(a,b):assert abs(a-b)<1e-10*max(1,abs(a),abs(b)),(a,b)
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));labels=json.loads((R/'experiments/yolo/gdt1264_interior_binary_alternation/artifacts/TRAIN.json').read_text())['labels'];alphabet=json.loads((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/src/SPEC.json').read_text())['signs']
 model=json.loads((B/'artifacts/MODEL.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());events=json.loads(gzip.decompress((B/'artifacts/EVENTS.json.gz').read_bytes()));assert hashlib.sha256((B/'artifacts/MODEL.json').read_bytes()).hexdigest()==json.loads((B/'artifacts/MODEL_LOCK.json').read_text())['sha256'];assert model['alphabet']==alphabet and model['alpha']==.5 and model['controls']==5
 records={};metadata={};fit={};fitstats={};eventmap={(e['reader'],e['id'],e['i']):e for e in events};assert len(eventmap)==len(events);used=set();sourcecount=0;checks={}
 def physical(row):return int(re.match('f([0-9]+)',row['page'])[1])
 for reader,rows in data.items():
  raw={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json').read_text())['lines']:
    for g in line['groups']:raw[g[0]]=(g,line['metadata'])
  for row in rows:
   g,m=raw[row['id']];assert row['ivtff_group_raw']==g[2] and row['kind']==m['kind']=='P' and reader==m['edition'] and row['page']==m['page'];assert not row['page'].startswith('f84') and row['page']!='f116v';metadata[reader,row['id']]=m['currier'];records[reader,row['id']]=row;sourcecount+=1
  counts=collections.defaultdict(collections.Counter);st=collections.Counter()
  for row in rows:
   units=row['units'];n=len(units)
   if physical(row)%2!=1 or n<4:continue
   st['groups']+=1
   for i,(previous,nextunit) in enumerate(zip(units,units[1:]),start=1):
    st['opportunities']+=1
    if previous not in labels:st['excluded_unknown_previous']+=1;continue
    st['scored_transitions']+=1;prefix=(metadata[reader,row['id']],n,i)
    for name,value in [('POS','ANY'),('BIT',str(labels[previous])),('EXACT',previous)]:counts[(name,)+prefix+(value,)][nextunit]+=1
  fit[reader]=counts;fitstats[reader]=dict(st)
  for name in ['POS','BIT','EXACT']:
   expected=[{'context':list(k[1:]),'counts':dict(sorted(v.items()))} for k,v in sorted(counts.items()) if k[0]==name];assert expected==model['tables'][reader][name]
  assert fitstats[reader]==model['train_counts'][reader]
  known={tuple(r['units'][1:-1]) for r in rows if physical(r)%2==1 and len(r['units'])>=4};by=collections.defaultdict(lambda:collections.defaultdict(list));census=collections.Counter();scored=0
  for row in rows:
   if physical(row)%2:continue
   census['all_groups']+=1;units=row['units'];n=len(units)
   if n<4:census['too_short_groups']+=1;continue
   census['eligible_groups']+=1;novel=tuple(units[1:-1]) not in known
   for i in range(1,n):
    census['opportunities']+=1;eid=(reader,row['id'],i);used.add(eid);e=eventmap[eid];reg='INNER' if 1<i<n-1 else 'EDGE'
    if units[i-1] not in labels:
     census['excluded_unknown_previous']+=1;assert e['status']=='UNKNOWN_PREVIOUS_CLASS' and e['region']==reg;continue
    census['scored_transitions']+=1;scored+=1;probs={};prefix=(metadata[reader,row['id']],n,i)
    for name,value in [('POS','ANY'),('BIT',str(labels[units[i-1]])),('EXACT',units[i-1])]:
     c=counts.get((name,)+prefix+(value,),collections.Counter());den=sum(c.values())+.5*len(alphabet);p=(c[units[i]]+.5)/den;probs[name]=math.log(p);near(e['logs'][name],probs[name])
     near(sum((c[a]+.5)/den for a in alphabet),1)
    assert (e['leaf'],e['n'],e['currier'],e['previous'],e['next'],e['region'],e['unseen_interior'])==(physical(row),n,prefix[0],units[i-1],units[i],reg,novel)
    for cohort in ['ALL']+(['UNSEEN_INTERIOR'] if novel else []):
     for a,b in [('EXACT','POS'),('EXACT','BIT'),('BIT','POS')]:by[cohort,reg,a+'-'+b][physical(row)].append(probs[a]-probs[b])
  assert dict(census)==result['readers'][reader]['census']
  for (cohort,reg,contrast),leaves in by.items():
   o=result['readers'][reader]['comparisons'][cohort][reg][contrast];N=sum(map(len,leaves.values()));L=len(leaves);means={str(k):sum(v)/len(v) for k,v in leaves.items()};avg=sum(means.values())/L;pos=sum(v>0 for v in means.values());assert set(means)==set(o['per_leaf'])
   for k,v in means.items():near(v,o['per_leaf'][k])
   assert (N,L,pos)==(o['transitions'],o['leaves'],o['positive_leaves']);near(avg,o['equal_leaf_gain']);near(sum(sum(v) for v in leaves.values())/N,o['event_mean_gain']);cap=N>=100 and L>=10;status='PASS' if cap and avg>=.01 and pos*3>=2*L else ('NONCONFIRMING' if cap else 'CAPACITY_STOP');assert o['status']==status
  checks[reader]={'transitions':scored,'excluded_unknown_previous':census['excluded_unknown_previous'],'status':'PASS'}
 assert used==set(eventmap) and sourcecount==model['source_groups_validated']
 p=[result['readers']['ZL3b']['comparisons'][c]['INNER']['EXACT-POS']['status'] for c in ['ALL','UNSEEN_INTERIOR']];status='INNER_EXACT_TRANSFER' if p==['PASS','PASS'] else ('CAPACITY_STOP' if 'CAPACITY_STOP' in p else 'NO_JOINT_INNER_TRANSFER');assert result['status']==status
 q=[result['readers']['ZL3b']['comparisons'][c]['INNER']['EXACT-BIT']['status'] for c in ['ALL','UNSEEN_INTERIOR']];extra='EXACT_IDENTITY_ADDS_PREDICTIVE_VALUE' if status=='INNER_EXACT_TRANSFER' and q==['PASS','PASS'] else 'NOT_ESTABLISHED';assert result['identity_increment']==extra
 v={'status':'PASS','source_groups':sourcecount,'readers':checks,'scope':'Independent flat-cell/source/logprobability/normalization/leaf/gate reconstruction; samecachedink, no physical or meaningvalidation.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
if __name__=='__main__':main()
