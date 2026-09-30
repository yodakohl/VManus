"""Render two explicitly partial C0 constructions; no decoder/semantic scorer."""
import json,hashlib,csv
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2]
def put(name,value):
 (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
 m=json.loads((HERE/'src/MODEL.json').read_text())
 for p,h in m['input_hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 cache=json.loads((ROOT/m['source']).read_text());assert not cache['RF1b']
 units=[]
 for e in m['editions']:
  for u in cache[e]:
   if any(l['locus'] in m['selection_loci'] for l in u['lines']):
    assert not u['page'].startswith('f84') and u['page']!='f116v'
    units.append({'edition':e,**u})
 assert len(units)==6
 put('src/SOURCE.json',{'units':units,'scope':'complete native paragraphs for the three selected loci; previously exposed','denominators':{e:len(cache[e]) for e in m['editions']},'RF_native_capacity':0})
 rows=[];graphs=[];reader=['# Complete raw paragraphs and partial constant C0 alternatives','All clauses and lexical values are assumptions; UNKNOWN is not a contradiction.']
 for u in units:
  reader+=['\n## '+u['edition']+' '+u['id']]
  for line in u['lines']:
   assert len(line['words'])==len(line['source_ids'])
   reader+=['\n'+line['locus']+' RAW: `'+ ' '.join(line['words'])+'`']
   for name,c in m['candidates'].items():
    vals=[c['dictionary'].get(w,'⟦'+w+'⟧') for w in line['words']]
    reader+=[name+': '+' '.join(vals)]
    for pos,(w,sid,v) in enumerate(zip(line['words'],line['source_ids'],vals),1):
     rows.append({'candidate':name,'edition':u['edition'],'paragraph':u['id'],'locus':line['locus'],'position':pos,'source_id':sid,'raw':w,'rendering':v,'assigned':w in c['dictionary']})
    if line['locus']==m['focal']:
     assert len(line['words'])==8
     graph={'candidate':name,'edition':u['edition'],'locus':line['locus'],'status':'ASSUMED_GRAPH_WITH_UNREAD_RESULT_AND_TAIL','raw':line['words'],'source_ids':line['source_ids'],'clauses':[[line['source_ids'][p-1] for p in cl] for cl in c['clauses']],'descent_subject':line['source_ids'][0],'change_subject':line['source_ids'][c['assumed_subjects']['change']-1],'result':{'source_id':line['source_ids'][4],'raw':line['words'][4],'meaning':'UNREAD'},'flow_carrier':'UNCONFIRMED_RESULT_AT_'+line['source_ids'][4],'qotain_role':c['qotain_role'],'qotain_bearer':line['source_ids'][0] if name=='AMT' else None,'MAT_DS_Q_identity':'UNBOUND' if name=='MAT' else 'NOT_APPLICABLE','unread_tail':list(zip(line['source_ids'][6:],line['words'][6:])),'independently_bound':False,'c0_reading':c['focal_c0'].replace('RESULT',line['words'][4]).replace('K O',' '.join(line['words'][6:]))}
     graphs.append(graph);reader+=['C0 clause sketch: '+graph['c0_reading']]
 put('artifacts/ALIGNMENT.json',rows);put('artifacts/GRAPHS.json',graphs)
 (HERE/'artifacts/FULL_READER.md').write_text('\n\n'.join(reader)+'\n')
 edge=[]
 for u in units:
  flat=[{'source_id':sid,'raw':w,'locus':l['locus']} for l in u['lines'] for w,sid in zip(l['words'],l['source_ids'])]
  for i,r in enumerate(flat):
   if r['raw']=='chedy':edge.append({'edition':u['edition'],'paragraph':u['id'],'target':r,'position':i+1,'paragraph_groups':len(flat),'right_groups':len(flat)-i-1,'outcome':'RIGHT_WRITTEN_COMPLEMENT_ABSENT' if i==len(flat)-1 else 'RAW_CAPACITY_ONLY_MEANING_UNBOUND'})
 put('artifacts/RIGHT_RESULT_DIAGNOSTIC.json',{'contract':json.loads((HERE/'src/DIAGNOSTIC.json').read_text()),'cases':edge,'counts':{e:{'chedy':sum(c['edition']==e for c in edge),'no_right_result':sum(c['edition']==e and c['right_groups']==0 for c in edge)} for e in m['editions']}})
 summary={}
 for name in m['candidates']:
  summary[name]={e:{'groups':sum(r['candidate']==name and r['edition']==e for r in rows),'assigned':sum(r['candidate']==name and r['edition']==e and r['assigned'] for r in rows),'unread':sum(r['candidate']==name and r['edition']==e and not r['assigned'] for r in rows)} for e in m['editions']}
 result={'decision':'EXPLORATORY_UNRANKED__RIGHT_RESULT_RULE_COUNTER','native_paragraphs':len(units),'unique_source_groups':sum(len(l['words']) for u in units for l in u['lines']),'alignment_rows':len(rows),'focal_graphs':len(graphs),'coverage':summary,'physical_leaves':[77,82,115],'confirmed_words':0,'independent_meaning_confirmation_capacity':0,'RF_native_capacity':0,'fixed_meaning_test_performed':False,'significance':False,'unresolved':['quantity-manner versus material-subject attachment','physical identity DS versus Q inMAT','result at fifth raw group','qokol olchey tail attachment/meaning','liquid/descent/change/flow meanings and clause boundaries themselves']}
 put('artifacts/RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
