"""Reconstruct every relaxed role case using recursive unit covers."""
from pathlib import Path
from itertools import permutations
from collections import Counter
from functools import lru_cache
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def load(n):return json.loads((A/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 lock=load('REGISTRATION_LOCK.json');assert lock['before_enumeration']
 for name,h in lock['files'].items():assert sha(ROOT/name)==h,name
 run=load('RUN_RECEIPT.json');assert run['runner_sha256']==sha(D/'src/run.py') and run['registration_lock_sha256']==sha(A/'REGISTRATION_LOCK.json') and run['assignments_sha256']==sha(A/'ASSIGNMENTS.json')
 results=load('RESULT.json');assignment=load('ASSIGNMENTS.json');atomized=load('ATOMIZED_LINES.json');lines=load('TARGET_LINES.json');spec=load('SPEC.json')
 raw=json.loads((ROOT/spec['raw_idea']).read_text());carrier=raw['design']['working_carrier'];abc=carrier['ordinary_signs_in_order']+['q','cfh',carrier['end_sign']]
 assert abc==assignment['alphabet'] and len(set(abc))==22
 assert len(lines)==3 and {l['edition'] for l in lines}==set(spec['editions'])
 for line in lines:
  ed=line['edition'];words=[];assert line['locus']=='f45r.10' and len(line['groups'])==9
  for i,g in enumerate(line['groups']):
   assert g['source_group_index']==i+1 and g['left_separator']==('LINE_START' if i==0 else 'DEFINITE_SPACE') and g['right_separator']==('LINE_END' if i==8 else 'DEFINITE_SPACE')
   text=g['ivtff_group_raw'];ways=[set() for _ in range(len(text)+1)];ways[0].add(())
   for finish in range(1,len(text)+1):
    for atom in abc:
     begin=finish-len(atom)
     if begin>=0 and text[begin:finish]==atom:
      ways[finish].update(old+(atom,) for old in ways[begin])
   assert len(ways[-1])==1;words.append(next(iter(ways[-1])))
  assert [list(w) for w in words]==atomized['working_units'][ed]
  assert [g['ivtff_group_raw'] for g in line['groups']]==atomized['tokens'][ed]
  rows=assignment['readings'][ed];assert len(rows)==22*21*20 and {(r[0],r[1],r[2]) for r in rows}==set(permutations(range(22),3))
  tally=Counter();survivors=[]
  for ie,ip2,ip3,recorded_state,recorded_at,recorded_vectors in rows:
   end,p2,p3=abc[ie],abc[ip2],abc[ip3];ordinary=set(abc)-{end,p2,p3}
   @lru_cache(None)
   def covers(w):
    if not w:return {(0,0)}
    forms=[]
    if w[0] in ordinary:forms.append((1,0))
    if w[0]==end:forms.append((1,1))
    if w[0]==p2 and len(w)>=2 and w[1] in ordinary:forms.append((2,0))
    if w[0]==p3 and len(w)>=3 and w[1] in ordinary and w[2] in ordinary:forms.append((3,0))
    return {(n+1,e+extra) for width,extra in forms for n,e in covers(w[width:])}
   vectors=[]
   for w in words:
    options=covers(w);assert len(options)<=1
    vectors.append(list(next(iter(options))) if options else [-1,-1])
   assert vectors==recorded_vectors
   state,at='PASS',0
   bad_parse=[i+1 for i,v in enumerate(vectors) if v[0]<0];bad_capacity=[i+1 for i,v in enumerate(vectors) if v[0]>=0 and not 1<=v[0]<=8]
   # Runner reports the earliest parse/capacity issue before any cross-group check.
   failures=[(i,'PARSE') for i in bad_parse]+[(i,'CAPACITY') for i in bad_capacity]
   if failures:at,state=min(failures)
   else:
    violations=[i+2 for i in range(8) if vectors[i][0]!=vectors[i][1] and vectors[i+1][0]+vectors[i][1]!=vectors[i][0]]
    if violations:state,at='BALANCE',min(violations)
   assert (state,at)==(recorded_state,recorded_at);tally[state]+=1
   if state=='PASS':survivors.append([ie,ip2,ip3])
  expected='NO_RENAMED_COLUMN_BALANCE' if not survivors else 'NECESSARY_RELAXATION_SURVIVES'
  assert results['readings'][ed]=={'assignment_count':len(rows),'outcomes':dict(tally),'survivors':survivors,'status':expected}
 controls=load('SOFTWARE_CONTROLS.json');byname={c['name']:c for c in controls};assert len(controls)==5
 assert byname['variable_width']['vectors']==[[2,0],[2,0],[2,2]] and byname['variable_width']['observed']=='PASS'
 assert byname['retirement']['vectors']==[[2,0],[2,1],[1,0],[1,1]]
 assert byname['missing_retirement']['observed']=='BALANCE' and byname['bad_selector']['observed']=='PARSE' and byname['relaxed_reset']['observed']=='PASS'
 assert results['status']==('NO_RENAMED_COLUMN_BALANCE' if all(not v['survivors'] for v in results['readings'].values()) else 'NECESSARY_RELAXATION_SURVIVES')
 assert results['physical_loci']==1 and results['native_meanings_assigned']==results['independent_confirmation_capacity']==0
 assert not any(results[k] for k in ['native_atom_binding_proven','new_census_or_image','source_decoded'])
 out={'status':'PASS','scope':'Independent full working-label segmentation, recursive unit covers for every role assignment, source/seam provenance, frozen hashes and relaxed conservation relation; not native atoms or meanings.','same_author':True,'finite_role_check_validated':True,'native_atom_or_semantic_validation':False,'scientific_status':results['status'],'validator_sha256':sha(Path(__file__))}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
