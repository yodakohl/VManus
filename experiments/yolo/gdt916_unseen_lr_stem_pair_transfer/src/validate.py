#!/usr/bin/env python3
"""Independent category and world replay, reusing only independently authored915 parser."""
import collections,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
p=E.parent/'gdt915_terminal_lr_phrase_transfer/src/validate.py';sp=importlib.util.spec_from_file_location('independent915',p);v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
def load(n):return json.loads((E/'artifacts'/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def classify(d,e):
 seen={tuple(x['stems']) for x in d['pairs']};license=collections.defaultdict(set)
 for word,leaf in d['tokens']:license[word[:-1]].add(word[-1])
 return ['A_SEEN' if tuple(p['stems']) in seen else 'B_NEW_LICENSED' if all(license[s]=={'r','l'} for s in p['stems']) else 'C_OTHER_NEW' for p in e['pairs']]
def report(e,categories,bits):
 out={}
 for category in ['A_SEEN','B_NEW_LICENSED','C_OTHER_NEW']:
  occ=[];leaves=collections.defaultdict(lambda:dict(same=0,mixed=0,movable=0));cells=dict(rr=0,rl=0,lr=0,ll=0)
  for p,cat in zip(e['pairs'],categories):
   if cat!=category:continue
   cell='rl'[bits[p['a']]]+'rl'[bits[p['b']]];cells[cell]+=1;occ.append(p|dict(cell=cell));x=leaves[str(p['leaf'])];x['same' if cell[0]==cell[1] else 'mixed']+=1;x['movable']+=int(p['a'] in e['movable'] or p['b'] in e['movable'])
  T=sum((x['same']-x['mixed'])/(x['same']+x['mixed']) for x in leaves.values())/len(leaves) if leaves else 0
  out[category]=dict(T=T,cells=cells,leaves=dict(leaves),movable_leaves=sum(x['movable']>0 for x in leaves.values()),occurrences=occ,pairs=len(occ),physical_leaves=len(leaves),stem_pairs=len({tuple(p['stems']) for p in occ}))
 return out
def main():
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for path,digest in lock['files'].items():assert sha(ROOT/path)==digest
 result=load('RESULT.json');datasets={}
 for ed in ['ZL3b','IT2a','RF1b']:
  d=v.prepare('DISCOVERY',ed);e=v.prepare('EVALUATION',ed);cats=classify(d,e);actual=report(e,cats,e['bits']);expected=load(f'OBSERVED_{ed}.json');datasets[ed]=(d,e,cats)
  for category,a in actual.items():
   b=expected[category];assert abs(a['T']-b['T'])<1e-14
   assert {k:x for k,x in a.items() if k!='T'}=={k:x for k,x in b.items() if k!='T'}
   summary={k:x for k,x in a.items() if k not in ['occurrences','leaves']}
   for k,x in summary.items():assert abs(x-result['readings'][ed][category][k])<1e-14 if isinstance(x,float) else x==result['readings'][ed][category][k]
  assert sum(x['pairs'] for x in actual.values())==len(e['pairs'])
 d,e,cats=datasets['ZL3b'];worlds=load('NULL_WORLDS.json')['rows'];assert len(worlds)==1024
 # Fixed category is invariant under within-stem stratum permutations.
 b_indices=[i for i,c in enumerate(cats) if c=='B_NEW_LICENSED'];leaf_indices=collections.defaultdict(list)
 for i in b_indices:leaf_indices[e['pairs'][i]['leaf']].append(i)
 for j,T in worlds:
  rng=np.random.default_rng(915000+j)
  for data in [d,e]:
   y=data['bits'].copy()
   for ids in data['mixed']:
    y[ids]=rng.permutation(y[ids]);assert y[ids].sum()==data['bits'][ids].sum()
  value=sum(sum(1 if y[e['pairs'][i]['a']]==y[e['pairs'][i]['b']] else -1 for i in ids)/len(ids) for ids in leaf_indices.values())/len(leaf_indices)
  assert abs(value-T)<1e-14,(j,value,T)
 B=result['readings']['ZL3b']['B_NEW_LICENSED'];capacity=B['stem_pairs']>=5 and B['physical_leaves']>=5 and B['movable_leaves']>=5;assert result['capacity']==capacity
 mean=float(np.mean([t for j,t in worlds]));tail=sum(t>=B['T'] for j,t in worlds);rank=(tail+1)/1025;ref=result['conditional_reference']
 assert abs(ref['mean_B_T']-mean)<1e-14 and ref['at_least_observed']==tail and ref['tail_rank']==rank
 positive=capacity and B['T']>mean and rank<=.01
 assert not positive and result['status']=='NEW_PAIR_CONCORDANCE_NOT_ESTABLISHED'
 assert result['meaning_claims']==0 and not result['project_significance_claim'] and result['previously_exposed_source']
 receipt=dict(status='PASS',worlds_replayed=1024,complete_readings=3,all_occurrences_categories_cells_and_leaves_checked=True,all_permutation_margins_checked=True,capacity=capacity,positive_diagnostic=positive,validator_sha256=sha(Path(__file__)),independent915_dependency_sha256=sha(p),prereg_lock_sha256=sha(E/'PREREG_LOCK.json'),artifacts={x.name:sha(x) for x in (E/'artifacts').glob('*.json') if x.name!='VALIDATION.json'})
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
