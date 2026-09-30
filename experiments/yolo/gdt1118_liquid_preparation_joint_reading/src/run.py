"""Materialize three declared C0 tuples without inferring unknown carriers."""
import json,hashlib,csv,itertools
from pathlib import Path
H=Path(__file__).resolve().parents[1];R=H.parents[2]
def put(p,x):(H/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 m=json.loads((H/'src/MODEL.json').read_text())
 for p,h in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 cache=json.loads((R/m['source']).read_text());units=[]
 for e in m['editions']:
  for wanted in m['paragraphs']:
   hits=[u for u in cache[e] if u['id']==wanted];assert len(hits)==1
   u=hits[0];assert not u['page'].startswith('f84') and u['page']!='f116v';units.append({'edition':e,**u})
 put('src/SOURCE.json',{'units':units,'scope':'ten unchanged native paragraph reader units; exposed exploratory selection','RF_native_capacity':0})
 rows=[];text=['# Complete constant joint readers: M/V/N, all meanings C0'];graphs=[]
 for u in units:
  seq=[w for l in u['lines'] for w in l['words']];split={i for i in range(len(seq)-1) if seq[i:i+2]==['dal','chedy']};offset=0
  text+=['\n## '+u['edition']+' '+u['id']]
  for l in u['lines']:
   text+=['\n'+l['locus']+' RAW: `'+ ' '.join(l['words'])+'`']
   for c,v in m['models'].items():
    vals=[]
    for i,(w,sid) in enumerate(zip(l['words'],l['source_ids'])):
     ctor=offset+i in split;val='NOT(scope-next-chedy)_C0' if ctor else v['dictionary'].get(w,'⟦'+w+'⟧')
     rows.append({'candidate':c,'edition':u['edition'],'paragraph':u['id'],'locus':l['locus'],'position':i+1,'source_id':sid,'raw':w,'value':val,'lexical':w in v['dictionary'],'construction_only':ctor});vals.append(val)
    text+=[c+': '+' '.join(vals)]
   if l['locus'] in m['focal_graphs']:
    g={'edition':u['edition'],'locus':l['locus'],'raw':l['words'],'source_ids':l['source_ids'],'interpretation':m['focal_graphs'][l['locus']]}
    if l['locus']=='f77r.27':g['N_subject_ids']=[l['source_ids'][i-1] for i in m['focal_graphs'][l['locus']]['N_subject_positions']];g['N_flow_id']=l['source_ids'][4];g['N_source_id']=l['source_ids'][5]
    graphs.append(g)
   offset+=len(l['words'])
  if u['page']=='f104r':
   heads=[{'raw':w,'source_id':sid} for l in u['lines'] for w,sid in zip(l['words'],l['source_ids']) if w in m['N_nominal_candidates']]
   graphs.append({'edition':u['edition'],'paragraph':u['id'],'N_possible_nominal_mentions':heads,'N_flow_carrier':'UNBOUND','repeated_genitives_are_not_bare_subjects':True,'old1117_failure':'RETAINED_NOT_RERUN_NOT_REPAIRED'})
  if u['page']=='f115v':graphs.append({'edition':u['edition'],'paragraph':u['id'],'N_interpretation':m['focal_graphs']['f115v.8-f115v.10'],'inherited_identity_status':'ASSUMED_NOT_BOUND'})
 put('artifacts/ALIGNMENT.json',rows);put('artifacts/GRAPHS.json',graphs);(H/'artifacts/FULL_READER.md').write_text('\n\n'.join(text)+'\n')
 prior=json.loads((R/'experiments/yolo/gdt1117_purification_operation_efficacy/src/MODEL.json').read_text())['candidates']['EFF']['dictionary']
 comp=[]
 for a,b in itertools.combinations(m['models'],2):
  da=m['models'][a]['dictionary'];db=m['models'][b]['dictionary'];diff=[{'raw':w,a:da[w],b:db[w]} for w in sorted(set(da)&set(db)) if da[w]!=db[w]];comp.append({'left':a,'right':b,'incompatible_shared_values':diff,'unchanged_shared_dictionary_compatible':not diff})
 with (H/'artifacts/CANDIDATE_TABLE.tsv').open('w',newline='') as f:
  writer=csv.writer(f,delimiter='\t',lineterminator='\n');writer.writerow(['raw','1117EFF','M','V','N'])
  for w in sorted(set().union(*(set(v['dictionary']) for v in m['models'].values()))):writer.writerow([w,prior.get(w,'UNASSIGNED')]+[m['models'][c]['dictionary'].get(w,'UNASSIGNED') for c in ['M','V','N']])
 put('artifacts/DICTIONARY_COMPARISON.json',{'pairs':comp,'EFF_parent_overrides':{c:{w:{'EFF':prior[w],'joint':v['dictionary'][w]} for w in prior if v['dictionary'][w]!=prior[w]} for c,v in m['models'].items()},'meaning_selection':None})
 focal={l:{'assigned':sum(r['lexical'] for r in rows if r['candidate']=='N' and r['edition']==e and r['locus']==l),'raw':sum(r['candidate']=='N' and r['edition']==e and r['locus']==l for r in rows)} for e in ['ZL3b'] for l in ['f77r.14','f77r.27','f77r.34','f77r.35','f77r.36']}
 f115={e:sum(r['lexical'] for r in rows if r['candidate']=='N' and r['edition']==e and r['paragraph'].startswith('f115v|')) for e in m['editions']}
 result={'decision':'NEW_JOINT_PREPARATION_C0_UNSELECTED_COUNTER_CARRIER_UNBOUND','native_units':len(units),'raw_groups':sum(u['groups'] for u in units),'alignments':len(rows),'physical_leaves':sorted({u['leaf'] for u in units}),'focal_N_ZL':focal,'focal115_N_assigned':f115,'counter104_N_possible_nominal_mentions':{g['edition']:len(g['N_possible_nominal_mentions']) for g in graphs if 'N_possible_nominal_mentions' in g},'global_scope':'Profiles descriptive179selectors; constant semantic reader limited tofive nominated complete native paragraphs per edition','old_failures':['GDT1112','GDT1113','GDT1114','GDT1116','GDT1117'],'semantic_selection':None,'confirmed_words':0,'independent_meaning_capacity':0,'significance':False}
 put('artifacts/RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
