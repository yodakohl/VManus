"""Exhaustive fixed complete-register calculation; no glyph decoder."""
from pathlib import Path
import csv,gzip,hashlib,io,itertools,json,re
import numpy as np
E=Path(__file__).resolve().parents[1]; R=E.parents[2]; A=E/'artifacts'
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tsv(p,rows,fields):
 with p.open('w') as f:
  w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def zipped(p,header,rows):
 text=io.StringIO();w=csv.writer(text,delimiter='\t',lineterminator='\n');w.writerow(header);w.writerows(rows)
 p.write_bytes(gzip.compress(text.getvalue().encode(),mtime=0))
def run():
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for p,h in lock['files'].items():assert sha(R/p)==h,p
 source=json.loads((E/'src/SOURCE.json').read_text());names={x['value']:x['name'] for x in source['figures']}
 mothers=np.array(list(itertools.product(range(16),repeat=4)),dtype=np.uint8)
 family=np.zeros((65536,15),dtype=np.uint8);family[:,:4]=mothers
 for r in range(4):
  for c in range(4):family[:,4+r]|=((mothers[:,c]>>(3-r))&1)<<(3-c)
 for j,(a,b) in enumerate(source['pairs_1based'],8):family[:,j]=family[:,a-1]^family[:,b-1]
 assert len({tuple(x) for x in family.tolist()})==65536
 zipped(A/'ALL_SOURCE_PREDICTIONS.tsv.gz',['candidate_id']+[f'figure_{i}' for i in range(1,16)],([i,*map(int,row)] for i,row in enumerate(family)))
 targets=[];cases=[];consequences=[];matches=[];steps=[]
 for ed in ['ZL3b','IT2a','RF1b']:
  rel=f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_EVALUATION_{ed}.json';d=json.loads((R/rel).read_text())
  selected={x['metadata']['locus']:x for x in d['lines'] if x['metadata']['page']=='f66r' and x['metadata']['locus'] in {f'f66r.{i}' for i in range(1,16)}}
  entries=[]
  for i in range(1,16):
   loc=f'f66r.{i}';line=selected.get(loc);groups=[] if line is None else [dict(zip(d['group_columns'],g)) for g in line['groups']]
   state='NO_CAPACITY' if len(groups)!=1 else 'KNOWN' if re.fullmatch('[a-z]+',groups[0]['ivtff_group_raw']) and groups[0]['left_separator']=='LINE_START' and groups[0]['right_separator']=='LINE_END' else 'UNKNOWN'
   record={'edition':ed,'page':'f66r','physical_leaf':'f66','position_top_down':i,'locus':loc,'state':state,'groups':groups,'raw':' | '.join(g['ivtff_group_raw'] for g in groups),'source':rel}
   targets.append(record);entries.append(record)
  for direction in ['TOP_DOWN','BOTTOM_UP']:
   ordered=entries if direction=='TOP_DOWN' else list(reversed(entries));cid=ed+'_'+direction
   capacity=any(x['state']=='NO_CAPACITY' for x in ordered);keep=np.ones(65536,dtype=bool);constraints=[]
   if not capacity:
    for j in range(15):
     if ordered[j]['state']!='KNOWN':continue
     for i in range(j):
      if ordered[i]['state']!='KNOWN':continue
      equal=ordered[i]['raw']==ordered[j]['raw'];before=int(keep.sum());keep&=(family[:,i]==family[:,j]) if equal else (family[:,i]!=family[:,j]);after=int(keep.sum())
      c={'case':cid,'step':len(constraints)+1,'position_a':i+1,'position_b':j+1,'locus_a':ordered[i]['locus'],'locus_b':ordered[j]['locus'],'raw_a':ordered[i]['raw'],'raw_b':ordered[j]['raw'],'required':'EQUAL' if equal else 'DIFFERENT','before':before,'after':after};constraints.append(c);steps.append(c)
   else:keep[:]=False
   indices=np.flatnonzero(keep);n=len(indices);unknown=sum(x['state']=='UNKNOWN' for x in ordered)
   status='NO_CAPACITY' if capacity else 'CONTRADICTED' if not n else 'UNRESOLVED_ONLY' if unknown else 'COMPATIBLE_HYPOTHETICAL_CALCULATIONS'
   case={'case':cid,'edition':ed,'direction':direction,'status':status,'surviving_calculations':n,'known_positions':sum(x['state']=='KNOWN' for x in ordered),'unknown_positions':unknown,'known_types':len({x['raw'] for x in ordered if x['state']=='KNOWN'}),'physical_leaves':1,'independent_confirmation_leaves':0,'first_elimination':next((c for c in constraints if c['before'] and not c['after']),None),'surviving_ids':list(map(int,indices))};cases.append(case)
   for j,x in enumerate(ordered):
    vals=sorted(set(map(int,family[indices,j]))) if n else []
    consequences.append({'case':cid,'model_position':j+1,'target_locus':x['locus'],'target_raw':x['raw'],'target_state':x['state'],'possible_figures':','.join(map(str,vals)),'possible_names':' | '.join(names[v] for v in vals),'candidate_count':n,'independent_confirmation_leaves':0})
   for idx in indices:matches.append([cid,int(idx),*map(int,family[idx])])
 reading_rows=[]
 for row in matches:
  if row[0].startswith('IT2a_'):
   reading_rows.append({'case':row[0],'candidate_id':row[1],**{f'position_{j+1}':names[v] for j,v in enumerate(row[2:])}})
 tsv(A/'ALL_COMPLETE_NAMED_READINGS.tsv',reading_rows,['case','candidate_id']+[f'position_{j}' for j in range(1,16)])
 js(A/'TARGET_RECORDS.json',targets);js(A/'ALL_CASES.json',cases)
 tsv(A/'POSITION_CONSEQUENCES.tsv',consequences,list(consequences[0]));tsv(A/'CONSTRAINT_ELIMINATION.tsv',steps,list(steps[0]) if steps else ['case','step'])
 zipped(A/'ALL_SURVIVING_CALCULATIONS.tsv.gz',['case','candidate_id']+[f'figure_{i}' for i in range(1,16)],matches)
 distinct=np.array([len(set(row)) for row in family.tolist()]);hist={str(i):int((distinct==i).sum()) for i in sorted(set(distinct))}
 result={'status':'ALL_FIXED_CASES_CONTRADICTED' if all(c['status']=='CONTRADICTED' for c in cases) else 'COMPLETE_EXPLORATORY_COMPARISON','source_calculations':65536,'source_distinct_figure_histogram':hist,'cases':[{k:v for k,v in c.items() if k not in {'surviving_ids','first_elimination'}} for c in cases],'source_program':'Turner1655 common; early program not certified','preregistration_commit':'8d017cb3d','prior_exposure':True,'new_pages':0,'independent_confirmation_leaves':0,'confirmed_words':0,'significance':'NOT_ASSESSED_NO_GLOBAL_SEARCH_NULL','excluded_alternative':'Turner alternative house placement and nonliteral/compositional labels not tested'}
 result['interpretation']='All15 IT labels differ: any injectively renamed fifteen-label list gives the same sixteen calculations per order. No spelling-specific content evidence or preferred key.'
 result['complete_IT_candidate_pairs']=len(reading_rows)
 result['selection_decision']='RETAIN_CONDITIONAL_READINGS_ONLY; do not adopt a figure name or expand merely from compatibility.'
 js(A/'RESULT.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
