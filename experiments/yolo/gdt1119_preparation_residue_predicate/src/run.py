"""Exact-source mechanical audit of two frozen, unconfirmed residue readers."""
import csv, hashlib, json
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parents[1];R=H.parents[2]
PROFILE='research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/EL_WORD_PROFILES.json'
def put(p,x): (H/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 m=json.loads((H/'src/MODEL.json').read_text())
 for p,h in m['input_hashes'].items(): assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 for v in m['models'].values():
  assert len(v['dictionary'])==29
  assert all(v['dictionary'][w]==g for w,g in m['parent_dictionary'].items())
 cache=json.loads((R/m['source']).read_text()); units=[]; targets=set(m['select_any_exact'])
 for e in m['editions']:
  seen=set()
  for u in cache[e]:
   # Selector is checked before paragraph content is accessed.
   if u['page'].startswith('f84') or u['page']=='f116v': continue
   if u['id'] in m['include_paragraphs'] or any(w in targets for l in u['lines'] for w in l['words']):
    assert u['id'] not in seen;seen.add(u['id']);units.append({'edition':e,**u})
  assert set(m['include_paragraphs'])<=seen
 profile=json.loads((R/PROFILE).read_text())
 put('src/SOURCE.json',{'source':m['source'],'sha256':hashlib.sha256((R/m['source']).read_bytes()).hexdigest(),'profile_source':PROFILE,'profile_sha256':hashlib.sha256((R/PROFILE).read_bytes()).hexdigest(),'selection_rule':m['selection_rule'],'units':units,'reader_policy':'native ZL/IT independently; RF has no borrowed boundaries','exposure':'previously exposed exploration'})
 rows=[]; occurrences=[]; graphs=[];text=['# Complete S/H constant readers','All glosses C0; unknown raw forms retained. Source IDs and native paragraph/line boundaries preserved. No grammatical success or meaning selection.'];daror=[]
 for u in units:
  seq=[(w,sid) for l in u['lines'] for w,sid in zip(l['words'],l['source_ids'])]
  neg={sid:seq[i+1][1] for i,(w,sid) in enumerate(seq[:-1]) if [w,seq[i+1][0]]==m['finite_construction']['exact']}
  block=['## '+u['edition']+' '+u['id']]
  for l in u['lines']:
   assert len(l['words'])==len(l['source_ids'])
   block+=['### '+l['locus'],'RAW: `'+ ' '.join(l['words'])+'`','IDS: `'+ ' '.join(l['source_ids'])+'`', 'Boundary: start='+str(l['start'])+'; end='+str(l['end'])]
   rendered={}
   for c,v in m['models'].items():
    vals=[]
    for i,(w,sid) in enumerate(zip(l['words'],l['source_ids'])):
     val='NOT' if sid in neg else v['dictionary'].get(w,'⟦'+w+'⟧');vals.append(val)
     rows.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'position':i+1,'source_id':sid,'raw':w,'value':val,'lexical':w in v['dictionary'],'construction_only':sid in neg,'scope_source_id':neg.get(sid)})
    rendered[c]=vals;block += [c+': '+' '.join(vals)]
   for i,(w,sid) in enumerate(zip(l['words'],l['source_ids'])):
    if w in targets: occurrences.append({'edition':u['edition'],'paragraph':u['id'],'form':w,'locus':l['locus'],'position':i+1,'source_id':sid,'raw_words':l['words'],'source_ids':l['source_ids'],'renderings':rendered})
   if l['locus'] in ['f77r.25','f77r.26']:
    graphs.append({'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'raw_words':l['words'],'source_ids':l['source_ids'],'renderings':rendered,'proposed':m['focal_core'] if l['locus']=='f77r.25' else m['focal_continuation'],'finite_negations':[{'source_id':sid,'scope_source_id':target} for sid,target in neg.items() if sid in l['source_ids']],'binding_status':'ASSUMED_NOT_INDEPENDENTLY_BOUND'})
  for g in graphs:
   if g.get('paragraph')!=u['id'] or g.get('edition')!=u['edition'] or not g.get('locus'):continue
   ids=g['source_ids']
   if g['locus']=='f77r.25':
    g['proposed_roles']={'subject':ids[2],'location':ids[3],'predicate':ids[4],'negation':ids[5],'quality':ids[6],'object':ids[7],'outside_core':ids[:2]}
    g['proposed_edges']=[{'from':ids[4],'to':ids[2],'role':'subject'},{'from':ids[4],'to':ids[7],'role':'object'},{'from':ids[3],'to':ids[2],'role':'location_assumed'},{'from':ids[5],'to':ids[6],'role':'finite_exact_negation'},{'from':ids[6],'to':ids[7],'role':'quality_attachment_assumed'}]
   else:
    g['proposed_roles']={'portion':ids[0],'flow_predicate':ids[1],'of_liquid':ids[2],'unread_tail':ids[3:]}
    g['proposed_edges']=[{'from':ids[1],'to':ids[0],'role':'flow_carrier_assumed'},{'from':ids[2],'to':ids[0],'role':'genitive_back_attachment_assumed'}]
    g['identity_with_25_preparation']='UNBOUND'
  if u['page']=='f104r': graphs.append({'edition':u['edition'],'paragraph':u['id'],'flow_carrier':'UNBOUND','identity_status':'NOT_INDEPENDENTLY_BOUND','old1117_failure':'RETAINED_NOT_RERUN_NOT_REPAIRED'})
  text+=block
  if any(w=='daror' for w,sid in seq):daror+=block
 text+=['# DAROR complete paragraph appendix']+daror
 put('artifacts/ALIGNMENT.json',rows);put('artifacts/TARGET_OCCURRENCES.json',occurrences);put('artifacts/GRAPHS.json',graphs)
 (H/'artifacts/FULL_READER.md').write_text('\n\n'.join(text)+'\n')
 with (H/'artifacts/CANDIDATE_TABLE.tsv').open('w',newline='') as f:
  out=csv.writer(f,delimiter='\t',lineterminator='\n');out.writerow(['raw','parent_N','S','H','status'])
  for w in sorted(m['models']['S']['dictionary']):out.writerow([w,m['parent_dictionary'].get(w,'UNASSIGNED'),m['models']['S']['dictionary'][w],m['models']['H']['dictionary'][w],'C0_UNCONFIRMED'])
 coverage={}
 for p in profile['profiles']:
  if p['form'] not in targets:continue
  coverage[p['form']]={}
  for e,stat in p['editions'].items():
   selected=sum(o['edition']==e and o['form']==p['form'] for o in occurrences)
   assert selected<=stat['count']
   coverage[p['form']][e]={'global_179_selector_count':stat['count'],'global_P_count':next(x['count'] for x in stat['strata']['kind'] if x['value']=='P'),'selected_complete_native_P_count':selected,'unscored_global_count':stat['count']-selected,'reason':'RF_NO_NATIVE_PARAGRAPH_CACHE' if e=='RF1b' else 'OUTSIDE_SELECTED_COMPLETE_NATIVE_P_CACHE','global_count_not_semantic_evidence':True}
 result={'decision':'EXACT_SOURCE_REPRESENTATION_C0_S_H_UNSELECTED','native_units':len(units),'units_by_edition':dict(Counter(u['edition'] for u in units)),'selected_paragraph_ids':{e:[u['id'] for u in units if u['edition']==e] for e in m['editions']},'raw_groups':sum(len(l['words']) for u in units for l in u['lines']),'alignments':len(rows),'target_occurrences':len(occurrences),'target_coverage':coverage,'daror_complete_native_paragraphs':{e:[u['id'] for u in units if u['edition']==e and any(w=='daror' for l in u['lines'] for w in l['words'])] for e in m['editions']},'parent_values_conserved':True,'dictionary_values_per_model':29,'finite_adjacent_negation_occurrences':sum(r['construction_only'] for r in rows if r['candidate']=='S'),'contradictions':'NOT_INDEPENDENTLY_SCORABLE','grammar_success':None,'semantic_selection':None,'confirmed_words':0,'independent_meaning_capacity':0,'significance':False,'assumptions':m['focal_core']['unpaid']+m['focal_continuation']['unpaid'],'old_failures_retained':['GDT1117'],'counter104_carrier':'UNBOUND','scope':'exposed native paragraph application; alternate readings not independent samples'}
 put('artifacts/RESULT.json',result);print(json.dumps({k:result[k] for k in ['native_units','units_by_edition','raw_groups','alignments','target_occurrences','target_coverage','daror_complete_native_paragraphs','finite_adjacent_negation_occurrences']},indent=2))
if __name__=='__main__':main()
