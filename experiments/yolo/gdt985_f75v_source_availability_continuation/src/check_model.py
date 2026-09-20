# Independent finite-domain model; no SMT, runner, or result import.
import time

def check(words,start,question=None,budget=10):
 deadline=time.monotonic()+budget
 forms=sorted(set(words)); wi={w:i for i,w in enumerate(forms)};base=len(forms)
 domains=[set(range(9)) for _ in forms]+[{0,1} for _ in range(len(words)+1)]
 for w,c in [('ol',2),('or',7),('qol',1),('sheedy',1)]:
  if w in wi:domains[wi[w]]={c}
 domains[base]={start}
 if question:
  if question['kind']=='word':domains[wi[question['word']]]&={question['code']}
  if question['kind']=='final':domains[-1]&={question['state']}
 constraints=[(wi[w],base+i,base+i+1) for i,w in enumerate(words)]
 triples=[(code,before,(code//3,code%3)[before]) for code in range(9) for before in [0,1] if (code//3,code%3)[before]!=2]
 def search(ds):
  if time.monotonic()>deadline:raise TimeoutError
  changed=True
  while changed:
   changed=False
   for slots in constraints:
    allowed=[t for t in triples if all(v in ds[k] for k,v in zip(slots,t))]
    if not allowed:return None
    for j,k in enumerate(slots):
     new={t[j] for t in allowed}
     if new!=ds[k]:ds[k]=new;changed=True
  if any(not d for d in ds):return None
  unfixed=[i for i,d in enumerate(ds) if len(d)>1]
  if not unfixed:return ds
  k=min(unfixed,key=lambda i:(len(ds[i]), i<base, i))
  for value in sorted(ds[k]):
   trial=[set(d) for d in ds];trial[k]={value};got=search(trial)
   if got is not None:return got
  return None
 try:answer=search(domains)
 except TimeoutError:return {'status':'UNKNOWN'}
 if answer is None:return {'status':'UNSAT'}
 values=[next(iter(d)) for d in answer]
 return {'status':'SAT','dictionary':{w:[values[i]//3,values[i]%3] for w,i in wi.items()},'states':values[base:]}

def ground(words,start,dictionary,states):
 assert len(states)==len(words)+1 and states[0]==start
 assert set(dictionary)==set(words)
 for w,pair in dictionary.items():assert len(pair)==2 and set(pair)<={0,1,2}
 for w,c in [('ol',2),('or',7),('qol',1),('sheedy',1)]:
  if w in dictionary:assert dictionary[w]==[c//3,c%3]
 for i,w in enumerate(words):
  assert states[i] in [0,1] and states[i+1] in [0,1]
  assert dictionary[w][states[i]]==states[i+1]
