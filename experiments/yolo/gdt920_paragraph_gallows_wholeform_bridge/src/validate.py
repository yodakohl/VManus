#!/usr/bin/env python3
"""Independent raw-cache paragraph, complete matrix and randomization replay."""
import json,re,hashlib,random,math
from collections import defaultdict,Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];OLD=E.parent/'gdt915_terminal_lr_phrase_transfer'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def equal(a,b):
 if isinstance(a,dict):assert a.keys()==b.keys();[equal(a[k],b[k]) for k in a]
 elif isinstance(a,list):assert len(a)==len(b);[equal(x,y) for x,y in zip(a,b)]
 elif isinstance(a,float):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-13),(a,b)
 else:assert a==b,(a,b)
def eligible(g):return bool(re.fullmatch('[a-z]+',g['ivtff_group_raw'])) and g['left_separator'] in ['LINE_START','DEFINITE_SPACE'] and g['right_separator'] in ['LINE_END','DEFINITE_SPACE']
def anchor(w):return w.count('p')+w.count('f')==1 and 'k' not in w and 't' not in w
def mapped(w,g):return w.translate(str.maketrans('pf','kt' if g=='A' else 'tk'))
def frames(rows):
 pages=defaultdict(list)
 for m,gs in rows:pages[m['page']].append((m,gs))
 out=[];ex=[]
 for page,rs in sorted(pages.items()):
  pending=[]
  for m,gs in sorted(rs,key=lambda r:int(r[0]['source_row_index'])):
   if m['paragraph_start']=='1':
    if pending:ex.append(dict(loci=[x[0]['locus'] for x in pending],reason='RESET_BEFORE_END'))
    pending=[];opened=True
   elif not pending:continue
   pending.append((m,gs))
   if m['paragraph_end']=='1':
    loci=[x[0]['locus'] for x in pending]
    if len(pending)>=2 and all(x[0]['kind']=='P' for x in pending):out.append(loci)
    else:ex.append(dict(loci=loci,reason='SHORT_OR_NON_P'))
    pending=[]
  if pending:ex.append(dict(loci=[x[0]['locus'] for x in pending],reason='UNFINISHED_TAIL'))
 return dict(frames=out,exclusions=ex)
def build(rows,bounds,ed):
 lookup={m['locus']:(m,gs) for m,gs in rows};fs=[];ex=[]
 for loci in bounds:
  if any(l not in lookup or lookup[l][0]['kind']!='P' for l in loci):ex.append(dict(loci=loci,reason='MISSING_OR_NON_P_ALIGNMENT'));continue
  rs=[lookup[l] for l in loci];m=rs[0][0]
  words=lambda row:[dict(id=g['source_group_id'],locus=row[0]['locus'],word=g['ivtff_group_raw']) for g in row[1] if eligible(g)]
  body=[x for row in rs[1:] for x in words(row)]
  if not body:ex.append(dict(loci=loci,reason='EMPTY_ELIGIBLE_BODY'));continue
  head=[x for x in words(rs[0]) if anchor(x['word'])]
  fs.append(dict(anchors=sorted({x['word'] for x in head}),body=body,header_occurrences=head,id=loci[0],leaf=re.match(r'f\d+',m['page'])[0],loci=loci,page=m['page'],start_index=int(m['source_row_index'])))
 byleaf=defaultdict(list)
 for f in fs:byleaf[f['leaf']].append(f)
 leaves={};pred=[]
 for leaf,group in sorted(byleaf.items()):
  group.sort(key=lambda f:(f['page'],f['start_index']));n=len(group);total=sum(len(f['anchors']) for f in group);exchange=n>=2 and total>0
  counts=[Counter(x['word'] for x in f['body']) for f in group];sizes=[len(f['body']) for f in group]
  mats={g:[[0.0]*n for _ in group] for g in ['A','B']}
  for i,f in enumerate(group):
   for g in ['A','B']:
    for a in f['anchors']:
     w=mapped(a,g);rates=[c[w]/size for c,size in zip(counts,sizes)]
     for j,rate in enumerate(rates):mats[g][i][j]+=rate/total
     pred.append(dict(anchor=a,edition=ed,exchange_mean_rate=sum(rates)/n,exchangeable=exchange,leaf=leaf,map=g,mobile=max(rates)-min(rates)>1e-15,other_body_counts=[dict(count=counts[j][w],paragraph=other['id'],tokens=sizes[j]) for j,other in enumerate(group) if j!=i],own_body_tokens=sizes[i],own_count=counts[i][w],own_rate=rates[i],paragraph=f['id'],predicted_whole=w,witnesses=[x for x in f['body'] if x['word']==w]))
  if exchange:leaves[leaf]=dict(anchor_count=total,matrices=mats,paragraphs=[f['id'] for f in group])
 stats={}
 for g in ['A','B']:
  ps=[p for p in pred if p['map']==g and p['exchangeable']];nm=len(leaves)
  t=sum(sum(v['matrices'][g][i][i] for i in range(len(v['paragraphs']))) for v in leaves.values())/nm
  mu=sum(sum(sum(row)/len(row) for row in v['matrices'][g]) for v in leaves.values())/nm
  distinct=len({p['anchor'] for p in ps});mobile=len({p['leaf'] for p in ps if p['mobile']})
  stats[g]=dict(T=t,conditional_mean=mu,residual=t-mu,anchor_paragraphs=len(ps),distinct_anchors=distinct,mobile_leaves=mobile,capacity=distinct>=5 and mobile>=5,own_matches=sum(p['own_count'] for p in ps),own_positive_predictions=sum(p['own_count']>0 for p in ps))
 return dict(exclusions=ex,frames=fs,leaves=leaves,predictions=pred,statistics=stats)
