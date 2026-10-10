import collections,csv,gzip,hashlib,json,math,random,re
from pathlib import Path
B=Path(__file__).resolve().parents[1]; R=B.parents[2]
A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
F={f'c{h}h':h for h in 'ktpf'}
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def save(n,x):
 d=(json.dumps(x,indent=2)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(d,mtime=0) if n.endswith('.gz') else d)
def extract(u,order):
 source=[];events=[];i=0
 while i<len(u):
  g=u[i]
  if g in F:
   h=F[g];events.append((len(source),h,1));source.extend(['ch',h] if order=='BH' else [h,'ch']);i+=1
  elif i+1<len(u) and ((order=='BH' and g=='ch' and u[i+1] in 'ktpf') or (order=='HB' and g in 'ktpf' and u[i+1]=='ch')):
   h=u[i+1] if order=='BH' else g;events.append((len(source),h,0));source.extend(u[i:i+2]);i+=2
  else:source.append(g);i+=1
 return source,events

def score(es,ys,detail=False):
 global_counts=collections.defaultdict(lambda:[0,0]);local=collections.defaultdict(lambda:[0,0])
 for e,y in zip(es,ys):
  if e['train']:
   for table,key in [(global_counts,(e['c'],e['h'])),(local,(e['c'],e['h'],tuple(e['source'])))]:table[key][0]+=y;table[key][1]+=1
 leaves=collections.defaultdict(list);held=[]
 for e,y in zip(es,ys):
  if e['train']:continue
  f,n=global_counts[e['c'],e['h']];p=(f+.5)/(n+1);a,m=local[e['c'],e['h'],tuple(e['source'])];q=(a+2*p)/(m+2);gain=math.log((q if y else 1-q)/(p if y else 1-p));leaves[e['leaf']].append(gain)
  if detail:held.append({**e,'baseline_p':p,'word_p':q,'gain':gain,'train_word_opportunities':m})
 per={str(k):sum(v)/len(v) for k,v in sorted(leaves.items())};value=sum(per.values())/len(per) if per else 0
 if not detail:return value
 return {'equal_leaf_gain':value,'held_opportunities':sum(map(len,leaves.values())),'leaves':len(per),'positive_leaves':sum(x>0 for x in per.values()),'per_leaf':per,'train_rates':[{'c':k[0],'h':k[1],'fused':v[0],'N':v[1],'p':(v[0]+.5)/(v[1]+1)} for k,v in sorted(global_counts.items())]},held

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};out={};events={};held={};joins=0
 for ed in ['ZL3b','IT2a','RF1b']:
  source={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    for g in line['groups']:source[g[0]]=(line['metadata'],g)
  good=[]
  for row in data[ed]:
   m,g=source[row['id']];assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert m['page']==row['page'] and m['locus']==row['locus'] and m['edition']==ed and m['kind']==row['kind']=='P';assert g[2]==row['ivtff_group_raw'] and int(g[1])==int(row['source_group_index']) and g[3]==g[4]==row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert ''.join(row['units'])==g[2] and set(row['units'])<=set(A);joins+=1
   if m['currier'] in ['A','B']:good.append((row,m))
  for order in ['BH','HB']:
   key=ed+'_'+order;es=[]
   for row,m in good:
    s,ev=extract(row['units'],order);leaf=int(re.match(r'f(\d+)',row['page'])[1])
    for pos,h,y in ev:es.append({'id':row['id'],'page':row['page'],'locus':row['locus'],'units':row['units'],'source':s,'position':pos,'h':h,'y':y,'c':m['currier'],'leaf':leaf,'train':bool(leaf%2)})
   ys=[e['y'] for e in es];summary,he=score(es,ys,True);groups=collections.defaultdict(list)
   for i,e in enumerate(es):groups[e['c'],e['h']].append(i)
   rng=random.Random(1320);null=[]
   for rep in range(199):
    z=ys.copy()
    for k,ix in sorted(groups.items()):
     v=[ys[i] for i in ix];rng.shuffle(v)
     for i,y in zip(ix,v):z[i]=y
    null.append(score(es,z))
   p=(1+sum(x>=summary['equal_leaf_gain'] for x in null))/200;capacity=summary['held_opportunities']>=100 and summary['leaves']>=10;lead=capacity and summary['equal_leaf_gain']>=.01 and summary['positive_leaves']*3>=2*summary['leaves'] and p<=.05/6
   summary.update({'status':'NO_CAPACITY' if not capacity else ('WORD_CONDITIONED_CHOICE_GAIN' if lead else 'NO_RETAINED_WORD_GAIN'),'monte_carlo_p':p,'null_scores':null,'opportunities':len(es),'source_wholes':len({tuple(e['source']) for e in es})});out[key]=summary;events[key]=es;held[key]=he
   print(key,summary['status'],'gain',summary['equal_leaf_gain'],'positive',summary['positive_leaves'],'/',summary['leaves'],'p',p,flush=True)
 save('OPPORTUNITIES.json.gz',events);save('HELD_SCORES.json.gz',held);save('RESULT.json',{'status':'FIXED_OPTIONAL_CHOICE_COMPARISON','source_joins':joins,'cases':out})
if __name__=='__main__':main()
