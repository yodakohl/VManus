#!/usr/bin/env python3
"""Fit first. Held bodies require a separate --evaluate invocation."""
import argparse,hashlib,json,re,time
from collections import Counter
from pathlib import Path
from fit import fit_panel,canonical
from prepare import prepare,CACHE,EDITIONS,E,ROOT

def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value,check=False):
 p=E/'artifacts'/name;text=canonical(value)+'\n'
 if check:assert p.read_text()==text,name
 else:p.write_text(text)
def locked():
 for name,digest in read(E/'src/PREREG_LOCK.json').items():assert sha(ROOT/name)==digest,name

def source_counts(role):
 source=read(E/'src/SOURCE.json')
 names={r:re.findall('[a-z]+',head.lower()) for r,head in source['headwords'].items()}
 patterns=sorted(names.items(),key=lambda x:(-len(x[1]),x[0]))
 words=re.findall('[a-z]+',source['entries'][role]['body'].lower());counts=Counter();i=0
 while i<len(words):
  for target,pattern in patterns:
   if words[i:i+len(pattern)]==pattern:counts[target]+=1;i+=len(pattern);break
  else:i+=1
 return {r:counts[r] for r in source['node_order']}

def predictions(result,fit_input):
 out={};counts=None
 for ed,panel in result['panels'].items():
  if not panel['complete'] or len(panel['lexicons'])!=1:continue
  if counts is None:counts=source_counts('S')
  lexicon=panel['lexicons'][0]
  ids=sorted(h['paragraph_id'] for h in fit_input['panels'][ed]['held_heads'] if h['head']==lexicon['head_forms']['S'])
  assert ids and all(s['held_head_paragraphs']==ids for s in panel['solutions'])
  out[ed]=dict(lexicon=lexicon,expected_counts=counts,paragraph_ids=ids)
 return dict(experiment_id='GDT888',panels=out,ceiling='Frozen conditional predictions; no held bodies used in fitting.')

def initial_evaluations(result):
 out={}
 for ed,p in result['panels'].items():
  status='INCOMPLETE_FIT' if not p['complete'] else 'NO_TRAINING_SOLUTION' if not p['lexicons'] else 'NONUNIQUE_TRAINING_LEXICON' if len(p['lexicons'])>1 else 'WAITING_HELD_RELEASE'
  out[ed]=dict(status=status)
 return out

def evaluate(result,predicted,fit_input):
 assert predicted==predictions(result,fit_input)
 out=initial_evaluations(result)
 if not predicted['panels']:return out
 cached=read(ROOT/CACHE);idx={f['paragraph_id']:f for f in cached['frames']}
 for ed,p in predicted['panels'].items():
  forms={r:tuple(v) for r,v in p['lexicon']['mention_forms'].items()};inverse={v:r for r,v in forms.items()}
  assert len(inverse)==6;observations=[]
  for pid in p['paragraph_ids']:
   f=idx[pid];r=f['readings'][ed]
   assert int(f['physical_folio'][1:])%2==0 and r['eligible'] and r['groups'][0]['sta']==p['lexicon']['head_forms']['S']
   counts=Counter();matched=[]
   for group in r['groups'][1:]:
    role=inverse.get(tuple(group['sta']))
    if role is not None:counts[role]+=1;matched.append(dict(role=role,source_group_id=group['source_group_id'],locus=group['locus'],raw=group['raw'],sta=group['sta']))
   actual={role:counts[role] for role in forms}
   observations.append(dict(paragraph_id=pid,page=f['page'],physical_folio=f['physical_folio'],observed_counts=actual,expected_counts=p['expected_counts'],passed=actual==p['expected_counts'],matched_groups=matched))
  out[ed]=dict(status='HELD_ALL_PASS' if all(x['passed'] for x in observations) else 'HELD_FAILURE',observations=observations,held_leaves=sorted({x['physical_folio'] for x in observations}),score_ready=False)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--evaluate',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args();locked()
 if a.evaluate:
  result=read(E/'artifacts/RESULT.json');fit_input=read(E/'artifacts/FIT_INPUT.json');predicted=read(E/'artifacts/PREDICTIONS.json')
  assert fit_input==prepare(),'blinded input drift'
  result['evaluations']=evaluate(result,predicted,fit_input);result['phase']='EVALUATED'
  write('RESULT.json',result,a.check)
 else:
  fit_input=prepare();template=read(E/'src/FIT_TEMPLATE.json');deadline=time.monotonic()+1200
  panels={ed:fit_panel(fit_input['panels'][ed],template,deadline) for ed in EDITIONS}
  result=dict(experiment_id='GDT888',phase='FIT_ONLY',panels=panels,complete=all(p['complete'] for p in panels.values()))
  result['evaluations']=initial_evaluations(result);predicted=predictions(result,fit_input)
  write('FIT_INPUT.json',fit_input,a.check);write('PREDICTIONS.json',predicted,a.check);write('RESULT.json',result,a.check)
 print(json.dumps(dict(phase=result['phase'],complete=result['complete'],panels={ed:dict(solutions=len(p['solutions']),lexicons=len(p['lexicons']),complete=p['complete'],evaluation=result['evaluations'][ed]['status']) for ed,p in result['panels'].items()}),sort_keys=True))
if __name__=='__main__':main()