def synthetic():
 def row(i,start,end,page='f1r'):
  return (dict(page=page,locus=page+'.'+str(i),source_row_index=str(i),paragraph_start=str(start),paragraph_end=str(end),kind='P'),[])
 assert frames([row(1,1,0),row(2,1,0),row(3,0,1)])['frames']==[['f1r.2','f1r.3']]
 assert not frames([row(1,1,0),row(2,0,1,'f1v')])['frames']
 assert anchor('chpody') and not anchor('pfody') and not anchor('pkoht')
 assert mapped('chpody','A')=='chkody' and mapped('chfody','B')=='chkody'
 g=dict(ivtff_group_raw='pody',left_separator='LINE_START',right_separator='DEFINITE_SPACE');assert eligible(g);g['right_separator']='UNCERTAIN_SPACE';assert not eligible(g)
 return 7
def main():
 lock=load(E/'PREREG_LOCK.json')
 for p,h in lock['files'].items():assert sha(R/p)==h,p
 allrows={}
 for ed in ['ZL3b','IT2a','RF1b']:
  allrows[ed]=[]
  for phase in ['DISCOVERY','EVALUATION']:
   d=load(OLD/'artifacts'/f'SOURCE_{phase}_{ed}.json')
   for row in d['lines']:
    m=row['metadata'];assert m['edition']==ed and not m['page'].startswith('f84')
    allrows[ed].append((m,[dict(zip(d['group_columns'],x)) for x in row['groups']]))
 boundary=frames(allrows['ZL3b']);equal(boundary,load(E/'artifacts/FRAME_BOUNDARIES.json'))
 summaries={};censuses={}
 for ed,rows in allrows.items():
  c=build(rows,boundary['frames'],ed);equal(c,load(E/'artifacts'/f'CENSUS_{ed}.json'));censuses[ed]=c
  summaries[ed]=dict(aligned_frames=len(c['frames']),excluded_frames=len(c['exclusions']),exchangeable_leaves=len(c['leaves']),predictions=len(c['predictions']),statistics=c['statistics'])
 c=censuses['ZL3b'];worlds=[]
 for j in range(1024):
  rng=random.Random(920000+j);scores=dict(A=0.0,B=0.0)
  for leaf,v in sorted(c['leaves'].items()):
   perm=list(range(len(v['paragraphs'])));rng.shuffle(perm)
   assert sorted(perm)==list(range(len(perm)))
   for g in scores:scores[g]+=sum(v['matrices'][g][i][k] for i,k in enumerate(perm))/len(c['leaves'])
  residuals={g:scores[g]-c['statistics'][g]['conditional_mean'] for g in scores}
  worlds.append(dict(world=j,residuals=residuals,maximum=max(residuals.values())))
 equal(worlds,load(E/'artifacts/WORLDS.json'))
 observed=max(s['residual'] for s in c['statistics'].values());ge=sum(w['maximum']>=observed-1e-12 for w in worlds);rank=(ge+1)/1025
 provisional=[g for g,s in c['statistics'].items() if s['capacity'] and s['residual']>0 and rank<=.05]
 result=load(E/'artifacts/RESULT.json');equal(result['editions'],summaries);equal(result['primary_observed_maximum'],observed);equal(result['joint_rank_fraction'],rank)
 assert result['worlds_ge_observed']==ge and result['provisional_maps']==provisional==[] and result['status']=='BRIDGE_NOT_ESTABLISHED' and result['confirmed_meanings']==result['fresh_confirmation_leaves']==0
 receipt=dict(status='PASS',validator_sha256=sha(Path(__file__)),prereg_lock_sha256=sha(E/'PREREG_LOCK.json'),locked_files_verified=len(lock['files']),output_sha256={p.name:sha(p) for p in sorted((E/'artifacts').glob('*.json')) if p.name!='VALIDATION.json'},editions=summaries,worlds_replayed=1024,worlds_ge_observed=ge,joint_rank_fraction=rank,synthetic_checks=synthetic(),scope='Complete source frames, anchors, predictions, matrices and all conditional worlds replayed independently. No bridge or lexical identity/meaning established.')
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
