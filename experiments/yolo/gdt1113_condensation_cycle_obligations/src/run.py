"""Fixed literal inverse-last constructor. No decoder or meaning confirmation."""
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parents[1]
def put(p,x): (HERE/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 m=json.loads((HERE/'src/MODEL.json').read_text());lock=json.loads((HERE/'MODEL_LOCK.json').read_text())
 for p,h in {**m['input_hashes'],**lock['files']}.items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 allow={r['page'] for r in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 assert len(allow)==179 and not any(p.startswith('f84') or p=='f116v' for p in allow)
 original=json.loads((ROOT/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());assert not original['RF1b']
 selected=[]
 for ed in ('ZL3b','IT2a'):
  for u in original[ed]:
   assert u['page'] in allow
   if any(w in ('lchedy','chealy') for l in u['lines'] for w in l['words']): selected.append({'edition':ed,**u})
 put('src/SOURCE.json',{'units':selected,'denominators':{e:len(v) for e,v in original.items()},'selection':'all native paragraphs with exact lchedy or chealy','exposed':True,'RF_native_capacity':0})
 cases=[];cold=[];align=[];reader=[];focal=[];d=m['dictionary']
 for u in selected:
  rows=[];reader+=['\n## '+u['edition']+' '+u['id']]
  for l in u['lines']:
   assert len(l['words'])==len(l['source_ids'])
   reader += [l['locus']+' RAW: `'+ ' '.join(l['words'])+'`','C0: '+' '.join(d.get(w,'⟦'+w+'⟧') for w in l['words'])]
   for n,(w,sid) in enumerate(zip(l['words'],l['source_ids'])):rows.append({'id':sid,'raw':w,'locus':l['locus'],'line_last':n==len(l['words'])-1})
  for i,g in enumerate(rows):
   align.append({'edition':u['edition'],'paragraph':u['id'],'page':u['page'],'id':g['id'],'raw':g['raw'],'value':d.get(g['raw'],'UNREAD')})
   if g['raw']=='chealy':cold.append({'edition':u['edition'],'paragraph':u['id'],'page':u['page'],'target':g,'paragraph_last':i==len(rows)-1,'if_air_is_cold':[r['raw'] for r in rows[max(0,i-3):i+1]]==['sheedy','qokaiin','chedaiin','chealy'],'before_ids':[r['id'] for r in rows[:i]]})
   if g['raw']!='lchedy':continue
   prior=[j for j in range(i) if rows[j]['raw']=='chedy'];c={'edition':u['edition'],'paragraph':u['id'],'page':u['page'],'target':g,'prior_chedy_count':len(prior),'last_change':None,'X':None,'Y':None,'inverse_from':None,'inverse_to':None,'interval_ids':[],'unknown_interval':None,'participant_continuity_confirmed':False}
   if not prior:c['status']='OVERT_CONSTRUCTOR_CONTRADICTION'
   else:
    j=prior[-1];x=j-2 if j>=2 and rows[j-1]['raw']=='okaiin' else j-1
    c['last_change']=rows[j];c['X']=rows[x] if x>=0 else None;c['Y']=rows[j+1] if j+1<len(rows) else None;c['inverse_from']=c['Y'];c['inverse_to']=c['X']
    c['interval_ids']=[r['id'] for r in rows[j+1:i]];c['unknown_interval']=sum(r['raw'] not in d for r in rows[j+1:i]);c['status']='CONDITIONAL_REFERENCE_UNBOUND_MATERIALS'
    if c['X'] and c['Y'] and c['X']['raw']=='solkeey' and c['Y']['raw']=='qokain':c['status']='C0_VAPOUR_WATER_REFERENCE_ONLY'
   cases.append(c)
   if u['page']=='f77r' and g['locus']=='f77r.37':
    seed=[r for r in rows if r['locus']=='f77r.35' and r['raw']=='chedy'];assert len(seed)==1
    focal.append({'edition':u['edition'],'target':g,'claimed_change35':seed[0],'actual_change':c['last_change'],'X':c['X'],'Y':c['Y'],'claim_matches_last':c['last_change']==seed[0]})
 for name,x in [('CASES',cases),('COLD_CASES',cold),('FOCAL',focal)]:put('artifacts/'+name+'.json',x)
 for name,x in [('CASE_TABLE',cases),('ALIGNMENT',align)]:
  with (HERE/('artifacts/'+name+'.tsv')).open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t');w.writeheader()
   for r in x:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
 (HERE/'artifacts/FULL_READER.md').write_text('# Full selected native paragraphs; every gloss C0\n'+'\n\n'.join(reader)+'\n')
 summaries={e:{'lchedy':sum(c['edition']==e for c in cases),'status_counts':dict(Counter(c['status'] for c in cases if c['edition']==e)),'chealy':sum(c['edition']==e for c in cold),'cold_templates':sum(c['edition']==e and c['if_air_is_cold'] for c in cold)} for e in ('ZL3b','IT2a')}
 result={'decision':'OVERT_INVERSE_LAST_WRITER_CONTRADICTED' if any(c['status']=='OVERT_CONSTRUCTOR_CONTRADICTION' for c in cases) else 'C0_WRITER_ONLY','focal_decision':'DIRECT_35_TO_37_BINDING_CONTRADICTED' if any(not c['claim_matches_last'] for c in focal) else 'C0_ONLY','native_paragraphs':len(selected),'source_groups':len(align),'summaries':summaries,'leaves':sorted({re.match(r'f(\d+)',c['page'])[1] for c in cases},key=int),'confirmed_words':0,'independent_meaning_confirmation_capacity':0,'RF_native_capacity':0,'significance':False}
 put('artifacts/RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
