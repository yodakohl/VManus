#!/usr/bin/env python3
"""Replay frozen artifacts in a new, minimal repository-shaped directory."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile,os
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-dir');a=p.parse_args();out=Path(a.output_dir).resolve() if a.output_dir else Path(tempfile.mkdtemp(prefix='vmanus1395-replay-'))/'repository'
 if out.exists():raise SystemExit('Output directory must be new')
 lock=json.loads((B/'LOCK.json').read_text());out.mkdir(parents=True)
 for item in lock['files']:
  src=R/item['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==item['sha256']
  dst=out/item['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 rel=B.relative_to(R);b=out/rel;shutil.copyfile(B/'LOCK.json',b/'LOCK.json')
 for script in ['run.py','validate.py']:subprocess.run([sys.executable,str(b/'src'/script)],cwd=out,check=True,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'))
 comparison={}
 for name in ['DATA.json','RESULT.json','NULLS.json']:
  expected=hashlib.sha256((B/'artifacts'/name).read_bytes()).hexdigest();actual=hashlib.sha256((b/'artifacts'/name).read_bytes()).hexdigest();assert actual==expected,name;comparison[name]=actual
 v=json.loads((b/'artifacts/VALIDATION.json').read_text());assert v['status']=='PASS_INDEPENDENT_VALIDATION'
 receipt={'experiment_id':'GDT1395','status':'PASS_FROZEN_REPLAY','compared':comparison,'independent_validation':v['status'],'scientific_status':v['scientific_status'],'scope':'Minimal repository-shaped replay; exposed cached cohort, no new manuscript access.'}
 (out/'REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
