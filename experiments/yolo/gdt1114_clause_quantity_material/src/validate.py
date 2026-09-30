"""Independent raw selection/alignment reconstruction. Does not validate meanings."""
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[2]
def read(p):return json.loads((HERE/p).read_text())
def main():
 m=read('src/MODEL.json')
 for p,h in m['input_hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 cache=json.loads((ROOT/m['source']).read_text());assert cache['RF1b']==[]
 expected=[{'edition':e,**u} for e in m['editions'] for u in cache[e] if {l['locus'] for l in u['lines']} & set(m['selection_loci'])]
 assert read('src/SOURCE.json')['units']==expected and len(expected)==6
 rows=read('artifacts/ALIGNMENT.json');want=[]
 for u in expected:
  assert not u['page'].startswith('f84') and u['page']!='f116v'
  for l in u['lines']:
   for c,model in m['candidates'].items():
    for p,(w,sid) in enumerate(zip(l['words'],l['source_ids']),1):
     want.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'position':p,'source_id':sid,'raw':w,'rendering':model['dictionary'].get(w,'⟦'+w+'⟧'),'assigned':w in model['dictionary']})
 assert rows==want
 graphs=read('artifacts/GRAPHS.json');assert len(graphs)==4
 for g in graphs:
  line=next(l for u in expected if u['edition']==g['edition'] for l in u['lines'] if l['locus']=='f77r.36')
  c=m['candidates'][g['candidate']]
  assert g['raw']==line['words'] and g['source_ids']==line['source_ids']
  assert g['change_subject']==line['source_ids'][0 if g['candidate']=='AMT' else 2]
  assert g['clauses']==[[line['source_ids'][i-1] for i in cl] for cl in c['clauses']]
  assert g['qotain_bearer']==(line['source_ids'][0] if g['candidate']=='AMT' else None)
  assert g['result']['raw']==('d[o:a]lchl' if g['edition']=='ZL3b' else 'dolchl')
  assert g['result']['meaning']=='UNREAD' and not g['independently_bound']
  assert g['unread_tail']==[list(v) for v in zip(line['source_ids'][6:],line['words'][6:])]
 result=read('artifacts/RESULT.json');assert result['unique_source_groups']==sum(len(l['words']) for u in expected for l in u['lines'])
 assert result['alignment_rows']==len(rows) and not result['fixed_meaning_test_performed'] and result['confirmed_words']==0
 for c in m['candidates']:
  for e in m['editions']:
   sub=[r for r in rows if r['candidate']==c and r['edition']==e];v=result['coverage'][c][e]
   assert v=={'groups':len(sub),'assigned':sum(r['assigned'] for r in sub),'unread':sum(not r['assigned'] for r in sub)}
 diagnostic=read('artifacts/RIGHT_RESULT_DIAGNOSTIC.json');assert diagnostic['contract']==read('src/DIAGNOSTIC.json')
 expected_edges=[]
 for u in expected:
  flat=[{'source_id':sid,'raw':w,'locus':l['locus']} for l in u['lines'] for w,sid in zip(l['words'],l['source_ids'])]
  for i,r in enumerate(flat):
   if r['raw']=='chedy':expected_edges.append({'edition':u['edition'],'paragraph':u['id'],'target':r,'position':i+1,'paragraph_groups':len(flat),'right_groups':len(flat)-i-1,'outcome':'RIGHT_WRITTEN_COMPLEMENT_ABSENT' if i==len(flat)-1 else 'RAW_CAPACITY_ONLY_MEANING_UNBOUND'})
 assert diagnostic['cases']==expected_edges
 counters=[c for c in expected_edges if c['right_groups']==0]
 assert len(counters)==2 and all(c['target']['locus']=='f115v.10' for c in counters)
 assert diagnostic['counts']=={e:{'chedy':sum(c['edition']==e for c in expected_edges),'no_right_result':sum(c['edition']==e and c['right_groups']==0 for c in expected_edges)} for e in m['editions']}
 text=(HERE/'artifacts/FULL_READER.md').read_text()
 for u in expected:
  assert u['edition']+' '+u['id'] in text
  for l in u['lines']:
   assert l['locus']+' RAW: `'+ ' '.join(l['words'])+'`' in text
   for c in m['candidates'].values():assert ' '.join(c['dictionary'].get(w,'⟦'+w+'⟧') for w in l['words']) in text
 output={'status':'PASS','native_paragraphs':len(expected),'unique_source_groups':result['unique_source_groups'],'alignment_rows':len(rows),'graphs':len(graphs),'coverage':'raw source selection, complete constant renderings and specified graph ids; not syntax, semantic consistency or meaning','semantic_validation':False}
 (HERE/'artifacts/VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
if __name__=='__main__':main()
