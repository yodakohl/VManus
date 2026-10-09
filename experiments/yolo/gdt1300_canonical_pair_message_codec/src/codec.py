"""Finite canonical-pair codec. No native word meanings or whole-word codebook."""
from collections import Counter
import hashlib,heapq,json,re
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
PAT=re.compile(r'c[ktpf]h|ch|sh|[aoeindqysrlmktpf]')
END='\0'
def parse(w):
 u=PAT.findall(w)
 if ''.join(u)!=w:raise ValueError('outside working alphabet')
 return [SIGNS.index(g) for g in u]
def sha(data):return hashlib.sha256(data).hexdigest()
def huffman(weights):
 heap=[]
 for key,w in sorted(weights.items()):
  assert w>0;heapq.heappush(heap,(w,key,('L',key)))
 while len(heap)>1:
  a,b=heapq.heappop(heap),heapq.heappop(heap)
  heapq.heappush(heap,(a[0]+b[0],min(a[1],b[1]),('N',a[2],b[2])))
 codes={}
 def walk(node,s):
  if node[0]=='L':codes[node[1]]=s
  else:walk(node[1],s+'0');walk(node[2],s+'1')
 walk(heap[0][2],'');return codes
def greedy(units,pairs):
 lookup={tuple(p):22+i for i,p in enumerate(pairs)};tokens=[];i=0
 while i<len(units):
  pair=tuple(units[i:i+2])
  if len(pair)==2 and pair in lookup:tokens.append(lookup[pair]);i+=2
  else:tokens.append(units[i]);i+=1
 return tokens
def cls(unit,spec):
 g=SIGNS[unit]
 return '0' if g in spec['class0'] else '1' if g in spec['class1'] else 'U'
def key_for(phase,prev):return phase if phase in ('SINGLE','HEAD') else phase+'|'+str(prev)
def build_model(train,streams,spec):
 pair_counts=Counter((a,b) for row in train for a,b in zip(row['units'],row['units'][1:]))
 ranked=sorted(pair_counts,key=lambda p:(-pair_counts[p],SIGNS.index(p[0]),SIGNS.index(p[1])))[:spec['pairs']]
 pairs=[[SIGNS.index(a),SIGNS.index(b)] for a,b in ranked];vocab=[[i] for i in range(22)]+pairs;V=len(vocab)
 roles=['SINGLE','HEAD']+[p+'_'+c for p in ['MIDDLE','TAIL'] for c in ['0','1','U']]
 counts={r:[0]*V for r in roles};Tcounts=Counter();train_ids=[]
 for row in train:
  ids=greedy([SIGNS.index(g) for g in row['units']],pairs);T=len(ids)
  if T>13:raise ValueError('TRAIN_T_CAPACITY_STOP')
  Tcounts[T]+=1;train_ids.append(row['id'])
  for j,t in enumerate(ids):
   if T==1:counts['SINGLE'][t]+=1
   elif j==0:counts['HEAD'][t]+=1
   else:
    p='TAIL' if j==T-1 else 'MIDDLE';c=cls(vocab[ids[j-1]][-1],spec);counts[p+'_U'][t]+=1
    if c!='U':counts[p+'_'+c][t]+=1
 tables=[];contexts={};dedup={};pairset={tuple(p) for p in pairs}
 for phase,prev in [('SINGLE',None),('HEAD',None)]+[(p,i) for p in ['MIDDLE','TAIL'] for i in range(V)]:
  role=phase if prev is None else phase+'_'+cls(vocab[prev][-1],spec)
  allowed=[i for i in range(V) if prev is None or len(vocab[prev])==2 or (vocab[prev][0],vocab[i][0]) not in pairset]
  assert len(allowed)>=6
  codes=huffman({i:2*counts[role][i]+1 for i in allowed});sig=tuple(sorted(codes.items()))
  if sig not in dedup:dedup[sig]=len(tables);tables.append({str(k):v for k,v in codes.items()})
  contexts[key_for(phase,prev)]=dedup[sig]
 source_counts=Counter(c for text in streams.values() for c in text);assert END not in source_counts;source_counts[END]=len(streams);chars=sorted(source_counts)
 source_codes=huffman({i:source_counts[c] for i,c in enumerate(chars)})
 return {'signs':SIGNS,'pairs':pairs,'pair_counts':[pair_counts[p] for p in ranked],'vocabulary':vocab,'role_counts':counts,'T_counts':{str(t):Tcounts[t] for t in range(1,14)},'T_codes':{str(k):v for k,v in huffman({t:2*Tcounts[t]+1 for t in range(1,14)}).items()},'tables':tables,'contexts':contexts,'source_counts':dict(source_counts),'source_codes':{c:source_codes[i] for i,c in enumerate(chars)},'train_groups':len(train),'train_ids_sha256':sha(('\n'.join(train_ids)).encode()),'output_lookup_entries':sum(map(len,tables)),'unique_output_tables':len(tables),'source_table_entries':len(chars),'length_table_entries':13}
