"""Independent frozen source/role/consequence reconstruction, not meanings."""
import json,hashlib,csv,io
from pathlib import Path
H=Path(__file__).resolve().parents[1];R=H.parents[2]
def j(p):return json.loads((H/p).read_text())
def main():
 m=j('src/MODEL.json')
 for p,d in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==d
 cache=json.loads((R/m['source']).read_text());assert cache['RF1b']==[]
 us=[];want=[];events=[]
 for e in m['editions']:
  for u in cache[e]:
   if not any(set(l['words'])&set(m['target_wholes']) for l in u['lines']):continue
   us.append({'edition':e,**u}); seq=[(w,sid) for l in u['lines'] for w,sid in zip(l['words'],l['source_ids'])]
   split={i for i in range(len(seq)-1) if [seq[i][0],seq[i+1][0]]==['dal','chedy']}
   for i,(w,sid) in enumerate(seq):
    if w!='pchedy':continue
    after=seq[i+1] if i+1<len(seq) else None;typ=m['types_CAUS'].get(after[0],'UNKNOWN') if after else 'ABSENT'
    label='ARITY_CONTRADICTION' if after is None else 'ASSUMED_NOMINAL_COMPATIBLE' if typ=='NOMINAL' else 'UNBOUND_PATIENT_TYPE' if typ=='UNKNOWN' else 'ASSIGNED_NONNOMINAL_CONTRADICTION'
    for c in m['candidates']:events.append({'candidate':c,'edition':e,'paragraph':u['id'],'pchedy_id':sid,'patient_id':after[1] if after else None,'patient_raw':after[0] if after else None,'CAUS_assumed_patient_type':typ,'prediction':'immediate right nominal patient' if c=='CAUS' else 'no universal immediate right nominal rule','result':label if c=='CAUS' else 'NOT_ASSERTED_NO_MEANING_CONFIRMATION'})
   off=0
   for l in u['lines']:
    for c,v in m['candidates'].items():
     for i,(w,sid) in enumerate(zip(l['words'],l['source_ids'])):
      ctor=off+i in split;want.append({'candidate':c,'edition':e,'paragraph':u['id'],'locus':l['locus'],'position':i+1,'source_id':sid,'raw':w,'value':'NOT(scope-next-chedy)_C0' if ctor else v['dictionary'].get(w,'⟦'+w+'⟧'),'lexical':w in v['dictionary'],'construction_only':ctor})
    off+=len(l['words'])
 assert us==j('src/SOURCE.json')['units'];assert want==j('artifacts/ALIGNMENT.json');assert events==j('artifacts/CANDIDATE_TABLE.json')
 tab=list(csv.DictReader(io.StringIO((H/'artifacts/CANDIDATE_TABLE.tsv').read_text()),delimiter='\t'));assert len(tab)==len(events)
 for got,expected in zip(tab,events):assert got=={k:'' if v is None else str(v) for k,v in expected.items()}
 graphs=j('artifacts/GRAPHS.json');assert len(graphs)==8
 for g in graphs:
  ln=next(l for u in us if u['edition']==g['edition'] for l in u['lines'] if l['locus']==g['locus']);assert g['source_ids']==ln['source_ids']
  if g['locus']=='f77r.36':assert g['fifth_raw']==ln['words'][4] and g['P_node']==ln['source_ids'][1] and g['medicine']==ln['source_ids'][2] and g['flow_carrier']=='UNBOUND' and g['tail_ids']==ln['source_ids'][6:]
  else:assert g['LP_node']==ln['source_ids'][6] and g['LKE_node']==ln['source_ids'][8] and g['arguments']=='UNBOUND'
 reader=(H/'artifacts/FULL_READER.md').read_text()
 for u in us:
  assert u['edition']+' '+u['id'] in reader
  for l in u['lines']:assert l['locus']+' RAW: `'+ ' '.join(l['words'])+'`' in reader
 result=j('artifacts/RESULT.json');assert result['source_groups']==sum(u['groups'] for u in us) and result['native_paragraphs']==len(us) and result['alignment_rows']==len(want) and result['candidate_cases']==len(events)
 ca=[v for v in events if v['candidate']=='CAUS'];failure=[v for v in ca if 'CONTRADICTION' in v['result']]
 assert result['decision']==('LOCAL_OPERATION_EFFICACY_UNSELECTED_CAUS_RIGHT_PATIENT_CONTRADICTED' if failure else 'LOCAL_OPERATION_EFFICACY_UNSELECTED_NO_CONFIRMED_PATIENT')
 assert result['contradiction_physical_loci']==sorted({v['pchedy_id'].split('|')[1] for v in failure})
 for e in m['editions']:
  for label,count in result['CAUS_results'][e].items():assert count==sum(v['edition']==e and v['result']==label for v in ca)
  assert result['target_occurrences'][e]=={w:sum(l['words'].count(w) for u in us if u['edition']==e for l in u['lines']) for w in m['target_wholes']}
  for c in m['candidates']:
   rows=[r for r in want if r['edition']==e and r['candidate']==c]
   assert sum(r['lexical'] for r in rows if r['locus']=='f77r.36')==5
   assert sum(r['lexical'] for r in rows if r['paragraph']=='f115v|f115v.8-f115v.10')==15
 assert result['confirmed_words']==0 and result['semantic_selection'] is None
 out={'status':'PASS','units':len(us),'groups':result['source_groups'],'alignments':len(want),'cases':len(events),'scope':'source/model hashes, complete native selection, constant readers, finite constructor/raw fields, every registered right-patient consequence and graph identities','semantic_validation':False};(H/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
