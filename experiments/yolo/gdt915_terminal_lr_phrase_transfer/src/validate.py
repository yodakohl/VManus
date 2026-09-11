#!/usr/bin/env python3
"""Independent source/nomination/count and full conditional-world replay."""
import collections,hashlib,json,re
from pathlib import Path
import numpy as np
E=Path(__file__).resolve().parents[1]
def load(name):return json.loads((E/'artifacts'/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(phase,ed):
 d=load(f'SOURCE_{phase}_{ed}.json');tokens=[];pairs=[];strata=collections.defaultdict(list);den=dict(lines=0,raw_adjacent=0,eligible_pairs=0)
 for line in d['lines']:
  m=line['metadata'];assert not m['page'].startswith('f84');leaf=int(re.match(r'f(\d+)',m['page'])[1]);assert leaf%2==(phase=='DISCOVERY')
  if m['kind']!='P':continue
  den['lines']+=1;gs=[dict(zip(d['group_columns'],g)) for g in line['groups']];den['raw_adjacent']+=max(0,len(gs)-1);local={};n=int(m['source_group_count'])
  for j,g in enumerate(gs):
   w=g['ivtff_group_raw'];idx=int(g['source_group_index'])
   if re.fullmatch('[a-z]+[rl]',w) is None:continue
   pos='SINGLE' if n==1 else 'FIRST' if idx==1 else 'LAST' if idx==n else 'INTERNAL';i=len(tokens);local[j]=i
   tokens.append((w,leaf));strata[(leaf,w[:-1],pos)].append(i)
  for j in range(len(gs)-1):
   if j not in local or j+1 not in local:continue
   a,b=local[j],local[j+1];x,y=gs[j:j+2]
   if tokens[a][0][:-1]==tokens[b][0][:-1]:continue
   if int(y['source_group_index'])-int(x['source_group_index'])!=1 or x['right_separator']!='DEFINITE_SPACE' or y['left_separator']!='DEFINITE_SPACE':continue
   pairs.append(dict(a=a,b=b,leaf=leaf,locus=m['locus'],page=m['page'],source_ids=[x['source_group_id'],y['source_group_id']],stems=[tokens[a][0][:-1],tokens[b][0][:-1]],words=[tokens[a][0],tokens[b][0]]));den['eligible_pairs']+=1
 bits=np.array([w.endswith('l') for w,l in tokens],dtype=np.int8);mixed=[np.array(ids,dtype=int) for ids in strata.values() if len(set(bits[ids]))==2];movable={int(i) for ids in mixed for i in ids}
 return dict(tokens=tokens,pairs=pairs,bits=bits,mixed=mixed,movable=movable,den=den)
def census(d,bits):
 c=collections.defaultdict(lambda:{x:[] for x in ['rr','rl','lr','ll']})
 for p in d['pairs']:c[tuple(p['stems'])]['rl'[bits[p['a']]]+'rl'[bits[p['b']]]].append(p)
 return c
def nominate(c):return sorted(k for k,v in c.items() if v['rr'] and v['ll'] and len({p['leaf'] for p in v['rr']+v['ll']})>=2)
def score(d,bits,chosen):
 leaves={str(p['leaf']):dict(eligible=0,same=0,mixed=0,movable=0) for p in d['pairs']};chosen=set(chosen)
 for p in d['pairs']:
  leaf=leaves[str(p['leaf'])];leaf['eligible']+=1
  if tuple(p['stems']) in chosen:
   leaf['same' if bits[p['a']]==bits[p['b']] else 'mixed']+=1
   leaf['movable']+=int(p['a'] in d['movable'] or p['b'] in d['movable'])
 T=sum((v['same']-v['mixed'])/v['eligible'] for v in leaves.values())/len(leaves) if leaves else 0
 return leaves,T
def main():
 for name in ['PREREG_LOCK.json','DISCOVERY_LOCK.json']:
  lock=json.loads((E/name).read_text())
  for path,digest in lock['files'].items():assert sha(E/path)==digest
 dr=load('DISCOVERY_RESULT.json');res=load('RESULT.json');chosen=[tuple(x) for x in load('CANDIDATES.json')];data={}
 for ed in ['ZL3b','IT2a','RF1b']:
  for phase in ['DISCOVERY','EVALUATION']:
   d=prepare(phase,ed);data[(phase,ed)]=d;c=census(d,d['bits']);base=dict(denominators=d['den'],tokens=len(d['tokens']),movable_strata=len(d['mixed']),movable_tokens=len(d['movable']))
   if phase=='DISCOVERY':
    expected=[dict(stems=list(k),cells=c[k]) for k in sorted(c)];assert expected==load(f'DISCOVERY_CENSUS_{ed}.json')
    base.update(stem_pairs=len(c),own_qualifying_pairs=len(nominate(c)));assert base==dr['readings'][ed]
    if ed=='ZL3b':assert nominate(c)==chosen
   else:
    ev=load(f'EVALUATION_{ed}.json');leaves,T=score(d,d['bits'],chosen);assert leaves==ev['leaves'] and abs(T-ev['T'])<1e-14
    for k,o in zip(chosen,ev['candidates']):
     cells=c.get(k,{x:[] for x in ['rr','rl','lr','ll']});occ=sum((cells[x] for x in ['rr','rl','lr','ll']),[])
     assert o['stems']==list(k) and o['cells']=={x:len(v) for x,v in cells.items()}
     assert sorted(o['occurrences'],key=lambda p:p['a'])==sorted(occ,key=lambda p:p['a']) and o['leaves']==sorted({p['leaf'] for p in occ})
    aggregate=dict(T=T,same=sum(v['same'] for v in leaves.values()),mixed=sum(v['mixed'] for v in leaves.values()),nominated_leaves=sum(bool(v['same']+v['mixed']) for v in leaves.values()),movable_nominated_leaves=sum(v['movable']>0 for v in leaves.values()))
    for k,v in aggregate.items():assert abs(ev[k]-v)<1e-14
    for k,v in (base|aggregate).items():assert abs(res['readings'][ed][k]-v)<1e-14 if isinstance(v,float) else res['readings'][ed][k]==v
 assert len(chosen)==dr['candidates']==res['candidates']==22
 worlds=load('NULL_WORLDS.json')['rows'];assert len(worlds)==1024
 for j,count,T in worlds:
  rng=np.random.default_rng(915000+j);ys=[]
  for phase in ['DISCOVERY','EVALUATION']:
   d=data[(phase,'ZL3b')];y=d['bits'].copy()
   for ids in d['mixed']:
    y[ids]=rng.permutation(y[ids]);assert int(y[ids].sum())==int(d['bits'][ids].sum())
   ys.append(y)
  nominated=nominate(census(data[('DISCOVERY','ZL3b')],ys[0]));_,actual=score(data[('EVALUATION','ZL3b')],ys[1],nominated)
  assert len(nominated)==count and abs(actual-T)<1e-14,(j,len(nominated),count,actual,T)
 observed=res['readings']['ZL3b']['T'];tail=sum(t>=observed for j,n,t in worlds);ref=res['conditional_reference']
 assert ref['at_least_observed']==tail and abs(ref['tail_rank']-(tail+1)/1025)<1e-14 and abs(ref['mean_T']-np.mean([t for j,n,t in worlds]))<1e-14
 assert res['meaning_claims']==0 and res['project_significance_claim'] is False
 assert res['adequate_replication']==(len(chosen)>=5 and res['readings']['ZL3b']['nominated_leaves']>=5 and res['readings']['ZL3b']['movable_nominated_leaves']>=5)
 receipt=dict(status='PASS',frozen_locks_verified=['PREREG_LOCK.json','DISCOVERY_LOCK.json'],validator_sha256=sha(Path(__file__)),candidates=22,worlds_replayed=1024,all_stratum_margins_checked=True,source_and_artifact_sha256={p.name:sha(p) for p in (E/'artifacts').glob('*.json') if p.name!='VALIDATION.json'},limits='conditional exploratory reference, not project-wide significance or semantic identification')
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
