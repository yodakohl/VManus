"""Exact exposed native selection, fixed C0 readers and negative-state extension."""
import csv, hashlib, json
from pathlib import Path
H=Path(__file__).resolve().parents[1]; R=H.parents[2]
def write(name,obj): (H/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def flat(u): return [(l['locus'],n,w,sid) for l in u['lines'] for n,(w,sid) in enumerate(zip(l['words'],l['source_ids']),1)]
def negatives(g):
 out=[]
 for i,(_,_,w,_) in enumerate(g):
  if w=='dalchedy': out.append((i,i,'JOINED'))
  elif w=='dal' and i+1<len(g) and g[i+1][2]=='chedy': out.append((i,i+1,'SPLIT'))
 return out

def main():
 m=json.loads((H/'src/MODEL.json').read_text())
 for p,h in m['input_hashes'].items(): assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 cache=json.loads((R/m['source']).read_text()); assert cache['RF1b']==[]
 units=[{'edition':e,**u} for e in m['editions'] for u in cache[e] if negatives(flat(u)) or any(l['locus']==m['include_counter_locus'] for l in u['lines'])]
 assert all(not u['page'].startswith('f84') and u['page']!='f116v' for u in units)
 write('src/SOURCE.json',{'units':units,'RF_native_capacity':0,'selection':'every joined/split negative native paragraph plus retained f113r.14 counter','exposure':'already exposed admitted text'})
 rows=[]; cases=[]; graphs=[]; reader=['# Joint C0 state hypotheses: complete native paragraphs, unknowns retained']
 for u in units:
  g=flat(u); ns=negatives(g); negtails={b for a,b,t in ns if t=='SPLIT'}; negstarts={a for a,b,t in ns if t=='SPLIT'}
  reader+=['\n## '+u['edition']+' '+u['id']]
  for c,v in m['candidates'].items():
   for a,b,t in ns:
    later=[x[3] for i,x in enumerate(g) if i>b and x[2]=='chedy' and i not in negtails]
    cases.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'leaf':u['leaf'],'kind':t,'negative_ids':[x[3] for x in g[a:b+1]],'negative_raw':[x[2] for x in g[a:b+1]],'later_positive_ids':later,'prediction':'later exact bare positive in same native paragraph','result':'RAW_CAPACITY_ONLY' if later else 'CONDITIONAL_CONSTRUCTION_CONTRADICTION','independent_carrier_binding':False,'negative_value':v['joint_negative'],'positive_value':v['joint_positive']})
  k=0
  for l in u['lines']:
   reader+=['\n'+l['locus']+' RAW: `'+ ' '.join(l['words'])+'`']
   for c,v in m['candidates'].items():
    vals=[]
    for n,(w,sid) in enumerate(zip(l['words'],l['source_ids']),1):
     lexical=w in v['dictionary']; constructor=(k+n-1) in negstarts
     value='NOT(scope-next-chedy)_C0' if constructor else v['dictionary'].get(w,'⟦'+w+'⟧')
     vals.append(value); rows.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'position':n,'source_id':sid,'raw':w,'value':value,'lexical':lexical,'construction_only':constructor})
    reader+=[c+': '+' '.join(vals)]
    if l['locus']=='f115v.9': reader+=['C0: '+v['focal_middle_C0']]
    if l['locus']=='f115v.10': reader+=['C0: '+v['focal_final_C0']]
   k+=len(l['words'])
  if any(l['locus']=='f115v.10' for l in u['lines']):
   q=next(l for l in u['lines'] if l['locus']=='f115v.9')['source_ids']; z=next(l for l in u['lines'] if l['locus']=='f115v.10')['source_ids']
   for c,v in m['candidates'].items(): graphs.append({'candidate':c,'edition':u['edition'],'patient_identity_assumed':[q[8],z[3]],'preparation_identity_assumed':[q[6],z[1]],'removal':{'agent':q[6],'predicate':q[7],'patient':q[8],'removed':q[9]},'transition':{'patient':z[3],'initial_state':z[4],'predicate':z[5],'final_state':z[6]},'status':'ASSUMED_NOT_MEANING_BOUND'})
 write('artifacts/ALIGNMENT.json',rows); write('artifacts/CANDIDATE_TABLE.json',cases); write('artifacts/GRAPHS.json',graphs)
 with (H/'artifacts/CANDIDATE_TABLE.tsv').open('w',newline='') as f:
  cols=['candidate','edition','paragraph','leaf','kind','negative_ids','negative_raw','negative_value','positive_value','later_positive_ids','result','independent_carrier_binding']
  wr=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');wr.writeheader()
  for v in cases: wr.writerow({k:json.dumps(v[k],ensure_ascii=False) if isinstance(v[k],list) else v[k] for k in cols})
 (H/'artifacts/FULL_READER.md').write_text('\n\n'.join(reader)+'\n')
 summaries={c:{e:{'negative_cases':sum(v['candidate']==c and v['edition']==e for v in cases),'contradictions':sum(v['candidate']==c and v['edition']==e and v['result']=='CONDITIONAL_CONSTRUCTION_CONTRADICTION' for v in cases),'raw_capacity_only':sum(v['candidate']==c and v['edition']==e and v['result']=='RAW_CAPACITY_ONLY' for v in cases),'groups':sum(v['candidate']==c and v['edition']==e for v in rows),'lexical_assigned':sum(v['candidate']==c and v['edition']==e and v['lexical'] for v in rows),'construction_only':sum(v['candidate']==c and v['edition']==e and v['construction_only'] for v in rows),'unread':sum(v['candidate']==c and v['edition']==e and not v['lexical'] and not v['construction_only'] for v in rows)} for e in m['editions']} for c in m['candidates']}
 has_failure=any(v['result']=='CONDITIONAL_CONSTRUCTION_CONTRADICTION' for v in cases)
 result={'decision':'JOINT_HEALTH_PURITY_C0_UNRANKED_EXPLICIT_PROGRESS_CONTRADICTED' if has_failure else 'JOINT_HEALTH_PURITY_C0_UNRANKED_PROGRESS_CAPACITY_ONLY','native_paragraphs':len(units),'source_groups':sum(u['groups'] for u in units),'alignment_rows':len(rows),'candidate_cases':len(cases),'focal_graphs':len(graphs),'physical_leaves':sorted({u['leaf'] for u in units}),'summaries':summaries,'confirmed_words':0,'independent_meaning_confirmation_capacity':0,'extension_contradiction_physical_loci':sorted({v['negative_ids'][0].split('|')[1] for v in cases if v['result']=='CONDITIONAL_CONSTRUCTION_CONTRADICTION'}),'focal_assigned_groups_per_reader':13,'focal_unread_groups_per_reader':14,'semantic_selection':None,'relation_score_ready':False,'significance':False,'prior_failures_preserved':['GDT1112','GDT1113','GDT1114']}
 write('artifacts/RESULT.json',result);print(json.dumps(result))
if __name__=='__main__': main()
