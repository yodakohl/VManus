#!/usr/bin/env python3
import argparse,gzip,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--parent-packet',type=Path);args=ap.parse_args()
 sp=BASE/'artifacts/SOURCE_INPUT.json';tp=BASE/'artifacts/TARGET_INPUT.json'
 assert sha(sp)=='aec96b65f3bc4248fd6979a3e69556720ad841523eca5c85d52ef6ce1c3e87cf'
 assert sha(tp)=='850582c870458a96ee5b8a541e280f9bba3c56732f2432fe362f08289820f194'
 s=json.loads(sp.read_text());t=json.loads(tp.read_text());assert len(s['records'])==8 and len(s['atoms'])==38
 assert [r['row_count'] for r in s['records']]==list(range(9,1,-1))
 assert sum(len(r['sequence']) for r in s['records'])==220
 for r in s['records']:
  for i in range(0,len(r['sequence']),5):
   a,m,b,e,c=r['sequence'][i:i+5];assert m=='OP:fia' and e=='OP:fa';assert int(a[4:])*int(b[4:])==int(c[4:])
 parent=False
 if args.parent_packet:
  assert sha(args.parent_packet)==t['parent_sha256']=='1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed'
  assert json.loads(gzip.decompress(args.parent_packet.read_bytes()))['panels']==t['panels'];parent=True
 for rows in t['panels'].values():
  assert len({r['id'] for r in rows})==len(rows)
  for r in rows:assert r['words'] and len(r['words'])==len(r['source_group_ids']) and not r['page'].startswith('f84') and int(r['physical_folio'][1:])%2==1
 phase='FROZEN_INPUTS_ONLY';rp=BASE/'artifacts/RESULT.json'
 if rp.exists():
  phase='NECESSARY_RESULTS';r=json.loads(rp.read_text());assert r['source_sha256']==sha(sp) and r['target_sha256']==sha(tp)
  assert {p['panel'] for p in r['panels']}==set(t['panels']) and len(r['panels'])==4
  for p in r['panels']:
   dp=BASE/'artifacts'/p['artifact'];assert sha(dp)==p['artifact_sha256'];d=json.loads(gzip.decompress(dp.read_bytes()));assert d['status']==p['status']
   if p['status']=='CAPACITY_STOP':assert d['available']<d['required']==8
   elif p['status']=='EMPTY_ATOM_DOMAINS_UNSAT':assert d['empty_atoms'] and all(not d['domains'][a] for a in d['empty_atoms'])
   elif p['status']=='OPERATOR_PAIR_DOMAINS_UNSAT':assert not d['operator_pairs']
  assert r['model_excluded_in_all_panels']==all(p['status'] in ['CAPACITY_STOP','EMPTY_ATOM_DOMAINS_UNSAT','OPERATOR_PAIR_DOMAINS_UNSAT'] for p in r['panels'])
 out={'status':'PASS','phase':phase,'source_sha256':sha(sp),'target_sha256':sha(tp),'parent_exact_replay':parent,'coverage':'Frozen complete source, arithmetic, target scope and resultbindings; independent necessary-domain replay required for exclusion.'}
 (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
