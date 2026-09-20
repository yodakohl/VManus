#!/usr/bin/env python3
"""Independent direct-forward validation of finite conditional completions."""
import copy,gzip,hashlib,importlib.util,itertools,json,math
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];OLD=R/'experiments/yolo/gdt837_scg_integrated_wholeword_control'
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
 s=importlib.util.spec_from_file_location('independent_frozen_reference',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def forward(text,key,order):
 inverse={(v['role'],v['output']):c for c,v in key.items()}
 if ('W',text) in inverse:return (inverse['W',text],)
 for c in order:
  s=key[c]['output']
  if text.endswith(s) and len(text)-len(s)>=3:
   try:return tuple(inverse['L',x] for x in text[:-len(s)])+(c,)
   except KeyError:return None
 try:return tuple(inverse['L',x] for x in text)
 except KeyError:return None

def orders_by_behavior(key):
 S=sorted(c for c,v in key.items() if v['role']=='S');pairs=[]
 for a,b in itertools.combinations(S,2):
  x,y=key[a]['output'],key[b]['output']
  if x.endswith(y) or y.endswith(x):pairs.append((a,b))
 classes={}
 for order in itertools.permutations(S):
  sig=tuple(order.index(a)<order.index(b) for a,b in pairs)
  classes.setdefault(sig,[]).append(order)
 return list(classes.values())

def direct_orders(words,key):
 decoded={w:''.join(key[c]['output'] for c in w) for w in words};passing=[]
 for group in orders_by_behavior(key):
  if all(forward(text,key,group[0])==w for w,text in decoded.items()):passing.extend(group)
 return sorted(passing)

def independent_allowed(words,key,pool):
 # Directly run each single-candidate suffix dictionary on all literal spellings.
 # Other roles retain their original values; no use of runner's block list.
 literals={v['output']:c for c,v in key.items() if v['role']=='L'}
 whole={v['output']:c for c,v in key.items() if v['role']=='W'}
 allowable=[]
 for suffix in pool:
  invalid=False
  for w in words:
   if any(key[c]['role']!='L' for c in w):continue
   text=''.join(key[c]['output'] for c in w)
   if text in whole:continue
   stem=text[:-len(suffix)] if text.endswith(suffix) else ''
   if len(stem)>=3 and all(c in literals for c in stem):invalid=True;break
  if not invalid:allowable.append(suffix)
 return allowable

def check_one(payload):
 row,result=payload;fit=read(OLD/row['fit']);key=fit['key'];world=fit['world_id']
 cipher=read(OLD/f'prepared/world_{world}_discovery.json.gz')
 words=Counter(tuple(w) for p in cipher['paragraphs'] for w in p['words'])
 pool=read(OLD/'prepared/candidates.json')['suffix_pool'];S=sorted(c for c in key if key[c]['role']=='S')
 assert S==row['suffix_carriers']
 assert bool(direct_orders(words,key))==row['original_gate']['compatible']
 allowed=independent_allowed(words,key,pool)
 assert allowed==row['remaining_value_pool']
 model=load(R/'experiments/yolo/gdt832_joint_family_context_control/src/reference_model.py').load_model(E/'runtime/reference')
 found={};examined=0
 for values in itertools.permutations(allowed,4):
  examined+=1;k=copy.deepcopy(key)
  for c,v in zip(S,values):k[c]['output']=v
  orders=direct_orders(words,k)
  if orders:
   score=sum(model.paragraph_score([''.join(k[c]['output'] for c in w) for w in p['words']]) for p in cipher['paragraphs'])
   found[values]=(orders,score)
 assert row['nominal_assignments']==math.perm(12,4)==11880
 assert row['full_gate_assignments']==examined and row['rejected_by_literal_gate']==11880-examined
 assert set(found)=={tuple(x['suffix_values']) for x in row['completions']}
 for x in row['completions']:
  orders,score=found[tuple(x['suffix_values'])]
  assert orders==sorted(tuple(o) for o in x['suffix_orders'])
  assert abs(score-x['discovery_score'])<1e-6
 selected=min(row['completions'],key=lambda x:(-x['discovery_score'],tuple(x['suffix_values']))) if found else None
 assert selected==row['selected']
 truth=read(OLD/f'confirmation/world_{world}_truth.json.gz')['decode_map']
 active={c for w in words for c in w}
 expected=[]
 for x in row['completions']:
  k=copy.deepcopy(key)
  for c,v in zip(S,x['suffix_values']):k[c]['output']=v
  expected.append(dict(suffix_values=x['suffix_values'],active_mismatch_ids=[c for c in sorted(active) if k[c]!=truth[c]]))
 assert result['completion_truth']==expected
 assert result['exact_active_completions']==sum(not v['active_mismatch_ids'] for v in expected)
 assert result['compatible_assignments']==len(found)
 assert result['was_original_selected']==(fit==read(OLD/f'artifacts/fits/world_{world}_{fit["arm"]}_selected.json'))
 if selected:
  k=copy.deepcopy(key)
  for c,v in zip(S,selected['suffix_values']):k[c]['output']=v
  held=read(OLD/f'prepared/world_{world}_held.json.gz')
  hwords=Counter(tuple(w) for p in held['paragraphs'] for w in p['words'])
  orders=direct_orders(hwords,k)
  joint=sorted(set(orders)&{tuple(o) for o in selected['suffix_orders']})
  v=result['selection'];assert joint==sorted(tuple(o) for o in v['joint_suffix_orders'])
  assert bool(orders)==v['held_gate']['compatible']
  # Independent gold check uses planted encoding emissions per held atom;
  # source truth linkage is additionally checked without using runner metrics.
  gold=[p for p in read(OLD/'confirmation/source_truth.json.gz')['paragraphs'] if p['split']=='held']
  exact=sentences=total=0
  assert len(gold)==len(held['paragraphs'])
  for p,g in zip(held['paragraphs'],gold):
   original=[''.join(truth[c]['output'] for c in w) for w in p['words']]
   assert original==g['words'] and p['paragraph_id']==g['paragraph_id']
   predictions=[''.join(k[c]['output'] for c in w) for w in p['words']]
   exact+=sum(a==b for a,b in zip(predictions,original));sentences+=predictions==original;total+=len(original)
  assert (exact,sentences,total)==(v['held_exact_words'],v['held_exact_sentences'],v['held_words'])
  mismatch=[c for c in sorted(active) if k[c]!=truth[c]]
  assert mismatch==v['active_mismatch_ids'] and v['full_active_recovery']==(not mismatch)
 else:assert result['selection'] is None
 return dict(fit=row['fit'],compatible_assignments=len(found),conditional_selected=selected is not None)

def main():
 for n,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/n)==h,n
 lock=read(OLD/'artifacts/FIT_LOCK.json')
 for n,h in lock['sha256'].items():assert sha(OLD/n)==h
 dl=read(E/'artifacts/DISCOVERY_LOCK.json');assert dl['discovery_sha256']==sha(E/'artifacts/DISCOVERY.json')
 assert dl['prereg_sha256']==sha(E/'PREREG_LOCK.json')
 d=read(E/'artifacts/DISCOVERY.json');result=read(E/'artifacts/RESULT.json')
 assert [r['fit'] for r in d['rows']]==lock['restarts'] and len(d['rows'])==48
 assert [r['fit'] for r in result['rows']]==lock['restarts']
 with ProcessPoolExecutor(max_workers=16) as p:checks=list(p.map(check_one,zip(d['rows'],result['rows'])))
 assert result['old_compatible']==sum(r['original_gate']['compatible'] for r in d['rows'])
 assert result['completable']==sum(r['conditional_selected'] for r in checks)
 assert result['selected_exact_active']==sum(bool(r['selection'] and r['selection']['full_active_recovery']) for r in result['rows'])
 assert result['original_six_selected_exact']==sum(bool(r['was_original_selected'] and r['selection'] and r['selection']['full_active_recovery']) for r in result['rows'])
 out=dict(status='PASS',scope='Independent direct forward enumeration, original sentence scoring, locked selections, truth and held consequences',
          rows=48,nominal_assignments=48*11880,compatible_assignments=sum(r['compatible_assignments'] for r in checks),
          result_sha256=sha(E/'artifacts/RESULT.json'),discovery_sha256=sha(E/'artifacts/DISCOVERY.json'),same_author=True,semantic_independence=False)
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
