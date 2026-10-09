"""Enumerate all role renamings of a relaxed ragged-column carrier."""
from pathlib import Path
from functools import lru_cache
from itertools import permutations
from collections import Counter
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (A/n).write_text(json.dumps(v,separators=(',',':'),ensure_ascii=False)+'\n')
def atomizations(word,alphabet):
 @lru_cache(None)
 def rec(t):
  if not t:return [()]
  return [(a,)+q for a in alphabet if t.startswith(a) for q in rec(t[len(a):])]
 return rec(word)
def counts(word,end,p2,p3):
 specials={end,p2,p3};i=n=e=0
 while i<len(word):
  sign=word[i];width=2 if sign==p2 else 3 if sign==p3 else 1
  if i+width>len(word) or any(t in specials for t in word[i+1:i+width]):return [-1,-1]
  n+=1;e+=sign==end;i+=width
 return [n,e]
def decision(vectors):
 for i,(n,e) in enumerate(vectors):
  if n<0:return 'PARSE',i+1
  if not 1<=n<=8:return 'CAPACITY',i+1
 for i,((n,e),(m,_)) in enumerate(zip(vectors,vectors[1:])):
  if n!=e and m!=n-e:return 'BALANCE',i+2
 return 'PASS',0
def main():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for name,h in lock['files'].items():assert sha(ROOT/name)==h,name
 spec=json.loads((A/'SPEC.json').read_text());raw=json.loads((ROOT/spec['raw_idea']).read_text());book=raw['design']['working_carrier'];alphabet=book['ordinary_signs_in_order']+['q','cfh',book['end_sign']];assert len(alphabet)==len(set(alphabet))==22
 assert set(['q','cfh',book['end_sign']]).isdisjoint(book['ordinary_signs_in_order'])
 lines=json.loads((A/'TARGET_LINES.json').read_text());streams={};tokens={}
 for line in lines:
  assert line['locus']==spec['locus'] and line['edition'] in spec['editions'];groups=line['groups'];assert len(groups)==9
  for i,g in enumerate(groups):
   assert g['source_group_index']==i+1
   assert g['left_separator']==('LINE_START' if i==0 else 'DEFINITE_SPACE')
   assert g['right_separator']==('LINE_END' if i==8 else 'DEFINITE_SPACE')
  pp=[atomizations(g['ivtff_group_raw'],tuple(alphabet)) for g in groups]
  if any(len(p)!=1 for p in pp):
   save('RESULT.json',{'status':'UNRESOLVED_FIXED_ATOMIZATION','edition':line['edition']});return
  streams[line['edition']]=[list(p[0]) for p in pp];tokens[line['edition']]=[g['ivtff_group_raw'] for g in groups]
 assert set(streams)==set(spec['editions'])
 # Software fixtures only: variable glyph widths, retirements, reset relaxation.
 e,p2,p3=book['end_sign'],'q','cfh'
 fixtures=[('variable_width',[['a','a'],['q','a','q','o'],[e,e]],'PASS'),('missing_retirement',[['a','a'],['a']],'BALANCE'),('retirement',[['a','a'],[e,'a'],['a'],[e]],'PASS'),('relaxed_reset',[[e],['a','a']],'PASS'),('bad_selector',[[p2,p3]],'PARSE')]
 tests=[]
 for name,words,want in fixtures:
  vv=[counts(w,e,p2,p3) for w in words];got=decision(vv)[0];assert got==want;(tests.append({'name':name,'groups':words,'vectors':vv,'expected':want,'observed':got}))
 save('SOFTWARE_CONTROLS.json',tests)
 results={};records={}
 for ed,words in streams.items():
  rows=[];survivors=[];tally=Counter()
  for ie,ip2,ip3 in permutations(range(22),3):
   vv=[counts(w,alphabet[ie],alphabet[ip2],alphabet[ip3]) for w in words];state,at=decision(vv);rows.append([ie,ip2,ip3,state,at,vv]);tally[state]+=1
   if state=='PASS':survivors.append([ie,ip2,ip3])
  results[ed]={'assignment_count':len(rows),'outcomes':dict(tally),'survivors':survivors,'status':'NO_RENAMED_COLUMN_BALANCE' if not survivors else 'NECESSARY_RELAXATION_SURVIVES'};records[ed]=rows
 save('ASSIGNMENTS.json',{'alphabet':alphabet,'columns':['END_index','P2_index','P3_index','status','first_failing_group','all_group_count_END_pairs'],'readings':records})
 save('ATOMIZED_LINES.json',{'tokens':tokens,'working_units':streams,'native_atoms_proven':False})
 status='NO_RENAMED_COLUMN_BALANCE' if all(not r['survivors'] for r in results.values()) else 'NECESSARY_RELAXATION_SURVIVES'
 out={'status':status,'readings':results,'physical_loci':1,'native_meanings_assigned':0,'native_atom_binding_proven':False,'independent_confirmation_capacity':0,'new_census_or_image':False,'source_decoded':False,'scope':'Necessary relaxed column-cell balance under every fixed22-working-glyph bijection; source letters/selectors and both window edges deliberately relaxed.'}
 save('RESULT.json',out);save('RUN_RECEIPT.json',{'runner_sha256':sha(Path(__file__)),'registration_lock_sha256':sha(A/'REGISTRATION_LOCK.json'),'assignments_sha256':sha(A/'ASSIGNMENTS.json')});print(json.dumps(out,indent=2))
if __name__=='__main__':main()
