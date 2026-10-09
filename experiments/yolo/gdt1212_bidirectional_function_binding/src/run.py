#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import hashlib,json
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
RAW='research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_BIDIRECTIONAL_FUNCTION_BINDING_RAW_20261005.json'
SOURCE='experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET='experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def save(name,x):(A/(name+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def partition(words,right,left):
 out=[];pending=[];state='E'
 for word in words:
  cls='X' if not word.isalpha() else 'R' if word in right else 'L' if word in left else 'H'
  if cls=='X':
   if state!='R' and pending:out.append(pending);pending=[]
   out.append(pending+[word]);pending=[];state='E'
  elif cls=='R':
   if state!='R' and pending:out.append(pending);pending=[]
   pending.append(word);state='R'
  elif cls=='L':
   if state=='R':out.append(pending);pending=[]
   pending.append(word);state='H' if state=='H' else 'L'
  else:
   if state!='R' and pending:out.append(pending);pending=[]
   pending.append(word);state='H'
 if pending:out.append(pending)
 return out

def main():
 started=datetime.now(timezone.utc).isoformat()
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for rel,h in lock['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
 raw=json.loads((ROOT/RAW).read_text());design=raw['design']
 right={w for k in ('CONJ','ARTICLE','PREP') for w in design['right_list'][k]};left=set(design['left_list']['words'])
 assert len(right)==44 and len(left)==7 and not right&left
 for ex in raw['invented_demonstrations']:assert partition(ex['source'].split(),right,left)==ex['groups']
 sources=json.loads((ROOT/SOURCE).read_text());targets=json.loads((ROOT/TARGET).read_text())['targets']
 result={'experiment':'GDT1212','sample_groups':8000,'source_scope':{},'metrics':{},'comparison':[],'roundtrip':True};receipts={}
 for book in ('b4','w1','bs1','gr1'):
  groups=[];receipts[book]=[];word_count=0
  for recipe in sources[book]:
   words=recipe['words'];out=partition(words,right,left)
   assert [w for g in out for w in g]==words
   receipts[book].append({'id':recipe['id'],'words':len(words),'groups':len(out),'sha256':digest(out)})
   word_count+=len(words);groups.extend(tuple(g) for g in out)
  sample=groups[:8000];assert len(sample)==8000,book
  c=Counter(sample);head=sum(sorted(c.values(),reverse=True)[:10])
  result['source_scope'][book]={'recipes':len(sources[book]),'words':word_count,'groups':len(groups)}
  result['metrics'][book]={'types':len(c),'type_ratio':len(c)/8000,'top10_count':head,'top10_share':head/8000,'sample_sha256':digest(sample)}
  for ed,t in targets.items():
   for metric,observed,ref in [('types',len(c),t['types']),('top10_count',head,round(t['top10_share']*8000))]:
    result['comparison'].append({'book':book,'reader':ed,'metric':metric,'source':observed,'target':ref,'absolute_difference':abs(observed-ref),'within':abs(observed-ref)<=400})
 result['all_necessary_conditions']=all(r['within'] for r in result['comparison'])
 result['status']='BIDIRECTIONAL_GROUPING_NOT_EXCLUDED' if result['all_necessary_conditions'] else 'BIDIRECTIONAL_GROUPING_FREQUENCY_FAIL'
 result['claim_ceiling']='Necessary tuple-identity frequencies on fixed exposed sources only; no physical carrier, historical attestation, native meanings or independent confirmation.'
 save('GROUP_RECEIPTS',receipts);save('RESULT',result)
 save('RUN_RECEIPT',{'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'registration_lock_sha256':hashlib.sha256((A/'REGISTRATION_LOCK.json').read_bytes()).hexdigest()})
 print(json.dumps({'status':result['status'],'metrics':result['metrics'],'failed':[r for r in result['comparison'] if not r['within']]},indent=2))
if __name__=='__main__':main()
