#!/usr/bin/env python3
import argparse,collections,hashlib,importlib.util,json,re
from pathlib import Path
import numpy as np
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(n,x):(E/'artifacts'/n).write_text(enc(x))
def read(n):return json.loads((E/'artifacts'/n).read_text())
def module(name,p):
 sp=importlib.util.spec_from_file_location(name,ROOT/p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def intake(phase,s,cached):
 if not cached:
  assert not (E/'artifacts'/f'SOURCE_{phase}_ZL3b.json').exists(),'source already captured; use --cached'
  ss=dict(s,allowed_selectors=s['partitions'][phase]);reader=module('gdt829_guard','experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py');packer=module('gdt851_pack','experiments/yolo/gdt851_primitive_tandem_raw_group_discovery/src/run.py');rows,guard=reader.query(ss);packed=packer.pack(rows,ss);save(f'GUARD_{phase}.json',guard)
  for ed,lines in packed.items():save(f'SOURCE_{phase}_{ed}.json',dict(group_columns=s['group_columns'],lines=lines))
 return {ed:read(f'SOURCE_{phase}_{ed}.json') for ed in s['editions']}

def prepare(data,s,phase):
 tokens=[];pairs=[];strata=collections.defaultdict(list);den=collections.Counter(lines=0,raw_adjacent=0,eligible_pairs=0)
 for line in data['lines']:
  m=line['metadata'];assert m['page'] in s['partitions'][phase] and not m['page'].startswith('f84')
  if m['kind']!='P':continue
  den['lines']+=1;gs=[dict(zip(data['group_columns'],v)) for v in line['groups']];local={};leaf=int(re.match(r'f(\d+)',m['page'])[1])
  for i,g in enumerate(gs):
   w=g['ivtff_group_raw']
   if not re.fullmatch('[a-z]+',w) or len(w)<2 or w[-1] not in 'rl':continue
   index=int(g['source_group_index']);n=int(m['source_group_count']);pos='SINGLE' if n==1 else 'FIRST' if index==1 else 'LAST' if index==n else 'INTERNAL';ti=len(tokens);local[i]=ti
   tokens.append(dict(source_id=g['source_group_id'],page=m['page'],locus=m['locus'],index=index,leaf=leaf,word=w,stem=w[:-1],ending=w[-1],position=pos));strata[(leaf,w[:-1],pos)].append(ti)
  for i in range(len(gs)-1):
   den['raw_adjacent']+=1
   if i not in local or i+1 not in local:continue
   a,b=local[i],local[i+1];ga,gb=gs[i:i+2]
   if tokens[a]['stem']==tokens[b]['stem'] or int(gb['source_group_index'])!=int(ga['source_group_index'])+1 or ga['right_separator']!=gb['left_separator'] or ga['right_separator']!='DEFINITE_SPACE':continue
   pairs.append(dict(a=a,b=b,stems=[tokens[a]['stem'],tokens[b]['stem']],leaf=leaf,page=m['page'],locus=m['locus'],source_ids=[tokens[a]['source_id'],tokens[b]['source_id']]));den['eligible_pairs']+=1
 endings=np.array([t['ending']=='l' for t in tokens],dtype=np.int8);movable=[np.array(v,dtype=int) for v in strata.values() if len({int(endings[i]) for i in v})>1];moving={int(i) for v in movable for i in v}
 return dict(tokens=tokens,pairs=pairs,endings=endings,movable=movable,moving=moving,den=dict(den))

def census(d,endings=None):
 y=d['endings'] if endings is None else endings;by=collections.defaultdict(lambda:collections.defaultdict(list))
 for p in d['pairs']:
  cell=('l' if y[p['a']] else 'r')+('l' if y[p['b']] else 'r');by[tuple(p['stems'])][cell].append(p)
 return by

def nominate(d,y=None):
 by=census(d,y);return sorted(k for k,v in by.items() if v.get('rr') and v.get('ll') and len({p['leaf'] for cell in ['rr','ll'] for p in v[cell]})>=2)

def evaluate(d,candidates,y=None):
 candidates=set(map(tuple,candidates));y=d['endings'] if y is None else y;leaves=collections.defaultdict(lambda:dict(eligible=0,same=0,mixed=0,movable=0));rows=[];by=census(d,y)
 for p in d['pairs']:
  q=leaves[p['leaf']];q['eligible']+=1
  if tuple(p['stems']) in candidates:
   q['same' if y[p['a']]==y[p['b']] else 'mixed']+=1;q['movable']+=int(p['a'] in d['moving'] or p['b'] in d['moving'])
 for k in sorted(candidates):
  v=by.get(k,{});rows.append(dict(stems=list(k),cells={cell:len(v.get(cell,[])) for cell in ['rr','rl','lr','ll']},leaves=sorted({p['leaf'] for ps in v.values() for p in ps}),occurrences=[dict(p,words=[d['tokens'][p['a']]['stem']+('l' if y[p['a']] else 'r'),d['tokens'][p['b']]['stem']+('l' if y[p['b']] else 'r')]) for cell in ['rr','rl','lr','ll'] for p in v.get(cell,[])]))
 t=float(np.mean([(v['same']-v['mixed'])/v['eligible'] for v in leaves.values()])) if leaves else 0.
 return dict(T=t,leaves={str(k):v for k,v in sorted(leaves.items())},candidates=rows,same=sum(v['same'] for v in leaves.values()),mixed=sum(v['mixed'] for v in leaves.values()),nominated_leaves=sum(v['same']+v['mixed']>0 for v in leaves.values()),movable_nominated_leaves=sum(v['movable']>0 for v in leaves.values()))

def draw(d,rng):
 y=d['endings'].copy()
 for v in d['movable']:y[v]=rng.permutation(y[v])
 return y

def main():
 ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['discovery','evaluation']);ap.add_argument('--cached',action='store_true');a=ap.parse_args();s=json.loads((E/'src/SPEC.json').read_text());lock=json.loads((E/'PREREG_LOCK.json').read_text());assert all(hashlib.sha256((E/p).read_bytes()).hexdigest()==h for p,h in lock['files'].items())
 if a.phase=='discovery':
  src=intake('DISCOVERY',s,a.cached);decks={ed:prepare(x,s,'DISCOVERY') for ed,x in src.items()};c=nominate(decks['ZL3b']);save('CANDIDATES.json',[list(k) for k in c]);result={}
  for ed,d in decks.items():
   by=census(d);cards=[dict(stems=list(k),cells={cell:[dict(p,words=[d['tokens'][p['a']]['word'],d['tokens'][p['b']]['word']]) for p in v.get(cell,[])] for cell in ['rr','rl','lr','ll']}) for k,v in sorted(by.items())];save(f'DISCOVERY_CENSUS_{ed}.json',cards);result[ed]=dict(denominators=d['den'],tokens=len(d['tokens']),stem_pairs=len(by),own_qualifying_pairs=len(nominate(d)),movable_strata=len(d['movable']),movable_tokens=len(d['moving']))
  save('DISCOVERY_RESULT.json',dict(candidates=len(c),readings=result));print(enc(dict(candidates=c,readings=result)));return
 freeze=json.loads((E/'DISCOVERY_LOCK.json').read_text());assert all(hashlib.sha256((E/p).read_bytes()).hexdigest()==h for p,h in freeze['files'].items());c=read('CANDIDATES.json');assert c,'no candidates: no evaluation access'
 ds=intake('DISCOVERY',s,True);es=intake('EVALUATION',s,a.cached);dis={ed:prepare(x,s,'DISCOVERY') for ed,x in ds.items()};ev={ed:prepare(x,s,'EVALUATION') for ed,x in es.items()};results={}
 for ed,d in ev.items():
  r=evaluate(d,c);save(f'EVALUATION_{ed}.json',r);results[ed]={k:v for k,v in r.items() if k not in ['leaves','candidates']};results[ed].update(denominators=d['den'],tokens=len(d['tokens']),movable_strata=len(d['movable']),movable_tokens=len(d['moving']))
 worlds=[]
 for j in range(s['worlds']):
  rng=np.random.default_rng(s['seed_base']+j);dy=draw(dis['ZL3b'],rng);ey=draw(ev['ZL3b'],rng);nc=nominate(dis['ZL3b'],dy);r=evaluate(ev['ZL3b'],nc,ey);worlds.append([j,len(nc),r['T']])
 save('NULL_WORLDS.json',dict(columns=['world','candidate_count','T'],rows=worlds));obs=results['ZL3b']['T'];greater=sum(x[2]>=obs-1e-15 for x in worlds);adequate=len(c)>=5 and results['ZL3b']['nominated_leaves']>=5 and results['ZL3b']['movable_nominated_leaves']>=5
 result=dict(status='COMPLETE_EXPLORATORY_PHRASE_TRANSFER',candidates=len(c),readings=results,adequate_replication=adequate,conditional_reference=dict(worlds=len(worlds),at_least_observed=greater,tail_rank=(1+greater)/(1+len(worlds)),mean_T=float(np.mean([x[2] for x in worlds]))),project_significance_claim=False,meaning_claims=0);save('RESULT.json',result);print(enc(result))
if __name__=='__main__':main()
