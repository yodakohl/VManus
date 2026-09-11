#!/usr/bin/env python3
"""Reconcile separately frozen native observations without altering either."""
import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent.parent;A=E/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 expected=json.loads((E/'src/EXPECTED.json').read_text());packets=[json.loads((E/('src/OBSERVER_'+r+'.json')).read_text()) for r in ['A','B']]
 rows=[]
 for i,w in enumerate(expected['words']):
  cells=[p['rows'][i] for p in packets]
  assert all(c['index']==i and c['expected']==w and c['status'] in ['MATCH','CONTRADICTED','UNRESOLVED'] for c in cells)
  both=cells[0]['status']==cells[1]['status'];status=cells[0]['status'] if both else 'UNRESOLVED'
  rows.append(dict(index=i,expected=w,A=cells[0]['status'],B=cells[1]['status'],joint=status))
 localized=all(p['paragraph_localized'] and p['line_counts']==[11,6] and p['boundaries_resolved'] for p in packets)
 status='NATIVE_INPUT_SUPPORTED' if localized and all(r['joint']=='MATCH' for r in rows) else 'NATIVE_CONTRADICTION' if any(r['joint']=='CONTRADICTED' for r in rows) else 'NATIVE_INPUT_UNRESOLVED'
 result=dict(status=status,rows=rows,complete_localization_and_boundaries=localized,packet_hashes={r:sha(E/('src/OBSERVER_'+r+'.json')) for r in ['A','B']},joint_matching_groups=sum(r['joint']=='MATCH' for r in rows),joint_unresolved_groups=sum(r['joint']=='UNRESOLVED' for r in rows),joint_contradicted_groups=sum(r['joint']=='CONTRADICTED' for r in rows),confirmed_meanings=0,claim='Native written-input audit only; GDT923 transcript-relative result remains unchanged, no repaired transcript or Latin key extension.')
 (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
