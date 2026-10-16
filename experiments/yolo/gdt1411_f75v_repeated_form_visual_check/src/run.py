#!/usr/bin/env python3
"""Account for frozen qualitative judgments; never validate visual truth."""
import hashlib,itertools,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
CLAIM='Qualitative informedAIjudgments ofoneownedphotograph; accountingPASSdoesnotvalidateperception, phonemes, semanticwordboundaries ormeaning.'
J=('SIMILAR_SEQUENCE','CLEAR_DIFFERENCE','UNRESOLVED');S=('SPACE_LIKE','INTERNAL_LIKE','UNRESOLVED')
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def decide(a,b,seams=None):
 assert a in J and b in J
 if 'CLEAR_DIFFERENCE' in (a,b):return 'PREMISE_REVIEW_REQUIRED'
 if a==b=='SIMILAR_SEQUENCE' and (seams is None or seams==('SPACE_LIKE','SPACE_LIKE')):return 'LOCAL_GRAPHIC_REPEAT_SUPPORTED'
 return 'UNRESOLVED'
def controls():
 n=0
 for a,b in itertools.product(J,repeat=2):
  actual=decide(a,b)
  expected='PREMISE_REVIEW_REQUIRED' if a=='CLEAR_DIFFERENCE' or b=='CLEAR_DIFFERENCE' else ('LOCAL_GRAPHIC_REPEAT_SUPPORTED' if a==b=='SIMILAR_SEQUENCE' else 'UNRESOLVED')
  assert actual==expected;n+=1
  for x,y in itertools.product(S,repeat=2):
   actual=decide(a,b,(x,y))
   expected='PREMISE_REVIEW_REQUIRED' if a=='CLEAR_DIFFERENCE' or b=='CLEAR_DIFFERENCE' else ('LOCAL_GRAPHIC_REPEAT_SUPPORTED' if a==b=='SIMILAR_SEQUENCE' and x==y=='SPACE_LIKE' else 'UNRESOLVED')
   assert actual==expected;n+=1
 return {'status':'PASS_DECISION_ACCOUNTING_CONTROLS','finite_combinations':n,'scope':'Fixed judgment combination only; not a visual control or perceptual accuracy.'}
def run():
 lock=read(E/'CODE_LOCK.json')
 for path,h in lock['files'].items():assert sha(ROOT/path)==h,path
 spec=read(E/'src/SPEC.json');view=read(E/'VIEW_LOCK.json')
 for path,h in view['files'].items():assert sha(ROOT/path)==h,path
 a=read(A/'VIEWER_A.json');b=read(A/'VIEWER_B.json');seal=read(A/'A_SEAL.json')
 assert seal['viewer_a_sha256']==sha(A/'VIEWER_A.json')
 assert a['image_sha256']==b['image_sha256']==spec['source_sha256']==sha(ROOT/spec['source_path'])
 assert a['presentation']['original_image_view_calls']==b['presentation']['views_this_task']==1
 cases=[]
 for index,target in enumerate(spec['comparisons']):
  aa,bb=a['comparisons'][index],b['comparisons'][index]
  for field in ['id','left','right']:assert aa[field]==bb[field]==target[field]
  assert aa['judgment'] in J and bb['judgment'] in J
  seams=None
  if target['id']=='P5':
   assert a['adjacent_separator']['target']==b['adjacent_separator']['target']=='P5'
   seams=(a['adjacent_separator']['judgment'],b['adjacent_separator']['judgment']);assert all(x in S for x in seams)
  cases.append(dict(target,viewer_a=aa['judgment'],viewer_b=bb['judgment'],assessment=decide(aa['judgment'],bb['judgment'],seams)))
 assert len(a['comparisons'])==len(b['comparisons'])==len(cases)==5
 result={'experiment_id':'GDT1411','status':'QUALIFIED_GRAPHIC_REPEAT_CHECK_COMPLETE','pair_results':cases,
         'counts':{name:sum(row['assessment']==name for row in cases) for name in ['LOCAL_GRAPHIC_REPEAT_SUPPORTED','PREMISE_REVIEW_REQUIRED','UNRESOLVED']},
         'p5_separator':{'viewer_a':a['adjacent_separator']['judgment'],'viewer_b':b['adjacent_separator']['judgment']},
         'word_meanings_assigned':0,'claim_ceiling':CLAIM}
 write(A/'CONTROLS.json',controls());write(A/'RESULT.json',result)
 print(json.dumps({'status':result['status'],'counts':result['counts'],'validation_scope':'ACCOUNTING_ONLY_NOT_PERCEPTION'}))
if __name__=='__main__':run()
