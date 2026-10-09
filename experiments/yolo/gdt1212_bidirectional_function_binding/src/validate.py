#!/usr/bin/env python3
"""Separate regex grouping; no runner import."""
from pathlib import Path
from itertools import product
from datetime import datetime,timezone
import hashlib,json,re,unicodedata
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def read(rel):return json.loads((ROOT/rel).read_text())
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def partition(words,right,left):
 classes=''.join('X' if any(not unicodedata.category(c).startswith('L') for c in w) else 'R' if w in right else 'L' if w in left else 'H' for w in words)
 spans=[m.span() for m in re.finditer(r'R*(?:HL*|X)|R+|L+',classes)]
 assert ''.join(classes[a:b] for a,b in spans)==classes
 return [words[a:b] for a,b in spans]
def declared(classes,table):
 state='E';pending=[];out=[]
 for cls in classes:
  for action in table[state][cls].split('; '):
   if action.startswith('emit singleton'):out.append([cls])
   elif action.startswith('emit'):
    assert pending
    out.append(pending);pending=[]
   elif action.startswith('start'):
    assert not pending
    pending=[cls]
   elif action.startswith('append'):
    assert pending
    pending.append(cls)
   elif action.startswith('state '):state=action[-1]
   else:raise AssertionError(action)
 if pending:out.append(pending)
 return out

def main():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for rel,h in lock['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
 raw=read('research_registry/proposals/production_origin_supply_20261003/HUMAN_SOURCE_BIDIRECTIONAL_FUNCTION_BINDING_RAW_20261005.json');d=raw['design']
 right={w for k in ('CONJ','ARTICLE','PREP') for w in d['right_list'][k]};left=set(d['left_list']['words'])
 old=read('experiments/yolo/gdt1177_preposition_binding_transfer/src/SPEC.json')
 assert right=={w for k in ('CONJ','ARTICLE','PREP') for w in old['sets'][k]}
 assert left=={'so','du','es','da','dan','dann','denn'}
 checked=0
 for n in range(9):
  for seq in product('RLHX',repeat=n):
   classes=''.join(seq);expected=[list(m.group()) for m in re.finditer(r'R*(?:HL*|X)|R+|L+',classes)]
   assert declared(seq,d['complete_transition_table'])==expected
   assert [c for g in expected for c in g]==list(seq)
   checked+=1
 for demo in raw['invented_demonstrations']:assert partition(demo['source'].split(),right,left)==demo['groups']
 sources=read('experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json')
 targets=read('experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json')['targets']
 result=json.loads((A/'RESULT.json').read_text());saved=json.loads((A/'GROUP_RECEIPTS.json').read_text())
 rows=[];recipes=0;tokens=0
 for book in ('b4','w1','bs1','gr1'):
  groups=[];receipts=[];word_count=0
  for recipe in sources[book]:
   words=recipe['words'];gs=partition(words,right,left)
   assert [w for g in gs for w in g]==words
   receipts.append({'id':recipe['id'],'words':len(words),'groups':len(gs),'sha256':digest(gs)})
   groups.extend(gs);word_count+=len(words)
  assert receipts==saved[book]
  assert result['source_scope'][book]=={'recipes':len(sources[book]),'words':word_count,'groups':len(groups)}
  sample=groups[:8000];assert len(sample)==8000
  freqs={}
  for g in sample:
   key=tuple(g);freqs[key]=freqs.get(key,0)+1
  head=sum(sorted(freqs.values())[-10:])
  assert result['metrics'][book]=={'types':len(freqs),'type_ratio':len(freqs)/8000,'top10_count':head,'top10_share':head/8000,'sample_sha256':digest(sample)}
  for ed,t in targets.items():
   for metric,observed,ref in [('types',len(freqs),t['types']),('top10_count',head,round(t['top10_share']*8000))]:
    rows.append({'book':book,'reader':ed,'metric':metric,'source':observed,'target':ref,'absolute_difference':abs(observed-ref),'within':ref-400<=observed<=ref+400})
  recipes+=len(sources[book]);tokens+=word_count
 assert result['comparison']==rows and len(rows)==24
 passed=all(r['within'] for r in rows)
 assert result['all_necessary_conditions']==passed
 assert result['status']==('BIDIRECTIONAL_GROUPING_NOT_EXCLUDED' if passed else 'BIDIRECTIONAL_GROUPING_FREQUENCY_FAIL')
 out={'status':'PASS','same_author':True,'runner_imported':False,'method':'Independent regex grouping; raw transition interpreter on all class sequences0..8; complete source/group hash and count replay','class_sequences':checked,'invented_examples':len(raw['invented_demonstrations']),'complete_recipes':recipes,'source_words':tokens,'conditions':24,'ceiling':'Accounting and implementation only; no independent science, human usability, native grammar or translation.','completed_utc':datetime.now(timezone.utc).isoformat()}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
