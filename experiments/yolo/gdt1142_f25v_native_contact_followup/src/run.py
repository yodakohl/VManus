#!/usr/bin/env python3
"""Offline replay of retained observations; never acquire or infer new pixels."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1]
def main():
 a=P/'artifacts';freeze=json.loads((a/'COMPARISON_FREEZE.json').read_text())
 for name,digest in freeze['files'].items():assert hashlib.sha256((a/name).read_bytes()).hexdigest()==digest,name
 r=json.loads((a/'ROOT_OBSERVATION.json').read_text());o=json.loads((a/'OBSERVER.json').read_text());result=json.loads((a/'RESULT.json').read_text())
 rows=[]
 for u,v in zip(r['observations'],o['items']):
  assert u['item']==v['item'];same=u['judgment']==v['assessment'];rows.append(dict(item=u['item'],root=u['judgment'],second_observer=v['assessment'],agreement=same,retained=u['judgment'] if same else 'UNRESOLVED'))
 assert rows==result['items'];assert len(rows)==5
 assert result['decision']=='NATIVE_OBSERVATIONS_RETAINED_ROLE_UNSELECTED'
 print(json.dumps({'decision':result['decision'],'paired_observations':rows,'meaning_selected':False,'basis':'Frozen manual visual judgments, not automated image recognition.'},indent=2))
if __name__=='__main__':main()
