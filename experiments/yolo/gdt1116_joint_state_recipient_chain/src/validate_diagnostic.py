"""Validate diagnostic rows without importing the diagnostic implementation."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parents[1]
def j(p):return json.loads((H/p).read_text())
def main():
 d=j('src/POST_READER_DIAGNOSTIC.json');m=j('src/MODEL.json');got=j('artifacts/POST_READER_DIAGNOSTIC.json');want=[]
 for p,key in [('src/SOURCE.json','source_sha256'),('src/MODEL.json','model_sha256')]:assert hashlib.sha256((H/p).read_bytes()).hexdigest()==d[key]
 for unit in j('src/SOURCE.json')['units']:
  sequence=[{'raw':w,'id':sid} for line in unit['lines'] for w,sid in zip(line['words'],line['source_ids'])]
  for index,target in enumerate(sequence):
   if target['raw']!='chedy':continue
   left=sequence[index-1] if index else None
   if left and left['raw']=='dal':continue
   for candidate,model in m['candidates'].items():
    typ=d['candidate_types'][candidate].get(left['raw']) if left else None
    if typ is not None:
     label=d['outcomes']['typed_matching'] if typ in d['property_domain'][candidate] else d['outcomes']['typed_nonmatching']
    elif left and left['raw'] in model['dictionary']:label=d['outcomes']['known_non_nominal']
    else:label=d['outcomes']['unknown']
    want.append({'candidate':candidate,'edition':unit['edition'],'paragraph':unit['id'],'positive_id':target['id'],'head_id':left['id'] if left else None,'head_raw':left['raw'] if left else None,'assumed_head_type':typ,'assumed_property':model['joint_positive'],'result':label})
 assert got['cases']==want
 for candidate in m['candidates']:
  assert got['contradiction_loci'][candidate]==sorted({r['positive_id'].split('|')[1] for r in want if r['candidate']==candidate and r['result']==d['outcomes']['typed_nonmatching']})
  for edition in m['editions']:
   assert got['summaries'][candidate][edition]=={label:sum(r['candidate']==candidate and r['edition']==edition and r['result']==label for r in want) for label in d['outcomes'].values()}
 out={'status':'PASS','rows':len(want),'scope':'Frozen diagnostic source/model hashes and every exact-positive/direct-head classification; no property, noun identity or attachment confirmation','semantic_validation':False};(H/'artifacts/DIAGNOSTIC_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
