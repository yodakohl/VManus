import bisect, collections, csv, gzip, hashlib, itertools, json, math, random, re
from pathlib import Path
B=Path(__file__).resolve().parents[1]; R=B.parents[2]
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
READERS=['ZL3b','IT2a','RF1b']; SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'

def save(name,value):
 (B/'artifacts'/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def load_rows():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items(): assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 data=json.loads(gzip.decompress((R/SOURCE).read_bytes())); out={}; joined=0
 for reader in READERS:
  lines={}
  for phase in ['DISCOVERY','EVALUATION']:
   d=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json').read_text())
   for line in d['lines']: lines[line['metadata']['locus']]=line
  rows=[]
  for row in data[reader]:
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v']
   line=lines[row['locus']]; meta=line['metadata']; g=next(g for g in line['groups'] if g[0]==row['id'])
   assert g[2]==row['ivtff_group_raw'] and row['kind']==meta['kind']=='P' and row['page']==meta['page'] and reader==meta['edition']
   assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE' and ''.join(row['units'])==row['ivtff_group_raw'] and set(row['units'])<=set(SIGNS)
   joined+=1
   if len(row['units'])<4: continue
   leaf=int(re.match(r'f(\d+)',row['page'])[1]); u=tuple(row['units'])
   rows.append({'id':row['id'],'locus':row['locus'],'page':row['page'],'leaf':leaf,'c':meta['currier'],'u':u})
  out[reader]=rows
 return out,joined

def fit(rows):
 t=collections.defaultdict(collections.Counter); words=collections.defaultdict(collections.Counter)
 for row in rows:
  if not row['leaf']%2: continue
  u=row['u']; c=row['c']; n=len(u); words[(c,n)][u]+=1
  for i,s in enumerate(u): t[(c,n,i,u[i-1] if i else '^')][s]+=1
 return t,words

def probability(t,c,u):
 p=1.0; n=len(u)
 for i,s in enumerate(u):
  counts=t.get((c,n,i,u[i-1] if i else '^'),{})
  p*=(counts.get(s,0)+.5)/(sum(counts.values())+11)
 return p

def summarize(events):
 result={}
 for cohort in ['ALL','Q_POSITIVE','Q_ZERO','GLOBAL_UNSEEN']:
  es=[e for e in events if cohort=='ALL' or (cohort=='Q_POSITIVE' and e['q']>0) or (cohort=='Q_ZERO' and e['q']==0) or (cohort=='GLOBAL_UNSEEN' and e['global_unseen'])]
  leaves=collections.defaultdict(list)
  for e in es: leaves[e['leaf']].append(e['gain'])
  means={str(k):sum(v)/len(v) for k,v in sorted(leaves.items())}; N=len(es); L=len(means); avg=sum(means.values())/L if L else None; pos=sum(v>0 for v in means.values())
  capacity=N>=100 and L>=10
  result[cohort]={'words':N,'leaves':L,'positive_leaves':pos,'equal_leaf_gain':avg,'token_mean_gain':sum(e['gain'] for e in es)/N if N else None,'mean_m1_loss':-sum(math.log(e['p']) for e in es)/N if N else None,'mean_mix_loss':-sum(math.log(e['mix']) for e in es)/N if N else None,'per_leaf':means,'material_gate':bool(capacity and avg>=.01 and pos*3>=2*L)}
 return result

def evaluate(rows,t,words,full=True):
 known={w for v in words.values() for w in v}; events=[]
 for row in rows:
  if row['leaf']%2: continue
  u=row['u']; c=row['c']; counts=words.get((c,len(u)),{}); N=sum(counts.values()); q=counts.get(u,0)/N if N else 0; p=probability(t,c,u); mix=(p+q)/2 if N else p
  events.append({'id':row['id'],'leaf':row['leaf'],'c':c,'units':u,'p':p,'q':q,'mix':mix,'gain':math.log(mix/p),'cell_train_N':N,'global_unseen':u not in known})
 return summarize(events),events

def draw_rows(rows,t,seed):
 rng=random.Random(seed); tables={}; out=[]; digest=hashlib.sha256()
 for row in rows:
  c=row['c']; n=len(row['u']); u=[]
  for i in range(n):
   k=(c,n,i,u[-1] if i else '^')
   if k not in tables:
    cnt=t.get(k,{}); weights=[cnt.get(s,0)+.5 for s in SIGNS]; tables[k]=list(itertools.accumulate(weights))
   cumulative=tables[k]; u.append(SIGNS[bisect.bisect_right(cumulative,rng.random()*cumulative[-1])])
  digest.update((' '.join(u)+'\n').encode()); out.append({**row,'u':tuple(u)})
 return out,digest.hexdigest()

def fixtures():
 ws=list(itertools.product('ab',repeat=4)); even=[w for w in ws if w.count('b')%2==0]
 p={w:1/16 for w in ws}; q={w:1/8 if w in even else 0 for w in ws}; mix={w:(p[w]+q[w])/2 for w in ws}
 assert sum(p.values())==sum(q.values())==sum(mix.values())==1
 for w in ws: assert abs(math.log(mix[w]/p[w])-(math.log(1.5) if w in even else -math.log(2)))<1e-12
 assert all(math.log(((p[w]+p[w])/2)/p[w])==0 for w in ws)
 return {'status':'PASS','binary_words':16,'parity_gain':math.log(1.5),'unseen_penalty':-math.log(2)}

def main():
 f=fixtures(); data,joins=load_rows(); all_events=[]; results={}; models={}; simulations={}
 # Fit and seal all native TRAIN tables before any held scoring.
 fits={reader:fit(rows) for reader,rows in data.items()}
 for reader,(t,words) in fits.items():
  models[reader]={'m1':[{'context':list(k),'counts':dict(sorted(v.items()))} for k,v in sorted(t.items())],'whole':[{'cell':list(k),'counts':[{'units':w,'count':v} for w,v in sorted(counts.items())]} for k,counts in sorted(words.items())]}
 save('MODEL.json',models); save('MODEL_LOCK.json',{'sha256':hashlib.sha256((B/'artifacts/MODEL.json').read_bytes()).hexdigest()})
 for ri,reader in enumerate(READERS):
  rows=data[reader]; t,words=fits[reader]; scores,events=evaluate(rows,t,words); all_events.extend({'reader':reader,**e} for e in events)
  sims=[]
  for rep in range(32):
   seed=1308000+1000*ri+rep; sr,dh=draw_rows(rows,t,seed); st,sw=fit(sr); ss,_=evaluate(sr,st,sw)
   sims.append({'replicate':rep,'seed':seed,'draw_sha256':dh,'ALL':ss['ALL']})
  native=scores['ALL']['equal_leaf_gain']; ceiling=max(s['ALL']['equal_leaf_gain'] for s in sims); lead=scores['ALL']['material_gate'] and native>ceiling
  results[reader]={'cohorts':scores,'train_words':sum(sum(v.values()) for v in words.values()),'train_distinct_wholes':len({w for v in words.values() for w in v}),'train_whole_cell_entries':sum(map(len,words.values())),'train_cells':len(words),'m1_observed_contexts':len(t),'synthetic_max_gain':ceiling,'synthetic_min_gain':min(s['ALL']['equal_leaf_gain'] for s in sims),'synthetic_at_least_native':sum(s['ALL']['equal_leaf_gain']>=native for s in sims),'lead':lead}
  simulations[reader]=sims
  print(reader,'lead',lead,'native_gain',native,'synthetic_max',ceiling,flush=True)
 save('RESULT.json',{'status':'WHOLE_FORM_PREDICTIVE_LEAD' if results['ZL3b']['lead'] else 'NO_WHOLE_FORM_LEAD','joined_groups':joins,'fixtures':f,'readers':results,'claim_ceiling':'Fixed predictor comparison; no lexical mechanism, native meaning, universal M1 rejection or independent confirmation.'})
 save('SIMULATIONS.json',simulations)
 (B/'artifacts/EVENTS.json.gz').write_bytes(gzip.compress(json.dumps(all_events,separators=(',',':')).encode(),mtime=0))
if __name__=='__main__': main()
