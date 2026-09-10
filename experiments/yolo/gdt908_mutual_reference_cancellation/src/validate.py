#!/usr/bin/env python3
"""Independent finite proof replay. Imports no primary experiment code."""
import collections
import hashlib
import itertools
import json
from pathlib import Path
import re

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
RECORDS=['MS03','MS09','MJ03','MJ09']
COLUMNS=['a','b','lcp','lcs','cuts','prefix_incomparable','X_external_suffix','XY_external_suffix','four_distinct_cuts','four_distinct_combinations']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((E/'artifacts'/name).read_text())
def comparable(x,y):return x.startswith(y) or y.startswith(x)
def common(x,y):return next((i for i,(a,b) in enumerate(zip(x,y)) if a!=b),min(len(x),len(y)))
def outside_suffix(texts,ending,a,b):
 return [i for i,t in enumerate(texts) if i not in (a,b) and len(t)>len(ending) and t.endswith(ending)]
def cancellation(texts):
 rows=[];survivors=[]
 for a,b in itertools.combinations(range(len(texts)),2):
  A,B=texts[a],texts[b];lp=common(A,B);ls=common(A[::-1],B[::-1]);counts=[0]*6
  for u in range(1,lp+1):
   for v in range(2,min(ls,len(A)-u-1,len(B)-u-1)+1):
    counts[0]+=1;X=A[u:len(A)-v];Y=B[u:len(B)-v]
    assert X and Y
    if comparable(X,Y):continue
    counts[1]+=1;ds=outside_suffix(texts,X,a,b);cs=outside_suffix(texts,Y,a,b)
    if not ds:continue
    counts[2]+=1
    if not cs:continue
    counts[3]+=1;assignments=[(c,d) for c in cs for d in ds if c!=d]
    if not assignments:continue
    counts[4]+=1;counts[5]+=len(assignments)
    survivors.append((a,b,u,v,X,Y,assignments))
  rows.append([a,b,lp,ls]+counts)
 return rows,survivors

def theorem(source):
 programs={p['id']:p for p in source['programs']}
 assert programs['MS03']['body_atoms']==['RET'] and programs['MS09']['body_atoms']==['RET']
 assert programs['MJ03']['body_atoms']==['RET','REF','N09'] and programs['MJ09']['body_atoms']==['REF','N03']
 assert len(source['header_orders'])==6 and {tuple(x) for x in source['header_orders']}==set(itertools.permutations(['location','mercury','companion']))
 output=[]
 for order in source['header_orders']:
  equations={}
  for ident in RECORDS:
   p=programs[ident];n='N03' if ident.endswith('03') else 'N09'
   assert p['header_factors']=={'location':['HOUSE',n],'mercury':['MERCURY'],'companion':['SATURN' if ident.startswith('MS') else 'JUPITER']}
   assert p['after_header']==['PARTILE']
   equations[ident]=sum((p['header_factors'][k] for k in order),[])+p['after_header']+p['body_atoms']
  a=equations['MS03'];b=equations['MS09'];i=a.index('N03');U=a[:i];V=a[i+1:]
  assert b==U+['N09']+V and 'HOUSE' in U and V[-2:]==['PARTILE','RET']
  assert len(U)>=1 and len(V)>=2 and equations['MJ03'][-1]=='N09' and equations['MJ09'][-1]=='N03'
  output.append({'U_atoms':U,'V_atoms':V,'equations':equations,'order':order})
 return output

def fixtures(theorems):
 output=[]
 atoms=['HOUSE','MERCURY','SATURN','PARTILE','RET','N03','N09','JUPITER','REF']
 base=dict(zip(atoms,['ha','mer','s','part','re','xx','yyy','ju','fo']))
 for th in theorems:
  for reverse in (False,True):
   code=dict(base)
   if reverse:code['N03'],code['N09']=code['N09'],code['N03']
   assert all(x and y and not comparable(x,y) for x,y in itertools.combinations(code.values(),2))
   words={k:''.join(code[a] for a in seq) for k,seq in th['equations'].items()};texts=sorted(words.values());assert len(set(texts))==4
   rows,survivors=cancellation(texts)
   original=[texts.index(words[k]) for k in RECORDS];a,b,c,d=original
   U=''.join(code[t] for t in th['U_atoms']);V=''.join(code[t] for t in th['V_atoms'])
   found=False
   for ai,bi,u,v,X,Y,assignments in survivors:
    if (ai,bi)==(min(a,b),max(a,b)) and (u,v)==(len(U),len(V)):
     expected=(c,d) if a<b else (d,c)
     if expected in assignments:found=True
   assert found,(th['order'],reverse)
   assert words['MS03']==U+code['N03']+V and words['MS09']==U+code['N09']+V
   assert words['MJ03'].endswith(code['N09']) and words['MJ09'].endswith(code['N03'])
   output.append({'order':th['order'],'swapped_house_codes':reverse,'source_orientation_in_sorted_pair':'forward' if a<b else 'reverse','known_code':code,'complete_outputs':words,'necessary_domain_contains_known_witness':True})
 return output

