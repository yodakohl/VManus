import collections,csv,gzip,hashlib,itertools,json,math,random,re
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 x=p.read_bytes();return json.loads(gzip.decompress(x) if p.suffix=='.gz' else x)
def save(n,x):
 v=(json.dumps(x,indent=2)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(v,mtime=0) if n.endswith('.gz') else v)
def pair(x):return [x.numerator,x.denominator]
def parse(u):
 if u[-2:]==['d','y']:base,tag=u[:-2],1
 elif u[-1:]==['y']:base,tag=u[:-1],0
 else:return None
 return (tuple(base),tag) if base and base[-1]!='d' else None
def fold(base):return hashlib.sha256(('1325|'+','.join(base)).encode()).digest()[0]&1
def ranks2(scores):
 out=[0]*len(scores);order=sorted(range(len(scores)),key=lambda i:scores[i]);lo=0
 while lo<len(order):
  hi=lo+1
  while hi<len(order) and scores[order[hi]]==scores[order[lo]]:hi+=1
  for j in order[lo:hi]:out[j]=lo+hi+1
  lo=hi
 return out
def u2(tags,ranks):
 n=sum(tags);return sum(r for t,r in zip(tags,ranks) if t)-n*(n+1)
def fixtures():
 count=0
 for n in range(1,5):
  for base in itertools.product(['a','d','y'],repeat=n):
   if base[-1]=='d':continue
   for tag in [0,1]:
    out=list(base)+(['d','y'] if tag else ['y']);assert parse(out)==(base,tag);assert out[0]==base[0] and out[-1]=='y';count+=1
 assert parse(['y']) is None and parse(['d','y']) is None and parse(['a','d','d','y']) is None
 for tags in itertools.product([0,1],repeat=4):
  if sum(tags) in [0,4]:continue
  scores=[F(1),F(1),F(2),F(3)];direct=sum(2*int(scores[i]>scores[j])+int(scores[i]==scores[j]) for i in range(4) for j in range(4) if tags[i] and not tags[j]);assert direct==u2(tags,ranks2(scores))
 return {'module_alternatives_checked':count,'tied_auc_binary_labelings':14}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};allresults={};joined=0
 for ed,rr in sorted(data.items()):
  source={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    for g in line['groups']:source[g[0]]=(line['metadata'],g)
  by={};licenses=collections.defaultdict(set)
  for r in rr:
   m,g=source[r['id']];assert r['page'] in allow and not r['page'].startswith(('f84','f116v','f1r'));assert m['page']==r['page'] and m['locus']==r['locus'] and m['kind']==r['kind']=='P';assert g[2]==r['ivtff_group_raw']==''.join(r['units']) and int(g[1])==int(r['source_group_index']);assert g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';assert set(r['units'])<=set(A);key=(r['locus'],int(r['source_group_index']));assert key not in by;by[key]=r;joined+=1
   p=parse(r['units'])
   if p:licenses[p[0]].add(p[1])
  paired={b for b,t in licenses.items() if t=={0,1}};events=[]
  for (loc,pos),r in sorted(by.items()):
   p=parse(r['units']);m,g=source[r['id']]
   if not p or p[0] not in paired or m['currier'] not in ['A','B'] or (loc,pos-1) not in by or (loc,pos+1) not in by:continue
   base,tag=p;l=by[(loc,pos-1)];v=by[(loc,pos+1)];leaf=int(re.match(r'f(\d+)',r['page']).group(1));bf=fold(base);role='TRAIN' if leaf%2==1 and bf==0 else ('TEST' if leaf%2==0 and bf==1 else 'UNUSED')
   events.append({'id':r['id'],'base':list(base),'base_key':','.join(base),'tag':tag,'page':r['page'],'leaf':leaf,'currier':m['currier'],'base_fold':bf,'split':role,'left_id':l['id'],'right_id':v['id'],'left':l['units'][-1],'right':v['units'][0]})
  events.sort(key=lambda e:e['id']);train=collections.defaultdict(list)
  for e in events:
   if e['split']=='TRAIN':train[(e['base_key'],e['currier'])].append(e)
  train={k:v for k,v in train.items() if {e['tag'] for e in v}=={0,1}};models={};trainbases={k[0] for k in train}
  for c in ['A','B']:
   cells=[v for k,v in sorted(train.items()) if k[1]==c];counts=[[[F() for _ in A] for _ in range(2)] for _ in range(2)]
   for cell in cells:
    for tag in [0,1]:
     subset=[e for e in cell if e['tag']==tag]
     for side,name in enumerate(['left','right']):
      for e in subset:counts[tag][side][A.index(e[name])]+=F(1,len(subset))
   probs=[[[(x+F(1,2))/(len(cells)+11) for x in row] for row in t] for t in counts];assert all(sum(row)==1 for t in probs for row in t);models[c]={'paired_bases':len(cells),'probs':[[[pair(x) for x in row] for row in t] for t in probs]}
  def score(e):
   p=models[e['currier']]['probs'];return F(*p[1][0][A.index(e['left'])])/F(*p[0][0][A.index(e['left'])])*F(*p[1][1][A.index(e['right'])])/F(*p[0][1][A.index(e['right'])])
  held=collections.defaultdict(list)
  for e in events:
   if e['split']=='TEST':held[(e['base_key'],e['page'])].append(e)
  held={k:sorted(v,key=lambda e:e['id']) for k,v in held.items() if {e['tag'] for e in v}=={0,1}};cells=[]
  for k,cell in sorted(held.items()):
   tags=[e['tag'] for e in cell];scores=[score(e) for e in cell];rank=ranks2(scores);n1=sum(tags);den=2*n1*(len(tags)-n1);obs=u2(tags,rank);cells.append({'base_key':k[0],'page':k[1],'leaf':cell[0]['leaf'],'ids':[e['id'] for e in cell],'tags':tags,'scores':[pair(x) for x in scores],'ranks2':rank,'auc_numerator':obs,'auc_denominator':den})
  leafcells=collections.Counter(x['leaf'] for x in cells);leaves=sorted(leafcells);L=math.lcm(*(len(leaves)*leafcells[x['leaf']]*x['auc_denominator'] for x in cells)) if cells else 1;weights=[L//(len(leaves)*leafcells[x['leaf']]*x['auc_denominator']) for x in cells];observed=sum(w*x['auc_numerator'] for w,x in zip(weights,cells));auc=F(observed,L);leafauc={leaf:sum((F(x['auc_numerator'],x['auc_denominator']) for x in cells if x['leaf']==leaf),F())/leafcells[leaf] for leaf in leaves};positive=sum(v>F(1,2) for v in leafauc.values());nbases=len({k[0] for k in held});nevents=sum(len(x['tags']) for x in cells);capacity=len(trainbases)>=10 and nbases>=10 and len(leaves)>=10 and nevents>=100;mobile=any(len(set(x['ranks2']))>1 for x in cells);null=[];pvalue=None;status='NO_CAPACITY'
  if capacity and mobile:
   rng=random.Random(1325)
   for _ in range(1999):
    value=0
    for w,x in zip(weights,cells):
     tags=x['tags'].copy();rng.shuffle(tags);value+=w*u2(tags,x['ranks2'])
    null.append(value)
   pvalue=F(1+sum(v>=observed for v in null),2000);samplemobile=len(set(null))>=2;passed=auc>=F(55,100) and 3*positive>=2*len(leaves) and pvalue<=F(1,60) and samplemobile;status='HELD_BASE_FLANK_CHOICE_TRANSFER' if passed else 'NOT_CONFIRMED'
  elif capacity:status='SCORE_IMMOBILE'
  result={'status':status,'eligible_events':len(events),'globally_paired_bases':len(paired),'train_paired_bases':len(trainbases),'train_events_used':sum(len(v) for v in train.values()),'held_bases':nbases,'held_cells':len(cells),'held_events':nevents,'held_leaves':len(leaves),'positive_leaves':positive,'auc':pair(auc),'auc_decimal':float(auc),'p_one_sided':pair(pvalue) if pvalue is not None else None,'capacity':capacity,'score_mobile':mobile,'null_score_denominator':L,'observed_score_numerator':observed,'leaf_auc':{str(k):pair(v) for k,v in leafauc.items()}};allresults[ed]=result;save(ed+'_EVENTS.json.gz',events);save(ed+'_MODEL.json',models);save(ed+'_HELD.json.gz',cells);save(ed+'_NULL.json.gz',null);print(ed,status,'trainbases',len(trainbases),'held',nbases,nevents,len(leaves),'AUC',float(auc),'positive',positive,'p',str(pvalue),flush=True)
 save('RESULT.json',{'status':'HELD_BASE_CHOICE_TRANSFER_ALL_READINGS' if all(v['status']=='HELD_BASE_FLANK_CHOICE_TRANSFER' for v in allresults.values()) else 'NO_COMMON_HELD_BASE_CHOICE_TRANSFER','source_joins':joined,'fixtures':fx,'readers':allresults,'scope':'Conditional external-flank FORMtag transfer only; no meaning, actual morphology, language or reserved confirmation.'})
if __name__=='__main__':main()
