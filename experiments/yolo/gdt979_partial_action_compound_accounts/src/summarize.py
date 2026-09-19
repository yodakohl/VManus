"""Display-only tables of the frozen primary consequences; no new search."""
import collections,csv,gzip,json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
cases=json.loads(gzip.decompress((E/'artifacts/CASES.json.gz').read_bytes()));atoms=['L','P','S','OA','OB','OC']
labels={'L':'late arrival / A to B','P':'permission / B to C (M), B to A (D)','S':'satisfaction / B or C to A','OA':'observe A','OB':'observe B','OC':'observe C'}
def table(name,cols,rows):
 with (E/'artifacts'/name).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(cols);w.writerows(rows)
rows=[]
for c in cases:
 for i,w in enumerate(c['witnesses']):
  groups=['+'.join(atoms[a] for a in g) for g in w['groups']]
  rows.append([c['reading'],c['model'],c['id'],c['leaf'],i,' '.join(c['words']),*[(v if v is not None else 'UNASSIGNED') for v in w['key']],' | '.join(groups),w['has_p'],','.join(atoms[j] for j,v in enumerate(w['key']) if v is None),'LOCAL_ONLY_NO_REGISTERED_JOINT_KEY',0])
table('CANDIDATE_TABLE.tsv',['reading','model','paragraph','leaf','witness','whole_literal_paragraph',*atoms,'complete_atom_groups','contains_permission','unassigned_atom_values','decision','independent_confirmation_leaves'],rows)
pairrows=[];summary={}
for reading in ['ZL3b','IT2a','RF1b']:
 for model in ['M','D']:
  cs=[c for c in cases if c['reading']==reading and c['model']==model]
  yes=[(c,i,w) for c in cs for i,w in enumerate(c['witnesses']) if w['has_p']]
  no=[(c,i,w) for c in cs for i,w in enumerate(c['witnesses']) if not w['has_p']]
  reasons=collections.Counter();conflicts=collections.Counter()
  for a,ai,wa in yes:
   for b,bi,wb in no:
    diff=[atoms[i]+':'+x+'!='+y for i,(x,y) in enumerate(zip(wa['key'],wb['key'])) if x is not None and y is not None and x!=y]
    merged=[x if x is not None else y for x,y in zip(wa['key'],wb['key'])]
    prefix=[atoms[i]+'/'+atoms[j] for i,x in enumerate(merged) for j,y in enumerate(merged) if i<j and x is not None and y is not None and (x.startswith(y) or y.startswith(x))]
    decision='SAME_PHYSICAL_LEAF' if a['leaf']==b['leaf'] else 'ATOM_VALUE_CONFLICT' if diff else 'PREFIX_CONFLICT' if prefix else 'COMPATIBLE'
    reasons[decision]+=1
    if a['leaf']!=b['leaf']:
     conflicts.update(x.split(':',1)[0] for x in diff)
    pairrows.append([reading,model,a['id'],ai,b['id'],bi,decision,';'.join(diff),';'.join(prefix)])
  summary[reading+'/'+model]={'comparisons':len(yes)*len(no),'decisions':dict(reasons),'different_leaf_atom_conflicts':dict(conflicts)}
table('PAIR_CONTRADICTIONS.tsv',['reading','model','permission_paragraph','permission_witness','no_permission_paragraph','no_permission_witness','decision','all_shared_atom_conflicts','merged_prefix_conflicts'],pairrows)
(E/'artifacts/DISPLAY_CHECK.json').write_text(json.dumps({'status':'COMPLETE_DISPLAY_TABLES','candidate_rows':len(rows),'pair_rows':len(pairrows),'pair_summary':summary,'scope':'Frozen witness consequences only; no new model, binding or target search.'},indent=2)+'\n')
print(json.dumps({'candidate_rows':len(rows),'pair_rows':len(pairrows),'pair_summary':summary},indent=2))
