#!/usr/bin/env python3
"""Fixed single-run categorical-choice context test; no lexical assignments."""
import argparse,collections,gzip,hashlib,itertools,json,math,random,re
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def save(name,obj):(B/'artifacts'/name).write_text(json.dumps(obj,indent=2)+'\n')
def collapse(units):
 out=[];runs=[];j=0
 while j<len(units):
  u=units[j];end=j+1
  if u in ('e','i'):
   while end<len(units) and units[end]==u:end+=1
   runs.append((len(out),u,end-j))
  out.append(u);j=end
 return out,runs
def feature_sets(cell):
 out=[]
 for ev in cell['events']:
  sides=[]
  for side in ['left_source','right_source']:
   u=['<B>']+ev[side]+['<E>'];sides.append(set(zip(u,u[1:])))
  out.append(sides)
 return out
def features(cell):
 ss=feature_sets(cell);vocab=sorted({(side,*bg) for sides in ss for side,pairs in enumerate(sides) for bg in pairs});col={x:i for i,x in enumerate(vocab)};F=np.zeros((len(ss),len(vocab)))
 for i,sides in enumerate(ss):
  for side,pairs in enumerate(sides):
   for bg in pairs:F[i,col[(side,*bg)]]=1/math.sqrt(2*len(pairs))
 return F
def score(labels,F):
 cats=sorted(set(labels));Y=np.array([[int(y==c) for c in cats] for y in labels],dtype=float);Z=Y-Y.mean(axis=0);den=float(np.sum(Z*Z));assert den>0
 U=Z.T@F;return float(np.sum(U*U)/den)
def witness(labels,F,obs,tol):
 for i in range(len(labels)):
  for j in range(i+1,len(labels)):
   if labels[i]==labels[j]:continue
   alt=labels.copy();alt[i],alt[j]=alt[j],alt[i];v=score(alt,F)
   if abs(v-obs)>tol:return {'i':i,'j':j,'swapped_score':v}
 return None
