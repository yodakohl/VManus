#!/usr/bin/env python3
"""Author's exact accounting only; no linguistic truth or independent review."""
import csv, json, hashlib
from pathlib import Path
B=Path(__file__).resolve().parents[1]
R=B.parents[2]
def main():
 a=json.loads((B/'artifacts/AUTHOR_ACCOUNT.json').read_text())
 src=list(csv.DictReader((R/a['source_native_path']).open(), delimiter='\t'))
 assert a['conserved_native_rows']==src
 assert len(src)==473
 p=[r for r in src if r['edition']=='ZL3b' and r['block']!='OUTSIDE']
 assert len(p)==108
 assert [r['native'] for r in a['primary_account']]==p
 assert a['core_sha256']==hashlib.sha256((B/'CORE.json').read_bytes()).hexdigest()
 assert a['core_md_sha256']==hashlib.sha256((B/'CORE.md').read_bytes()).hexdigest()
 assert set(a['connected_readings'])=={'N','E','S','W'}
 for r in a['primary_account']:
  assert r['native']['source_group_id']
  assert r['grammatical_attachment']
  assert r['contribution']
  f=r['native']['ivtff_group_raw']
  if r['semantic_status']=='UNKNOWN_WORD':
   assert f'UNKNOWN:{f}' in a['connected_readings'][r['native']['block']]
 d={}
 for r in a['primary_account']:
  f=r['native']['ivtff_group_raw']
  if f in d:assert d[f]==r['stable_denotation']
  d[f]=r['stable_denotation']
 assert a['counts']['semantic_unknown_positions']==sum(r['semantic_status']=='UNKNOWN_WORD' for r in a['primary_account'])
 assert a['counts']['structural_positions']==sum(r['semantic_status']=='STRUCTURAL_MARK' for r in a['primary_account'])
 for ext in a['extensions']['ordered_component_licenses']:
  form=ext['form']
  assert ext['occurrences']==[r['native']['source_group_id'] for r in a['primary_account'] if r['native']['ivtff_group_raw']==form]
 print(json.dumps({'author_accounting':'PASS','conserved_native_rows':473,'primary_positions':108,'unknown_positions':a['counts']['semantic_unknown_positions'],'candidate':a['candidate_label'],'semantic_truth':'NOT_TESTED','independent_review':'PENDING'},indent=2))
if __name__=='__main__':main()
