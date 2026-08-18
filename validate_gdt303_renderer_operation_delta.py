#!/usr/bin/env python3
"""Independent reconstruction of GDT303 pairs, scores, and sign null."""
import csv,hashlib,itertools,json,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;Y=('FIRST','MIDDLE','LAST');checks=[]
def ck(n,v):assert v,n;checks.append(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def close(a,b,t=2e-10):return abs(float(a)-float(b))<=t
def yy(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def pop(rows):
 b=[x for x in rows if x['control_id']=='VOYNICH_REFERENCE' and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in b:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in b if len(hf[x['page_host']])>1 and len(sf[x['source_surface_sha256']])>1]
def make(E,F):
 D=defaultdict(lambda:defaultdict(list));ans=[]
 for x in E:D[x['page_host']][x['source_surface_sha256']].append(x)
 for h,q in D.items():
  A=[(s,tuple(v[0][k] for k in F),v) for s,v in q.items() if len(v)>=5 and len({x['physical_folio'] for x in v})>=3]
  for a,b in itertools.combinations(A,2):
   z=[i for i,(u,v) in enumerate(zip(a[1],b[1])) if u!=v]
   if len(z)!=1:continue
   i=z[0];u,v=a[1][i],b[1][i]
   if u in ('NONE','0') and v not in ('NONE','0'):src,tgt=a,b
   elif v in ('NONE','0') and u not in ('NONE','0'):src,tgt=b,a
   elif u<v:src,tgt=a,b
   else:src,tgt=b,a
   cs=Counter(yy(x) for x in src[2]);ct=Counter(yy(x) for x in tgt[2]);delta=tuple(ct[y]/len(tgt[2])-cs[y]/len(src[2]) for y in Y);ans.append((f'{F[i]}:{src[1][i]}>{tgt[1][i]}',h,src[0],tgt[0],delta))
 return ans
def vec(P):
 q=defaultdict(list)
 for o,h,a,b,d in P:q[(o,h)].append(d)
 return {k:tuple(sum(x[i] for x in v)/len(v) for i in range(3)) for k,v in q.items()}
def ev(V,o,signs=None):
 H=sorted(h for q,h in V if q==o);Q={h:tuple((signs.get(h,1) if signs else 1)*x for x in V[(o,h)]) for h in H};a=b=0;right=0
 for h in H:
  T=[Q[x] for x in H if x!=h];p=tuple(sum(z[i] for z in T)/len(T) for i in range(3));v=Q[h];a+=sum(x*x for x in v);b+=sum((x-y)**2 for x,y in zip(v,p));right+=sum(x*y for x,y in zip(v,p))>0
 return a-b,right,len(H)
def sg(o,h,w,seed):return 1 if int(hashlib.sha256(f'{seed}|{w}|{o}|{h}'.encode()).hexdigest()[:16],16)&1 else -1
d=json.loads((R/'gdt303_design.json').read_text());q=dict(d);q.pop('content_sha256');ck('design',d['content_sha256']==can(q));r=json.loads((R/'gdt303_result.json').read_text());q=dict(r);q.pop('content_sha256');ck('result',r['content_sha256']==can(q));
for g in ('inputs','documents','implementation','outputs'):
 for n,h in r[g].items():ck(g+'_'+n,sha(R/n)==h)
rows=read(R/'gdt278_native_event_inventory.tsv');ck('f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows));P=make(pop(rows),d['renderer_fields']);V=vec(P);cap={x['operation']:x for x in read(R/'gdt303_capacity.tsv')};ops=sorted(o for o,x in cap.items() if x['capacity']=='POWERED');stored={x['operation']:x for x in read(R/'gdt303_operation_scores.tsv')};pairrows=read(R/'gdt303_pair_deltas.tsv');ck('pair_count',len(pairrows)==sum(x[0] in ops for x in P));O={}
for o in ops:
 gain,right,n=ev(V,o);O[o]=gain;z=stored[o];ck('gain_'+o,close(z['sse_gain'],gain));ck('right_'+o,int(z['direction_correct_hosts'])==right and int(z['hosts'])==n)
N={o:[] for o in ops}
for w in range(d['null_worlds']):
 for o in ops:
  H=[h for q,h in V if q==o];N[o].append(ev(V,o,{h:sg(o,h,w,d['null_seed']) for h in H})[0])
means={o:statistics.mean(N[o]) for o in ops};sds={o:statistics.pstdev(N[o]) for o in ops};zs={o:(O[o]-means[o])/sds[o] for o in ops};wm=[max((N[o][w]-means[o])/sds[o] for o in ops) for w in range(d['null_worlds'])];null=read(R/'gdt303_null_max.tsv')
for w,x in enumerate(null):ck('nullmax_'+str(w),close(x['max_standardized_gain'],wm[w]))
for o in ops:
 z=stored[o];mp=(1+sum(x>=zs[o]-1e-15 for x in wm))/(1+d['null_worlds']);ck('maxp_'+o,close(z['max_family_p'],mp));acc=int(z['direction_correct_hosts'])/int(z['hosts']);cl=d['decision']['transfer'] if O[o]>0 and acc>=.7 and mp<=.05 else d['decision']['weak'] if O[o]>0 else d['decision']['fail'];ck('class_'+o,z['classification']==cl)
cc=Counter(x['classification'] for x in stored.values());status='RENDERER_OPERATION_POSITION_DELTAS_FOUND' if cc[d['decision']['transfer']] else 'NO_TRANSFERRED_RENDERER_DELTA';ck('status',status==r['status']);ck('summary',r['summary']['class_counts']==dict(cc));ck('report',status in (R/'GDT303_RENDERER_OPERATION_POSITION_DELTA_REPORT.md').read_text());val={'schema':'GDT303_VALIDATION_V1','status':'PASS','checks':len(checks),'result_sha256':sha(R/'gdt303_result.json'),'result_content_sha256':r['content_sha256'],'scope':'INDEPENDENT_SOURCE_PAIR_LOHO_SIGN_NULL_MAX_FAMILY_DECISION_HASH_RECONSTRUCTION'};(R/'gdt303_validation.json').write_text(json.dumps(val,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
