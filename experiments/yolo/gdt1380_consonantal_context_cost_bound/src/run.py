import csv,gzip,hashlib,itertools,json,math,re
from collections import Counter,defaultdict
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
from functools import lru_cache
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
C='bcdfghjklmnpqrstvwxyz';A=C+' ';SCALE=2**32;LETTERS='abcdefghijklmnopqrstuvxyz'
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def save(n,x):
 raw=(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(raw,mtime=0) if n.endswith('.gz') else raw)
@lru_cache(None)
def logs(n):
 with localcontext() as c:
  c.prec=60
  if n==1:return Decimal(0),Decimal(0)
  x=Decimal(n).ln();return x.next_minus(),x.next_plus()
@lru_cache(None)
def ticks(N,D):
 assert 0<N<=D
 g=math.gcd(N,D);a=N//g;b=D//g
 if not(a&(a-1)) and not(b&(b-1)):
  t=(b.bit_length()-a.bit_length())*SCALE;return t,t
 nl,nu=logs(N);dl,du=logs(D);bl,bu=logs(2)
 with localcontext() as c:
  c.prec=60;c.rounding=ROUND_FLOOR
  lo=max(Decimal(0),dl-nu)/bu
  low=int((lo*SCALE).to_integral_value(rounding=ROUND_FLOOR))
 with localcontext() as c:
  c.prec=60;c.rounding=ROUND_CEILING
  hi=(du-nl)/bl
  high=int((hi*SCALE).to_integral_value(rounding=ROUND_CEILING))
 assert 0<=low<=high;return low,high

def pre(w):
 prefix='NONE';h=w
 for x in ('che','ch','sh','t','s','d','q'):
  if h.startswith(x) and len(h)>len(x):prefix=x;h=h[len(x):];break
 if h.endswith('dy') and len(h)>2:h=h[:-2]
 if h.endswith('m') and len(h)>1:h=h[:-1]
 for x in ('aiin','air','ain','ar','al'):
  if h.endswith(x) and len(h)>len(x):h=h[:-len(x)];break
 if prefix in ('ch','che','sh') and h.startswith('d') and len(h)>1:h=h[1:]
 assert h;return h

def corpus(spec):
 allowed={x['page'] for x in csv.DictReader((R/spec['allowlist']).open(),delimiter='\t')};out={}
 for ed in spec['readers']:
  selected=[];rejected=[];seen=set()
  for phase in ('DISCOVERY','EVALUATION'):
   entry,=[x for x in spec['inputs'] if x['path'].endswith(f'SOURCE_{phase}_{ed}.json')]
   assert hashlib.sha256((R/entry['path']).read_bytes()).hexdigest()==entry['sha256']
   data=read(R/entry['path']);columns=data['group_columns'];assert columns==spec['group_columns']
   for line in data['lines']:
    m=line['metadata'];page=m['page'];locus=m['locus']
    if page not in allowed or page in ('f1r','f116v') or page.startswith('f84') or locus=='f102v2.33' or m['kind']!='P':continue
    assert m['edition']==ed and locus not in seen;seen.add(locus)
    rows=sorted([dict(zip(columns,v)) for v in line['groups']],key=lambda x:int(x['source_group_index']));n=int(m['source_group_count']);bad=[]
    if n<1 or [int(v['source_group_index']) for v in rows]!=list(range(1,n+1)):bad.append('indices')
    if len({v['source_group_id'] for v in rows})!=len(rows) or any(v['source_group_id']!=f"{ed}|{locus}|G{int(v['source_group_index']):03d}" for v in rows):bad.append('ids')
    if any(x['right_separator']!='DEFINITE_SPACE' or y['left_separator']!='DEFINITE_SPACE' for x,y in zip(rows,rows[1:])):bad.append('seams')
    if any(not v['ivtff_group_raw'] or not set(v['ivtff_group_raw'])<=set(LETTERS) for v in rows):bad.append('literal')
    if bad:rejected.append({'page':page,'locus':locus,'reasons':bad})
    else:selected.append({'metadata':m,'groups':line['groups'],'hosts':[pre(v['ivtff_group_raw']) for v in rows]})
  selected.sort(key=lambda x:(x['metadata']['page'],x['metadata']['locus']));rejected.sort(key=lambda x:(x['page'],x['locus']))
  freq=Counter(w for l in selected for w in l['hosts']);licensed={h for h in freq if freq['o'+h] and freq['ot'+h]}|{'ar','al','ol'}
  contexts=defaultdict(Counter);active=set();events=groups=0
  for line in selected:
   line['hosts']=[w[2:] if w.startswith('ot') and w[2:] in licensed else w[1:] if w.startswith('o') and w[1:] in licensed else w for w in line['hosts']]
   assert all(line['hosts']);groups+=len(line['hosts']);h=('^','^')
   for x in ' '.join(line['hosts']):contexts[h][x]+=1;events+=1;active.add(x) if x!=' ' else None;h=(h[1],x)
  out[ed]={'lines':selected,'rejected':rejected,'licensed':sorted(licensed),'contexts':[{'context':list(k),'counts':dict(sorted(v.items()))} for k,v in sorted(contexts.items())],'active':sorted(active),'events':events,'groups':groups}
 return out

