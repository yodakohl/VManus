#!/usr/bin/env python3
"""Independent whole-paragraph structural replay; no primary imports."""
import hashlib
import itertools
import json
from pathlib import Path
import re
E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def placements(words,width):
 rows=[words[i:i+width] for i in range(0,len(words),width)]
 columns=list(zip(*rows));variable={j for j,col in enumerate(columns) if len(set(col))>1}
 if not 3<=len(variable)<=4:return []
 answer=[]
 # Transfer plus within-step distinction forces A,B,R to vary for K>=3:
 # A0!=B0=A1; B0!=R0=B1; R0=B1=A2!=B2=R1.
 for a,b,r in itertools.permutations(sorted(variable),3):
  for q in range(width):
   if q in (a,b,r) or not variable.issubset({a,b,q,r}):continue
   equations=[[row[j] for j in (a,b,q,r)] for row in rows]
   if any(len({A,B,R})!=3 for A,B,Q,R in equations):continue
   if any(later[0]!=earlier[1] or later[1]!=earlier[3] for earlier,later in zip(equations,equations[1:])):continue
   answer.append({'width':width,'steps':len(rows),'roles':[a,b,q,r],'equations':equations})
 return answer

def full_oracle(words,width):
 rows=[words[i:i+width] for i in range(0,len(words),width)];answer=set()
 for roles in itertools.permutations(range(width),4):
  if any(len({row[j] for row in rows})>1 for j in range(width) if j not in roles):continue
  a,b,q,r=roles
  if any(len({row[a],row[b],row[r]})!=3 for row in rows):continue
  if all(rows[i+1][a]==rows[i][b] and rows[i+1][b]==rows[i][r] for i in range(len(rows)-1)):answer.add(roles)
 return answer

def numeric_key(equations,a,b):
 forward={};reverse={}
 for A,B,Q,R in equations:
  if not 0<b<a:return None
  q,r=divmod(a,b)
  for token,value in zip((A,B,Q,R),(a,b,q,r)):
   if token in forward and forward[token]!=value:return None
   if value in reverse and reverse[value]!=token:return None
   forward[token]=value;reverse[value]=token
  a,b=b,r
 return forward

def fixtures():
 eq=[['n23','n10','n2','n3'],['n10','n3','n3','n1'],['n3','n1','n3','n0']]
 tests=0;oracle_tests=0
 for width,slots in [(4,[0,1,2,3]),(6,[0,2,3,5])]:
  for roles in itertools.permutations(slots):
   rows=[]
   for e in eq:
    row=['fixed_'+str(j) for j in range(width)]
    for j,t in zip(roles,e):row[j]=t
    rows.append(row)
   words=sum(rows,[]);actual={tuple(c['roles']) for c in placements(words,width)}
   assert tuple(roles) in actual and actual==full_oracle(words,width)
   key=numeric_key(eq,23,10);assert key is not None and key['n0']==0
   bad=[list(e) for e in eq];bad[2][0]='alien'
   bad_rows=[list(r) for r in rows];bad_rows[2][roles[0]]='alien'
   assert tuple(roles) not in {tuple(c['roles']) for c in placements(sum(bad_rows,[]),width)}
   assert numeric_key(bad,23,10) is None
   wrong_q=[list(e) for e in eq];wrong_q[0][2]='n3';assert numeric_key(wrong_q,23,10) is None
   tests+=1
 # Exhaust small three-row/four-column binary tables: no A/B/R distinct
 # triples possible. Add fixed nonbinary positive/negative mutation cases.
 for bits in itertools.product('ab',repeat=12):
  assert placements(list(bits),4)==[]
  oracle_tests+=1
 return {'positive_role_and_scaffold_cases':tests,'transfer_and_numeric_negatives':tests*2,'full_role_oracle_compared_positive_cases':tests,'binary_negative_tables':oracle_tests}

def main():
 specpath=E/'src/SPEC.json';spec=json.loads(specpath.read_text());path=ROOT/spec['source']['path'];assert sha(path)==spec['source']['sha256']
 source=json.loads(path.read_text());assert spec['minimum_steps']==3 and spec['minimum_step_groups']==4
 positive=fixtures();all_candidates=[];core=[];counts={}
 for ed in spec['readings']:
  pars=source['panels'][ed];np=0;small=0
  for p in pars:
   assert not p['page'].startswith('f84') and int(re.fullmatch(r'f([0-9]+)',p['physical_folio'])[1])%2
   words=p['words'];assert p['text']==' '.join(words) and len(words)==len(p['source_group_ids'])
   records=[]
   for steps in range(3,len(words)//4+1):
    if len(words)%steps:continue
    width=len(words)//steps;rows=[words[i:i+width] for i in range(0,len(words),width)];var=[j for j in range(width) if len({row[j] for row in rows})>1]
    np+=1;small+=len(var)<=4
    candidates=placements(words,width)
    for c in candidates:all_candidates.append({**c,'reading':ed,'id':p['id'],'page':p['page']})
    records.append({'width':width,'steps':steps,'varying_columns':var,'candidates':len(candidates)})
   core.append({'reading':ed,'id':p['id'],'page':p['page'],'groups':len(words),'partitions':sorted(records,key=lambda r:r['width'])})
  counts[ed]={'paragraphs':len(pars),'partitions':np,'at_most_four_varying':small}
 primary=json.loads((E/'artifacts/PARTITIONS.json').read_text())
 projected=[]
 for p in primary:
  projected.append({k:p[k] for k in ['reading','id','page','groups']})
  projected[-1]['partitions']=sorted([{k:r[k] for k in ['width','steps','varying_columns','candidates']} for r in p['partitions']],key=lambda r:r['width'])
 sortkey=lambda p:(p['reading'],p['id'])
 assert sorted(core,key=sortkey)==sorted(projected,key=sortkey)
 candidates=json.loads((E/'artifacts/CANDIDATES.json').read_text())
 assert not all_candidates and candidates==[],'Positive candidates require separate numeric solution-set verification'
 result=json.loads((E/'artifacts/RESULT.json').read_text())
 assert result['status']=='NO_FIXED_TEMPLATE_CHAIN' and result['structural_candidates']==result['numeric_candidates']==0
 for ed,c in counts.items():
  assert all(result['readings'][ed][k]==v for k,v in c.items())
  assert result['readings'][ed]['candidates']==0
  assert result['readings'][ed]['physical_leaves']==len({p['physical_folio'] for p in source['panels'][ed]})
 output={'status':'PASS','validator_sha256':sha(Path(__file__)),'source_sha256':sha(path),'spec_sha256':sha(specpath),'reading_counts':counts,'structural_candidates':0,'fixtures':positive,'artifact_sha256':{n:sha(E/'artifacts'/n) for n in ['PARTITIONS.json','CANDIDATES.json','RESULT.json']},'claim_ceiling':'Every complete equal partition and admissible four-role assignment is covered independently; zero literal structures excludes the fixed template regardless of numeric bound. Arithmetic search was not reached on manuscript data. No general arithmetic or meaning exclusion. Primary efficiency counters are not claimed as independently replayed.'}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
if __name__=='__main__':main()
