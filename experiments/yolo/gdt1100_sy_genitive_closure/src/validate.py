#!/usr/bin/env python3
"""Preservation, independently recorded units, finite consequences only."""
import csv,hashlib,json
from pathlib import Path
from run import build
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def main():
 out,units=build()
 for name,text in out.items():assert (E/'artifacts'/name).read_text()==text,name
 m=json.loads((E/'src/MODEL.json').read_text());prior=json.loads((R/m['paragraph_receipt']).read_text())
 expected={(ed,p['id']):p for ed,pp in prior.items() for p in pp}
 assert set(units)==set(expected),'complete unit set differs from GDT928'
 for key,u in units.items():
  assert [l['metadata']['locus'] for l in u['lines']]==[l['locus'] for l in expected[key]['lines']]
  assert [g['source_group_id'] for l in u['lines'] for g in l['groups']]==[g for l in expected[key]['lines'] for g in l['source_ids']]
 result=json.loads(out['RESULT.json']);assert result['counts']=={'ZL3b':27,'IT2a':30,'RF1b':31}
 occ=list(csv.DictReader((E/'artifacts/OCCURRENCES.tsv').open(),delimiter='\t'));cases=list(csv.DictReader((E/'artifacts/CANDIDATE_CASES.tsv').open(),delimiter='\t'));assert len(cases)==3*len(occ)==264
 for c in cases:
  spec=m['candidates'][c['candidate']];faults=[]
  if c['eligibility']=='READY':
   if spec['left'] and int(c['available_left'])==0:faults.append('NO_WRITTEN_LEFT_OPERAND')
   if spec['right'] and int(c['available_right'])==0:faults.append('NO_WRITTEN_RIGHT_OPERAND')
  assert c['contradiction']=='|'.join(faults)
  expected_outcome='NOT_TESTABLE' if c['eligibility']!='READY' else ('CONTRADICTION' if faults else 'CAPACITY_COMPATIBLE')
  assert c['outcome']==expected_outcome
  assert not c['page'].startswith('f84') and c['page']!='f116v'
 receipt={'status':'PASS_PRESERVATION_AND_FINITE_ARITY','occurrences':len(occ),'cases':len(cases),'paragraphs_crosschecked':len(units),'meanings_verified':False,'paragraph_marks_native_verified':False,'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((E/'artifacts').glob('*')) if p.suffix in ['.json','.tsv'] and p.name!='VALIDATION.json'}}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['status','occurrences','cases','paragraphs_crosschecked','meanings_verified']}))
if __name__=='__main__':main()