def main():
 specpath=E/'src/SPEC.json';spec=json.loads(specpath.read_text());inputs={}
 assert spec['records']==RECORDS and spec['sealed_data']==['f84','f84r']
 for name in ('source','target'):
  p=ROOT/spec[name]['path'];assert sha(p)==spec[name]['sha256'];inputs[name]=json.loads(p.read_text())
 th=theorem(inputs['source']);assert th==read('THEOREM.json')
 panel=inputs['target']['panels'][spec['panel']];assert len(panel)==259
 grouped=collections.defaultdict(list)
 for row in panel:
  assert not row['page'].startswith('f84') and int(re.fullmatch(r'f([0-9]+)',row['physical_folio'])[1])%2==1
  assert row['text']==' '.join(row['words']) and len(row['words'])==len(row['source_group_ids'])
  grouped[row['text']].append(row['id'])
 target_table=[{'ids':sorted(ids),'text':s} for s,ids in sorted(grouped.items())]
 assert {'strings':target_table}==read('TARGET_IDS.json')
 texts=[r['text'] for r in target_table];rows,survivors=cancellation(texts)
 assert {'columns':COLUMNS,'rows':rows}==read('PAIRS.json')
 # An empty necessary domain proves all orientations/orders impossible. No
 # nine-atom refinement result is inferred when a necessary survivor exists.
 assert not survivors,'Nonempty necessary domain requires independent exact refinement'
 assert read('RELAXED.json')==[] and read('WITNESSES.json')==[]
 positive=fixtures(th)
 primary_fixtures=read('FIXTURES.json');assert len(primary_fixtures)==6
 for f,t in zip(primary_fixtures,th):
  assert f['header_order']==t['order'] and f['both_source_orientations_recovered'] and f['fixture_witnesses']>0 and f['swapped_fixture_witnesses']>0
 totals={name:sum(r[j] for r in rows) for j,name in enumerate(COLUMNS) if j>=4}
 result=read('RESULT.json')
 assert result['pair_stage_totals']==totals and result['pairs']==len(rows)
 assert result['source_sha256']==spec['source']['sha256'] and result['target_sha256']==spec['target']['sha256']
 assert result['target_distinct_strings']==len(texts) and result['target_paragraphs']==len(panel)
 assert result['relaxed_cuts']==result['relaxed_four_distinct_combinations']==result['exact_four_record_witnesses']==0
 assert result['status']=='FIXED_899_FULL_MODEL_EXCLUDED'
 assert [r['order'] for r in result['header_orders']]==inputs['source']['header_orders']
 assert all(r['status']=='EXCLUDED_BY_NECESSARY_FOUR_RECORDS' and r['counts']=={} for r in result['header_orders'])
 out={'status':'PASS','validator_sha256':sha(Path(__file__)),'spec_sha256':sha(specpath),'source_sha256':spec['source']['sha256'],'target_sha256':spec['target']['sha256'],'theorem_headers':len(th),'target_paragraphs':len(panel),'distinct_strings':len(texts),'pairs':len(rows),'pair_stage_totals':totals,'necessary_survivors':0,'independent_positive_fixtures':positive,'primary_fixture_scope':'Positive counts inspected; independent known variable-length nine-code constructions replay all six headers and both source orientations. Primary exact-refinement multiplicities are not independently certified and are unnecessary for the empty target relaxation.','artifact_sha256':{n:sha(E/'artifacts'/n) for n in ['THEOREM.json','TARGET_IDS.json','PAIRS.json','RELAXED.json','WITNESSES.json','FIXTURES.json','RESULT.json']},'claim_ceiling':'All six full GDT899 model cases are excluded by an independently exhausted necessary four-record relaxation on the unchanged discovery packet. No general astrology, conditional-language or meaning claim.'}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('independent_positive_fixtures','artifact_sha256')}))
if __name__=='__main__':main()
