import collections,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];P=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(n,x):(E/'artifacts'/n).write_text(enc(x))
def helper():
 sp=importlib.util.spec_from_file_location('frozen915',P/'src/run.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def classify(d,e):
 seen={tuple(p['stems']) for p in d['pairs']};licenses=collections.defaultdict(set)
 for t in d['tokens']:licenses[t['stem']].add(t['ending'])
 cats=[]
 for p in e['pairs']:
  k=tuple(p['stems']);cats.append('A_SEEN' if k in seen else 'B_NEW_LICENSED' if all(licenses[x]=={'r','l'} for x in k) else 'C_OTHER_NEW')
 return cats

def score(e,cats,y=None,detail=True):
 y=e['endings'] if y is None else y;groups={k:[] for k in ['A_SEEN','B_NEW_LICENSED','C_OTHER_NEW']}
 for p,k in zip(e['pairs'],cats):groups[k].append(p)
 out={}
 for k,ps in groups.items():
  leaves=collections.defaultdict(lambda:dict(same=0,mixed=0,movable=0));cells=collections.Counter(rr=0,rl=0,lr=0,ll=0);records=[]
  for p in ps:
   cell=('l' if y[p['a']] else 'r')+('l' if y[p['b']] else 'r');cells[cell]+=1;v=leaves[p['leaf']];v['same' if cell[0]==cell[1] else 'mixed']+=1;v['movable']+=int(p['a'] in e['moving'] or p['b'] in e['moving'])
   if detail:records.append(dict(p,words=[e['tokens'][p['a']]['stem']+cell[0],e['tokens'][p['b']]['stem']+cell[1]],cell=cell))
  t=float(np.mean([(v['same']-v['mixed'])/(v['same']+v['mixed']) for v in leaves.values()])) if leaves else 0.
  out[k]=dict(T=t,pairs=len(ps),stem_pairs=len({tuple(p['stems']) for p in ps}),physical_leaves=len(leaves),movable_leaves=sum(v['movable']>0 for v in leaves.values()),cells=dict(cells))
  if detail:out[k].update(leaves={str(f):v for f,v in sorted(leaves.items())},occurrences=records)
 return out

def main():
 lock=json.loads((E/'PREREG_LOCK.json').read_text());assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in lock['files'].items());r=helper();spec=json.loads((P/'src/SPEC.json').read_text());decks={};outputs={}
 for ed in spec['editions']:
  d=r.prepare(json.loads((P/'artifacts'/f'SOURCE_DISCOVERY_{ed}.json').read_text()),spec,'DISCOVERY');e=r.prepare(json.loads((P/'artifacts'/f'SOURCE_EVALUATION_{ed}.json').read_text()),spec,'EVALUATION');cats=classify(d,e);decks[ed]=(d,e,cats);o=score(e,cats);save(f'OBSERVED_{ed}.json',o);outputs[ed]={k:{a:b for a,b in v.items() if a not in ['leaves','occurrences']} for k,v in o.items()}
 d,e,cats=decks['ZL3b'];worlds=[]
 for j in range(1024):
  rng=np.random.default_rng(915000+j);r.draw(d,rng);y=r.draw(e,rng);v=score(e,cats,y,False);worlds.append([j,v['B_NEW_LICENSED']['T']])
 save('NULL_WORLDS.json',dict(columns=['world','B_T'],rows=worlds));b=outputs['ZL3b']['B_NEW_LICENSED'];avg=float(np.mean([v[1] for v in worlds]));ge=sum(v[1]>=b['T']-1e-15 for v in worlds);rank=(1+ge)/1025;capacity=b['stem_pairs']>=5 and b['physical_leaves']>=5 and b['movable_leaves']>=5;positive=capacity and b['T']>avg and rank<=.01
 result=dict(status='NEW_PAIR_CONCORDANCE_DIAGNOSTIC_POSITIVE' if positive else 'NEW_PAIR_CONCORDANCE_NOT_ESTABLISHED',capacity=capacity,readings=outputs,conditional_reference=dict(mean_B_T=avg,at_least_observed=ge,worlds=1024,tail_rank=rank),previously_exposed_source=True,project_significance_claim=False,meaning_claims=0);save('RESULT.json',result);print(enc(result))
if __name__=='__main__':main()
