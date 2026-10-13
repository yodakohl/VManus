from pathlib import Path
from collections import defaultdict
import gzip,hashlib,json,math,random,re,csv
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,x):
 b=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');events=read(R/'experiments/yolo/gdt1316_fixed_half_form_prediction/artifacts/EVENTS.json.gz');emap={e['id']:e for e in events};assert len(emap)==len(events);allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={};all_scores={}
 for rd,rows in sorted(data.items()):
  groups=defaultdict(dict)
  for row in rows:
   assert row['edition']==rd and row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v') and row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   u=re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',row['ivtff_group_raw']);assert u==row['units'] and ''.join(u)==row['ivtff_group_raw'];i=int(row['source_group_index']);assert row['id']==f"{rd}|{row['locus']}|G{i:03d}";g=groups[(row['page'],row['locus'])];assert i not in g;g[i]=row
  runs=[]
  for key,g in sorted(groups.items()):
   buf=[];last=None
   for i in sorted(g):
    if last is not None and i!=last+1:runs.append(buf);buf=[]
    buf.append(g[i]);last=i
   if buf:runs.append(buf)
  records=[];pools=[];found=set();leaf_n=defaultdict(int)
  for ri,run in enumerate(runs):
   leaf=int(re.match(r'f(\d+)',run[0]['page']).group(1))
   if leaf%2:continue
   ws=[tuple(r['units']) for r in run];ps=[];cs=set();lengths=defaultdict(list)
   for i,row in enumerate(run):
    if len(ws[i])<4:ps.append(None);continue
    e=emap[row['id']];assert e['reader']==rd and e['leaf']==leaf and tuple(e['units'])==ws[i];found.add(e['id']);ps.append(e['mix_h']);cs.add(e['c']);lengths[len(ws[i])].append(i);leaf_n[leaf]+=1
   assert len(cs)<=1
   idx=len(records);records.append((leaf,[r['id'] for r in run],ws,ps))
   for n,ix in sorted(lengths.items()):pools.append((idx,ix))
  assert found=={e['id'] for e in events if e['reader']==rd}
  def evaluate(words,probs,detail=False):
   sums=defaultdict(float);details=[];available=0;cache_leaves=set();baseline=0.0
   for ri,(leaf,ids,oldw,oldp) in enumerate(records):
    seq=words[ri];pseq=probs[ri]
    for j,(w,p) in enumerate(zip(seq,pseq)):
     if p is None:continue
     history=[v for v in seq[max(0,j-4):j] if len(v)==len(w)];n=len(history);hits=sum(v==w for v in history);new=p if not n else .875*p+.125*hits/n;gain=math.log(new/p);sums[leaf]+=gain;baseline+=math.log(p)
     if n:available+=1;cache_leaves.add(leaf)
     if detail:details.append({'id':ids[j],'reader':rd,'leaf':leaf,'cache_size':n,'cache_hits':hits,'base_probability':p,'new_probability':new,'gain':gain})
   per={str(leaf):{'words':n,'gain':sums[leaf]/n} for leaf,n in sorted(leaf_n.items())};mean=math.fsum(v['gain'] for v in per.values())/len(per);token=math.fsum(sums.values())/sum(leaf_n.values())
   return mean,token,per,details,available,len(cache_leaves),baseline
  original_w=[r[2] for r in records];original_p=[r[3] for r in records];value,token,per,detail,available,cacheleaves,base_sum=evaluate(original_w,original_p,True)
  for s in detail:all_scores[s['id']]=s
  capacity=available>=100 and cacheleaves>=10;null=[];rng=random.Random(1373)
  if capacity:
   for rep in range(199):
    ws=[list(w) for w in original_w];ps=[list(p) for p in original_p]
    for ri,ix in pools:
     order=ix.copy();rng.shuffle(order)
     for dst,src in zip(ix,order):ws[ri][dst]=original_w[ri][src];ps[ri][dst]=original_p[ri][src]
    nv,_,_,_,_,_,bs=evaluate(ws,ps);assert abs(bs-base_sum)<1e-7;null.append(nv)
  mobile=bool(null) and max(null)-min(null)>1e-12;pv=(1+sum(v>=value for v in null))/200 if mobile else None;positive=sum(v['gain']>0 for v in per.values());material=value>=.01 and positive*3>=2*len(per)
  status='NO_CAPACITY' if not capacity else 'NO_SCORE_MOBILITY' if not mobile else 'NO_RETAINED_CACHE_GAIN' if not material else 'GAIN_WITHOUT_DEMONSTRATED_ORDER_EXCESS' if pv>.05/3 else 'ORDER_SENSITIVE_PREDICTIVE_INCREMENT'
  results[rd]={'words':sum(leaf_n.values()),'leaves':len(per),'cache_available':available,'cache_leaves':cacheleaves,'positive_leaves':positive,'equal_leaf_gain':value,'token_gain':token,'per_leaf':per,'null_scores':null,'p_or_null':pv,'status':status};print(rd,status,value,positive,pv,(min(null),max(null)) if null else None,flush=True)
 assert set(all_scores)==set(emap);save('SCORES.json.gz',[all_scores[e['id']] for e in events]);save('RESULT.json',{'status':'FROZEN_WHOLE_CACHE_ORDER_INCREMENT','readers':results})
if __name__=='__main__':main()
