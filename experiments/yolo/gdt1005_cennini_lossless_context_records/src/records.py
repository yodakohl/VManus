"""Semantic records, lossless changed-field masks, and prefix-code capacity."""
import collections,heapq,itertools,math
FIELDS=('scope','modality','subject','predicate','object')
def build(records,writer,order):
 assert set(order)==set(FIELDS) and len(order)==5 and writer in ('FULL','DELTA')
 previous={};tokens=[];ends=[];changes=[];types={}
 for r in records:
  changed=[k for k in FIELDS if previous.get(k)!=r[k]] if writer=='DELTA' else list(FIELDS)
  if writer=='DELTA':
   mask='M:'+''.join('1' if k in changed else '0' for k in FIELDS);tokens.append(mask);types[mask]='MASK'
  for k in order:
   if k in changed:a='V:'+r[k];tokens.append(a);types[a]='VALUE'
  changes.append(changed);ends.append(len(tokens));previous={k:r[k] for k in FIELDS}
 return dict(atoms=tokens,record_ends=ends,types=types,changes=changes)
def inverse(atoms,writer,order):
 state={};result=[];i=0
 while i<len(atoms):
  if writer=='DELTA':
   mask=atoms[i];i+=1;assert mask.startswith('M:') and len(mask)==7 and set(mask[2:])<=set('01');changed={k for k,b in zip(FIELDS,mask[2:]) if b=='1'}
  else:changed=set(FIELDS)
  for k in order:
   if k in changed:assert i<len(atoms) and atoms[i].startswith('V:');state[k]=atoms[i][2:];i+=1
  assert set(state)==set(FIELDS);result.append(dict(state))
 return result

def profile(records,writer):
 b=build(records,writer,FIELDS);last=0;mins=[]
 for e in b['record_ends']:mins.append(e-last);last=e
 return dict(writer=writer,record_minimum_lengths=mins,frequencies={t:dict(collections.Counter(a for a in b['atoms'] if b['types'][a]==t)) for t in sorted(set(b['types'].values()))},atoms=len(b['atoms']),records=len(records))
def prefix_bound(frequencies,alphabet):
 costs={};traces={}
 for namespace,freq in frequencies.items():
  ws=list(freq.values());n=len(ws)
  if not n:costs[namespace]=0;traces[namespace]=[];continue
  if alphabet<2 and n>1:return dict(possible=False,reason='UNARY_PREFIX_CODE_CAPACITY',namespace=namespace)
  if n==1:costs[namespace]=ws[0];traces[namespace]=[];continue
  pad=(-(n-1))%(alphabet-1);heap=ws+[0]*pad;heapq.heapify(heap);cost=0;trace=[]
  while len(heap)>1:
   taken=[heapq.heappop(heap) for _ in range(alphabet)];s=sum(taken);cost+=s;trace.append(taken);heapq.heappush(heap,s)
  costs[namespace]=cost;traces[namespace]=trace
 return dict(possible=True,minimum_characters=sum(costs.values()),namespace_costs=costs,merges=traces)
def packing(minima,lengths):
 # Word j must consume one or two complete consecutive records.
 active={0};stages=[sorted(active)]
 for length in lengths:
  nxt=set()
  for start in active:
   for count in (1,2):
    stop=start+count
    if stop<=len(minima) and sum(minima[start:stop])<=length:nxt.add(stop)
  active=nxt;stages.append(sorted(active))
  if not active:return False,stages
 return len(minima) in active,stages

def prelim(p,words):
 n=len(words);records=p['records'];chars=sum(map(len,words))
 if not (math.ceil(records/2)<=n<=records):return dict(status='CONTRADICTED_RECORD_COUNT',observed_groups=n,source_records=records)
 if chars<p['atoms']:return dict(status='CONTRADICTED_MINIMUM_CHARACTERS',observed_characters=chars,minimum_characters=p['atoms'])
 okay,stages=packing(p['record_minimum_lengths'],list(map(len,words)))
 if not okay:return dict(status='CONTRADICTED_RECORD_PACKING',reachable_final_records=stages[-1],first_empty_word=len(stages)-1 if not stages[-1] else None)
 alphabet=len(set(''.join(words)));bound=prefix_bound(p['frequencies'],alphabet)
 if not bound['possible']:return dict(status='CONTRADICTED_PREFIX_CAPACITY',alphabet_size=alphabet,bound=bound)
 if chars<bound['minimum_characters']:return dict(status='CONTRADICTED_PREFIX_CAPACITY',observed_characters=chars,alphabet_size=alphabet,bound=bound)
 return dict(status='EXACT_SEARCH_REQUIRED',alphabet_size=alphabet,minimum_characters=bound['minimum_characters'])
