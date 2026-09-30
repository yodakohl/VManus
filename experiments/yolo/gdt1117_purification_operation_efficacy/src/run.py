"""Finite C0 purification roles and exact causal next-patient conjunction."""
import json,hashlib,csv
from pathlib import Path
H=Path(__file__).resolve().parents[1];R=H.parents[2]
def put(p,x):(H/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 m=json.loads((H/'src/MODEL.json').read_text())
 for p,h in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 cache=json.loads((R/m['source']).read_text());assert cache['RF1b']==[]
 units=[{'edition':e,**u} for e in m['editions'] for u in cache[e] if any(w in m['target_wholes'] for l in u['lines'] for w in l['words'])]
 assert all(not u['page'].startswith('f84') and u['page']!='f116v' for u in units)
 put('src/SOURCE.json',{'units':units,'RF_native_capacity':0,'exposure':'already admitted exposed native cache'})
 rows=[];cases=[];graphs=[];reader=['# Complete C0 readers; CAUS operation versus EFF cleansing ability']
 for u in units:
  flat=[(l['locus'],n,w,sid) for l in u['lines'] for n,(w,sid) in enumerate(zip(l['words'],l['source_ids']),1)]
  splits={i for i,v in enumerate(flat[:-1]) if v[2]=='dal' and flat[i+1][2]=='chedy'}
  reader+=['\n## '+u['edition']+' '+u['id']]
  for i,x in enumerate(flat):
   if x[2]!='pchedy':continue
   following=flat[i+1] if i+1<len(flat) else None
   typ=m['types_CAUS'].get(following[2],'UNKNOWN') if following else 'ABSENT'
   result='ARITY_CONTRADICTION' if following is None else ('ASSUMED_NOMINAL_COMPATIBLE' if typ=='NOMINAL' else ('UNBOUND_PATIENT_TYPE' if typ=='UNKNOWN' else 'ASSIGNED_NONNOMINAL_CONTRADICTION'))
   for c in m['candidates']:cases.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'pchedy_id':x[3],'patient_id':following[3] if following else None,'patient_raw':following[2] if following else None,'CAUS_assumed_patient_type':typ,'prediction':'immediate right nominal patient' if c=='CAUS' else 'no universal immediate right nominal rule','result':result if c=='CAUS' else 'NOT_ASSERTED_NO_MEANING_CONFIRMATION'})
  offset=0
  for l in u['lines']:
   reader+=['\n'+l['locus']+' RAW: `'+ ' '.join(l['words'])+'`']
   for c,v in m['candidates'].items():
    vals=[]
    for n,(w,sid) in enumerate(zip(l['words'],l['source_ids']),1):
     ctor=offset+n-1 in splits;lexical=w in v['dictionary'];value='NOT(scope-next-chedy)_C0' if ctor else v['dictionary'].get(w,'⟦'+w+'⟧')
     vals.append(value);rows.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'position':n,'source_id':sid,'raw':w,'value':value,'lexical':lexical,'construction_only':ctor})
    reader+=[c+': '+' '.join(vals)]
    if l['locus']=='f77r.36':
     graphs.append({'candidate':c,'edition':u['edition'],'locus':l['locus'],'source_ids':l['source_ids'],'topic':l['source_ids'][0],'P_role':v['pchedy_role'],'P_node':l['source_ids'][1],'medicine':l['source_ids'][2],'pure_property':l['source_ids'][3],'topic_medicine_same_identity':'ASSUMED','fifth_raw':l['words'][4],'fifth_id':l['source_ids'][4],'flow_predicate':l['source_ids'][5],'flow_carrier':'UNBOUND','tail_ids':l['source_ids'][6:],'tail_meaning':'UNBOUND','first4_C0':v['focal_first4']});reader+=['C0 first4 only: '+v['focal_first4']]
    if l['locus']=='f115v.8':graphs.append({'candidate':c,'edition':u['edition'],'locus':l['locus'],'source_ids':l['source_ids'],'LP_node':l['source_ids'][6],'LP_role':v['lpchedy_role'],'LKE_node':l['source_ids'][8],'LKE_role':v['lkechedy_role'],'arguments':'UNBOUND','compositional_semantics':'STIPULATED_NOT_MORPHEMES'})
   offset+=len(l['words'])
 put('artifacts/ALIGNMENT.json',rows);put('artifacts/CANDIDATE_TABLE.json',cases);put('artifacts/GRAPHS.json',graphs);(H/'artifacts/FULL_READER.md').write_text('\n\n'.join(reader)+'\n')
 with (H/'artifacts/CANDIDATE_TABLE.tsv').open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(cases[0]),delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(cases)
 ca=[x for x in cases if x['candidate']=='CAUS'];counts={e:{r:sum(x['edition']==e and x['result']==r for x in ca) for r in ['ASSUMED_NOMINAL_COMPATIBLE','UNBOUND_PATIENT_TYPE','ARITY_CONTRADICTION','ASSIGNED_NONNOMINAL_CONTRADICTION']} for e in m['editions']}
 contradictions=[x for x in ca if 'CONTRADICTION' in x['result']]
 result={'decision':'LOCAL_OPERATION_EFFICACY_UNSELECTED_CAUS_RIGHT_PATIENT_CONTRADICTED' if contradictions else 'LOCAL_OPERATION_EFFICACY_UNSELECTED_NO_CONFIRMED_PATIENT','native_paragraphs':len(units),'source_groups':sum(u['groups'] for u in units),'alignment_rows':len(rows),'candidate_cases':len(cases),'focal_graphs':len(graphs),'physical_leaves':sorted({u['leaf'] for u in units}),'target_occurrences':{e:{w:sum(l['words'].count(w) for u in units if u['edition']==e for l in u['lines']) for w in m['target_wholes']} for e in m['editions']},'CAUS_results':counts,'contradiction_physical_loci':sorted({x['pchedy_id'].split('|')[1] for x in contradictions}),'focal77_assigned':5,'focal77_unread':3,'focal115_assigned':15,'focal115_unread':12,'confirmed_words':0,'semantic_selection':None,'independent_meaning_capacity':0,'prior_failures_preserved':['GDT1112','GDT1113','GDT1114','GDT1116'],'significance':False}
 put('artifacts/RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
