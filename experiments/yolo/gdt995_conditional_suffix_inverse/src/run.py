#!/usr/bin/env python3
"""Finite conditional audit; no role/literal/wholeword fitting."""
import argparse, copy, datetime, gzip, hashlib, importlib.util, itertools, json, math
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
E=Path(__file__).resolve().parents[1]; R=E.parents[2]
OLD=R/'experiments/yolo/gdt837_scg_integrated_wholeword_control'
MODEL_SRC=R/'experiments/yolo/gdt832_joint_family_context_control/src/reference_model.py'
def read(p):
 p=Path(p); b=p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify():
 for n,h in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/n)==h,n
 lock=read(OLD/'artifacts/FIT_LOCK.json')
 for n,h in lock['sha256'].items():assert sha(OLD/n)==h,n
 return lock

def projection(cipher):
 words=Counter(); transitions=Counter(); first=Counter()
 for p in cipher['paragraphs']:
  seq=[tuple(w) for w in p['words']];words.update(seq)
  if seq:first[seq[0]]+=1
  transitions.update(zip(seq,seq[1:]))
 return words,transitions,first

def encode_summary(words,key):
 """Constraint implementation; a single global suffix order must exist."""
 S=sorted(c for c,v in key.items() if v['role']=='S')
 W={v['output']:c for c,v in key.items() if v['role']=='W'}
 edges=set();counts=Counter(); witnesses={}
 for codes,n in sorted(words.items()):
  text=''.join(key[c]['output'] for c in codes)
  roles=[key[c]['role'] for c in codes];reason=None
  applicable=[c for c in S if text.endswith(key[c]['output']) and len(text)-len(key[c]['output'])>=3]
  if text in W:
   if codes!=(W[text],):reason='WHOLEWORD_PRIORITY'
  elif roles==['W']:reason='INVALID_W'
  elif roles[-1:] == ['S'] and all(x=='L' for x in roles[:-1]) and len(codes)>=4:
   actual=codes[-1]
   if actual not in applicable:reason='SUFFIX_STEM'
   else:edges.update((actual,other) for other in applicable if other!=actual)
  elif all(x=='L' for x in roles):
   if applicable:reason='MANDATORY_SUFFIX'
  else:reason='ROLE_POSITION'
  if reason:
   counts[reason]+=n
   witnesses.setdefault(reason,dict(codes=list(codes),decoded=text,occurrences=n))
 orders=[list(p) for p in itertools.permutations(S) if all(p.index(a)<p.index(b) for a,b in edges)]
 if not orders:counts['NO_GLOBAL_SUFFIX_ORDER']=1
 return dict(compatible=not counts,violations=dict(counts),first_lexicographic_witnesses=witnesses,
             suffix_orders=orders if not counts else [],precedence_edges=[list(e) for e in sorted(edges)])

def suffix_domains(words,key,pool):
 W={v['output'] for v in key.values() if v['role']=='W'}
 blocked={}
 for codes,n in sorted(words.items()):
  if not all(key[c]['role']=='L' for c in codes):continue
  text=''.join(key[c]['output'] for c in codes)
  if text in W:continue # W contradiction is checked by the complete gate.
  for s in pool:
   if text.endswith(s) and len(text)-len(s)>=3:
    blocked.setdefault(s,dict(codes=list(codes),decoded=text,occurrences=n))
 return [s for s in pool if s not in blocked],blocked

def scored(proj,key,model):
 words,transitions,first=proj
 text={c:''.join(key[a]['output'] for a in c) for c in words}
 return math.fsum([n*model.log_conditional(None,text[c]) for c,n in first.items()]+
                  [n*model.log_conditional(text[a],text[b]) for (a,b),n in transitions.items()])

def model_load():
 return load(MODEL_SRC,'frozen_model').load_model(E/'runtime/reference')

def one_fit(relative):
 fit=read(OLD/relative);key=fit['key'];world=fit['world_id']
 cipher=read(OLD/f'prepared/world_{world}_discovery.json.gz')
 assert cipher['split']=='discovery'
 proj=projection(cipher);words=proj[0];pool=read(OLD/'prepared/candidates.json')['suffix_pool']
 assert len(pool)==12 and len(set(pool))==12
 S=sorted(c for c,v in key.items() if v['role']=='S');assert len(S)==4
 allowed,blocked=suffix_domains(words,key,pool);model=model_load(); completions=[]; tested=0
 for values in itertools.permutations(allowed,4):
  tested+=1;k=copy.deepcopy(key)
  for c,v in zip(S,values):k[c]['output']=v
  gate=encode_summary(words,k)
  if gate['compatible']:
   completions.append(dict(suffix_values=list(values),suffix_orders=gate['suffix_orders'],discovery_score=scored(proj,k,model)))
 completions.sort(key=lambda x:tuple(x['suffix_values']))
 selected=min(completions,key=lambda x:(-x['discovery_score'],tuple(x['suffix_values']))) if completions else None
 row=dict(fit=relative,world_id=world,arm=fit['arm'],start=fit['start'],suffix_carriers=S,
          original_gate=encode_summary(words,key),original_score=scored(proj,key,model),
          original_saved_score=fit['discovery_objective']['total_nats'],
          literal_excluded_values=blocked,remaining_value_pool=allowed,nominal_assignments=11880,
          rejected_by_literal_gate=11880-tested,full_gate_assignments=tested,
          compatible_assignments=len(completions),completions=completions,selected=selected,
          discovery_words=sum(words.values()),discovery_types=len(words))
 assert abs(row['original_score']-row['original_saved_score'])<1e-4
 return row

