"""Replay frozen observation accounting in an isolated source-only workspace.
Does not repeat human/AI visual perception or claim a new independent observation.
"""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 spec=json.loads((B/'src/SPEC.json').read_text());old=[spec['source_image'],'experiments/yolo/gdt1342_qoky_written_predecessor/artifacts/SOURCE.json.gz','experiments/yolo/gdt1348_graphic_component_check/artifacts/SOURCE_PACKET.json','experiments/yolo/gdt1348_graphic_component_check/artifacts/RESULT.json']
 with tempfile.TemporaryDirectory(prefix='vmanus1402replay_') as t:
  q=Path(t);rel=B.relative_to(R);shutil.copytree(B,q/rel,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for name in old:
   p=q/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,p)
  for filename in ['RESULT.json','VALIDATION.json']:(q/rel/'artifacts'/filename).unlink(missing_ok=True)
  for script in ['run.py','validate.py']:subprocess.run([sys.executable,str(q/rel/'src'/script)],cwd=q,check=True,stdout=subprocess.DEVNULL)
  matches={n:digest(q/rel/'artifacts'/n)==digest(B/'artifacts'/n) for n in ['RESULT.json','VALIDATION.json']};assert all(matches.values()),matches
  print(json.dumps({'status':'PASS','byte_exact':matches,'scope':'Isolated computation over frozen observations and source pixels, not renewed perception or external chronology attestation.'},sort_keys=True))
if __name__=='__main__':main()
