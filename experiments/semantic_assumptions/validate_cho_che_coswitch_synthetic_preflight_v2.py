#!/usr/bin/env python3
"""Nonimporting reconstruction of the v2 co-switch synthetic preflight."""
from __future__ import annotations
import csv,hashlib,itertools,json,os,tempfile
from collections import Counter,defaultdict
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import numpy as np
B=Path(__file__).resolve().parent;R=B/'results';SELF=Path(__file__).resolve();P=R/'cho_che_coswitch_masked_panel.tsv';V1=R/'cho_che_coswitch_synthetic_preflight.json';V2=R/'cho_che_coswitch_synthetic_preflight_v2.json';REP=R/'cho_che_coswitch_synthetic_preflight_v2_report.md';OUT=R/'cho_che_coswitch_synthetic_preflight_v2_validation.json';REPORT=R/'cho_che_coswitch_synthetic_preflight_v2_validation_report.md'
HASH={P:'25ae579c3f122f188089edc8fd2e0f617194bf6240cb20570d9aff881f80e003',V1:'d82a6a2cc0ac10c6f5eab3bc3b425ee30cd0759c4277e74b86a49373bd8f7f9e',V2:'d7906941588b8f8b8792a2809e64a3288db578eb272c9803cc0930190c011d37',REP:'d3508e8149597f5217a6adf0eb40bd6e5d4d673cd8480dd86618e4c6c6ff9fa7',B/'CHO_CHE_COSWITCH_SYNTHETIC_PREFLIGHT_V2_AMENDMENT.md':'a306f3342b80a57f6f8ccbb11e3caebd54f708b36f188a5ec46228e265995acf',B/'cho_che_coswitch_core.py':'a1f246f7c25318eb7c54c393425d939f4ef5755df066732716322aa1b214602d',B/'cho_che_coswitch_core_v2.py':'34e53d843c70e1f4fe68b9d9ec8cd1c1da1433a501b5f554b526b77be513dae5',B/'cho_che_coswitch_fixture.py':'3b79e60770d67cee7e43506fef00a9d95de1abf24d0a1f79bf4c81ad80b06ce4',B/'run_cho_che_coswitch_synthetic_preflight_v2.py':'46a0f4a12bba40ad64900f79c25a403f664dbf431aed4e607a7ade6d4bb763d9'}
E=('ZL3b','IT2a','RF1b');L=('f39','f55','f68','f73','f87','f89','f90','f96');D=(24,48,576);HR=np.array([0,1,1,0,1,0,1,1],bool);DG=np.array([0,0,1,1,0,1,0,0],bool);NU=('section','currier','hand','kind','grammar_scope','primary_sta_symbol_count','page_position_quartile','group_position_class')
F={'NULL':(64,0.),'DISTRIBUTED_THREE_BLOCK':(8,.75),'DISTRIBUTED_TWO_BLOCK':(8,.75),'ONE_LEAF':(8,1.),'ONE_READING':(8,1.),'OPPOSITE_READING':(8,1.),'SIDE_ONLY':(8,1.),'DIAGNOSTIC_ONLY':(8,1.),'PROSE_ONLY':(8,1.),'ONE_BLOCK':(8,1.)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seed(*x):return int.from_bytes(hashlib.sha256('|'.join(map(str,x)).encode()).digest()[:8],'little')
def unit(x):
 n=np.linalg.norm(x,axis=-1,keepdims=True)
 if not np.isfinite(x).all() or np.any(n<=0):raise ValueError
 return x/n
def mp(x):return float(np.mean([float(x[i]@x[j]) for i in range(len(x)) for j in range(i+1,len(x))]))
def cos(a,b):
 x=float(np.linalg.norm(a)*np.linalg.norm(b));return float(a@b/x) if x>0 else -1.
def geometry():
 rows=list(csv.DictReader(P.open(),delimiter='\t'));g=defaultdict(list)
 for r in rows:g[(r['edition'],r['physical_folio'],r['side'],tuple(r[k] for k in NU))].append(r['source_group_id'])
 s=np.zeros((3,8));shared={};counts=Counter()
 for ei,e in enumerate(E):
  for li,l in enumerate(L):
   a={k[3] for k,v in g.items() if k[:3]==(e,l,'r') and len(v)>=2};b={k[3] for k,v in g.items() if k[:3]==(e,l,'v') and len(v)>=2};c=sorted(a&b);shared[e,l]=c;var=0
   for q in c:
    nr,nv=len(g[e,l,'r',q]),len(g[e,l,'v',q]);counts[e,l,'r']+=nr;counts[e,l,'v']+=nv;var+=1/nr+1/nv
   s[ei,li]=np.sqrt(var/len(c)**2)
 return s,shared,counts
def world(s,f,w,strength):
 dirs=[]
 for bi,d in enumerate(D):
  q=np.random.default_rng(seed('CCSW001',f,w,'DIRECTION',bi)).normal(size=d);dirs.append(q/np.linalg.norm(q))
 out=[]
 for bi,d in enumerate(D):
  z=np.zeros((3,8,d))
  for li,l in enumerate(L):
   shared=np.random.default_rng(seed('CCSW001',f,w,'SHARED',bi,l)).normal(size=d)
   for ei,e in enumerate(E):
    noise=np.sqrt(.8)*shared+np.sqrt(.2)*np.random.default_rng(seed('CCSW001',f,w,'READING',bi,l,e)).normal(size=d);z[ei,li]=s[ei,li]*noise;active=True;sign=1
    if f=='NULL':active=False
    elif f=='ONE_LEAF':active=li==0
    elif f=='ONE_READING':active=ei==0
    elif f=='OPPOSITE_READING':sign=-1 if ei==2 else 1
    elif f=='SIDE_ONLY':sign=1 if HR[li] else -1
    elif f=='DIAGNOSTIC_ONLY':active=bool(DG[li])
    elif f=='PROSE_ONLY':active=not DG[li]
    elif f=='ONE_BLOCK':active=bi==0
    elif f=='DISTRIBUTED_TWO_BLOCK':active=bi in (0,2)
    elif f!='DISTRIBUTED_THREE_BLOCK':raise ValueError
    if active:z[ei,li]+=sign*strength*s[ei,li]*np.sqrt(d)*dirs[bi]
  out.append(z)
 return tuple(out)
def evaluate(blocks):
 ub=[unit(x) for x in blocks];c=unit(np.concatenate([x/np.sqrt(3) for x in ub],axis=2));align=[mp(c[e]) for e in range(3)];primary=min(align);null=[]
 for signs in itertools.product((-1.,1.),repeat=8):
  q=np.array(signs)[None,:,None];null.append(min(mp((c*q)[e]) for e in range(3)))
 p=sum(x>=primary-1e-15 for x in null)/256;ph=[];md=[];oc=[];dc=[];mc=[];pb=[]
 for e in range(3):
  held=[];delete=[]
  for i in range(8):held.append(cos(c[e,i],np.mean(np.delete(c[e],i,0),0)));delete.append(mp(np.delete(c[e],i,0)))
  ph.append(sum(x>0 for x in held));md.append(min(delete));oc.append(cos(np.mean(c[e,HR],0),np.mean(c[e,~HR],0)));dc.append(cos(np.mean(c[e,DG],0),np.mean(c[e,~DG],0)));la=np.array([np.mean([float(c[e,i]@c[e,j]) for j in range(8) if j!=i]) for i in range(8)]);pos=np.maximum(la,0);mass=np.sum(pos);mc.append(float(np.max(pos)/mass) if mass>0 else 1);pb.append(sum(mp(x[e])>0 for x in ub))
 ra=float(np.mean([float(c[a,l]@c[b,l]) for l in range(8) for a in range(3) for b in range(a+1,3)]));bp=[];bq=[]
 for u in ub:
  x=min(mp(u[e]) for e in range(3));n=[]
  for signs in itertools.product((-1.,1.),repeat=8):
   q=np.array(signs)[None,:,None];n.append(min(mp((u*q)[e]) for e in range(3)))
  bp.append(x);bq.append(sum(y>=x-1e-15 for y in n)/256)
 exact=sum(x>=.1 and y<=.01 for x,y in zip(bp,bq));v1=primary>=.1 and p<=.01 and min(ph)>=7 and min(md)>0 and min(oc)>0 and min(dc)>0 and ra>=.4 and max(mc)<=.3 and min(pb)>=2;passed=primary>=.1 and p<=.01 and min(ph)>=7 and min(md)>0 and min(oc)>0 and min(dc)>0 and ra>=.4 and max(mc)<=.3 and exact>=2
 return {'primary':primary,'p_value':p,'reading_alignment':align,'positive_held':ph,'min_deletion':md,'orientation_cross':oc,'domain_cross':dc,'reading_agreement':ra,'max_concentration':mc,'positive_blocks':pb,'v1_passes':bool(v1),'block_primary':bp,'block_p_value':bq,'exact_block_passes':exact,'passes':bool(passed)}
def install(a,b):
 if OUT.exists() or REPORT.exists():raise FileExistsError
 with tempfile.TemporaryDirectory(dir=R,prefix='ccswv2val_') as d:
  x,y=Path(d)/'j',Path(d)/'m';x.write_bytes(a);y.write_bytes(b);os.link(x,OUT)
  try:os.link(y,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 checks=[]
 for p,h in HASH.items():
  if sha(p)!=h:raise AssertionError(p.name)
  checks.append('hash:'+p.name)
 actual=json.loads(V2.read_text());s,shared,counts=geometry();records={};pc={}
 for f,(n,q) in F.items():
  rr=[]
  for w in range(n):rr.append({'world':w,**evaluate(world(s,f,w,q))})
  records[f]=rr;pc[f]=sum(x['passes'] for x in rr)
  if rr!=actual['worlds'][f]:raise AssertionError('world '+f)
  checks.append('worlds:'+f)
 if pc!=actual['pass_counts']:raise AssertionError('counts')
 checks+=['counts','geometry']
 if len(shared)!=24 or sum(map(len,shared.values()))!=272 or sum(counts.values())!=2730 or min(counts.values())!=9:raise AssertionError('geometry')
 if actual['status']!='PASS_TARGET_FREE_CHO_CHE_COSWITCH_PREFLIGHT_V2' or not all(actual['gates'].values()):raise AssertionError('decision')
 checks.append('decision')
 result={'experiment':'CHO_CHE_COSWITCH_SYNTHETIC_PREFLIGHT_V2_VALIDATION','status':'PASS_INDEPENDENT_136_WORLD_BLOCKWISE_RECONSTRUCTION','checks_passed':len(checks),'inputs':{p.name:sha(p) for p in (*HASH,SELF)},'pass_counts':pc,'geometry':{'shared_cells':272,'rows':2730,'minimum_side':9,'scale_sha256':hashlib.sha256(np.asarray(s,dtype='<f8').tobytes()).hexdigest()},'target_associations_computed':0,'english_glosses':0,'claim_ceiling':'Validation confirms only the target-free synthetic scorer and supplies no manuscript co-switch result meaning plaintext or translation.'}
 report=f"# `cho/che` co-switch synthetic preflight v2 validation\n\n**PASS**: {len(checks)} checks independently reconstruct all 136 worlds, exact blockwise scores, pass counts, geometry, and the target-free authorization. No manuscript family/state association was opened.\n";install((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),report.encode());print(json.dumps({'status':result['status'],'checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
