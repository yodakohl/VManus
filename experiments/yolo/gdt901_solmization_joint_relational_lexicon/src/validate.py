#!/usr/bin/env python3
import argparse,gzip,hashlib,json
from pathlib import Path
from source import load
from role_source import CASES,compile_case
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--parent-packet',type=Path);a=ap.parse_args()
 sp=BASE/'artifacts/SOURCE_INPUT.json';tp=BASE/'artifacts/TARGET_INPUT.json';mp=BASE/'artifacts/MODEL_SPEC.json'
 assert sha(sp)=='0daf60d86d63ec371137378310871dd0f3bc0b7d16ac78770986b66647fe5d65'
 assert sha(tp)=='6244c721c3d48c88a8a855e1dea038a39d3f0b291493d333fa28f8458d9f3544'
 assert sha(mp)=='119be016d348b28d0915792bdb59a2c4f40496ed821be9c5fcddae2c2856b17a'
 source=load(sp);spec=json.loads(mp.read_text());target=json.loads(tp.read_text())
 assert spec['cases']==CASES and spec['role_compiler_sha256']==sha(BASE/'src/role_source.py')
 assert [len(compile_case(source,c)['atoms']) for c in CASES]==spec['form_counts']
 assert {p:len(rs) for p,rs in target['panels'].items()}=={'CONSENSUS':1,'IT2a':259,'RF1b':11,'ZL3b':14}
 for rows in target['panels'].values():
  assert len({r['id'] for r in rows})==len(rows)
  for row in rows:
   assert row['words'] and len(row['words'])==len(row['source_group_ids'])
   assert not row['page'].startswith('f84') and int(row['physical_folio'][1:])%2==1
 parent_replay=False
 if a.parent_packet:
  assert sha(a.parent_packet)==target['parent_sha256']=='1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed'
  parent=json.loads(gzip.decompress(a.parent_packet.read_bytes()))
  assert parent['panels']==target['panels'];parent_replay=True
 phase='REGISTERED_INPUTS_ONLY';rp=BASE/'artifacts/RESULT.json'
 if rp.exists():
  phase='RESULTS';r=json.loads(rp.read_text());assert r['source_sha256']==sha(sp) and r['target_sha256']==sha(tp) and r['model_spec_sha256']==sha(mp)
  assert len(r['cases'])==40 and len({(c['panel'],c['case']) for c in r['cases']})==40
  for c in r['cases']:
   dp=BASE/'artifacts'/c['artifact'];assert sha(dp)==c['artifact_sha256'];d=json.loads(dp.read_text())
   assert d['status']==c['status']
   if c['status']=='EMPTY_ATOM_DOMAINS_UNSAT':assert d['empty_atoms'] and all(not d['domains'][x] for x in d['empty_atoms'])
   elif c['status']=='CAPACITY_STOP':assert d['available']<d['required']==22
  assert r['model_excluded_in_all_panels']==all(c['status'] in ['CAPACITY_STOP','EMPTY_ATOM_DOMAINS_UNSAT'] for c in r['cases'])
 out={'schema':'GDT901_VALIDATION_V1','status':'PASS','phase':phase,'source_sha256':sha(sp),'target_sha256':sha(tp),'model_spec_sha256':sha(mp),'parent_packet_exact_replay':parent_replay,'morphology_cases':10,'scope':'Frozeninputs and resultbindings; independent domain proof required for exclusion. No meaning validation.'}
 (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':'PASS','phase':phase,'parent_replay':parent_replay}))
if __name__=='__main__':main()