def project(spec):
 strict=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');pat=re.compile('|'.join(sorted(spec['signs'],key=lambda x:(-len(x),x))));output={};counts={}
 for ed in spec['readers']:
  rows=strict[ed];positions={};original={};line_sizes={}
  for phase in ['DISCOVERY','EVALUATION']:
   d=read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')
   assert d['group_columns']==['source_group_id','source_group_index','ivtff_group_raw','left_separator','right_separator']
   for line in d['lines']:
    m=line['metadata'];assert m['edition']==ed and m['page'] in spec['allowed'] and not m['page'].startswith('f84') and m['page'] not in ('f1r','f116v')
    n=int(m['source_group_count']);assert n==len(line['groups']) and [int(g[1]) for g in line['groups']]==list(range(1,n+1))
    lk=(m['page'],m['locus']);assert lk not in line_sizes;line_sizes[lk]=n
    for g in line['groups']:
     assert g[0] not in original;original[g[0]]=(m,g)
  for row in rows:
   m,g=original[row['id']];assert row['edition']==ed and row['page']==m['page'] and row['locus']==m['locus'] and row['kind']==m['kind']=='P'
   assert [row['id'],str(row['source_group_index']),row['ivtff_group_raw'],row['left_separator'],row['right_separator']]==g
   assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert pat.findall(row['ivtff_group_raw'])==row['units'] and ''.join(row['units'])==row['ivtff_group_raw']
   key=(row['page'],row['locus'],int(row['source_group_index']));assert key not in positions;positions[key]=row
  cells=collections.defaultdict(list);count={'strict_groups':len(rows),'three_strict_positions':0,'single_run_positions':0}
  for key,row in sorted(positions.items()):
   page,loc,j=key;left=positions.get((page,loc,j-1));right=positions.get((page,loc,j+1))
   if left is None or right is None:continue
   count['three_strict_positions']+=1;src,runs=collapse(row['units'])
   if len(runs)!=1:continue
   count['single_run_positions']+=1;n=line_sizes[page,loc];third=min(2,3*(j-1)//n)
   ev={'id':row['id'],'raw':row['ivtff_group_raw'],'length':runs[0][2],'left_id':left['id'],'left_raw':left['ivtff_group_raw'],'left_source':collapse(left['units'])[0],'right_id':right['id'],'right_raw':right['ivtff_group_raw'],'right_source':collapse(right['units'])[0],'line_groups':n,'index':j}
   cells[(page,tuple(src),third)].append(ev)
  selected=[]
  for (page,src,third),events in sorted(cells.items()):
   if len(events)<3 or len({e['length'] for e in events})<2:continue
   selected.append({'page':page,'leaf':re.match(r'f\d+',page).group(),'source':list(src),'third':third,'events':sorted(events,key=lambda e:e['id'])})
  count['candidate_cells']=len(selected);output[ed]=selected;counts[ed]=count
 return output,counts

def evaluate(cells,counts,spec,reader_index):
 prepared=[];leaves=collections.Counter(c['leaf'] for c in cells)
 for c in cells:
  F=features(c);labels=[e['length'] for e in c['events']];obs=score(labels,F);wit=witness(labels,F,obs,spec['swap_tolerance']);c.update(score=obs,witness=wit);prepared.append((F,labels))
 ws=[c for c in cells if c['witness'] is not None];counts.update(witnessed_cells=len(ws),witnessed_occurrences=sum(len(c['events']) for c in ws),witnessed_leaves=len({c['leaf'] for c in ws}),score_leaves=len(leaves))
 weights=[1/(len(leaves)*leaves[c['leaf']]) for c in cells];obs=math.fsum(c['score']*w for c,w in zip(cells,weights));entry={'counts':counts,'observed':obs}
 cap=counts['witnessed_cells']>=spec['min_witnessed_cells'] and counts['witnessed_occurrences']>=spec['min_witnessed_occurrences'] and counts['witnessed_leaves']>=spec['min_witnessed_leaves']
 if not cap:entry['status']='CAPACITY_STOP';return entry,[]
 rng=random.Random(spec['seed']+reader_index);global_null=np.zeros(spec['draws']);leaf_null={leaf:np.zeros(spec['draws']) for leaf in leaves};leaf_obs={leaf:0. for leaf in leaves}
 for c,(F,labels),w in zip(cells,prepared,weights):
  n=len(labels);cats=sorted(set(labels));base=np.array([[float(y==k) for k in cats] for y in labels]);mean=base.mean(axis=0);den=float(np.sum((base-mean)**2));perms=[]
  for draw in range(spec['draws']):
   order=list(range(n));rng.shuffle(order);perms.append(order)
  Z=base[np.array(perms)]-mean;U=np.einsum('bnc,nf->bcf',Z,F,optimize=True);sc=np.sum(U*U,axis=(1,2))/den
  global_null+=w*sc;leaf_null[c['leaf']]+=sc/leaves[c['leaf']];leaf_obs[c['leaf']]+=c['score']/leaves[c['leaf']]
 null=global_null.tolist();mu=math.fsum(null)/len(null);sd=math.sqrt(math.fsum((v-mu)**2 for v in null)/(len(null)-1));p=(1+sum(v>=obs-1e-12 for v in null))/(len(null)+1);gain=(obs-mu)/mu if mu>0 else None
 summaries=[{'leaf':leaf,'observed':leaf_obs[leaf],'null_mean':float(np.mean(leaf_null[leaf]))} for leaf in sorted(leaves)];directions=sum(x['observed']>x['null_mean']+1e-12 for x in summaries)
 a,b=spec['leaf_direction_fraction'];reject=p<=spec['p_max'] and gain is not None and gain>=spec['relative_gain_min'] and directions*b>=a*len(leaves)
 entry.update(status='REJECTED' if reject else 'NOT_REJECTED',statistics={'null_mean':mu,'null_sd':sd,'p_upper':p,'relative_gain':gain,'direction_leaves':directions,'leaves':len(leaves)},leaf_summaries=summaries)
 return entry,null

def controls():
 # Categorical masses cancel after preserving a complete histogram.
 from fractions import Fraction
 labels=[1,1,2,3];assignments=set(itertools.permutations(labels));probs=[math.prod(Fraction({1:2,2:3,3:5}[v],10) for v in a) for a in assignments];assert len(set(probs))==1 and len(assignments)==12
 F=np.array([[1.,0.],[1.,0.],[0.,1.]]);a=[1,1,2];values=[score(list(p),F) for p in set(itertools.permutations(a))];assert max(values)>min(values) and witness(a,F,score(a,F),1e-9)
 for a,F in [([1,2],np.eye(2)),([1,2,3],np.array([[1.,0.],[1.,0.],[0.,1.]])),([1,1,2],np.ones((3,1)))]:
  vals=[score(list(p),F) for p in set(itertools.permutations(a))];assert max(vals)-min(vals)<1e-12 and witness(a,F,score(a,F),1e-9) is None
 for l in range(1,5):
  for rr in range(1,5):assert collapse(['q']+['e']*l+['d']+['i']*rr+['n'])[0]==['q','e','d','i','n']
 cell={'events':[{'left_source':[x],'right_source':['c']} for x in ['a','a','b']]};F=features(cell)
 assert np.allclose(F@F.T,[[1,1,.5],[1,1,.5],[.5,.5,1]],atol=1e-12)
 labs=[1,1,2];perms=list(set(itertools.permutations(labs)));scalar=[score(list(p),F) for p in perms]
 assert math.isclose(score(labs,F),2/3) and math.isclose(math.fsum(scalar)/len(scalar),1/3)
 base=np.array([[[float(y==c) for c in [1,2]] for y in p] for p in perms]);Z=base-base.mean(axis=1,keepdims=True);U=np.einsum('bnc,nf->bcf',Z,F,optimize=True)
 batched=np.sum(U*U,axis=(1,2))/np.sum(Z[0]*Z[0]);assert np.allclose(batched,scalar,atol=1e-12)
 return {'status':'PASS_SOURCE_FREE_CONTROLS','categorical_assignments':12,'mobile_fixture':True,'invariant_fixtures':3,'adjacent_context_collapse_variants':16,'normalized_kernel_and_exact_orbit_mean':True,'batch_scalar_agreement':True,'native_access':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args()
 if a.controls:print(json.dumps(controls()));return
 lock=read(B/'LOCK.json')
 for item in lock['files']:assert hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
 spec=read(B/'src/SPEC.json');data,counts=project(spec);res={'readers':{}};nulls={}
 for i,ed in enumerate(spec['readers']):
  entry,draws=evaluate(data[ed],counts[ed],spec,i);res['readers'][ed]=entry;nulls[ed]=draws
 res['status']='CONTEXT_INDEPENDENT_RUN_CHOICE_REJECTED' if all(x['status']=='REJECTED' for x in res['readers'].values()) else ('CAPACITY_STOP' if any(x['status']=='CAPACITY_STOP' for x in res['readers'].values()) else 'NOT_REJECTED')
 save('DATA.json',{'readers':data});save('RESULT.json',res);save('NULLS.json',{'readers':nulls});print(json.dumps(res,indent=2))
if __name__=='__main__':main()
