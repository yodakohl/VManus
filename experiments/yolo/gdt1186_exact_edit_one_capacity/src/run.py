from pathlib import Path
from itertools import permutations,product
import json,sys,hashlib,random
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt1184_contextual_initial_styles/src'))
import codec as c
import run as old
m=old.m
BOOKS=['b4','w1']
def save(n,x):(A/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def domain(g):
 if g<21:return 'I'
 if 22<=g<25:return 'M'
 if 25<=g<31:return 'F'
 raise AssertionError(g)
def classify(a,b):
 if len(a)==len(b):return 'fixed' if sum(x!=y for x,y in zip(a,b))==1 else None
 if abs(len(a)-len(b))!=1:return None
 if len(a)<len(b):a,b=b,a
 possible=set()
 for i in range(len(a)):
  edges=set();valid=True
  for x,y in zip(a[:i]+a[i+1:],b):
   if x==y:continue
   dx,dy=domain(x),domain(y)
   if dx==dy:valid=False;break
   if dx=='M':x,y=y,x;dx,dy=dy,dx
   assert dy=='M' and dx in ['I','F']
   edges.add((dx,x if dx=='I' else x-25,y-22))
  if valid:
   if not edges:return 'fixed'
   assert len(edges)==1
   possible.update(edges)
 assert len(possible)<=1,('Theorem violation',a,b,possible)
 return next(iter(possible)) if possible else None

def numeric_lines(codec,recipes):
 lines=[];remaining=8000
 for recipe in recipes:
  line=[];size=0
  for word in codec.numeric(recipe['words']):
   if not remaining:break
   n=len(word)
   if line and size+1+n>48:lines.append(line);line=[];size=0
   size+=n+bool(line);line.append(word);remaining-=1
  if line:lines.append(line)
  if not remaining:break
 assert remaining==0
 return lines

def summarize(lines):
 pairs=[(a,b) for line in lines for a,b in zip(line,line[1:])]
 result={'fixed':0,'I':[[0]*3 for _ in range(21)],'F':[[0]*3 for _ in range(6)],'denominator':len(pairs)}
 for a,b in pairs:
  kind=classify(a,b)
  if kind=='fixed':result['fixed']+=1
  elif kind is not None:k,i,j=kind;result[k][i][j]+=1
 return result,pairs

def matchings(profiles,key):
 patterns=permutations(range(22),3) if key=='I' else (p for p in product(range(7),repeat=3) if len([x for x in p if x!=6])==len(set(x for x in p if x!=6)))
 records={};total=0;limit=21 if key=='I' else 6
 for pat in patterns:
  total+=1
  gains=tuple(sum(profiles[b][key][i][j] for j,i in enumerate(pat) if i<limit) for b in BOOKS)
  records.setdefault(gains,pat)
 assert total==(9240 if key=='I' else 229),total
 return records,total

def realize(ip,fp):
 medial=[c.SIGNS[x] for x in ip];final=[None]*6
 for j,i in enumerate(fp):
  if i<6:final[i]=medial[j]
 avail=[g for g in c.SIGNS if g not in medial and g not in final]
 if c.SIGNS[21] not in medial and c.SIGNS[21] not in final:avail.remove(c.SIGNS[21]);avail.insert(0,c.SIGNS[21])
 for i,g in enumerate(final):
  if g is None:final[i]=avail.pop(0)
 extend=lambda p:p+[g for g in c.SIGNS if g not in p]
 alph={'initial':c.SIGNS[:],'medial':extend(medial),'final':extend(final)}
 assert old.coverage(alph)
 return alph

def predicted(p,alph):
 n=p['fixed']
 for key,bank,limit in [('I',alph['initial'],21),('F',alph['final'],6)]:
  for i in range(limit):
   for j in range(3):
    if bank[i]==alph['medial'][j]:n+=p[key][i][j]
 return n

def direct(pairs,alph):
 mapping=alph['initial']+alph['medial'][:3]+alph['final'][:6]
 return sum(m.edit_one([mapping[x] for x in a],[mapping[x] for x in b]) for a,b in pairs)

def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(old.SOURCE.read_text());targets=json.loads(old.TARGET.read_text())['targets'];tables=json.loads((ROOT/'experiments/yolo/gdt1184_contextual_initial_styles/artifacts/TABLES.json').read_text());result={'experiment':'GDT1186','models':{}}
 for model in c.MODELS:
  codec=c.Codec(model,tables);profiles={};pairs={}
  for book in BOOKS:profiles[book],pairs[book]=summarize(numeric_lines(codec,source[book]))
  ims,ic=matchings(profiles,'I');fms,fc=matchings(profiles,'F');intervals={}
  for book,p in profiles.items():
   valid=[n for n in range(p['denominator']+1) if all(abs(n/p['denominator']-t['edit1_repeat'])<=.03 for t in targets.values())]
   intervals[book]=[min(valid),max(valid)]
  maximum={book:profiles[book]['fixed']+max(g[i] for g in ims)+max(g[i] for g in fms) for i,book in enumerate(BOOKS)}
  witness=None;best=None
  for ig,ip in ims.items():
   for fg,fp in fms.items():
    counts={b:profiles[b]['fixed']+ig[i]+fg[i] for i,b in enumerate(BOOKS)}
    if all(intervals[b][0]<=counts[b]<=intervals[b][1] for b in BOOKS):
     order=(sum(counts[b]-intervals[b][0] for b in BOOKS),ip,fp)
     if best is None or order<best:best=order;witness={'I_match':ip,'F_match':fp,'counts':counts}
  rng=random.Random(118600);random_checks=0
  for _ in range(20):
   while True:
    alph={k:rng.sample(c.SIGNS,22) for k in ['initial','medial','final']}
    if old.coverage(alph):break
   for book in BOOKS:assert predicted(profiles[book],alph)==direct(pairs[book],alph);random_checks+=1
  if witness:
   alph=realize(witness['I_match'],witness['F_match']);witness['alphabets']=alph;writer=c.Codec(model,tables,alph);roundtrips=0
   for book in BOOKS:
    assert direct(pairs[book],alph)==predicted(profiles[book],alph)==witness['counts'][book]
    ps,_=old.pages(writer,source[book]);met=old.measure(ps);assert abs(met['edit1_repeat']-witness['counts'][book]/profiles[book]['denominator'])<1e-15;roundtrips+=len(source[book])
   witness['full_recipe_roundtrips']=roundtrips
  entry={'profiles':profiles,'intervals':intervals,'individual_max_counts':maximum,'individual_max_rates':{b:maximum[b]/profiles[b]['denominator'] for b in BOOKS},'matching_counts':{'I':ic,'F':fc},'distinct_gain_pairs':{'I':len(ims),'F':len(fms)},'joint_feasible':witness is not None,'witness':witness,'random_map_book_checks':random_checks}
  save(model+'_ATTAINABLE.json',{'I':[{'gains':g,'pattern':p} for g,p in sorted(ims.items())],'F':[{'gains':g,'pattern':p} for g,p in sorted(fms.items())]})
  result['models'][model]=entry;save('RESULT.json',result);print(json.dumps({'model':model,'maximum':maximum,'intervals':intervals,'joint_feasible':witness is not None}),flush=True)
 result['status']='EDIT_ONE_CAPACITY_EXISTS' if any(x['joint_feasible'] for x in result['models'].values()) else 'FIXED_ROLE_ALPHABET_FAMILY_IMPOSSIBLE'
 result['claim_ceiling']='Exact capacity for one adjacency condition only. No full statistical writer, native meaning, transfer or historical usability claim.';save('RESULT.json',result)
if __name__=='__main__':main()
