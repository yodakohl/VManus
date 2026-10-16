#!/usr/bin/env python3
"""Replay primary, preserved original failure and explicit schema diagnostic."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir');a=ap.parse_args();out=Path(a.output_dir).resolve() if a.output_dir else Path(tempfile.mkdtemp(prefix='vmanus1396-replay-'))/'repository'
 if out.exists():raise SystemExit('Output directory must be new')
 out.mkdir(parents=True);rel=B.relative_to(R);b=out/rel
 paths={}
 for name in ['LOCK.json','ADAPTER_LOCK.json']:
  lock=json.loads((B/name).read_text())
  for item in lock['files']:paths[item['path']]=item['sha256']
 for p,h in paths.items():
  src=R/p;assert sha(src)==h;dst=out/p;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 for name in ['LOCK.json','ADAPTER_LOCK.json','src/derive_keyspace.py']:shutil.copyfile(B/name,b/name)
 primary=subprocess.run([sys.executable,str(b/'src/run.py')],cwd=out,capture_output=True,text=True,check=True)
 original=subprocess.run([sys.executable,str(b/'src/validate.py')],cwd=out,capture_output=True,text=True)
 assert original.returncode!=0 and "assert witness==expected and group['units']==[unit]" in original.stderr and 'AssertionError' in original.stderr
 assert not (b/'artifacts/VALIDATION.json').exists()
 subprocess.run([sys.executable,str(b/'src/validate_schema_adapter.py')],cwd=out,capture_output=True,text=True,check=True)
 subprocess.run([sys.executable,str(b/'src/derive_keyspace.py')],cwd=out,capture_output=True,text=True,check=True)
 compared={}
 for name in ['RESULT.json','VALIDATION_DIAGNOSTIC.json','KEYSPACE_COROLLARY.json']:
  expected=sha(B/'artifacts'/name);actual=sha(b/'artifacts'/name);assert actual==expected,name;compared[name]=actual
 receipt={'experiment_id':'GDT1396','status':'PASS_REPLAY_WITH_PRESERVED_ORIGINAL_VALIDATOR_FAILURE','original_validator':'EXPECTED_METADATA_ASSERTION_REPRODUCED','diagnostic_validator':'PASS_DIAGNOSTIC_SCHEMA_NORMALIZATION','scientific_status':json.loads((b/'artifacts/RESULT.json').read_text())['status'],'compared':compared,'scope':'Fixed wordbook-domain counts and explicit corrected diagnostic only; not an original-validator PASS or complete writer.'}
 (out/'REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
