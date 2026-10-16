"""Post-result replay: parsed content plus verified output bindings.

The frozen legacy summarizer emits one dict from a set, so byte order may vary.
This wrapper preserves all frozen scientific files and records byte inequality.
"""
from pathlib import Path
import copy,gzip,hashlib,json,shutil,subprocess,sys,tempfile
D=Path(__file__).resolve().parents[1];R=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def canonical(p):return hashlib.sha256(json.dumps(read(p),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def normalized_receipt(base,root,spec):
 receipt=copy.deepcopy(read(base/'artifacts/VALIDATION.json'));pins=receipt['pins']
 assert pins['validator_sha256']==sha(base/'src/validate.py')
 assert pins['lock_sha256']==sha(base/'LOCK.json')
 assert pins['source_envelope_sha256']==sha(root/spec['source_envelope_path'])
 for key,name in [('result_sha256','RESULT.json'),('families_sha256','FAMILIES.json.gz')]:
  assert pins[key]==sha(base/'artifacts'/name);pins[key]=canonical(base/'artifacts'/name)
 for name,value in pins['certificates'].items():
  assert value==sha(base/'artifacts'/name);pins['certificates'][name]=canonical(base/'artifacts'/name)
 return receipt
def main():
 spec=read(D/'src/SPEC.json');names=['FAMILIES.json.gz','RESULT.json']+['CERT_'+e+'_'+p+'.json.gz' for e in spec['readers'] for p in spec['panels']]
 with tempfile.TemporaryDirectory(prefix='vmanus1405semantic_') as tmp:
  root=Path(tmp);rel=D.relative_to(R);dest=root/rel;shutil.copytree(D,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for entry in spec['inputs']:
   p=root/entry['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/entry['path'],p)
  for name in names+['VALIDATION.json']:(dest/'artifacts'/name).unlink(missing_ok=True)
  for program in ['run.py','validate.py']:subprocess.run([sys.executable,str(dest/'src'/program)],cwd=root,check=True,stdout=subprocess.DEVNULL)
  byte={n:sha(D/'artifacts'/n)==sha(dest/'artifacts'/n) for n in names+['VALIDATION.json']}
  content={n:read(D/'artifacts'/n)==read(dest/'artifacts'/n) for n in names}
  validation_equal=normalized_receipt(D,R,spec)==normalized_receipt(dest,root,spec)
  assert all(content.values()) and validation_equal,{'content_equal':content,'normalized_validation_equal':validation_equal}
  print(json.dumps({'status':'PASS_CONTENT_AND_BINDING_REPLAY','byte_exact':byte,'parsed_content_equal':content,'validation_equal_after_verified_output_pin_normalization':validation_equal,'frozen_scientific_files_unchanged':True,'normalization':'Only validated result/family/certificate byte pins are replaced by canonical JSON-content hashes for comparison. Every original and fresh byte pin is checked before replacement. Code, lock and source-envelope pins stay unchanged.','scope':'Legacy dict key order may differ; every scientific value, proof-node order, native provenance and validator decision agrees. No meanings or alphabet identified.'},sort_keys=True))
if __name__=='__main__':main()
