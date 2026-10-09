import collections,gzip,hashlib,itertools,json,math,re,sys
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def ff(x):return [x.numerator,x.denominator]
def pair_stats(x,y):
 assert len(x)==len(y);cols=[a+b for a,b in zip(x,y)];k=cols.count(1);r=sum(x)-cols.count(2);constant=0;adj=0;runs=[];run=0
 for c in cols:
  if c==1:run+=1
  elif run:runs.append(run);run=0
 if run:runs.append(run)
 for a,b in zip(cols,cols[1:]):
  if a==b==1:adj+=1
  elif a==1 or b==1:constant+=1
  else:constant+=2*int(a!=b)
 expected=Fraction(constant)+(Fraction(4*r*(k-r)*adj,k*(k-1)) if k>=2 else 0)
 dp={0:(0,0)}
 for length in runs:
  new={}
  for used,(lo,hi) in dp.items():
   for count in range(length+1):
    used2=used+count
    if used2>r:continue
    least=0 if count in [0,length] else 1;most=min(length-1,2*min(count,length-count));a,b=lo+least,hi+most
    if used2 in new:a=min(a,new[used2][0]);b=max(b,new[used2][1])
    new[used2]=(a,b)
  dp=new
 lo,hi=dp[r];minimum=constant+2*lo;maximum=constant+2*hi;observed=sum(a!=b for a,b in zip(x,x[1:]))+sum(a!=b for a,b in zip(y,y[1:]));assert minimum<=observed<=maximum and minimum<=expected<=maximum
 if minimum==maximum:assert expected==observed
 return {'column_sums':cols,'variable_columns':k,'first_variable_ones':r,'variable_runs':runs,'constant':constant,'variable_adjacent_pairs':adj,'configurations':math.comb(k,r),'observed':observed,'expected':ff(expected),'minimum':minimum,'maximum':maximum,'informative':minimum<maximum}

def controls():
 count=0
 for n in range(1,6):
  for xy in itertools.product([0,1],repeat=2*n):
   x=list(xy[:n]);y=list(xy[n:]);s=pair_stats(x,y);cols=s['column_sums'];free=[j for j,v in enumerate(cols) if v==1];values=[]
   for chosen in itertools.combinations(free,s['first_variable_ones']):
    chosen=set(chosen);a=[int(v==2 or(v==1 and j in chosen)) for j,v in enumerate(cols)];b=[v-bit for v,bit in zip(cols,a)];assert sum(a)==sum(x) and sum(b)==sum(y)
    values.append(sum(u!=v for u,v in zip(a,a[1:]))+sum(u!=v for u,v in zip(b,b[1:])))
   assert len(values)==s['configurations'] and min(values)==s['minimum'] and max(values)==s['maximum'] and Fraction(sum(values),len(values))==Fraction(*s['expected']);count+=1
 # The separate-controls counterexample has no joint-pair excess.
 words=[[0,0,1],[0,1,0],[0,1,0],[0,1,0],[1,0,0]]
 assert sum(Fraction(pair_stats(words[i],words[i+1])['observed'])-Fraction(*pair_stats(words[i],words[i+1])['expected']) for i in [0,2])==0
 return count

