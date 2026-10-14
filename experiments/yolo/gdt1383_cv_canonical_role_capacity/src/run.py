"""Exact role classes for the fixed greedy CV writer; no sound assignments."""
import argparse,gzip,hashlib,itertools,json,math
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SOURCE=R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
OLD=R/'experiments/yolo/gdt1248_prefix_bound_attainment/artifacts/RESULT.json'
U=('a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh')
HEADS={'cfh':('a','d','e','o','s','y'),'cph':('a','d','e','k','o','y')}
READERS=('IT2a','RF1b','ZL3b')
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(name,x):(B/'artifacts'/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def inspect(word,h,followers):
 after=[];i=0;active=False;used=set()
 while i<len(word):
  if word[i]!=h:i+=1;continue
  assert i+1<len(word) and word[i+1] in followers
  active=True;used.add(word[i+1])
  if i+2<len(word):after.append((i,word[i+2]))
  i+=2
 return active,used,after

def controls():
 h='H';f={'A','B'}
 assert inspect(('H','A','v'),h,f)[2]==[(0,'v')]
 assert inspect(('H','A','C'),h,f)[2]==[(0,'C')]
 assert inspect(('H','A','H','B'),h,f)[2]==[(0,'H')]
 assert not inspect(('H','A'),h,f)[2]
 for w in [('H',),('H','v')]:
  try:inspect(w,h,f)
  except AssertionError:pass
  else:raise AssertionError(w)
 # Per-word scanning never creates a cross-space HF,V event.
 assert sum((inspect(w,h,f)[2] for w in [('H','A'),('v',)]),[])==[]
 return {'status':'PASS','HFV_detected':True,'HF_CV_allowed':True,'successive_HF_allowed':True,'group_boundaries_preserved':True,'terminal_and_wrong_follower_rejected':True}

def main():
 a=argparse.ArgumentParser();a.add_argument('--controls-only',action='store_true');args=a.parse_args();c=controls()
 if args.controls_only:print(json.dumps(c));return
 for p,h in load(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 save('CONTROLS.json',c);data=load(SOURCE);prior={(x['reader'],x['head']):x for x in load(OLD)['cases']};out=[]
 assert set(data)==set(READERS)
 for ed in READERS:
  rows=data[ed]
  for h,fs in HEADS.items():
   F=set(fs);T=set();seen={};active=0;actual=set()
   for row in rows:
    assert not row['page'].startswith('f84') and row['page'] not in ('f116v','f1r')
    w=row['units'];assert w and set(w)<=set(U) and ''.join(w)==row['ivtff_group_raw']
    a,used,afters=inspect(w,h,F);active+=a;actual.update(used)
    for i,s in afters:
     T.add(s)
     if s not in seen:seen[s]={'next':s,'id':row['id'],'page':row['page'],'locus':row['locus'],'raw':row['ivtff_group_raw'],'units':w,'index':i}
   assert actual==F
   ntypes=len({tuple(x['units']) for x in rows});old=prior[(ed,h)];assert (len(rows),ntypes,active)==(old['groups'],old['types'],old['active_groups']) and old['failed_groups']==0
   E=sorted(set(U)-{h}-F-T);vs=list(itertools.combinations(E,3));status='NO_CANONICAL_ROLE_KEY' if not vs else 'UNIQUE_ROLE_CLASS' if len(vs)==1 else 'MULTIPLE_ROLE_CLASSES'
   case={'reader':ed,'head':h,'groups':len(rows),'types':ntypes,'active_groups':active,'followers':sorted(F),'after_pair':sorted(T),'eligible':E,'vowel_sets':[list(v) for v in vs],'count':len(vs),'status':status,'witnesses':[seen[s] for s in sorted(T)]};out.append(case)
   print(ed,h,'eligible',E,'role_classes',len(vs),status,flush=True)
 save('RESULT.json',{'experiment':'GDT1383','status':'EXACT_CANONICAL_ROLE_CLASSIFICATION','labelings_per_role_set':math.factorial(6)*math.factorial(3)*math.factorial(12),'cases':out})
if __name__=='__main__':main()