def trie(codes):
 root={}
 for value,code in codes.items():
  assert code;node=root
  for bit in code:node=node.setdefault(bit,{})
  assert not node;node['value']=value
 def check(node):
  if 'value' in node:assert len(node)==1
  else:assert set(node)=={'0','1'};check(node['0']);check(node['1'])
 check(root);return root
class Codec:
 def __init__(self,model):
  self.m=model;self.count_tree=trie({int(k):v for k,v in model['T_codes'].items()});self.trees=[trie({int(k):v for k,v in d.items()}) for d in model['tables']];self.source_tree=trie(model['source_codes'])
 def draw(self,tree,bit):
  node=tree
  while 'value' not in node:node=node[bit()]
  return node['value']
 def word(self,bit):
  T=self.draw(self.count_tree,bit);tokens=[]
  for j in range(T):
   p='SINGLE' if T==1 else 'HEAD' if j==0 else 'TAIL' if j==T-1 else 'MIDDLE'
   table=self.m['contexts'][key_for(p,None if j==0 else tokens[-1])];tokens.append(self.draw(self.trees[table],bit))
  units=[u for t in tokens for u in self.m['vocabulary'][t]];assert greedy(units,self.m['pairs'])==tokens
  return ''.join(SIGNS[u] for u in units)
 def encode(self,text):
  if END in text or not set(text)<=set(self.m['source_codes']):raise ValueError('unsupported source character')
  bits=''.join(self.m['source_codes'][c] for c in text+END);pos=0
  def bit():
   nonlocal pos
   value=bits[pos] if pos<len(bits) else '0';pos+=1;return value
  words=[]
  while pos<len(bits):words.append(self.word(bit))
  return words,{'source_bits':len(bits),'padding_bits':pos-len(bits),'source_sha256':sha(text.encode()),'word_count':len(words)}
 def bits(self,words):
  chunks=[]
  for w in words:
   ids=greedy(parse(w),self.m['pairs']);T=len(ids)
   if not 1<=T<=13:raise ValueError('token count')
   chunks.append(self.m['T_codes'][str(T)])
   for j,t in enumerate(ids):
    phase='SINGLE' if T==1 else 'HEAD' if j==0 else 'TAIL' if j==T-1 else 'MIDDLE';table=self.m['tables'][self.m['contexts'][key_for(phase,None if j==0 else ids[j-1])]]
    if str(t) not in table:raise ValueError('noncanonical token transition')
    chunks.append(table[str(t)])
  return ''.join(chunks)
 def decode(self,words,canonical=True):
  bits=self.bits(words);node=self.source_tree;text=[];stop=None
  for i,b in enumerate(bits):
   node=node[b]
   if 'value' in node:
    c=node['value']
    if c==END:stop=i+1;break
    text.append(c);node=self.source_tree
  if stop is None:raise ValueError('missing source END')
  if any(b!='0' for b in bits[stop:]):raise ValueError('nonzero padding')
  text=''.join(text)
  if canonical and self.encode(text)[0]!=words:raise ValueError('nonminimal padding/additional words')
  return text