def kt(rows,K):
 lo=hi=0
 for row in rows:
  counts=row['counts'].values();T=sum(counts)
  for t in range(T):a,b=ticks(1,2*t+K);lo+=a;hi+=b
  for n in counts:
   for t in range(n):a,b=ticks(1,2*t+1);lo-=b;hi-=a
 return lo,hi

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 spec=read(B/'src/SPEC.json');models=read(B/'artifacts/MODEL_COUNTS.json.gz');data=corpus(spec);save('CORPUS.json.gz',data)
 domain=C+' ^';costs={}
 for pack,model in sorted(models.items()):
  rows={tuple(x['context']):x['counts'] for x in model['rows']};costs[pack]={}
  for ctx in itertools.product(domain,repeat=2):
   v=rows.get(ctx,[0]*22);den=2*sum(v)+22;lower=[ticks(2*n+1,den)[0] for n in v]
   costs[pack][ctx]=(sorted(lower[:21]),lower[21])
 results={}
 for ed,x in data.items():
  m=len(x['active']);r={'lines':len(x['lines']),'groups':x['groups'],'events':x['events'],'active_symbols':x['active'],'context_count':len(x['contexts']),'kt_lo':None,'kt_hi':None,'key_lo':None,'key_hi':None,'selector_lo':None,'selector_hi':None,'packs':{}}
  if not x['events']:r['status']='NO_EVENTS'
  elif m>21:r['status']='EMPTY_INJECTIVE_FAMILY'
  else:
   r['kt_lo'],r['kt_hi']=kt(x['contexts'],m+1);r['key_lo'],r['key_hi']=ticks(1,math.prod(range(22-m,22)));r['selector_lo'],r['selector_hi']=ticks(1,6)
   for pack in sorted(models):
    cert=[];payload=0
    for row in x['contexts']:
     ctx=tuple(row['context']);w=sorted([n for k,n in row['counts'].items() if k!=' '],reverse=True);space=row['counts'].get(' ',0)
     domains=[(s,) if s in ('^',' ') else C for s in ctx]
     best=None
     for dest in itertools.product(*domains):
      order,cs=costs[pack][dest];value=sum(a*b for a,b in zip(w,order))+space*cs
      z=(value,dest)
      if best is None or z<best:best=z
     value,dest=best;payload+=value;cert.append({'context':list(ctx),'target_context':list(dest),'lower':value})
    paid=payload+r['key_lo']+r['selector_lo'];margin=paid-r['kt_hi'];r['packs'][pack]={'payload_lower':payload,'paid_lower':paid,'margin_lower':margin,'status':'CERTIFIED_NO_KEY_BEATS_MATCHED_KT' if margin>0 else 'BOUND_INCONCLUSIVE','rows':cert}
   r['status']='ALL_PACKS_CERTIFIED' if all(z['margin_lower']>0 for z in r['packs'].values()) else 'BOUND_INCONCLUSIVE'
  results[ed]=r;print(ed,'lines',r['lines'],'events',r['events'],'m',m,'status',r['status'],{p:round(v['margin_lower']/SCALE,5) for p,v in r['packs'].items()},flush=True)
 save('RESULT.json',{'status':'CERTIFIED_CONTEXT_BOUND','scale':SCALE,'readers':results})
if __name__=='__main__':main()
