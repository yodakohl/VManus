"""Reconstruct artifact selection and raw alignments, not meanings."""
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parents[1];R=H.parents[2]
def j(p):return json.loads((H/p).read_text())
def main():
 m=j('src/MODEL.json')
 for p,h in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 cache=json.loads((R/m['source']).read_text());assert cache['RF1b']==[]
 units=[{'edition':e,**u} for e in m['editions'] for u in cache[e] if set(l['locus'] for l in u['lines']) & set(m['selection_loci'])];assert len(units)==4 and j('src/SOURCE.json')['units']==units
 want=[]
 for u in units:
  for l in u['lines']:
   for c,model in m['candidates'].items():
    for n,(w,sid) in enumerate(zip(l['words'],l['source_ids']),1):want.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'position':n,'source_id':sid,'raw':w,'value':model['dictionary'].get(w,'⟦'+w+'⟧'),'assigned':w in model['dictionary']})
 assert want==j('artifacts/ALIGNMENT.json')
 graphs=j('artifacts/GRAPHS.json');assert len(graphs)==4
 for g in graphs:
  l=next(l for u in units if u['edition']==g['edition'] for l in u['lines'] if l['locus']=='f115v.10');ids=l['source_ids'];assert g['raw']==l['words'] and g['source_ids']==ids and g['predicate']==ids[6]
  assert g['subject']==(ids[3:6] if g['candidate']=='FORM' else ids[3:4]);assert g['written_result']==([] if g['candidate']=='FORM' else ids[4:6]);assert g['opening_to_final_physical_identity']=='UNBOUND'
 reader=(H/'artifacts/FULL_READER.md').read_text()
 for u in units:
  assert u['edition']+' '+u['id'] in reader
  for l in u['lines']:assert l['locus']+' RAW: `'+ ' '.join(l['words'])+'`' in reader
 result=j('artifacts/RESULT.json');assert result['source_groups']==sum(len(l['words']) for u in units for l in u['lines']) and result['alignment_rows']==len(want) and result['confirmed_words']==0 and not result['fixed_meaning_test']
 for c in m['candidates']:
  for e in m['editions']:
   rows=[r for r in want if r['candidate']==c and r['edition']==e];assert result['coverage'][c][e]=={'groups':len(rows),'assigned':sum(r['assigned'] for r in rows),'unread':sum(not r['assigned'] for r in rows)}
 out={'status':'PASS','source_groups':result['source_groups'],'alignment_rows':len(want),'graphs':4,'scope':'Exact native selection, constant whole values, raw source ids and specified focal graph positions; not syntax/meaning/physical identity','semantic_validation':False};(H/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