def main():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 assert hashlib.sha256((R/s['fit']).read_bytes()).hexdigest()==json.loads((R/s['fit_lock']).read_text())['train_sha256']
 data=json.loads(gzip.decompress((R/s['source']).read_bytes()));labels=json.loads((R/s['fit']).read_text())['labels'];reports=[];packets=[];unpaired=[];exclusions=[];leaf=lambda r:int(re.match(r'f(\d+)',r['page'])[1])
 for reader in s['readers']:
  rows=data[reader];assert all(not r['page'].startswith('f84') and r['page']!='f116v' for r in rows)
  seenwhole={tuple(r['units']) for r in rows if leaf(r)%2};seeninner={tuple(r['units'][1:-1]) for r in rows if leaf(r)%2 and len(r['units'])-2>=s['minimum_interior_units']}
  for cohort in s['cohorts']:
   cells=collections.defaultdict(list);counts=collections.Counter();by_leaf=collections.defaultdict(lambda:{'groups':0,'edges':0,'observed':0,'expected':Fraction(0),'pairs':0,'informative_pairs':0,'unpaired_groups':0})
   for r in rows:
    if leaf(r)%2:continue
    inner=r['units'][1:-1]
    if cohort=='UNSEEN_WHOLE' and tuple(r['units']) in seenwhole:continue
    if cohort=='UNSEEN_INTERIOR' and tuple(inner) in seeninner:continue
    counts['source_groups']+=1
    if len(inner)<s['minimum_interior_units']:counts['too_short']+=1;continue
    counts['eligible_groups']+=1
    if not set(inner)<=set(labels):counts['unknown_unit_groups']+=1;exclusions.append({'reader':reader,'cohort':cohort,'id':r['id'],'reason':'UNSEEN_TRAIN_UNIT','whole_units':r['units']});continue
    bits=[labels[u] for u in inner];item={'id':r['id'],'page':r['page'],'leaf':leaf(r),'whole_units':r['units'],'interior':inner,'bits':bits};cells[(r['page'],len(inner))].append(item);counts['scorable_groups']+=1;by_leaf[leaf(r)]['groups']+=1;by_leaf[leaf(r)]['edges']+=len(inner)-1
   for (page,n),items in sorted(cells.items()):
    for index in range(0,len(items)-1,2):
     left,right=items[index:index+2];st=pair_stats(left['bits'],right['bits']);q=by_leaf[left['leaf']];q['pairs']+=1;q['informative_pairs']+=int(st['informative']);q['observed']+=st['observed'];q['expected']+=Fraction(*st['expected']);counts['pairs']+=1;counts['informative_pairs']+=int(st['informative']);packets.append({'reader':reader,'cohort':cohort,'page':page,'length':n,'pair_index':index//2,'left':left,'right':right,**st})
    if len(items)%2:
     item=items[-1];obs=sum(a!=b for a,b in zip(item['bits'],item['bits'][1:]));q=by_leaf[item['leaf']];q['unpaired_groups']+=1;q['observed']+=obs;q['expected']+=obs;counts['unpaired_groups']+=1;unpaired.append({'reader':reader,'cohort':cohort,**item})
   leafrows=[]
   for f,q in sorted(by_leaf.items()):
    excess=Fraction(q['observed'])-q['expected'];effect=excess/q['edges'];leafrows.append({'leaf':f,**{k:v for k,v in q.items() if k!='expected'},'expected':ff(q['expected']),'excess':ff(excess),'effect':ff(effect),'effect_float':float(effect),'informative':q['informative_pairs']>0})
   inf=[q for q in leafrows if q['informative']];mean=lambda rows:sum((Fraction(*q['effect']) for q in rows),Fraction(0))/len(rows) if rows else Fraction(0);avg=mean(inf);pos=sum(Fraction(*q['effect'])>0 for q in inf);pf=Fraction(pos,len(inf)) if inf else Fraction(0);capacity=len(inf)>=s['minimum_informative_leaves'];passed=capacity and pf>=Fraction(*s['positive_fraction']) and avg>=Fraction(*s['minimum_mean_excess'])
   reports.append({'reader':reader,'cohort':cohort,'counts':dict(counts),'scorable_leaves':len(leafrows),'informative_leaves':len(inf),'positive_informative_leaves':pos,'zero_informative_leaves':sum(Fraction(*q['effect'])==0 for q in inf),'mean_informative':ff(avg),'mean_informative_float':float(avg),'mean_all':ff(mean(leafrows)),'mean_all_float':float(mean(leafrows)),'positive_fraction':ff(pf),'capacity_pass':capacity,'gate_pass':passed,'leaves':leafrows})
 primary=[q for q in reports if q['reader']==s['primary_reader'] and q['cohort'] in s['primary_cohorts']];status='JOINT_CONTROL_CAPACITY_STOP' if not all(q['capacity_pass'] for q in primary) else 'PAIRED_POSITION_BAG_LEAD_RETAINED' if all(q['gate_pass'] for q in primary) else 'JOINT_PAIRED_LEAD_NOT_ESTABLISHED'
 result={'status':status,'reports':reports,'controls':controls(),'claim_ceiling':'Restricted paired joint word-bag/class-position comparison, no phonetics, meanings, unrestricted global-margin null or pvalue.'}
 for name,obj in [('RESULT',result),('UNPAIRED',unpaired),('EXCLUSIONS',exclusions)]: (B/('artifacts/'+name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
 (B/'artifacts/PAIRS.json.gz').write_bytes(gzip.compress(json.dumps(packets,separators=(',',':')).encode(),mtime=0));print(json.dumps({'status':status,'reports':[{k:v for k,v in q.items() if k!='leaves'} for q in reports]},indent=2))
if __name__=='__main__':
 if '--controls' in sys.argv:print(controls())
 else:main()