def audit(workers):
 lock=verify();assert not (E/'artifacts/DISCOVERY_LOCK.json').exists()
 mod=load(MODEL_SRC,'builder');(E/'runtime').mkdir(exist_ok=True)
 mod.build(OLD/'prepared/reference.jsonl',OLD/'prepared/families.json',E/'runtime/reference')
 started=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with ProcessPoolExecutor(max_workers=min(workers,32)) as pool:rows=list(pool.map(one_fit,lock['restarts']))
 assert len(rows)==48
 out=dict(schema='GDT995_DISCOVERY_V1',started_utc=started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          nominal_assignments=48*11880,rows=rows,truth_or_held_read=False)
 emit(E/'artifacts/DISCOVERY.json',out)
 emit(E/'artifacts/DISCOVERY_LOCK.json',dict(discovery_sha256=sha(E/'artifacts/DISCOVERY.json'),prereg_sha256=sha(E/'PREREG_LOCK.json')))
 print(json.dumps(dict(status='DISCOVERY_LOCKED',old_compatible=sum(r['original_gate']['compatible'] for r in rows),
                      completable=sum(bool(r['completions']) for r in rows),completions=sum(r['compatible_assignments'] for r in rows))))

def evaluate():
 lock=verify();dl=read(E/'artifacts/DISCOVERY_LOCK.json')
 assert dl['discovery_sha256']==sha(E/'artifacts/DISCOVERY.json') and dl['prereg_sha256']==sha(E/'PREREG_LOCK.json')
 assert not (E/'artifacts/RESULT.json').exists()
 source=read(OLD/'confirmation/source_truth.json.gz');gold=[p for p in source['paragraphs'] if p['split']=='held']
 rows=[]
 for row in read(E/'artifacts/DISCOVERY.json')['rows']:
  old=read(OLD/row['fit']);key=old['key'];w=row['world_id']
  truth=read(OLD/f'confirmation/world_{w}_truth.json.gz')['decode_map']
  discovery=read(OLD/f'prepared/world_{w}_discovery.json.gz');held=read(OLD/f'prepared/world_{w}_held.json.gz')
  active={c for p in discovery['paragraphs'] for word in p['words'] for c in word}
  truths=[]
  for completion in row['completions']:
   k=copy.deepcopy(key)
   for c,v in zip(row['suffix_carriers'],completion['suffix_values']):k[c]['output']=v
   bad=[c for c in sorted(active) if k[c]!=truth[c]]
   truths.append(dict(suffix_values=completion['suffix_values'],active_mismatch_ids=bad))
  selected=row['selected'];out=dict(fit=row['fit'],world_id=w,arm=row['arm'],start=row['start'],
        was_original_selected=old==read(OLD/f'artifacts/fits/world_{w}_{row["arm"]}_selected.json'),
        original_compatible=row['original_gate']['compatible'],compatible_assignments=len(truths),
        exact_active_completions=sum(not x['active_mismatch_ids'] for x in truths),completion_truth=truths,selection=None)
  if selected:
   k=copy.deepcopy(key)
   for c,v in zip(row['suffix_carriers'],selected['suffix_values']):k[c]['output']=v
   bad=[c for c in sorted(active) if k[c]!=truth[c]]
   total=exact=sentences=0
   assert len(held['paragraphs'])==len(gold)
   for p,g in zip(held['paragraphs'],gold):
    assert p['paragraph_id']==g['paragraph_id'] and len(p['words'])==len(g['words'])
    pred=[''.join(k[c]['output'] for c in word) for word in p['words']]
    total+=len(pred);exact+=sum(a==b for a,b in zip(pred,g['words']));sentences+=pred==g['words']
   gate=encode_summary(projection(held)[0],k)
   common=[o for o in selected['suffix_orders'] if o in gate['suffix_orders']]
   out['selection']=dict(suffix_values=selected['suffix_values'],active_packages=len(active),active_mismatch_ids=bad,
        held_words=total,held_exact_words=exact,held_exact_sentences=sentences,held_sentences=len(gold),
        held_gate=gate,joint_suffix_orders=common,full_active_recovery=not bad,
        discovery_score=selected['discovery_score'],score_gain=selected['discovery_score']-row['original_score'])
  rows.append(out)
 result=dict(schema='GDT995_RESULT_V1',status='RETROSPECTIVE_CONDITIONAL_AUDIT_COMPLETE',discovery_lock_sha256=sha(E/'artifacts/DISCOVERY_LOCK.json'),
       rows=rows,old_compatible=sum(r['original_compatible'] for r in rows),
       completable=sum(r['selection'] is not None for r in rows),
       selected_exact_active=sum(bool(r['selection'] and r['selection']['full_active_recovery']) for r in rows),
       original_six_selected_exact=sum(bool(r['was_original_selected'] and r['selection'] and r['selection']['full_active_recovery']) for r in rows),
       original_GDT837_status='STRICT_RECOVERY_FAIL',new_full_key_fits=0,confirmed_words=0,independent_corpora=1,
       claim_ceiling='Retrospective conditional known-encoder audit; no fresh blind recovery or Voynich meaning')
 emit(E/'artifacts/RESULT.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['audit','evaluate']);p.add_argument('--workers',type=int,default=16);a=p.parse_args()
 audit(a.workers) if a.phase=='audit' else evaluate()
