"""Exploratory constant C0 sentences and assumed predication graphs only."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parents[1];R=H.parents[2]
def put(p,x):(H/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 m=json.loads((H/'src/MODEL.json').read_text())
 for p,h in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 cache=json.loads((R/m['source']).read_text());assert cache['RF1b']==[]
 units=[{'edition':e,**u} for e in m['editions'] for u in cache[e] if any(l['locus'] in m['selection_loci'] for l in u['lines'])];assert len(units)==4
 assert all(not u['page'].startswith('f84') and u['page']!='f116v' for u in units)
 put('src/SOURCE.json',{'units':units,'exposure':'already exposed admitted native paragraphs','RF_native_capacity':0})
 rows=[];graphs=[];text=['# Complete paragraphs, seven-group hypotheses; all meanings C0']
 for u in units:
  text+=['\n## '+u['edition']+' '+u['id']]
  for l in u['lines']:
   assert len(l['words'])==len(l['source_ids'])
   text+=['\n'+l['locus']+' RAW: `'+ ' '.join(l['words'])+'`']
   for c,model in m['candidates'].items():
    d=model['dictionary'];vals=[d.get(w,'⟦'+w+'⟧') for w in l['words']];text+=[c+': '+' '.join(vals)]
    for n,(w,sid,v) in enumerate(zip(l['words'],l['source_ids'],vals),1):rows.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'position':n,'source_id':sid,'raw':w,'value':v,'assigned':w in d})
    if l['locus']==m['focal']:
     assert len(l['words'])==7
     graphs.append({'candidate':c,'edition':u['edition'],'locus':l['locus'],'raw':l['words'],'source_ids':l['source_ids'],'first_clause':l['source_ids'][:3],'subject':[l['source_ids'][i-1] for i in model['subject_positions']],'written_result':[l['source_ids'][i-1] for i in model['result_positions']],'predicate':l['source_ids'][6],'opening_to_final_physical_identity':'UNBOUND','subject_result_identity':'UNBOUND' if c=='TRANS' else 'SINGLE_QUALIFIED_SUBJECT_ASSUMED','status':'ASSUMED_NOT_INDEPENDENTLY_BOUND','reading':model['focal_c0']});text+=['C0: '+model['focal_c0']]
 put('artifacts/ALIGNMENT.json',rows);put('artifacts/GRAPHS.json',graphs);(H/'artifacts/FULL_READER.md').write_text('\n\n'.join(text)+'\n')
 coverage={c:{e:{'groups':sum(r['candidate']==c and r['edition']==e for r in rows),'assigned':sum(r['candidate']==c and r['edition']==e and r['assigned'] for r in rows),'unread':sum(r['candidate']==c and r['edition']==e and not r['assigned'] for r in rows)} for e in m['editions']} for c in m['candidates']}
 result={'decision':'FULL_FINAL_LINE_C0_FORMATION_ALTERNATIVES_UNRANKED','native_paragraphs':len(units),'source_groups':sum(len(l['words']) for u in units for l in u['lines']),'alignment_rows':len(rows),'focal_graphs':len(graphs),'coverage':coverage,'physical_leaves':[77,115],'confirmed_words':0,'fixed_meaning_test':False,'independent_meaning_confirmation_capacity':0,'significance':False,'unresolved':['All word meanings and clause roles','Formation state versus transformation/result attachment','Opening/final same participant','Physical subject/result identity or subset relation','dalchedy/chedy composition','Most of whole paragraphs unread']};put('artifacts/RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
