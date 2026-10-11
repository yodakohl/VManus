import collections,csv,gzip,hashlib,itertools,json,math,random,re
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 x=p.read_bytes();return json.loads(gzip.decompress(x) if p.suffix=='.gz' else x)
def decode(u):
 if not u or u[-1]!='y':return None
 body=list(u[:-1]);tag=0
 if body and body[-1]=='d':body.pop();tag=1
 return (tuple(body),tag) if body and body[-1]!='d' else None
def units(raw):
 dp={0:[()]}
 for i in range(len(raw)):
  if i not in dp:continue
  for g in A:
   if raw.startswith(g,i):dp.setdefault(i+len(g),[]).extend(p+(g,) for p in dp[i])
 assert len(dp.get(len(raw),[]))==1;return list(dp[len(raw)][0])
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 mapping={}
 for n in range(1,5):
  for base in itertools.product('ady',repeat=n):
   if base[-1]=='d':continue
   for tag in range(2):
    w=base+(('d','y') if tag else ('y',));assert w not in mapping;mapping[w]=(base,tag);assert decode(w)==(base,tag)
 assert len(mapping)==160
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};out=read(B/'artifacts/RESULT.json');njoin=nevent=nscore=nnull=0;parsed={}
 for ed,rr in sorted(data.items()):
  target={r['id']:r for r in rr};licenses=collections.defaultdict(set)
  for r in rr:
   u=parsed.setdefault(r['ivtff_group_raw'],units(r['ivtff_group_raw']));assert u==r['units'];p=decode(u)
   if p:licenses[p[0]].add(p[1])
  paired={k for k,v in licenses.items() if len(v)==2};events=[];seen=set()
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    m=line['metadata'];groups=line['groups']
    for g in groups:
     if g[0] not in target:continue
     r=target[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['page']==r['page'] and m['locus']==r['locus'] and m['kind']==r['kind']=='P';assert r['page'] in allow and not r['page'].startswith(('f84','f116v','f1r'));assert g[2]==r['ivtff_group_raw'] and int(g[1])==int(r['source_group_index']);assert g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';njoin+=1
    for i in range(1,len(groups)-1):
     gl,g,gr=groups[i-1:i+2]
     if not all(z[0] in target for z in [gl,g,gr]) or int(gl[1])+1!=int(g[1]) or int(g[1])+1!=int(gr[1]):continue
     r=target[g[0]];p=decode(r['units'])
     if not p or p[0] not in paired or m['currier'] not in ['A','B']:continue
     base,tag=p;bk=','.join(base);fold=hashlib.sha256(('1325|'+bk).encode('utf8')).digest()[0]%2;leaf=int(re.match('f([0-9]+)',m['page']).group(1));role='UNUSED'
     if leaf%2 and not fold:role='TRAIN'
     if not leaf%2 and fold:role='TEST'
     events.append({'id':g[0],'base':list(base),'base_key':bk,'tag':tag,'page':m['page'],'leaf':leaf,'currier':m['currier'],'base_fold':fold,'split':role,'left_id':gl[0],'right_id':gr[0],'left':target[gl[0]]['units'][-1],'right':target[gr[0]]['units'][0]})
  assert seen==set(target);events.sort(key=lambda e:e['id']);assert events==read(B/'artifacts'/f'{ed}_EVENTS.json.gz');nevent+=len(events)
  train=[e for e in events if e['split']=='TRAIN'];den=collections.Counter((e['base_key'],e['currier'],e['tag']) for e in train);keys={(b,c) for b,c,t in den if (b,c,0) in den and (b,c,1) in den};P={};expectedmodel={}
  for c in ['A','B']:
   K=sum(cc==c for b,cc in keys);arr=[]
   for tag in [0,1]:
    sides=[]
    for side in ['left','right']:
     weight={u:F(1,2) for u in A}
     for e in train:
      if e['currier']==c and e['tag']==tag and (e['base_key'],c) in keys:weight[e[side]]+=F(1,den[e['base_key'],c,tag])
     row=[weight[u]/(K+11) for u in A];assert sum(row)==1;sides.append(row)
    arr.append(sides)
   P[c]=arr;expectedmodel[c]={'paired_bases':K,'probs':[[[[v.numerator,v.denominator] for v in row] for row in tag] for tag in arr]}
  assert expectedmodel==read(B/'artifacts'/f'{ed}_MODEL.json')
  test=collections.defaultdict(list)
  for e in events:
   if e['split']=='TEST':test[e['base_key'],e['page']].append(e)
  test={k:v for k,v in test.items() if {e['tag'] for e in v}=={0,1}};stored=read(B/'artifacts'/f'{ed}_HELD.json.gz');assert len(stored)==len(test);matrix=[];obs=[];leafvalues=collections.defaultdict(list)
  for (key,cell),s in zip(sorted(test.items()),stored):
   assert s['ids']==[e['id'] for e in cell] and s['tags']==[e['tag'] for e in cell] and (s['base_key'],s['page'])==key
   scores=[]
   for e in cell:
    probs=P[e['currier']];scores.append(probs[1][0][A.index(e['left'])]*probs[1][1][A.index(e['right'])]/(probs[0][0][A.index(e['left'])]*probs[0][1][A.index(e['right'])]));nscore+=1
   assert scores==[F(*x) for x in s['scores']];pairs=[[2 if a>b else int(a==b) for b in scores] for a in scores];matrix.append(pairs);tags=s['tags'];value=sum(pairs[i][j] for i in range(len(tags)) for j in range(len(tags)) if tags[i]==1 and tags[j]==0);denom=2*tags.count(1)*tags.count(0);assert value==s['auc_numerator'] and denom==s['auc_denominator'];obs.append(value);leafvalues[s['leaf']].append(F(value,denom))
   # Twice midranks, independently from pairwise order counts.
   assert s['ranks2']==[2*sum(b<a for b in scores)+sum(b==a for b in scores)+1 for a in scores]
  leafauc={k:sum(v,F())/len(v) for k,v in leafvalues.items()};auc=sum(leafauc.values(),F())/len(leafauc) if leafauc else F();r=out['readers'][ed];assert auc==F(*r['auc']) and {str(k):[v.numerator,v.denominator] for k,v in leafauc.items()}==r['leaf_auc'];positive=sum(v>F(1,2) for v in leafauc.values());trainbases={b for b,c in keys};testbases={b for b,p in test};cnt=sum(len(v) for v in test.values());assert (r['train_paired_bases'],r['held_bases'],r['held_events'],r['positive_leaves'])==(len(trainbases),len(testbases),cnt,positive);assert not trainbases&testbases;assert not {e['leaf'] for e in train}&set(leafvalues)
  capacity=len(trainbases)>=10 and len(testbases)>=10 and len(leafvalues)>=10 and cnt>=100;mobile=any(len(set(tuple(x) for x in s['scores']))>=2 for s in stored);assert capacity==r['capacity'] and mobile==r['score_mobile'];L=math.lcm(*(len(leafvalues)*len(leafvalues[s['leaf']])*s['auc_denominator'] for s in stored)) if stored else 1;assert L==r['null_score_denominator'];weights=[L//(len(leafvalues)*len(leafvalues[s['leaf']])*s['auc_denominator']) for s in stored];N=sum(w*v for w,v in zip(weights,obs));assert N==r['observed_score_numerator'];null=read(B/'artifacts'/f'{ed}_NULL.json.gz');status='NO_CAPACITY'
  if capacity and mobile:
   assert len(null)==1999;rng=random.Random(1325)
   for expected in null:
    total=0
    for w,s,rel in zip(weights,stored,matrix):
     tags=s['tags'].copy();rng.shuffle(tags);positiveidx=[i for i,t in enumerate(tags) if t];negativeidx=[j for j,t in enumerate(tags) if not t];total+=w*sum(rel[i][j] for i in positiveidx for j in negativeidx)
    assert total==expected;nnull+=1
   p=F(1+sum(v>=N for v in null),2000);assert p==F(*r['p_one_sided']);passed=auc>=F(11,20) and 3*positive>=2*len(leafvalues) and p<=F(1,60) and len(set(null))>=2;status='HELD_BASE_FLANK_CHOICE_TRANSFER' if passed else 'NOT_CONFIRMED'
  else:
   assert null==[] and r['p_one_sided'] is None
   if capacity:status='SCORE_IMMOBILE'
  assert r['status']==status;print(ed,'validated',cnt,'events',len(null),'nulls',flush=True)
 assert njoin==out['source_joins'];expected='HELD_BASE_CHOICE_TRANSFER_ALL_READINGS' if all(r['status']=='HELD_BASE_FLANK_CHOICE_TRANSFER' for r in out['readers'].values()) else 'NO_COMMON_HELD_BASE_CHOICE_TRANSFER';assert out['status']==expected
 result={'status':'PASS','source_joins':njoin,'eligible_events_verified':nevent,'held_rational_scores_verified':nscore,'conditional_permutations_rescored':nnull,'source_free_inverse_cases':160,'scope':'Independent source-window extraction, rational fitting and direct pairwise AUC/permutation checks; not independent palaeography or semantic confirmation.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
